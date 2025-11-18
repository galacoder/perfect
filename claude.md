# Claude Code Project Guide

**Project**: Perfect - BusOS Email Sequence (Prefect Migration)
**Last Updated**: November 16, 2025
**Structure**: Campaign-Based Organization

---

## Project Overview

This is an automated email nurture sequence system built with Prefect v3, replacing an original n8n workflow. The system sends a 5-email sequence to contacts who complete the BusOS assessment, with intelligent segment-based routing (CRITICAL/URGENT/OPTIMIZE).

**Tech Stack**:
- **Orchestration**: Prefect v3
- **API Server**: FastAPI
- **Database**: Notion (Contacts + Templates)
- **Email**: Resend API
- **Notifications**: Discord (hot leads)
- **Testing**: pytest (93 unit tests)

---

## Campaign-Based Structure

### Why Campaign-Based?

The project migrated from a flat structure to a campaign-based organization (Nov 14, 2025):

**Old Structure** (Deprecated):
```
/flows/signup_handler.py
/tasks/notion_operations.py
```

**New Structure** (Current):
```
/campaigns/businessx_canada_lead_nurture/
  ├── flows/signup_handler.py
  ├── tasks/notion_operations.py
  ├── tests/test_notion_operations.py
  ├── diagrams/CAMPAIGN_OVERVIEW.txt
  ├── README.md
  └── ARCHITECTURE.md
```

**Benefits**:
- ✅ Scalable: Add new campaigns without file conflicts
- ✅ Self-documenting: Each campaign has README, ARCHITECTURE, diagrams
- ✅ Team ownership: Clear responsibility per campaign
- ✅ Better testing: Campaign-specific test isolation

**Backward Compatibility**: Old imports still work via deprecation shims in `/flows/` and `/tasks/`, but use new paths for new code.

---

## Project Structure

```
perfect/
├── campaigns/                              # 🎯 Campaign-based organization
│   └── businessx_canada_lead_nurture/      # BusOS Lead Nurture Campaign
│       ├── README.md                       # Campaign overview
│       ├── ARCHITECTURE.md                 # Technical architecture
│       ├── flows/                          # 3 Prefect flows
│       │   ├── signup_handler.py           # Handle new signups
│       │   ├── assessment_handler.py       # Process assessments
│       │   └── email_sequence.py           # 5-email nurture sequence
│       ├── tasks/                          # 4 task modules
│       │   ├── notion_operations.py        # Notion CRUD (4 functions)
│       │   ├── resend_operations.py        # Email sending (3 functions)
│       │   ├── routing.py                  # Segment classification
│       │   └── template_operations.py      # Dynamic template fetching
│       ├── tests/                          # 93 unit tests
│       │   ├── test_notion_operations.py   # Notion task tests
│       │   ├── test_resend_operations.py   # Resend task tests
│       │   └── test_routing.py             # Routing logic tests
│       └── diagrams/                       # ASCII workflow diagrams
│           ├── CAMPAIGN_OVERVIEW.txt       # High-level architecture
│           ├── SIGNUP_HANDLER.txt          # Signup flow breakdown
│           ├── ASSESSMENT_HANDLER.txt      # Assessment flow + segment logic
│           └── EMAIL_SEQUENCE.txt          # Complete 5-email sequence
│
├── flows/                                  # ⚠️ Deprecated (backward compat shims)
├── tasks/                                  # ⚠️ Deprecated (backward compat shims)
├── tests/                                  # Legacy tests (mostly deprecated)
│
├── config/                                 # Configuration
│   └── email_templates.py                 # Static template fallbacks
│
├── scripts/                                # Utility scripts
│   └── seed_templates.py                  # Seed Notion email templates
│
├── server.py                               # 🚀 FastAPI webhook server (entry point)
├── test_flows_dry_run.py                   # Dry-run validation (no API calls)
├── test_integration_e2e.py                 # E2E integration tests
│
├── requirements.txt                        # Python dependencies
├── .env                                    # Environment variables (gitignored)
│
├── README.md                               # Main documentation
├── DEPLOYMENT.md                           # Deployment guide
├── MIGRATION_GUIDE.md                      # Campaign migration guide
├── COMPLETION_SUMMARY.md                   # Migration completion summary
└── VALIDATION_REPORT.md                    # Validation report
```

---

## Import Patterns

### ✅ Correct (Use This)

```python
# Campaign-based imports (recommended)
from campaigns.businessx_canada_lead_nurture.flows.signup_handler import signup_handler_flow
from campaigns.businessx_canada_lead_nurture.flows.assessment_handler import assessment_handler_flow
from campaigns.businessx_canada_lead_nurture.flows.email_sequence import email_sequence_flow

from campaigns.businessx_canada_lead_nurture.tasks.notion_operations import (
    search_contact_by_email,
    create_contact,
    update_contact,
    fetch_template
)
from campaigns.businessx_canada_lead_nurture.tasks.resend_operations import send_email
from campaigns.businessx_canada_lead_nurture.tasks.routing import classify_segment
from campaigns.businessx_canada_lead_nurture.tasks.template_operations import render_template
```

### ⚠️ Deprecated (Still Works, But Avoid)

```python
# Old imports (deprecated, shows warnings)
from flows.signup_handler import signup_handler_flow
from tasks.notion_operations import create_contact
```

**When to use old imports**: Only for backward compatibility in existing code. For new code or refactoring, always use campaign-based imports.

---

## Architecture Overview

### Data Flow

```
Website Form
    │
    ├──► POST /webhook/signup ──► signup_handler_flow ──► Notion (Contact Created)
    │
    └──► POST /webhook/assessment ──► assessment_handler_flow ──┬──► Notion (Segment Updated)
                                                                 │
                                                                 ├──► Discord (if CRITICAL)
                                                                 │
                                                                 └──► email_sequence_flow ──► Resend API
                                                                         │
                                                                         └──► 5 emails over 7 days
```

### Key Components

**1. Entry Points** (`server.py`):
- `POST /webhook/signup` - Capture lead from website form
- `POST /webhook/assessment` - Process completed assessment
- `GET /health` - Health check endpoint

**2. Prefect Flows** (`campaigns/.../flows/`):
- `signup_handler_flow` - Create/update contact in Notion
- `assessment_handler_flow` - Classify segment, trigger email sequence
- `email_sequence_flow` - Send 5 emails with wait times

**3. Prefect Tasks** (`campaigns/.../tasks/`):
- `notion_operations.py` - Database CRUD (search, create, update, fetch)
- `resend_operations.py` - Email delivery
- `routing.py` - Segment classification logic
- `template_operations.py` - Dynamic template rendering

**4. Testing**:
- **Unit tests**: `campaigns/.../tests/` (93 tests)
- **Dry-run**: `test_flows_dry_run.py` (structure validation)
- **Integration**: `test_integration_e2e.py` (mock/real mode)

---

## Email Sequence Logic

### Segment Classification

Contacts are classified into 3 segments based on assessment results:

| Segment | Condition | Action |
|---------|-----------|--------|
| **CRITICAL** | `red_systems >= 2` | Discord alert + personalized emails |
| **URGENT** | `red_systems == 1` OR `orange_systems >= 2` | Personalized emails |
| **OPTIMIZE** | All others | Standard emails |

**Routing logic**: `campaigns/.../tasks/routing.py:classify_segment()`

### Email Sequence Timeline

**Production Mode** (`TESTING_MODE=false`):
1. Email 1 (universal) → Wait 24h
2. Email 2 (segment-specific: 2A/2B/2C) → Wait 48h
3. Email 3 (universal) → Wait 48h
4. Email 4 (universal) → Wait 48h
5. Email 5 (segment-specific: 5A/5B/5C) → Done

**Total duration**: 7 days

**Testing Mode** (`TESTING_MODE=true`):
- Wait times: 1min → 2min → 3min → 4min (~10 minutes total)

---

## Working with This Codebase

### When Editing Flows

**Location**: `campaigns/businessx_canada_lead_nurture/flows/`

**Key files**:
- `signup_handler.py` - Modify signup logic
- `assessment_handler.py` - Modify assessment processing
- `email_sequence.py` - Modify email sequence timing or content

**Testing after changes**:
```bash
# Dry-run (no API calls)
python test_flows_dry_run.py

# Integration test (mocked)
python test_integration_e2e.py --mode mock
```

### When Editing Tasks

**Location**: `campaigns/businessx_canada_lead_nurture/tasks/`

**Key files**:
- `notion_operations.py` - Notion API interactions
- `resend_operations.py` - Email sending logic
- `routing.py` - Segment classification rules
- `template_operations.py` - Template rendering

**Testing after changes**:
```bash
# Unit tests for specific module
pytest campaigns/businessx_canada_lead_nurture/tests/test_notion_operations.py -v

# All unit tests
pytest campaigns/businessx_canada_lead_nurture/tests/ -v
```

### When Adding New Features

1. **Create new task** in `campaigns/.../tasks/your_task.py`
2. **Write unit tests** in `campaigns/.../tests/test_your_task.py`
3. **Use task in flow** by importing from campaign path
4. **Update diagrams** in `campaigns/.../diagrams/` (ASCII format)
5. **Document in README** at `campaigns/.../README.md`

### When Adding New Campaigns

```bash
# Create campaign structure
mkdir -p campaigns/your_new_campaign/{flows,tasks,tests,diagrams}

# Create documentation
touch campaigns/your_new_campaign/{README.md,ARCHITECTURE.md}

# Copy and adapt from existing campaign
cp campaigns/businessx_canada_lead_nurture/flows/signup_handler.py \
   campaigns/your_new_campaign/flows/your_flow.py
```

**Import pattern**:
```python
from campaigns.your_new_campaign.flows.your_flow import your_flow
from campaigns.your_new_campaign.tasks.your_task import your_task
```

---

## Testing Strategy

### Test Hierarchy

1. **Unit Tests** (Fast, Isolated):
   - Location: `campaigns/.../tests/`
   - Coverage: 93 tests across 3 modules
   - Run: `pytest campaigns/businessx_canada_lead_nurture/tests/ -v`

2. **Dry-Run Tests** (Structure Validation):
   - Location: `test_flows_dry_run.py`
   - Purpose: Validate flow structure without API calls
   - Run: `python test_flows_dry_run.py`

3. **Integration Tests** (E2E):
   - Location: `test_integration_e2e.py`
   - Modes: `mock` (safe) or `real` (creates records)
   - Run: `python test_integration_e2e.py --mode mock`

### Test Before Commit

```bash
# Quick validation (30 seconds)
python test_flows_dry_run.py

# Full unit tests (1-2 minutes)
pytest campaigns/businessx_canada_lead_nurture/tests/ -v

# Integration test (2-3 minutes)
python test_integration_e2e.py --mode mock
```

---

## Environment Variables

### Required

```bash
NOTION_TOKEN=ntn_xxxxx                  # Notion integration token
NOTION_CONTACTS_DB_ID=xxxxx             # Contacts database ID
NOTION_TEMPLATES_DB_ID=xxxxx            # Email templates database ID
RESEND_API_KEY=re_xxxxx                 # Resend API key
```

### Optional

```bash
TESTING_MODE=false                      # true = fast waits (minutes), false = prod waits (days)
DISCORD_WEBHOOK_URL=https://...         # Discord webhook for CRITICAL segment alerts
API_HOST=0.0.0.0                        # FastAPI server host
API_PORT=8000                           # FastAPI server port
```

**Configuration location**: `.env` file (gitignored)

---

## Common Tasks

### Run Webhook Server

```bash
# Development (auto-reload)
uvicorn server:app --reload

# Production
uvicorn server:app --host 0.0.0.0 --port 8000 --workers 4
```

### Test Webhooks

```bash
# Health check
curl http://localhost:8000/health

# Signup
curl -X POST http://localhost:8000/webhook/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","name":"Test User","business_name":"Test Corp"}'

# Assessment
curl -X POST http://localhost:8000/webhook/assessment \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","red_systems":2,"orange_systems":1}'
```

### Seed Email Templates

```bash
python scripts/seed_templates.py
```

This creates 8 email templates in Notion:
- `email_1` (universal)
- `email_2a_critical`, `email_2b_urgent`, `email_2c_optimize`
- `email_3` (universal)
- `email_4` (universal)
- `email_5a_critical`, `email_5b_urgent`, `email_5c_optimize`

### Run Full Test Suite

```bash
# All validation steps
python test_flows_dry_run.py && \
python test_integration_e2e.py --mode mock && \
pytest campaigns/businessx_canada_lead_nurture/tests/ -v
```

---

## Deployment

### Local Development

```bash
# Set testing mode for fast sequences
export TESTING_MODE=true

# Start server
uvicorn server:app --reload
```

### Production Deployment

See **[DEPLOYMENT.md](DEPLOYMENT.md)** for complete guide.

**Options**:
- **Server**: Direct `uvicorn` with systemd/supervisor
- **Docker**: `docker-compose up -d`
- **Prefect Cloud**: Deploy flows with `python flows/deploy.py`

---

## Error Handling

### Retry Strategy

- **Notion API**: 3 retries, 60s delay
- **Resend API**: 3 retries, 30s delay
- **Discord webhook**: 2 retries, 30s delay

### Fallback Behavior

- **Template fetch fails**: Use static templates from `config/email_templates.py`
- **Email send fails**: Retry 3×, then log for manual follow-up
- **Discord fails**: Log but don't block email sequence
- **Contact not found**: Return 404 error (assessment requires existing contact)

---

## Documentation Structure

### Project-Level Docs (Root)

- `README.md` - Main documentation (getting started, architecture)
- `DEPLOYMENT.md` - Deployment guide (server, Docker, Prefect Cloud)
- `MIGRATION_GUIDE.md` - Campaign migration details
- `claude.md` - This file (AI assistant guide)

### Campaign-Level Docs

- `campaigns/.../README.md` - Campaign overview and quick start
- `campaigns/.../ARCHITECTURE.md` - Technical architecture and data flow
- `campaigns/.../diagrams/` - ASCII workflow diagrams

**When to read what**:
- **Getting started**: Root `README.md`
- **Understanding flows**: Campaign `ARCHITECTURE.md` + `diagrams/`
- **Deploying**: `DEPLOYMENT.md`
- **Migrating old code**: `MIGRATION_GUIDE.md`

---

## Key Design Decisions

### Why Prefect v3?

- ✅ Version control (Git)
- ✅ Type-safe (Pydantic)
- ✅ Testable (unit + integration tests)
- ✅ Dynamic templates (Notion)
- ✅ Better observability than n8n

### Why Notion for Templates?

- ✅ Non-technical team can edit emails
- ✅ No code deployment for content changes
- ✅ Version history built-in
- ✅ Structured data (database)

### Why Campaign-Based Structure?

- ✅ Scalability (add campaigns without conflicts)
- ✅ Self-documenting (README per campaign)
- ✅ Team ownership (clear responsibility)
- ✅ Better testing (isolated test suites)

### Why ASCII Diagrams?

- ✅ No external dependencies
- ✅ Easy to version control
- ✅ Viewable in any editor
- ✅ Accessible (no special software)

---

## Migration Status

**Date**: November 14, 2025
**Status**: ✅ Complete
**Breaking Changes**: ❌ None (backward compatibility maintained)

**What changed**:
- Moved flows/tasks to `campaigns/businessx_canada_lead_nurture/`
- Created deprecation shims in old locations
- Updated all project references to new paths
- Added campaign-specific documentation and diagrams

**What still works**:
- Old imports (with deprecation warnings)
- Existing test suite
- All deployment configurations

See **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** for full details.

---

## Quick Reference

### File Locations

| Component | Location |
|-----------|----------|
| **Flows** | `campaigns/businessx_canada_lead_nurture/flows/` |
| **Tasks** | `campaigns/businessx_canada_lead_nurture/tasks/` |
| **Tests** | `campaigns/businessx_canada_lead_nurture/tests/` |
| **Diagrams** | `campaigns/businessx_canada_lead_nurture/diagrams/` |
| **Server** | `server.py` (root) |
| **Config** | `config/email_templates.py` |
| **Scripts** | `scripts/seed_templates.py` |

### Common Commands

```bash
# Development
uvicorn server:app --reload                           # Start server
python test_flows_dry_run.py                          # Quick validation
python test_integration_e2e.py --mode mock            # Integration test

# Testing
pytest campaigns/businessx_canada_lead_nurture/tests/ -v  # Unit tests
pytest campaigns/.../tests/test_routing.py -v         # Specific module

# Deployment
python flows/deploy.py                                # Deploy to Prefect Cloud
docker-compose up -d                                  # Docker deployment
```

### Test Data

```json
// Signup payload
{
  "email": "test@example.com",
  "name": "Test User",
  "first_name": "Test",
  "business_name": "Test Corp"
}

// Assessment payload (CRITICAL segment)
{
  "email": "test@example.com",
  "red_systems": 2,
  "orange_systems": 1
}
```

---

## Support

**Issues**: GitHub Issues
**Email**: sang@sanglescalinglabs.com
**Documentation**: See root `README.md` and `DEPLOYMENT.md`

---

## License

Proprietary - Sang Le Scaling Labs

---

**Last Updated**: November 16, 2025
**Project Version**: Campaign-Based Structure (Post-Migration)
