# Discovery: Test Complete Sales Funnel Flow with Playwright, Notion Integration, and Email Delivery

## Requirements Understanding

- **Core Functionality**: Create comprehensive end-to-end testing suite for the complete sales funnel flow using Playwright to validate:
  1. Website sales funnel flow (assessment completion → webhook trigger)
  2. Prefect flow execution (signup_handler_flow → email scheduling)
  3. Notion database verification (contacts, email sequences, analytics)
  4. Email delivery validation (Resend API integration)
  5. All integrations working together seamlessly

- **User Stories**:
  - As a product owner, I need to validate that the entire sales funnel works end-to-end before going live
  - As a developer, I need to ensure webhook → Prefect → Notion → Resend integration is working correctly
  - As a QA engineer, I need automated tests that can verify the complete customer journey

- **Acceptance Criteria**:
  - ✅ Playwright tests can simulate customer filling out assessment form
  - ✅ FastAPI webhook server receives assessment data correctly
  - ✅ Prefect flows execute successfully (signup_handler_flow, send_email flows)
  - ✅ Notion databases are updated correctly (BusinessX Canada, Email Sequence, Analytics)
  - ✅ Email scheduling is verified in Prefect (7 emails for Christmas campaign)
  - ✅ All test data is verifiable via Notion integration skill
  - ✅ Tests can run in both local and production environments
  - ✅ Clear reporting of test results with pass/fail status

- **Constraints**:
  - Must use Playwright skill for browser automation
  - Must use Notion integration skill for database verification
  - Should NOT send actual emails to customer addresses (use test emails)
  - Must work with existing FastAPI webhook server (server.py)
  - Must integrate with existing Prefect flows (no modifications)
  - Tests should be repeatable and idempotent
  - Should use TESTING_MODE=true for fast execution when applicable

## Codebase Analysis

### Technology Stack

- **Automation Framework**: Playwright (via playwright-skill)
- **Backend**: FastAPI 0.115.6 (webhook server)
- **Orchestration**: Prefect v3.4.1 (self-hosted at https://prefect.galatek.dev)
- **Language**: Python 3.x
- **Database**: Notion API (notion-client==2.2.1)
- **Email**: Resend API (resend==2.19.0)
- **HTTP Client**: httpx==0.27.2
- **Testing**: pytest==8.3.4, pytest-mock==3.14.0
- **Validation**: Pydantic 2.10.4
- **Environment**: python-dotenv==1.0.1

### Relevant Files

**Primary files to interact with**:
- `server.py` - FastAPI webhook server (4 endpoints: /health, /webhook/signup, /webhook/assessment, /webhook/christmas-signup, /webhook/calcom-booking)
- `campaigns/christmas_campaign/flows/signup_handler.py` - Main signup flow
- `campaigns/christmas_campaign/flows/send_email.py` - Individual email sending flow
- `campaigns/businessx_canada_lead_nurture/flows/signup_handler.py` - BusinessX signup flow
- `campaigns/businessx_canada_lead_nurture/flows/assessment_handler.py` - Assessment processing flow

**Test files to create**:
- `tests/e2e/test_sales_funnel_playwright.py` - Main E2E test suite
- `tests/e2e/test_notion_verification.py` - Notion database verification tests
- `tests/e2e/conftest.py` - Shared fixtures and configuration

**Configuration files**:
- `.env` - Environment variables (NOTION_TOKEN, RESEND_API_KEY, etc.)
- `requirements.txt` - Dependencies
- `prefect.yaml` - Prefect deployment configuration

### Dependencies

**External packages**:
- **Playwright**: Browser automation (via playwright-skill)
- **Notion SDK**: Database verification (notion-client==2.2.1)
- **Resend**: Email API (resend==2.19.0)
- **FastAPI**: Webhook server (fastapi==0.115.6)
- **Prefect**: Orchestration (prefect==3.4.1)
- **httpx**: HTTP client for API calls
- **pytest**: Test framework

**Internal modules**:
- `campaigns.christmas_campaign.flows.signup_handler`
- `campaigns.christmas_campaign.flows.send_email`
- `campaigns.businessx_canada_lead_nurture.flows.signup_handler`
- `campaigns.businessx_canada_lead_nurture.flows.assessment_handler`
- `campaigns.christmas_campaign.tasks.notion_operations`
- `campaigns.christmas_campaign.tasks.resend_operations`

**Skills to use**:
- `playwright-skill` - For browser automation and website testing
- `notion-integration` - For database verification

### Code Patterns to Reuse

**Similar features**:
- Existing test files: `test_integration_e2e.py`, `test_flows_dry_run.py`
- Existing campaign tests: `campaigns/christmas_campaign/tests/test_signup_handler.py`
- Existing shell tests: `campaigns/christmas_campaign/tests/test_wave4_e2e.sh`

**Code to reuse**:
```python
# FastAPI webhook payload validation (from server.py)
class ChristmasSignupRequest(BaseModel):
    email: EmailStr
    first_name: str
    business_name: Optional[str]
    assessment_score: int
    red_systems: int
    orange_systems: int
    # ... more fields

# Notion query pattern (from existing tests)
from campaigns.christmas_campaign.tasks.notion_operations import (
    search_contact_by_email,
    fetch_email_template,
    create_sequence_entry
)

# Prefect flow execution pattern
from campaigns.christmas_campaign.flows.signup_handler import signup_handler_flow
result = signup_handler_flow(
    email="test@example.com",
    first_name="Test",
    # ... parameters
)
```

**Anti-patterns to avoid**:
- ❌ Don't modify production Notion databases during tests (use test databases or mocks)
- ❌ Don't send actual emails to customer addresses
- ❌ Don't hardcode credentials in test files
- ❌ Don't use deprecated import paths (flows/*, tasks/*)
- ❌ Don't skip cleanup after tests

### Architecture Understanding

**Data Flow**:
```
Website Form (Playwright simulated)
    ↓
POST /webhook/christmas-signup (FastAPI server.py)
    ↓
Christmas Signup Handler Flow (Prefect)
    ↓
├── Notion Database Updates (3 databases)
│   ├── BusinessX Canada (contacts)
│   ├── Email Sequence (tracking)
│   └── Email Analytics (metrics)
│
└── Schedule 7 Email Flows (Prefect deployments)
    ↓
    Send Email Flows (executed at scheduled times)
    ↓
    Resend API (email delivery)
```

**Module Organization**:
- Campaign-based structure: `campaigns/{campaign_name}/{flows,tasks,tests}`
- Centralized webhook server: `server.py` (entry point)
- Shared configuration: `.env`, `config/`
- Testing utilities: `tests/`, campaign-specific `tests/`

**Integration Points**:
1. **Website → FastAPI**: POST /webhook/christmas-signup with assessment data
2. **FastAPI → Prefect**: Triggers signup_handler_flow via background task
3. **Prefect → Notion**: Creates/updates contacts, sequences, analytics
4. **Prefect → Prefect**: Schedules 7 send_email flows via deployment API
5. **Prefect → Resend**: Sends emails via Resend API

**API Contracts**:
- **Christmas Signup Webhook**: POST /webhook/christmas-signup (ChristmasSignupRequest)
- **Prefect Deployment API**: POST /api/deployments/{id}/create_flow_run
- **Notion API**: Query, create, update pages in databases
- **Resend API**: Send emails via POST /emails

### Potential Conflicts

**Breaking Changes**:
- None expected - we're only adding tests, not modifying existing code

**API Changes**:
- Using skills (playwright-skill, notion-integration) instead of direct API calls
- Skills abstract the complexity and provide higher-level interfaces

**Database Migrations**:
- None required - using existing Notion databases

**Deprecations**:
- Avoid using deprecated import paths (flows/*, tasks/*)
- Use campaign-based imports instead

## Technical Constraints

**Performance Requirements**:
- Tests should complete within 5-10 minutes total
- Individual test cases should complete within 2-3 minutes
- Use TESTING_MODE=true for fast Prefect waits (minutes instead of days)

**Browser/Device Support**:
- Playwright tests should work on headless Chrome (default)
- Optional: Test on Firefox and WebKit for comprehensive coverage

**Security Considerations**:
- Use test email addresses only (e.g., test+{timestamp}@example.com)
- Load credentials from .env (never hardcode)
- Clean up test data after tests complete
- Don't expose sensitive data in test logs

**Scalability**:
- Tests should be parallelizable (each test independent)
- Use unique email addresses per test run to avoid conflicts
- Clean up test data to prevent database bloat

**Maintainability**:
- Well-documented test cases with clear descriptions
- Shared fixtures in conftest.py
- Reusable helper functions
- Clear pass/fail reporting

## Risk Assessment

### High Risk Areas

**1. Live Database Modifications**
- **Risk**: Tests could modify production Notion databases
- **Mitigation**:
  - Use test databases with separate IDs
  - OR use unique test email prefixes (e.g., test+timestamp@example.com)
  - Clean up test data after each run
  - Add safeguards to prevent accidental production writes

**2. Email Sending to Real Addresses**
- **Risk**: Tests could send emails to actual customers
- **Mitigation**:
  - Use test email addresses only
  - Consider mocking Resend API calls in tests
  - OR use Resend sandbox mode if available
  - Verify email addresses before sending

**3. Prefect Deployment API Calls**
- **Risk**: Creating unnecessary flow runs in production
- **Mitigation**:
  - Use test work pool or separate Prefect instance
  - Verify flow run parameters before creation
  - Clean up test flow runs after completion

### Medium Risk Areas

**1. Webhook Server Availability**
- **Risk**: Tests fail if server.py is not running
- **Mitigation**:
  - Start server.py automatically in test setup
  - Use health check endpoint to verify server is ready
  - Provide clear error messages if server is down

**2. Notion API Rate Limits**
- **Risk**: Tests could hit Notion API rate limits (3 requests/second)
- **Mitigation**:
  - Add delays between Notion API calls
  - Use batch operations where possible
  - Implement retry logic with exponential backoff

**3. Playwright Skill Reliability**
- **Risk**: Playwright skill may have limitations or bugs
- **Mitigation**:
  - Test skill functionality with simple examples first
  - Have fallback plan to use direct Playwright if needed
  - Document skill limitations encountered

### Low Risk Areas

**1. Test Isolation**
- **Risk**: Tests may interfere with each other
- **Mitigation**: Use unique identifiers per test (timestamps, UUIDs)

**2. Environment Configuration**
- **Risk**: Missing environment variables
- **Mitigation**: Validate .env file in test setup

## Testing Strategy

**Unit Tests**:
- Not applicable - we're testing integration, not individual units
- Existing unit tests already cover individual modules

**Integration Tests**:
- **Test 1**: Webhook → Prefect flow execution
- **Test 2**: Prefect flow → Notion database updates
- **Test 3**: Prefect flow → Email scheduling
- **Test 4**: Complete end-to-end flow (all components)

**E2E Tests**:
- **Test 1**: Simulate website form submission (Playwright)
- **Test 2**: Verify webhook triggers Prefect flow
- **Test 3**: Verify Notion databases updated correctly
- **Test 4**: Verify emails scheduled in Prefect
- **Test 5**: Verify email analytics tracking

**Manual Testing**:
- Review test data in Notion databases
- Check Prefect UI for flow runs
- Verify email scheduling (not actual sending)

**Regression Tests**:
- Ensure existing flows still work
- Verify no breaking changes to webhook API
- Confirm Notion database schemas unchanged

## Development Environment

**Setup Required**:
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Install Playwright browsers (if using direct Playwright)
# Note: playwright-skill may handle this

# 3. Configure environment variables
cp .env.example .env
# Edit .env with test credentials

# 4. Start FastAPI server
uvicorn server:app --reload

# 5. Verify Prefect connection
PREFECT_API_URL=https://prefect.galatek.dev/api prefect deployment ls
```

**Run Command**:
```bash
# Run all E2E tests
pytest tests/e2e/ -v

# Run specific test
pytest tests/e2e/test_sales_funnel_playwright.py::test_christmas_signup_flow -v

# Run with detailed output
pytest tests/e2e/ -v -s
```

**Test Command**:
```bash
# Quick validation
python test_flows_dry_run.py

# Integration tests (mocked)
python test_integration_e2e.py --mode mock
```

**Build Command**:
- Not applicable (Python project, no build step)
- Validation: `python -m py_compile tests/e2e/*.py`

## Key Technical Decisions

### Decision 1: Use Skills vs Direct API Calls

**Choice**: Use `playwright-skill` and `notion-integration` skills

**Rationale**:
- ✅ Skills provide higher-level abstractions
- ✅ Skills handle common patterns and error cases
- ✅ Faster development (less boilerplate)
- ✅ More maintainable code

**Trade-offs**:
- ⚠️ Less control over low-level details
- ⚠️ Potential skill limitations
- ⚠️ Dependency on skill implementations

### Decision 2: Test Data Strategy

**Choice**: Use unique test email addresses with timestamps

**Rationale**:
- ✅ Avoids conflicts between test runs
- ✅ Easy to identify test data in databases
- ✅ No need for complex cleanup logic
- ✅ Test data is traceable

**Trade-offs**:
- ⚠️ Database may accumulate test data over time
- ⚠️ Need periodic cleanup of old test data

### Decision 3: Testing Mode

**Choice**: Use TESTING_MODE=true for fast execution

**Rationale**:
- ✅ Tests complete in minutes instead of days
- ✅ Fast feedback loop
- ✅ Doesn't affect production flows

**Trade-offs**:
- ⚠️ Doesn't test actual production timing
- ⚠️ Need separate tests for production mode validation

### Decision 4: Webhook Server Management

**Choice**: Assume server.py is already running

**Rationale**:
- ✅ Simpler test setup
- ✅ Matches production environment (server always running)
- ✅ Allows manual server inspection during tests

**Trade-offs**:
- ⚠️ Tests fail if server not running
- ⚠️ Need clear documentation about prerequisites

## Test Scope

### In Scope

✅ Website form simulation (Playwright)
✅ Webhook endpoint testing (FastAPI)
✅ Prefect flow execution validation
✅ Notion database verification (3 databases)
✅ Email scheduling verification (Prefect)
✅ End-to-end integration testing
✅ Test data cleanup
✅ Clear test reporting

### Out of Scope

❌ Actual email sending (not testing Resend API reliability)
❌ Website development (only simulating existing website)
❌ Prefect infrastructure setup (using existing production instance)
❌ Notion database schema changes
❌ Performance/load testing
❌ Security testing (authentication, authorization)

## Success Metrics

**Test succeeds when**:
1. ✅ Playwright successfully simulates form submission
2. ✅ Webhook server receives correct data
3. ✅ Prefect flow executes without errors
4. ✅ Contact created/updated in BusinessX Canada database
5. ✅ Sequence entry created in Email Sequence database
6. ✅ 7 email flows scheduled in Prefect
7. ✅ Analytics entry created (if applicable)
8. ✅ All test data is verifiable via Notion skill
9. ✅ Test cleanup completes successfully
10. ✅ Clear pass/fail reporting provided

**Verification Methods**:
- Notion skill queries for database records
- Prefect API queries for scheduled flow runs
- FastAPI server logs for webhook calls
- Test assertions for expected values
