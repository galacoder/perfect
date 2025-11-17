"""
Pydantic models for Christmas Campaign data validation.

This module defines data models for:
1. Assessment data
2. Contact data
3. Email data
4. Booking data

Author: Christmas Campaign Team
Created: 2025-11-16
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Literal
from datetime import datetime


# ==============================================================================
# Assessment Models
# ==============================================================================

class AssessmentData(BaseModel):
    """
    Assessment data from BusOS assessment completion.

    Used for:
    - Segment classification (CRITICAL/URGENT/OPTIMIZE)
    - Triggering email nurture sequence
    - Personalizing email content
    """
    email: EmailStr = Field(..., description="Contact email address")
    red_systems: int = Field(0, ge=0, le=8, description="Number of red (broken) systems")
    orange_systems: int = Field(0, ge=0, le=8, description="Number of orange (struggling) systems")
    yellow_systems: int = Field(0, ge=0, le=8, description="Number of yellow (functional) systems")
    green_systems: int = Field(0, ge=0, le=8, description="Number of green (optimized) systems")
    assessment_score: int = Field(..., ge=0, le=100, description="Overall BusOS score")
    first_name: Optional[str] = Field(None, description="Contact first name")
    business_name: Optional[str] = Field(None, description="Business name")

    @validator('assessment_score')
    def validate_total_systems(cls, v, values):
        """Validate that total systems add up to 8."""
        total = (
            values.get('red_systems', 0) +
            values.get('orange_systems', 0) +
            values.get('yellow_systems', 0) +
            values.get('green_systems', 0)
        )
        if total != 8:
            raise ValueError(f"Total systems must equal 8, got {total}")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "email": "john@testcorp.com",
                "red_systems": 2,
                "orange_systems": 3,
                "yellow_systems": 2,
                "green_systems": 1,
                "assessment_score": 35,
                "first_name": "John",
                "business_name": "Test Corp"
            }
        }


# ==============================================================================
# Contact Models
# ==============================================================================

class ContactData(BaseModel):
    """
    Contact data for email personalization and tracking.

    Used for:
    - Email template variable substitution
    - Notion database updates
    - Flow scheduling
    """
    email: EmailStr = Field(..., description="Contact email address")
    first_name: str = Field("there", description="Contact first name (default: 'there')")
    business_name: str = Field("your business", description="Business name (default: 'your business')")
    segment: Literal["CRITICAL", "URGENT", "OPTIMIZE"] = Field("OPTIMIZE", description="Contact segment")
    phase: Literal[
        "Phase 1 Assessment",
        "Phase 1 Diagnostic",
        "Phase 2A Done-For-You",
        "Phase 2B Coaching",
        "Phase 2C DIY"
    ] = Field("Phase 1 Assessment", description="Current phase in customer journey")
    assessment_score: Optional[int] = Field(None, ge=0, le=100, description="BusOS score")
    notion_page_id: Optional[str] = Field(None, description="Notion page ID for this contact")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "john@testcorp.com",
                "first_name": "John",
                "business_name": "Test Corp",
                "segment": "URGENT",
                "phase": "Phase 1 Assessment",
                "assessment_score": 45,
                "notion_page_id": "abc123"
            }
        }


# ==============================================================================
# Email Models
# ==============================================================================

class EmailTemplate(BaseModel):
    """
    Email template data from Notion database.

    Used for:
    - Storing template content
    - Variable substitution
    - Email sending
    """
    template_id: str = Field(..., description="Unique template identifier (e.g., 'christmas_email_1')")
    subject: str = Field(..., description="Email subject line")
    html_body: str = Field(..., description="HTML email body with {{variable}} placeholders")
    segment: Optional[Literal["CRITICAL", "URGENT", "OPTIMIZE", "ALL"]] = Field(
        "ALL",
        description="Target segment (ALL = universal)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "template_id": "christmas_email_1",
                "subject": "Your BusOS Assessment Results",
                "html_body": "<html><body>Hi {{first_name}}...</body></html>",
                "segment": "ALL"
            }
        }


class EmailVariables(BaseModel):
    """
    Variables for email template substitution.

    Used for:
    - Personalizing email content
    - Dynamic content insertion
    """
    first_name: str = Field("there", description="Contact first name")
    business_name: str = Field("your business", description="Business name")
    assessment_score: Optional[int] = Field(None, description="BusOS score")
    segment: Optional[str] = Field(None, description="Contact segment")
    diagnostic_call_date: Optional[str] = Field(None, description="Scheduled call date")
    portal_url: Optional[str] = Field(None, description="Customer portal URL")

    class Config:
        json_schema_extra = {
            "example": {
                "first_name": "John",
                "business_name": "Test Corp",
                "assessment_score": 45,
                "segment": "URGENT"
            }
        }


# ==============================================================================
# Booking Models
# ==============================================================================

class BookingData(BaseModel):
    """
    Cal.com booking webhook data.

    Used for:
    - Triggering pre-call prep sequence
    - Updating contact phase
    - Scheduling follow-up emails
    """
    email: EmailStr = Field(..., description="Attendee email address")
    booking_id: str = Field(..., description="Cal.com booking ID")
    booking_uid: str = Field(..., description="Cal.com booking UID")
    call_title: str = Field(..., description="Call title")
    start_time: datetime = Field(..., description="Scheduled start time (ISO 8601)")
    end_time: datetime = Field(..., description="Scheduled end time (ISO 8601)")
    attendee_name: str = Field(..., description="Attendee full name")
    attendee_timezone: str = Field("America/Toronto", description="Attendee timezone")
    business_name: Optional[str] = Field(None, description="Business name from metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "john@testcorp.com",
                "booking_id": "12345",
                "booking_uid": "booking-uid-123",
                "call_title": "BusOS Diagnostic Call",
                "start_time": "2025-11-20T10:00:00Z",
                "end_time": "2025-11-20T11:00:00Z",
                "attendee_name": "John Doe",
                "attendee_timezone": "America/Toronto",
                "business_name": "Test Corp"
            }
        }


class CallCompleteData(BaseModel):
    """
    Data for completed diagnostic call webhook.

    Used for:
    - Triggering customer portal delivery
    - Updating contact phase
    - Recording call notes
    """
    email: EmailStr = Field(..., description="Contact email address")
    call_date: str = Field(..., description="Call completion date (YYYY-MM-DD)")
    call_notes: Optional[str] = Field(None, description="Call notes/summary")
    next_steps: Literal[
        "Phase 2A Done-For-You",
        "Phase 2B Coaching",
        "Phase 2C DIY",
        "No Phase 2"
    ] = Field(..., description="Recommended next phase")
    portal_url: Optional[str] = Field(None, description="Customer portal URL (if created)")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "john@testcorp.com",
                "call_date": "2025-11-20",
                "call_notes": "Great call, customer ready for Done-For-You",
                "next_steps": "Phase 2A Done-For-You",
                "portal_url": "https://notion.so/customer-portal-123"
            }
        }


# ==============================================================================
# Flow Run Models
# ==============================================================================

class FlowRunMetadata(BaseModel):
    """
    Metadata for tracking flow runs in Notion.

    Used for:
    - Recording email send status
    - Tracking flow run IDs
    - Debugging and monitoring
    """
    email_number: int = Field(..., ge=1, le=7, description="Email number in sequence (1-7)")
    flow_run_id: str = Field(..., description="Prefect flow run ID")
    scheduled_time: datetime = Field(..., description="Scheduled send time")
    actual_send_time: Optional[datetime] = Field(None, description="Actual send time (if sent)")
    status: Literal["scheduled", "running", "completed", "failed", "cancelled"] = Field(
        "scheduled",
        description="Flow run status"
    )
    error_message: Optional[str] = Field(None, description="Error message if failed")

    class Config:
        json_schema_extra = {
            "example": {
                "email_number": 1,
                "flow_run_id": "flow-run-id-123",
                "scheduled_time": "2025-11-16T12:00:00Z",
                "actual_send_time": "2025-11-16T12:00:05Z",
                "status": "completed"
            }
        }
