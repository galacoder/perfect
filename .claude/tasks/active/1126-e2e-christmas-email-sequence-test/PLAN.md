# PLAN.md - E2E Christmas Campaign Email Sequence Test

**Task**: 1126-e2e-christmas-email-sequence-test
**Created**: 2025-11-26
**Domain**: CODING
**Test Email**: lengobaosang@gmail.com
**TDD Approach**: Yes (verify before execute)

---

## Executive Summary

This plan outlines a comprehensive E2E test of the Christmas Campaign email sequence. The test will send REAL emails to `lengobaosang@gmail.com` and verify the complete funnel from form submission to email delivery.

**Test Duration**:
- Wave 1: ~10 minutes (infrastructure)
- Wave 2: ~5 minutes (signup flow)
- Wave 3: ~5 minutes (assessment flow)
- Wave 4: ~15 minutes (email sequence in TESTING_MODE)
- Wave 5: ~15 minutes (verification & documentation)

**Total Estimated Time**: ~50 minutes

---

## Wave 1: Foundation - Infrastructure Verification

### 1.1 Objective
Verify all infrastructure components are operational before running real tests.

### 1.2 Tests

#### Test 1.1: Prefect Worker Status
**Command**:
```bash
PREFECT_API_URL=https://prefect.galatek.dev/api prefect work-pool ls
```
**Expected**: `default` work pool shows at least 1 active worker

#### Test 1.2: Prefect Deployments Exist
**Command**:
```bash
PREFECT_API_URL=https://prefect.galatek.dev/api prefect deployment ls
```
**Expected**:
- `christmas-signup-handler/christmas-signup-handler` - Ready
- `christmas-send-email/christmas-send-email` - Ready

#### Test 1.3: Secret Blocks Accessible
**Command**:
```bash
PREFECT_API_URL=https://prefect.galatek.dev/api python3 -c "
from prefect.blocks.system import Secret
blocks = ['notion-token', 'notion-email-templates-db-id', 'notion-email-sequence-db-id',
          'notion-businessx-db-id', 'resend-api-key']
for block in blocks:
    try:
        Secret.load(block)
        print(f'OK: {block}')
    except Exception as e:
        print(f'FAIL: {block} - {e}')
"
```
**Expected**: All 5 blocks return `OK`

#### Test 1.4: Notion API Connectivity
**Command**:
```bash
cd /Users/sangle/Dev/action/projects/perfect && \
source .env && \
python3 -c "
from notion_client import Client
import os
notion = Client(auth=os.getenv('NOTION_TOKEN'))
# Test Email Sequence DB
db = notion.databases.retrieve(os.getenv('NOTION_EMAIL_SEQUENCE_DB_ID'))
print(f'Email Sequence DB: {db[\"title\"][0][\"plain_text\"]}')
"
```
**Expected**: Returns database name

#### Test 1.5: Resend API Connectivity
**Command**:
```bash
cd /Users/sangle/Dev/action/projects/perfect && \
source .env && \
python3 -c "
import resend
import os
resend.api_key = os.getenv('RESEND_API_KEY')
# List domains to verify API key works
domains = resend.Domains.list()
print(f'Resend API OK - Domains: {len(domains.data)}')
"
```
**Expected**: Returns domain count

#### Test 1.6: Email Templates Exist in Notion
**Command**:
```bash
cd /Users/sangle/Dev/action/projects/perfect && \
source .env && \
python3 -c "
from notion_client import Client
import os
notion = Client(auth=os.getenv('NOTION_TOKEN'))
templates = ['christmas_email_1', 'christmas_email_2a_critical', 'christmas_email_3']
for t in templates:
    r = notion.databases.query(
        database_id=os.getenv('NOTION_EMAIL_TEMPLATES_DB_ID'),
        filter={'property': 'Template Name', 'title': {'equals': t}}
    )
    status = 'OK' if r['results'] else 'MISSING'
    print(f'{status}: {t}')
"
```
**Expected**: All templates return `OK`

### 1.3 Go/No-Go Criteria
- ALL tests must pass before proceeding to Wave 2
- If any test fails, document failure and troubleshoot before continuing

### 1.4 Rollback
- No rollback needed for verification tests

---

## Wave 2: Signup Flow Testing

### 2.1 Objective
Test the signup webhook with real email (lengobaosang@gmail.com) and verify contact creation.

### 2.2 Pre-Test: Clean Existing Data

**Step 2.0: Check for Existing Sequence**
```bash
cd /Users/sangle/Dev/action/projects/perfect && \
source .env && \
python3 -c "
from notion_client import Client
import os
notion = Client(auth=os.getenv('NOTION_TOKEN'))
r = notion.databases.query(
    database_id=os.getenv('NOTION_EMAIL_SEQUENCE_DB_ID'),
    filter={'property': 'Email', 'email': {'equals': 'lengobaosang@gmail.com'}}
)
if r['results']:
    print(f'EXISTING SEQUENCE FOUND: {r[\"results\"][0][\"id\"]}')
    print('ACTION: Delete or archive before testing')
else:
    print('NO EXISTING SEQUENCE - Ready for testing')
"
```

**Step 2.0b: Archive Existing Sequence (if needed)**
```bash
cd /Users/sangle/Dev/action/projects/perfect && \
source .env && \
python3 -c "
from notion_client import Client
import os
notion = Client(auth=os.getenv('NOTION_TOKEN'))
r = notion.databases.query(
    database_id=os.getenv('NOTION_EMAIL_SEQUENCE_DB_ID'),
    filter={'property': 'Email', 'email': {'equals': 'lengobaosang@gmail.com'}}
)
for page in r['results']:
    notion.pages.update(page_id=page['id'], archived=True)
    print(f'Archived: {page[\"id\"]}')
print('Cleanup complete')
"
```

### 2.3 Tests

#### Test 2.1: Direct Prefect API Trigger (Recommended)
**Command**:
```bash
curl -X POST https://prefect.galatek.dev/api/deployments/1ae3a3b3-e076-49c5-9b08-9c176aa47aa0/create_flow_run \
  -H "Content-Type: application/json" \
  -d '{
    "name": "e2e-test-signup-'$(date +%s)'",
    "parameters": {
      "email": "lengobaosang@gmail.com",
      "first_name": "Bao Sang",
      "business_name": "E2E Test Salon",
      "assessment_score": 52,
      "red_systems": 2,
      "orange_systems": 1,
      "yellow_systems": 2,
      "green_systems": 3,
      "gps_score": 45,
      "money_score": 38,
      "weakest_system_1": "GPS",
      "weakest_system_2": "Money",
      "revenue_leak_total": 14700
    }
  }'
```
**Expected Response**:
```json
{
  "id": "<flow-run-id>",
  "state_type": "SCHEDULED",
  "state_name": "Scheduled"
}
```
**Record**: Flow Run ID for tracking

#### Test 2.2: Monitor Flow Execution
**Command**:
```bash
PREFECT_API_URL=https://prefect.galatek.dev/api prefect flow-run logs <flow-run-id>
```
**Expected**:
- Flow starts
- Email sequence record created
- 7 email flows scheduled
- Flow completes successfully

### 2.4 Verification

#### Verify 2.1: Email Sequence Created in Notion
```bash
cd /Users/sangle/Dev/action/projects/perfect && \
source .env && \
python3 -c "
from notion_client import Client
import os
notion = Client(auth=os.getenv('NOTION_TOKEN'))
r = notion.databases.query(
    database_id=os.getenv('NOTION_EMAIL_SEQUENCE_DB_ID'),
    filter={'property': 'Email', 'email': {'equals': 'lengobaosang@gmail.com'}}
)
if r['results']:
    seq = r['results'][0]
    print(f'SEQUENCE ID: {seq[\"id\"]}')
    print(f'Campaign: {seq[\"properties\"][\"Campaign\"][\"select\"][\"name\"]}')
    print(f'Segment: {seq[\"properties\"].get(\"Segment\", {}).get(\"select\", {}).get(\"name\", \"N/A\")}')
    print('VERIFICATION: SUCCESS')
else:
    print('VERIFICATION: FAILED - No sequence found')
"
```

### 2.5 Expected Outcomes
- Flow run completes with status `Completed`
- Email sequence record exists in Notion
- Segment classified as `CRITICAL` (2+ red systems)
- 7 scheduled flow runs created

### 2.6 Rollback
If test fails:
1. Archive the created email sequence (if any)
2. Check Prefect logs for errors
3. Document failure details

---

## Wave 3: Assessment Flow Testing (Alternative Path)

### 3.1 Objective
Test the FastAPI webhook endpoint if local server is running.

### 3.2 Pre-Conditions
- FastAPI server running locally (`uvicorn server:app --reload`)
- TESTING_MODE=true in .env

### 3.3 Tests

#### Test 3.1: Health Check
```bash
curl http://localhost:8000/health
```
**Expected**:
```json
{
  "status": "healthy",
  "environment": {
    "testing_mode": "true",
    "notion_configured": true,
    "resend_configured": true
  }
}
```

#### Test 3.2: Christmas Signup Webhook
```bash
curl -X POST http://localhost:8000/webhook/christmas-signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "lengobaosang@gmail.com",
    "first_name": "Bao Sang",
    "business_name": "E2E Test Salon",
    "assessment_score": 52,
    "red_systems": 2,
    "orange_systems": 1,
    "yellow_systems": 2,
    "green_systems": 3,
    "gps_score": 45,
    "money_score": 38,
    "weakest_system_1": "GPS",
    "weakest_system_2": "Money",
    "revenue_leak_total": 14700
  }'
```
**Expected**:
```json
{
  "status": "accepted",
  "message": "Christmas signup received and email sequence will begin shortly",
  "campaign": "Christmas 2025"
}
```

### 3.4 Note
- Wave 3 is OPTIONAL if Wave 2 succeeds with direct Prefect API
- Wave 2 is the recommended path for production-like testing

---

## Wave 4: Complete Email Sequence Verification

### 4.1 Objective
Verify all 7 emails are delivered to lengobaosang@gmail.com.

### 4.2 Pre-Conditions
- Wave 2 completed successfully
- TESTING_MODE should be `true` for fast execution (~6 min total)

### 4.3 Monitoring Schedule (TESTING_MODE=true)

| Email | Expected Time | Verification Action |
|-------|---------------|---------------------|
| 1 | Immediate | Check inbox |
| 2 | +1 min | Check inbox |
| 3 | +2 min | Check inbox |
| 4 | +3 min | Check inbox |
| 5 | +4 min | Check inbox |
| 6 | +5 min | Check inbox |
| 7 | +6 min | Check inbox |

### 4.4 Tests

#### Test 4.1: List Scheduled Flow Runs
```bash
PREFECT_API_URL=https://prefect.galatek.dev/api prefect flow-run ls --limit 10
```
**Expected**: 7 flow runs for `christmas-send-email` with `Scheduled` status

#### Test 4.2: Monitor Email 1 Delivery
Wait for Email 1 to be sent (immediate), then verify:
```bash
PREFECT_API_URL=https://prefect.galatek.dev/api prefect flow-run logs <email-1-flow-run-id>
```
**Expected**: `Email sent: <resend-email-id>`

#### Test 4.3: Verify Notion Email Sequence Updates
```bash
cd /Users/sangle/Dev/action/projects/perfect && \
source .env && \
python3 -c "
from notion_client import Client
import os
notion = Client(auth=os.getenv('NOTION_TOKEN'))
r = notion.databases.query(
    database_id=os.getenv('NOTION_EMAIL_SEQUENCE_DB_ID'),
    filter={'property': 'Email', 'email': {'equals': 'lengobaosang@gmail.com'}}
)
if r['results']:
    seq = r['results'][0]['properties']
    for i in range(1, 8):
        field = f'Email {i} Sent'
        sent = seq.get(field, {}).get('date', {})
        status = 'SENT' if sent else 'PENDING'
        print(f'Email {i}: {status}')
"
```
**Expected**: All 7 emails show `SENT` status after sequence completes

### 4.5 Email Verification Checklist

For each email received at lengobaosang@gmail.com:

| Email | Subject Contains | Sender | Variables Populated |
|-------|------------------|--------|---------------------|
| 1 | "Assessment Results" or "BusOS" | noreply@sangletech.com | first_name, business_name |
| 2 | Segment-specific content | noreply@sangletech.com | first_name |
| 3-6 | Campaign content | noreply@sangletech.com | first_name |
| 7 | Final urgency | noreply@sangletech.com | first_name |

### 4.6 Expected Outcomes
- All 7 emails delivered to inbox (check spam too)
- Email content is personalized with correct variables
- Notion Email Sequence record shows all emails sent
- No duplicate emails (idempotency check)

### 4.7 Rollback
If emails not delivered:
1. Check Resend dashboard for delivery status
2. Check spam folder
3. Verify template exists in Notion
4. Check Prefect flow logs for errors

---

## Wave 5: Integration & Validation

### 5.1 Objective
Document test results and verify production readiness.

### 5.2 Documentation Tasks

#### Task 5.1: Record All Flow Run IDs
Create a test results file:
```bash
cat > /Users/sangle/Dev/action/projects/perfect/.claude/tasks/active/1126-e2e-christmas-email-sequence-test/TEST_RESULTS.md << 'EOF'
# E2E Test Results - Christmas Campaign Email Sequence

**Test Date**: $(date)
**Test Email**: lengobaosang@gmail.com

## Flow Run IDs

| Flow | Run ID | Status |
|------|--------|--------|
| Signup Handler | <id> | <status> |
| Email 1 | <id> | <status> |
| Email 2 | <id> | <status> |
| Email 3 | <id> | <status> |
| Email 4 | <id> | <status> |
| Email 5 | <id> | <status> |
| Email 6 | <id> | <status> |
| Email 7 | <id> | <status> |

## Email Delivery

| Email | Received | Time | Notes |
|-------|----------|------|-------|
| 1 | YES/NO | | |
| 2 | YES/NO | | |
| 3 | YES/NO | | |
| 4 | YES/NO | | |
| 5 | YES/NO | | |
| 6 | YES/NO | | |
| 7 | YES/NO | | |

## Issues Found

- [ ] None found
- [ ] Issue 1: ...
- [ ] Issue 2: ...

## Production Readiness

- [ ] All 7 emails delivered
- [ ] Variables correctly populated
- [ ] Notion records updated
- [ ] No duplicate sends
- [ ] READY FOR ADS

EOF
```

#### Task 5.2: Screenshot Evidence
- Take screenshots of emails received
- Save Notion database state
- Archive flow run logs

### 5.3 Production Mode Validation (Optional)

If time permits, test with `TESTING_MODE=false` to verify production timing:

**Note**: This would take 11+ days for full sequence. Only test timing verification:

```bash
PREFECT_API_URL=https://prefect.galatek.dev/api python3 -c "
from prefect.client.orchestration import get_client
import asyncio

async def check_scheduled_times():
    async with get_client() as client:
        runs = await client.read_flow_runs(limit=10)
        for run in runs:
            if 'christmas-send-email' in run.name:
                print(f'{run.name}: {run.state_name} @ {run.scheduled_time}')

asyncio.run(check_scheduled_times())
"
```

### 5.4 Expected Outcomes
- Complete test documentation
- All issues documented and resolved
- Production readiness confirmed

---

## Appendix A: Test Commands Quick Reference

### Start FastAPI Server (if needed)
```bash
cd /Users/sangle/Dev/action/projects/perfect && \
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

### Set TESTING_MODE
```bash
export TESTING_MODE=true
```

### View Prefect Flow Runs
```bash
PREFECT_API_URL=https://prefect.galatek.dev/api prefect flow-run ls
```

### View Flow Logs
```bash
PREFECT_API_URL=https://prefect.galatek.dev/api prefect flow-run logs <flow-run-id>
```

### Cancel Scheduled Flow Run (if needed)
```bash
PREFECT_API_URL=https://prefect.galatek.dev/api prefect flow-run cancel <flow-run-id>
```

---

## Appendix B: Troubleshooting

### Problem: Email not delivered
1. Check Resend dashboard (resend.com)
2. Check spam folder
3. Verify `FROM_EMAIL` domain is verified in Resend

### Problem: Flow run failed
1. Check flow logs: `prefect flow-run logs <id>`
2. Verify Secret blocks are accessible
3. Check Notion database permissions

### Problem: Duplicate emails
1. Flow is idempotent - check if previous sequence existed
2. Verify Email Sequence DB has the record

### Problem: Wrong segment classification
1. Check `red_systems` count in parameters
2. Verify routing logic in `tasks/routing.py`

---

## Appendix C: Cleanup Commands

### Archive Test Email Sequence
```bash
cd /Users/sangle/Dev/action/projects/perfect && \
source .env && \
python3 -c "
from notion_client import Client
import os
notion = Client(auth=os.getenv('NOTION_TOKEN'))
r = notion.databases.query(
    database_id=os.getenv('NOTION_EMAIL_SEQUENCE_DB_ID'),
    filter={'property': 'Email', 'email': {'equals': 'lengobaosang@gmail.com'}}
)
for page in r['results']:
    notion.pages.update(page_id=page['id'], archived=True)
    print(f'Archived: {page[\"id\"]}')
"
```

### Cancel All Scheduled Email Flows (Emergency)
```bash
PREFECT_API_URL=https://prefect.galatek.dev/api python3 -c "
from prefect.client.orchestration import get_client
import asyncio

async def cancel_scheduled():
    async with get_client() as client:
        runs = await client.read_flow_runs(limit=20)
        for run in runs:
            if 'christmas-send-email' in str(run.name) and run.state_name == 'Scheduled':
                await client.set_flow_run_state(run.id, state='Cancelled')
                print(f'Cancelled: {run.id}')

asyncio.run(cancel_scheduled())
"
```
