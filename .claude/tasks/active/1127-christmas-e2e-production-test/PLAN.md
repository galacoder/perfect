# Plan: Christmas Campaign E2E Production Test

**Task ID**: 1127-christmas-e2e-production-test
**Domain**: CODING
**Source**: feature_list.json

---

## Wave 1: Pre-flight Checks
**Objective**: Verify production environment is ready for E2E testing
**Status**: Pending

### Tasks
- [ ] 1.1: Verify Prefect server connectivity
- [ ] 1.2: Verify TESTING_MODE is enabled
- [ ] 1.3: Check worker pool status
- [ ] 1.4: Verify deployment exists

### Success Criteria
- [ ] Prefect API responds to health check
- [ ] TESTING_MODE Secret block = true
- [ ] Default work pool has active workers
- [ ] Deployment ID 1ae3a3b3-e076-49c5-9b08-9c176aa47aa0 exists

### Commands
```bash
# Check Prefect API
curl https://prefect.galatek.dev/api/health

# Verify deployment exists
PREFECT_API_URL=https://prefect.galatek.dev/api prefect deployment inspect christmas-signup-handler/christmas-signup-handler
```

---

## Wave 2: Funnel Navigation & Form Submission
**Objective**: Use Puppeteer to navigate production funnel and submit form
**Status**: Pending

### Tasks
- [ ] 2.1: Navigate to production funnel
- [ ] 2.2: Fill signup form
- [ ] 2.3: Accept privacy checkbox
- [ ] 2.4: Submit form and capture response
- [ ] 2.5: Complete assessment (if multi-step)

### Puppeteer Actions

```javascript
// 2.1: Navigate
await page.goto('https://sangletech.com/en/flows/businessX/dfu/xmas-a01');

// 2.2: Fill form
await page.fill('#firstName', 'E2E Test');
await page.fill('#email', 'lengobaosang@gmail.com');
await page.select('#monthlyRevenue', '20k-50k');
await page.select('#biggestChallenge', 'systems');

// 2.3: Accept privacy
await page.click('#privacy');

// 2.4: Submit
await page.click('button[type="submit"]');
await page.waitForNavigation();
```

### Success Criteria
- [ ] Page loads without errors
- [ ] All form fields filled correctly
- [ ] Form submits without validation errors
- [ ] Navigates to assessment or confirmation page

---

## Wave 3: Christmas Signup Flow Verification
**Objective**: Verify signup webhook triggers Prefect flow and schedules emails
**Status**: Pending

### Tasks
- [ ] 3.1: Trigger christmas-signup webhook directly
- [ ] 3.2: Verify flow run created
- [ ] 3.3: Verify Email Sequence record in Notion
- [ ] 3.4: Verify 7 scheduled email flow runs

### Webhook Payload

```json
{
  "name": "e2e-test-1127",
  "parameters": {
    "email": "lengobaosang@gmail.com",
    "first_name": "E2E Test",
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
}
```

### Commands

```bash
# Trigger webhook
curl -X POST https://prefect.galatek.dev/api/deployments/1ae3a3b3-e076-49c5-9b08-9c176aa47aa0/create_flow_run \
  -H "Content-Type: application/json" \
  -d '{...payload...}'
```

### Success Criteria
- [ ] Flow run created with state PENDING/RUNNING
- [ ] Flow run ID returned in response
- [ ] Email Sequence record appears in Notion
- [ ] 7 scheduled flow runs visible in Prefect UI

---

## Wave 4: Email Delivery Verification
**Objective**: Wait for email sequence and verify delivery
**Status**: Pending

### Tasks
- [ ] 4.1: Wait for email sequence (7 minutes)
- [ ] 4.2: Verify Email 1 sent timestamp in Notion
- [ ] 4.3: Verify all 7 flow runs completed
- [ ] 4.4: Check Resend delivery status (optional)

### Timeline (TESTING_MODE)

| Email | Wait Time | Cumulative |
|-------|-----------|------------|
| 1 | 0 min | 0 min |
| 2 | 1 min | 1 min |
| 3 | 2 min | 3 min |
| 4 | 3 min | 6 min |
| 5 | 4 min | 10 min |
| 6 | 5 min | 15 min |
| 7 | 6 min | 21 min |

**Note**: Actual total ~6-7 minutes as emails are scheduled from start.

### Success Criteria
- [ ] All 7 email flow runs show state: Completed
- [ ] No flow runs show state: Failed
- [ ] Email sent timestamps populated in Notion
- [ ] Emails received at lengobaosang@gmail.com

---

## Wave 5: Traditional Service Webhooks
**Objective**: Test no-show, post-call, and onboarding webhook flows
**Status**: Pending

### Tasks
- [ ] 5.1: Test calendly-noshow webhook
- [ ] 5.2: Test postcall-maybe webhook
- [ ] 5.3: Test onboarding-start webhook
- [ ] 5.4: Verify all Traditional Service flows completed

### No-Show Webhook

```bash
curl -X POST http://localhost:8000/webhook/calendly-noshow \
  -H "Content-Type: application/json" \
  -d '{
    "email": "lengobaosang@gmail.com",
    "first_name": "E2E Test",
    "business_name": "Test Salon E2E",
    "calendly_event_uri": "https://calendly.com/events/E2E-TEST-123",
    "scheduled_time": "2025-11-27T14:00:00Z",
    "reschedule_url": "https://calendly.com/reschedule/E2E-TEST-123"
  }'
```

### Post-Call Webhook

```bash
curl -X POST http://localhost:8000/webhook/postcall-maybe \
  -H "Content-Type: application/json" \
  -d '{
    "email": "lengobaosang@gmail.com",
    "first_name": "E2E Test",
    "business_name": "Test Salon E2E",
    "call_date": "2025-11-27T14:30:00Z",
    "call_outcome": "Maybe",
    "call_notes": "E2E Test",
    "objections": ["Price"],
    "follow_up_priority": "High"
  }'
```

### Onboarding Webhook

```bash
curl -X POST http://localhost:8000/webhook/onboarding-start \
  -H "Content-Type: application/json" \
  -d '{
    "email": "lengobaosang@gmail.com",
    "first_name": "E2E Test",
    "business_name": "Test Salon E2E",
    "payment_confirmed": true,
    "payment_amount": 2997.00,
    "payment_date": "2025-11-27T15:00:00Z",
    "docusign_completed": true
  }'
```

### Success Criteria
- [ ] No-show flow creates 3 scheduled email runs
- [ ] Post-call flow creates 3 scheduled email runs
- [ ] Onboarding flow creates 3 scheduled email runs
- [ ] All 9 Traditional Service emails complete within 5 minutes

---

## Summary

| Wave | Features | Priority | Est. Time |
|------|----------|----------|-----------|
| 1 | 4 | High | 5 min |
| 2 | 5 | High | 10 min |
| 3 | 4 | High | 5 min |
| 4 | 4 | High | 10 min |
| 5 | 4 | Medium | 10 min |

**Total Features**: 20
**Total Estimated Time**: ~40 minutes
**Total Emails Triggered**: 16 (7 + 3 + 3 + 3)

---

## Risk Mitigation

### Known Issues
1. **asyncio Python 3.12**: May cause Email 1 to fail occasionally
   - **Mitigation**: Check flow logs, retry if needed

2. **Template not in Notion**: Flow will fail with clear error
   - **Mitigation**: Verify templates exist before testing

3. **Duplicate sequences**: Idempotency prevents duplicates
   - **Mitigation**: Use unique test run identifier or clear previous test data

### Rollback Plan
- No production data is modified (only test email used)
- All test records identifiable by email: lengobaosang@gmail.com
- Can be manually deleted from Notion if needed

---

**Next Step**: Run `/execute` to begin Wave 1
