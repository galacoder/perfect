# Plan: E2E Puppeteer Sales Funnel Email Verification

**Task ID**: 1127-e2e-puppeteer-sales-funnel-email-verification
**Domain**: CODING
**Source**: feature_list.json

---

## Overview

End-to-end test using Puppeteer MCP to:
1. Navigate through the sangletech.com sales funnel
2. Complete the BusOS assessment (CRITICAL segment)
3. Verify webhook triggers Christmas campaign flow
4. Confirm all 7 emails delivered to lengobaosang@gmail.com within 10 minutes

---

## Wave 1: Pre-Test Setup

**Objective**: Prepare environment by deleting existing sequence and verifying TESTING_MODE

**Status**: Pending

### Tasks

- [ ] 1.1: Delete existing email sequence for lengobaosang@gmail.com from Notion
  - Query Notion Email Sequence database (ID: 576de1aa-6064-4201-a5e6-623b7f2be79a)
  - Delete any existing record for test email
  - This bypasses the idempotency check in signup_handler_flow

- [ ] 1.2: Verify TESTING_MODE=true in Prefect Secret block
  - Confirm `testing-mode` Secret block is set to `true`
  - This ensures emails send at 1-minute intervals (not days)

- [ ] 1.3: Verify FastAPI server is running with correct endpoints
  - Start server: `uvicorn server:app --reload`
  - Health check: `curl http://localhost:8000/health`
  - Verify `/webhook/christmas-signup` endpoint available

### Success Criteria

- [ ] No existing sequence record for lengobaosang@gmail.com
- [ ] TESTING_MODE confirmed as true
- [ ] FastAPI server responding to health checks

---

## Wave 2: Puppeteer Browser Automation

**Objective**: Navigate sales funnel, fill forms, complete assessment, capture screenshots

**Status**: Pending

### Tasks

- [ ] 2.1: Navigate to sales funnel landing page
  ```
  URL: https://sangletech.com/en/flows/businessX/dfu/xmas-a01
  ```
  - Use `puppeteer_navigate` MCP tool
  - Capture landing page screenshot
  - Verify page loads without errors

- [ ] 2.2: Fill opt-in form with test email
  ```json
  {
    "first_name": "Sang",
    "email": "lengobaosang@gmail.com",
    "business_name": "E2E Test Salon"
  }
  ```
  - Use `puppeteer_fill` for each form field
  - Click submit button
  - Capture screenshot of filled form

- [ ] 2.3: Complete 16-question BusOS assessment with CRITICAL segment answers
  - Answer all 16 questions
  - Target: 2+ red systems (CRITICAL segment)
  - Use `puppeteer_click` for answer selection
  - Capture screenshots at questions 1, 8, 16
  - Submit assessment

- [ ] 2.4: Verify results page displayed with correct segment
  - Wait for results page to load
  - Verify BusOS score displayed
  - Verify CRITICAL segment shown
  - Capture final results screenshot

### Success Criteria

- [ ] All screenshots captured (landing, form, assessment, results)
- [ ] Assessment completed successfully
- [ ] CRITICAL segment achieved (2+ red systems)
- [ ] Results page displays score and segment

---

## Wave 3: Webhook & Flow Verification

**Objective**: Verify webhook triggers Prefect flow and email sequence is created

**Status**: Pending

### Tasks

- [ ] 3.1: Verify webhook triggered to /webhook/christmas-signup
  - Option A: Website automatically sends webhook after assessment
  - Option B: Manually trigger via FastAPI endpoint:
    ```bash
    curl -X POST http://localhost:8000/webhook/christmas-signup \
      -H "Content-Type: application/json" \
      -d '{
        "email": "lengobaosang@gmail.com",
        "first_name": "Sang",
        "business_name": "E2E Test Salon",
        "assessment_score": 35,
        "red_systems": 3,
        "orange_systems": 1,
        "yellow_systems": 2,
        "green_systems": 2
      }'
    ```
  - Verify response: `{"status": "accepted", "campaign": "Christmas 2025"}`

- [ ] 3.2: Verify Prefect flow run created
  - Query Prefect API for recent flow runs
  - Find `christmas-signup-handler` flow run
  - Verify status is COMPLETED or RUNNING

- [ ] 3.3: Verify email sequence record created in Notion
  - Query Notion Email Sequence database
  - Find record for lengobaosang@gmail.com
  - Verify:
    - Campaign = "Christmas 2025"
    - Segment = "CRITICAL"
    - 7 email flow runs scheduled

### Success Criteria

- [ ] Webhook accepted (status 200)
- [ ] Prefect flow run created and completed
- [ ] Notion sequence record exists with correct segment

---

## Wave 4: Email Delivery Verification

**Objective**: Monitor and verify all 7 emails delivered to test inbox

**Status**: Pending

### Tasks

- [ ] 4.1: Wait for Email 1 (immediate) and verify delivery
  - Email 1 sends immediately (0 minutes)
  - Check Notion for "Email 1 Sent" timestamp
  - Verify in Resend delivery logs
  - Expected subject: Assessment results email

- [ ] 4.2: Monitor Emails 2-7 delivery over 6 minutes
  - Email timing (TESTING_MODE=true):
    | Email | Delay | Expected Time |
    |-------|-------|---------------|
    | 1 | 0 min | Immediate |
    | 2 | 1 min | +1 minute |
    | 3 | 2 min | +2 minutes |
    | 4 | 3 min | +3 minutes |
    | 5 | 4 min | +4 minutes |
    | 6 | 5 min | +5 minutes |
    | 7 | 6 min | +6 minutes |
  - Poll Notion every minute for "Email N Sent" timestamps
  - Check Resend dashboard for delivery confirmations

- [ ] 4.3: Verify all 7 emails received in test inbox
  - Check lengobaosang@gmail.com inbox
  - Verify all 7 emails present
  - Check spam/junk folder if needed
  - Verify email content matches templates

- [ ] 4.4: Generate E2E test report with screenshots and timing
  - Compile all screenshots into report
  - Document email delivery timeline
  - Record pass/fail for each verification step
  - Save to `campaigns/christmas_campaign/tests/e2e/results/`

### Success Criteria

- [ ] All 7 emails delivered within 10 minutes
- [ ] Notion records show all "Email N Sent" timestamps
- [ ] All emails visible in test inbox
- [ ] Test report generated with evidence

---

## Implementation Notes

### Puppeteer MCP Usage

```javascript
// Example MCP tool calls:
mcp__puppeteer__puppeteer_navigate({ url: "https://sangletech.com/en/flows/businessX/dfu/xmas-a01" })
mcp__puppeteer__puppeteer_fill({ selector: "input[name='email']", value: "lengobaosang@gmail.com" })
mcp__puppeteer__puppeteer_click({ selector: "button[type='submit']" })
mcp__puppeteer__puppeteer_screenshot({ name: "results-page" })
```

### Notion API Pattern

```python
# Delete existing sequence (uses notion-integration skill pattern)
from prefect.blocks.system import Secret

async def delete_sequence_for_email(email: str):
    notion_token = Secret.load("notion-token").get()
    db_id = Secret.load("notion-email-sequence-db-id").get()
    # Query and delete record
```

### Email Timing Verification

```python
# In TESTING_MODE=true:
delays_hours = [0, 1/60, 2/60, 3/60, 4/60, 5/60, 6/60]  # Minutes as hours
# Total: ~6-7 minutes for all 7 emails
```

---

## Risk Mitigation

| Risk | Mitigation | Priority |
|------|------------|----------|
| Idempotency blocks test | Delete existing sequence FIRST | Critical |
| Website form changed | Use flexible selectors, take screenshots | High |
| Email delivery delayed | Allow 10+ minutes, check Resend logs | High |
| Puppeteer timeout | Set extended timeouts (60s) | Medium |

---

## Estimated Timeline

| Wave | Time | Cumulative |
|------|------|------------|
| Wave 1: Setup | 15 min | 15 min |
| Wave 2: Browser | 30 min | 45 min |
| Wave 3: Webhook | 20 min | 65 min |
| Wave 4: Email | 45 min | 110 min |

**Total Estimated Time**: ~2 hours

---

## Next Steps

After approval:
1. Run `/execute-coding` to begin Wave 1
2. Execute tasks sequentially within each wave
3. Capture screenshots and evidence at each step
4. Complete Wave 4 with email delivery verification
5. Run `/verify-coding` to validate completion

---

**Plan Created**: 2025-11-27
**Status**: AWAITING_APPROVAL
