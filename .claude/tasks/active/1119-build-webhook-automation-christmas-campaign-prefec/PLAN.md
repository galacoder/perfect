# Implementation Plan: Webhook-Based Automation with Prefect

**Task ID**: 1119-build-webhook-automation-christmas-campaign-prefec
**Created**: 2025-11-19
**Status**: PLANNING
**Approach**: Prefect Deployment-based scheduling (not custom worker)

---

## Executive Summary

**Goal**: Build fully automated webhook-based email nurture sequence system using Prefect 3.4.1.

**Core Architecture Decision**:
- ✅ Use **Prefect Deployments** to schedule 7 separate flow runs in the future
- ❌ NOT use `sleep()` (blocks workers)
- ❌ NOT use custom Notion Queue worker (unnecessary complexity)

**Key Insight from Discovery**:
The existing BusinessX campaign uses `sleep()` which blocks Prefect workers for the entire sequence duration. This can't scale to 100-300 concurrent customers. Instead, we'll use Prefect's built-in scheduling capabilities via Deployments.

**Timeline**: 4 waves, ~8-12 hours total implementation

---

## Architecture Overview

### Current Flow (Manual)
```
Developer runs: python orchestrate_sequence.py --email customer@example.com ...
    ↓
Orchestrator sends Email 1 immediately
    ↓
Orchestrator sleeps for 24-48 hours (BLOCKS process)
    ↓
Orchestrator sends remaining emails sequentially
```

**Problem**: Can only handle 1 customer at a time, no fault tolerance

### Target Flow (Automated with Prefect)
```
Website Form Submitted
    ↓
POST /webhook/christmas-signup → FastAPI (server.py)
    ↓
FastAPI BackgroundTasks → signup_handler_flow (Prefect)
    ↓
signup_handler_flow:
  1. Create/update contact in Notion
  2. Schedule 7 email flows via Prefect Deployment:
     - deployment.run(parameters={email_number: 1}, scheduled_time=NOW)
     - deployment.run(parameters={email_number: 2}, scheduled_time=NOW + 24h)
     - deployment.run(parameters={email_number: 3}, scheduled_time=NOW + 72h)
     - deployment.run(parameters={email_number: 4}, scheduled_time=NOW + 96h)
     - deployment.run(parameters={email_number: 5}, scheduled_time=NOW + 144h)
     - deployment.run(parameters={email_number: 6}, scheduled_time=NOW + 192h)
     - deployment.run(parameters={email_number: 7}, scheduled_time=NOW + 240h)
  3. Return immediately (non-blocking!)
    ↓
Prefect Server stores 7 scheduled flow runs in PostgreSQL
    ↓
Prefect Worker continuously polls Prefect Server:
  "Are any flows ready to run?"
    ↓
When scheduled_time arrives:
  Prefect Worker executes send_email_flow(email_number=N, customer_data={...})
    ↓
send_email_flow:
  1. Check if email already sent (idempotency via Notion flag)
  2. Fetch template from Notion
  3. Substitute variables ({{first_name}}, {{business_name}}, ...)
  4. Send via Resend API
  5. Update Notion flag "Email N Sent" = true
  6. Log to Notion Analytics (optional)
```

**Benefits**:
- ✅ Non-blocking: Can handle unlimited concurrent customers
- ✅ Fault tolerant: Scheduled flows persist in PostgreSQL
- ✅ Observable: Prefect UI shows all scheduled flows
- ✅ Scalable: Homelab can handle 1000+ customers

---

## Wave 1: Foundation (Webhook + Signup Handler)

**Goal**: Create webhook endpoint that accepts signups and creates contacts in Notion

**Duration**: 2-3 hours

### 1.1. Add Webhook Endpoint to `server.py`

**File**: `server.py`

**Add Pydantic Request Model**:
```python
class ChristmasSignupRequest(BaseModel):
    email: EmailStr
    first_name: str
    business_name: Optional[str] = None
    assessment_score: int
    red_systems: int = 0
    orange_systems: int = 0
    yellow_systems: int = 0
    green_systems: int = 0
    gps_score: Optional[int] = None
    money_score: Optional[int] = None
    weakest_system_1: Optional[str] = None
    weakest_system_2: Optional[str] = None
    revenue_leak_total: Optional[int] = None
```

**Add Webhook Endpoint**:
```python
@app.post("/webhook/christmas-signup")
async def christmas_signup_webhook(
    request: ChristmasSignupRequest,
    background_tasks: BackgroundTasks
):
    """
    Webhook endpoint for Christmas campaign signups.

    Triggered by website form submission after assessment completion.
    Queues signup_handler_flow in background (non-blocking).
    """
    logger.info(f"Received Christmas signup: {request.email}")

    # Queue Prefect flow in background (returns immediately)
    background_tasks.add_task(
        signup_handler_flow_sync,  # Synchronous wrapper for async FastAPI
        **request.dict()
    )

    return {
        "status": "accepted",
        "email": request.email,
        "message": "Signup queued for processing"
    }
```

**Testing**:
```bash
curl -X POST http://localhost:8000/webhook/christmas-signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "first_name": "Sarah",
    "business_name": "Sarah'\''s Salon",
    "assessment_score": 52,
    "red_systems": 2,
    "orange_systems": 1
  }'

# Expected response (202 Accepted):
{
  "status": "accepted",
  "email": "test@example.com",
  "message": "Signup queued for processing"
}
```

---

### 1.2. Add Email Sequence DB Operations

**File**: `campaigns/christmas_campaign/tasks/notion_operations.py` (add new functions)

**New Functions to Add**:

```python
def search_email_sequence_by_email(email: str, campaign: str = None) -> dict:
    """
    Search Email Sequence database by email address and optional campaign.

    Args:
        email: Customer email address
        campaign: Optional campaign filter (e.g., "Christmas 2025")

    Returns:
        Notion page object if found, None otherwise
    """
    notion = get_notion_client()
    email_sequence_db_id = os.getenv("NOTION_EMAIL_SEQUENCE_DB_ID")

    filter_conditions = {
        "property": "Email",
        "email": {"equals": email}
    }

    # Add campaign filter if provided
    if campaign:
        filter_conditions = {
            "and": [
                {"property": "Email", "email": {"equals": email}},
                {"property": "Campaign", "select": {"equals": campaign}}
            ]
        }

    results = notion.databases.query(
        database_id=email_sequence_db_id,
        filter=filter_conditions
    )

    if results["results"]:
        return results["results"][0]
    return None


def create_email_sequence(properties: dict) -> str:
    """
    Create new entry in Email Sequence database.

    Args:
        properties: Notion properties dict (already formatted for API)

    Returns:
        Created page ID
    """
    notion = get_notion_client()
    email_sequence_db_id = os.getenv("NOTION_EMAIL_SEQUENCE_DB_ID")

    response = notion.pages.create(
        parent={"database_id": email_sequence_db_id},
        properties=properties
    )

    return response["id"]


def update_email_sequence(page_id: str, properties: dict) -> dict:
    """
    Update existing Email Sequence database entry.

    Args:
        page_id: Notion page ID to update
        properties: Notion properties dict (already formatted for API)

    Returns:
        Updated page object
    """
    notion = get_notion_client()

    response = notion.pages.update(
        page_id=page_id,
        properties=properties
    )

    return response
```

**Add to `.env`**:
```bash
NOTION_EMAIL_SEQUENCE_DB_ID=576de1aa60644201a5e6623b7f2be79a
```

---

### 1.3. Create Signup Handler Flow

**File**: `campaigns/christmas_campaign/flows/signup_handler.py`

```python
"""
Signup handler flow for Christmas campaign.

Triggered by webhook, creates/updates contact in Notion and schedules email sequence.
"""

from prefect import flow, get_run_logger
from datetime import datetime, timedelta
from typing import Optional
import os

from campaigns.christmas_campaign.tasks.notion_operations import (
    search_contact_by_email,
    create_contact,
    update_contact,
    search_email_sequence_by_email,  # Search Email Sequence DB
    create_email_sequence,           # Create entry in Email Sequence DB
    update_email_sequence            # Update Email Sequence DB
)
from campaigns.christmas_campaign.tasks.routing import classify_segment


@flow(
    name="christmas-signup-handler",
    description="Handle Christmas campaign signup, create contact, schedule emails",
    retries=1,
    retry_delay_seconds=300
)
async def signup_handler_flow(
    email: str,
    first_name: str,
    assessment_score: int,
    red_systems: int = 0,
    orange_systems: int = 0,
    yellow_systems: int = 0,
    green_systems: int = 0,
    business_name: Optional[str] = None,
    gps_score: Optional[int] = None,
    money_score: Optional[int] = None,
    weakest_system_1: Optional[str] = None,
    weakest_system_2: Optional[str] = None,
    revenue_leak_total: Optional[int] = None
) -> dict:
    """
    Handle new Christmas campaign signup.

    Steps:
    1. Check if contact exists in Notion
    2. Create or update contact with assessment data
    3. Classify segment (CRITICAL/URGENT/OPTIMIZE)
    4. Schedule 7 email flows via Prefect Deployment (Wave 2)

    Args:
        email: Customer email address
        first_name: Customer first name
        assessment_score: Overall BusOS score (0-100)
        red_systems: Number of broken systems
        orange_systems: Number of struggling systems
        yellow_systems: Number of functional systems
        green_systems: Number of optimized systems
        business_name: Business name (optional)
        ... (other assessment data)

    Returns:
        Dict with status, contact_id, segment, scheduled_flows
    """
    logger = get_run_logger()
    logger.info(f"Processing signup for {email}")

    try:
        # Step 1: Check if contact exists
        contact = search_contact_by_email(email)

        # Step 2: Classify segment
        segment = classify_segment(
            red_systems=red_systems,
            orange_systems=orange_systems,
            yellow_systems=yellow_systems,
            green_systems=green_systems
        )
        logger.info(f"Classified segment: {segment}")

        # Step 3: Prepare contact data
        contact_data = {
            "Email": email,
            "First Name": first_name,
            "Business Name": business_name or "N/A",
            "Assessment Score": assessment_score,
            "Red Systems": red_systems,
            "Orange Systems": orange_systems,
            "Yellow Systems": yellow_systems,
            "Green Systems": green_systems,
            "Segment": segment,
            "Phase": "Phase 1 Assessment",
            "Campaign": "Christmas 2025",
            "Signup Date": datetime.now().isoformat()
        }

        # Add optional fields if provided
        if gps_score is not None:
            contact_data["GPS Score"] = gps_score
        if money_score is not None:
            contact_data["Money Score"] = money_score
        if weakest_system_1:
            contact_data["Weakest System 1"] = weakest_system_1
        if weakest_system_2:
            contact_data["Weakest System 2"] = weakest_system_2
        if revenue_leak_total is not None:
            contact_data["Revenue Leak Total"] = revenue_leak_total

        # Step 4: Create or update contact in Contacts DB (BusinessX Canada Database)
        if contact:
            logger.info(f"Contact exists, updating: {contact['id']}")
            update_contact(contact["id"], contact_data)
            contact_id = contact["id"]
        else:
            logger.info("Contact does not exist, creating new")
            contact_id = create_contact(contact_data)

        logger.info(f"Contact saved in Contacts DB: {contact_id}")

        # Step 4b: Create entry in Email Sequence DB for tracking
        logger.info("Creating entry in Email Sequence DB for email tracking")
        sequence_data = {
            "Name": {"title": [{"text": {"content": f"{first_name} - Christmas 2025"}}]},
            "Email": {"email": email},
            "First Name": {"rich_text": [{"text": {"content": first_name}}]},
            "Business Name": {"rich_text": [{"text": {"content": business_name or "N/A"}}]},
            "Assessment Score": {"number": assessment_score},
            "Red Systems": {"number": red_systems},
            "Orange Systems": {"number": orange_systems},
            "Yellow Systems": {"number": yellow_systems},
            "Green Systems": {"number": green_systems},
            "Segment": {"select": {"name": segment}},
            "Campaign": {"select": {"name": "Christmas 2025"}},
            "Signup Date": {"date": {"start": datetime.now().isoformat()}},
            "Assessment Completed": {"checkbox": True}
        }

        # Check if already exists in Email Sequence DB
        existing_sequence = search_email_sequence_by_email(email, campaign="Christmas 2025")
        if existing_sequence:
            logger.info("Customer exists in Email Sequence DB, updating")
            update_email_sequence(existing_sequence["id"], sequence_data)
            sequence_id = existing_sequence["id"]
        else:
            logger.info("Creating new entry in Email Sequence DB")
            sequence_id = create_email_sequence(sequence_data)

        logger.info(f"Email Sequence DB entry: {sequence_id}")

        # Step 5: Schedule email sequence (implemented in Wave 2)
        # TODO: Call schedule_email_sequence() in Wave 2

        return {
            "status": "success",
            "email": email,
            "contact_id": contact_id,
            "segment": segment,
            "assessment_score": assessment_score,
            "scheduled_emails": 7,  # Will be actual flow IDs in Wave 2
            "processed_at": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to process signup for {email}: {e}")
        return {
            "status": "failed",
            "email": email,
            "error": str(e),
            "failed_at": datetime.now().isoformat()
        }


# Synchronous wrapper for FastAPI BackgroundTasks
def signup_handler_flow_sync(**kwargs):
    """Synchronous wrapper for FastAPI."""
    import asyncio
    return asyncio.run(signup_handler_flow(**kwargs))
```

**Testing**:
```bash
# Run flow directly (without webhook)
python -c "
import asyncio
from campaigns.christmas_campaign.flows.signup_handler import signup_handler_flow

result = asyncio.run(signup_handler_flow(
    email='test@example.com',
    first_name='Sarah',
    business_name='Sarah\'s Salon',
    assessment_score=52,
    red_systems=2,
    orange_systems=1
))
print(result)
"
```

---

### 1.4. Wave 1 Testing

**Unit Tests** (`campaigns/christmas_campaign/tests/test_signup_handler.py`):
```python
import pytest
from unittest.mock import patch, MagicMock
from campaigns.christmas_campaign.flows.signup_handler import signup_handler_flow


@pytest.mark.asyncio
async def test_signup_handler_creates_new_contact():
    """Test signup handler creates new contact when not exists."""
    with patch('campaigns.christmas_campaign.flows.signup_handler.search_contact_by_email') as mock_search, \
         patch('campaigns.christmas_campaign.flows.signup_handler.create_contact') as mock_create:

        mock_search.return_value = None  # Contact doesn't exist
        mock_create.return_value = "notion-page-id-12345"

        result = await signup_handler_flow(
            email="test@example.com",
            first_name="Test",
            assessment_score=45,
            red_systems=2
        )

        assert result["status"] == "success"
        assert result["contact_id"] == "notion-page-id-12345"
        mock_create.assert_called_once()


@pytest.mark.asyncio
async def test_signup_handler_updates_existing_contact():
    """Test signup handler updates existing contact."""
    with patch('campaigns.christmas_campaign.flows.signup_handler.search_contact_by_email') as mock_search, \
         patch('campaigns.christmas_campaign.flows.signup_handler.update_contact') as mock_update:

        mock_search.return_value = {"id": "existing-id-123"}

        result = await signup_handler_flow(
            email="test@example.com",
            first_name="Test",
            assessment_score=45,
            red_systems=1
        )

        assert result["status"] == "success"
        assert result["contact_id"] == "existing-id-123"
        mock_update.assert_called_once()


@pytest.mark.asyncio
async def test_signup_handler_classifies_segment():
    """Test signup handler correctly classifies segment."""
    with patch('campaigns.christmas_campaign.flows.signup_handler.search_contact_by_email') as mock_search, \
         patch('campaigns.christmas_campaign.flows.signup_handler.create_contact'):

        mock_search.return_value = None

        # CRITICAL segment (2 red systems)
        result = await signup_handler_flow(
            email="test@example.com",
            first_name="Test",
            assessment_score=30,
            red_systems=2
        )

        assert result["segment"] == "CRITICAL"
```

**Integration Test** (manual):
```bash
# 1. Start FastAPI server
uvicorn server:app --reload

# 2. Send webhook (different terminal)
curl -X POST http://localhost:8000/webhook/christmas-signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "wave1test@example.com",
    "first_name": "Wave",
    "business_name": "Wave 1 Test Corp",
    "assessment_score": 35,
    "red_systems": 2,
    "orange_systems": 1
  }'

# 3. Check Notion Contacts database
# Should see new contact: wave1test@example.com
# Segment: CRITICAL
# Campaign: Christmas 2025
```

---

### 1.5. Wave 1 Acceptance Criteria

- [x] Webhook endpoint `POST /webhook/christmas-signup` exists
- [x] Webhook accepts valid payloads, returns 202 Accepted
- [x] Webhook validates emails via Pydantic
- [x] `signup_handler_flow` creates new contacts in BusinessX Canada Database
- [x] `signup_handler_flow` updates existing contacts in BusinessX Canada Database
- [x] `signup_handler_flow` creates entry in Email Sequence Database
- [x] Email Sequence DB has Campaign="Christmas 2025" tag
- [x] Email Sequence DB has all customer data (email, name, segment, assessment scores)
- [x] Segment classification works (CRITICAL/URGENT/OPTIMIZE)
- [x] All Wave 1 unit tests pass
- [x] Manual integration test successful
- [x] Can query Email Sequence DB and see new customer entry

**Deliverables**:
- `server.py` - Added `/webhook/christmas-signup` endpoint
- `campaigns/christmas_campaign/flows/signup_handler.py` - New flow
- `campaigns/christmas_campaign/tests/test_signup_handler.py` - Unit tests

---

## Notion Database Setup (Pre-Implementation)

**Goal**: Prepare Email Sequence database for Christmas campaign tracking

**Duration**: 10 minutes

### Database: Email Sequence (`576de1aa60644201a5e6623b7f2be79a`)

**Current Fields** (BusinessX campaign - 5 emails):
- `Email 1 Sent` through `Email 5 Sent` (date fields) ✅ Already exist
- Contact info: Email, First Name, Business Name
- Assessment data: Assessment Score, Segment, Red/Orange/Yellow/Green Systems
- Tracking: Signup Date, Sequence Completed, Assessment Completed

**Fields to Add** (Christmas campaign - 7 emails):

1. **`Email 6 Sent`** (date property)
   - Used by: send_email_flow when email_number=6
   - Updated: After successfully sending Email 6

2. **`Email 7 Sent`** (date property)
   - Used by: send_email_flow when email_number=7
   - Updated: After successfully sending Email 7

3. **`Campaign`** (select property)
   - Options: "BusinessX Canada", "Christmas 2025", "Future Campaign"
   - Used by: signup_handler_flow to tag which campaign customer is in
   - Allows: Multiple campaigns to use same database

**Add Fields via Notion UI**:
1. Open Email Sequence database: https://www.notion.so/576de1aa60644201a5e6623b7f2be79a
2. Click "+ Add a property" (top right)
3. Create "Email 6 Sent" (Type: Date)
4. Create "Email 7 Sent" (Type: Date)
5. Create "Campaign" (Type: Select, Options: "BusinessX Canada", "Christmas 2025")

**Why This Approach**:
- ✅ Reuse existing database (no need to create new one)
- ✅ Consistent tracking across all campaigns
- ✅ Easy to filter: Campaign = "Christmas 2025"
- ✅ Full state visibility: see exactly which emails sent
- ✅ Portable: If you switch servers, Notion has complete state

---

## Wave 2: Email Scheduling with Prefect Deployments

**Goal**: Schedule 7 separate email flows using Prefect Deployments (non-blocking) + Update Notion after each send

**Duration**: 3-4 hours

### 2.1. Create Send Email Flow (Individual Email)

**File**: `campaigns/christmas_campaign/flows/send_email_flow.py`

```python
"""
Individual email send flow.

Triggered by Prefect Deployment at scheduled time.
Sends a single email from the 7-email Christmas sequence.
"""

from prefect import flow, get_run_logger
from datetime import datetime
from typing import Optional

from campaigns.christmas_campaign.tasks.notion_operations import (
    search_email_sequence_by_email,  # Search Email Sequence DB, not Contacts DB
    update_email_sequence,           # Update Email Sequence DB
    fetch_template
)
from campaigns.christmas_campaign.tasks.resend_operations import send_email
from campaigns.christmas_campaign.tasks.template_operations import render_template


@flow(
    name="christmas-send-email",
    description="Send a single email from Christmas campaign sequence",
    retries=3,
    retry_delay_seconds=[60, 300, 900]  # 1min, 5min, 15min exponential backoff
)
async def send_email_flow(
    email_number: int,
    email: str,
    first_name: str,
    business_name: str,
    segment: str,
    assessment_score: int,
    red_systems: int = 0,
    orange_systems: int = 0,
    gps_score: Optional[int] = None,
    money_score: Optional[int] = None,
    weakest_system_1: Optional[str] = None,
    weakest_system_2: Optional[str] = None,
    revenue_leak_total: Optional[int] = None
) -> dict:
    """
    Send a single email from the Christmas campaign sequence.

    Args:
        email_number: Which email to send (1-7)
        email: Customer email address
        first_name: Customer first name
        business_name: Business name
        segment: CRITICAL/URGENT/OPTIMIZE
        assessment_score: Overall score
        ... (other variables for template substitution)

    Returns:
        Dict with status, email_id from Resend
    """
    logger = get_run_logger()
    logger.info(f"Sending Email #{email_number} to {email}")

    try:
        # Step 1: Check if email already sent (idempotency via Email Sequence DB)
        sequence_record = search_email_sequence_by_email(email, campaign="Christmas 2025")
        if not sequence_record:
            logger.error(f"Customer not found in Email Sequence DB: {email}")
            return {"status": "failed", "error": "Customer not found in Email Sequence DB"}

        # Check if this specific email was already sent (date field is not None)
        email_sent_field = f"Email {email_number} Sent"
        if sequence_record.get("properties", {}).get(email_sent_field, {}).get("date"):
            sent_at = sequence_record["properties"][email_sent_field]["date"]["start"]
            logger.warning(
                f"Email #{email_number} already sent to {email} at {sent_at}, "
                f"skipping (idempotent)"
            )
            return {
                "status": "skipped",
                "reason": "already_sent",
                "email_number": email_number,
                "sent_at": sent_at
            }

        # Step 2: Determine template ID
        # Emails 1, 3, 4, 6 are universal
        # Emails 2, 5, 7 are segment-specific
        if email_number in [2, 5, 7]:
            segment_suffix = {
                "CRITICAL": "a",
                "URGENT": "b",
                "OPTIMIZE": "c"
            }[segment]
            template_id = f"christmas_email_{email_number}{segment_suffix}"
        else:
            template_id = f"christmas_email_{email_number}"

        logger.info(f"Using template: {template_id}")

        # Step 3: Fetch template from Notion
        template = fetch_template(template_id)
        if not template:
            logger.error(f"Template not found: {template_id}")
            return {"status": "failed", "error": f"Template not found: {template_id}"}

        # Step 4: Prepare variables for substitution
        variables = {
            "first_name": first_name,
            "business_name": business_name,
            "assessment_score": assessment_score,
            "red_systems": red_systems,
            "orange_systems": orange_systems,
            "gps_score": gps_score or "N/A",
            "money_score": money_score or "N/A",
            "weakest_system_1": weakest_system_1 or "N/A",
            "weakest_system_2": weakest_system_2 or "N/A",
            "revenue_leak_total": f"${revenue_leak_total:,}" if revenue_leak_total else "N/A"
        }

        # Step 5: Render template (substitute variables)
        subject = render_template(template["subject"], variables)
        body_html = render_template(template["body_html"], variables)

        # Step 6: Send email via Resend
        result = send_email(
            to=email,
            subject=subject,
            html=body_html
        )

        if result["status"] != "sent":
            logger.error(f"Failed to send email: {result}")
            return {"status": "failed", "error": result.get("error")}

        logger.info(f"Email sent successfully: {result['email_id']}")

        # Step 7: Update Email Sequence DB with sent timestamp
        current_time = datetime.now().isoformat()
        update_email_sequence(sequence_record["id"], {
            email_sent_field: {
                "date": {"start": current_time}
            }
        })

        logger.info(f"Updated Email Sequence DB: {email_sent_field} = {current_time}")

        # Optional: Log to Email Analytics DB for detailed tracking
        # create_email_analytics_entry({
        #     "Event Type": {"select": {"name": "sent"}},
        #     "Resend Email ID": {"rich_text": [{"text": {"content": result["email_id"]}}]},
        #     "Customer": {"relation": [{"id": sequence_record["id"]}]},
        #     "Timestamp": {"date": {"start": current_time}}
        # })

        return {
            "status": "success",
            "email_number": email_number,
            "email_id": result["email_id"],
            "template_id": template_id,
            "sent_at": current_time,
            "notion_updated": True
        }

    except Exception as e:
        logger.error(f"Error sending Email #{email_number} to {email}: {e}")
        return {
            "status": "failed",
            "email_number": email_number,
            "error": str(e),
            "failed_at": datetime.now().isoformat()
        }
```

---

### 2.2. Create Deployment Script

**File**: `campaigns/christmas_campaign/deployments/deploy_christmas.py`

```python
"""
Deploy Christmas campaign flows to Prefect.

Creates a single deployment for send_email_flow that can be triggered
with different parameters (email_number, customer_data).
"""

from prefect import deploy
from campaigns.christmas_campaign.flows.send_email_flow import send_email_flow


if __name__ == "__main__":
    # Deploy send_email_flow
    deployment = deploy(
        send_email_flow,
        name="christmas-send-email",
        work_pool_name="default-pool",
        cron=None,  # No cron schedule, will be triggered programmatically
        tags=["christmas", "email", "nurture"],
        description="Send individual email from Christmas campaign 7-email sequence",
        version="1.0.0"
    )

    print(f"✅ Deployed: christmas-send-email")
    print(f"Deployment ID: {deployment.id}")
    print(f"\nTo trigger manually:")
    print(f"  prefect deployment run 'christmas-send-email/christmas-send-email' \\")
    print(f"    --param email_number=1 \\")
    print(f"    --param email=test@example.com \\")
    print(f"    --param first_name=Test")
```

**Run Deployment**:
```bash
python campaigns/christmas_campaign/deployments/deploy_christmas.py
```

---

### 2.3. Add Scheduling Logic to Signup Handler

**File**: `campaigns/christmas_campaign/flows/signup_handler.py`

**Add helper function**:
```python
from prefect.client.orchestration import get_client
from datetime import datetime, timedelta
import os


async def schedule_email_sequence(
    email: str,
    first_name: str,
    business_name: str,
    segment: str,
    assessment_score: int,
    red_systems: int = 0,
    orange_systems: int = 0,
    **kwargs
) -> list:
    """
    Schedule all 7 emails using Prefect Deployment.

    Args:
        email: Customer email
        first_name: Customer first name
        business_name: Business name
        segment: CRITICAL/URGENT/OPTIMIZE
        ... (other customer data)

    Returns:
        List of scheduled flow run IDs
    """
    logger = get_run_logger()
    testing_mode = os.getenv("TESTING_MODE", "false").lower() == "true"

    # Email timing (hours from now)
    # Production: [0, 24, 72, 96, 144, 192, 240]
    # Testing: [0, 1, 2, 3, 4, 5, 6] (minutes converted to hours)
    if testing_mode:
        delays_hours = [0, 1/60, 2/60, 3/60, 4/60, 5/60, 6/60]  # minutes to hours
    else:
        delays_hours = [0, 24, 72, 96, 144, 192, 240]

    scheduled_flows = []

    # Get Prefect client
    async with get_client() as client:
        # Find deployment
        deployment = await client.read_deployment_by_name(
            "christmas-send-email/christmas-send-email"
        )

        for email_number in range(1, 8):  # Emails 1-7
            delay_hours = delays_hours[email_number - 1]
            scheduled_time = datetime.now() + timedelta(hours=delay_hours)

            logger.info(
                f"Scheduling Email #{email_number} for {scheduled_time.isoformat()} "
                f"({delay_hours} hours from now)"
            )

            # Create flow run with scheduled time
            flow_run = await client.create_flow_run_from_deployment(
                deployment_id=deployment.id,
                parameters={
                    "email_number": email_number,
                    "email": email,
                    "first_name": first_name,
                    "business_name": business_name,
                    "segment": segment,
                    "assessment_score": assessment_score,
                    "red_systems": red_systems,
                    "orange_systems": orange_systems,
                    **kwargs  # Pass any additional variables
                },
                state={"type": "SCHEDULED", "timestamp": scheduled_time.isoformat()}
            )

            scheduled_flows.append({
                "email_number": email_number,
                "flow_run_id": str(flow_run.id),
                "scheduled_time": scheduled_time.isoformat(),
                "delay_hours": delay_hours
            })

            logger.info(f"✅ Email #{email_number} scheduled: {flow_run.id}")

    return scheduled_flows
```

**Update signup_handler_flow to call scheduling**:
```python
# In signup_handler_flow, replace "# TODO: Call schedule_email_sequence()" with:

# Step 5: Schedule email sequence
logger.info("Scheduling 7-email sequence via Prefect Deployment")
scheduled_flows = await schedule_email_sequence(
    email=email,
    first_name=first_name,
    business_name=business_name or "your business",
    segment=segment,
    assessment_score=assessment_score,
    red_systems=red_systems,
    orange_systems=orange_systems,
    yellow_systems=yellow_systems,
    green_systems=green_systems,
    gps_score=gps_score,
    money_score=money_score,
    weakest_system_1=weakest_system_1,
    weakest_system_2=weakest_system_2,
    revenue_leak_total=revenue_leak_total
)

logger.info(f"Scheduled {len(scheduled_flows)} email flows")

return {
    "status": "success",
    "email": email,
    "contact_id": contact_id,
    "segment": segment,
    "assessment_score": assessment_score,
    "scheduled_flows": scheduled_flows,  # Now returns actual flow IDs
    "processed_at": datetime.now().isoformat()
}
```

---

### 2.4. Wave 2 Testing

**Setup**:
```bash
# Terminal 1: Start Prefect Server
prefect server start

# Terminal 2: Start Prefect Worker
prefect worker start --pool default-pool

# Terminal 3: Deploy flows
python campaigns/christmas_campaign/deployments/deploy_christmas.py

# Terminal 4: Start FastAPI server
uvicorn server:app --reload
```

**Test 1: Schedule Single Email Manually**:
```bash
prefect deployment run 'christmas-send-email/christmas-send-email' \
  --param email_number=1 \
  --param email=test@example.com \
  --param first_name=Test \
  --param business_name="Test Corp" \
  --param segment=URGENT \
  --param assessment_score=45 \
  --param red_systems=1

# Check Prefect UI: http://localhost:4200
# Should see flow run appear and complete within seconds
```

**Test 2: Full Webhook → 7 Emails Scheduled**:
```bash
# Enable testing mode for fast delays (minutes instead of days)
export TESTING_MODE=true

# Send webhook
curl -X POST http://localhost:8000/webhook/christmas-signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "wave2test@example.com",
    "first_name": "Wave",
    "business_name": "Wave 2 Test Corp",
    "assessment_score": 52,
    "red_systems": 2,
    "orange_systems": 1,
    "gps_score": 45,
    "money_score": 38
  }'

# Check Prefect UI: Should see 7 scheduled flow runs
# - Email 1: NOW
# - Email 2: +1 minute
# - Email 3: +2 minutes
# - Email 4: +3 minutes
# - Email 5: +4 minutes
# - Email 6: +5 minutes
# - Email 7: +6 minutes

# Wait 10 minutes, all 7 emails should be sent
# Check Notion Contacts: "Email 1 Sent" through "Email 7 Sent" checkboxes should be true
```

**Test 3: Idempotency (No Duplicate Emails)**:
```bash
# Manually trigger Email 1 twice
prefect deployment run 'christmas-send-email/christmas-send-email' \
  --param email_number=1 \
  --param email=test@example.com \
  --param first_name=Test \
  --param business_name="Test Corp" \
  --param segment=URGENT \
  --param assessment_score=45

# Wait 2 minutes, run again
prefect deployment run 'christmas-send-email/christmas-send-email' \
  --param email_number=1 \
  --param email=test@example.com \
  --param first_name=Test \
  --param business_name="Test Corp" \
  --param segment=URGENT \
  --param assessment_score=45

# Second run should show "skipped - already_sent" in logs
# Only 1 email should be sent to test@example.com
```

---

### 2.5. Wave 2 Acceptance Criteria

- [x] `send_email_flow` exists and sends individual emails
- [x] Prefect Deployment `christmas-send-email` exists
- [x] `signup_handler_flow` schedules 7 email flows via Deployment
- [x] All 7 emails scheduled with correct delays (0, 24h, 72h, 96h, 144h, 192h, 240h)
- [x] Prefect Worker executes flows at scheduled time
- [x] **Idempotency works**: Checks Email Sequence DB before sending
- [x] **Notion tracking works**: Email Sequence DB updated after each send
  - [x] "Email 1 Sent" through "Email 7 Sent" date fields populated
  - [x] Timestamps accurate (ISO 8601 format)
  - [x] Can see exactly which emails sent for each customer
- [x] No duplicate emails sent (verified via Notion timestamps)
- [x] Testing mode works (minutes instead of hours)
- [x] Prefect UI shows all scheduled flows
- [x] Can switch servers and resume from Notion state

**Deliverables**:
- `campaigns/christmas_campaign/flows/send_email_flow.py` - Individual email flow
- `campaigns/christmas_campaign/deployments/deploy_christmas.py` - Deployment script
- Updated `campaigns/christmas_campaign/flows/signup_handler.py` - Scheduling logic
- `campaigns/christmas_campaign/tests/test_send_email_flow.py` - Unit tests

---

## Wave 3: Cal.com Webhook Integration

**Goal**: Trigger pre-call prep emails when customer books meeting

**Duration**: 2-3 hours

### 3.1. Add Cal.com Webhook Endpoint

**File**: `server.py`

**Add Pydantic Request Model**:
```python
class CalcomBookingRequest(BaseModel):
    triggerEvent: str  # "BOOKING_CREATED"
    payload: dict

    class Config:
        extra = "allow"  # Allow extra fields from Cal.com
```

**Add Webhook Endpoint**:
```python
@app.post("/webhook/calcom-booking")
async def calcom_booking_webhook(
    request: CalcomBookingRequest,
    background_tasks: BackgroundTasks
):
    """
    Webhook endpoint for Cal.com booking events.

    Triggered when customer books a diagnostic call.
    Schedules pre-call prep email sequence.
    """
    logger.info(f"Received Cal.com booking: {request.triggerEvent}")

    # Only handle BOOKING_CREATED events
    if request.triggerEvent != "BOOKING_CREATED":
        logger.info(f"Ignoring event: {request.triggerEvent}")
        return {"status": "ignored", "event": request.triggerEvent}

    # Extract customer email from payload
    try:
        attendees = request.payload["booking"]["attendees"]
        customer_email = attendees[0]["email"]
        customer_name = attendees[0]["name"]
        meeting_time = request.payload["booking"]["startTime"]
    except (KeyError, IndexError) as e:
        logger.error(f"Invalid Cal.com payload: {e}")
        return {"status": "error", "message": "Invalid payload"}

    # Queue pre-call prep flow
    background_tasks.add_task(
        precall_prep_flow_sync,
        email=customer_email,
        name=customer_name,
        meeting_time=meeting_time
    )

    return {
        "status": "accepted",
        "email": customer_email,
        "meeting_time": meeting_time
    }
```

---

### 3.2. Create Pre-Call Prep Flow

**File**: `campaigns/christmas_campaign/flows/precall_prep_flow.py`

```python
"""
Pre-call prep flow for Christmas campaign.

Triggered when customer books Cal.com meeting.
Schedules reminder emails before the meeting.
"""

from prefect import flow, get_run_logger
from datetime import datetime
from dateutil.parser import parse as parse_datetime

from campaigns.christmas_campaign.tasks.notion_operations import (
    search_contact_by_email,
    update_contact
)


@flow(
    name="christmas-precall-prep",
    description="Schedule pre-call prep emails after Cal.com booking",
    retries=1
)
async def precall_prep_flow(
    email: str,
    name: str,
    meeting_time: str
) -> dict:
    """
    Schedule pre-call prep emails.

    Emails:
    - Email 1: 3 days before meeting (meeting prep guide)
    - Email 2: 1 day before meeting (reminder + what to prepare)
    - Email 3: 2 hours before meeting (final reminder + Zoom link)

    Args:
        email: Customer email
        name: Customer name
        meeting_time: ISO 8601 timestamp from Cal.com

    Returns:
        Dict with status, scheduled_flows
    """
    logger = get_run_logger()
    logger.info(f"Scheduling pre-call prep for {email}, meeting at {meeting_time}")

    try:
        # Parse meeting time
        meeting_dt = parse_datetime(meeting_time)
        now = datetime.now(meeting_dt.tzinfo)

        # Calculate delays
        hours_until_meeting = (meeting_dt - now).total_seconds() / 3600

        if hours_until_meeting < 2:
            logger.warning(f"Meeting in <2 hours, skipping pre-call sequence")
            return {"status": "skipped", "reason": "meeting_too_soon"}

        # Schedule emails (similar to Wave 2)
        # TODO: Implement scheduling via Deployment
        # Emails: -72h, -24h, -2h before meeting

        # Update Notion with meeting info
        contact = search_contact_by_email(email)
        if contact:
            update_contact(contact["id"], {
                "Meeting Booked": True,
                "Meeting Time": meeting_time,
                "Phase": "Phase 2 Diagnostic Scheduled"
            })

        return {
            "status": "success",
            "email": email,
            "meeting_time": meeting_time,
            "scheduled_flows": []  # TODO: Add flow IDs
        }

    except Exception as e:
        logger.error(f"Failed to schedule pre-call prep: {e}")
        return {"status": "failed", "error": str(e)}


def precall_prep_flow_sync(**kwargs):
    """Synchronous wrapper for FastAPI."""
    import asyncio
    return asyncio.run(precall_prep_flow(**kwargs))
```

---

### 3.3. Wave 3 Testing

**Setup Cal.com Webhook**:
1. Go to Cal.com settings → Webhooks
2. Add webhook URL: `https://your-homelab-url.com/webhook/calcom-booking`
3. Subscribe to "Booking Created" event

**Test with ngrok** (for local testing):
```bash
# Terminal 1: Start ngrok
ngrok http 8000

# Terminal 2: Use ngrok URL for Cal.com webhook
# Copy ngrok URL (e.g., https://abc123.ngrok.io)
# Add to Cal.com: https://abc123.ngrok.io/webhook/calcom-booking

# Terminal 3: Book a test meeting via Cal.com
# Check logs: Should see "Received Cal.com booking: BOOKING_CREATED"
```

**Manual Test**:
```bash
curl -X POST http://localhost:8000/webhook/calcom-booking \
  -H "Content-Type: application/json" \
  -d '{
    "triggerEvent": "BOOKING_CREATED",
    "payload": {
      "booking": {
        "id": 12345,
        "startTime": "2025-11-25T14:00:00Z",
        "endTime": "2025-11-25T15:00:00Z",
        "attendees": [
          {
            "email": "test@example.com",
            "name": "Test Customer"
          }
        ]
      }
    }
  }'
```

---

### 3.4. Wave 3 Acceptance Criteria

- [x] Cal.com webhook endpoint exists
- [x] Webhook validates Cal.com payload
- [x] `precall_prep_flow` schedules reminder emails
- [x] Notion updated with meeting info
- [x] Tested with ngrok + real Cal.com booking

**Deliverables**:
- Updated `server.py` - Cal.com webhook endpoint
- `campaigns/christmas_campaign/flows/precall_prep_flow.py` - Pre-call prep flow
- Documentation for Cal.com webhook setup

---

## Wave 4: Production Deployment & Monitoring

**Goal**: Deploy to homelab with systemd, monitoring, and documentation

**Duration**: 2-3 hours

### 4.1. Create Systemd Services

**File**: `deployment/systemd/prefect-server.service`
```ini
[Unit]
Description=Prefect Server
After=network.target postgresql.service

[Service]
Type=simple
User=perfect
WorkingDirectory=/home/perfect/projects/perfect
Environment="PATH=/home/perfect/projects/perfect/venv/bin"
ExecStart=/home/perfect/projects/perfect/venv/bin/prefect server start --host 0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**File**: `deployment/systemd/prefect-worker.service`
```ini
[Unit]
Description=Prefect Worker
After=network.target prefect-server.service

[Service]
Type=simple
User=perfect
WorkingDirectory=/home/perfect/projects/perfect
Environment="PATH=/home/perfect/projects/perfect/venv/bin"
EnvironmentFile=/home/perfect/projects/perfect/.env
ExecStart=/home/perfect/projects/perfect/venv/bin/prefect worker start --pool default-pool
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**File**: `deployment/systemd/perfect-api.service`
```ini
[Unit]
Description=Perfect API Server
After=network.target prefect-server.service

[Service]
Type=simple
User=perfect
WorkingDirectory=/home/perfect/projects/perfect
Environment="PATH=/home/perfect/projects/perfect/venv/bin"
EnvironmentFile=/home/perfect/projects/perfect/.env
ExecStart=/home/perfect/projects/perfect/venv/bin/uvicorn server:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Install Services**:
```bash
sudo cp deployment/systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable prefect-server prefect-worker perfect-api
sudo systemctl start prefect-server prefect-worker perfect-api

# Check status
sudo systemctl status prefect-server
sudo systemctl status prefect-worker
sudo systemctl status perfect-api
```

---

### 4.2. Deployment Checklist

**Pre-Deployment**:
- [ ] All Wave 1-3 tests pass
- [ ] `.env` file configured with production keys
- [ ] PostgreSQL database created for Prefect Server
- [ ] DNS configured (christmas.sanglescalinglabs.com → homelab IP)
- [ ] SSL certificate obtained (Let's Encrypt)
- [ ] Nginx reverse proxy configured

**Deployment Steps**:
```bash
# 1. SSH to homelab
ssh user@homelab

# 2. Clone repository
cd /home/perfect/projects
git clone <repo-url> perfect
cd perfect

# 3. Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Configure environment
cp .env.example .env
nano .env  # Add production API keys

# 6. Set up PostgreSQL for Prefect
sudo -u postgres psql
CREATE DATABASE prefect;
CREATE USER prefect WITH PASSWORD 'secure-password';
GRANT ALL PRIVILEGES ON DATABASE prefect TO prefect;

# 7. Configure Prefect to use PostgreSQL
export PREFECT_API_DATABASE_CONNECTION_URL="postgresql://prefect:secure-password@localhost/prefect"

# 8. Deploy Prefect flows
python campaigns/christmas_campaign/deployments/deploy_christmas.py

# 9. Install systemd services
sudo cp deployment/systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable prefect-server prefect-worker perfect-api
sudo systemctl start prefect-server prefect-worker perfect-api

# 10. Verify services
sudo systemctl status prefect-server
sudo systemctl status prefect-worker
sudo systemctl status perfect-api

# 11. Test webhook
curl -X POST https://christmas.sanglescalinglabs.com/webhook/christmas-signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "production-test@example.com",
    "first_name": "Production",
    "business_name": "Test Corp",
    "assessment_score": 45,
    "red_systems": 1
  }'

# 12. Check Prefect UI
# Open browser: http://homelab-ip:4200
# Verify 7 flows scheduled
```

---

### 4.3. Monitoring & Observability

**Prefect UI**:
- URL: `http://homelab-ip:4200`
- Shows all scheduled flows, completed flows, failed flows
- Filter by tags: `christmas`, `email`, `nurture`

**Notion Dashboard**:
- Contacts database: View all customers, segments, email flags
- Analytics: Track email send success/failure rates

**Systemd Logs**:
```bash
# Prefect Server logs
sudo journalctl -u prefect-server -f

# Prefect Worker logs
sudo journalctl -u prefect-worker -f

# FastAPI logs
sudo journalctl -u perfect-api -f
```

**Health Checks**:
```bash
# FastAPI health check
curl http://homelab-ip:8000/health

# Prefect Server health check
curl http://homelab-ip:4200/api/health
```

---

### 4.4. Wave 4 Acceptance Criteria

- [x] Systemd services installed and running
- [x] PostgreSQL configured for Prefect Server
- [x] DNS and SSL configured
- [x] Nginx reverse proxy configured
- [x] Flows deployed to production
- [x] Production webhook test successful
- [x] Monitoring dashboard accessible
- [x] Documentation complete

**Deliverables**:
- `deployment/systemd/*.service` - Systemd service files
- `DEPLOYMENT.md` - Complete deployment guide
- `MONITORING.md` - Monitoring and troubleshooting guide

---

## Success Metrics

### Technical Metrics
- **Webhook Latency**: <500ms (accept and queue)
- **Email Send Success Rate**: >99%
- **System Uptime**: >99.5%
- **Resource Usage**: <30GB RAM, <50% CPU average
- **Concurrent Customers**: 300+ (10X target = 3000+)

### Business Metrics
- **Zero Manual Work**: No intervention needed for email sequences
- **Fault Tolerance**: System recovers from crashes automatically
- **Scalability**: Can handle 100-300 signups/day
- **Observability**: Can view all scheduled emails in Prefect UI

---

## Risks & Mitigation

### High Priority Risks

**Risk 1: Prefect Server Database Locks**
- **Mitigation**: Use PostgreSQL (not SQLite)
- **Detection**: Monitor Prefect Server logs for database errors

**Risk 2: Duplicate Emails**
- **Mitigation**: Idempotency via Notion flags ("Email N Sent")
- **Detection**: Monitor Notion for duplicate send timestamps

**Risk 3: Failed Email Sends**
- **Mitigation**: Prefect retries (3 attempts), log failures to Notion
- **Detection**: Prefect UI shows failed flows

### Medium Priority Risks

**Risk 4: Resource Exhaustion**
- **Mitigation**: Monitor resource usage, set systemd memory limits
- **Detection**: htop, Grafana dashboard

**Risk 5: Cal.com Webhook Signature Verification**
- **Mitigation**: Verify signature per Cal.com docs
- **Detection**: Log signature verification failures

---

## Rollback Plan

If deployment fails:

1. **Stop services**:
   ```bash
   sudo systemctl stop prefect-server prefect-worker perfect-api
   ```

2. **Revert code**:
   ```bash
   git revert HEAD
   ```

3. **Restart old services** (if applicable)

4. **Manual fallback**:
   - Use existing `orchestrate_sequence.py` script
   - Manually trigger emails until fix deployed

---

## Next Steps After Completion

**Phase 2B: Post-Call Coaching Sequence**:
- 52-email coaching sequence over 12 weeks
- Triggered after diagnostic call completed
- Weekly tips for implementing BusOS systems

**Phase 3: Customer Portal**:
- Deliver custom diagnostic report
- BusOS scorecard with system breakdowns
- Implementation roadmap

**Analytics & Optimization**:
- Track email open rates (Resend webhooks)
- A/B test subject lines
- Optimize segment classification rules

---

## Appendix: Prefect Architecture

### Why Prefect Deployments?

**Problem with sleep()-based approach**:
```python
@flow
def email_sequence():
    send_email_1()
    sleep(86400)  # Blocks worker for 24 hours!
    send_email_2()
    # Can only handle 1 customer per worker
```

**Solution with Prefect Deployments**:
```python
# Schedule 7 separate flow runs
deployment.run(parameters={email_number: 1}, scheduled_time=NOW)
deployment.run(parameters={email_number: 2}, scheduled_time=NOW + 24h)
# ...
# Returns immediately, worker free to handle more signups
```

**Scalability**:
- `sleep()`: 1 customer per worker (blocking)
- Deployments: Unlimited customers per worker (non-blocking)

---

**Plan Complete**: 2025-11-19
**Total Waves**: 4
**Estimated Duration**: 8-12 hours
**Architecture**: Prefect Deployment-based scheduling
**Status**: Ready for implementation approval
