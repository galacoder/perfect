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
from flows.signup_handler import signup_handler_flow
from flows.assessment_handler import assessment_handler_flow

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
        from tasks.routing import determine_segment

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
