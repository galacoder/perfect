# Discovery: E2E Puppeteer Sales Funnel Email Verification

**Task ID**: 1127-e2e-puppeteer-sales-funnel-email-verification
**Domain**: CODING
**Started**: 2025-11-27
**Phase**: EXPLORE Complete

---

## 1. Domain Detected

**CODING** - This task involves:
- Browser automation with Puppeteer/MCP
- API integration testing
- Prefect flow verification
- Email delivery verification through Resend API

---

## 2. Codebase Analysis

### 2.1 Project Structure

The Christmas Campaign is located at:
```
/campaigns/christmas_campaign/
  ├── flows/
  │   ├── signup_handler.py          # Main entry - schedules 7 emails
  │   ├── send_email_flow.py         # Individual email sender
  │   ├── noshow_recovery_handler.py # No-show sequence (3 emails)
  │   ├── postcall_maybe_handler.py  # Post-call sequence (3 emails)
  │   └── onboarding_handler.py      # Onboarding sequence (3 emails)
  │
  ├── tests/e2e/
  │   ├── conftest_e2e.py            # Shared fixtures, HTTP client
  │   ├── e2e_test_runner.py         # CLI test runner
  │   ├── test_lead_nurture_funnel.py # Lead nurture tests
  │   ├── test_full_integration_e2e.py # Multi-sequence tests
  │   └── fixtures/                  # Test data JSON files
  │
  └── STATUS.md                      # Deployment status tracking
```

### 2.2 Webhook Endpoints (server.py)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/webhook/christmas-signup` | POST | Trigger 7-email lead nurture |
| `/webhook/calendly-noshow` | POST | Trigger 3-email no-show recovery |
| `/webhook/postcall-maybe` | POST | Trigger 3-email post-call follow-up |
| `/webhook/onboarding-start` | POST | Trigger 3-email onboarding welcome |
| `/health` | GET | Health check |

### 2.3 Sales Funnel URL

**Target**: `https://sangletech.com/en/flows/businessX/dfu/xmas-a01`

This is a Next.js-based assessment funnel that:
1. Collects user email and business info
2. Runs 16-question BusOS assessment
3. Displays results page
4. Sends webhook to `/webhook/christmas-signup`

### 2.4 Email Timing (TESTING_MODE=true)

When `testing-mode` Secret block is `true`:
- Email 1: Immediate (0 min)
- Email 2: +1 minute
- Email 3: +2 minutes
- Email 4: +3 minutes
- Email 5: +4 minutes
- Email 6: +5 minutes
- Email 7: +6 minutes

**Total duration**: ~6-10 minutes

### 2.5 Required Test Email

**MANDATORY**: `lengobaosang@gmail.com`
- This email is specified in user requirements
- Must delete existing sequence from Notion first (idempotency bypass)

### 2.6 Notion Database IDs

| Database | Secret Block Name |
|----------|-------------------|
| Email Sequence | `notion-email-sequence-db-id` (576de1aa-6064-4201-a5e6-623b7f2be79a) |
| Email Templates | `notion-email-templates-db-id` |
| BusinessX Canada | `notion-businessx-db-id` |

---

## 3. Dependencies Identified

### 3.1 Infrastructure

- **Prefect Server**: `https://prefect.galatek.dev/api`
- **FastAPI Server**: Local development (localhost:8000)
- **Website**: `https://sangletech.com` (production)
- **Notion API**: Via Prefect Secret blocks
- **Resend API**: Via Prefect Secret blocks

### 3.2 MCP Tools Available

- **Puppeteer MCP**: `mcp__puppeteer__*` tools
  - `puppeteer_navigate` - Navigate to URL
  - `puppeteer_screenshot` - Capture screenshots
  - `puppeteer_click` - Click elements
  - `puppeteer_fill` - Fill form fields

### 3.3 Existing Test Infrastructure

- `conftest_e2e.py` - HTTP client, fixtures, result capture
- `test_customer_data.json` - Test payloads for all segments
- `e2e_test_runner.py` - CLI test orchestrator

---

## 4. Risks Identified

### 4.1 High Risk

| Risk | Mitigation |
|------|------------|
| Idempotency blocking test | Delete existing sequence for lengobaosang@gmail.com BEFORE test |
| Puppeteer timeout on slow website | Set extended timeout (60s+ for page loads) |
| Email delivery delay | Monitor for 10+ minutes, check Resend dashboard |

### 4.2 Medium Risk

| Risk | Mitigation |
|------|------------|
| Webhook endpoint not exposed | Ensure FastAPI server running locally |
| TESTING_MODE not set | Verify `testing-mode` Secret block = true |
| Form structure changed | Take screenshots at each step for debugging |

### 4.3 Low Risk

| Risk | Mitigation |
|------|------------|
| Network latency | Retry logic with backoff |
| Screenshot storage | Save to dedicated directory |

---

## 5. Recommendations

### 5.1 Test Strategy

1. **Pre-test cleanup**: Delete existing Notion records for test email
2. **Browser automation**: Use Puppeteer MCP for funnel navigation
3. **Webhook verification**: Check Prefect flow run created
4. **Email monitoring**: Wait for all 7 emails (~10 min in testing mode)
5. **Post-test verification**: Query Notion for sequence record

### 5.2 Technical Approach

```
Phase 1: Setup
  - Delete existing sequence from Notion (bypass idempotency)
  - Verify TESTING_MODE=true
  - Start FastAPI server locally

Phase 2: Browser Automation
  - Navigate to sangletech.com/en/flows/businessX/dfu/xmas-a01
  - Fill opt-in form with lengobaosang@gmail.com
  - Complete 16-question assessment (CRITICAL segment answers)
  - Capture screenshots at each step
  - Verify results page displayed

Phase 3: Webhook Verification
  - Wait for webhook to trigger (automatic from website)
  - OR manually trigger via FastAPI endpoint
  - Verify Prefect flow run created

Phase 4: Email Monitoring
  - Wait 10 minutes for all 7 emails
  - Check Resend delivery logs
  - Verify emails arrived at lengobaosang@gmail.com
```

### 5.3 Success Criteria

- [ ] Browser navigates through entire funnel
- [ ] Assessment completed with CRITICAL segment
- [ ] Webhook triggered successfully
- [ ] Prefect flow run created
- [ ] 7 emails scheduled in Notion
- [ ] All 7 emails delivered to lengobaosang@gmail.com

---

## 6. Files to Create/Modify

### New Files

| File | Purpose |
|------|---------|
| `tests/e2e/test_puppeteer_funnel_e2e.py` | Main Puppeteer E2E test |
| `tests/e2e/utils/notion_cleanup.py` | Utility to delete sequence records |
| `tests/e2e/utils/email_monitor.py` | Utility to monitor email delivery |

### Files to Reference

| File | Purpose |
|------|---------|
| `conftest_e2e.py` | Reuse existing fixtures |
| `test_customer_data.json` | Reuse CRITICAL segment payload |
| `signup_handler.py` | Understand flow parameters |

---

## 7. Environment Requirements

```bash
# Required environment variables
TESTING_MODE=true                    # Fast email timing
NOTION_TOKEN=ntn_xxxxx              # Notion API (or via Secret block)
RESEND_API_KEY=re_xxxxx             # Resend API (or via Secret block)

# Secret blocks on Prefect (already configured)
testing-mode=true
notion-token=xxx
notion-email-sequence-db-id=576de1aa-6064-4201-a5e6-623b7f2be79a
resend-api-key=xxx
```

---

## 8. Key Learnings from Codebase

1. **Idempotency**: The `signup_handler_flow` checks for existing sequences and skips if found
2. **Segment Classification**:
   - CRITICAL: 2+ red systems
   - URGENT: 1 red OR 2+ orange
   - OPTIMIZE: all others
3. **Email Scheduling**: Uses Prefect deployment `christmas-send-email/christmas-send-email`
4. **Timing**: In testing mode, emails send at 0, 1, 2, 3, 4, 5, 6 minutes

---

**Discovery Complete**: Ready for PLAN phase
