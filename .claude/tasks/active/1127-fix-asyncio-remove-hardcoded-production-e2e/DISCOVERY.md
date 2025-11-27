# Discovery Report: Fix AsyncIO, Remove Hardcoded Templates, E2E Production Test

**Task ID**: 1127-fix-asyncio-remove-hardcoded-production-e2e
**Domain**: CODING
**Date**: 2025-11-27
**Status**: EXPLORE Complete

---

## Executive Summary

This task addresses three critical requirements for the Christmas Campaign production deployment:
1. **Fix Python 3.12 AsyncIO Issue** - Workers crash with `NotImplementedError` from `asyncio.get_child_watcher()`
2. **Remove Hardcoded Email Templates** - All templates must come from Notion, no fallbacks
3. **Full E2E Production Test** - Puppeteer-based funnel test with email delivery verification

---

## 1. Python 3.12 AsyncIO Issue Analysis

### Problem

Production Prefect workers at `https://prefect.galatek.dev` crash on first flow run with:

```
File "/usr/local/lib/python3.12/asyncio/events.py", line 645, in get_child_watcher
    raise NotImplementedError
NotImplementedError
```

### Root Cause

- Python 3.12 deprecated `asyncio.get_child_watcher()` (PEP 671)
- uvloop triggers this deprecated method
- Prefect workers use subprocess management that relies on child watcher

### Documented Fix (from PRODUCTION_FIX.md)

```bash
# Option 1: Remove uvloop (quickest fix)
pip uninstall uvloop -y
pkill -f "prefect worker"
prefect worker start --pool default &

# Option 2: Upgrade Prefect
pip install --upgrade prefect>=3.4.1
pkill -f "prefect worker"
prefect worker start --pool default &
```

### Server Access

- **Server**: Hublab (MINISFORUM UH125 Pro) - Coolify managed
- **Access Method**: Coolify integration skill available at `~/.claude/skills/coolify-integration/`
- **Alternative**: SSH if Coolify doesn't have pip access

### Impact Evidence

From Wave 4 test (WAVE4_EMAIL_DELIVERY_SUMMARY.md):
- Email 1: CRASHED with `NotImplementedError`
- Emails 2-7: All succeeded (85.71% success rate)
- The crash only affects first flow run after worker restart

---

## 2. Hardcoded Email Template Analysis

### Files with Hardcoded Templates

**Primary File**: `campaigns/christmas_campaign/tasks/resend_operations.py`
- Lines 215-271: `get_fallback_template()` function
- Contains hardcoded HTML for `christmas_email_1`, `christmas_email_2`
- Generic fallback for unknown templates

```python
def get_fallback_template(template_id: str) -> Dict[str, str]:
    """Get fallback email template if Notion fetch fails."""
    templates = {
        "christmas_email_1": {...},
        "christmas_email_2": {...},
    }
    return templates.get(template_id, {
        "subject": "Update from BusOS",
        "html_body": "<html>...</html>"
    })
```

### Files Using Fallback

**Primary Consumer**: `campaigns/christmas_campaign/flows/send_email_flow.py`
- Line 44: Imports `get_fallback_template`
- Lines 157-160: Uses fallback when template not found

```python
# Step 3b: Use fallback if Notion fetch fails
if not template_data:
    logger.warning(f"Template {template_id} not found in Notion, using fallback")
    template_data = get_fallback_template(template_id)
```

### Other Flows (No Fallback Usage)

The following flows do NOT use `get_fallback_template`:
- `noshow_recovery_handler.py` - Uses template_id parameter directly
- `postcall_maybe_handler.py` - Uses template_id parameter directly
- `onboarding_handler.py` - Uses template_id parameter directly
- `signup_handler.py` - Schedules flows, doesn't fetch templates

### Required Changes

1. **Remove** `get_fallback_template()` from `resend_operations.py`
2. **Remove** fallback import and usage from `send_email_flow.py`
3. **Raise Error** when template not found in Notion
4. **Update Tests** to reflect new behavior (expect errors, not fallbacks)

---

## 3. E2E Production Test Analysis

### Test Infrastructure

- **Puppeteer MCP**: Available via `mcp__puppeteer__*` tools
- **Production URL**: `https://sangletech.com/en/flows/businessX/dfu/xmas-a01`
- **Mandatory Test Email**: `lengobaosang@gmail.com`
- **Prefect Dashboard**: `https://prefect.galatek.dev`

### Existing E2E Tests

Located at `campaigns/christmas_campaign/tests/e2e/`:
- `test_full_integration_e2e.py` - Full integration suite
- `test_production_readiness_e2e.py` - Production readiness checks
- `test_lead_nurture_funnel.py` - Lead nurture sequence tests

### Test Flow

1. Navigate to production funnel URL
2. Complete BusOS assessment with real variables
3. Submit form (triggers webhook automatically)
4. Verify Prefect flows execute at `https://prefect.galatek.dev`
5. Verify emails scheduled in Notion Email Sequence database
6. Verify emails delivered via Resend
7. TESTING_MODE=true for 1-minute intervals

### Webhook Endpoints to Test

| Webhook | Deployment | Emails |
|---------|------------|--------|
| `/webhook/christmas-signup` | christmas-signup-handler | 7 |
| `/webhook/calendly-noshow` | christmas-noshow-recovery-handler | 3 |
| `/webhook/postcall-maybe` | christmas-postcall-maybe-handler | 3 |
| `/webhook/onboarding-start` | christmas-onboarding-handler | 3 |

---

## 4. Dependencies & Tech Stack

### Core Dependencies (requirements.txt)

```
prefect==3.4.1
notion-client==2.2.1
resend==2.19.0
httpx==0.27.2
python-dotenv==1.0.1
fastapi==0.115.6
uvicorn[standard]==0.34.0
pydantic[email]==2.10.4
pytest==8.3.4
pytest-mock==3.14.0
pytest-cov==6.0.0
```

### Prefect Secret Blocks (Production)

7 blocks configured:
- `notion-token`
- `notion-email-templates-db-id`
- `notion-email-sequence-db-id`
- `notion-businessx-db-id`
- `notion-customer-projects-db-id`
- `notion-email-analytics-db-id`
- `resend-api-key`

### Coolify Integration

Skill available at `~/.claude/skills/coolify-integration/`:
- `listServers()` - List servers
- `getServerResources(uuid)` - Get server resources
- `deployApplication(uuid)` - Deploy/restart applications

**Note**: May need SSH access for pip operations on workers.

---

## 5. Risk Assessment

### High Risk

1. **Python 3.12 AsyncIO Fix** - Requires server access, worker restart
   - Mitigation: Test on single worker first

2. **Template Removal** - Could break flows if templates missing in Notion
   - Mitigation: Verify all templates exist before removing fallbacks

### Medium Risk

1. **E2E Test** - Production environment, real emails
   - Mitigation: Use mandatory test email `lengobaosang@gmail.com`

2. **TESTING_MODE** - Must be TRUE for fast email intervals
   - Mitigation: Verify via Secret block before test

### Low Risk

1. **Code Changes** - Well-scoped, single file edits
   - Mitigation: Unit tests exist

---

## 6. Files to Modify

| File | Change | Risk |
|------|--------|------|
| `campaigns/christmas_campaign/tasks/resend_operations.py` | Remove `get_fallback_template()` | Medium |
| `campaigns/christmas_campaign/flows/send_email_flow.py` | Remove fallback import/usage, raise error | Medium |
| `campaigns/christmas_campaign/tests/test_resend_operations.py` | Update tests for new behavior | Low |

---

## 7. Recommended Approach

### Wave 1: Fix Python 3.12 AsyncIO Issue

1. Use Coolify skill to access Hublab server
2. Run `pip uninstall uvloop -y` on worker
3. Restart Prefect workers
4. Verify fix with test flow run

### Wave 2: Remove Hardcoded Templates

1. Delete `get_fallback_template()` from `resend_operations.py`
2. Modify `send_email_flow.py` to raise error instead of fallback
3. Update unit tests
4. Run test suite to verify

### Wave 3: E2E Production Test

1. Navigate to production funnel via Puppeteer
2. Complete assessment with test data
3. Verify flow execution in Prefect
4. Verify emails in Resend dashboard
5. Generate test report

### Wave 4: Verification & Documentation

1. Run full test suite
2. Update STATUS.md
3. Create deployment summary
4. Archive completed task

---

## 8. Success Criteria

1. **AsyncIO Fix**: Workers process first email without crash (100% success rate)
2. **Template Removal**: All templates fetched from Notion, errors on missing
3. **E2E Test**: 7/7 emails delivered to `lengobaosang@gmail.com`
4. **Documentation**: STATUS.md updated with production-ready status

---

**Discovery Completed**: 2025-11-27
**Ready for**: PLAN Phase
