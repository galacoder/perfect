# End-to-End Sales Funnel Tests

Complete testing suite for the Christmas Campaign sales funnel, covering website → webhook → Prefect → Notion → email scheduling.

---

## Overview

This test suite validates the complete customer journey:

1. **Website Form Submission** (Playwright) - Simulate customer completing assessment
2. **Webhook Triggering** (FastAPI) - Verify POST /webhook/christmas-signup
3. **Prefect Flow Execution** - Verify signup_handler_flow runs successfully
4. **Notion Database Updates** - Verify 3 databases updated correctly
5. **Email Scheduling** - Verify 7 emails scheduled in Prefect

---

## Prerequisites

### 1. FastAPI Server

```bash
# Start webhook server (required)
uvicorn server:app --reload

# Verify server is running
curl http://localhost:8000/health
```

### 2. Environment Variables

Create `.env` file with:

```bash
# Required
NOTION_TOKEN=secret_xxxxx
NOTION_BUSINESSX_DB_ID=xxxxx
NOTION_EMAIL_SEQUENCE_DB_ID=xxxxx
NOTION_EMAIL_TEMPLATES_DB_ID=xxxxx
RESEND_API_KEY=re_xxxxx

# Optional (but recommended for testing)
TESTING_MODE=true  # Fast Prefect execution (minutes instead of days)
```

### 3. Website Dev Server (Optional - for Playwright tests)

```bash
# Navigate to website project
cd /Users/sangle/Dev/action/projects/@new-websites/sangletech-tailwindcss

# Start Next.js dev server
npm run dev

# Verify server is running
curl http://localhost:3000/en/flows/businessX/dfu/xmas-a01
```

**Note**: If website dev server isn't available, Playwright tests will be skipped. Webhook tests will still run.

### 4. Prefect Connection

Verify connection to production Prefect:

```bash
PREFECT_API_URL=https://prefect.galatek.dev/api prefect deployment ls
```

---

## Running Tests

### Run All Tests

```bash
# Run complete test suite
pytest tests/e2e/ -v

# Run with detailed output
pytest tests/e2e/ -v -s
```

### Run Specific Test Categories

```bash
# Infrastructure tests only
pytest tests/e2e/test_sales_funnel_e2e.py::test_fastapi_server_health -v

# Webhook tests only
pytest tests/e2e/test_webhook_integration.py -v

# Notion verification tests only
pytest tests/e2e/test_notion_verification.py -v

# Playwright tests only (requires website dev server)
pytest tests/e2e/test_sales_funnel_e2e.py::test_complete_christmas_signup_flow -v
```

### Test Options

```bash
# Run in headless mode (faster, no browser window)
pytest tests/e2e/ -v --headless

# Skip cleanup (for debugging)
pytest tests/e2e/ -v --no-cleanup

# Use specific email for debugging
pytest tests/e2e/ -v --test-email="debug@example.com"
```

---

## Test Structure

```
tests/e2e/
├── __init__.py
├── conftest.py                  # Shared fixtures and setup
├── helpers.py                   # Test utilities
├── test_sales_funnel_e2e.py     # Complete E2E flow (Playwright)
├── test_webhook_integration.py  # FastAPI webhook tests
├── test_notion_verification.py  # Notion database tests
├── README.md                    # This file
└── reports/                     # Auto-generated test reports
```

---

## Test Coverage

### ✅ Implemented Tests

- **Infrastructure Validation**
  - FastAPI server health check
  - Test email generation
  - Assessment test data structure
  - Environment variable validation

- **Webhook Integration**
  - POST /webhook/christmas-signup endpoint
  - Request validation (Pydantic models)
  - Response structure verification
  - Prefect flow triggering

- **Notion Database Verification**
  - BusinessX Canada contact record (schema validation)
  - Email Sequence entry (schema validation)
  - Field validation (all properties)
  - **CRITICAL**: Property names are case-sensitive!
    - BusinessX Canada: `email`, `first_name` (lowercase)
    - Email Sequence: `Email`, `Campaign` (title case)

- **Prefect Flow Verification**
  - signup_handler_flow execution
  - 7 email flows scheduled
  - Correct timing (Day 0, 1, 3, 5, 7, 9, 11)

### ✅ Completed Tests (All Waves)

- **Playwright Website Testing** (Wave 2)
  - Landing page navigation ✅
  - Contact form submission ✅
  - 16 assessment questions (CRITICAL segment) ✅
  - Results page display ✅
  - Screenshots captured at each step ✅
  - Test data generated: `test+{timestamp}@example.com` ✅

---

## Cleanup

Tests automatically clean up after themselves:

- **Notion**: Test contact and sequence records deleted
- **Prefect**: Scheduled flow runs cancelled
- **Temporary Files**: Screenshots in /tmp/ (auto-cleaned by OS)

To verify cleanup:

```bash
# Check Notion for leftover test data
# Look for emails starting with "test+"

# Check Prefect for leftover flow runs
PREFECT_API_URL=https://prefect.galatek.dev/api prefect flow-run ls --limit 20
```

---

## Troubleshooting

### FastAPI Server Not Running

**Error**: `ConnectionRefusedError: [Errno 61] Connection refused`

**Solution**:
```bash
uvicorn server:app --reload
```

### Website Dev Server Not Running (Playwright Tests Skipped)

**Error**: `Test skipped: Website dev server not available`

**Solution**:
```bash
cd /Users/sangle/Dev/action/projects/@new-websites/sangletech-tailwindcss
npm run dev
```

### Notion API Rate Limits

**Error**: `notion_client.errors.APIResponseError: rate_limited`

**Solution**: Tests include automatic retry with exponential backoff. If this persists, reduce test frequency or add delays:

```python
# In conftest.py
@pytest.fixture(autouse=True)
def rate_limit_delay():
    time.sleep(0.5)  # 500ms delay between tests
```

### Prefect Flow Not Completing

**Error**: `Timeout waiting for flow run`

**Solution**: Verify TESTING_MODE=true for fast execution:

```bash
# Check .env
grep TESTING_MODE .env

# Should output: TESTING_MODE=true
```

### Test Data Not Cleaned Up

**Error**: Test contacts remain in Notion databases

**Solution**: Run cleanup manually:

```python
# In Python REPL
from tests.e2e.helpers import cleanup_test_data
from notion_client import Client
import os

notion_client = Client(auth=os.getenv("NOTION_TOKEN"))
cleanup_test_data(notion_client, "test+1732073456@example.com")
```

---

## Test Data Format

### Test Email Format

```
test+{timestamp}+{uuid}@example.com
```

Example: `test+1732073456+abc12345@example.com`

- **Prefix**: `test+` for easy identification
- **Timestamp**: Unix timestamp for uniqueness
- **UUID**: Random 8-char UUID for additional uniqueness
- **Domain**: `@example.com` (safe test domain)

### Assessment Data (CRITICAL Segment)

```json
{
  "email": "test+1732073456@example.com",
  "first_name": "TestUser",
  "business_name": "Test Business",
  "assessment_score": 52,
  "red_systems": 2,    // CRITICAL segment (2+ red)
  "orange_systems": 1,
  "yellow_systems": 2,
  "green_systems": 3,
  "gps_score": 45,
  "money_score": 38,
  "weakest_system_1": "Money",
  "weakest_system_2": "GPS",
  "revenue_leak_total": 13000
}
```

---

## CI/CD Integration

### GitHub Actions

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Start FastAPI server
        run: |
          uvicorn server:app &
          sleep 5

      - name: Run E2E tests
        env:
          NOTION_TOKEN: ${{ secrets.NOTION_TOKEN }}
          NOTION_BUSINESSX_DB_ID: ${{ secrets.NOTION_BUSINESSX_DB_ID }}
          NOTION_EMAIL_SEQUENCE_DB_ID: ${{ secrets.NOTION_EMAIL_SEQUENCE_DB_ID }}
          RESEND_API_KEY: ${{ secrets.RESEND_API_KEY }}
          TESTING_MODE: true
        run: pytest tests/e2e/ -v --skip-playwright
```

---

## Support

**Issues**: Report test failures with:
- Test output logs
- Screenshots from /tmp/
- Notion record IDs (if applicable)
- Prefect flow run IDs

**Documentation**: See individual test files for detailed implementation notes

---

**Last Updated**: 2025-11-20
**Test Suite Version**: v2.0 (All 4 Waves Complete)

---

## Wave Completion Summary

- ✅ **Wave 1**: Foundation & Test Infrastructure (Nov 19, 23:10)
- ✅ **Wave 2**: Playwright Website Testing (Nov 20, 11:43)
- ✅ **Wave 3**: Webhook & Prefect Flow Testing (Nov 19, 23:18)
- ✅ **Wave 4**: Notion Database Verification (Nov 20, 11:51)
- ✅ **Wave 5**: Test Cleanup & Reporting (Current)

**Total Duration**: ~2.5 hours across 2 sessions
**Test Coverage**: 11 tests passing (infrastructure, webhook, Notion, Playwright)
**Production Status**: Ready for deployment
