# Puppeteer E2E Manual Test: Assessment Sales Funnel

**Test ID**: Feature 4.7
**Test Email**: lengobaosang@gmail.com
**Production URL**: https://sangletech.com/en/flows/businessX/dfu/xmas-a01

## Prerequisites

1. Kestra running at https://kestra.galatek.dev
2. Notion databases configured with test email cleanup
3. Resend API accessible
4. Puppeteer MCP tools available

## Test Cases

### TC-4.7.1: Navigate to Funnel URL

**Steps**:
1. Use `mcp__puppeteer__puppeteer_navigate` to load funnel page
2. Take screenshot to verify page loaded
3. Verify page title contains "BusOS" or "Assessment"

**Expected**:
- Page loads successfully
- Assessment form visible
- No error messages

**MCP Commands**:
```
mcp__puppeteer__puppeteer_navigate(url="https://sangletech.com/en/flows/businessX/dfu/xmas-a01")
mcp__puppeteer__puppeteer_screenshot(name="tc-4-7-1-funnel-loaded")
```

---

### TC-4.7.2: Fill Assessment Form

**Steps**:
1. Navigate to funnel (from TC-4.7.1)
2. Fill email field with `lengobaosang@gmail.com`
3. Answer assessment questions (red_systems=2 for CRITICAL segment)
4. Take screenshot of filled form

**Expected**:
- All fields populate correctly
- No validation errors
- Form ready for submission

**MCP Commands**:
```
# Find and fill email field
mcp__puppeteer__puppeteer_evaluate(script="(() => {
  const emailInput = document.querySelector('input[type=\"email\"], input[name=\"email\"]');
  if (emailInput) {
    emailInput.value = 'lengobaosang@gmail.com';
    emailInput.dispatchEvent(new Event('input', { bubbles: true }));
  }
  return !!emailInput;
})()")

# Fill assessment questions (depends on form structure)
# Take screenshot
mcp__puppeteer__puppeteer_screenshot(name="tc-4-7-2-form-filled")
```

---

### TC-4.7.3: Submit Form and Verify Email #1

**Steps**:
1. Fill form (from TC-4.7.2)
2. Click submit button
3. Wait for confirmation message
4. Verify Email #1 sent by website

**Expected**:
- Form submits successfully
- Confirmation message appears
- Email #1 triggered immediately

**MCP Commands**:
```
# Submit form (find submit button)
mcp__puppeteer__puppeteer_evaluate(script="(() => {
  const submitBtn = Array.from(document.querySelectorAll('button, input[type=\"submit\"]'))
    .find(el => el.textContent.toLowerCase().includes('submit') || el.textContent.toLowerCase().includes('start'));
  if (submitBtn) submitBtn.click();
  return !!submitBtn;
})()")

# Wait for processing
mcp__puppeteer__puppeteer_evaluate(script="new Promise(resolve => setTimeout(() => resolve({ url: window.location.href, title: document.title }), 3000))")

# Screenshot confirmation
mcp__puppeteer__puppeteer_screenshot(name="tc-4-7-3-submitted")
```

---

### TC-4.7.4: Verify Webhook Includes email_1_sent_at

**Steps**:
1. Submit form (from TC-4.7.3)
2. Query Notion for Email #1 record
3. Verify email_1_sent_at timestamp exists
4. Query Kestra for webhook execution

**Expected**:
- Notion shows Email #1 sent
- Webhook payload includes email_1_sent_at
- Kestra flow triggered

**Verification** (Python API calls):
```python
# Query Notion Email Sequence DB
# Verify Email 1 Sent field exists
# Capture email_1_sent_at timestamp
```

---

### TC-4.7.5: Verify Kestra Flow Triggered

**Steps**:
1. Submit form
2. Wait 5 seconds
3. Query Kestra API for assessment-handler executions
4. Verify execution exists with correct parameters

**Expected**:
- Execution ID exists
- State is SUCCESS or RUNNING
- Parameters include test email

**Verification** (API):
```bash
curl -u galacoder69@gmail.com:Kestra2025Admin! \
  "https://kestra.galatek.dev/api/v1/executions/search?namespace=christmas&flowId=assessment-handler"
```

---

### TC-4.7.6: Verify Notion Email #1 Sent by Website

**Steps**:
1. Submit form
2. Query Notion Sequence Tracker
3. Verify Email #1 entry exists
4. Verify Email 1 Sent timestamp is set
5. Verify no Kestra flags on Email #1

**Expected**:
- Email #1 Sent field populated
- Timestamp matches submission time
- No "sent_by=kestra" flag

---

### TC-4.7.7: Verify Only 4 Emails Scheduled by Kestra

**Steps**:
1. Submit form
2. Wait for Kestra processing (10 seconds)
3. Query Kestra for scheduled subflow executions
4. Count scheduled emails

**Expected**:
- Exactly 4 subflows scheduled
- Email numbers are 2, 3, 4, 5 (not 1)

---

### TC-4.7.8: Test TESTING_MODE Timing (+1 min)

**Steps**:
1. Submit form with testing_mode=true
2. Capture email_1_sent_at timestamp
3. Wait 70 seconds
4. Verify Email #2 delivered

**Expected**:
- Email #2 scheduled at +1 minute
- Email #2 delivered after 1 minute
- Resend shows delivery

---

### TC-4.7.9: Test PRODUCTION Timing (+24h)

**Steps**:
1. Submit form with testing_mode=false
2. Query Kestra for Email #2 scheduled time
3. Verify scheduled for +24 hours

**Expected**:
- Email #2 scheduled at email_1_sent_at + 24 hours
- Do NOT wait for delivery (just verify scheduling)

---

### TC-4.7.10: Verify Email #2 Resend Delivery

**Steps**:
1. Submit form with testing_mode=true
2. Wait 70 seconds
3. Query Resend API for emails to test address
4. Verify Email #2 exists

**Expected**:
- Email found in Resend
- Subject matches Email #2 template
- Status is 'sent' or 'delivered'

---

## Cleanup

After each test:
```bash
# Archive Notion Contact
curl -X PATCH "https://api.notion.com/v1/pages/{contact_id}" \
  -H "Authorization: Bearer $NOTION_TOKEN" \
  -d '{"archived": true}'

# Archive Notion Email Sequence
curl -X PATCH "https://api.notion.com/v1/pages/{sequence_id}" \
  -H "Authorization: Bearer $NOTION_TOKEN" \
  -d '{"archived": true}'
```
