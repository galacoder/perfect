"""
FastAPI Webhook Server for BusOS Email Sequence.

This server provides webhook endpoints for frontend integration:
- POST /webhook/signup: Handle new user signups
- POST /webhook/assessment: Handle completed assessments

The server triggers Prefect flows in response to webhook events.

Usage:
    # Development (with auto-reload)
    uvicorn server:app --reload --port 8000

    # Production
    uvicorn server:app --host 0.0.0.0 --port 8000 --workers 4

Environment variables required:
- NOTION_TOKEN
- NOTION_CONTACTS_DB_ID
- NOTION_TEMPLATES_DB_ID
- RESEND_API_KEY
- TESTING_MODE (optional, default: false)
- DISCORD_WEBHOOK_URL (optional, for hot lead notifications)
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import logging
import os
from datetime import datetime

# Import Prefect flows
from campaigns.businessx_canada_lead_nurture.flows.signup_handler import signup_handler_flow
from campaigns.businessx_canada_lead_nurture.flows.assessment_handler import assessment_handler_flow

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="BusOS Email Sequence API",
    description="Webhook endpoints for triggering email nurture sequences",
    version="1.0.0"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== Pydantic Models for Request Validation =====

class SignupRequest(BaseModel):
    """
    Signup webhook payload.

    Example:
        {
            "email": "john@example.com",
            "name": "John Doe",
            "first_name": "John",
            "business_name": "John's Salon",
            "signup_source": "web_form"
        }
    """
    email: EmailStr = Field(..., description="Contact's email address")
    name: str = Field(..., description="Full name")
    first_name: str = Field(..., description="First name for personalization")
    business_name: str = Field(default="your business", description="Business name")
    signup_source: str = Field(default="web_form", description="Signup source")

    class Config:
        schema_extra = {
            "example": {
                "email": "john@example.com",
                "name": "John Doe",
                "first_name": "John",
                "business_name": "John's Salon",
                "signup_source": "web_form"
            }
        }


class AssessmentRequest(BaseModel):
    """
    Assessment completion webhook payload.

    Example:
        {
            "email": "john@example.com",
            "red_systems": 2,
            "orange_systems": 1,
            "yellow_systems": 2,
            "green_systems": 3,
            "assessment_score": 65,
            "assessment_date": "2025-11-12T10:30:00Z"
        }
    """
    email: EmailStr = Field(..., description="Contact's email address")
    red_systems: int = Field(..., ge=0, le=8, description="Number of red (broken) systems")
    orange_systems: int = Field(..., ge=0, le=8, description="Number of orange (warning) systems")
    yellow_systems: int = Field(default=0, ge=0, le=8, description="Number of yellow systems")
    green_systems: int = Field(default=0, ge=0, le=8, description="Number of green (healthy) systems")
    assessment_score: Optional[int] = Field(None, ge=0, le=100, description="Overall assessment score")
    assessment_date: Optional[str] = Field(None, description="ISO timestamp of assessment completion")

    class Config:
        schema_extra = {
            "example": {
                "email": "john@example.com",
                "red_systems": 2,
                "orange_systems": 1,
                "yellow_systems": 2,
                "green_systems": 3,
                "assessment_score": 65,
                "assessment_date": "2025-11-12T10:30:00Z"
            }
        }


class ChristmasSignupRequest(BaseModel):
    """
    Christmas campaign signup webhook payload.

    Triggered when customer completes assessment and signs up for Christmas campaign.
    Includes both contact info and assessment data.

    Example:
        {
            "email": "sarah@example.com",
            "first_name": "Sarah",
            "business_name": "Sarah's Salon",
            "assessment_score": 52,
            "red_systems": 2,
            "orange_systems": 1,
            "yellow_systems": 2,
            "green_systems": 3,
            "gps_score": 45,
            "money_score": 38,
            "weakest_system_1": "GPS",
            "weakest_system_2": "Money",
            "revenue_leak_total": 14700
        }
    """
    email: EmailStr = Field(..., description="Customer email address")
    first_name: str = Field(..., description="Customer first name")
    business_name: Optional[str] = Field(None, description="Business name")
    assessment_score: int = Field(..., ge=0, le=100, description="Overall BusOS score")
    red_systems: int = Field(default=0, ge=0, le=8, description="Number of broken systems")
    orange_systems: int = Field(default=0, ge=0, le=8, description="Number of struggling systems")
    yellow_systems: int = Field(default=0, ge=0, le=8, description="Number of functional systems")
    green_systems: int = Field(default=0, ge=0, le=8, description="Number of optimized systems")
    gps_score: Optional[int] = Field(None, ge=0, le=100, description="GPS system score")
    money_score: Optional[int] = Field(None, ge=0, le=100, description="Money system score")
    weakest_system_1: Optional[str] = Field(None, description="Weakest system name")
    weakest_system_2: Optional[str] = Field(None, description="Second weakest system")
    revenue_leak_total: Optional[int] = Field(None, description="Total revenue leak estimate")

    class Config:
        schema_extra = {
            "example": {
                "email": "sarah@example.com",
                "first_name": "Sarah",
                "business_name": "Sarah's Salon",
                "assessment_score": 52,
                "red_systems": 2,
                "orange_systems": 1,
                "yellow_systems": 2,
                "green_systems": 3,
                "gps_score": 45,
                "money_score": 38,
                "weakest_system_1": "GPS",
                "weakest_system_2": "Money",
                "revenue_leak_total": 14700
            }
        }


class CalcomBookingRequest(BaseModel):
    """
    Cal.com booking webhook payload.

    Triggered when customer books a diagnostic meeting via Cal.com.
    Used to schedule pre-call prep email sequence.

    Example:
        {
            "triggerEvent": "BOOKING_CREATED",
            "payload": {
                "booking": {
                    "id": 12345,
                    "uid": "booking-uid-123",
                    "title": "BusOS Diagnostic Call",
                    "startTime": "2025-11-25T14:00:00.000Z",
                    "endTime": "2025-11-25T15:00:00.000Z",
                    "attendees": [
                        {
                            "email": "customer@example.com",
                            "name": "Customer Name",
                            "timeZone": "America/Toronto"
                        }
                    ]
                }
            }
        }
    """
    triggerEvent: str = Field(..., description="Cal.com event type (e.g., BOOKING_CREATED)")
    payload: dict = Field(..., description="Cal.com booking payload")

    class Config:
        extra = "allow"  # Allow extra fields from Cal.com
        schema_extra = {
            "example": {
                "triggerEvent": "BOOKING_CREATED",
                "payload": {
                    "booking": {
                        "id": 12345,
                        "uid": "booking-uid-123",
                        "title": "BusOS Diagnostic Call",
                        "startTime": "2025-11-25T14:00:00.000Z",
                        "endTime": "2025-11-25T15:00:00.000Z",
                        "attendees": [
                            {
                                "email": "customer@example.com",
                                "name": "Customer Name",
                                "timeZone": "America/Toronto"
                            }
                        ]
                    }
                }
            }
        }


# ===== Health Check Endpoint =====

@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.

    Returns:
        Status information about the API and environment
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "environment": {
            "testing_mode": os.getenv("TESTING_MODE", "false"),
            "notion_configured": bool(os.getenv("NOTION_TOKEN")),
            "resend_configured": bool(os.getenv("RESEND_API_KEY")),
            "discord_configured": bool(os.getenv("DISCORD_WEBHOOK_URL"))
        }
    }


# ===== Webhook Endpoints =====

@app.post("/webhook/signup")
async def signup_webhook(
    request: SignupRequest,
    background_tasks: BackgroundTasks
):
    """
    Handle new user signup webhook.

    This endpoint:
    1. Validates signup data
    2. Triggers signup_handler_flow in background
    3. Creates/updates contact in Notion
    4. Returns immediately with 202 Accepted

    Args:
        request: Signup data validated by Pydantic

    Returns:
        Acceptance confirmation with request ID

    Example:
        curl -X POST http://localhost:8000/webhook/signup \\
          -H "Content-Type: application/json" \\
          -d '{
            "email": "john@example.com",
            "name": "John Doe",
            "first_name": "John",
            "business_name": "John's Salon"
          }'
    """
    logger.info(f"📥 Received signup webhook for {request.email}")

    try:
        # Trigger Prefect flow in background
        background_tasks.add_task(
            signup_handler_flow,
            email=request.email,
            name=request.name,
            first_name=request.first_name,
            business_name=request.business_name,
            signup_source=request.signup_source
        )

        logger.info(f"✅ Signup flow queued for {request.email}")

        return {
            "status": "accepted",
            "message": "Signup received and being processed",
            "email": request.email,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ Error processing signup for {request.email}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing signup: {str(e)}"
        )


@app.post("/webhook/assessment")
async def assessment_webhook(
    request: AssessmentRequest,
    background_tasks: BackgroundTasks
):
    """
    Handle completed assessment webhook.

    This endpoint:
    1. Validates assessment data
    2. Triggers assessment_handler_flow in background
    3. Updates Notion with results
    4. Triggers email sequence based on segment
    5. Returns immediately with 202 Accepted

    Args:
        request: Assessment data validated by Pydantic

    Returns:
        Acceptance confirmation with segment classification

    Example:
        curl -X POST http://localhost:8000/webhook/assessment \\
          -H "Content-Type: application/json" \\
          -d '{
            "email": "john@example.com",
            "red_systems": 2,
            "orange_systems": 1,
            "yellow_systems": 2,
            "green_systems": 3,
            "assessment_score": 65
          }'
    """
    logger.info(f"📥 Received assessment webhook for {request.email}")
    logger.info(f"   Systems: {request.red_systems}R, {request.orange_systems}O, {request.yellow_systems}Y, {request.green_systems}G")

    try:
        # Determine segment for quick response
        from campaigns.businessx_canada_lead_nurture.tasks.routing import determine_segment

        segment = determine_segment(
            red_systems=request.red_systems,
            orange_systems=request.orange_systems,
            yellow_systems=request.yellow_systems,
            green_systems=request.green_systems
        )

        logger.info(f"   Segment: {segment}")

        # Trigger Prefect flow in background
        background_tasks.add_task(
            assessment_handler_flow,
            email=request.email,
            red_systems=request.red_systems,
            orange_systems=request.orange_systems,
            yellow_systems=request.yellow_systems,
            green_systems=request.green_systems,
            assessment_score=request.assessment_score,
            assessment_date=request.assessment_date
        )

        logger.info(f"✅ Assessment flow queued for {request.email} ({segment})")

        # Optional: Send Discord notification for hot leads (CRITICAL segment)
        if segment == "CRITICAL" and os.getenv("DISCORD_WEBHOOK_URL"):
            background_tasks.add_task(
                send_discord_notification,
                email=request.email,
                segment=segment,
                red_systems=request.red_systems
            )

        return {
            "status": "accepted",
            "message": "Assessment received and email sequence will begin shortly",
            "email": request.email,
            "segment": segment,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ Error processing assessment for {request.email}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing assessment: {str(e)}"
        )


@app.post("/webhook/christmas-signup")
async def christmas_signup_webhook(
    request: ChristmasSignupRequest,
    background_tasks: BackgroundTasks
):
    """
    Handle Christmas campaign signup webhook.

    This endpoint:
    1. Validates signup data (via Pydantic)
    2. Triggers signup_handler_flow in background
    3. Creates/updates contact in BusinessX Canada Database
    4. Creates entry in Email Sequence Database with Campaign="Christmas 2025"
    5. Schedules 7-email nurture sequence via Prefect Deployment
    6. Returns immediately with 202 Accepted

    Args:
        request: Christmas signup data validated by Pydantic

    Returns:
        Acceptance confirmation with request ID

    Example:
        curl -X POST http://localhost:8000/webhook/christmas-signup \\
          -H "Content-Type: application/json" \\
          -d '{
            "email": "sarah@example.com",
            "first_name": "Sarah",
            "business_name": "Sarah's Salon",
            "assessment_score": 52,
            "red_systems": 2,
            "orange_systems": 1,
            "yellow_systems": 2,
            "green_systems": 3,
            "gps_score": 45,
            "money_score": 38,
            "weakest_system_1": "GPS",
            "weakest_system_2": "Money",
            "revenue_leak_total": 14700
          }'
    """
    logger.info(f"📥 Received Christmas signup webhook for {request.email}")
    logger.info(f"   Assessment Score: {request.assessment_score}, Red Systems: {request.red_systems}")

    try:
        # Import Christmas campaign signup handler
        from campaigns.christmas_campaign.flows.signup_handler import signup_handler_flow

        # Trigger Prefect flow in background
        background_tasks.add_task(
            signup_handler_flow,
            email=request.email,
            first_name=request.first_name,
            business_name=request.business_name or "your business",
            assessment_score=request.assessment_score,
            red_systems=request.red_systems,
            orange_systems=request.orange_systems,
            yellow_systems=request.yellow_systems,
            green_systems=request.green_systems,
            gps_score=request.gps_score,
            money_score=request.money_score,
            weakest_system_1=request.weakest_system_1,
            weakest_system_2=request.weakest_system_2,
            revenue_leak_total=request.revenue_leak_total
        )

        logger.info(f"✅ Christmas signup flow queued for {request.email}")

        return {
            "status": "accepted",
            "message": "Christmas signup received and email sequence will begin shortly",
            "email": request.email,
            "campaign": "Christmas 2025",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ Error processing Christmas signup for {request.email}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing Christmas signup: {str(e)}"
        )


@app.post("/webhook/calcom-booking")
async def calcom_booking_webhook(
    request: CalcomBookingRequest,
    background_tasks: BackgroundTasks
):
    """
    Handle Cal.com booking webhook.

    This endpoint:
    1. Validates Cal.com booking event (via Pydantic)
    2. Only processes BOOKING_CREATED events
    3. Extracts customer email, name, meeting time from payload
    4. Triggers precall_prep_flow in background
    5. Updates Notion with meeting booking status
    6. Returns immediately with 202 Accepted

    Args:
        request: Cal.com booking data validated by Pydantic

    Returns:
        Acceptance confirmation with booking details

    Example:
        curl -X POST http://localhost:8000/webhook/calcom-booking \\
          -H "Content-Type: application/json" \\
          -d '{
            "triggerEvent": "BOOKING_CREATED",
            "payload": {
              "booking": {
                "id": 12345,
                "startTime": "2025-11-25T14:00:00Z",
                "endTime": "2025-11-25T15:00:00Z",
                "attendees": [
                  {
                    "email": "customer@example.com",
                    "name": "Customer Name"
                  }
                ]
              }
            }
          }'
    """
    logger.info(f"📥 Received Cal.com webhook: {request.triggerEvent}")

    # Only handle BOOKING_CREATED events
    if request.triggerEvent != "BOOKING_CREATED":
        logger.info(f"⏭️  Ignoring non-booking event: {request.triggerEvent}")
        return {
            "status": "ignored",
            "event": request.triggerEvent,
            "message": "Only BOOKING_CREATED events are processed"
        }

    try:
        # Extract customer data from Cal.com payload
        booking = request.payload.get("booking", {})
        attendees = booking.get("attendees", [])

        if not attendees:
            logger.error("❌ No attendees found in Cal.com payload")
            raise HTTPException(
                status_code=400,
                detail="Invalid Cal.com payload: no attendees found"
            )

        customer_email = attendees[0].get("email")
        customer_name = attendees[0].get("name")
        meeting_time = booking.get("startTime")

        if not all([customer_email, customer_name, meeting_time]):
            logger.error(f"❌ Missing required fields in Cal.com payload")
            raise HTTPException(
                status_code=400,
                detail="Invalid Cal.com payload: missing email, name, or startTime"
            )

        logger.info(f"📅 Booking details: {customer_email}, meeting at {meeting_time}")

        # Import pre-call prep flow
        from campaigns.christmas_campaign.flows.precall_prep_flow import precall_prep_flow_sync

        # Trigger Prefect flow in background
        background_tasks.add_task(
            precall_prep_flow_sync,
            email=customer_email,
            name=customer_name,
            meeting_time=meeting_time
        )

        logger.info(f"✅ Pre-call prep flow queued for {customer_email}")

        return {
            "status": "accepted",
            "message": "Booking received and pre-call sequence will begin shortly",
            "email": customer_email,
            "meeting_time": meeting_time,
            "timestamp": datetime.now().isoformat()
        }

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"❌ Error processing Cal.com booking: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing Cal.com booking: {str(e)}"
        )


# ===== Optional Discord Notification =====

async def send_discord_notification(email: str, segment: str, red_systems: int):
    """
    Send Discord notification for hot leads (CRITICAL segment).

    Args:
        email: Contact email
        segment: Customer segment
        red_systems: Number of red systems
    """
    discord_webhook_url = os.getenv("DISCORD_WEBHOOK_URL")

    if not discord_webhook_url:
        return

    try:
        import httpx

        payload = {
            "content": f"🚨 **Hot Lead Alert!**",
            "embeds": [{
                "title": "CRITICAL Segment Contact",
                "description": f"New contact needs immediate attention",
                "color": 16711680,  # Red color
                "fields": [
                    {"name": "Email", "value": email, "inline": True},
                    {"name": "Segment", "value": segment, "inline": True},
                    {"name": "Red Systems", "value": str(red_systems), "inline": True}
                ],
                "footer": {"text": "BusOS Email Sequence"},
                "timestamp": datetime.now().isoformat()
            }]
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(discord_webhook_url, json=payload)
            response.raise_for_status()

        logger.info(f"✅ Discord notification sent for {email}")

    except Exception as e:
        logger.error(f"❌ Failed to send Discord notification: {e}")
        # Don't fail the webhook if Discord notification fails


# ==============================================================================
# Wave 5: New Webhook Endpoints (Christmas Traditional Service Campaign)
# ==============================================================================

class CalendlyNoShowRequest(BaseModel):
    """
    Calendly no-show webhook payload.

    Example:
        {
            "email": "sarah@example.com",
            "first_name": "Sarah",
            "business_name": "Sarah's Salon",
            "calendly_event_uri": "https://calendly.com/events/ABC123",
            "scheduled_time": "2025-12-01T14:00:00Z"
        }
    """
    email: EmailStr = Field(..., description="Contact email address")
    first_name: str = Field(..., description="Contact first name")
    business_name: str = Field(..., description="Business name")
    calendly_event_uri: str = Field(..., description="Calendly event URI")
    scheduled_time: str = Field(..., description="Original scheduled time (ISO format)")

    class Config:
        schema_extra = {
            "example": {
                "email": "sarah@example.com",
                "first_name": "Sarah",
                "business_name": "Sarah's Salon",
                "calendly_event_uri": "https://calendly.com/events/ABC123",
                "scheduled_time": "2025-12-01T14:00:00Z"
            }
        }


class PostCallMaybeRequest(BaseModel):
    """
    Post-call maybe webhook payload.

    Example:
        {
            "email": "sarah@example.com",
            "first_name": "Sarah",
            "business_name": "Sarah's Salon",
            "call_date": "2025-12-01T14:30:00Z",
            "call_outcome": "Maybe",
            "call_notes": "Interested but needs budget approval",
            "objections": ["Price", "Timing"],
            "follow_up_priority": "High"
        }
    """
    email: EmailStr = Field(..., description="Contact email address")
    first_name: str = Field(..., description="Contact first name")
    business_name: str = Field(..., description="Business name")
    call_date: str = Field(..., description="Call date (ISO format)")
    call_outcome: str = Field(default="Maybe", description="Call outcome")
    call_notes: Optional[str] = Field(None, description="Notes from the call")
    objections: Optional[list[str]] = Field(None, description="List of objections")
    follow_up_priority: str = Field(default="Medium", description="Follow-up priority (High/Medium/Low)")

    class Config:
        schema_extra = {
            "example": {
                "email": "sarah@example.com",
                "first_name": "Sarah",
                "business_name": "Sarah's Salon",
                "call_date": "2025-12-01T14:30:00Z",
                "call_outcome": "Maybe",
                "call_notes": "Interested but needs budget approval",
                "objections": ["Price", "Timing"],
                "follow_up_priority": "High"
            }
        }


class OnboardingStartRequest(BaseModel):
    """
    Onboarding start webhook payload.

    Example:
        {
            "email": "sarah@example.com",
            "first_name": "Sarah",
            "business_name": "Sarah's Salon",
            "payment_confirmed": true,
            "payment_amount": 2997.00,
            "payment_date": "2025-12-01T15:00:00Z",
            "docusign_completed": true,
            "salon_address": "123 Main St, Toronto, ON",
            "observation_dates": ["2025-12-10", "2025-12-17"],
            "start_date": "2025-12-10"
        }
    """
    email: EmailStr = Field(..., description="Client email address")
    first_name: str = Field(..., description="Client first name")
    business_name: str = Field(..., description="Salon/business name")
    payment_confirmed: bool = Field(..., description="Whether payment was confirmed")
    payment_amount: float = Field(..., description="Payment amount (e.g., 2997.00)")
    payment_date: str = Field(..., description="Payment date (ISO format)")
    docusign_completed: bool = Field(default=True, description="Whether DocuSign contract was completed")
    salon_address: Optional[str] = Field(None, description="Physical address of salon")
    observation_dates: Optional[list[str]] = Field(None, description="List of scheduled observation dates")
    start_date: Optional[str] = Field(None, description="Phase 1 start date (ISO format)")
    package_type: str = Field(default="Phase 1 - Traditional Service Diagnostic", description="Package purchased")

    class Config:
        schema_extra = {
            "example": {
                "email": "sarah@example.com",
                "first_name": "Sarah",
                "business_name": "Sarah's Salon",
                "payment_confirmed": True,
                "payment_amount": 2997.00,
                "payment_date": "2025-12-01T15:00:00Z",
                "docusign_completed": True,
                "salon_address": "123 Main St, Toronto, ON",
                "observation_dates": ["2025-12-10", "2025-12-17"],
                "start_date": "2025-12-10",
                "package_type": "Phase 1 - Traditional Service Diagnostic"
            }
        }


@app.post("/webhook/calendly-noshow")
async def calendly_noshow_webhook(request: CalendlyNoShowRequest, background_tasks: BackgroundTasks):
    """
    Handle Calendly no-show webhook.

    Triggered when: Client misses their scheduled call

    This endpoint:
    1. Receives no-show notification from Calendly
    2. Triggers noshow_recovery_handler_flow
    3. Schedules 3 recovery emails (5min, 24h, 48h)
    """
    logger.info(f"📞 Received Calendly no-show webhook for {request.email}")
    logger.info(f"   Business: {request.business_name}")
    logger.info(f"   Event URI: {request.calendly_event_uri}")
    logger.info(f"   Scheduled Time: {request.scheduled_time}")

    try:
        # Import flow
        from campaigns.christmas_campaign.flows.noshow_recovery_handler import noshow_recovery_handler_flow

        # Trigger flow in background
        def run_flow():
            result = noshow_recovery_handler_flow(
                email=request.email,
                first_name=request.first_name,
                business_name=request.business_name,
                calendly_event_uri=request.calendly_event_uri,
                scheduled_time=request.scheduled_time,
                missed_time=datetime.now().isoformat()
            )
            logger.info(f"✅ No-show recovery flow completed: {result.get('status')}")

        background_tasks.add_task(run_flow)

        logger.info(f"✅ No-show recovery flow triggered for {request.email}")

        return {
            "status": "accepted",
            "message": "No-show recovery sequence will begin shortly",
            "email": request.email,
            "campaign": "Christmas Traditional Service"
        }

    except Exception as e:
        logger.error(f"❌ Error triggering no-show recovery flow: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to trigger no-show recovery: {str(e)}")


@app.post("/webhook/postcall-maybe")
async def postcall_maybe_webhook(request: PostCallMaybeRequest, background_tasks: BackgroundTasks):
    """
    Handle post-call maybe webhook.

    Triggered when: Sales call ends with "maybe" outcome

    This endpoint:
    1. Receives post-call data from CRM
    2. Triggers postcall_maybe_handler_flow
    3. Schedules 3 follow-up emails (1h, Day 3, Day 7)
    """
    logger.info(f"📞 Received post-call maybe webhook for {request.email}")
    logger.info(f"   Business: {request.business_name}")
    logger.info(f"   Call Date: {request.call_date}")
    logger.info(f"   Outcome: {request.call_outcome}")
    logger.info(f"   Priority: {request.follow_up_priority}")

    try:
        # Import flow
        from campaigns.christmas_campaign.flows.postcall_maybe_handler import postcall_maybe_handler_flow

        # Trigger flow in background
        def run_flow():
            result = postcall_maybe_handler_flow(
                email=request.email,
                first_name=request.first_name,
                business_name=request.business_name,
                call_date=request.call_date,
                call_outcome=request.call_outcome,
                call_notes=request.call_notes,
                objections=request.objections,
                follow_up_priority=request.follow_up_priority
            )
            logger.info(f"✅ Post-call maybe flow completed: {result.get('status')}")

        background_tasks.add_task(run_flow)

        logger.info(f"✅ Post-call maybe flow triggered for {request.email}")

        return {
            "status": "accepted",
            "message": "Post-call follow-up sequence will begin shortly",
            "email": request.email,
            "call_outcome": request.call_outcome,
            "campaign": "Christmas Traditional Service"
        }

    except Exception as e:
        logger.error(f"❌ Error triggering post-call maybe flow: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to trigger post-call follow-up: {str(e)}")


@app.post("/webhook/onboarding-start")
async def onboarding_start_webhook(request: OnboardingStartRequest, background_tasks: BackgroundTasks):
    """
    Handle onboarding start webhook.

    Triggered when: Client completes payment + DocuSign

    This endpoint:
    1. Receives payment confirmation from payment system
    2. Triggers onboarding_handler_flow
    3. Schedules 3 welcome emails (1h, Day 1, Day 3)
    """
    logger.info(f"🎉 Received onboarding start webhook for {request.email}")
    logger.info(f"   Business: {request.business_name}")
    logger.info(f"   Payment: ${request.payment_amount:.2f} on {request.payment_date}")
    logger.info(f"   Package: {request.package_type}")

    try:
        # Import flow
        from campaigns.christmas_campaign.flows.onboarding_handler import onboarding_handler_flow

        # Trigger flow in background
        def run_flow():
            result = onboarding_handler_flow(
                email=request.email,
                first_name=request.first_name,
                business_name=request.business_name,
                payment_confirmed=request.payment_confirmed,
                payment_amount=request.payment_amount,
                payment_date=request.payment_date,
                docusign_completed=request.docusign_completed,
                salon_address=request.salon_address,
                observation_dates=request.observation_dates,
                start_date=request.start_date,
                package_type=request.package_type
            )
            logger.info(f"✅ Onboarding flow completed: {result.get('status')}")

        background_tasks.add_task(run_flow)

        logger.info(f"✅ Onboarding flow triggered for {request.email}")

        return {
            "status": "accepted",
            "message": "Onboarding welcome sequence will begin shortly",
            "email": request.email,
            "payment_amount": request.payment_amount,
            "campaign": "Christmas Traditional Service"
        }

    except Exception as e:
        logger.error(f"❌ Error triggering onboarding flow: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to trigger onboarding: {str(e)}")


# ===== Startup Event =====

@app.on_event("startup")
async def startup_event():
    """
    Validate environment configuration on startup.
    """
    logger.info("🚀 Starting BusOS Email Sequence API...")

    # Check required environment variables
    required_vars = [
        "NOTION_TOKEN",
        "NOTION_CONTACTS_DB_ID",
        "NOTION_TEMPLATES_DB_ID",
        "RESEND_API_KEY"
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        logger.error(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("   Please configure .env file with required credentials")
    else:
        logger.info("✅ All required environment variables configured")

    # Check optional variables
    testing_mode = os.getenv("TESTING_MODE", "false").lower() == "true"
    discord_url = os.getenv("DISCORD_WEBHOOK_URL")

    logger.info(f"   Testing Mode: {testing_mode}")
    logger.info(f"   Discord Notifications: {'Enabled' if discord_url else 'Disabled'}")

    logger.info("✅ API ready to receive webhooks")


if __name__ == "__main__":
    import uvicorn

    # Run with uvicorn
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
