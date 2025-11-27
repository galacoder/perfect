# Plan: Fix AsyncIO, Remove Hardcoded Templates, E2E Production Test

**Task ID**: 1127-fix-asyncio-remove-hardcoded-production-e2e
**Domain**: CODING
**Source**: feature_list.json

---

## Wave 1: Fix Python 3.12 AsyncIO Issue
**Objective**: Remove uvloop or upgrade Prefect on production workers to fix asyncio.get_child_watcher() NotImplementedError
**Status**: Pending
**Priority**: CRITICAL

### Tasks
- [ ] 1.1: Access production server via Coolify
- [ ] 1.2: Uninstall uvloop package
- [ ] 1.3: Restart Prefect workers
- [ ] 1.4: Verify fix with test flow run

### Success Criteria
- [ ] Production Prefect workers process first email without crash
- [ ] 100% email success rate (vs previous 85.71%)
- [ ] No `NotImplementedError` in flow run logs

### Implementation Details

**Access Method**: Use Coolify integration skill to connect to Hublab server

```bash
# Commands to run on Hublab server
pip uninstall uvloop -y
pkill -f "prefect worker"
prefect worker start --pool default &
```

**Verification Test**:
```bash
PREFECT_API_URL=https://prefect.galatek.dev/api \
prefect deployment run christmas-send-email/christmas-send-email \
  --param email="lengobaosang@gmail.com" \
  --param email_number=1 \
  --param first_name="Test" \
  --param business_name="Test Business"
```

---

## Wave 2: Remove Hardcoded Templates
**Objective**: Remove get_fallback_template() function and all fallback logic - templates must come from Notion ONLY
**Status**: Pending
**Priority**: HIGH

### Tasks
- [ ] 2.1: Remove get_fallback_template() function
- [ ] 2.2: Update send_email_flow.py to error on missing template
- [ ] 2.3: Update unit tests for new behavior
- [ ] 2.4: Run test suite and verify all pass

### Success Criteria
- [ ] `get_fallback_template()` function deleted from resend_operations.py
- [ ] `send_email_flow.py` raises explicit error when template not found
- [ ] All unit tests pass with updated behavior
- [ ] No fallback template code in codebase

### Implementation Details

**File 1: resend_operations.py (DELETE lines 215-271)**

```python
# DELETE THIS ENTIRE BLOCK:
# ==============================================================================
# Fallback Email Templates (Static)
# ==============================================================================

def get_fallback_template(template_id: str) -> Dict[str, str]:
    """Get fallback email template if Notion fetch fails..."""
    # ... entire function deleted
```

**File 2: send_email_flow.py (MODIFY lines 42-44, 157-160)**

Before:
```python
from campaigns.christmas_campaign.tasks.resend_operations import (
    send_template_email,
    get_email_variables,
    get_fallback_template  # <- REMOVE
)
```

After:
```python
from campaigns.christmas_campaign.tasks.resend_operations import (
    send_template_email,
    get_email_variables
)
```

Before (lines 157-163):
```python
# Step 3b: Use fallback if Notion fetch fails
if not template_data:
    logger.warning(f"Template {template_id} not found in Notion, using fallback")
    template_data = get_fallback_template(template_id)

subject = template_data.get("subject", "Update from BusOS")
html_body = template_data.get("html_body", "")
```

After:
```python
# Step 3b: Error if template not found (no fallbacks allowed)
if not template_data:
    error_msg = f"CRITICAL: Template '{template_id}' not found in Notion Email Templates database. All templates MUST exist in Notion."
    logger.error(error_msg)
    raise ValueError(error_msg)

subject = template_data.get("subject")
html_body = template_data.get("html_body")

if not subject or not html_body:
    error_msg = f"CRITICAL: Template '{template_id}' is missing subject or html_body"
    logger.error(error_msg)
    raise ValueError(error_msg)
```

---

## Wave 3: E2E Production Test via Puppeteer
**Objective**: Complete full production funnel test with real assessment, verify 7/7 emails delivered
**Status**: Pending
**Priority**: HIGH

### Tasks
- [ ] 3.1: Navigate to production funnel via Puppeteer
- [ ] 3.2: Complete BusOS assessment with test data
- [ ] 3.3: Submit form with mandatory test email
- [ ] 3.4: Verify webhook triggered signup_handler flow
- [ ] 3.5: Wait for and verify 7 email flow runs
- [ ] 3.6: Verify emails delivered via Resend

### Success Criteria
- [ ] Production funnel accessible at https://sangletech.com/en/flows/businessX/dfu/xmas-a01
- [ ] Assessment form submits successfully
- [ ] Webhook triggers christmas-signup-handler flow
- [ ] 7/7 email flow runs complete (TESTING_MODE = 1-minute intervals)
- [ ] All 7 emails delivered to lengobaosang@gmail.com

### Implementation Details

**Test Data**:
```json
{
  "email": "lengobaosang@gmail.com",
  "first_name": "Test",
  "business_name": "Production E2E Test",
  "assessment_score": 52,
  "red_systems": 2,
  "orange_systems": 1,
  "yellow_systems": 2,
  "green_systems": 3
}
```

**Puppeteer Flow**:
1. `puppeteer_navigate` to production URL
2. `puppeteer_screenshot` to capture initial state
3. `puppeteer_fill` form fields with test data
4. `puppeteer_click` submit button
5. Wait for webhook processing
6. Monitor Prefect dashboard for flow runs
7. Verify all 7 emails in Resend

**Timing (TESTING_MODE=true)**:
- Email 1: Immediate
- Email 2: +1 minute
- Email 3: +2 minutes
- Email 4: +3 minutes
- Email 5: +4 minutes
- Email 6: +5 minutes
- Email 7: +6 minutes
- Total: ~7 minutes

---

## Wave 4: Verification & Documentation
**Objective**: Run full test suite, update STATUS.md, create deployment summary
**Status**: Pending
**Priority**: MEDIUM

### Tasks
- [ ] 4.1: Run full test suite (pytest)
- [ ] 4.2: Update STATUS.md with production-ready status
- [ ] 4.3: Generate E2E test report
- [ ] 4.4: Create git commit with all changes

### Success Criteria
- [ ] All pytest tests pass
- [ ] STATUS.md reflects 100% production-ready status
- [ ] E2E test report generated with flow run IDs
- [ ] Changes committed to git

### Implementation Details

**Pytest Command**:
```bash
pytest campaigns/christmas_campaign/tests/ -v --tb=short
```

**STATUS.md Updates**:
- Wave 5 -> Wave 6 complete
- E2E Testing: COMPLETE
- Production Status: 100% READY
- Blockers: RESOLVED (asyncio fix applied)

**Git Commit**:
```bash
git add .
git commit -m "fix: remove hardcoded templates, fix asyncio, complete E2E production test

- Remove get_fallback_template() from resend_operations.py
- Update send_email_flow.py to error on missing Notion templates
- Fix Python 3.12 asyncio issue by removing uvloop
- Complete E2E production test with 7/7 emails delivered

Closes: asyncio NotImplementedError on first flow run
Tested: Full production funnel with lengobaosang@gmail.com"
```

---

## Dependencies

### External Access Required
- Coolify skill for server management
- Puppeteer MCP for browser automation
- Production Prefect at https://prefect.galatek.dev

### Mandatory Test Email
**CRITICAL**: Use `lengobaosang@gmail.com` for ALL testing

### Pre-requisites
- TESTING_MODE Secret block must be set to "true"
- All Notion email templates must exist (7 for signup, 3 each for noshow/postcall/onboarding)
- Prefect Secret blocks configured on production

---

## Estimated Timeline

| Wave | Duration | Dependencies |
|------|----------|--------------|
| Wave 1 | 30 min | Server access |
| Wave 2 | 30 min | None |
| Wave 3 | 15 min | Waves 1-2 complete |
| Wave 4 | 15 min | Wave 3 complete |
| **Total** | **~90 min** | |

---

## Risk Mitigation

### Wave 1 Risks
- **Server access fails**: Use SSH as backup
- **Worker restart issues**: Check worker logs, retry

### Wave 2 Risks
- **Missing Notion templates**: Verify templates exist before code changes
- **Test failures**: Revert changes if tests fail

### Wave 3 Risks
- **Funnel UI changes**: Capture screenshots for debugging
- **Slow email delivery**: Monitor Resend dashboard

### Wave 4 Risks
- **Test failures**: Fix issues before commit
- **Git conflicts**: Pull latest before push

---

**Plan Created**: 2025-11-27
**Awaiting**: User approval to proceed to /execute-coding
