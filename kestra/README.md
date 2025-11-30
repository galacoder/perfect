# Kestra Flows - Christmas Campaign

This directory contains all Kestra flow definitions for the Christmas Campaign automation.

## Directory Structure

```
kestra/
├── flows/
│   └── christmas/
│       ├── handlers/
│       │   ├── signup-handler.yml          # Handle new signups (tracking only, no emails)
│       │   ├── assessment-handler.yml      # Process assessments and trigger Emails #2-5
│       │   ├── noshow-recovery-handler.yml # 3-email recovery sequence
│       │   ├── postcall-maybe-handler.yml  # 3-email follow-up sequence
│       │   └── onboarding-handler.yml      # 3-email welcome sequence
│       ├── send-email.yml                  # Reusable email sending flow
│       └── health-check.yml                # Health check flow (verify Kestra is running)
└── README.md                               # This file
```

## Flow Descriptions

### Health Check Flow
**File**: `health-check.yml`
**Purpose**: Verify Kestra is running and can access secrets
**Trigger**: Manual (for testing)

### Handler Flows

#### 1. Signup Handler
**File**: `handlers/signup-handler.yml`
**Purpose**: Track new customer signups (NO EMAIL SENDING)
**Trigger**: Webhook from website
**Actions**:
- Parse signup data
- Create/update contact in Notion
- Log signup event

**IMPORTANT**: Website handles signup confirmation email directly. Kestra only tracks the signup.

#### 2. Assessment Handler
**File**: `handlers/assessment-handler.yml`
**Purpose**: Process completed assessments and trigger 5-day email sequence
**Trigger**: Webhook from website (includes `email_1_sent_at` timestamp)
**Actions**:
- Parse assessment data
- Classify segment (CRITICAL/URGENT/OPTIMIZE)
- Update Notion sequence tracker (mark Email #1 as 'sent_by_website')
- Schedule Emails #2-5 with delays relative to `email_1_sent_at`

**Email Responsibility Split**:
- Website sends: Email #1 immediately after assessment
- Kestra sends: Emails #2-5 (at +24h, +72h, +96h, +120h from Email #1)

#### 3. No-Show Recovery Handler
**File**: `handlers/noshow-recovery-handler.yml`
**Purpose**: 3-email recovery sequence for Calendly no-shows
**Trigger**: Webhook from Calendly
**Actions**:
- Parse no-show event
- Schedule 3-email recovery sequence

**Email Responsibility**: Kestra handles ALL 3 emails

#### 4. Post-Call Maybe Handler
**File**: `handlers/postcall-maybe-handler.yml`
**Purpose**: 3-email follow-up sequence for "maybe" leads
**Trigger**: Manual or webhook
**Actions**:
- Parse lead data
- Schedule 3-email follow-up sequence

**Email Responsibility**: Kestra handles ALL 3 emails

#### 5. Onboarding Handler
**File**: `handlers/onboarding-handler.yml`
**Purpose**: 3-email welcome sequence for new customers
**Trigger**: Webhook on payment confirmation
**Actions**:
- Validate payment
- Schedule 3-email onboarding sequence

**Email Responsibility**: Kestra handles ALL 3 emails

### Reusable Flows

#### Send Email Flow
**File**: `send-email.yml`
**Purpose**: Reusable flow for sending individual emails
**Called by**: All handler flows
**Actions**:
1. Check idempotency (skip if already sent)
2. Fetch template from Notion
3. Render template with personalization variables
4. Send via Resend API
5. Update Notion Sequence Tracker with delivery status

## Email Responsibility Matrix

| Sequence Type | Email #1 | Email #2 | Email #3 | Email #4 | Email #5 |
|---------------|----------|----------|----------|----------|----------|
| **5-Day Nurture** | Website | Kestra | Kestra | Kestra | Kestra |
| **No-Show Recovery** | Kestra | Kestra | Kestra | - | - |
| **Post-Call Maybe** | Kestra | Kestra | Kestra | - | - |
| **Onboarding** | Kestra | Kestra | Kestra | - | - |

## Secret Configuration

All flows use secrets from `.env.kestra` file (loaded via Docker Compose):

- `SECRET_NOTION_TOKEN` - Notion API token
- `SECRET_NOTION_CONTACTS_DB_ID` - Contacts database ID
- `SECRET_NOTION_TEMPLATES_DB_ID` - Email templates database ID
- `SECRET_NOTION_EMAIL_SEQUENCE_DB_ID` - Email sequence tracker database ID
- `SECRET_RESEND_API_KEY` - Resend API key
- `SECRET_DISCORD_WEBHOOK_URL` - Discord webhook for CRITICAL alerts (optional)
- `TESTING_MODE` - true = fast delays (minutes), false = production delays (days)

## Webhook Endpoints

Once deployed, Kestra will expose these webhook URLs:

- `/api/v1/executions/webhook/christmas/signup-handler` - Signup tracking
- `/api/v1/executions/webhook/christmas/assessment-handler` - Assessment processing
- `/api/v1/executions/webhook/christmas/noshow-recovery-handler` - No-show recovery
- `/api/v1/executions/webhook/christmas/postcall-maybe-handler` - Post-call follow-up
- `/api/v1/executions/webhook/christmas/onboarding-handler` - Onboarding welcome

## Testing

Run the health check flow to verify Kestra setup:

```bash
# Start Kestra with Docker Compose
docker-compose -f docker-compose.kestra.yml up -d

# Access Kestra UI
open http://localhost:8080

# Trigger health check flow manually
# Navigate to: Flows → christmas → health-check → Execute
```

## Migration Status

**Current**: Wave 1 (Foundation) complete
- Docker Compose setup
- Secret configuration
- Health check flow
- Directory structure

**Next**: Wave 2 (Core Flow Migration)
- Port routing logic
- Create Notion/Resend HTTP tasks
- Implement send-email flow
- Add email scheduling mechanism

## Documentation

- **Migration Guide**: See `/KESTRA_MIGRATION.md` (to be created in Wave 4)
- **Architecture**: See `campaigns/christmas_campaign/ARCHITECTURE.md`
- **Website Integration**: See `campaigns/christmas_campaign/WEBSITE_INTEGRATION.md`

---

**Last Updated**: 2025-11-29
**Wave Status**: Wave 1 (Foundation) - Complete
