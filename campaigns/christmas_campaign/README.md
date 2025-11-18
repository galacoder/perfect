# Christmas Campaign Email Automation

Automated 7-email nurture sequence for holiday salon bookings, built with Prefect v3 and Notion.

---

## Overview

This campaign sends a 7-email sequence to salon owners who complete the BusOS assessment, focusing on Christmas revenue optimization. Templates are dynamically fetched from Notion for easy editing by the marketing team.

**Timeline**: 14 days (2 weeks)
**Emails**: 7 total (1 per 2 days)
**Tech Stack**: Prefect v3, Notion API, Resend API

---

## Email Sequence

| Email | Day | Subject | Purpose |
|-------|-----|---------|---------|
| 1 | 0 | Assessment Results | Share BusOS scores & revenue leak |
| 2 | 2 | System Fix Framework | Provide actionable fix for weakest system |
| 3 | 4 | Horror Story | Show consequence of inaction (Sarah's story) |
| 4 | 6 | Diagnostic Booking Ask | Invite to free diagnostic call |
| 5 | 8 | Case Study | Demonstrate success (Min-Ji transformation) |
| 6 | 10 | Christmas Readiness Checklist | Audit 5 systems before December |
| 7 | 12 | Final Urgency | Last chance for Christmas slots |

---

## Template Management

### Upload Templates to Notion

All email templates are stored in Notion for dynamic editing:

```bash
# Upload all 7 templates
python campaigns/christmas_campaign/scripts/seed_email_templates.py

# Upload single template
python campaigns/christmas_campaign/scripts/seed_email_templates.py --template christmas_email_1

# Dry-run (see what would be uploaded)
python campaigns/christmas_campaign/scripts/seed_email_templates.py --dry-run
```

**Features**:
- ✅ Idempotent (safe to run multiple times)
- ✅ Preserves `{{variable}}` placeholders
- ✅ Updates existing templates (no duplicates)
- ✅ Validates environment variables

### Template Variables

All templates use `{{variable}}` syntax for personalization:

**Contact Info**:
- `{{first_name}}` - Contact first name
- `{{email}}` - Contact email

**Assessment Scores**:
- `{{GPSScore}}` - GPS system score (0-100)
- `{{GenerateScore}}` - Generate subscore
- `{{PersuadeScore}}` - Persuade subscore
- `{{ServeScore}}` - Serve subscore
- `{{MoneyScore}}` - Money system score

**Weaknesses** (ranked 1-2):
- `{{WeakestSystem1}}` - Name of weakest system
- `{{WeakestSystem2}}` - Name of 2nd weakest system
- `{{Score1}}` - Score of weakest system
- `{{Score2}}` - Score of 2nd weakest system

**Revenue Leak**:
- `{{RevenueLeakSystem1}}` - Monthly revenue leak from system 1
- `{{RevenueLeakSystem2}}` - Monthly revenue leak from system 2
- `{{TotalRevenueLeak}}` - Total monthly revenue leak
- `{{TotalRevenueLeak_K}}` - Total leak in thousands (e.g., "12")
- `{{AnnualRevenueLeak}}` - Annualized revenue leak

**Quick Win**:
- `{{QuickWinAction}}` - Actionable step for today
- `{{QuickWinExplanation}}` - Why it works
- `{{QuickWinImpact}}` - Expected financial impact

**Christmas-specific**:
- `{{Christmas_Slots_Remaining}}` - Number of diagnostic slots left
- `{{Christmas_Deadline}}` - Last date to book for implementation

---

## Template Configuration

Templates are defined in `campaigns/christmas_campaign/config/email_templates_christmas.py`:

```python
TEMPLATES = {
    "christmas_email_1": {
        "subject": "[RESULTS] Your salon is losing ${{TotalRevenueLeak_K}}K/month",
        "html_body": """<h2>Your BusOS Assessment Results Are Ready</h2>
        <p>Hi {{first_name}},</p>
        ...""",
        "campaign": "Christmas Campaign",
        "email_number": 1,
        "segment": ["universal"],
        "active": True
    },
    # ... 6 more templates
}
```

**Schema**:
- `subject` (str): Email subject with {{variables}}
- `html_body` (str): HTML email content
- `campaign` (str): Campaign identifier
- `email_number` (int): Sequence position (1-7)
- `segment` (list): Target segments (["universal"])
- `active` (bool): Whether template is active

---

## Notion Database Schema

**Database**: Email Templates (NOTION_EMAIL_TEMPLATES_DB_ID)

| Property | Type | Description |
|----------|------|-------------|
| Template Name | Title | Unique identifier (e.g., "christmas_email_1") |
| Subject Line | Rich Text | Email subject |
| Email Body HTML | Rich Text | Email HTML content |
| Email Number | Number | Sequence position (1-7) |
| Status | Select | Active / Inactive |
| Segment | Multi-select | Target segments |
| Template Type | Select | "Nurture Sequence" |
| Variables | Rich Text | List of {{variables}} used |
| Preview Text | Rich Text | Email preview snippet |
| Last Updated | Date | Auto-populated timestamp |

---

## Fetching Templates

Templates are fetched dynamically by Prefect flows:

```python
from campaigns.christmas_campaign.tasks.notion_operations import fetch_email_template

# Fetch template (returns dict with 'subject' and 'html_body')
template = fetch_email_template("christmas_email_1")
subject = template["subject"]
html_body = template["html_body"]
```

**Features**:
- ✅ Queries Notion database by Template Name
- ✅ Extracts subject and HTML body
- ✅ Preserves {{variable}} placeholders
- ✅ Returns None if template not found
- ✅ Includes retry logic (3 retries, 60s delay)

---

## Testing

### Unit Tests

```bash
# Run all unit tests (excludes integration)
pytest campaigns/christmas_campaign/tests/test_seed_email_templates.py -v -k "not integration"

# Run specific test class
pytest campaigns/christmas_campaign/tests/test_seed_email_templates.py::TestTemplateConfig -v

# Run with coverage
pytest campaigns/christmas_campaign/tests/test_seed_email_templates.py --cov
```

**Test Coverage**:
- ✅ 10 unit tests (100% passing)
- ✅ Template configuration validation
- ✅ Upload function mocking
- ✅ Idempotency testing
- ✅ Error handling

### Integration Tests

```bash
# Run integration tests (requires NOTION_TOKEN)
pytest campaigns/christmas_campaign/tests/test_seed_email_templates.py -m integration -v
```

**Note**: Integration tests create/update real Notion pages. Ensure `NOTION_TOKEN` and `NOTION_EMAIL_TEMPLATES_DB_ID` are set in `.env`.

---

## Environment Variables

Required variables in `.env`:

```bash
NOTION_TOKEN=secret_xxxxx                           # Notion integration token
NOTION_EMAIL_TEMPLATES_DB_ID=2ab7c374-1115-8115... # Email Templates database ID
```

Get your Notion token from: https://www.notion.so/my-integrations

---

## File Structure

```
campaigns/christmas_campaign/
├── README.md                           # This file
├── config/
│   └── email_templates_christmas.py   # Template definitions (7 emails)
├── scripts/
│   ├── __init__.py
│   └── seed_email_templates.py        # Upload script with CLI
├── tasks/
│   └── notion_operations.py           # fetch_email_template() function
└── tests/
    └── test_seed_email_templates.py   # Unit + integration tests
```

---

## Usage Workflow

1. **Define Templates**: Edit `config/email_templates_christmas.py`
2. **Upload to Notion**: Run `python campaigns/christmas_campaign/scripts/seed_email_templates.py`
3. **Verify in Notion**: Check templates in Notion database
4. **Edit in Notion**: Marketing team edits templates directly in Notion
5. **Fetch in Flow**: Prefect flows fetch latest templates dynamically

---

## Troubleshooting

### Templates Not Uploading

```bash
# Check environment variables
python campaigns/christmas_campaign/scripts/seed_email_templates.py --dry-run

# Verify Notion integration has access to database
# Go to: https://notion.so/[DATABASE_ID]
# Click "..." → "Add connections" → Select your integration
```

### Variables Not Preserved

Ensure `{{variable}}` syntax is used (not `{variable}` or `${variable}`). The upload script preserves all `{{...}}` placeholders.

### Template Not Found

```python
# Check template exists in Notion
from notion_client import Client
import os

notion = Client(auth=os.getenv("NOTION_TOKEN"))
response = notion.databases.query(
    database_id=os.getenv("NOTION_EMAIL_TEMPLATES_DB_ID"),
    filter={"property": "Template Name", "title": {"equals": "christmas_email_1"}}
)
print(response["results"])  # Should return 1 page
```

---

## References

- **Main Project README**: `/README.md`
- **Deployment Guide**: `/DEPLOYMENT.md`
- **BusOS Campaign**: `/campaigns/businessx_canada_lead_nurture/README.md`
- **Email Templates Config**: `config/email_templates_christmas.py`
- **Upload Script**: `scripts/seed_email_templates.py`
- **Notion Operations**: `tasks/notion_operations.py`

---

## Support

**Questions?** Check the main project documentation or contact the development team.

**Last Updated**: 2025-11-18
**Status**: ✅ Templates uploaded and tested
