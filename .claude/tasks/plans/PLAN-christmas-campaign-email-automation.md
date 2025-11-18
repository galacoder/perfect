# Plan: Christmas Campaign Email Automation

**Task ID**: christmas-campaign-email-automation
**Domain**: coding
**Created**: 2025-11-16
**Status**: Planning
**Source**: Detailed planning session from handoff document

---

## Implementation Strategy

### Approach
**Method**: Outside-in TDD with incremental delivery
**Paradigm**: Functional with Prefect decorators (existing pattern)
**Estimated Time**: 16-18 hours total
**Risk Level**: Medium (60-second portal delivery is critical constraint)

### Key Decisions

**Why this approach**:
1. **New campaign directory** (`campaigns/christmas_campaign/`): Keeps Christmas campaign separate from existing `businessx_canada_lead_nurture`, prevents conflicts
2. **Reuse existing task modules where possible**: `notion_operations`, `resend_operations`, `template_operations` - only extend, don't duplicate
3. **Incremental delivery**: Implement 7-email nurture first (highest value), then portal, then coaching emails
4. **60-second portal**: Use background tasks + async Notion operations to meet deadline

**Alternatives considered**:
- ❌ Extend existing campaign: Rejected due to different email structure (7 vs 5 emails)
- ❌ Use Trigger.dev: Rejected to minimize new dependencies, Prefect already handles scheduling
- ❌ Use Resend Audiences API: Rejected, simpler to manage contacts in Notion only

**Critical success factors**:
- Customer portal created in <60 seconds (this is THE constraint)
- All email templates stored in Notion (dynamic editing)
- Exit conditions properly stop/redirect sequences
- Cal.com webhook integration reliable

---

## Execution Waves

### Wave 1: Foundation & Setup (3-4 hours)

**Objective**: Set up Christmas campaign structure, environment, and base infrastructure

#### Tasks:

1. **Create campaign directory structure**
   ```bash
   cd /Users/sangle/Dev/action/projects/perfect
   mkdir -p campaigns/christmas_campaign/flows
   mkdir -p campaigns/christmas_campaign/tasks
   mkdir -p campaigns/christmas_campaign/tests
   touch campaigns/christmas_campaign/__init__.py
   touch campaigns/christmas_campaign/flows/__init__.py
   touch campaigns/christmas_campaign/tasks/__init__.py
   touch campaigns/christmas_campaign/tests/__init__.py
   ```

2. **Create Notion Customer Portal Database**
   - **Manual step** (user must do in Notion):
     - Duplicate from template or create new database
     - Properties:
       - `Name` (Title): Customer name + campaign
       - `Email` (Email): Customer email
       - `Status` (Select): Portal Created, Documents Uploaded, Complete
       - `Call Date` (Date): Diagnostic call date
       - `Portal URL` (URL): Public Notion page URL
       - `Created At` (Created time): Auto timestamp
   - Copy database ID to `.env` as `NOTION_CUSTOMER_PORTAL_DB_ID`

3. **Update Notion Contacts Database**
   - **Manual step** (user must do in Notion):
     - Add new properties:
       - `Phase` (Select): Phase 1 Assessment, Phase 1 Diagnostic, Phase 2A, Phase 2B, Phase 2C
       - `Diagnostic Call Date` (Date)
       - `Booking Status` (Select): Not Booked, Booked, Completed, No-Show
       - `Phase 2 Decision Date` (Date)
       - `Christmas Campaign Status` (Select): Nurture, Pre-Call Prep, Portal Delivered, Long-Term

4. **Add environment variables to .env**
   ```bash
   # Add to .env file
   CAL_WEBHOOK_SECRET=your_secret_here  # Get from Cal.com settings
   NOTION_CUSTOMER_PORTAL_DB_ID=your_db_id_here  # From step 2
   ```

5. **Create test helper module**
   - File: `campaigns/christmas_campaign/tests/conftest.py`
   - Fixtures for mocking Notion API, Resend API, Cal.com webhooks

6. **Commit: "chore(christmas): set up campaign directory structure"**

**Success Criteria**:
- [ ] Directory structure created
- [ ] Notion databases updated with new properties
- [ ] Environment variables added
- [ ] Test fixtures ready
- [ ] No errors when importing new modules
- [ ] Git commit created

---

### Wave 2: Core 7-Email Nurture Sequence (6-7 hours)

**Objective**: Implement complete 7-email nurture sequence with TDD approach

**Code Organization** (Top-Down):
```python
# HIGH-LEVEL: Public API (what we're doing)
@flow(name="christmas-nurture-7-emails")
def christmas_nurture_flow(contact_page_id, email, assessment_data):
    """Send 7-email Christmas nurture sequence"""
    # Orchestrate the sequence
    send_all_emails(contact_page_id, email, assessment_data)
    handle_exit_conditions(contact_page_id, email)
    return summary

# MEDIUM-LEVEL: How we do it
def send_all_emails(contact_page_id, email, assessment_data):
    """Send emails 1-7 with proper waits"""
    for email_num in range(1, 8):
        send_single_email(email_num, email, assessment_data)
        wait_for_next_email(email_num)

# LOW-LEVEL: Implementation details
def send_single_email(email_num, email, assessment_data):
    """Atomic operation to send one email"""
    template = get_christmas_template(email_num)
    send_email(to=email, template=template, vars=assessment_data)
```

#### 2.1 Create Assessment Data Model

**RED**: Write test
```python
# campaigns/christmas_campaign/tests/test_models.py

def test_assessment_data_model_validation():
    """Test AssessmentData model validates all required fields"""
    from campaigns.christmas_campaign.models import AssessmentData

    # Valid data
    data = AssessmentData(
        email="test@example.com",
        first_name="Test",
        gps_score=60,
        generate_score=55,
        persuade_score=65,
        serve_score=60,
        money_score=70,
        marketing_score=50,
        weakest_system_1="Generate",
        score_1=55,
        revenue_leak_system_1=3000,
        weakest_system_2="Persuade",
        score_2=65,
        revenue_leak_system_2=2500,
        total_revenue_leak=5500,
        annual_revenue_leak=66000,
        quick_win_action="Create Google Business Profile posts 3X/week",
        quick_win_explanation="Increases local visibility",
        quick_win_impact="2-4 new bookings/month"
    )
    assert data.email == "test@example.com"
    assert data.total_revenue_leak == 5500
```

**GREEN**: Implement model
```python
# campaigns/christmas_campaign/models.py

from pydantic import BaseModel, EmailStr, Field

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
```

**REFACTOR**: Add validation, edge cases

#### 2.2 Create Christmas-specific template operations

**RED**: Write test
```python
# campaigns/christmas_campaign/tests/test_christmas_templates.py

def test_get_christmas_template_returns_correct_email(mock_notion):
    """Test get_christmas_template fetches correct template from Notion"""
    from campaigns.christmas_campaign.tasks.christmas_templates import get_christmas_template

    # Mock Notion response
    mock_notion.databases.query.return_value = {
        "results": [{
            "properties": {
                "Subject": {"rich_text": [{"plain_text": "Your BusOS Results"}]},
                "HTML Body": {"rich_text": [{"plain_text": "<h1>Results</h1>"}]}
            }
        }]
    }

    template = get_christmas_template(email_number=1)
    assert template["subject"] == "Your BusOS Results"
    assert "<h1>Results</h1>" in template["html"]
```

**GREEN**: Implement task
```python
# campaigns/christmas_campaign/tasks/christmas_templates.py

from prefect import task
from campaigns.businessx_canada_lead_nurture.tasks.template_operations import fetch_template_from_notion

@task(retries=3, retry_delay_seconds=60, name="christmas-get-template")
def get_christmas_template(email_number: int) -> Dict[str, str]:
    """
    Fetch Christmas campaign email template from Notion.

    Template naming convention:
    - email_1_christmas: Results (immediate)
    - email_2_christmas: Quick Wins (Day 2)
    - email_3_christmas: Horror Story (Day 3)
    - email_4_christmas: First Ask (Day 4)
    - email_5_christmas: Case Study (Day 6)
    - email_6_christmas: Checklist (Day 8)
    - email_7_christmas: Final Ask (Day 10)
    """
    template_name = f"email_{email_number}_christmas"
    return fetch_template_from_notion(template_name)
```

**REFACTOR**: Add error handling, fallback templates

#### 2.3 Create 7-email nurture flow

**RED**: Write test
```python
# campaigns/christmas_campaign/tests/test_nurture_flow.py

def test_christmas_nurture_flow_sends_7_emails(mock_notion, mock_resend, mock_sleep):
    """Test nurture flow sends all 7 emails in correct order"""
    from campaigns.christmas_campaign.flows.nurture_sequence import christmas_nurture_flow

    result = christmas_nurture_flow(
        contact_page_id="page-123",
        email="test@example.com",
        assessment_data={...}
    )

    assert result["emails_sent"] == 7
    assert result["success"] == True
    assert mock_resend.emails.send.call_count == 7
```

**GREEN**: Implement flow
```python
# campaigns/christmas_campaign/flows/nurture_sequence.py

from prefect import flow
from time import sleep
from campaigns.christmas_campaign.tasks.christmas_templates import get_christmas_template
from campaigns.businessx_canada_lead_nurture.tasks.resend_operations import send_template_email
from campaigns.businessx_canada_lead_nurture.tasks.notion_operations import update_contact
import os

TESTING_MODE = os.getenv("TESTING_MODE", "false").lower() == "true"

# Wait durations (seconds)
WAIT_DURATIONS = {
    1: 60 if TESTING_MODE else 86400,      # 1 min vs 24h
    2: 120 if TESTING_MODE else 86400,     # 2 min vs 24h
    3: 180 if TESTING_MODE else 86400,     # 3 min vs 24h
    4: 240 if TESTING_MODE else 172800,    # 4 min vs 48h
    5: 300 if TESTING_MODE else 172800,    # 5 min vs 48h
    6: 360 if TESTING_MODE else 172800,    # 6 min vs 48h
}

@flow(name="christmas-nurture-7-emails", log_prints=True)
def christmas_nurture_flow(
    contact_page_id: str,
    email: str,
    assessment_data: dict
) -> dict:
    """
    Execute complete 7-email Christmas nurture sequence.

    Schedule:
    - Email 1: Results (immediate)
    - Email 2: Quick Wins (Day 2, +48h)
    - Email 3: Horror Story (Day 3, +24h)
    - Email 4: First Ask (Day 4, +24h)
    - Email 5: Case Study (Day 6, +48h)
    - Email 6: Checklist (Day 8, +48h)
    - Email 7: Final Ask (Day 10, +48h)
    """
    print(f"🎄 Starting Christmas nurture sequence for {email}")
    print(f"   Testing mode: {TESTING_MODE}")

    sent_emails = {}
    template_vars = {
        "first_name": assessment_data["first_name"],
        "gps_score": assessment_data["gps_score"],
        "weakest_system_1": assessment_data["weakest_system_1"],
        "score_1": assessment_data["score_1"],
        "revenue_leak_system_1": assessment_data["revenue_leak_system_1"],
        "total_revenue_leak": assessment_data["total_revenue_leak"],
        "annual_revenue_leak": assessment_data["annual_revenue_leak"],
        "quick_win_action": assessment_data["quick_win_action"],
        "quick_win_explanation": assessment_data["quick_win_explanation"],
        "quick_win_impact": assessment_data["quick_win_impact"],
    }

    # Send emails 1-7
    for email_num in range(1, 8):
        print(f"\n📧 Sending Email #{email_num}")
        template = get_christmas_template(email_number=email_num)

        email_result = send_template_email(
            to_email=email,
            subject=template["subject"],
            template=template["html"],
            variables=template_vars
        )
        sent_emails[f"email_{email_num}"] = email_result
        print(f"   ✅ Sent (ID: {email_result.get('id', 'N/A')})")

        # Update Notion
        update_contact(
            page_id=contact_page_id,
            properties={
                f"Christmas Email {email_num} Sent": {"checkbox": True},
                f"Christmas Email {email_num} Date": {"date": {"start": email_result.get("created_at", "")}}
            }
        )

        # Wait before next email (skip wait after last email)
        if email_num < 7:
            wait_duration = WAIT_DURATIONS[email_num]
            print(f"⏳ Waiting {wait_duration} seconds before Email #{email_num + 1}...")
            sleep(wait_duration)

    # Mark sequence complete
    update_contact(
        page_id=contact_page_id,
        properties={
            "Christmas Campaign Status": {"select": {"name": "Nurture Complete"}},
            "Christmas Sequence Completed": {"checkbox": True}
        }
    )

    print(f"\n✅ Christmas nurture sequence complete for {email}")
    return {
        "success": True,
        "emails_sent": 7,
        "sent_email_ids": sent_emails
    }
```

**REFACTOR**: Extract email sending logic to helper function, add error handling

#### 2.4 Add exit condition checks

**Implementation**:
```python
# campaigns/christmas_campaign/tasks/exit_conditions.py

from prefect import task
from campaigns.businessx_canada_lead_nurture.tasks.notion_operations import get_contact

@task(name="christmas-check-booking-status")
def check_booking_status(contact_page_id: str) -> str:
    """
    Check if contact has booked diagnostic call.

    Returns: "booked", "not_booked", "completed"
    """
    contact = get_contact(contact_page_id)
    booking_status = contact["properties"].get("Booking Status", {}).get("select", {}).get("name", "Not Booked")
    return booking_status.lower().replace(" ", "_")

@task(name="christmas-should-continue-sequence")
def should_continue_sequence(contact_page_id: str) -> bool:
    """
    Check if sequence should continue or exit.

    Exit conditions:
    - Booked diagnostic call
    - Unsubscribed
    - Sequence already completed
    """
    booking_status = check_booking_status(contact_page_id)
    if booking_status in ["booked", "completed"]:
        print(f"   🛑 Exiting: Contact has booked ({booking_status})")
        return False

    # Could add more checks (unsubscribe, etc.)
    return True
```

**Commit**: "feat(christmas): implement 7-email nurture sequence with exit conditions"

**Success Criteria**:
- [ ] All 7 emails send in correct order
- [ ] Wait durations respect TESTING_MODE
- [ ] Template variables properly substituted
- [ ] Notion contact updated after each email
- [ ] Exit conditions checked before each email
- [ ] Unit tests pass (>80% coverage)
- [ ] Integration test passes (mocked)

---

### Wave 3: Cal.com Webhooks & Pre-Call Prep + Customer Portal (5-6 hours)

**Objective**: Integrate Cal.com booking events, pre-call prep sequence, and 60-second portal delivery

#### 3.1 Create Cal.com webhook handler

**File**: `server.py` (extend existing)

**RED**: Write test
```python
# tests/test_server_christmas.py

def test_booking_webhook_triggers_pre_call_prep(client, mock_prefect):
    """Test Cal.com booking webhook triggers pre-call prep flow"""
    payload = {
        "triggerEvent": "BOOKING_CREATED",
        "payload": {
            "email": "test@example.com",
            "startTime": "2024-12-20T10:00:00Z",
            "metadata": {...}
        }
    }

    response = client.post("/webhook/booking-complete", json=payload)
    assert response.status_code == 202
    assert response.json()["status"] == "accepted"
    assert mock_prefect.flow_run_called_with == "pre-call-prep-sequence"
```

**GREEN**: Implement webhook
```python
# server.py (add new endpoint)

from campaigns.christmas_campaign.flows.pre_call_prep import pre_call_prep_flow

class CalBookingWebhook(BaseModel):
    triggerEvent: str
    payload: Dict[str, Any]

@app.post("/webhook/booking-complete")
async def handle_booking_webhook(
    request: CalBookingWebhook,
    background_tasks: BackgroundTasks
):
    """
    Handle Cal.com booking webhook for Christmas campaign.

    Triggers:
    - Stop nurture sequence
    - Start pre-call prep sequence (3 emails)
    """
    if request.triggerEvent != "BOOKING_CREATED":
        return {"status": "ignored", "reason": "Not a BOOKING_CREATED event"}

    email = request.payload.get("email")
    start_time = request.payload.get("startTime")

    # Trigger pre-call prep flow in background
    background_tasks.add_task(
        pre_call_prep_flow,
        email=email,
        call_date=start_time
    )

    return {
        "status": "accepted",
        "message": "Pre-call prep sequence will begin shortly",
        "email": email
    }
```

#### 3.2 Create pre-call prep sequence

**File**: `campaigns/christmas_campaign/flows/pre_call_prep.py`

```python
from prefect import flow
from datetime import datetime, timedelta
from campaigns.christmas_campaign.tasks.christmas_templates import get_christmas_template
from campaigns.businessx_canada_lead_nurture.tasks.resend_operations import send_template_email
from campaigns.businessx_canada_lead_nurture.tasks.notion_operations import search_contact_by_email, update_contact

@flow(name="christmas-pre-call-prep", log_prints=True)
def pre_call_prep_flow(email: str, call_date: str) -> dict:
    """
    Send 3-email pre-call prep sequence after booking.

    Emails:
    1. Booking confirmation (immediate)
    2. Questionnaire reminder (24h before call)
    3. Final reminder (2h before call)
    """
    print(f"📞 Starting pre-call prep for {email} (call: {call_date})")

    # Get contact
    contact = search_contact_by_email(email)
    if not contact:
        print(f"❌ Contact not found: {email}")
        return {"success": False, "error": "Contact not found"}

    contact_page_id = contact["id"]
    first_name = contact["properties"]["First Name"]["rich_text"][0]["plain_text"]

    # Update status
    update_contact(
        page_id=contact_page_id,
        properties={
            "Booking Status": {"select": {"name": "Booked"}},
            "Diagnostic Call Date": {"date": {"start": call_date}},
            "Christmas Campaign Status": {"select": {"name": "Pre-Call Prep"}}
        }
    )

    template_vars = {"first_name": first_name, "call_date": call_date}

    # Email 1: Booking confirmation (immediate)
    print("\n📧 Sending Email #1: Booking Confirmation")
    template_1 = get_christmas_template(email_number=101)  # pre_call_1
    email_result_1 = send_template_email(
        to_email=email,
        subject=template_1["subject"],
        template=template_1["html"],
        variables=template_vars
    )
    print(f"   ✅ Sent (ID: {email_result_1.get('id')})")

    # Email 2 & 3: Schedule based on call_date
    # TODO: Implement scheduling via Prefect deployments or external scheduler

    return {"success": True, "emails_sent": 1}
```

#### 3.3 Create customer portal delivery flow (60-second constraint!)

**File**: `campaigns/christmas_campaign/flows/portal_delivery.py`

```python
from prefect import flow, task
from notion_client import Client
import os
from datetime import datetime

notion = Client(auth=os.getenv("NOTION_TOKEN"))
CUSTOMER_PORTAL_DB_ID = os.getenv("NOTION_CUSTOMER_PORTAL_DB_ID")

@task(name="portal-create-page", timeout_seconds=15)
def create_portal_page(email: str, first_name: str, call_date: str) -> str:
    """Create customer portal page in Notion (target: <10 seconds)"""
    portal_page = notion.pages.create(
        parent={"database_id": CUSTOMER_PORTAL_DB_ID},
        properties={
            "Name": {"title": [{"text": {"content": f"{first_name} - Christmas Priority"}}]},
            "Email": {"email": email},
            "Status": {"select": {"name": "Portal Created"}},
            "Call Date": {"date": {"start": call_date}},
        }
    )
    print(f"✅ Portal page created: {portal_page['id']}")
    return portal_page["id"]

@task(name="portal-upload-diagnostic-report", timeout_seconds=20)
def upload_diagnostic_report(page_id: str, diagnostic_results: dict):
    """Upload diagnostic report to portal (target: <15 seconds)"""
    # TODO: Generate PDF from diagnostic_results
    # TODO: Upload to Notion page as file block
    print(f"✅ Diagnostic report uploaded to {page_id}")

@task(name="portal-create-90day-timeline", timeout_seconds=25)
def create_90day_timeline(page_id: str, diagnostic_results: dict):
    """Create 90-day timeline database (target: <20 seconds)"""
    # TODO: Create database inside portal page
    # TODO: Populate with 12 weeks of tasks
    print(f"✅ 90-day timeline created in {page_id}")

@task(name="portal-send-email", timeout_seconds=10)
def send_portal_email(email: str, first_name: str, portal_url: str):
    """Send portal access email (target: <5 seconds)"""
    from campaigns.businessx_canada_lead_nurture.tasks.resend_operations import send_email

    html = f"""
    <h2>Your Customer Portal is Live!</h2>
    <p>Hi {first_name},</p>
    <p>As promised, your customer portal is ready within 60 seconds!</p>
    <p><strong>Access your portal</strong>: <a href="{portal_url}">Open Portal →</a></p>
    """

    send_email(
        to_email=email,
        subject="Your BusOS Customer Portal is Ready (60 seconds!)",
        html=html
    )
    print(f"✅ Portal email sent to {email}")

@flow(name="christmas-portal-delivery-60s", log_prints=True)
def portal_delivery_flow(email: str, first_name: str, call_date: str, diagnostic_results: dict) -> dict:
    """
    Create customer portal and deliver within 60 seconds.

    Timeline:
    - 0-10s: Create portal page
    - 10-25s: Upload diagnostic report
    - 25-45s: Create 90-day timeline
    - 45-60s: Send email
    """
    start_time = datetime.now()
    print(f"🚀 Starting 60-second portal delivery for {email}")

    # Step 1: Create portal (10s)
    portal_page_id = create_portal_page(email, first_name, call_date)
    portal_url = f"https://notion.so/{portal_page_id.replace('-', '')}"

    # Step 2: Upload report (15s)
    upload_diagnostic_report(portal_page_id, diagnostic_results)

    # Step 3: Create timeline (20s)
    create_90day_timeline(portal_page_id, diagnostic_results)

    # Step 4: Send email (5s)
    send_portal_email(email, first_name, portal_url)

    # Calculate delivery time
    end_time = datetime.now()
    delivery_time = (end_time - start_time).total_seconds()
    print(f"✅ Portal delivered in {delivery_time:.1f} seconds (target: <60s)")

    return {
        "success": True,
        "portal_url": portal_url,
        "delivery_time": delivery_time,
        "met_deadline": delivery_time < 60
    }
```

**Commit**: "feat(christmas): add Cal.com webhooks, pre-call prep, and 60s portal delivery"

**Success Criteria**:
- [ ] Cal.com webhook triggers pre-call prep
- [ ] Pre-call prep sends confirmation email
- [ ] Customer portal created in <60 seconds (90%+ of time)
- [ ] Portal email sent successfully
- [ ] Notion contact status updated correctly
- [ ] Integration tests pass

---

### Wave 4: Phase 2 Transition + Coaching Emails + Polish (4-5 hours)

**Objective**: Implement Day 14 decision email, Phase 2B coaching sequence, documentation, and testing

#### 4.1 Create Day 14 decision email

**File**: `campaigns/christmas_campaign/flows/day14_decision.py`

```python
from prefect import flow
from datetime import datetime, timedelta
from campaigns.christmas_campaign.tasks.christmas_templates import get_christmas_template
from campaigns.businessx_canada_lead_nurture.tasks.resend_operations import send_template_email
from campaigns.businessx_canada_lead_nurture.tasks.notion_operations import search_contact_by_email, update_contact

@flow(name="christmas-day14-decision", log_prints=True)
def day14_decision_flow(email: str, diagnostic_call_date: str) -> dict:
    """
    Send Day 14 decision email presenting Phase 2 options.

    Triggered 14 days after diagnostic call completion.
    """
    print(f"📊 Sending Day 14 decision email to {email}")

    contact = search_contact_by_email(email)
    if not contact:
        return {"success": False, "error": "Contact not found"}

    contact_page_id = contact["id"]
    first_name = contact["properties"]["First Name"]["rich_text"][0]["plain_text"]

    # Get template
    template = get_christmas_template(email_number=201)  # day14_decision

    # Send email
    template_vars = {
        "first_name": first_name,
        "diagnostic_call_date": diagnostic_call_date,
        # Add more vars from contact properties
    }

    email_result = send_template_email(
        to_email=email,
        subject=template["subject"],
        template=template["html"],
        variables=template_vars
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

#### 4.2 Create Phase 2B coaching email sequence

**File**: `campaigns/christmas_campaign/flows/phase2b_coaching.py`

```python
from prefect import flow
from campaigns.christmas_campaign.tasks.christmas_templates import get_christmas_template
from campaigns.businessx_canada_lead_nurture.tasks.resend_operations import send_template_email

@flow(name="christmas-phase2b-welcome", log_prints=True)
def phase2b_welcome_flow(email: str, first_name: str, enrollment_date: str) -> dict:
    """Send Phase 2B welcome email"""
    template = get_christmas_template(email_number=301)  # phase2b_welcome

    email_result = send_template_email(
        to_email=email,
        subject=template["subject"],
        template=template["html"],
        variables={"first_name": first_name, "enrollment_date": enrollment_date}
    )

    return {"success": True, "email_id": email_result.get("id")}

@flow(name="christmas-phase2b-weekly-prep", log_prints=True)
def phase2b_weekly_prep_flow(email: str, week_number: int, agenda: list) -> dict:
    """Send weekly prep email 24h before coaching call"""
    template = get_christmas_template(email_number=302)  # phase2b_weekly_prep

    # TODO: Implement full logic

    return {"success": True}
```

#### 4.3 Add comprehensive documentation

1. **Update main README.md**
   - Add Christmas campaign section
   - Document new flows
   - Update environment variables

2. **Create campaign-specific docs**
   - `campaigns/christmas_campaign/README.md` - Campaign overview
   - `campaigns/christmas_campaign/ARCHITECTURE.md` - Technical details
   - `campaigns/christmas_campaign/TESTING.md` - Testing guide

3. **Add JSDoc-style comments**
   ```python
   def christmas_nurture_flow(...):
       """
       Execute complete 7-email Christmas nurture sequence.

       Args:
           contact_page_id: Notion contact page ID
           email: Recipient email address
           assessment_data: Assessment scores and metadata

       Returns:
           Dictionary with execution summary:
           {
               "success": True,
               "emails_sent": 7,
               "sent_email_ids": {...}
           }

       Raises:
           ValueError: If required assessment data missing
           HTTPError: If API calls fail after retries

       Example:
           result = christmas_nurture_flow(
               contact_page_id="page-123",
               email="test@example.com",
               assessment_data={...}
           )
       """
   ```

#### 4.4 Run all quality checks

```bash
# Type check (if using mypy)
python -m mypy campaigns/christmas_campaign/

# Linting
python -m pylint campaigns/christmas_campaign/

# All tests
pytest campaigns/christmas_campaign/tests/ -v

# Coverage
pytest campaigns/christmas_campaign/tests/ --cov=campaigns.christmas_campaign --cov-report=html

# Integration test
python test_integration_christmas.py --mode mock
```

#### 4.5 Manual testing checklist

- [ ] Send all 7 emails to mail-tester.com (target: 8/10+ spam score)
- [ ] Test customer portal creation (<60s)
- [ ] Verify Cal.com webhook triggers correctly
- [ ] Check all template variables replaced
- [ ] Test exit conditions (booking, unsubscribe)
- [ ] Verify Day 14 email triggers after 14 days
- [ ] Test Phase 2B welcome email

**Commit**: "docs(christmas): add comprehensive documentation and testing"

**Success Criteria**:
- [ ] All flows documented
- [ ] README updated
- [ ] All unit tests pass (>80% coverage)
- [ ] Integration tests pass
- [ ] Manual testing complete
- [ ] No console.log or debug statements
- [ ] All commits follow convention

---

## Quality & Validation Checklist

Before considering complete:
- [ ] All unit tests pass (>80% coverage)
- [ ] Integration tests pass (mocked and real mode)
- [ ] All 7 emails send correctly
- [ ] Customer portal created <60 seconds
- [ ] Cal.com webhook integration works
- [ ] Day 14 decision email triggers
- [ ] Phase 2B emails send correctly
- [ ] All template variables substituted
- [ ] Exit conditions work (booking, unsubscribe, complete)
- [ ] Notion databases updated correctly
- [ ] Environment variables documented
- [ ] README updated
- [ ] API documentation complete
- [ ] All commits follow convention
- [ ] No debug statements (print statements OK for logging)
- [ ] Error handling comprehensive
- [ ] Performance acceptable (<60s portal, <5s emails)

---

## Rollback & Contingency Plan

**If blocked or failed:**

1. **Stop immediately** - Don't continue if stuck

2. **Document blocker** in `BLOCKERS.md`:
   - What you were trying
   - What failed
   - Error messages
   - What you've tried

3. **Preserve work**:
   ```bash
   git add .
   git commit -m "wip(christmas): [what was being done]

   Blocked on: [specific issue]
   See BLOCKERS.md for details"
   ```

4. **Offer options**:
   - **Option A**: Revert and try alternative approach
   - **Option B**: User provides guidance/API keys
   - **Option C**: Skip temporarily (if low-risk)

5. **Don't force it** - Quality over speed

---

## Dependencies & Risk Management

### External Dependencies
- **Notion API**: Already integrated ✅
- **Resend API**: Already integrated ✅
- **Cal.com Webhooks**: Need webhook secret from user ⚠️
  - **Alternatives**: Manual trigger endpoint
  - **Risk**: Webhooks can be unreliable
  - **Mitigation**: Implement idempotency, retry logic

### Risks

**High Risk: 60-second portal delivery**
- **Problem**: Notion API can be slow (200-500ms per call)
- **Mitigation**: Use async operations, parallel calls, background completion
- **Detection**: Log delivery time on every portal creation
- **Fallback**: Send email even if portal not fully ready, finish in background

**Medium Risk: Cal.com webhook reliability**
- **Problem**: Webhooks can fail or be delayed
- **Mitigation**: Implement signature verification, idempotency keys, manual trigger endpoint
- **Monitoring**: Alert on webhook failures
- **Plan B**: Admin can manually trigger pre-call prep via API

**Medium Risk: Email deliverability**
- **Problem**: Spam filters may block emails
- **Mitigation**: Use Resend (good reputation), test with mail-tester.com, proper SPF/DKIM
- **Monitoring**: Track bounce/spam rates in Resend dashboard
- **Plan B**: Fall back to personal email (sang@sanglescalinglabs.com)

**Low Risk: Template variable errors**
- **Problem**: Missing placeholders break emails
- **Mitigation**: Validate templates before sending, provide defaults
- **Detection**: Test all templates in Wave 4
- **Plan B**: Fallback to static templates

---

## Success Definition

This plan succeeds when:
- ✅ All 4 waves completed
- ✅ Quality checklist 100% satisfied
- ✅ 7-email nurture sequence working end-to-end
- ✅ Customer portal delivered in <60 seconds
- ✅ Cal.com integration functional
- ✅ Day 14 + Phase 2B emails working
- ✅ All tests passing
- ✅ Documentation complete
- ✅ Ready for production deployment

---

## Timeline Estimate

| Wave | Description | Estimated Time |
|------|-------------|----------------|
| Wave 1 | Foundation & Setup | 3-4 hours |
| Wave 2 | 7-Email Nurture Sequence | 6-7 hours |
| Wave 3 | Webhooks + Portal | 5-6 hours |
| Wave 4 | Phase 2 + Polish | 4-5 hours |
| **Total** | **All waves** | **18-22 hours** |

**Note**: Handoff estimated 13-20 hours. My estimate is 18-22 hours due to:
- Comprehensive testing (added 2-3 hours)
- Documentation (added 1-2 hours)
- TDD approach (adds ~20% overhead, but saves debugging time)

**Recommendation**: Start with Wave 1+2 (core nurture sequence), get user feedback, then proceed to Wave 3+4.
