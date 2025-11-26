# DISCOVERY.md - E2E Christmas Campaign Email Sequence Test

**Task**: 1126-e2e-christmas-email-sequence-test
**Created**: 2025-11-26
**Domain**: CODING
**Test Email**: lengobaosang@gmail.com

---

## 1. Campaign Structure Analysis

### 1.1 Christmas Campaign Overview

**Location**: `/Users/sangle/Dev/action/projects/perfect/campaigns/christmas_campaign/`

**Campaign Status**: 100% Complete (per STATUS.md)
- Flows Developed: YES (2 flows)
- Git Repository: YES (https://github.com/galacoder/perfect.git)
- Prefect Deployments: YES (both flows deployed)
- Secret Blocks: YES (7 blocks created)
- End-to-End Testing: YES (verified on 2025-11-19)

### 1.2 Flow Architecture

```
Website Form (Assessment Completion)
    |
    v
POST /api/assessment/complete (Next.js API)
    |
    v
POST /webhook/christmas-signup (FastAPI) OR
POST https://prefect.galatek.dev/api/deployments/{id}/create_flow_run (Direct Prefect API)
    |
    v
christmas-signup-handler (Prefect Flow)
    |
    +-- Check Email Sequence DB (Idempotency)
    +-- Classify Segment (CRITICAL/URGENT/OPTIMIZE)
    +-- Search/Create Contact in BusinessX Canada DB
    +-- Create Email Sequence Record in Email Sequence DB
    +-- Schedule 7 Email Flow Runs via Prefect API
    |
    v
christmas-send-email (7x Prefect Flows - Scheduled)
    |
    +-- Email 1: Day 0 (immediate)
    +-- Email 2: Day 1 (+24h)
    +-- Email 3: Day 3 (+72h)
    +-- Email 4: Day 5 (+120h)
    +-- Email 5: Day 7 (+168h)
    +-- Email 6: Day 9 (+216h)
    +-- Email 7: Day 11 (+264h)
```

### 1.3 Key Files

| File | Purpose |
|------|---------|
| `flows/signup_handler.py` | Main entry flow - handles signup, creates records, schedules emails |
| `flows/send_email_flow.py` | Individual email send flow - fetches template, sends via Resend |
| `tasks/notion_operations.py` | Notion database CRUD operations |
| `tasks/resend_operations.py` | Resend API email sending |
| `tasks/routing.py` | Segment classification logic |

---

## 2. Flow Dependencies and Timing

### 2.1 Email Sequence Timing

**Production Mode** (`TESTING_MODE=false`):
| Email | Day | Delay (Hours) | Purpose |
|-------|-----|---------------|---------|
| 1 | 0 | 0 | Assessment Results |
| 2 | 1 | 24 | System Fix Framework |
| 3 | 3 | 72 | Horror Story (Sarah's story) |
| 4 | 5 | 120 | Diagnostic Booking Ask |
| 5 | 7 | 168 | Case Study (Min-Ji) |
| 6 | 9 | 216 | Christmas Readiness Checklist |
| 7 | 11 | 264 | Final Urgency |

**Testing Mode** (`TESTING_MODE=true`):
| Email | Delay |
|-------|-------|
| 1 | 0 min |
| 2 | 1 min |
| 3 | 2 min |
| 4 | 3 min |
| 5 | 4 min |
| 6 | 5 min |
| 7 | 6 min |

**Total Testing Time**: ~6-7 minutes for complete sequence

### 2.2 Segment Classification Logic

```python
def classify_segment(red_systems, orange_systems, yellow_systems, green_systems):
    if red_systems >= 2:
        return "CRITICAL"
    elif red_systems == 1 or orange_systems >= 2:
        return "URGENT"
    else:
        return "OPTIMIZE"
```

### 2.3 Template Routing

| Email # | CRITICAL | URGENT | OPTIMIZE |
|---------|----------|--------|----------|
| 1 | christmas_email_1 | christmas_email_1 | christmas_email_1 |
| 2 | christmas_email_2a_critical | christmas_email_2b_urgent | christmas_email_2c_optimize |
| 3-6 | christmas_email_{n} | christmas_email_{n} | christmas_email_{n} |
| 7 | christmas_email_7a_critical | christmas_email_7b_urgent | christmas_email_7c_optimize |

---

## 3. API Endpoints and Payloads

### 3.1 FastAPI Webhook (Local)

**Endpoint**: `POST http://localhost:8000/webhook/christmas-signup`

**Payload**:
```json
{
  "email": "lengobaosang@gmail.com",
  "first_name": "Bao Sang",
  "business_name": "Test Salon",
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
```

### 3.2 Direct Prefect API (Production)

**Christmas Signup Handler**:
- **Deployment ID**: `1ae3a3b3-e076-49c5-9b08-9c176aa47aa0`
- **Endpoint**: `POST https://prefect.galatek.dev/api/deployments/1ae3a3b3-e076-49c5-9b08-9c176aa47aa0/create_flow_run`

**Christmas Send Email**:
- **Deployment ID**: `5445a75a-ae20-4d65-8120-7237e68ae0d5`

**Payload Format**:
```json
{
  "name": "christmas-signup-{timestamp}",
  "parameters": {
    "email": "lengobaosang@gmail.com",
    "first_name": "Bao Sang",
    "business_name": "Test Salon",
    "assessment_score": 52,
    "red_systems": 2,
    "orange_systems": 1,
    "yellow_systems": 2,
    "green_systems": 3
  }
}
```

### 3.3 Prefect Secret Blocks

| Block Name | Purpose |
|------------|---------|
| `notion-token` | Notion integration auth |
| `notion-email-templates-db-id` | Email templates database |
| `notion-email-sequence-db-id` | Email sequence tracking |
| `notion-businessx-db-id` | BusinessX Canada contacts |
| `notion-customer-projects-db-id` | Customer portal pages |
| `notion-email-analytics-db-id` | Email analytics tracking |
| `resend-api-key` | Resend email sending |

---

## 4. Current Test Coverage Status

### 4.1 Existing E2E Tests

**Location**: `/Users/sangle/Dev/action/projects/perfect/tests/e2e/`

| Test File | Coverage |
|-----------|----------|
| `test_sales_funnel_e2e.py` | Infrastructure validation (FastAPI health) |
| `test_webhook_integration.py` | Webhook endpoint tests |
| `test_notion_verification.py` | Notion database verification |
| `test_notion_mocked.py` | Mocked Notion operations |
| `test_routing_unit.py` | Segment routing logic |
| `test_models_unit.py` | Data model validation |
| `test_resend_unit.py` | Resend operations |

### 4.2 Christmas Campaign Tests

| Test File | Coverage |
|-----------|----------|
| `tests/test_seed_email_templates.py` | Template seeding (10 tests) |
| `tests/test_signup_handler.py` | Signup flow tests |
| `tests/test_routing.py` | Christmas routing logic |
| `tests/test_precall_prep_dry_run.py` | Pre-call prep flow |

### 4.3 Test Coverage Gaps

- [x] Unit tests for Notion operations (96% coverage achieved)
- [ ] **REAL E2E test with actual email delivery** (THIS TASK)
- [ ] Full funnel test from website form to final email
- [ ] Multi-segment testing (CRITICAL/URGENT/OPTIMIZE)
- [ ] Email content verification
- [ ] Notion database state verification

---

## 5. Website Form Integration Analysis

### 5.1 Website Source Path

**Location**: `/Users/sangle/Dev/action/projects/@new-websites/sangletech-tailwindcss/pages/en/flows/businessX/dfu/xmas-a01/`

### 5.2 Assessment Flow

1. **Landing Page** (`index.tsx`) - Captures email, name, business name
2. **Assessment Page** (`assessment.tsx`) - 16 yes/no questions
3. **Results Display** - Shows scores and broken systems
4. **Diagnostic Page** (`diagnostic.tsx`) - CTA for discovery call

### 5.3 Webhook Trigger Point

**File**: `assessment.tsx` (lines 143-197)

```javascript
// Trigger Christmas campaign webhook (async - don't block UI)
await fetch('/api/assessment/complete', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email,
    firstName,
    lastName,
    businessName,
    scores: { gps, money, marketing },
    totalRevenueLeak,
    weakestSystem1,
    weakestSystem2,
    timestamp: new Date().toISOString()
  })
});
```

### 5.4 Data Flow from Website

```
localStorage (xmas-user-email, xmas-user-name, xmas-business-name)
    |
    v
Assessment Completion (16 questions answered)
    |
    v
/api/assessment/complete (Next.js API route)
    |
    v
Prefect API (create_flow_run) OR
/webhook/christmas-signup (FastAPI)
    |
    v
signup_handler_flow -> 7 email sequence
```

---

## 6. Key Risks and Mitigations

### 6.1 Identified Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Email deliverability issues | HIGH | Use verified email (lengobaosang@gmail.com), check spam |
| Notion rate limits | MEDIUM | Test with single contact first |
| Prefect worker downtime | MEDIUM | Verify worker status before testing |
| Template rendering errors | LOW | Pre-verify templates exist in Notion |
| Duplicate email sequences | LOW | Idempotency built into flow |

### 6.2 Pre-Test Verification Checklist

- [ ] Prefect worker is running (check https://prefect.galatek.dev)
- [ ] Secret blocks are accessible
- [ ] Email templates exist in Notion
- [ ] No existing sequence for test email
- [ ] TESTING_MODE environment verified

---

## 7. Dependencies

### 7.1 External Services

| Service | Purpose | Verification |
|---------|---------|--------------|
| Prefect (prefect.galatek.dev) | Flow orchestration | Worker status check |
| Notion | Database operations | API connectivity test |
| Resend | Email delivery | API key validation |

### 7.2 Python Dependencies

```
prefect>=3.4.1
notion-client>=2.0.0
resend>=0.5.0
httpx>=0.24.0
python-dotenv>=1.0.0
```

### 7.3 Environment Variables

**Required for Local Testing**:
```bash
NOTION_TOKEN=secret_xxx
NOTION_EMAIL_TEMPLATES_DB_ID=xxx
NOTION_EMAIL_SEQUENCE_DB_ID=xxx
NOTION_BUSINESSX_DB_ID=xxx
RESEND_API_KEY=re_xxx
TESTING_MODE=true  # For fast execution
```

---

## 8. Existing Test Results Summary

### 8.1 Last E2E Test (2025-11-19)

**Flow Run ID**: `c6a18968-ad3b-4c69-a116-0b2935341367`
**Flow Run Name**: `functional-camel`
**Result**: SUCCESS

**Verified**:
- Git clone from GitHub
- All 7 Secret blocks loaded
- Notion database access
- Email sequence record created
- 7 emails scheduled with correct timing

**Test Data**:
- Email: `final.test@example.com`
- Segment: CRITICAL
- Assessment Score: 52

### 8.2 Unit Test Results

```
pytest campaigns/christmas_campaign/tests/ -v
=====================================================
93 tests passed (100%)
Coverage: 88%
=====================================================
```

---

## 9. Test Approach Recommendation

### 9.1 Testing Strategy

1. **Phase 1: Verification** - Confirm all infrastructure is ready
2. **Phase 2: TESTING_MODE Test** - Fast execution (~7 min) with real emails
3. **Phase 3: Production Mode Validation** - Optional, verify timing delays
4. **Phase 4: Multi-Segment Test** - Test all 3 segments if time permits

### 9.2 Test Data for lengobaosang@gmail.com

**CRITICAL Segment** (Primary Test):
```json
{
  "email": "lengobaosang@gmail.com",
  "first_name": "Bao Sang",
  "business_name": "Test Salon E2E",
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
```

---

## 10. Next Steps

1. Create PLAN.md with detailed wave structure
2. Create CHECKPOINT_SUMMARY.md with go/no-go criteria
3. Execute Wave 1: Infrastructure verification
4. Execute Wave 2-4: Full E2E testing
5. Document results and any issues found
