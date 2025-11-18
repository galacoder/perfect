---
name: prefect-marketing-automation
description: Advanced Prefect v3 skill for building campaign-based marketing automation workflows including email campaigns (Resend), CRM sync (Notion), lead scoring, and assessment-driven nurture sequences. Uses campaign-based organization structure for scalability. Provides interactive flow generation and production-ready templates aligned with BusOS 8-System Framework. Use this skill when creating marketing workflows, campaign automation, lead nurturing sequences, or analytics pipelines in the perfect project.
---

# Prefect Marketing Automation Skill

## Overview

This skill helps you build sophisticated marketing automation workflows using **Prefect v3** with a **campaign-based organization structure**. It provides both interactive flow generation and a comprehensive template library for orchestrating campaigns, scoring leads, and analyzing performance.

**Key Capabilities:**
- 🎯 Email campaign orchestration (Assessment-driven nurture, segment-based routing)
- 📊 Lead scoring and automated routing (CRITICAL/URGENT/OPTIMIZE)
- 📈 Marketing analytics and ETL pipelines
- 🔔 Discord notifications for hot leads (CRITICAL segment)
- 🔄 Notion CRM bi-directional sync
- ✉️ Resend transactional email integration (dynamic templates from Notion)
- 🏗️ **Campaign-based organization** for multi-campaign scalability

**Your Setup:**
- **Prefect Version**: 3.4.1 (self-hosted)
- **Location**: `/Users/sangle/Dev/action/projects/perfect`
- **Organization**: Campaign-based structure (`campaigns/{campaign_name}/`)
- **Integrations**: Resend (email), Notion (CRM + Templates), Discord (notifications)

---

## Campaign-Based Organization Structure

**NEW**: All workflows are organized by campaign for better scalability:

```
perfect/
└── campaigns/
    └── {campaign_name}/               # e.g., businessx_canada_lead_nurture
        ├── README.md                  # Campaign overview
        ├── ARCHITECTURE.md            # Technical architecture
        ├── flows/                     # Prefect flows
        │   ├── signup_handler.py      # Handle new signups
        │   ├── assessment_handler.py  # Process assessments
        │   └── email_sequence.py      # Nurture sequence
        ├── tasks/                     # Prefect tasks
        │   ├── notion_operations.py   # Notion CRUD
        │   ├── resend_operations.py   # Email sending
        │   ├── routing.py             # Segment classification
        │   └── template_operations.py # Dynamic templates
        ├── tests/                     # Unit tests
        │   ├── test_notion_operations.py
        │   ├── test_resend_operations.py
        │   └── test_routing.py
        └── diagrams/                  # ASCII workflow diagrams
            ├── CAMPAIGN_OVERVIEW.txt
            ├── SIGNUP_HANDLER.txt
            ├── ASSESSMENT_HANDLER.txt
            └── EMAIL_SEQUENCE.txt
```

**Benefits**:
- ✅ Scale to multiple campaigns without file conflicts
- ✅ Self-documenting (README + diagrams per campaign)
- ✅ Clear ownership and team collaboration
- ✅ Easier testing and maintenance

---

## When to Use This Skill

Use this skill when you need to:

1. **Create new campaigns**
   - Assessment-driven nurture campaigns
   - Lead magnet funnels with segment-based routing
   - Multi-email sequences with dynamic timing
   - Webhook-triggered automation

2. **Build lead scoring systems**
   - BusOS 8-System scoring (Red/Orange/Yellow/Green)
   - Automated routing (CRITICAL/URGENT/OPTIMIZE)
   - Multi-touch attribution
   - Customer journey tracking

3. **Implement email workflows**
   - Dynamic Notion templates (edit without deployment)
   - Segment-specific email variants
   - Variable substitution ({{first_name}}, {{business_name}})
   - Testing mode (fast waits) vs Production mode (24-48hr waits)

4. **Set up webhook integrations**
   - FastAPI webhook server
   - Signup form processing
   - Assessment completion triggers
   - Real-time flow execution

5. **Organize complex workflows**
   - Campaign-based structure
   - ASCII workflow diagrams
   - Comprehensive documentation
   - Scalable architecture

---

## Quick Start

### Option 1: Interactive Campaign Generator (Fastest)

**Ask the skill to generate a new campaign:**

```
"Create a new email nurture campaign for beauty salon leads"
"Build an assessment-driven workflow with segment routing"
"Set up a 5-email sequence with Notion templates"
"Generate a campaign for [your use case]"
```

**The skill will ask clarifying questions:**
- Campaign name and purpose
- Email sequence structure (universal vs segment-specific)
- Trigger mechanism (webhook, scheduled, manual)
- Integration requirements (Resend, Notion, Discord)
- Testing mode preferences

**Then generate:**
- Complete campaign directory structure
- Prefect flows with @flow decorators
- Task modules with retry logic
- ASCII workflow diagrams
- README and ARCHITECTURE docs
- Testing instructions
- Deployment configuration

---

### Option 2: Clone Existing Campaign

Browse the existing campaign and customize:

**Reference Campaign**: `businessx_canada_lead_nurture`

**Location**: `campaigns/businessx_canada_lead_nurture/`

**What it includes:**
- 3 flows: signup_handler, assessment_handler, email_sequence
- 4 task modules: notion_operations, resend_operations, routing, template_operations
- 3 test suites with 93 unit tests
- 4 ASCII diagrams documenting workflows
- Complete README and ARCHITECTURE

**Clone and customize:**
```bash
cd /Users/sangle/Dev/action/projects/perfect
cp -r campaigns/businessx_canada_lead_nurture campaigns/your_campaign_name

# Update imports in all files
sed -i '' 's/businessx_canada_lead_nurture/your_campaign_name/g' campaigns/your_campaign_name/**/*.py
```

---

## Campaign Structure Guide

### Flows Layer (campaigns/{name}/flows/)

**Purpose**: Orchestrate high-level business workflows

**Pattern**:
```python
from prefect import flow
from campaigns.{campaign_name}.tasks.notion_operations import create_contact
from campaigns.{campaign_name}.tasks.routing import determine_segment

@flow(name="signup-handler")
def signup_handler_flow(email: str, name: str, first_name: str, business_name: str):
    """
    Handle new user signup from webhook.

    Steps:
    1. Search for existing contact in Notion
    2. Create new contact if not exists
    3. Update existing contact if found
    """
    contact = create_contact(email, name, first_name, business_name)
    return {"status": "created", "page_id": contact["id"]}
```

**Flows should**:
- Orchestrate tasks (don't contain business logic)
- Use descriptive @flow decorators with names
- Return structured results
- Handle high-level error recovery

### Tasks Layer (campaigns/{name}/tasks/)

**Purpose**: Reusable business logic and API integrations

**Pattern**:
```python
from prefect import task

@task(retries=3, retry_delay_seconds=60)
def create_contact(email: str, name: str, first_name: str, business_name: str):
    """
    Create contact in Notion Contacts database.

    Args:
        email: Contact email address
        name: Full name
        first_name: First name for personalization
        business_name: Business name

    Returns:
        dict: Notion page object with id, properties
    """
    # Implementation with retry logic
    pass
```

**Tasks should**:
- Contain business logic
- Have retry decorators for external APIs
- Be testable in isolation
- Return consistent data structures

### Diagrams Layer (campaigns/{name}/diagrams/)

**Purpose**: ASCII workflow visualization

**Files**:
- `CAMPAIGN_OVERVIEW.txt` - High-level architecture
- `{FLOW_NAME}.txt` - Detailed flow diagrams
- `EMAIL_SEQUENCE.txt` - Email timing and content

**Benefits**:
- Version controlled (no external tools)
- Viewable in any text editor
- Self-documenting
- Easy to maintain

### Tests Layer (campaigns/{name}/tests/)

**Purpose**: Unit tests for tasks and flows

**Pattern**:
```python
import pytest
from unittest.mock import patch
from campaigns.{campaign_name}.tasks.notion_operations import create_contact

@pytest.fixture
def mock_notion_client():
    with patch('campaigns.{campaign_name}.tasks.notion_operations.notion') as mock:
        yield mock

def test_create_contact(mock_notion_client):
    mock_notion_client.pages.create.return_value = {"id": "test-123"}

    result = create_contact("test@example.com", "Test User", "Test", "Test Co")

    assert result["id"] == "test-123"
    mock_notion_client.pages.create.assert_called_once()
```

---

## Integration Guides

### Resend Email Integration

**Setup**: Dynamic templates from Notion

**Key Features:**
- Templates stored in Notion Templates DB (edit without deployment)
- Variable substitution: `{{first_name}}`, `{{business_name}}`
- Segment-specific variants (email_2a_critical, email_2b_urgent, email_2c_optimize)
- Testing mode for fast validation

**Code Example:**
```python
from prefect import task
from campaigns.{campaign_name}.tasks.template_operations import get_template
from campaigns.{campaign_name}.tasks.resend_operations import send_template_email

@task(retries=3)
def send_nurture_email(email: str, template_name: str, first_name: str, business_name: str):
    """Send email using Notion template with variable substitution"""

    # Fetch template from Notion (cached)
    template = get_template(template_name, use_notion=True)

    # Send via Resend with variable substitution
    result = send_template_email(
        to_email=email,
        template=template,
        variables={
            "first_name": first_name,
            "business_name": business_name
        },
        from_email="noreply@yourdomain.com"
    )

    return result
```

**Template Structure in Notion**:
| Field | Type | Example |
|-------|------|---------|
| Template Name | Title | "email_1" |
| Subject | Rich Text | "Thanks {{first_name}}!" |
| HTML Body | Rich Text | "<p>Hi {{first_name}} from {{business_name}}</p>" |
| Active | Checkbox | ✓ |

---

### Notion CRM Integration

**Setup**: Bi-directional sync with Contacts and Templates databases

**Key Features:**
- Contact CRUD (create, search, update, get)
- Dynamic template fetching with caching
- Custom property mapping
- Real-time updates

**Code Example:**
```python
from campaigns.{campaign_name}.tasks.notion_operations import (
    search_contact_by_email,
    create_contact,
    update_contact
)

@flow
def sync_contact_flow(email: str, properties: dict):
    # Search for existing contact
    existing = search_contact_by_email(email)

    if existing:
        # Update existing contact
        update_contact(existing["id"], properties)
    else:
        # Create new contact
        create_contact(
            email=email,
            name=properties["name"],
            first_name=properties["first_name"],
            business_name=properties["business_name"]
        )
```

**Database Structure**:
- **Contacts DB**: Name, Email, First Name, Business Name, Signup Source, Assessment Score, Segment
- **Templates DB**: Template Name, Subject, HTML Body, Active, Last Modified

---

### Discord Notifications

**Setup**: Hot lead alerts for CRITICAL segment

**Key Features:**
- Instant alerts for high-value leads (CRITICAL = 2+ red systems)
- Rich embeds with lead details
- Error notifications
- Campaign completion reports

**Code Example:**
```python
import httpx
from prefect import task

@task
def send_discord_hot_lead_alert(email: str, segment: str, red_systems: int):
    """Send Discord notification for hot leads"""

    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")

    payload = {
        "content": "🚨 **Hot Lead Alert!**",
        "embeds": [{
            "title": f"{segment} Segment Contact",
            "description": "New contact needs immediate attention",
            "color": 16711680,  # Red
            "fields": [
                {"name": "Email", "value": email, "inline": True},
                {"name": "Segment", "value": segment, "inline": True},
                {"name": "Red Systems", "value": str(red_systems), "inline": True}
            ],
            "footer": {"text": "BusOS Email Sequence"},
            "timestamp": datetime.now().isoformat()
        }]
    }

    httpx.post(webhook_url, json=payload, timeout=10)
```

---

## Segment-Based Routing

**Pattern**: BusOS 8-System Assessment scoring

### Segment Classification

```python
from campaigns.{campaign_name}.tasks.routing import determine_segment

def classify_lead(red_systems: int, orange_systems: int) -> str:
    """
    Classify lead into segment based on broken systems.

    Rules:
    - CRITICAL: 2+ red systems (immediate action needed)
    - URGENT: 1 red OR 2+ orange (attention needed soon)
    - OPTIMIZE: 0-1 red, 0-1 orange (growth opportunities)
    """
    segment = determine_segment(red_systems, orange_systems)
    return segment  # "CRITICAL", "URGENT", or "OPTIMIZE"
```

### Email Template Selection

**Universal Emails** (all segments):
- Email #1: Immediate thank you and assessment results
- Email #3: BusOS Framework introduction
- Email #4: Offer presentation

**Segment-Specific Emails**:
- Email #2:
  - `email_2a_critical` - High urgency messaging
  - `email_2b_urgent` - Medium urgency
  - `email_2c_optimize` - Growth-focused
- Email #5:
  - `email_5a_critical` - Strong deadline urgency
  - `email_5b_urgent` - Moderate urgency
  - `email_5c_optimize` - Opportunity-focused

**Code Example**:
```python
from campaigns.{campaign_name}.tasks.routing import select_email_template

# Select appropriate template based on segment
template_name = select_email_template(email_number=2, segment="CRITICAL")
# Returns: "email_2a_critical"
```

---

## Testing Mode vs Production Mode

**Environment Variable**: `TESTING_MODE`

### Testing Mode (TESTING_MODE=true)

**Purpose**: Fast validation without waiting

**Wait Times**:
- Email #1 → #2: 1 minute
- Email #2 → #3: 2 minutes
- Email #3 → #4: 3 minutes
- Email #4 → #5: 4 minutes

**Use when**: Developing, testing, validating workflows

### Production Mode (TESTING_MODE=false)

**Purpose**: Real campaign execution

**Wait Times**:
- Email #1 → #2: 24 hours
- Email #2 → #3: 48 hours
- Email #3 → #4: 48 hours
- Email #4 → #5: 48 hours

**Use when**: Live campaigns, production deployment

**Code Example**:
```python
from campaigns.{campaign_name}.tasks.routing import get_wait_duration

# Get appropriate wait time
wait_seconds = get_wait_duration(email_number=1, testing_mode=False)
# Returns: 86400 (24 hours) in production
# Returns: 60 (1 minute) in testing
```

---

## Deployment to Your Self-Hosted Server

**Your Prefect Installation:**
- Location: `/Users/sangle/Dev/action/projects/perfect`
- Version: Prefect 3.4.1
- Profile: `local` (self-hosted)

### Option 1: FastAPI Webhook Server (Recommended)

**Best for**: Production webhook-triggered flows

```bash
cd /Users/sangle/Dev/action/projects/perfect

# Start webhook server
uvicorn server:app --reload --port 8000

# In production
uvicorn server:app --host 0.0.0.0 --port 8000 --workers 4
```

**Webhook Endpoints**:
- `POST /webhook/signup` - Handle new signups
- `POST /webhook/assessment` - Process completed assessments
- `GET /health` - Health check

**Test**:
```bash
curl -X POST http://localhost:8000/webhook/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","name":"Test User","first_name":"Test","business_name":"Test Co"}'
```

### Option 2: Prefect Deployments

**Best for**: Scheduled flows, background processing

```bash
cd /Users/sangle/Dev/action/projects/perfect

# Deploy flows
python flows/deploy.py

# Start Prefect agent
prefect agent start -q default
```

### Option 3: Direct Flow Execution

**Best for**: Testing, one-off runs

```python
from campaigns.businessx_canada_lead_nurture.flows.email_sequence import email_sequence_flow

# Run flow directly
result = email_sequence_flow(
    contact_page_id="notion-page-id",
    email="test@example.com",
    first_name="Test",
    business_name="Test Co",
    red_systems=2,
    orange_systems=1
)
```

---

## Creating a New Campaign

### Step 1: Generate Campaign Structure

**Ask the skill**:
```
"Create a new campaign called 'spring_promo_2025' for seasonal promotion"
```

**Or manually create**:
```bash
cd /Users/sangle/Dev/action/projects/perfect

mkdir -p campaigns/spring_promo_2025/{flows,tasks,tests,diagrams}
touch campaigns/spring_promo_2025/{README.md,ARCHITECTURE.md}
touch campaigns/spring_promo_2025/{flows,tasks,tests}/__init__.py
```

### Step 2: Define Flows

```python
# campaigns/spring_promo_2025/flows/promo_handler.py
from prefect import flow
from campaigns.spring_promo_2025.tasks.email_ops import send_promo_email

@flow(name="spring-promo-handler")
def promo_handler_flow(email: str, promo_code: str):
    """Handle spring promotion signup"""
    send_promo_email(email, promo_code)
    return {"status": "sent"}
```

### Step 3: Create Tasks

```python
# campaigns/spring_promo_2025/tasks/email_ops.py
from prefect import task
import httpx

@task(retries=3)
def send_promo_email(email: str, promo_code: str):
    """Send promotional email via Resend"""
    # Implementation
    pass
```

### Step 4: Write Tests

```python
# campaigns/spring_promo_2025/tests/test_email_ops.py
from campaigns.spring_promo_2025.tasks.email_ops import send_promo_email

def test_send_promo_email():
    result = send_promo_email("test@example.com", "SPRING25")
    assert result["status"] == "sent"
```

### Step 5: Document

Create ASCII diagrams, README, and ARCHITECTURE docs following the `businessx_canada_lead_nurture` pattern.

---

## Best Practices

### Campaign Organization
- [ ] One campaign per business objective
- [ ] Self-documenting with README and diagrams
- [ ] Separate flows (orchestration) from tasks (logic)
- [ ] Comprehensive tests (aim for 75%+ coverage)

### Production Checklist
- [ ] Environment variables for API keys (never hardcode)
- [ ] Retry logic for external APIs (3 attempts minimum)
- [ ] Error notifications (Discord/Slack)
- [ ] Logging at key decision points
- [ ] Testing mode validation before production
- [ ] Monitoring via Prefect UI or FastAPI logs
- [ ] Version control for all campaign files

### Security
- [ ] Use environment variables for credentials
- [ ] Rotate API keys regularly
- [ ] Validate webhook signatures
- [ ] Limit worker permissions (least privilege)
- [ ] Monitor for unusual activity

---

## Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'campaigns.{name}'`
**Solution**: Ensure you're running from project root and campaign exists:
```bash
cd /Users/sangle/Dev/action/projects/perfect
python -c "from campaigns.{campaign_name}.flows.{flow_name} import {flow_function}"
```

**Issue**: `NOTION_TOKEN not found`
**Solution**: Set environment variables:
```bash
export NOTION_TOKEN=ntn_xxxxx
export NOTION_CONTACTS_DB_ID=xxxxx
export NOTION_TEMPLATES_DB_ID=xxxxx
export RESEND_API_KEY=re_xxxxx
```

**Issue**: `Tests failing after campaign creation`
**Solution**: Update mock patch paths to use new campaign structure:
```python
# OLD
with patch('tasks.notion_operations.notion') as mock:

# NEW
with patch('campaigns.{campaign_name}.tasks.notion_operations.notion') as mock:
```

**Issue**: `Email templates not loading from Notion`
**Solution**:
1. Seed templates: `python scripts/seed_templates.py`
2. Verify Templates DB ID in .env
3. Check template Active checkbox in Notion

---

## Reference Campaigns

### businessx_canada_lead_nurture

**Location**: `campaigns/businessx_canada_lead_nurture/`

**Features**:
- ✅ 3 flows (signup, assessment, email sequence)
- ✅ 4 task modules (notion, resend, routing, templates)
- ✅ 93 unit tests with pytest
- ✅ 4 ASCII workflow diagrams
- ✅ Segment-based routing (CRITICAL/URGENT/OPTIMIZE)
- ✅ Dynamic Notion templates
- ✅ Testing and production modes
- ✅ FastAPI webhook server
- ✅ Discord hot lead alerts

**Use as template for**:
- Assessment-driven campaigns
- Multi-email nurture sequences
- Segment-based content routing
- Webhook-triggered workflows

---

## Resources

**Project Location**: `/Users/sangle/Dev/action/projects/perfect`

**Campaign Documentation**:
- README: `campaigns/{campaign_name}/README.md`
- Architecture: `campaigns/{campaign_name}/ARCHITECTURE.md`
- Diagrams: `campaigns/{campaign_name}/diagrams/`

**Project Documentation**:
- Main README: `README.md`
- Deployment: `DEPLOYMENT.md`
- Migration Guide: `MIGRATION_GUIDE.md`
- Validation Report: `VALIDATION_REPORT.md`

**Prefect Docs**: https://docs.prefect.io/3.0/
**Resend API**: https://resend.com/docs
**Notion API**: https://developers.notion.com/

---

## Next Steps

1. **Explore existing campaign**
   - Read `campaigns/businessx_canada_lead_nurture/README.md`
   - Review ASCII diagrams in `diagrams/`
   - Run dry-run tests: `python test_flows_dry_run.py`

2. **Create your first campaign**
   - Ask skill to generate campaign structure
   - Define flows and tasks
   - Write tests
   - Create documentation

3. **Deploy and test**
   - Start webhook server: `uvicorn server:app --reload`
   - Test with curl or integration tests
   - Monitor in FastAPI logs

4. **Scale gradually**
   - Add new campaigns following the pattern
   - Reuse task modules across campaigns
   - Build shared utilities in project root

**Questions or need help?** Reference:
- Campaign README for overview
- ARCHITECTURE.md for technical details
- ASCII diagrams for workflow visualization
- Migration guide for structure explanation

---

**Skill Version**: 2.0 (Campaign-Based Organization)
**Updated**: 2025-01-14
**Prefect Version**: 3.4.1+
**Framework**: BusOS 8-System Assessment
