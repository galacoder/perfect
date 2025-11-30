# Christmas Campaign - Prefect to Kestra Migration Guide

**Migration Date**: November 2025
**Status**: Migration Complete
**Migrated By**: Task 1129-port-prefect-to-kestra

---

## Table of Contents

1. [Why Migrate to Kestra](#why-migrate-to-kestra)
2. [Migration Overview](#migration-overview)
3. [Architecture Changes](#architecture-changes)
4. [Email Responsibility Split](#email-responsibility-split)
5. [Component Mapping](#component-mapping)
6. [Migration Patterns](#migration-patterns)
7. [Secret Management](#secret-management)
8. [Testing Strategy](#testing-strategy)
9. [Rollback Plan](#rollback-plan)
10. [Troubleshooting](#troubleshooting)

---

## Why Migrate to Kestra

### Prefect Limitations

1. **Complexity**: Prefect v3.4.1 required Python code for flow orchestration
2. **Deployment**: Git-based deployments with Prefect Cloud/Server dependency
3. **Secret Management**: Prefect Secret blocks required API calls to retrieve
4. **Debugging**: Flow debugging required Python environment + Prefect CLI
5. **Team Accessibility**: Only Python developers could modify flows

### Kestra Advantages

1. **YAML-First**: Declarative workflows easy to read and maintain
2. **Self-Hosted**: Single Docker Compose deployment, no external dependencies
3. **UI-Driven**: Full flow editing, execution, and monitoring in web UI
4. **Built-in Tasks**: HTTP, Notion, Resend integrations without custom code
5. **Secret Management**: Environment variable-based secrets (simpler)
6. **No Code Skills**: Non-technical team members can edit flows
7. **Better Observability**: Real-time flow execution graphs in UI

---

## Migration Overview

### What Was Migrated

| Component | Prefect | Kestra | Status |
|-----------|---------|--------|--------|
| **Signup Handler** | `signup_handler.py` | `signup-handler.yml` | ✅ Complete |
| **Assessment Handler** | `assessment_handler.py` | `assessment-handler.yml` | ✅ Complete |
| **No-Show Recovery** | `noshow_recovery_handler.py` | `noshow-recovery-handler.yml` | ✅ Complete |
| **Post-Call Maybe** | `postcall_maybe_handler.py` | `postcall-maybe-handler.yml` | ✅ Complete |
| **Onboarding** | `onboarding_handler.py` | `onboarding-handler.yml` | ✅ Complete |
| **Send Email Flow** | Embedded in handlers | `send-email.yml` (reusable) | ✅ Complete |
| **Routing Logic** | `tasks/routing.py` | `lib/routing.py` | ✅ Complete |
| **Notion Tasks** | `tasks/notion_operations.py` | `tasks/notion_*.yml` | ✅ Complete |
| **Resend Tasks** | `tasks/resend_operations.py` | `tasks/resend_send_email.yml` | ✅ Complete |
| **Template Fetching** | `tasks/template_operations.py` | `lib/fetch_template.py` | ✅ Complete |
| **Webhook Server** | FastAPI (`server.py`) | Kestra webhooks (native) | 🟡 Optional |
| **Secret Blocks** | Prefect Secret API | Docker Compose `.env.kestra` | ✅ Complete |

### What Changed

**CRITICAL ARCHITECTURAL CHANGE: Email Responsibility Split**

| Sequence | Email # | Prefect Behavior | Kestra Behavior |
|----------|---------|-----------------|----------------|
| **Signup** | - | Sent signup email | **NO EMAIL** (website sends) |
| **5-Day Sequence** | Email #1 | Sent by Prefect | **Sent by WEBSITE** |
| **5-Day Sequence** | Emails #2-5 | Sent by Prefect | **Sent by KESTRA** |
| **No-Show Recovery** | All 3 emails | Sent by Prefect | Sent by Kestra |
| **Post-Call Maybe** | All 3 emails | Sent by Prefect | Sent by Kestra |
| **Onboarding** | All 3 emails | Sent by Prefect | Sent by Kestra |

**Why This Change?**

- **Prevents duplicate emails**: Website sends Email #1 immediately after assessment
- **Better timing**: Email #1 synchronous with assessment completion (no race conditions)
- **Clear responsibility**: Website owns first touch, Kestra owns nurture sequence

---

## Architecture Changes

### Prefect Architecture (Old)

```
┌─────────────┐
│   Website   │
│   Form      │
└──────┬──────┘
       │ POST /webhook/christmas-signup
       │
┌──────▼──────────────────────────────────────────────────────────────┐
│                    FastAPI Webhook Server                           │
│  (server.py)                                                        │
│                                                                      │
│  1. Validate payload                                                │
│  2. Trigger Prefect deployment via API                              │
│  3. Return 200 OK                                                   │
└──────┬──────────────────────────────────────────────────────────────┘
       │ Prefect API call
       │
┌──────▼──────────────────────────────────────────────────────────────┐
│              Prefect Flow (Python Code)                             │
│                                                                      │
│  1. Load secrets from Prefect Secret blocks                         │
│  2. Search/create contact in Notion                                 │
│  3. Classify segment (CRITICAL/URGENT/OPTIMIZE)                     │
│  4. FOR EACH email in sequence:                                     │
│     a. Fetch template from Notion                                   │
│     b. Substitute variables                                         │
│     c. Send via Resend API                                          │
│     d. Update Notion sequence tracker                               │
│     e. Sleep (wait for next email)                                  │
└─────────────────────────────────────────────────────────────────────┘
```

### Kestra Architecture (New)

```
┌─────────────┐
│   Website   │
│   Form      │
└──────┬──────┘
       │ 1. Send Email #1 immediately (assessment results)
       │ 2. POST webhook to Kestra with email_1_sent_at timestamp
       │
       ├────────────────────────────────────────┐
       │                                        │
       │ Email #1 sent                          │ POST /api/v1/executions/webhook/...
       │ by WEBSITE                             │
       │                                        │
┌──────▼──────────────────────────────────┐    │
│      Website Email Service              │    │
│  (Resend API direct from Next.js)       │    │
│                                          │    │
│  send_template_email(                    │    │
│    template: "christmas_email_1",       │    │
│    variables: {assessment_data}         │    │
│  )                                       │    │
└──────────────────────────────────────────┘    │
                                                │
┌───────────────────────────────────────────────▼──────┐
│              Kestra Webhook Endpoint                 │
│  http://kestra:8080/api/v1/executions/webhook/...   │
│                                                       │
│  1. Parse webhook payload                            │
│  2. Extract email_1_sent_at timestamp                │
│  3. Trigger assessment-handler flow                  │
└───────────────────────────┬───────────────────────────┘
                            │
┌───────────────────────────▼───────────────────────────┐
│         Kestra Flow (YAML Declarative)                │
│  kestra/flows/christmas/handlers/assessment-handler   │
│                                                        │
│  1. Load secrets from environment variables           │
│  2. Search/update contact in Notion (HTTP task)       │
│  3. Classify segment (Python script task)             │
│  4. Record Email #1 as 'sent_by_website' in Notion    │
│  5. Schedule Emails #2-5 with delays from             │
│     email_1_sent_at:                                  │
│     - Email #2: email_1_sent_at + 24h                 │
│     - Email #3: email_1_sent_at + 72h                 │
│     - Email #4: email_1_sent_at + 96h                 │
│     - Email #5: email_1_sent_at + 120h                │
│                                                        │
│  FOR EACH scheduled email (#2-5):                     │
│    a. Wait until scheduled time                       │
│    b. Call send-email.yml subflow                     │
│    c. Fetch template from Notion (HTTP task)          │
│    d. Substitute variables (Python script)            │
│    e. Send via Resend API (HTTP task)                 │
│    f. Update Notion sequence tracker (HTTP task)      │
└───────────────────────────────────────────────────────┘
```

---

## Email Responsibility Split

### Email Responsibility Matrix

| Sequence | Email # | Sent By | Timing | email_1_sent_at Required? |
|----------|---------|---------|--------|--------------------------|
| **Signup** | - | **Website** | Immediate | N/A |
| **5-Day Assessment** | #1 | **Website** | Immediately after assessment | ✅ YES (website provides) |
| **5-Day Assessment** | #2 | **Kestra** | email_1_sent_at + 24h | ✅ YES (used for delay) |
| **5-Day Assessment** | #3 | **Kestra** | email_1_sent_at + 72h | ✅ YES (used for delay) |
| **5-Day Assessment** | #4 | **Kestra** | email_1_sent_at + 96h | ✅ YES (used for delay) |
| **5-Day Assessment** | #5 | **Kestra** | email_1_sent_at + 120h | ✅ YES (used for delay) |
| **No-Show Recovery** | All 3 | **Kestra** | Standard delays | ❌ NO |
| **Post-Call Maybe** | All 3 | **Kestra** | Standard delays | ❌ NO |
| **Onboarding** | All 3 | **Kestra** | Standard delays | ❌ NO |

### Critical Website Requirements

**For Assessment Handler**, website MUST:

1. **Send Email #1 immediately** after assessment completion
2. **Record timestamp** when Email #1 was sent
3. **Include email_1_sent_at** in webhook payload to Kestra (ISO 8601 format)
4. **Include email_1_status** = "sent" in webhook payload

**Example Webhook Payload from Website**:
```json
{
  "email": "customer@example.com",
  "first_name": "Sarah",
  "business_name": "Sarah's Salon",
  "red_systems": 2,
  "orange_systems": 1,
  "yellow_systems": 2,
  "green_systems": 3,
  "weakest_system_1": "GPS",
  "revenue_leak_total": 14700,
  "email_1_sent_at": "2025-12-01T10:30:00Z",    // CRITICAL!
  "email_1_status": "sent"                        // CRITICAL!
}
```

### What Kestra Does With email_1_sent_at

1. **Validates** timestamp format (ISO 8601)
2. **Records** Email #1 in Notion as `sent_by='website'`
3. **Calculates delays** for Emails #2-5 relative to this timestamp:
   - Email #2 scheduled at: `email_1_sent_at + 24 hours`
   - Email #3 scheduled at: `email_1_sent_at + 72 hours`
   - Email #4 scheduled at: `email_1_sent_at + 96 hours`
   - Email #5 scheduled at: `email_1_sent_at + 120 hours`

### Fallback Behavior

If `email_1_sent_at` is missing:
- Kestra logs **WARNING**
- Uses **webhook trigger time** as fallback
- Continues execution (doesn't fail)

---

## Component Mapping

### Flow Structure Comparison

#### Prefect Flow (signup_handler.py)
```python
from prefect import flow, task
from prefect.blocks.system import Secret

@task(retries=3)
async def search_contact_by_email(email: str):
    token = await Secret.load("notion-token").get()
    # ... Notion API call

@flow(name="christmas-signup-handler")
async def signup_handler_flow(email: str, first_name: str, ...):
    contact = await search_contact_by_email(email)
    if not contact:
        contact = await create_contact(email, first_name, ...)

    # Send lead nurture sequence
    for i in range(1, 6):
        template = await fetch_template(f"lead_nurture_email_{i}")
        await send_email(template, contact)
        await asyncio.sleep(get_delay(i))

    # Send christmas_email_1
    template = await fetch_template("christmas_email_1")
    await send_email(template, contact)
```

#### Kestra Flow (signup-handler.yml)
```yaml
id: christmas-signup-handler
namespace: christmas.handlers

inputs:
  - id: email
    type: STRING
    required: true
  - id: first_name
    type: STRING
    required: true

tasks:
  - id: search_contact
    type: io.kestra.plugin.core.http.Request
    uri: https://api.notion.com/v1/databases/{{ secret('SECRET_NOTION_CONTACTS_DB_ID') }}/query
    method: POST
    headers:
      Authorization: "Bearer {{ secret('SECRET_NOTION_TOKEN') }}"
      Notion-Version: "2022-06-28"
    body: |
      {
        "filter": {
          "property": "Email",
          "email": { "equals": "{{ inputs.email }}" }
        }
      }

  # NO EMAIL SENDING - Website handles signup email!
  - id: log_signup_event
    type: io.kestra.plugin.core.log.Log
    message: "Signup tracked for {{ inputs.email }}, website handles email"
```

### Task Comparison

#### Prefect Task (notion_operations.py)
```python
@task(retries=3, retry_delay_seconds=60)
async def search_contact_by_email(email: str) -> Optional[Dict]:
    notion_token = await Secret.load("notion-token").get()
    db_id = await Secret.load("notion-contacts-db-id").get()

    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }

    payload = {
        "filter": {
            "property": "Email",
            "email": {"equals": email}
        }
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://api.notion.com/v1/databases/{db_id}/query",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        data = response.json()
        return data["results"][0] if data["results"] else None
```

#### Kestra Task (notion_search_contact.yml)
```yaml
id: notion_search_contact
namespace: christmas.tasks

inputs:
  - id: email
    type: STRING
    required: true

tasks:
  - id: search
    type: io.kestra.plugin.core.http.Request
    uri: "https://api.notion.com/v1/databases/{{ secret('SECRET_NOTION_CONTACTS_DB_ID') }}/query"
    method: POST
    headers:
      Authorization: "Bearer {{ secret('SECRET_NOTION_TOKEN') }}"
      Notion-Version: "2022-06-28"
      Content-Type: "application/json"
    body: |
      {
        "filter": {
          "property": "Email",
          "email": { "equals": "{{ inputs.email }}" }
        }
      }

outputs:
  - id: contact_id
    type: STRING
    value: "{{ outputs.search.body.results[0].id }}"
```

**Key Differences**:
1. **No Python code** - Pure HTTP task
2. **Secrets from environment** - `{{ secret('SECRET_NAME') }}`
3. **Outputs** - Explicit output declaration
4. **No retry logic** - Kestra handles automatically

---

## Migration Patterns

### Pattern 1: Python Task → HTTP Task

**Prefect**:
```python
@task
async def send_email(to: str, subject: str, body: str):
    resend_key = await Secret.load("resend-api-key").get()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {resend_key}"},
            json={"from": "...", "to": to, "subject": subject, "html": body}
        )
        return response.json()
```

**Kestra**:
```yaml
- id: send_email
  type: io.kestra.plugin.core.http.Request
  uri: "https://api.resend.com/emails"
  method: POST
  headers:
    Authorization: "Bearer {{ secret('SECRET_RESEND_API_KEY') }}"
  body: |
    {
      "from": "BusinessX Canada <noreply@sangletech.com>",
      "to": "{{ inputs.email }}",
      "subject": "{{ inputs.subject }}",
      "html": "{{ inputs.body }}"
    }
```

### Pattern 2: Python Logic → Python Script Task

**Prefect**:
```python
from campaigns.christmas_campaign.tasks.routing import classify_segment

@task
def classify_segment(red_systems: int, orange_systems: int) -> str:
    if red_systems >= 2:
        return "CRITICAL"
    elif red_systems == 1 or orange_systems >= 2:
        return "URGENT"
    else:
        return "OPTIMIZE"
```

**Kestra**:
```yaml
- id: classify_segment
  type: io.kestra.plugin.scripts.python.Script
  script: |
    red_systems = {{ inputs.red_systems }}
    orange_systems = {{ inputs.orange_systems }}

    if red_systems >= 2:
        segment = "CRITICAL"
    elif red_systems == 1 or orange_systems >= 2:
        segment = "URGENT"
    else:
        segment = "OPTIMIZE"

    print(f"::{{outputs.segment={segment}}}::")
```

### Pattern 3: Sequential Tasks → Task List

**Prefect**:
```python
@flow
async def email_sequence_flow(contact_id: str):
    template = await fetch_template("email_1")
    result = await send_email(template, contact_id)
    await update_notion(contact_id, result)
```

**Kestra**:
```yaml
tasks:
  - id: fetch_template
    type: io.kestra.plugin.core.flow.Subflow
    namespace: christmas.tasks
    flowId: notion_fetch_template
    inputs:
      template_name: "email_1"

  - id: send_email
    type: io.kestra.plugin.core.flow.Subflow
    namespace: christmas.tasks
    flowId: resend_send_email
    inputs:
      template: "{{ outputs.fetch_template.body }}"
      email: "{{ inputs.email }}"

  - id: update_notion
    type: io.kestra.plugin.core.flow.Subflow
    namespace: christmas.tasks
    flowId: notion_update_sequence_tracker
    inputs:
      contact_id: "{{ inputs.contact_id }}"
      email_number: 1
      resend_id: "{{ outputs.send_email.id }}"
```

### Pattern 4: Delayed Execution → Scheduled Subflow

**Prefect**:
```python
import asyncio

@flow
async def email_sequence_flow(emails: List[str]):
    for i, email_id in enumerate(emails):
        await send_email(email_id)
        if i < len(emails) - 1:
            await asyncio.sleep(get_delay(i))  # Wait 24h
```

**Kestra**:
```yaml
tasks:
  - id: schedule_email_2
    type: io.kestra.plugin.core.flow.Subflow
    namespace: christmas
    flowId: send-email
    inputs:
      email: "{{ inputs.email }}"
      template_name: "christmas_email_2"
    wait: true
    scheduleDate: "{{ inputs.email_1_sent_at | dateAdd(1, 'DAYS') }}"

  - id: schedule_email_3
    type: io.kestra.plugin.core.flow.Subflow
    namespace: christmas
    flowId: send-email
    inputs:
      email: "{{ inputs.email }}"
      template_name: "christmas_email_3"
    wait: true
    scheduleDate: "{{ inputs.email_1_sent_at | dateAdd(3, 'DAYS') }}"
```

**Key Difference**: Kestra uses `scheduleDate` property on subflows, Prefect uses `asyncio.sleep()`

---

## Secret Management

### Prefect Secret Blocks (Old)

**Creating Secrets**:
```bash
PREFECT_API_URL=https://prefect.galatek.dev/api python3 -c "
from prefect.blocks.system import Secret
Secret(value='notion_token_value').save('notion-token', overwrite=True)
Secret(value='db_id_value').save('notion-contacts-db-id', overwrite=True)
"
```

**Accessing in Flow**:
```python
notion_token = await Secret.load("notion-token").get()
```

**Issues**:
- Requires API call to Prefect server
- Async await needed
- Prefect-specific syntax

### Kestra Secrets (New)

**Creating Secrets** (`.env.kestra` file):
```bash
# Notion credentials
SECRET_NOTION_TOKEN=<base64_encoded_value>
SECRET_NOTION_CONTACTS_DB_ID=<base64_encoded_value>
SECRET_NOTION_TEMPLATES_DB_ID=<base64_encoded_value>

# Resend credentials
SECRET_RESEND_API_KEY=<base64_encoded_value>

# Testing mode
SECRET_TESTING_MODE=false
```

**Accessing in Flow**:
```yaml
uri: "https://api.notion.com/v1/databases/{{ secret('SECRET_NOTION_CONTACTS_DB_ID') }}/query"
headers:
  Authorization: "Bearer {{ secret('SECRET_NOTION_TOKEN') }}"
```

**Benefits**:
- Standard environment variables
- No API calls needed
- Works in any tool (Docker Compose, kubectl, etc.)
- Base64 encoded for security

### Secret Migration Script

```bash
#!/bin/bash
# migrate_secrets.sh - Extract from Prefect, encode for Kestra

set -a && source .env && set +a

PREFECT_API_URL=https://prefect.galatek.dev/api

# Get secrets from Prefect
NOTION_TOKEN=$(python3 -c "
from prefect.blocks.system import Secret
import asyncio
async def get():
    return await Secret.load('notion-token').get()
print(asyncio.run(get()))
")

# Base64 encode
ENCODED_TOKEN=$(echo -n "$NOTION_TOKEN" | base64)

# Write to .env.kestra
echo "SECRET_NOTION_TOKEN=$ENCODED_TOKEN" >> .env.kestra

echo "✅ Secrets migrated to .env.kestra"
```

---

## Testing Strategy

### Phase 1: Unit Testing (Kestra Flow YAML Validation)

**Test each flow file**:
```bash
pytest tests/kestra/test_signup_handler_flow.py -v
pytest tests/kestra/test_assessment_handler_flow.py -v
pytest tests/kestra/test_notion_tasks.py -v
pytest tests/kestra/test_resend_tasks.py -v
```

**Total Test Coverage**: 196 tests

**What's Tested**:
- YAML syntax validation
- Task structure verification
- Input/output validation
- Notion API payload correctness
- Resend API payload correctness
- Email scheduling logic
- Sequence tracker updates

### Phase 2: Integration Testing (Kestra API Execution)

**Start Kestra**:
```bash
docker-compose -f docker-compose.kestra.yml up -d
```

**Test Flow Execution**:
```bash
# Test signup handler
pytest tests/kestra/e2e/test_signup_e2e.py -v

# Test assessment handler with email_1_sent_at
pytest tests/kestra/e2e/test_assessment_e2e.py -v

# Test all handlers
pytest tests/kestra/e2e/test_all_handlers_e2e.py -v
```

### Phase 3: E2E Testing (Puppeteer)

**Test complete funnels**:
```bash
# Assessment funnel (website + Kestra)
pytest tests/kestra/e2e/test_puppeteer_assessment_funnel.py -v

# Signup funnel (tracking only)
pytest tests/kestra/e2e/test_puppeteer_signup_funnel.py -v

# Secondary funnels
pytest tests/kestra/e2e/test_puppeteer_secondary_funnels.py -v
```

### Testing Checklist

- [ ] All 196 unit tests passing
- [ ] YAML files validated by Kestra API
- [ ] Webhook triggers working
- [ ] Email #1 sent by website (mock)
- [ ] email_1_sent_at included in webhook payload
- [ ] Notion shows Email #1 as 'sent_by_website'
- [ ] Only 4 emails scheduled by Kestra (#2-5)
- [ ] Email #2 timing relative to email_1_sent_at correct
- [ ] Resend delivery working
- [ ] TESTING_MODE toggle working
- [ ] All secondary handlers working (noshow, postcall, onboarding)

---

## Rollback Plan

### Option 1: Quick Rollback (Prefect Still Deployed)

If Kestra fails in production and Prefect deployments still exist:

**Step 1**: Update website webhook URLs back to Prefect
```javascript
// Change from:
const WEBHOOK_URL = "http://kestra:8080/api/v1/executions/webhook/christmas/assessment-handler/KEY";

// Back to:
const WEBHOOK_URL = "http://localhost:8000/webhook/christmas-assessment";
```

**Step 2**: Restart Prefect worker
```bash
sudo systemctl restart prefect-worker
```

**Step 3**: Monitor Prefect dashboard
```
https://prefect.galatek.dev
```

**Rollback time**: ~5 minutes

### Option 2: Full Rollback (Kestra Removed)

If Kestra is completely removed:

**Step 1**: Stop Kestra
```bash
docker-compose -f docker-compose.kestra.yml down
```

**Step 2**: Restore Prefect flows from git
```bash
git checkout campaigns/christmas_campaign/flows/
```

**Step 3**: Redeploy Prefect flows
```bash
PREFECT_API_URL=https://prefect.galatek.dev/api \
  prefect deploy --all
```

**Step 4**: Update website webhook URLs (see Option 1)

**Rollback time**: ~15 minutes

### Data Preservation During Rollback

**Notion Databases** - No changes needed:
- Contacts database unchanged
- Email templates database unchanged
- Sequence tracker database unchanged

**Prefect vs Kestra** - Both use same Notion databases, so rollback is seamless.

---

## Troubleshooting

### Issue 1: "email_1_sent_at missing in webhook payload"

**Symptoms**: Kestra logs warning, uses webhook trigger time instead

**Root Cause**: Website not sending email_1_sent_at timestamp

**Fix**:
```javascript
// In website assessment completion handler
const email1SentAt = new Date().toISOString();

await sendEmail({
  template: "christmas_email_1",
  to: customer.email,
  variables: assessmentData
});

// CRITICAL: Include email_1_sent_at in webhook
await fetch(KESTRA_WEBHOOK_URL, {
  method: 'POST',
  body: JSON.stringify({
    ...assessmentData,
    email_1_sent_at: email1SentAt,  // ✅ REQUIRED
    email_1_status: "sent"           // ✅ REQUIRED
  })
});
```

### Issue 2: "Duplicate emails sent (Email #1 sent by both website and Kestra)"

**Symptoms**: Customer receives Email #1 twice

**Root Cause**: Assessment handler configured to send Email #1

**Fix**: Verify assessment-handler.yml does NOT have task for Email #1
```yaml
# ❌ WRONG - Do not include Email #1!
- id: send_email_1
  type: io.kestra.plugin.core.flow.Subflow
  flowId: send-email
  inputs:
    template_name: "christmas_email_1"

# ✅ CORRECT - Start from Email #2
- id: schedule_email_2
  type: io.kestra.plugin.core.flow.Subflow
  flowId: send-email
  inputs:
    template_name: "christmas_email_2"
  scheduleDate: "{{ inputs.email_1_sent_at | dateAdd(1, 'DAYS') }}"
```

### Issue 3: "Kestra webhook returns 404 Not Found"

**Symptoms**: Website POST to Kestra webhook fails with 404

**Root Cause**: Incorrect webhook URL or flow not deployed

**Fix**:
1. Verify flow deployed in Kestra UI
2. Check webhook key in flow definition:
```yaml
id: christmas-assessment-handler
namespace: christmas.handlers

triggers:
  - id: webhook
    type: io.kestra.plugin.core.trigger.Webhook
    key: "assessment-handler-webhook-key"  # ← Must match URL
```

3. Correct webhook URL format:
```
http://kestra:8080/api/v1/executions/webhook/christmas/handlers/assessment-handler-webhook-key
```

### Issue 4: "Email timing is wrong (Email #2 sent immediately instead of 24h later)"

**Symptoms**: All 4 emails sent immediately

**Root Cause**: Missing `scheduleDate` or incorrect TESTING_MODE

**Fix**: Verify scheduleDate calculation:
```yaml
- id: schedule_email_2
  type: io.kestra.plugin.core.flow.Subflow
  flowId: send-email
  inputs:
    template_name: "christmas_email_2"
  wait: true  # ✅ CRITICAL - Wait for scheduled time
  scheduleDate: "{{
    secret('SECRET_TESTING_MODE') == 'true'
    ? (inputs.email_1_sent_at | dateAdd(1, 'MINUTES'))
    : (inputs.email_1_sent_at | dateAdd(1, 'DAYS'))
  }}"
```

### Issue 5: "Notion sequence tracker not updating"

**Symptoms**: Emails sent but Notion doesn't show delivery status

**Root Cause**: update_sequence_tracker task failing silently

**Fix**: Check Kestra execution logs:
```bash
# View flow run logs in Kestra UI
http://localhost:8080/ui/executions

# Or via API
curl http://localhost:8080/api/v1/executions/{execution_id}/logs
```

Verify Notion update task includes all required fields:
```yaml
- id: update_sequence_tracker
  type: io.kestra.plugin.core.http.Request
  uri: "https://api.notion.com/v1/pages/{{ inputs.sequence_id }}"
  method: PATCH
  headers:
    Authorization: "Bearer {{ secret('SECRET_NOTION_TOKEN') }}"
    Notion-Version: "2022-06-28"
  body: |
    {
      "properties": {
        "Email Number": { "number": {{ inputs.email_number }} },
        "Sent At": { "date": { "start": "{{ inputs.sent_at }}" } },
        "Status": { "select": { "name": "sent" } },
        "Resend ID": { "rich_text": [{ "text": { "content": "{{ inputs.resend_id }}" } }] },
        "Sent By": { "select": { "name": "kestra" } }
      }
    }
```

### Issue 6: "Secret not found error"

**Symptoms**: Flow fails with "secret 'SECRET_NOTION_TOKEN' not found"

**Root Cause**: .env.kestra not loaded or wrong secret name

**Fix**:
1. Verify .env.kestra exists and has correct format:
```bash
cat .env.kestra
# Should show:
# SECRET_NOTION_TOKEN=<base64_value>
# SECRET_RESEND_API_KEY=<base64_value>
```

2. Restart Kestra to reload secrets:
```bash
docker-compose -f docker-compose.kestra.yml restart kestra
```

3. Verify secret names match in YAML:
```yaml
# Flow uses:
{{ secret('SECRET_NOTION_TOKEN') }}

# Must match .env.kestra:
SECRET_NOTION_TOKEN=...
```

---

## Migration Checklist

### Pre-Migration

- [ ] Export all Prefect Secret blocks to `.env.kestra`
- [ ] Base64 encode all secret values
- [ ] Test Kestra Docker Compose locally
- [ ] Verify all 196 unit tests passing
- [ ] Document all webhook endpoint URLs
- [ ] Update website integration docs

### Migration Execution

- [ ] Deploy Kestra on production server
- [ ] Load `.env.kestra` secrets
- [ ] Deploy all Kestra flows via UI or API
- [ ] Test all webhook endpoints
- [ ] Update website webhook URLs
- [ ] Test with TESTING_MODE=true
- [ ] Verify Email #1 sent by website
- [ ] Verify Emails #2-5 scheduled by Kestra
- [ ] Monitor first 10 real customers
- [ ] Switch TESTING_MODE=false for production timing

### Post-Migration

- [ ] Monitor Kestra execution dashboard
- [ ] Check Notion sequence tracker updates
- [ ] Verify Resend delivery rates
- [ ] Collect customer feedback
- [ ] Document any issues encountered
- [ ] Keep Prefect deployments for 30 days (rollback safety)
- [ ] Decommission Prefect after 30 days

---

## Support Resources

### Kestra Documentation

- **Official Docs**: https://kestra.io/docs
- **HTTP Plugin**: https://kestra.io/plugins/plugin-core/tasks/http/io.kestra.plugin.core.http.request
- **Python Script Plugin**: https://kestra.io/plugins/plugin-script-python
- **Webhook Trigger**: https://kestra.io/docs/workflow-components/triggers/webhook
- **Secret Management**: https://kestra.io/docs/configuration/secrets

### Internal Documentation

- **ARCHITECTURE.md**: Kestra architecture with email responsibility matrix
- **WEBSITE_INTEGRATION.md**: Webhook payload requirements and examples
- **DEPLOYMENT.md**: Kestra deployment guide for homelab

### Contact

**Questions?** Contact: sang@sanglescalinglabs.com

**Kestra UI**: http://localhost:8080 (local) or http://kestra.homelab (production)

---

**Migration Completed**: November 2025
**Last Updated**: 2025-11-30
**Next Review**: 2026-01-01 (post-holiday campaign analysis)
