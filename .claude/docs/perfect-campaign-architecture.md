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
│   ├── businessx_canada_lead_nurture/      # BusOS Lead Nurture Campaign
│   │   ├── README.md                       # Campaign overview
│   │   ├── ARCHITECTURE.md                 # Technical architecture
│   │   ├── flows/                          # 3 Prefect flows
│   │   │   ├── signup_handler.py           # Handle new signups
│   │   │   ├── assessment_handler.py       # Process assessments
│   │   │   └── email_sequence.py           # 5-email nurture sequence
│   │   ├── tasks/                          # 4 task modules
│   │   │   ├── notion_operations.py        # Notion CRUD (4 functions)
│   │   │   ├── resend_operations.py        # Email sending (3 functions)
│   │   │   ├── routing.py                  # Segment classification
│   │   │   └── template_operations.py      # Dynamic template fetching
│   │   ├── tests/                          # 93 unit tests
│   │   │   ├── test_notion_operations.py   # Notion task tests
│   │   │   ├── test_resend_operations.py   # Resend task tests
│   │   │   └── test_routing.py             # Routing logic tests
│   │   └── diagrams/                       # ASCII workflow diagrams
│   │       ├── CAMPAIGN_OVERVIEW.txt       # High-level architecture
│   │       ├── SIGNUP_HANDLER.txt          # Signup flow breakdown
│   │       ├── ASSESSMENT_HANDLER.txt      # Assessment flow + segment logic
│   │       └── EMAIL_SEQUENCE.txt          # Complete 5-email sequence
│   │
│   └── christmas_campaign/                 # Christmas 2025 Campaign
│       ├── README.md                       # Campaign overview
│       ├── ARCHITECTURE.md                 # Technical architecture
│       ├── STATUS.md                       # ⭐ Deployment status tracking
│       ├── WEBSITE_INTEGRATION.md          # API integration guide
│       ├── WORKER_SETUP.md                 # Worker environment setup (deprecated)
│       ├── flows/
│       │   ├── signup_handler.py           # Handle assessment completions
│       │   └── send_email.py               # Send individual emails (7 total)
│       ├── tasks/
│       │   ├── notion_operations.py        # Notion database operations
│       │   └── resend_operations.py        # Email sending operations
│       └── diagrams/
│           └── CAMPAIGN_OVERVIEW.txt       # Campaign architecture
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

