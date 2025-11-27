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

---

## Wave 6: Puppeteer E2E Funnel Test (ADDED)

### 6.1 Objective
Test the complete website funnel from landing page to email sequence using Puppeteer MCP browser automation.

### 6.2 Pre-Conditions
- Website running at https://sangletech.com (or localhost for local testing)
- Prefect worker running with TESTING_MODE=true
- Puppeteer MCP server connected

### 6.3 Complete Funnel Flow to Test

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 1: LANDING PAGE (/en/flows/businessX/dfu/xmas-a01)                     │
├─────────────────────────────────────────────────────────────────────────────┤
│ • Fill opt-in form (firstName, email, monthlyRevenue, biggestChallenge)     │
│ • Check privacy checkbox                                                     │
│ • Submit form → POST /api/form/submit-businessx-xmas-campaign               │
│ • localStorage saves: xmas-user-email, xmas-user-name                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 2: THANK YOU PAGE (/thank-you?name=...&email=...)                      │
├─────────────────────────────────────────────────────────────────────────────┤
│ • Displays personalized greeting                                             │
│ • CTA: "Start Your Free 8-System Assessment Now"                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 3: ASSESSMENT PAGE (/assessment)                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│ • Answer 16 yes/no questions (0.5s delay per question)                      │
│ • On completion:                                                             │
│   ├── POST /api/assessment/save-results (Notion)                            │
│   └── POST /api/assessment/complete → 🚀 TRIGGERS PREFECT WEBHOOK           │
│         │                                                                    │
│         └── Prefect christmas-signup-handler:                               │
│             ├── Creates Email Sequence record in Notion                     │
│             └── Schedules 7 email flows (TESTING_MODE: 1-6 min)             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                         ┌────────────┴────────────┐
                         │                         │
                         ▼                         ▼
┌──────────────────────────────────┐  ┌──────────────────────────────────────┐
│ EMAIL SEQUENCE (Background)       │  │ STEP 4: DIAGNOSTIC PAGE (/diagnostic) │
├──────────────────────────────────┤  ├──────────────────────────────────────┤
│ Email #1: Immediate              │  │ • Displays personalized results       │
│ Email #2: +1 min (testing)       │  │ • Shows broken systems (red/orange)   │
│ Email #3: +2 min                 │  │ • CTA: "Book FREE Discovery Call"     │
│ Email #4: +3 min                 │  └──────────────────────────────────────┘
│ Email #5: +4 min                 │                    │
│ Email #6: +5 min                 │                    ▼
│ Email #7: +6 min                 │  ┌──────────────────────────────────────┐
│                                  │  │ STEP 5: BOOK CALL PAGE (/book-call)   │
│ FROM: value@galatek.dev          │  ├──────────────────────────────────────┤
│ TO: lengobaosang@gmail.com       │  │ • Cal.com embedded calendar           │
└──────────────────────────────────┘  │ • calLink: sang-le-tech/businessx-   │
                                      │            together                   │
                                      │ • On booking success → redirect       │
                                      └──────────────────────────────────────┘
                                                       │
                                                       ▼
                                      ┌──────────────────────────────────────┐
                                      │ STEP 6: BOOKING CONFIRMED              │
                                      │ (/booking-confirmed?date=...&time=...) │
                                      ├──────────────────────────────────────┤
                                      │ • Displays booking details             │
                                      │ • POST /api/subscribe-and-notify       │
                                      │ • Facebook Pixel: InitiateCheckout     │
                                      └──────────────────────────────────────┘
```

**KEY INSIGHT**: The 7-email sequence is triggered at **Step 3 (Assessment Completion)**, NOT at booking. The book-call and booking-confirmed pages are part of the sales funnel but don't trigger additional email sequences.

### 6.4 Test Steps

#### Step 6.1: Navigate to Landing Page
```javascript
await page.goto('https://sangletech.com/en/flows/businessX/dfu/xmas-a01');
// OR for local: http://localhost:3000/en/flows/businessX/dfu/xmas-a01
```
**Verify**: Page loads with opt-in form visible

#### Step 6.2: Fill Opt-In Form
```javascript
await page.fill('#firstName', 'Puppeteer Test');
await page.fill('#email', 'lengobaosang@gmail.com');
await page.selectOption('#monthlyRevenue', '10k-20k');
await page.selectOption('#biggestChallenge', 'scaling');
await page.check('#privacy');
```
**Verify**: All fields populated, checkbox checked

#### Step 6.3: Submit Form
```javascript
await page.click('button[type="submit"]');
// Wait for redirect
await page.waitForURL(/thank-you/);
```
**Verify**:
- API response 200
- Redirect to thank-you page
- localStorage contains xmas-user-email and xmas-user-name

#### Step 6.4: Navigate to Assessment
```javascript
await page.click('a[href*="/assessment"]');
await page.waitForURL(/assessment/);
```
**Verify**: Assessment page loads with Question 1 visible

#### Step 6.5: Answer 16 Questions
```javascript
for (let i = 0; i < 16; i++) {
  // Create varied scoring pattern for realistic test
  if (i % 3 === 0) {
    await page.click('button:has-text("YES")');
  } else {
    await page.click('button:has-text("NO")');
  }
  await page.waitForTimeout(600); // Animation delay
}
```
**Verify**: Progress bar advances, final question shows completion state

#### Step 6.6: Verify Prefect Webhook
```javascript
// The assessment.tsx automatically calls /api/assessment/complete
// which triggers the Prefect webhook
```
**Verify**:
- Network request to /api/assessment/complete returns 200
- Response contains `success: true`

#### Step 6.7: Navigate to Diagnostic Page (Results)
```javascript
// After assessment completion, user sees results
// Click link to go to diagnostic page
await page.click('a[href*="/diagnostic"]');
await page.waitForURL(/diagnostic/);
```
**Verify**:
- Personalized hero shows assessment results
- System scores displayed (red/orange/yellow/green)
- CTA visible: "Book FREE Discovery Call"

#### Step 6.8: Navigate to Book Call Page
```javascript
await page.click('a[href*="/book-call"]');
await page.waitForURL(/book-call/);
```
**Verify**: Page loads with Cal.com calendar section

#### Step 6.9: Verify Cal.com Calendar Loads
```javascript
// Cal.com calendar is embedded via @calcom/embed-react
// calLink: "sang-le-tech/businessx-together"
// Wait for Cal.com iframe to load
await page.waitForSelector('iframe[src*="cal.com"]', { timeout: 10000 });
```
**Verify**:
- Cal.com calendar iframe is visible
- Calendar shows available time slots

**NOTE**: Actually booking via Cal.com requires interacting with external service.
For E2E testing, we verify:
1. Calendar loads successfully
2. Page displays correctly
3. (Optional) Mock Cal.com booking callback to test redirect to booking-confirmed

#### Step 6.10: Verify Email Sequence Created
```bash
# Check Notion Email Sequence Database
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
    print(f'✅ SEQUENCE FOUND: {seq[\"id\"]}')
    print(f'   Campaign: {seq[\"properties\"][\"Campaign\"][\"select\"][\"name\"]}')
    print(f'   Segment: {seq[\"properties\"].get(\"Segment\", {}).get(\"select\", {}).get(\"name\", \"N/A\")}')
"
```
**Verify**: Email sequence record exists with Christmas 2025 campaign

#### Step 6.8: Monitor Email Delivery
```bash
PREFECT_API_URL=https://prefect.galatek.dev/api prefect flow-run ls \
  --flow-name christmas-send-email \
  --limit 10
```
**Verify** (with TESTING_MODE=true):
- Email #1: Sent immediately
- Email #2: Sent after 1 min
- Email #3: Sent after 2 min
- Email #4: Sent after 3 min
- Email #5: Sent after 4 min
- Email #6: Sent after 5 min
- Email #7: Sent after 6 min

### 6.5 Expected Outcomes
- Complete funnel traversal without errors
- 7 emails delivered to lengobaosang@gmail.com
- Notion Email Sequence updated with all "Email X Sent" timestamps
- Production readiness confirmed

### 6.6 CSS Selectors Reference

| Page | Element | Selector |
|------|---------|----------|
| **Landing** | First Name | `#firstName` |
| **Landing** | Email | `#email` |
| **Landing** | Revenue Dropdown | `#monthlyRevenue` |
| **Landing** | Challenge Dropdown | `#biggestChallenge` |
| **Landing** | Privacy Checkbox | `#privacy` |
| **Landing** | Submit Button | `button[type="submit"]` |
| **Thank You** | Assessment CTA | `a[href*="/assessment"]` |
| **Assessment** | YES Button | `button:has-text("YES")` |
| **Assessment** | NO Button | `button:has-text("NO")` |
| **Assessment** | Progress | `text=/Question \\d+ of 16/` |
| **Diagnostic** | Book Call CTA | `a[href*="/book-call"]` |
| **Diagnostic** | Score Display | `text=/\\d+\\/100/` |
| **Book Call** | Cal.com Calendar | `iframe[src*="cal.com"]` |
| **Book Call** | Page Title | `text=/Book Your FREE/` |

### 6.7 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/form/submit-businessx-xmas-campaign` | POST | Opt-in form submission |
| `/api/assessment/save-results` | POST | Save to Notion |
| `/api/assessment/complete` | POST | Trigger Prefect webhook |

### 6.8 Environment Variables Required

For the website (sangletech-tailwindcss):
```bash
PREFECT_WEBHOOK_URL=https://prefect.galatek.dev/api/webhook/christmas-signup
# OR for local: http://localhost:8000/webhook/christmas-signup
```

For Prefect worker:
```bash
TESTING_MODE=true  # Fast email intervals (1-6 min)
```

---

## Wave 9: Full Funnel + All Email Sequences Test (ADDED)

### 9.1 Objective
Fix frontend assessment loading bug, complete E2E sales funnel via Puppeteer, and test all 4 email sequences (16 emails total) to lengobaosang@gmail.com.

### 9.2 Pre-Conditions
- Frontend project at: `/Users/sangle/Dev/action/projects/@new-websites/sangletech-tailwindcss`
- Assessment page path: `pages/en/flows/businessX/dfu/xmas-a01`
- FastAPI server running at localhost:8000
- Prefect deployments active with TESTING_MODE=true
- Test email: lengobaosang@gmail.com

### 9.3 Tasks

#### Task 9.1: Investigate Frontend Assessment Loading Bug (CRITICAL)
**Issue**: Assessment page stuck on "Preparing your 8-System Assessment..." loading screen

**Investigation Steps**:
1. Verify dev server running at localhost:3005
2. Open browser DevTools and check console for errors
3. Inspect `assessment.tsx` component for initialization issues
4. Check localStorage for missing/corrupted user data

**Test Scenarios**:
- [ ] Verify dev server running
- [ ] Check browser console for errors
- [ ] Inspect assessment.tsx component
- [ ] Check localStorage initialization

**Estimated Time**: 30 minutes

#### Task 9.2: Fix Frontend Assessment Bug (CRITICAL)
**Once root cause identified, apply fix**

**Test Scenarios**:
- [ ] Apply fix to assessment component
- [ ] Verify page loads correctly
- [ ] Test state transitions
- [ ] Verify no console errors

**Estimated Time**: 30 minutes

#### Task 9.3: Puppeteer E2E - Opt-In Form Submission
```javascript
// Navigate to landing page
await page.goto('http://localhost:3005/en/flows/businessX/dfu/xmas-a01');

// Fill opt-in form
await page.fill('#firstName', 'E2E Test User');
await page.fill('#email', 'lengobaosang@gmail.com');
await page.selectOption('#monthlyRevenue', '10k-20k');
await page.selectOption('#biggestChallenge', 'scaling');
await page.check('#privacy');

// Submit
await page.click('button[type="submit"]');
await page.waitForURL(/thank-you/);
```

**Test Scenarios**:
- [ ] Navigate to landing page
- [ ] Fill form fields
- [ ] Submit form
- [ ] Verify redirect to thank-you

**Estimated Time**: 15 minutes

#### Task 9.4: Puppeteer E2E - Complete 16-Question Assessment
```javascript
// Navigate to assessment
await page.click('a[href*="/assessment"]');
await page.waitForURL(/assessment/);

// Answer 16 questions (varied pattern)
for (let i = 0; i < 16; i++) {
  if (i % 3 === 0) {
    await page.click('button:has-text("YES")');
  } else {
    await page.click('button:has-text("NO")');
  }
  await page.waitForTimeout(600);
}
```

**Test Scenarios**:
- [ ] Navigate to assessment
- [ ] Answer all 16 questions
- [ ] Verify completion triggers webhook
- [ ] Verify redirect to results

**Estimated Time**: 20 minutes

#### Task 9.5: Verify Webhook Triggers and Notion Records
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
"
```

**Test Scenarios**:
- [ ] Check Prefect flow triggered
- [ ] Verify email sequence created in Notion
- [ ] Check segment classification

**Estimated Time**: 10 minutes

#### Task 9.6: Send Lead Nurture Email Sequence (7 emails)
**Trigger**: Via website opt-in + assessment completion (Tasks 9.3-9.5)
**Email Count**: 7
**Expected Time**: ~6 minutes with TESTING_MODE

**Test Scenarios**:
- [ ] Trigger christmas-signup-handler
- [ ] Monitor 7 emails scheduled
- [ ] Wait for all 7 emails sent (~6 min with TESTING_MODE)
- [ ] Verify all delivered

**Estimated Time**: 15 minutes

#### Task 9.7: Send No-Show Recovery Email Sequence (3 emails)
**Trigger**: POST /webhook/calendly-no-show
```bash
curl -X POST http://localhost:8000/webhook/calendly-no-show \
  -H "Content-Type: application/json" \
  -d '{
    "email": "lengobaosang@gmail.com",
    "first_name": "Bao Sang",
    "business_name": "Test Salon",
    "event_name": "BusinessX Discovery Call",
    "event_time": "2025-11-27T14:00:00Z"
  }'
```
**Email Count**: 3

**Test Scenarios**:
- [ ] Trigger calendly-no-show webhook
- [ ] Monitor 3 emails scheduled
- [ ] Wait for all 3 emails sent
- [ ] Verify all delivered

**Estimated Time**: 10 minutes

#### Task 9.8: Send Post-Call Maybe Email Sequence (3 emails)
**Trigger**: POST /webhook/post-call-maybe
```bash
curl -X POST http://localhost:8000/webhook/post-call-maybe \
  -H "Content-Type: application/json" \
  -d '{
    "email": "lengobaosang@gmail.com",
    "first_name": "Bao Sang",
    "business_name": "Test Salon",
    "call_date": "2025-11-27"
  }'
```
**Email Count**: 3

**Test Scenarios**:
- [ ] Trigger post-call-maybe webhook
- [ ] Monitor 3 emails scheduled
- [ ] Wait for all 3 emails sent
- [ ] Verify all delivered

**Estimated Time**: 10 minutes

#### Task 9.9: Send Onboarding Email Sequence (3 emails)
**Trigger**: POST /webhook/onboarding-phase1
```bash
curl -X POST http://localhost:8000/webhook/onboarding-phase1 \
  -H "Content-Type: application/json" \
  -d '{
    "email": "lengobaosang@gmail.com",
    "first_name": "Bao Sang",
    "business_name": "Test Salon",
    "client_since": "2025-11-27"
  }'
```
**Email Count**: 3

**Test Scenarios**:
- [ ] Trigger onboarding webhook
- [ ] Monitor 3 emails scheduled
- [ ] Wait for all 3 emails sent
- [ ] Verify all delivered

**Estimated Time**: 10 minutes

#### Task 9.10: Verify All 16 Emails in Resend Dashboard (CRITICAL)
**Check Resend API for all sent emails**:
```bash
cd /Users/sangle/Dev/action/projects/perfect && \
source .env && \
python3 -c "
import resend
import os
resend.api_key = os.getenv('RESEND_API_KEY')

# List recent emails
emails = resend.Emails.list()
target_email = 'lengobaosang@gmail.com'

count = 0
for email in emails.data[:50]:  # Check last 50
    if email.to and target_email in str(email.to):
        count += 1
        print(f'{count}. {email.subject[:50]} - {email.status}')

print(f'\\nTotal emails to {target_email}: {count}')
print(f'Expected: 16 (7 Lead + 3 NoShow + 3 Maybe + 3 Onboard)')
"
```

**Test Scenarios**:
- [ ] Check Resend API for all emails
- [ ] Verify delivery status for all 16
- [ ] Document any bounces or failures
- [ ] Screenshot evidence

**Expected Emails**: 16 total
**Estimated Time**: 15 minutes

### 9.4 Email Sequence Summary

| Sequence | Email Count | Trigger | Wait Times (TESTING_MODE) |
|----------|-------------|---------|---------------------------|
| Lead Nurture | 7 | Website funnel completion | 0, 1, 2, 3, 4, 5, 6 min |
| No-Show Recovery | 3 | calendly-no-show webhook | 0, 1, 2 min |
| Post-Call Maybe | 3 | post-call-maybe webhook | 0, 1, 2 min |
| Onboarding Phase 1 | 3 | onboarding-phase1 webhook | 0, 1, 2 min |
| **TOTAL** | **16** | | |

### 9.5 Expected Outcomes
- Frontend bug fixed and assessment loads correctly
- Complete E2E funnel passes via Puppeteer
- All 16 emails sent and delivered to lengobaosang@gmail.com
- Resend dashboard confirms all 16 emails delivered
- No bounces or failures

### 9.6 Total Estimated Time
- Frontend bug investigation/fix: 60 minutes
- E2E funnel test: 45 minutes
- Email sequences (4 total): 45 minutes
- Resend verification: 15 minutes
- **Total Wave 9**: ~2.5 hours

---

## Wave 11: Verify Updated Templates After Testimonial Audit (ADDED)

### 11.1 Objective
Re-test all 16 emails after template updates from task `1127-audit-email-templates-replace-fabricated-case-studies`. Verify that real testimonials (Van Tiny, Hera Nguyen, Loc Diem) have replaced fabricated ones (Jennifer K, Sarah P, Linh, Marcus Chen, etc.).

### 11.2 Context
**Related Task**: 1127-audit-email-templates-replace-fabricated-case-studies
**Changes Made**: Replaced 42 fabricated testimonials with real case studies
**Real Testimonials Added**: Van Tiny, Hera Nguyen, Loc Diem
**Fabricated Names Removed**: Jennifer K, Sarah P, Linh, Marcus Chen, Maria Santos, David Kim

### 11.3 Tasks

#### Task 11.1: Verify Notion Email Templates Have Updated Testimonials
**Command**:
```bash
cd /Users/sangle/Dev/action/projects/perfect && \
source .env && \
python3 -c "
from notion_client import Client
import os
notion = Client(auth=os.getenv('NOTION_TOKEN'))

# Query all email templates
templates = notion.databases.query(
    database_id=os.getenv('NOTION_EMAIL_TEMPLATES_DB_ID')
)

real_names = ['Van Tiny', 'Hera Nguyen', 'Loc Diem']
fabricated_names = ['Jennifer K', 'Sarah P', 'Linh', 'Marcus Chen', 'Maria Santos', 'David Kim']

for template in templates['results']:
    name = template['properties']['Template Name']['title'][0]['plain_text']
    # Check body content for testimonials
    body = template['properties'].get('Body', {}).get('rich_text', [])
    body_text = ' '.join([t['plain_text'] for t in body]) if body else ''

    has_real = any(n in body_text for n in real_names)
    has_fabricated = any(n in body_text for n in fabricated_names)

    status = 'OK' if has_real and not has_fabricated else 'CHECK' if has_fabricated else 'CLEAN'
    print(f'{status}: {name}')
"
```
**Expected**: All templates show OK or CLEAN (no fabricated names)
**Estimated Time**: 10 minutes

#### Task 11.2: Send Updated Lead Nurture Sequence (7 emails)
**Trigger**: Via christmas-signup-handler or orchestrate_sequence.py
**Test Email**: lengobaosang@gmail.com
**Email Count**: 7

**Test Scenarios**:
- [ ] Trigger christmas-signup-handler
- [ ] Verify all 7 emails scheduled
- [ ] Wait for all 7 emails sent (~6 min with TESTING_MODE)
- [ ] Verify templates render correctly with real testimonials

**Estimated Time**: 15 minutes

#### Task 11.3: Send Updated No-Show Recovery Sequence (3 emails)
**Trigger**: POST /webhook/calendly-no-show
```bash
curl -X POST http://localhost:8000/webhook/calendly-no-show \
  -H "Content-Type: application/json" \
  -d '{
    "email": "lengobaosang@gmail.com",
    "first_name": "Template Test",
    "business_name": "Test Salon",
    "event_name": "BusinessX Discovery Call",
    "event_time": "2025-11-27T14:00:00Z"
  }'
```
**Email Count**: 3

**Test Scenarios**:
- [ ] Trigger noshow-recovery-handler via webhook
- [ ] Verify all 3 emails scheduled
- [ ] Test all 3 emails with new testimonials
- [ ] Verify delivery

**Estimated Time**: 10 minutes

#### Task 11.4: Send Updated Post-Call Maybe Sequence (3 emails)
**Trigger**: POST /webhook/post-call-maybe
```bash
curl -X POST http://localhost:8000/webhook/post-call-maybe \
  -H "Content-Type: application/json" \
  -d '{
    "email": "lengobaosang@gmail.com",
    "first_name": "Template Test",
    "business_name": "Test Salon",
    "call_date": "2025-11-27"
  }'
```
**Email Count**: 3
**Special Attention**: postcall_maybe_email_2 was updated with Van Tiny testimonial

**Test Scenarios**:
- [ ] Trigger postcall-maybe-handler via webhook
- [ ] Specifically verify postcall_maybe_email_2 (updated with Van Tiny)
- [ ] Verify all 3 emails scheduled and delivered
- [ ] Check testimonial content renders correctly

**Estimated Time**: 10 minutes

#### Task 11.5: Send Updated Onboarding Sequence (3 emails)
**Trigger**: POST /webhook/onboarding-phase1
```bash
curl -X POST http://localhost:8000/webhook/onboarding-phase1 \
  -H "Content-Type: application/json" \
  -d '{
    "email": "lengobaosang@gmail.com",
    "first_name": "Template Test",
    "business_name": "Test Salon",
    "client_since": "2025-11-27"
  }'
```
**Email Count**: 3

**Test Scenarios**:
- [ ] Trigger onboarding-handler via webhook
- [ ] Verify all 3 emails scheduled
- [ ] Test all 3 emails delivered
- [ ] Check content renders correctly

**Estimated Time**: 10 minutes

#### Task 11.6: Verify All 16 Emails Delivered in Resend
**Command**:
```bash
cd /Users/sangle/Dev/action/projects/perfect && \
source .env && \
python3 -c "
import resend
import os
resend.api_key = os.getenv('RESEND_API_KEY')

emails = resend.Emails.list()
target_email = 'lengobaosang@gmail.com'

count = 0
for email in emails.data[:50]:
    if email.to and target_email in str(email.to):
        count += 1
        print(f'{count}. {email.subject[:60]} - {email.status}')

print(f'\\nTotal emails to {target_email}: {count}')
print(f'Expected: 16 (7 Lead + 3 NoShow + 3 Maybe + 3 Onboard)')
"
```

**Test Scenarios**:
- [ ] Check Resend API for all 16 emails
- [ ] Verify delivery status via Resend API
- [ ] Confirm no template rendering errors
- [ ] Document delivery timestamps

**Expected Emails**: 16 total
**Estimated Time**: 10 minutes

#### Task 11.7: Visual Verification - Review Email Content
**Manual Steps**:
1. Open lengobaosang@gmail.com inbox
2. Locate all 16 emails from Wave 11 test
3. For each email with testimonials:
   - Verify Van Tiny, Hera Nguyen, or Loc Diem names appear
   - Confirm no Jennifer K, Sarah P, Linh, Marcus Chen, Maria Santos, David Kim
   - Check all placeholder variables are substituted
4. Take screenshots as evidence

**Test Scenarios**:
- [ ] Open emails in inbox (lengobaosang@gmail.com)
- [ ] Check that testimonials display correctly (Van Tiny, Hera Nguyen stories)
- [ ] Verify no placeholder variables remain unsubstituted
- [ ] Confirm no fabricated names appear (Jennifer K, Sarah P, etc.)
- [ ] Screenshot evidence of real testimonials

**Estimated Time**: 15 minutes

### 11.4 Email Sequence Summary

| Sequence | Email Count | Trigger | Key Testimonials to Verify |
|----------|-------------|---------|---------------------------|
| Lead Nurture | 7 | christmas-signup-handler | Van Tiny, Hera Nguyen |
| No-Show Recovery | 3 | calendly-no-show webhook | Various |
| Post-Call Maybe | 3 | post-call-maybe webhook | Van Tiny (email 2) |
| Onboarding | 3 | onboarding-phase1 webhook | Various |
| **TOTAL** | **16** | | |

### 11.5 Expected Outcomes
- All 16 email templates verified in Notion (no fabricated names)
- All 16 emails sent and delivered to lengobaosang@gmail.com
- Real testimonials (Van Tiny, Hera Nguyen, Loc Diem) display correctly
- No fabricated names (Jennifer K, Sarah P, etc.) appear in any email
- No unsubstituted placeholder variables

### 11.6 Total Estimated Time
- Notion template verification: 10 minutes
- Lead Nurture sequence: 15 minutes
- No-Show Recovery sequence: 10 minutes
- Post-Call Maybe sequence: 10 minutes
- Onboarding sequence: 10 minutes
- Resend verification: 10 minutes
- Visual verification: 15 minutes
- **Total Wave 11**: ~1.5 hours

---

## Wave 12: Production Readiness (ADDED)

### 12.1 Objective
Perform comprehensive production readiness verification before advertisement launch. Test full E2E funnel with Puppeteer, verify Notion template fetching (not hardcoded), test all 4 email sequences via production Prefect server, and complete production readiness checklist.

### 12.2 Pre-Conditions
- Frontend project at: `/Users/sangle/Dev/action/projects/@new-websites/sangletech-tailwindcss`
- FastAPI server running at localhost:8000
- Production Prefect server: https://prefect.galatek.dev
- Test email: lengobaosang@gmail.com
- All Prefect deployments active with TESTING_MODE=true

### 12.3 Tasks

#### Task 12.1: Start sangletech-tailwindcss Dev Server (localhost:3005)
**Command**:
```bash
cd /Users/sangle/Dev/action/projects/@new-websites/sangletech-tailwindcss && pnpm dev
```
**Expected**:
- Server starts on localhost:3005
- Pages load at localhost:3005/en/flows/businessX/dfu/xmas-a01/

**Test Scenarios**:
- [ ] Run pnpm dev in /Users/sangle/Dev/action/projects/@new-websites/sangletech-tailwindcss
- [ ] Verify server starts successfully on localhost:3005
- [ ] Verify pages load at localhost:3005/en/flows/businessX/dfu/xmas-a01/

**Estimated Time**: 5 minutes

#### Task 12.2: Full E2E Test Through Sales Funnel with Puppeteer
**Navigate through complete funnel**:
```javascript
// Navigate to opt-in page
await page.goto('http://localhost:3005/en/flows/businessX/dfu/xmas-a01/');

// Fill form with test data
await page.fill('#firstName', 'Production Test');
await page.fill('#email', 'lengobaosang@gmail.com');
await page.selectOption('#monthlyRevenue', '10k-20k');
await page.selectOption('#biggestChallenge', 'scaling');
await page.check('#privacy');

// Submit form
await page.click('button[type="submit"]');
await page.waitForURL(/thank-you/);

// Continue to assessment
await page.click('a[href*="/assessment"]');
await page.waitForURL(/assessment/);

// Answer 16 questions
for (let i = 0; i < 16; i++) {
  if (i % 3 === 0) {
    await page.click('button:has-text("YES")');
  } else {
    await page.click('button:has-text("NO")');
  }
  await page.waitForTimeout(600);
}
```

**Test Scenarios**:
- [ ] Navigate to opt-in page at localhost:3005/en/flows/businessX/dfu/xmas-a01/
- [ ] Fill form with test data (email: lengobaosang@gmail.com)
- [ ] Complete assessment (16 questions)
- [ ] Verify webhook triggers FastAPI server (localhost:8000)
- [ ] Verify Prefect flow runs on PRODUCTION server (https://prefect.galatek.dev)

**Estimated Time**: 20 minutes

#### Task 12.3: Verify Email Flows Fetch Templates from Notion Database (CRITICAL)
**Check orchestrate_sequence.py for Notion API usage**:
```bash
# Verify code uses Notion API to fetch templates
grep -n "notion" campaigns/christmas_campaign/flows/orchestrate_sequence.py
grep -n "NOTION_EMAIL_TEMPLATES_DB_ID" campaigns/christmas_campaign/flows/orchestrate_sequence.py

# Check for hardcoded templates (should NOT find any)
grep -n "subject.*=" campaigns/christmas_campaign/flows/orchestrate_sequence.py
grep -n "body.*=" campaigns/christmas_campaign/flows/orchestrate_sequence.py

# Verify Version field usage
grep -n "Version" campaigns/christmas_campaign/flows/orchestrate_sequence.py
```

**Test Scenarios**:
- [ ] Check that orchestrate_sequence.py uses Notion API to fetch templates
- [ ] Verify templates are NOT hardcoded
- [ ] Verify templates come from NOTION_EMAIL_TEMPLATES_DB_ID
- [ ] Verify Version field is used to get latest template updates

**Estimated Time**: 15 minutes

#### Task 12.4: Test Webhook to Prefect Production Flow Chain
**Trigger webhook and verify production flow**:
```bash
# Start FastAPI server (if not running)
cd /Users/sangle/Dev/action/projects/perfect && uvicorn server:app --reload --port 8000

# Trigger signup webhook
curl -X POST http://localhost:8000/webhook/christmas-signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "lengobaosang@gmail.com",
    "first_name": "Production Test",
    "business_name": "Test Salon",
    "assessment_score": 52,
    "red_systems": 2,
    "orange_systems": 1,
    "yellow_systems": 2,
    "green_systems": 3
  }'

# Verify flow runs on production Prefect
PREFECT_API_URL=https://prefect.galatek.dev/api prefect flow-run ls --limit 5
```

**Test Scenarios**:
- [ ] POST to localhost:8000/webhook/signup triggers Prefect flow
- [ ] Flow runs on production Prefect server (https://prefect.galatek.dev/api)
- [ ] Verify flow uses Secret blocks for credentials
- [ ] Verify flow fetches templates from Notion

**Estimated Time**: 15 minutes

#### Task 12.5: Verify All 4 Sequences Work via Production Prefect
**Test each email sequence**:

**Lead Nurture (7 emails)**:
```bash
# Already triggered via Task 12.4 or Task 12.2
# Verify 7 emails scheduled
PREFECT_API_URL=https://prefect.galatek.dev/api prefect flow-run ls --flow-name christmas-send-email --limit 10
```

**No-Show Recovery (3 emails)**:
```bash
curl -X POST http://localhost:8000/webhook/calendly-no-show \
  -H "Content-Type: application/json" \
  -d '{
    "email": "lengobaosang@gmail.com",
    "first_name": "Production Test",
    "business_name": "Test Salon",
    "event_name": "BusinessX Discovery Call",
    "event_uri": "https://calendly.com/test/123"
  }'
```

**Post-Call Maybe (3 emails)**:
```bash
curl -X POST http://localhost:8000/webhook/post-call-maybe \
  -H "Content-Type: application/json" \
  -d '{
    "email": "lengobaosang@gmail.com",
    "first_name": "Production Test",
    "business_name": "Test Salon",
    "call_date": "2025-11-27",
    "call_notes": "Interested but needs to think",
    "objections": ["price", "timing"]
  }'
```

**Onboarding (3 emails)**:
```bash
curl -X POST http://localhost:8000/webhook/onboarding-phase1 \
  -H "Content-Type: application/json" \
  -d '{
    "email": "lengobaosang@gmail.com",
    "first_name": "Production Test",
    "business_name": "Test Salon",
    "client_since": "2025-11-27"
  }'
```

**Test Scenarios**:
- [ ] Lead Nurture (7 emails) - triggered, templates from Notion
- [ ] No-Show Recovery (3 emails) - triggered, templates from Notion
- [ ] Post-Call Maybe (3 emails) - triggered, templates from Notion
- [ ] Onboarding (3 emails) - triggered, templates from Notion

**Estimated Time**: 30 minutes

#### Task 12.6: Production Readiness Checklist
**Final checklist before ad launch**:

| Check | Status | Notes |
|-------|--------|-------|
| All webhooks trigger correct Prefect deployments | [ ] | |
| All templates fetched from Notion (not hardcoded) | [ ] | |
| All credentials from Secret blocks (not .env) | [ ] | |
| Git-based deployment working | [ ] | |
| Ready for advertisement launch | [ ] | |

**Verification Commands**:
```bash
# Check deployments exist
PREFECT_API_URL=https://prefect.galatek.dev/api prefect deployment ls

# Check Secret blocks accessible
PREFECT_API_URL=https://prefect.galatek.dev/api python3 -c "
from prefect.blocks.system import Secret
blocks = ['notion-token', 'notion-email-templates-db-id', 'resend-api-key']
for block in blocks:
    try:
        Secret.load(block)
        print(f'OK: {block}')
    except Exception as e:
        print(f'FAIL: {block} - {e}')
"

# Check git-based deployment
PREFECT_API_URL=https://prefect.galatek.dev/api prefect deployment inspect christmas-signup-handler/christmas-signup-handler | grep -A5 "pull"
```

**Test Scenarios**:
- [ ] All webhooks trigger correct Prefect deployments
- [ ] All templates fetched from Notion (not hardcoded)
- [ ] All credentials from Secret blocks (not .env)
- [ ] Git-based deployment working
- [ ] Ready for advertisement launch

**Estimated Time**: 10 minutes

### 12.4 Email Sequence Summary

| Sequence | Email Count | Trigger | Template Source |
|----------|-------------|---------|-----------------|
| Lead Nurture | 7 | christmas-signup-handler | Notion (NOTION_EMAIL_TEMPLATES_DB_ID) |
| No-Show Recovery | 3 | calendly-no-show webhook | Notion |
| Post-Call Maybe | 3 | post-call-maybe webhook | Notion |
| Onboarding | 3 | onboarding-phase1 webhook | Notion |
| **TOTAL** | **16** | | |

### 12.5 Expected Outcomes
- Dev server running at localhost:3005
- Full E2E funnel completes successfully via Puppeteer
- All email templates fetched from Notion (not hardcoded)
- All webhooks trigger correct Prefect deployments
- All 16 emails (4 sequences) work via production Prefect
- Production readiness checklist complete
- **READY FOR ADVERTISEMENT LAUNCH**

### 12.6 Total Estimated Time
- Dev server startup: 5 minutes
- Full E2E Puppeteer test: 20 minutes
- Notion template verification: 15 minutes
- Webhook to Prefect chain test: 15 minutes
- All 4 sequences verification: 30 minutes
- Production readiness checklist: 10 minutes
- **Total Wave 12**: ~1.5 hours

---

## Wave 13: Production Site E2E Test (ADDED)

### 13.1 Objective
Full E2E test on PRODUCTION site (sangletech.com NOT localhost) using Puppeteer MCP. Test complete funnel, all 4 email sequences (16 emails total), and verify new template variables from task 1127.

### 13.2 Context
**Production Site Deployed**: https://sangletech.com
**Task 1127 Completed**: Email templates updated with:
- Real testimonials: Van Tiny, Hera Nguyen, Loc Diem
- New automation variables: {{q1_foundation_deadline}}, {{days_to_q1_deadline}}, {{slots_remaining}}, {{spots_taken}}
- Deadline changed: November 15 -> December 15, 2025
- Slot count: 10 founding members

### 13.3 Pre-Conditions
- Production site live at https://sangletech.com
- Puppeteer MCP server connected
- Prefect worker running at https://prefect.galatek.dev with TESTING_MODE=true
- Test email: lengobaosang@gmail.com

### 13.4 Tasks

#### Task 13.1: Puppeteer - Navigate to PRODUCTION Sales Funnel
**Use Puppeteer MCP**:
```javascript
// Navigate to PRODUCTION site (NOT localhost!)
await puppeteer_navigate({ url: 'https://sangletech.com/en/flows/businessX/dfu/xmas-a01' });
await puppeteer_screenshot({ name: 'wave13-landing-page' });
```
**Verify**:
- Page loads without errors
- Opt-in form visible
- Screenshot captured

**Estimated Time**: 5 minutes

#### Task 13.2: Puppeteer - Complete Opt-In Form
**Use Puppeteer MCP**:
```javascript
await puppeteer_fill({ selector: '#firstName', value: 'Production Test' });
await puppeteer_fill({ selector: '#email', value: 'lengobaosang@gmail.com' });
await puppeteer_select({ selector: '#monthlyRevenue', value: '10k-20k' });
await puppeteer_select({ selector: '#biggestChallenge', value: 'scaling' });
await puppeteer_click({ selector: '#privacy' });
await puppeteer_click({ selector: 'button[type="submit"]' });
// Wait for redirect to thank-you page
```
**Verify**:
- All fields populated
- Form submitted successfully
- Redirect to thank-you page

**Estimated Time**: 10 minutes

#### Task 13.3: Puppeteer - Complete 16-Question Assessment
**Use Puppeteer MCP**:
```javascript
// Navigate to assessment from thank-you page
await puppeteer_click({ selector: 'a[href*="/assessment"]' });

// Answer 16 questions (varied pattern)
for (let i = 0; i < 16; i++) {
  if (i % 3 === 0) {
    await puppeteer_click({ selector: 'button:has-text("YES")' });
  } else {
    await puppeteer_click({ selector: 'button:has-text("NO")' });
  }
  // Wait for animation
}
```
**Verify**:
- Progress bar advances
- Assessment completes
- Redirect to results page

**Estimated Time**: 15 minutes

#### Task 13.4: Verify Webhook Triggers PRODUCTION Prefect
**Check Prefect API**:
```bash
PREFECT_API_URL=https://prefect.galatek.dev/api prefect flow-run ls --limit 5
```
**Verify**:
- New flow run created after assessment completion
- Flow run status: RUNNING -> COMPLETED
- Record flow run ID

**Estimated Time**: 10 minutes

#### Task 13.5: Verify All 7 Lead Nurture Emails Scheduled
**Check Prefect for scheduled emails**:
```bash
PREFECT_API_URL=https://prefect.galatek.dev/api prefect flow-run ls \
  --flow-name christmas-send-email \
  --limit 10
```
**Expected (TESTING_MODE=true)**:
- Email 1: Sent immediately
- Emails 2-7: Sent at 1-minute intervals
- Total sequence: ~6 minutes

**Estimated Time**: 15 minutes

#### Task 13.6: Verify Lead Nurture Emails Delivered via Resend API
**Query Resend API**:
```bash
cd /Users/sangle/Dev/action/projects/perfect && \
source .env && \
python3 -c "
import resend
import os
resend.api_key = os.getenv('RESEND_API_KEY')

emails = resend.Emails.list()
target = 'lengobaosang@gmail.com'
count = 0
for email in emails.data[:20]:
    if email.to and target in str(email.to):
        count += 1
        print(f'{count}. {email.subject[:50]} - {email.status}')
print(f'\\nLead Nurture emails: {count}/7')
"
```
**Verify**:
- All 7 emails delivered
- Check status: sent/delivered/opened

**Estimated Time**: 10 minutes

#### Task 13.7: Verify Updated Templates with New Variables
**Manual verification in inbox (lengobaosang@gmail.com)**:
1. Open emails from Wave 13 test
2. Check new automation variables:
   - {{q1_foundation_deadline}} -> "December 15, 2025"
   - {{days_to_q1_deadline}} -> Correct countdown number
   - {{slots_remaining}} -> Number (10 or less)
   - {{spots_taken}} -> Number
3. Check testimonials:
   - Van Tiny, Hera Nguyen, Loc Diem appear
   - No Jennifer K, Sarah P, Linh, Marcus Chen

**Estimated Time**: 15 minutes

#### Task 13.8: Test No-Show Recovery Sequence (3 emails)
**Trigger webhook**:
```bash
curl -X POST https://sangletech.com/api/webhook/calendly-noshow \
  -H "Content-Type: application/json" \
  -d '{
    "email": "lengobaosang@gmail.com",
    "first_name": "Wave13 Test",
    "business_name": "Test Salon",
    "event_name": "BusinessX Discovery Call",
    "event_uri": "https://calendly.com/test/wave13"
  }'
```
**Verify**:
- Prefect flow triggered
- 3 emails scheduled
- All 3 delivered (~3 min with TESTING_MODE)

**Estimated Time**: 10 minutes

#### Task 13.9: Test Post-Call Maybe Sequence (3 emails)
**Trigger webhook**:
```bash
curl -X POST https://sangletech.com/api/webhook/postcall-maybe \
  -H "Content-Type: application/json" \
  -d '{
    "email": "lengobaosang@gmail.com",
    "first_name": "Wave13 Test",
    "business_name": "Test Salon",
    "call_date": "2025-11-27",
    "call_notes": "Interested but needs to think",
    "objections": ["price", "timing"]
  }'
```
**Verify**:
- Prefect flow triggered
- 3 emails scheduled
- All 3 delivered

**Estimated Time**: 10 minutes

#### Task 13.10: Test Onboarding Sequence (3 emails)
**Trigger webhook**:
```bash
curl -X POST https://sangletech.com/api/webhook/onboarding-start \
  -H "Content-Type: application/json" \
  -d '{
    "email": "lengobaosang@gmail.com",
    "first_name": "Wave13 Test",
    "business_name": "Test Salon",
    "client_since": "2025-11-27"
  }'
```
**Verify**:
- Prefect flow triggered
- 3 emails scheduled
- All 3 delivered

**Estimated Time**: 10 minutes

#### Task 13.11: Production Readiness Final Verification
**Complete verification checklist**:

| Check | Status | Notes |
|-------|--------|-------|
| Total 16 emails sent to test inbox | [ ] | |
| Lead Nurture: 7 emails verified | [ ] | |
| No-Show Recovery: 3 emails verified | [ ] | |
| Post-Call Maybe: 3 emails verified | [ ] | |
| Onboarding: 3 emails verified | [ ] | |
| New template variables render correctly | [ ] | |
| Real testimonials displayed | [ ] | |
| No fabricated testimonials | [ ] | |
| **PRODUCTION READY FOR LIVE ADS** | [ ] | |

**Estimated Time**: 15 minutes

### 13.5 Email Sequence Summary

| Sequence | Email Count | Trigger | Variables to Verify |
|----------|-------------|---------|---------------------|
| Lead Nurture | 7 | Website funnel | All new variables |
| No-Show Recovery | 3 | /webhook/calendly-noshow | testimonials |
| Post-Call Maybe | 3 | /webhook/postcall-maybe | Van Tiny (email 2) |
| Onboarding | 3 | /webhook/onboarding-start | testimonials |
| **TOTAL** | **16** | | |

### 13.6 New Template Variables to Verify

| Variable | Expected Value |
|----------|---------------|
| {{q1_foundation_deadline}} | December 15, 2025 |
| {{days_to_q1_deadline}} | Dynamic countdown |
| {{slots_remaining}} | 10 or less |
| {{spots_taken}} | 0 or more |

### 13.7 Expected Outcomes
- Complete E2E funnel passes on PRODUCTION site (sangletech.com)
- Webhook triggers PRODUCTION Prefect (prefect.galatek.dev)
- All 16 emails sent and delivered to lengobaosang@gmail.com
- New template variables render correctly
- Real testimonials display (Van Tiny, Hera Nguyen, Loc Diem)
- No fabricated testimonials present
- **PRODUCTION READY FOR LIVE AD TRAFFIC**

### 13.8 Total Estimated Time
- Navigate + opt-in form: 15 minutes
- Complete assessment: 15 minutes
- Webhook verification: 10 minutes
- Lead Nurture sequence: 25 minutes (15 + 10)
- Template variable verification: 15 minutes
- No-Show Recovery sequence: 10 minutes
- Post-Call Maybe sequence: 10 minutes
- Onboarding sequence: 10 minutes
- Final verification: 15 minutes
- **Total Wave 13**: ~2 hours

---

## Wave 14: Production Launch Verification (Worker Capacity + Full E2E Retest) (ADDED)

### 14.1 Objective
Verify Prefect worker capacity for 50-100 concurrent signups, confirm workers are healthy on production Prefect (prefect.galatek.dev), perform full E2E retest on PRODUCTION site (sangletech.com) after uvloop fix, and complete final pre-launch checklist.

### 14.2 Context
**uvloop Fix Applied**: Python 3.12 + uvloop crash resolved (commit ac65816 via Coolify rebuild)
**Verified Flow Run**: b58af269-bdd0-477c-8edd-6ee53f174711 COMPLETED
**Expected Traffic**: 50-100 concurrent signups from advertisement launch
**Minimum Workers Required**: 3 (for 50-100 concurrent capacity)

### 14.3 Pre-Conditions
- Production site live at https://sangletech.com
- Prefect workers running at https://prefect.galatek.dev
- uvloop fix applied and deployed via Coolify
- Test email: lengobaosang@gmail.com

### 14.4 Tasks

#### Task 14.1: Verify Prefect Worker Count and Capacity (3+ Workers for 50-100 Concurrent Flows)
**Command**:
```bash
PREFECT_API_URL=https://prefect.galatek.dev/api prefect work-pool ls
```
**Expected**:
- At least 3 workers active
- Each worker can handle 10-20 concurrent flows
- Total capacity: 50-100+ concurrent signups

**Test Scenarios**:
- [ ] Query Prefect API for worker count
- [ ] Verify at least 3 workers are active and healthy
- [ ] Check worker CPU/memory capacity via Prefect dashboard
- [ ] Calculate concurrent flow capacity
- [ ] Verify 50-100 concurrent signups can be handled

**Estimated Time**: 10 minutes

#### Task 14.2: Verify Workers Are Healthy and Connected to Production Prefect
**Commands**:
```bash
# Check work pool status
PREFECT_API_URL=https://prefect.galatek.dev/api prefect work-pool ls

# List workers in default pool
PREFECT_API_URL=https://prefect.galatek.dev/api python3 -c "
from prefect.client.orchestration import get_client
import asyncio

async def check_workers():
    async with get_client() as client:
        pools = await client.read_work_pools()
        for pool in pools:
            print(f'Pool: {pool.name}')
            print(f'  Status: {pool.status}')
            print(f'  Workers: Check Prefect dashboard')

asyncio.run(check_workers())
"
```
**Expected**:
- All workers show 'online' or 'running' status
- Workers heartbeat within last 60 seconds
- No worker errors in logs

**Test Scenarios**:
- [ ] Check worker status via Prefect API
- [ ] Verify all workers show 'online' or 'running' status
- [ ] Confirm workers last heartbeat within last 60 seconds
- [ ] Test worker health with a simple ping flow run
- [ ] Verify no worker errors in Prefect logs

**Estimated Time**: 10 minutes

#### Task 14.3: Test Concurrent Flow Capacity (Run Multiple Test Flows Simultaneously)
**Command**:
```bash
# Trigger 5 concurrent flows
for i in {1..5}; do
  curl -X POST https://prefect.galatek.dev/api/deployments/<deployment-id>/create_flow_run \
    -H "Content-Type: application/json" \
    -d '{
      "name": "concurrent-test-'$i'-'$(date +%s)'",
      "parameters": {
        "email": "test'$i'@example.com",
        "first_name": "Concurrent Test '$i'"
      }
    }' &
done
wait

# Monitor all flows
PREFECT_API_URL=https://prefect.galatek.dev/api prefect flow-run ls --limit 10
```
**Expected**:
- All 5 flows start within 30 seconds
- No failures due to worker capacity
- Workers distribute load evenly

**Test Scenarios**:
- [ ] Trigger 5 concurrent christmas-signup-handler flows
- [ ] Monitor all 5 flows start within 30 seconds
- [ ] Verify no flow run failures due to worker capacity
- [ ] Monitor worker load distribution across all workers
- [ ] Document peak concurrent flow handling

**Estimated Time**: 15 minutes

#### Task 14.4: Full E2E Puppeteer Test on PRODUCTION Site (sangletech.com)
**Use Puppeteer MCP**:
```javascript
// Navigate to PRODUCTION site
await puppeteer_navigate({ url: 'https://sangletech.com/en/flows/businessX/dfu/xmas-a01' });
await puppeteer_screenshot({ name: 'wave14-landing-page' });

// Fill opt-in form
await puppeteer_fill({ selector: '#firstName', value: 'Wave14 Test' });
await puppeteer_fill({ selector: '#email', value: 'lengobaosang@gmail.com' });
await puppeteer_select({ selector: '#monthlyRevenue', value: '10k-20k' });
await puppeteer_select({ selector: '#biggestChallenge', value: 'no-shows' });
await puppeteer_click({ selector: '#privacy' });
await puppeteer_click({ selector: 'button[type="submit"]' });

// Complete 16-question assessment
// ... (answer all questions)

// Verify results page
await puppeteer_screenshot({ name: 'wave14-results-page' });
```
**Expected**:
- Complete funnel works on production
- Webhook triggers Prefect flow
- Results page displays correctly

**Test Scenarios**:
- [ ] Navigate to https://sangletech.com/en/flows/businessX/dfu/xmas-a01 via Puppeteer MCP
- [ ] Fill opt-in form with unique test email (timestamp-based)
- [ ] Complete 16-question assessment
- [ ] Verify redirect to results page
- [ ] Screenshot evidence of successful completion

**Estimated Time**: 20 minutes

#### Task 14.5: Verify Webhook Triggers Production Prefect Flows (All 4 Endpoints)
**Commands**:
```bash
# Test Lead Nurture (7 emails)
curl -X POST http://localhost:8000/webhook/christmas-signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "lengobaosang@gmail.com",
    "first_name": "Wave14 Test",
    "business_name": "Test Salon",
    "red_systems": 2
  }'

# Test No-Show Recovery (3 emails)
curl -X POST http://localhost:8000/webhook/calendly-noshow \
  -H "Content-Type: application/json" \
  -d '{
    "email": "lengobaosang@gmail.com",
    "first_name": "Wave14 Test",
    "event_uri": "https://calendly.com/test/wave14"
  }'

# Test Post-Call Maybe (3 emails)
curl -X POST http://localhost:8000/webhook/postcall-maybe \
  -H "Content-Type: application/json" \
  -d '{
    "email": "lengobaosang@gmail.com",
    "first_name": "Wave14 Test",
    "call_date": "2025-11-27"
  }'

# Test Onboarding (3 emails)
curl -X POST http://localhost:8000/webhook/onboarding-start \
  -H "Content-Type: application/json" \
  -d '{
    "email": "lengobaosang@gmail.com",
    "first_name": "Wave14 Test",
    "client_since": "2025-11-27"
  }'

# Verify all flows created
PREFECT_API_URL=https://prefect.galatek.dev/api prefect flow-run ls --limit 10
```
**Expected**:
- Each webhook creates a flow run on prefect.galatek.dev
- All 4 deployments triggered correctly

**Test Scenarios**:
- [ ] Test /webhook/christmas-signup - Lead Nurture (7 emails)
- [ ] Test /webhook/calendly-noshow - No-Show Recovery (3 emails)
- [ ] Test /webhook/postcall-maybe - Post-Call Maybe (3 emails)
- [ ] Test /webhook/onboarding-start - Onboarding (3 emails)
- [ ] Verify each webhook creates flow run on prefect.galatek.dev
- [ ] Record flow run IDs for all 4 sequences

**Estimated Time**: 20 minutes

#### Task 14.6: Verify All 4 Email Sequences Work with Production Workers (16 Emails Total)
**Command**:
```bash
cd /Users/sangle/Dev/action/projects/perfect && \
source .env && \
python3 -c "
import resend
import os
resend.api_key = os.getenv('RESEND_API_KEY')

emails = resend.Emails.list()
target = 'lengobaosang@gmail.com'
count = 0
for email in emails.data[:30]:
    if email.to and target in str(email.to):
        count += 1
        print(f'{count}. {email.subject[:50]} - {email.status}')

print(f'\\nTotal emails to {target}: {count}')
print(f'Expected: 16 (7 Lead + 3 NoShow + 3 PostCall + 3 Onboarding)')
"
```
**Expected**:
- All 16 emails sent and delivered
- All emails have 'delivered' or 'opened' status

**Test Scenarios**:
- [ ] Trigger Lead Nurture sequence (7 emails) - verify all 7 scheduled and sent
- [ ] Trigger No-Show Recovery sequence (3 emails) - verify all 3 scheduled and sent
- [ ] Trigger Post-Call Maybe sequence (3 emails) - verify all 3 scheduled and sent
- [ ] Trigger Onboarding sequence (3 emails) - verify all 3 scheduled and sent
- [ ] Query Resend API for all 16 emails to lengobaosang@gmail.com
- [ ] Verify all emails have 'delivered' or 'opened' status

**Estimated Time**: 30 minutes

#### Task 14.7: Final Production Launch Readiness Checklist
**Checklist**:

| Check | Status | Notes |
|-------|--------|-------|
| 3+ Prefect workers active and healthy | [ ] | |
| All workers connected to prefect.galatek.dev | [ ] | |
| Concurrent flow capacity verified (50-100 flows) | [ ] | |
| Production site (sangletech.com) fully functional | [ ] | |
| All 4 webhook endpoints trigger correct deployments | [ ] | |
| All 16 email templates work correctly | [ ] | |
| Resend API confirms email delivery | [ ] | |
| uvloop crash fix applied and verified | [ ] | |
| **READY FOR ADVERTISEMENT LAUNCH WITH 50-100 CONCURRENT SIGNUPS** | [ ] | |

**Test Scenarios**:
- [ ] 3+ Prefect workers active and healthy
- [ ] All workers connected to prefect.galatek.dev
- [ ] Concurrent flow capacity verified (50-100 flows)
- [ ] Production site (sangletech.com) fully functional
- [ ] All 4 webhook endpoints trigger correct deployments
- [ ] All 16 email templates work correctly
- [ ] Resend API confirms email delivery
- [ ] uvloop crash fix applied and verified
- [ ] READY FOR ADVERTISEMENT LAUNCH WITH 50-100 CONCURRENT SIGNUPS

**Estimated Time**: 15 minutes

### 14.5 Email Sequence Summary

| Sequence | Email Count | Trigger | Purpose |
|----------|-------------|---------|---------|
| Lead Nurture | 7 | Website funnel | New signup nurturing |
| No-Show Recovery | 3 | /webhook/calendly-noshow | Re-engage no-shows |
| Post-Call Maybe | 3 | /webhook/postcall-maybe | Follow up maybes |
| Onboarding | 3 | /webhook/onboarding-start | Welcome new clients |
| **TOTAL** | **16** | | |

### 14.6 Expected Outcomes
- 3+ Prefect workers verified active and healthy
- Workers connected to production Prefect (prefect.galatek.dev)
- Concurrent flow capacity verified for 50-100 signups
- Production site (sangletech.com) fully functional
- All 4 webhook endpoints trigger correct deployments
- All 16 emails sent and delivered via production workers
- uvloop crash fix confirmed working
- **READY FOR ADVERTISEMENT LAUNCH WITH 50-100 CONCURRENT SIGNUPS**

### 14.7 Total Estimated Time
- Worker count verification: 10 minutes
- Worker health check: 10 minutes
- Concurrent flow test: 15 minutes
- Full E2E Puppeteer test: 20 minutes
- Webhook endpoint tests: 20 minutes
- Email sequence verification: 30 minutes
- Final checklist: 15 minutes
- **Total Wave 14**: ~2 hours
