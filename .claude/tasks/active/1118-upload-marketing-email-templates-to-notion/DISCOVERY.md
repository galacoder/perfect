# Discovery: Upload Marketing Email Templates to Notion

## Requirements Understanding

- **Core Functionality**: Create a Python script to upload 7 email templates from marketing team's handoff document to the Notion Email Templates database
- **User Stories**:
  - Marketing team has created 7 complete email templates for the Christmas Campaign
  - Automation developer needs these templates in Notion to be dynamically fetched by Prefect flows
  - Templates must be easily editable by marketing team in Notion (no code deployment needed for content changes)
- **Acceptance Criteria**:
  - All 7 email templates uploaded to NOTION_EMAIL_TEMPLATES_DB_ID
  - Each template includes: template_id, subject line, HTML body
  - Templates match the marketing team's specifications from handoff document
  - Script can be run multiple times (idempotent - updates existing templates)
  - Script provides clear output showing success/failure
- **Constraints**:
  - Must use existing Notion database structure (NOTION_EMAIL_TEMPLATES_DB_ID)
  - Must preserve marketing copy exactly as provided
  - Must convert markdown format to HTML for email sending
  - Must be reusable for future template updates

## Codebase Analysis

### Technology Stack

- **Framework**: Prefect v3 (workflow orchestration)
- **Language**: Python 3.x
- **Runtime**: Python 3.x with Prefect
- **Database**: Notion (via notion-client Python SDK)
- **Email**: Resend API (for email delivery)
- **Testing**: pytest (existing test suite)

### Relevant Files

**Primary files to modify**:
- Create NEW: `campaigns/christmas_campaign/scripts/seed_email_templates.py` (main upload script)
- Create NEW: `campaigns/christmas_campaign/config/email_templates_christmas.py` (template data extracted from marketing docs)

**Reference files**:
- `campaigns/christmas_campaign/tasks/notion_operations.py` - Existing Notion operations (fetch_email_template function at line 279)
- `scripts/seed_templates.py` - Existing template seeding script for businessx_canada_lead_nurture campaign
- `campaigns/businessx_canada_lead_nurture/tasks/template_operations.py` - Template operations reference
- `/Users/sangle/Dev/action/projects/@agents/businessX/docs/money-model/model-16-christmas-traditional-service-2997/implementation/HANDOFF-AUTOMATION-DEVELOPER.md` - Source document with email specifications
- `/Users/sangle/Dev/action/projects/@agents/businessX/docs/money-model/model-16-christmas-traditional-service-2997/messaging/email-sequences/lead-nurture-7-days.md` - Complete email copy (1,872 lines)

**Test files**:
- Create NEW: `campaigns/christmas_campaign/tests/test_seed_email_templates.py` (unit tests for upload script)

**Configuration files**:
- `.env` - Contains NOTION_TOKEN and NOTION_EMAIL_TEMPLATES_DB_ID
  - NOTION_TOKEN=secret_eXSRJe3C3J2CAgE4AjG25HzplCiXVIIxFwO2AsQVysM
  - NOTION_EMAIL_TEMPLATES_DB_ID=2ab7c374-1115-8115-932c-ca6789c5b87b

### Dependencies

**External packages** (already installed):
- `notion-client` - Notion API SDK
- `python-dotenv` - Environment variable loading
- `prefect` - Workflow orchestration (though not strictly needed for seeding script)

**Internal modules**:
- `campaigns.christmas_campaign.tasks.notion_operations` - Notion client and database operations

**Breaking changes**: None - this is net-new functionality

### Code Patterns to Reuse

**Similar features**:
- `scripts/seed_templates.py` - Existing template seeding pattern for businessx_canada_lead_nurture
- `campaigns/businessx_canada_lead_nurture/tasks/template_operations.py` - Template structure and seeding logic
- `campaigns/christmas_campaign/tasks/notion_operations.py` - fetch_email_template() shows expected Notion database schema

**Code to reuse**:
```python
# Pattern from existing seed_templates.py
from notion_client import Client
from dotenv import load_dotenv

# Initialize Notion client
notion = Client(auth=NOTION_TOKEN)

# Query database to check if template exists
response = notion.databases.query(
    database_id=NOTION_EMAIL_TEMPLATES_DB_ID,
    filter={
        "property": "template_id",
        "rich_text": {"equals": template_id}
    }
)

# Create or update template
if response["results"]:
    # Update existing
    notion.pages.update(page_id=page_id, properties=...)
else:
    # Create new
    notion.pages.create(parent={"database_id": db_id}, properties=...)
```

**Anti-patterns to avoid**:
- DON'T hardcode template content in Python code (extract to config file)
- DON'T use @task decorator for seeding script (it's a standalone utility, not a Prefect flow)
- DON'T fail silently - provide clear success/failure messages

### Architecture Understanding

**Data Flow**:
```
Marketing Team (Markdown Docs)
    ↓
Python Script (Extract + Convert)
    ↓
Notion API (Upload Templates)
    ↓
Notion Email Templates Database (Storage)
    ↓
Prefect Flows (fetch_email_template)
    ↓
Resend API (Send Emails)
```

**Module Organization**:
- `/campaigns/christmas_campaign/` - Campaign-specific code
  - `/scripts/` - Utility scripts (seed templates, test data, etc.)
  - `/config/` - Configuration data (template content)
  - `/tasks/` - Prefect tasks (notion_operations, resend_operations, etc.)
  - `/tests/` - Unit tests

**Integration Points**:
- Notion API: Create/update pages in Email Templates database
- Environment variables: NOTION_TOKEN, NOTION_EMAIL_TEMPLATES_DB_ID
- Marketing handoff: Source of truth for email content

**API Contracts**:
```python
# Notion Email Templates Database Schema
{
    "template_id": "rich_text",  # e.g., "christmas_email_1"
    "subject": "title",  # Email subject line
    "html_body": "rich_text",  # HTML email body
    "campaign": "select",  # "Christmas Campaign"
    "email_number": "number",  # 1-7
    "segment": "multi_select",  # ["universal", "critical", "urgent", "optimize"]
    "active": "checkbox",  # true/false
    "last_modified": "last_edited_time"  # Auto-updated by Notion
}
```

### Potential Conflicts

**Breaking Changes**: None identified - net-new functionality

**API Changes**: None - using existing Notion API

**Database Migrations**: None required - Notion database already exists with correct schema

**Deprecations**: None

## Technical Constraints

- **Performance Requirements**:
  - Upload script should complete in <30 seconds for 7 templates
  - Each template upload should be <5 seconds
- **Browser/Device Support**: N/A (server-side script)
- **Security Considerations**:
  - NOTION_TOKEN must remain in .env file (never commit to git)
  - Validate template_id format to prevent injection
  - Sanitize markdown → HTML conversion
- **Scalability**: Script should handle 10-20 templates easily
- **Maintainability**:
  - Marketing team should be able to update templates directly in Notion
  - Script should be reusable for future campaigns

## Risk Assessment

### High Risk Areas

- **Markdown to HTML conversion**: Marketing provided markdown format, but emails need HTML
  - **Mitigation**: Use simple markdown-to-HTML library or manual conversion for 7 templates
  - **Testing**: Render each email template in email client preview

- **Template variable placeholders**: Templates use `{{variable}}` syntax, must preserve exactly
  - **Mitigation**: Don't process/escape template variables during upload
  - **Testing**: Verify variables like `{{first_name}}`, `{{assessment_score}}` remain intact

- **Notion database schema mismatch**: If database properties don't match expected schema
  - **Mitigation**: Query database schema first, validate before upload
  - **Testing**: Test upload to Notion staging database first

### Medium Risk Areas

- **Idempotency**: Script may be run multiple times
  - **Mitigation**: Check if template exists (by template_id), update instead of create
  - **Testing**: Run script twice, verify no duplicates

- **Long text fields**: HTML email bodies may exceed Notion's rich_text limits
  - **Mitigation**: Check Notion rich_text limit (2000 chars per block, use multiple blocks if needed)
  - **Testing**: Upload longest email template (Email 5 is longest)

### Low Risk Areas

- **Network failures**: Notion API may be temporarily unavailable
  - **Mitigation**: Add retry logic (3 retries, 5s delay)
  - **Acceptance**: Inform user if upload fails after retries

## Testing Strategy

### Unit Tests

- **Test template data extraction**: Verify 7 templates extracted correctly from config
- **Test template_id generation**: Verify naming convention (christmas_email_1, christmas_email_2a_critical, etc.)
- **Test Notion API calls**: Mock Notion client, verify correct properties sent
- **Test idempotency**: Verify update logic when template already exists

### Integration Tests

- **Test full upload flow**: Upload all 7 templates to Notion (real API)
- **Test template retrieval**: Verify fetch_email_template() can retrieve uploaded templates
- **Test variable preservation**: Verify {{placeholders}} remain intact after upload

### E2E Tests

- **Test email rendering**: Fetch template from Notion → Render with test data → Verify HTML output
- **Test template editing in Notion**: Manually edit template in Notion → Verify changes fetched correctly

### Manual Testing

- **Visual inspection**: Open each template in Notion, verify formatting
- **Email preview**: Send test email with each template → Verify rendering in Gmail/Outlook
- **Variable substitution**: Verify template variables work with actual contact data

### Regression Tests

- **Existing email sequence**: Verify businessx_canada_lead_nurture campaign still works
- **Notion operations**: Verify other Notion operations (search_contact, update_assessment) unaffected

## Development Environment

### Setup Required

```bash
# Already installed (from existing project)
pip install notion-client python-dotenv

# Environment variables (already in .env)
NOTION_TOKEN=secret_eXSRJe3C3J2CAgE4AjG25HzplCiXVIIxFwO2AsQVysM
NOTION_EMAIL_TEMPLATES_DB_ID=2ab7c374-1115-8115-932c-ca6789c5b87b
```

### Run Command

```bash
# Development (test upload)
python campaigns/christmas_campaign/scripts/seed_email_templates.py

# Production (actual upload)
python campaigns/christmas_campaign/scripts/seed_email_templates.py --production
```

### Test Command

```bash
# Unit tests
pytest campaigns/christmas_campaign/tests/test_seed_email_templates.py -v

# Integration test (with real Notion API)
pytest campaigns/christmas_campaign/tests/test_seed_email_templates.py --integration -v
```

### Build Command

N/A (Python script, no build step)

## Key Decisions Made

### Email Template Structure

**Decision**: Extract 7 email templates from marketing handoff document

**Templates to create**:
1. `christmas_email_1` - Assessment Results (Day 0, immediate, universal)
2. `christmas_email_2a_critical` - System Fix Framework (Day 1, CRITICAL segment)
3. `christmas_email_2b_urgent` - System Fix Framework (Day 1, URGENT segment)
4. `christmas_email_2c_optimize` - System Fix Framework (Day 1, OPTIMIZE segment)
5. `christmas_email_3` - Horror Story (Day 2, universal)
6. `christmas_email_4` - Diagnostic Booking Ask (Day 3, universal)
7. `christmas_email_5` - Case Study (Day 5, universal)

NOTE: Marketing handoff mentions 7 emails, but lead-nurture-7-days.md is still being updated. We'll extract the actual email copy from the HANDOFF document's code examples.

### Markdown to HTML Conversion

**Decision**: Use `markdown` library for conversion

**Rationale**:
- Marketing provided content in markdown format
- Emails need HTML for proper rendering
- Simple library, already commonly used

**Alternative considered**: Manual HTML templates
- **Rejected**: Too time-consuming to manually convert 7 emails

### Template Variable Format

**Decision**: Preserve `{{variable}}` syntax exactly as provided

**Rationale**:
- Matches existing template_operations.py render logic
- Marketing team used this format in handoff
- Compatible with Jinja2-style templating

### Idempotency Strategy

**Decision**: Query by template_id first, update if exists, create if not

**Rationale**:
- Allows re-running script without duplicates
- Enables template updates by marketing team
- Notion query filter is efficient

### Script Location

**Decision**: `campaigns/christmas_campaign/scripts/seed_email_templates.py`

**Rationale**:
- Campaign-specific utility (not shared across campaigns)
- Follows project structure convention
- Parallel to existing `scripts/seed_templates.py`

