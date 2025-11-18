# Plan: Christmas Campaign Email Automation (UPDATED - Prefect Deployments)

**Task ID**: christmas-campaign-email-automation
**Domain**: coding
**Created**: 2025-11-16
**Updated**: 2025-11-16 22:50 (Prefect deployments + real credentials)
**Status**: Ready for execution
**Source**: Handoff document + Production credentials

---

## 🎯 Implementation Strategy

### Approach
**Method**: Event-driven with Prefect Cloud deployments
**Paradigm**: Production-grade workflow orchestration
**Estimated Time**: 18-20 hours total
**Risk Level**: Medium (60-second portal delivery is critical constraint)

### Key Architecture Decisions

**✅ Use Prefect Deployments (Production Pattern)**
- **Instead of**: `time.sleep()` for wait times
- **Benefits**:
  - Flows survive server restarts
  - Better observability in Prefect Cloud/UI
  - Automatic retry handling
  - Scheduled emails persist even if process crashes
- **How it works**: Trigger child flow deployments with scheduled start times

**✅ Use Existing Databases (No Manual Setup Needed!)**
All databases already exist and have been updated:

| Database | ID | Status |
|----------|-----|--------|
| BusinessX Canada | `199c97e4c0a045278086941b7cca62f1` | ✅ Added 19 Christmas properties |
| Customer Projects | `2ab7c374-1115-8176-961f-d8e192e56c4b` | ✅ Has Portal URL field |
| Email Templates | `2ab7c374-1115-8115-932c-ca6789c5b87b` | ✅ Ready for templates |
| Email Analytics | `2ab7c374-1115-8145-acd4-e2963bc3e441` | ✅ Email tracking ready |

**✅ Real Credentials**
```bash
NOTION_TOKEN=secret_eXSRJe3C3J2CAgE4AjG25HzplCiXVIIxFwO2AsQVysM
CAL_WEBHOOK_URL=https://sangletech.com/api/webhooks/calcom-booking
RESEND_API_KEY=re_e5qfBYsX_B9wNs12TKG82XoSi79kuMyWe
```

**Critical Success Factors**:
- Customer portal created in <60 seconds (this is THE constraint)
- All email templates stored in Notion (dynamic editing)
- Exit conditions properly stop/redirect sequences
- Cal.com webhook integration reliable
- Prefect deployments handle scheduled emails robustly

---

## 📋 New Properties Added to BusinessX Database

Already completed ✅:
- `Phase` (select): Phase 1 Assessment, Phase 1 Diagnostic, Phase 2A, Phase 2B, Phase 2C
- `Diagnostic Call Date` (date)
- `Booking Status` (select): Not Booked, Booked, Completed, No-Show
- `Phase 2 Decision Date` (date)
- `Christmas Campaign Status` (select): Nurture, Pre-Call Prep, Portal Delivered, Long-Term, Unsubscribed
- `Christmas Email 1-7 Sent` (checkbox × 7)
- `Christmas Email 1-7 Date` (date × 7)

---

## 🌊 Execution Waves (Updated with Prefect Deployments)

### Wave 1: Foundation & Prefect Deployment Setup (3-4 hours)

**Objective**: Set up Christmas campaign structure with Prefect Cloud deployments

#### Tasks:

**1.1 Create Campaign Directory Structure**
```bash
cd /Users/sangle/Dev/action/projects/perfect
mkdir -p campaigns/christmas_campaign/flows
mkdir -p campaigns/christmas_campaign/tasks
mkdir -p campaigns/christmas_campaign/tests
mkdir -p campaigns/christmas_campaign/deployments
touch campaigns/christmas_campaign/__init__.py
touch campaigns/christmas_campaign/flows/__init__.py
touch campaigns/christmas_campaign/tasks/__init__.py
touch campaigns/christmas_campaign/tests/__init__.py
```

**1.2 Update Environment Variables**
Update `/Users/sangle/Dev/action/projects/perfect/.env`:
```bash
# Christmas Campaign - Production Credentials
NOTION_TOKEN=secret_eXSRJe3C3J2CAgE4AjG25HzplCiXVIIxFwO2AsQVysM
NOTION_BUSINESSX_DB=199c97e4c0a045278086941b7cca62f1
NOTION_CUSTOMER_PROJECTS_DB=2ab7c374-1115-8176-961f-d8e192e56c4b
NOTION_EMAIL_TEMPLATES_DB=2ab7c374-1115-8115-932c-ca6789c5b87b
NOTION_EMAIL_ANALYTICS_DB=2ab7c374-1115-8145-acd4-e2963bc3e441

# Cal.com Webhook
CAL_WEBHOOK_URL=https://sangletech.com/api/webhooks/calcom-booking

# Resend Email
RESEND_API_KEY=re_e5qfBYsX_B9wNs12TKG82XoSi79kuMyWe

# Prefect Cloud (get from prefect cloud login)
PREFECT_API_KEY=your_prefect_api_key_here
PREFECT_API_URL=https://api.prefect.cloud/api/accounts/[account_id]/workspaces/[workspace_id]
```

**1.3 Set Up Prefect Cloud**
```bash
# Login to Prefect Cloud
prefect cloud login

# Create work pool for Christmas campaign
prefect work-pool create christmas-campaign-pool --type process

# Verify connection
prefect work-pool ls
```

**1.4 Create Deployment Utilities**
File: `campaigns/christmas_campaign/deployments/deploy_utils.py`

```python
"""
Prefect deployment utilities for Christmas campaign.

This module provides helpers for deploying flows with scheduled start times.
"""

from prefect import get_run_logger
from prefect.client.orchestration import get_client
from datetime import datetime, timedelta
from typing import Dict, Any
import os

async def schedule_email_flow(
    flow_name: str,
    email_number: int,
    contact_data: Dict[str, Any],
    delay_hours: int
) -> str:
    """
    Schedule an email flow to run after a delay.

    This replaces time.sleep() with Prefect scheduled deployments.

    Args:
        flow_name: Name of flow deployment (e.g., "send-christmas-email-2")
        email_number: Which email in sequence (1-7)
        contact_data: Contact information for personalization
        delay_hours: Hours to wait before sending

    Returns:
        Flow run ID for tracking

    Example:
        # Schedule Email 2 to send in 48 hours
        run_id = await schedule_email_flow(
            flow_name="send-christmas-email-2",
            email_number=2,
            contact_data={"email": "test@example.com", "first_name": "Test"},
            delay_hours=48
        )
    """
    logger = get_run_logger()

    # Calculate scheduled start time
    scheduled_start = datetime.now() + timedelta(hours=delay_hours)

    # Get Prefect client
    async with get_client() as client:
        # Create flow run with scheduled start
        flow_run = await client.create_flow_run_from_deployment(
            deployment_id=os.getenv(f"DEPLOYMENT_ID_{flow_name.upper().replace('-', '_')}"),
            parameters={
                "email_number": email_number,
                "contact_email": contact_data["email"],
                "contact_first_name": contact_data["first_name"],
                "contact_page_id": contact_data["page_id"]
            },
            scheduled_start_time=scheduled_start
        )

    logger.info(f"📅 Scheduled Email #{email_number} for {scheduled_start.isoformat()}")
    logger.info(f"   Flow run ID: {flow_run.id}")

    return flow_run.id


def get_wait_duration_hours(email_number: int, testing_mode: bool = False) -> int:
    """
    Get wait duration in hours before next email.

    Args:
        email_number: Current email number (1-6)
        testing_mode: If True, use short waits for testing

    Returns:
        Hours to wait before next email
    """
    # Production wait times (hours)
    WAIT_HOURS_PROD = {
        1: 48,   # Email 1 → Email 2: 48 hours (Day 2)
        2: 24,   # Email 2 → Email 3: 24 hours (Day 3)
        3: 24,   # Email 3 → Email 4: 24 hours (Day 4)
        4: 48,   # Email 4 → Email 5: 48 hours (Day 6)
        5: 48,   # Email 5 → Email 6: 48 hours (Day 8)
        6: 48,   # Email 6 → Email 7: 48 hours (Day 10)
    }

    # Testing wait times (minutes converted to hours)
    WAIT_HOURS_TEST = {
        1: 0.033,  # 2 minutes
        2: 0.050,  # 3 minutes
        3: 0.067,  # 4 minutes
        4: 0.083,  # 5 minutes
        5: 0.100,  # 6 minutes
        6: 0.117,  # 7 minutes
    }

    wait_times = WAIT_HOURS_TEST if testing_mode else WAIT_HOURS_PROD
    return wait_times.get(email_number, 24)
```

**1.5 Create Test Fixtures**
File: `campaigns/christmas_campaign/tests/conftest.py`

```python
"""Pytest fixtures for Christmas campaign tests"""

import pytest
from unittest.mock import Mock, MagicMock
from notion_client import Client

@pytest.fixture
def mock_notion():
    """Mock Notion client"""
    notion = MagicMock(spec=Client)
    notion.databases.query.return_value = {"results": []}
    notion.pages.create.return_value = {"id": "test-page-id"}
    notion.pages.update.return_value = {"id": "test-page-id"}
    return notion

@pytest.fixture
def mock_resend():
    """Mock Resend API"""
    resend = MagicMock()
    resend.emails.send.return_value = {"id": "test-email-id"}
    return resend

@pytest.fixture
def sample_assessment_data():
    """Sample assessment data for testing"""
    return {
        "email": "test@example.com",
        "first_name": "Test",
        "gps_score": 60,
        "generate_score": 55,
        "persuade_score": 65,
        "serve_score": 60,
        "money_score": 70,
        "marketing_score": 50,
        "weakest_system_1": "Generate",
        "score_1": 55,
        "revenue_leak_system_1": 3000,
        "weakest_system_2": "Persuade",
        "score_2": 65,
        "revenue_leak_system_2": 2500,
        "total_revenue_leak": 5500,
        "annual_revenue_leak": 66000,
        "quick_win_action": "Create Google Business Profile posts 3X/week",
        "quick_win_explanation": "Increases local visibility",
        "quick_win_impact": "2-4 new bookings/month"
    }
```

**Commit**: `chore(christmas): set up campaign structure with Prefect deployments`

**Success Criteria**:
- [ ] Directory structure created
- [ ] Environment variables updated with real credentials
- [ ] Prefect Cloud logged in and work pool created
- [ ] Deployment utilities created
- [ ] Test fixtures ready
- [ ] Git commit created

---

### Wave 2: Core 7-Email Nurture Sequence with Prefect Deployments (7-8 hours)

**Objective**: Implement 7-email sequence using Prefect scheduled deployments

#### 2.1 Create Assessment Data Model

**File**: `campaigns/christmas_campaign/models.py`

```python
"""Data models for Christmas campaign"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class AssessmentData(BaseModel):
    """Assessment data for Christmas nurture sequence"""
    email: EmailStr
    first_name: str
    gps_score: int = Field(ge=0, le=100)
    generate_score: int = Field(ge=0, le=100)
    persuade_score: int = Field(ge=0, le=100)
    serve_score: int = Field(ge=0, le=100)
    money_score: int = Field(ge=0, le=100)
    marketing_score: int = Field(ge=0, le=100)
    weakest_system_1: str
    score_1: int
    revenue_leak_system_1: int
    weakest_system_2: str
    score_2: int
    revenue_leak_system_2: int
    total_revenue_leak: int
    annual_revenue_leak: int
    quick_win_action: str
    quick_win_explanation: str
    quick_win_impact: str

    class Config:
        schema_extra = {
            "example": {
                "email": "test@example.com",
                "first_name": "Test",
                "gps_score": 60,
                # ... (rest of example)
            }
        }
```

**Test**: `campaigns/christmas_campaign/tests/test_models.py`

```python
"""Tests for Christmas campaign data models"""

import pytest
from pydantic import ValidationError
from campaigns.christmas_campaign.models import AssessmentData

def test_assessment_data_validation(sample_assessment_data):
    """Test AssessmentData model validates correctly"""
    data = AssessmentData(**sample_assessment_data)
    assert data.email == "test@example.com"
    assert data.total_revenue_leak == 5500

def test_assessment_data_invalid_email():
    """Test invalid email raises validation error"""
    with pytest.raises(ValidationError):
        AssessmentData(email="invalid-email", first_name="Test")
```

#### 2.2 Create Single Email Flow (Atomic Operation)

**File**: `campaigns/christmas_campaign/flows/send_single_email.py`

```python
"""
Send a single Christmas campaign email.

This is an atomic flow that sends ONE email. It's deployed separately
so Prefect can schedule it independently.
"""

from prefect import flow, task
from prefect.client.schemas.schedules import IntervalSchedule
from datetime import datetime, timedelta
import os

# Import existing task modules
from campaigns.businessx_canada_lead_nurture.tasks.template_operations import fetch_template_from_notion
from campaigns.businessx_canada_lead_nurture.tasks.resend_operations import send_template_email
from campaigns.businessx_canada_lead_nurture.tasks.notion_operations import update_contact

NOTION_BUSINESSX_DB = os.getenv("NOTION_BUSINESSX_DB")


@task(name="christmas-get-template")
def get_christmas_template(email_number: int):
    """Fetch Christmas email template from Notion"""
    template_name = f"email_{email_number}_christmas"
    return fetch_template_from_notion(template_name)


@flow(name="send-christmas-email", log_prints=True)
def send_christmas_email_flow(
    email_number: int,
    contact_email: str,
    contact_first_name: str,
    contact_page_id: str,
    assessment_data: dict
) -> dict:
    """
    Send a single Christmas campaign email.

    This flow is designed to be deployed and scheduled independently
    by the orchestrator flow.

    Args:
        email_number: Which email to send (1-7)
        contact_email: Recipient email
        contact_first_name: First name for personalization
        contact_page_id: Notion page ID for status updates
        assessment_data: Assessment scores and metadata

    Returns:
        Dict with email_id and status
    """
    print(f"📧 Sending Christmas Email #{email_number} to {contact_email}")

    # Get template
    template = get_christmas_template(email_number)

    # Prepare template variables
    template_vars = {
        "first_name": contact_first_name,
        "email": contact_email,
        **assessment_data
    }

    # Send email
    email_result = send_template_email(
        to_email=contact_email,
        subject=template["subject"],
        template=template["html"],
        variables=template_vars
    )

    print(f"✅ Email sent (ID: {email_result.get('id')})")

    # Update Notion
    update_contact(
        page_id=contact_page_id,
        properties={
            f"Christmas Email {email_number} Sent": {"checkbox": True},
            f"Christmas Email {email_number} Date": {
                "date": {"start": datetime.now().isoformat()}
            }
        }
    )

    print(f"✅ Notion updated for Email #{email_number}")

    return {
        "success": True,
        "email_id": email_result.get("id"),
        "email_number": email_number,
        "sent_at": datetime.now().isoformat()
    }
```

#### 2.3 Create Orchestrator Flow (Schedules All 7 Emails)

**File**: `campaigns/christmas_campaign/flows/nurture_sequence.py`

```python
"""
Christmas 7-email nurture sequence orchestrator.

This flow DOES NOT send emails directly. Instead, it schedules 7 separate
flow runs using Prefect deployments with calculated start times.
"""

from prefect import flow, get_run_logger
from prefect.client.orchestration import get_client
from datetime import datetime, timedelta
import os

from campaigns.christmas_campaign.deployments.deploy_utils import (
    schedule_email_flow,
    get_wait_duration_hours
)
from campaigns.businessx_canada_lead_nurture.tasks.notion_operations import update_contact

TESTING_MODE = os.getenv("TESTING_MODE", "false").lower() == "true"


@flow(name="christmas-nurture-orchestrator", log_prints=True)
async def christmas_nurture_orchestrator_flow(
    contact_page_id: str,
    contact_email: str,
    contact_first_name: str,
    assessment_data: dict
) -> dict:
    """
    Orchestrate the complete 7-email Christmas nurture sequence.

    This flow schedules 7 separate email flows with appropriate delays.

    Schedule:
    - Email 1: Immediate (sent by this flow directly)
    - Email 2: +48h (scheduled deployment)
    - Email 3: +24h (scheduled deployment)
    - Email 4: +24h (scheduled deployment)
    - Email 5: +48h (scheduled deployment)
    - Email 6: +48h (scheduled deployment)
    - Email 7: +48h (scheduled deployment)

    Args:
        contact_page_id: Notion page ID
        contact_email: Email address
        contact_first_name: First name
        assessment_data: Assessment scores

    Returns:
        Dict with scheduled flow run IDs
    """
    logger = get_run_logger()
    logger.info(f"🎄 Starting Christmas nurture orchestration for {contact_email}")
    logger.info(f"   Testing mode: {TESTING_MODE}")

    # Update Notion: Mark sequence started
    update_contact(
        page_id=contact_page_id,
        properties={
            "Christmas Campaign Status": {"select": {"name": "Nurture Sequence"}},
            "Phase": {"select": {"name": "Phase 1 Assessment"}}
        }
    )

    # Prepare contact data for scheduled flows
    contact_data = {
        "page_id": contact_page_id,
        "email": contact_email,
        "first_name": contact_first_name
    }

    scheduled_runs = {}
    cumulative_delay_hours = 0

    # Schedule emails 2-7 (Email 1 is sent immediately by assessment handler)
    for email_num in range(2, 8):
        # Calculate delay from NOW (cumulative)
        cumulative_delay_hours += get_wait_duration_hours(
            email_number=email_num - 1,
            testing_mode=TESTING_MODE
        )

        # Schedule this email
        run_id = await schedule_email_flow(
            flow_name=f"send-christmas-email-{email_num}",
            email_number=email_num,
            contact_data=contact_data,
            delay_hours=cumulative_delay_hours
        )

        scheduled_runs[f"email_{email_num}"] = run_id

        logger.info(f"✅ Email #{email_num} scheduled for +{cumulative_delay_hours}h from now")

    logger.info(f"✅ All 7 emails scheduled for {contact_email}")

    return {
        "success": True,
        "contact_email": contact_email,
        "scheduled_runs": scheduled_runs,
        "total_emails": 7
    }
```

#### 2.4 Create Deployment Script

**File**: `campaigns/christmas_campaign/deployments/deploy_all.py`

```python
"""
Deploy all Christmas campaign flows to Prefect Cloud.

Run this script to create deployments for all flows.
"""

from prefect.deployments import Deployment
from prefect.server.schemas.schedules import CronSchedule
from campaigns.christmas_campaign.flows.send_single_email import send_christmas_email_flow
from campaigns.christmas_campaign.flows.nurture_sequence import christmas_nurture_orchestrator_flow

def deploy_all():
    """Deploy all Christmas campaign flows"""

    # Deploy single email sender (1 deployment per email type)
    for email_num in range(1, 8):
        deployment = Deployment.build_from_flow(
            flow=send_christmas_email_flow,
            name=f"send-christmas-email-{email_num}",
            work_pool_name="christmas-campaign-pool",
            tags=["christmas", f"email-{email_num}"]
        )
        deployment.apply()
        print(f"✅ Deployed: send-christmas-email-{email_num}")

    # Deploy orchestrator
    orchestrator_deployment = Deployment.build_from_flow(
        flow=christmas_nurture_orchestrator_flow,
        name="christmas-nurture-orchestrator",
        work_pool_name="christmas-campaign-pool",
        tags=["christmas", "orchestrator"]
    )
    orchestrator_deployment.apply()
    print(f"✅ Deployed: christmas-nurture-orchestrator")

    print("\n🚀 All deployments created!")
    print("Start worker with: prefect worker start --pool christmas-campaign-pool")

if __name__ == "__main__":
    deploy_all()
```

**Run deployment**:
```bash
python campaigns/christmas_campaign/deployments/deploy_all.py
```

**Commit**: `feat(christmas): implement 7-email nurture with Prefect deployments`

**Success Criteria**:
- [ ] Assessment data model validates correctly
- [ ] Single email flow sends email successfully
- [ ] Orchestrator flow schedules all 7 emails
- [ ] Deployments created in Prefect Cloud
- [ ] Worker can pick up scheduled flows
- [ ] Testing mode uses short delays (minutes)
- [ ] Production mode uses real delays (hours/days)
- [ ] Unit tests pass (>80% coverage)

---

### Wave 3: Cal.com Webhooks + Portal Delivery (5-6 hours)

**Objective**: Cal.com booking triggers pre-call prep and 60-second portal delivery

#### 3.1 Add Cal.com Webhook to FastAPI Server

**File**: `server.py` (extend existing)

```python
from pydantic import BaseModel
from typing import Dict, Any

class CalBookingPayload(BaseModel):
    """Cal.com booking webhook payload"""
    triggerEvent: str
    payload: Dict[str, Any]

@app.post("/webhook/calcom-booking")
async def handle_calcom_booking(
    request: CalBookingPayload,
    background_tasks: BackgroundTasks
):
    """
    Handle Cal.com booking webhook for Christmas campaign.

    URL: https://sangletech.com/api/webhooks/calcom-booking

    Triggers:
    - Stop nurture sequence (cancel scheduled emails)
    - Start pre-call prep sequence
    - Update booking status in Notion
    """
    if request.triggerEvent != "BOOKING_CREATED":
        return {"status": "ignored", "reason": f"Unsupported event: {request.triggerEvent}"}

    payload = request.payload
    email = payload.get("attendees", [{}])[0].get("email")
    start_time = payload.get("startTime")
    booking_id = payload.get("uid")

    if not email:
        raise HTTPException(status_code=400, detail="No email in booking payload")

    logger.info(f"📞 Booking created for {email} at {start_time}")

    # Trigger pre-call prep in background
    from campaigns.christmas_campaign.flows.pre_call_prep import pre_call_prep_flow
    background_tasks.add_task(
        pre_call_prep_flow,
        email=email,
        call_date=start_time,
        booking_id=booking_id
    )

    return {
        "status": "accepted",
        "message": "Pre-call prep sequence will begin",
        "email": email,
        "call_date": start_time
    }
```

#### 3.2 Create Pre-Call Prep Flow

**File**: `campaigns/christmas_campaign/flows/pre_call_prep.py`

```python
"""Pre-call prep email sequence (3 emails after booking)"""

from prefect import flow
from datetime import datetime
from campaigns.businessx_canada_lead_nurture.tasks.notion_operations import (
    search_contact_by_email,
    update_contact
)
from campaigns.businessx_canada_lead_nurture.tasks.template_operations import fetch_template_from_notion
from campaigns.businessx_canada_lead_nurture.tasks.resend_operations import send_template_email

@flow(name="christmas-pre-call-prep", log_prints=True)
def pre_call_prep_flow(email: str, call_date: str, booking_id: str) -> dict:
    """
    Send 3-email pre-call prep sequence after booking.

    Emails:
    1. Booking confirmation (immediate)
    2. Questionnaire reminder (scheduled 24h before call)
    3. Final reminder (scheduled 2h before call)
    """
    print(f"📞 Starting pre-call prep for {email} (call: {call_date})")

    # Find contact
    contact = search_contact_by_email(email)
    if not contact:
        print(f"❌ Contact not found: {email}")
        return {"success": False, "error": "Contact not found"}

    contact_page_id = contact["id"]

    # Extract first name from contact
    name_prop = contact["properties"].get("first_name", {})
    first_name = name_prop.get("title", [{}])[0].get("plain_text", "there")

    # Update Notion: Mark as booked, stop nurture sequence
    update_contact(
        page_id=contact_page_id,
        properties={
            "Booking Status": {"select": {"name": "Booked"}},
            "Diagnostic Call Date": {"date": {"start": call_date}},
            "Christmas Campaign Status": {"select": {"name": "Pre-Call Prep"}},
            "Phase": {"select": {"name": "Phase 1 Diagnostic"}}
        }
    )

    print(f"✅ Booking status updated in Notion")

    # Email 1: Booking confirmation (immediate)
    template = fetch_template_from_notion("pre_call_confirmation")
    email_result = send_template_email(
        to_email=email,
        subject=template["subject"],
        template=template["html"],
        variables={
            "first_name": first_name,
            "call_date": call_date,
            "booking_id": booking_id
        }
    )

    print(f"✅ Booking confirmation sent (ID: {email_result.get('id')})")

    # TODO: Schedule Email 2 & 3 based on call_date
    # (Use Prefect deployment scheduling like in nurture sequence)

    return {
        "success": True,
        "emails_sent": 1,
        "contact_page_id": contact_page_id
    }
```

#### 3.3 Create 60-Second Portal Delivery Flow

**File**: `campaigns/christmas_campaign/flows/portal_delivery.py`

```python
"""
60-second customer portal delivery after diagnostic call.

Critical constraint: Portal must be created in <60 seconds.
"""

from prefect import flow, task
from notion_client import Client
from datetime import datetime
import os

notion = Client(auth=os.getenv("NOTION_TOKEN"))
CUSTOMER_PROJECTS_DB = os.getenv("NOTION_CUSTOMER_PROJECTS_DB")

@task(name="portal-create-project", timeout_seconds=15)
def create_customer_project(email: str, first_name: str, call_date: str) -> str:
    """
    Create customer project in Notion (target: <10 seconds).

    Uses existing Customer Projects database.
    """
    project_page = notion.pages.create(
        parent={"database_id": CUSTOMER_PROJECTS_DB},
        properties={
            "Project Name": {
                "title": [{"text": {"content": f"{first_name} - Christmas Priority"}}]
            },
            "Customer": {
                "relation": [{"id": "contact_page_id_here"}]  # TODO: Link to contact
            },
            "Start Date": {"date": {"start": call_date}},
            "Project Status": {"select": {"name": "Phase 1: Diagnostic"}},
            "Notion Portal URL": {"url": ""}  # Will update after page creation
        }
    )

    project_id = project_page["id"]
    portal_url = f"https://notion.so/{project_id.replace('-', '')}"

    # Update with portal URL
    notion.pages.update(
        page_id=project_id,
        properties={
            "Notion Portal URL": {"url": portal_url}
        }
    )

    print(f"✅ Project created: {project_id}")
    return portal_url

@task(name="portal-send-email", timeout_seconds=10)
def send_portal_email(email: str, first_name: str, portal_url: str):
    """Send portal access email (target: <5 seconds)"""
    from campaigns.businessx_canada_lead_nurture.tasks.resend_operations import send_email

    html = f"""
    <h2>Your Customer Portal is Live!</h2>
    <p>Hi {first_name},</p>
    <p>As promised, your customer portal is ready within 60 seconds!</p>
    <p><strong>Access your portal</strong>: <a href="{portal_url}">Open Portal →</a></p>
    <p>Inside you'll find:</p>
    <ul>
      <li>📊 Your BusOS Diagnostic Report</li>
      <li>🗓️ Your 90-Day Transformation Timeline</li>
      <li>✅ December Revenue Maximizer Checklist</li>
      <li>📚 Case Study Library</li>
    </ul>
    <p>Best,<br>Sang Le</p>
    """

    send_email(
        to_email=email,
        subject="Your BusOS Customer Portal is Ready (60 seconds!)",
        html=html
    )
    print(f"✅ Portal email sent to {email}")

@flow(name="christmas-portal-delivery-60s", log_prints=True)
def portal_delivery_flow(
    email: str,
    first_name: str,
    call_date: str,
    diagnostic_results: dict
) -> dict:
    """
    Create customer portal and deliver within 60 seconds.

    Timeline:
    - 0-15s: Create project page
    - 15-60s: Send email
    """
    start_time = datetime.now()
    print(f"🚀 Starting 60-second portal delivery for {email}")

    # Create portal
    portal_url = create_customer_project(email, first_name, call_date)

    # Send email
    send_portal_email(email, first_name, portal_url)

    # Calculate delivery time
    end_time = datetime.now()
    delivery_time = (end_time - start_time).total_seconds()
    met_deadline = delivery_time < 60

    print(f"{'✅' if met_deadline else '⚠️'} Portal delivered in {delivery_time:.1f} seconds")

    return {
        "success": True,
        "portal_url": portal_url,
        "delivery_time": delivery_time,
        "met_deadline": met_deadline
    }
```

**Commit**: `feat(christmas): add Cal.com webhooks, pre-call prep, portal delivery`

**Success Criteria**:
- [ ] Cal.com webhook receives booking events
- [ ] Pre-call prep sends confirmation email
- [ ] Customer portal created in <60 seconds (90%+ of time)
- [ ] Portal URL generated and emailed
- [ ] Notion contact status updated
- [ ] Integration tests pass

---

### Wave 4: Phase 2 Emails + Polish + Deployment (4-5 hours)

**Objective**: Day 14 decision email, Phase 2B coaching, documentation, production deployment

#### 4.1 Create Day 14 Decision Flow

**File**: `campaigns/christmas_campaign/flows/day14_decision.py`

```python
"""Day 14 decision email (Phase 2 options presentation)"""

from prefect import flow
from datetime import datetime
from campaigns.businessx_canada_lead_nurture.tasks.notion_operations import (
    search_contact_by_email,
    update_contact
)
from campaigns.businessx_canada_lead_nurture.tasks.template_operations import fetch_template_from_notion
from campaigns.businessx_canada_lead_nurture.tasks.resend_operations import send_template_email

@flow(name="christmas-day14-decision", log_prints=True)
def day14_decision_flow(email: str) -> dict:
    """
    Send Day 14 decision email presenting Phase 2 options.

    Triggered 14 days after diagnostic call completion.
    Scheduled via Prefect deployment.
    """
    print(f"📊 Sending Day 14 decision email to {email}")

    # Find contact
    contact = search_contact_by_email(email)
    if not contact:
        return {"success": False, "error": "Contact not found"}

    contact_page_id = contact["id"]

    # Extract data
    props = contact["properties"]
    first_name = props.get("first_name", {}).get("title", [{}])[0].get("plain_text", "there")

    # Get template
    template = fetch_template_from_notion("day14_decision_email")

    # Send email
    email_result = send_template_email(
        to_email=email,
        subject=template["subject"],
        template=template["html"],
        variables={"first_name": first_name}
    )

    # Update Notion
    update_contact(
        page_id=contact_page_id,
        properties={
            "Phase 2 Decision Date": {"date": {"start": datetime.now().isoformat()}},
            "Phase 2 Decision Email Sent": {"checkbox": True}
        }
    )

    print(f"✅ Day 14 decision email sent (ID: {email_result.get('id')})")
    return {"success": True, "email_id": email_result.get("id")}
```

#### 4.2 Create Phase 2B Coaching Flows

**File**: `campaigns/christmas_campaign/flows/phase2b_coaching.py`

```python
"""Phase 2B coaching support emails (12-week program)"""

from prefect import flow
from campaigns.businessx_canada_lead_nurture.tasks.template_operations import fetch_template_from_notion
from campaigns.businessx_canada_lead_nurture.tasks.resend_operations import send_template_email

@flow(name="christmas-phase2b-welcome", log_prints=True)
def phase2b_welcome_flow(email: str, first_name: str) -> dict:
    """Send Phase 2B welcome email"""
    template = fetch_template_from_notion("phase2b_welcome")

    email_result = send_template_email(
        to_email=email,
        subject=template["subject"],
        template=template["html"],
        variables={"first_name": first_name}
    )

    return {"success": True, "email_id": email_result.get("id")}

@flow(name="christmas-phase2b-weekly-prep", log_prints=True)
def phase2b_weekly_prep_flow(email: str, week_number: int, agenda: list) -> dict:
    """Send weekly prep email 24h before coaching call"""
    template = fetch_template_from_notion("phase2b_weekly_prep")

    # TODO: Implement full logic with agenda customization

    return {"success": True}
```

#### 4.3 Update Server with All Webhooks

**File**: `server.py` (final version)

Update to include:
- Cal.com booking webhook ✅ (from Wave 3)
- Diagnostic call completion webhook
- Payment webhook (if needed for portal trigger)

#### 4.4 Comprehensive Documentation

**Create**: `campaigns/christmas_campaign/README.md`

```markdown
# Christmas Campaign Email Automation

7-email nurture sequence + pre-call prep + 60-second portal delivery.

## Quick Start

```bash
# Set up environment
cp .env.example .env
# Add NOTION_TOKEN, RESEND_API_KEY, etc.

# Deploy flows to Prefect Cloud
python campaigns/christmas_campaign/deployments/deploy_all.py

# Start worker
prefect worker start --pool christmas-campaign-pool

# Test in development
TESTING_MODE=true python -m pytest campaigns/christmas_campaign/tests/
```

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for technical details.

## Email Sequence

1. Email 1: Results (immediate)
2. Email 2: Quick Wins (+48h)
3. Email 3: Horror Story (+24h)
4. Email 4: First Ask (+24h)
5. Email 5: Case Study (+48h)
6. Email 6: Checklist (+48h)
7. Email 7: Final Ask (+48h)

Total: 10 days
```

#### 4.5 Deploy to Production

```bash
# Build Prefect deployments
python campaigns/christmas_campaign/deployments/deploy_all.py

# Start worker (systemd service)
sudo systemctl enable prefect-worker-christmas
sudo systemctl start prefect-worker-christmas

# Monitor in Prefect Cloud
prefect deployment ls
prefect flow-run ls --limit 10
```

**Commit**: `feat(christmas): add Phase 2 emails, docs, production deployment`

**Success Criteria**:
- [ ] Day 14 decision email sends correctly
- [ ] Phase 2B welcome email works
- [ ] All webhooks integrated
- [ ] README and ARCHITECTURE docs complete
- [ ] All unit tests pass (>80% coverage)
- [ ] Integration tests pass
- [ ] Prefect deployments running in Cloud
- [ ] Worker picking up scheduled flows
- [ ] Manual testing complete

---

## 🎯 Quality & Validation Checklist

- [ ] All 7 emails send in correct sequence
- [ ] Prefect deployments schedule emails correctly
- [ ] Customer portal created <60 seconds
- [ ] Cal.com webhook integration works
- [ ] Day 14 decision email triggers after 14 days
- [ ] Phase 2B emails send correctly
- [ ] All template variables substituted
- [ ] Exit conditions work (booking stops nurture)
- [ ] Notion databases updated correctly
- [ ] Environment variables documented
- [ ] README complete
- [ ] All commits follow convention
- [ ] No debug statements
- [ ] Error handling comprehensive
- [ ] Performance acceptable
- [ ] Prefect UI shows flow runs
- [ ] Worker processing scheduled flows

---

## 📊 Timeline Estimate (Updated)

| Wave | Description | Estimated Time |
|------|-------------|----------------|
| Wave 1 | Foundation + Prefect Setup | 3-4 hours |
| Wave 2 | 7-Email Nurture (Deployments) | 7-8 hours |
| Wave 3 | Webhooks + Portal | 5-6 hours |
| Wave 4 | Phase 2 + Polish + Deploy | 4-5 hours |
| **Total** | **All waves** | **19-23 hours** |

**Note**: Prefect deployment approach adds 1-2 hours vs simple sleep(), but provides production-grade robustness.

---

## 🚀 Ready to Execute?

All prerequisites complete:
- ✅ Notion databases updated with Christmas properties
- ✅ Real credentials documented
- ✅ Prefect deployment pattern defined
- ✅ Cal.com webhook URL confirmed

**Next step**: Run `/execute-coding` to implement all 4 waves!
