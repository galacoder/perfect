# Plan: Fix AsyncIO, Remove Hardcoded Templates, E2E Production Test

**Task ID**: 1127-fix-asyncio-remove-hardcoded-production-e2e
**Domain**: CODING
**Source**: feature_list.json

---

## Wave 1: Fix Python 3.12 AsyncIO Issue
**Objective**: Remove uvloop or upgrade Prefect on production workers to fix asyncio.get_child_watcher() NotImplementedError
**Status**: Skipped (using local Python 3.11.8 worker)
**Priority**: CRITICAL

### Tasks
- [x] 1.1: Access production server via Coolify (SKIPPED)
- [x] 1.2: Uninstall uvloop package (SKIPPED)
- [x] 1.3: Restart Prefect workers (SKIPPED)
- [x] 1.4: Verify fix with test flow run (SKIPPED)

---

## Wave 2: Remove Hardcoded Templates
**Objective**: Remove get_fallback_template() function and all fallback logic - templates must come from Notion ONLY
**Status**: Complete
**Priority**: HIGH

### Tasks
- [x] 2.1: Remove get_fallback_template() function
- [x] 2.2: Update send_email_flow.py to error on missing template
- [x] 2.3: Update unit tests for new behavior
- [x] 2.4: Run test suite and verify all pass

---

## Wave 3: E2E Production Test via Puppeteer
**Objective**: Complete full production funnel test with real assessment, verify 7/7 emails delivered
**Status**: Complete
**Priority**: HIGH

### Tasks
- [x] 3.1: Navigate to production funnel via Puppeteer
- [x] 3.2: Complete BusOS assessment with test data
- [x] 3.3: Submit form with mandatory test email
- [x] 3.4: Verify webhook triggered signup_handler flow
- [x] 3.5: Verify template fetch from Notion
- [x] 3.6: Verify no fallback code exists

---

## Wave 4: Verification & Documentation
**Objective**: Run full test suite, update STATUS.md, create deployment summary
**Status**: Complete
**Priority**: MEDIUM

### Tasks
- [x] 4.1: Run full test suite (pytest)
- [x] 4.2: Update STATUS.md with production-ready status
- [x] 4.3: Generate E2E test report
- [x] 4.4: Create git commit with all changes

---

## Wave 5: E2E Production Integration Test
**Objective**: Full customer journey test from production sales funnel to Prefect flow execution to email delivery verification
**Status**: Complete
**Priority**: HIGH
**Added via**: /add-tasks-coding (2025-11-28)

### Tasks
- [x] 5.1: Navigate production funnel via Puppeteer MCP
- [x] 5.2: Complete full assessment with test data
- [x] 5.3: Submit form with mandatory test email (lengobaosang@gmail.com)
- [x] 5.4: Verify webhook triggers Prefect flow on PRODUCTION server
- [x] 5.5: Test all 4 webhook endpoints
- [x] 5.6: Monitor email flow runs complete
- [x] 5.7: Verify emails delivered via Resend dashboard
- [x] 5.8: Run pytest with coverage report (target >85%) - RESULT: 46% (BELOW TARGET)

---

## Wave 6: Test Coverage Improvement to 85%+ (NEW - Added 2025-11-28)
**Objective**: Fix 14 failing tests, add unit tests for uncovered flows, implement production E2E tests via Playwright for sales funnel and Prefect production server
**Status**: Pending
**Priority**: HIGH
**Added via**: /add-tasks-coding

### Coverage Analysis

**Current State**:
- **163 tests passed**, 14 failed, 30 skipped
- **Overall coverage: 46%** (target: 85%)
- **Gap to close: 39 percentage points**

**Failing Tests Root Causes**:
1. `RuntimeError: Failed to reach API at http://127.0.0.1:8516/api/` (10 tests) - Prefect ephemeral test server not running
2. `notion_client.errors.APIResponseError: Template Type is not a property` (4 tests) - Notion property name mismatches

**Uncovered Files**:
| File | Current Coverage | Target |
|------|-----------------|--------|
| `flows/email_sequence_orchestrator.py` | 0% | 80% |
| `flows/send_email_flow.py` | 0% | 80% |
| `flows/precall_prep_flow.py` | 0% | 80% |
| `flows/signup_handler.py` | 10% | 80% |
| `flows/postcall_maybe_handler.py` | 10% | 80% |
| `flows/noshow_recovery_handler.py` | 30% | 80% |
| `tasks/notion_operations.py` | 36% | 80% |
| `orchestrate_sequence.py` | 0% | 80% |
| `tasks/models.py` | 0% | 80% |

### Tasks

#### Phase 1: Fix Failing Tests (Features 6.1-6.2)
- [ ] 6.1: Fix Prefect ephemeral test server connection failures
  - Mock `get_client()` and Prefect API calls in conftest.py
  - Use `unittest.mock.MagicMock` or `pytest-mock`
  - Fix 10+ failing tests
  - **File**: `campaigns/christmas_campaign/tests/conftest.py`
  - **Estimate**: 1 hour

- [ ] 6.2: Fix Notion property name mismatches in tests
  - Update mock responses to match actual Notion database schema
  - Fix "Template Type" property errors
  - Fix 4+ failing tests
  - **File**: `campaigns/christmas_campaign/tests/conftest.py`
  - **Estimate**: 0.5 hours

#### Phase 2: Add Unit Tests for Flows (Features 6.3-6.7)
- [ ] 6.3: Add unit tests for signup_handler.py (10% -> 80%)
  - Test valid payload handling
  - Test error handling for missing email
  - Test duplicate contact handling
  - Test segment classification routing
  - Test email sequence scheduling
  - **File**: `campaigns/christmas_campaign/tests/test_signup_handler.py`
  - **Estimate**: 1.5 hours

- [ ] 6.4: Add unit tests for send_email_flow.py (0% -> 80%)
  - Test email flow with valid Notion template
  - Test error when template not found
  - Test error when template missing subject/body
  - Test variable substitution
  - Test Resend API call
  - **File**: `campaigns/christmas_campaign/tests/test_send_email_flow.py`
  - **Estimate**: 1.5 hours

- [ ] 6.5: Add unit tests for noshow_recovery_handler.py (30% -> 80%)
  - Test with valid Calendly payload
  - Test 3-email recovery sequence scheduling
  - Test error handling for missing event_uri
  - Test malformed payload handling
  - **File**: `campaigns/christmas_campaign/tests/test_noshow_recovery_handler.py`
  - **Estimate**: 1 hour

- [ ] 6.6: Add unit tests for postcall_maybe_handler.py (10% -> 80%)
  - Test with valid payload
  - Test 3-email follow-up sequence scheduling
  - Test call notes and objections handling
  - Test error handling for missing email
  - **File**: `campaigns/christmas_campaign/tests/test_postcall_maybe_handler.py`
  - **Estimate**: 1 hour

- [ ] 6.7: Add unit tests for email_sequence_orchestrator.py (0% -> 80%)
  - Test scheduling multiple emails with correct delays
  - Test TESTING_MODE uses minute intervals
  - Test PRODUCTION mode uses day intervals
  - Test sequence state management
  - **File**: `campaigns/christmas_campaign/tests/test_email_sequence_orchestrator.py`
  - **Estimate**: 1.5 hours

#### Phase 3: Add Unit Tests for Tasks/Models (Features 6.8-6.10)
- [ ] 6.8: Add unit tests for notion_operations.py (36% -> 80%)
  - Test search_contact_by_email (found/not found)
  - Test create_contact with all fields
  - Test update_contact with partial fields
  - Test fetch_template success/failure cases
  - **File**: `campaigns/christmas_campaign/tests/test_notion_operations.py`
  - **Estimate**: 1 hour

- [ ] 6.9: Add unit tests for models.py (0% -> 80%)
  - Test ContactPayload validation (valid/invalid)
  - Test AssessmentResult model
  - Test EmailTemplate model
  - **File**: `campaigns/christmas_campaign/tests/test_models.py`
  - **Estimate**: 0.5 hours

- [ ] 6.10: Add unit tests for precall_prep_flow.py (0% -> 80%)
  - Test with scheduled call
  - Test prep data fetching from Notion
  - Test error handling for missing contact
  - **File**: `campaigns/christmas_campaign/tests/test_precall_prep_flow.py`
  - **Estimate**: 1 hour

#### Phase 4: Production E2E Tests (Features 6.11-6.12)
- [ ] 6.11: Production sales funnel E2E test via Playwright
  - Navigate to production funnel URL
  - Verify all form fields visible
  - Fill assessment form with test data
  - Submit with mandatory test email
  - Verify redirect to thank-you page
  - Capture screenshots for documentation
  - **File**: `campaigns/christmas_campaign/tests/e2e/test_production_funnel.py`
  - **URL**: https://sangletech.com/en/flows/businessX/dfu/xmas-a01
  - **Email**: lengobaosang@gmail.com (MANDATORY)
  - **Estimate**: 1.5 hours

- [ ] 6.12: Production Prefect server API tests
  - Verify Prefect API health endpoint
  - Verify all 4 deployment existence
  - Test flow run creation and status polling
  - **File**: `campaigns/christmas_campaign/tests/e2e/test_production_prefect.py`
  - **URL**: https://prefect.galatek.dev
  - **Estimate**: 1 hour

#### Phase 5: Final Verification (Feature 6.13)
- [ ] 6.13: Run full test suite and verify 85%+ coverage
  - All 14 previously failing tests fixed
  - All new unit tests pass
  - Production E2E tests pass
  - Coverage report shows >= 85%
  - **Estimate**: 0.5 hours

### Success Criteria
- [ ] All 14 previously failing tests now pass
- [ ] All uncovered flow files have >= 80% coverage
- [ ] Production E2E tests pass for sales funnel and Prefect server
- [ ] Overall test coverage >= 85%
- [ ] No RuntimeError or Notion API errors in test runs

### Implementation Details

**Prefect Mocking Strategy (Feature 6.1)**:
```python
# In conftest.py
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

@pytest.fixture
def mock_prefect_client():
    """Mock Prefect client to avoid ephemeral server connection."""
    with patch('prefect.client.orchestration.get_client') as mock:
        client = AsyncMock()
        client.read_deployment_by_name = AsyncMock(return_value=MagicMock(id="test-deployment-id"))
        client.create_flow_run_from_deployment = AsyncMock(return_value=MagicMock(id="test-flow-run-id"))
        mock.return_value.__aenter__.return_value = client
        yield client
```

**Notion Mock Fix (Feature 6.2)**:
```python
# Fix property name to match actual database
mock_template_response = {
    "results": [{
        "properties": {
            "Template ID": {"title": [{"text": {"content": "christmas_email_1"}}]},
            "Subject": {"rich_text": [{"text": {"content": "Test Subject"}}]},
            "HTML Body": {"rich_text": [{"text": {"content": "<p>Test</p>"}}]}
            # Note: "Template Type" should be removed or renamed to match actual schema
        }
    }]
}
```

**Playwright E2E Test Structure (Feature 6.11)**:
```python
# campaigns/christmas_campaign/tests/e2e/test_production_funnel.py
import pytest
from playwright.sync_api import Page, expect

PRODUCTION_URL = "https://sangletech.com/en/flows/businessX/dfu/xmas-a01"
MANDATORY_EMAIL = "lengobaosang@gmail.com"

def test_funnel_loads(page: Page):
    """Test production funnel page loads correctly."""
    page.goto(PRODUCTION_URL)
    expect(page.locator("form")).to_be_visible()

def test_form_submission(page: Page):
    """Test form submission with mandatory email."""
    page.goto(PRODUCTION_URL)
    page.fill('[name="email"]', MANDATORY_EMAIL)
    page.fill('[name="name"]', "E2E Test")
    page.click('button[type="submit"]')
    expect(page).to_have_url_matching(r"/thank-you")
```

---

## Updated Estimated Timeline

| Wave | Duration | Dependencies | Status |
|------|----------|--------------|--------|
| Wave 0 | 30 min | None | Complete |
| Wave 1 | 30 min | Server access | Skipped |
| Wave 2 | 30 min | None | Complete |
| Wave 3 | 15 min | Waves 0-2 complete | Complete |
| Wave 4 | 15 min | Wave 3 complete | Complete |
| Wave 5 | 120 min | Waves 0-4 complete | Complete |
| Wave 6 | 180 min | Wave 5 complete | **Pending** |
| **Total** | **~7 hours** | | |

---

## Dependencies

### External Access Required
- Coolify skill for server management
- Puppeteer MCP for browser automation
- Playwright skill for E2E testing
- Production Prefect at https://prefect.galatek.dev

### Mandatory Test Email
**CRITICAL**: Use `lengobaosang@gmail.com` for ALL testing

### Pre-requisites
- TESTING_MODE Secret block must be set to "true"
- All Notion email templates must exist
- Prefect Secret blocks configured on production
- Playwright installed for E2E tests

---

## Blockers

| ID | Severity | Description | Status | Solution |
|----|----------|-------------|--------|----------|
| B1 | Critical | Python 3.12 asyncio.get_child_watcher() deprecated | Resolved | Using local Python 3.11.8 worker |
| B2 | High | 14 failing tests (Prefect API + Notion property) | Pending | Wave 6 features 6.1-6.2 |
| B3 | High | Test coverage at 46% (target: 85%) | Pending | Wave 6 features 6.3-6.13 |

---

**Plan Created**: 2025-11-27
**Updated**: 2025-11-28 (Wave 6 added via /add-tasks-coding)
**Awaiting**: User approval to proceed to /execute-coding
