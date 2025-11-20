# Plan: Test Complete Sales Funnel Flow with Playwright, Notion Integration, and Email Delivery

**Task ID**: 1119-test-complete-sales-funnel-flow-with-playwright-no
**Domain**: coding
**Created**: 2025-11-19
**Status**: Planning
**Source**: Detailed planning session

---

## Implementation Strategy

### Approach
**Method**: Skill-based integration testing (playwright-skill + notion-integration)
**Paradigm**: End-to-end testing with real integrations, test-driven verification
**Estimated Time**: 6-8 hours total
**Risk Level**: Medium (involves production databases and Prefect deployments)

### Key Decisions
- **Why this approach**: Skills provide high-level abstractions for browser automation and Notion verification, reducing test complexity
- **Alternatives considered**:
  - Direct Playwright API (more control but more boilerplate)
  - Mocked integrations (faster but doesn't test real flow)
  - Manual testing (not repeatable or scalable)
- **Critical success factors**:
  - Use test email addresses to avoid production impact
  - Verify FastAPI server is running before tests
  - Clean up test data after each run
  - Use TESTING_MODE=true for fast Prefect execution

---

## Execution Waves

### Wave 1: Foundation & Test Infrastructure (45-60 min)
**Objective**: Set up test environment, verify prerequisites, create helper utilities

**Tasks**:
1. [ ] Verify prerequisites
   ```bash
   # Check FastAPI server is running
   curl http://localhost:8000/health

   # Check Prefect connection
   PREFECT_API_URL=https://prefect.galatek.dev/api prefect deployment ls

   # Verify .env configuration
   grep -E "NOTION_TOKEN|RESEND_API_KEY|TESTING_MODE" .env
   ```

2. [ ] Create test directory structure
   ```bash
   mkdir -p tests/e2e
   touch tests/e2e/__init__.py
   touch tests/e2e/conftest.py
   touch tests/e2e/test_sales_funnel_e2e.py
   touch tests/e2e/test_notion_verification.py
   touch tests/e2e/helpers.py
   ```

3. [ ] Create shared test fixtures (conftest.py)
   - Fixture for test email generation (unique timestamps)
   - Fixture for Notion database cleanup
   - Fixture for FastAPI server health check
   - Fixture for test data factory
   - Setup/teardown hooks

4. [ ] Create helper utilities (helpers.py)
   - `generate_test_email()` - Create unique test emails
   - `wait_for_prefect_flow()` - Poll Prefect API for flow completion
   - `verify_notion_record()` - Check Notion database for expected records
   - `cleanup_test_data()` - Remove test records from Notion
   - `get_assessment_test_data()` - Generate realistic assessment data

5. [ ] Commit: "chore(e2e): set up end-to-end test infrastructure"

**Success Criteria**:
- [ ] Test directory structure created
- [ ] Shared fixtures and helpers implemented
- [ ] All helper functions have docstrings
- [ ] No syntax errors (python -m py_compile tests/e2e/*.py)
- [ ] Prerequisites verified

---

### Wave 2: Playwright Website Testing (2-3 hours)
**Objective**: Use playwright-skill to test complete website sales funnel flow

**Code Organization Philosophy**:
- **Top-Down Structure**: Test cases organized from high-level scenarios to detailed steps
- **Layer 1 (Top)**: High-level test scenarios (e.g., `test_complete_christmas_signup_flow`)
- **Layer 2 (Middle)**: Page interaction helpers (e.g., `fill_assessment_form`, `submit_contact_info`)
- **Layer 3 (Bottom)**: Low-level element selectors and waits

**Test Flow**:
```
Website Landing Page
  ↓
Enter Email/Name
  ↓
Complete 16 Assessment Questions
  ↓
Trigger Webhook (POST /api/assessment/complete)
  ↓
Verify Results Page Shown
```

**Tasks**:

#### 2.1 Test Christmas Campaign Website Flow
1. [ ] Create `test_christmas_campaign_website_flow` test
   ```python
   def test_christmas_campaign_website_flow(playwright_skill, test_email):
       """
       Test complete Christmas campaign website flow:
       1. Navigate to landing page
       2. Fill in contact info
       3. Complete assessment (16 questions)
       4. Verify results page shown
       5. Verify webhook triggered
       """
       pass  # Will invoke playwright-skill
   ```

2. [ ] Use playwright-skill to:
   - Navigate to /Users/sangle/Dev/action/projects/@new-websites/sangletech-tailwindcss/pages/en/flows/businessX/dfu/xmas-a01
   - Fill contact form (email, name, business name)
   - Click through 16 assessment questions (yes/no answers)
   - Wait for results page to load
   - Verify "results saved to localStorage" console log
   - Verify POST to /api/assessment/complete was made

3. [ ] Capture test data from browser:
   - Email used
   - Assessment scores calculated
   - Timestamp of completion
   - Webhook payload sent

4. [ ] Verify with assertions:
   - Contact form accepted data
   - All 16 questions answered
   - Results page displayed
   - Console logs show successful webhook trigger

#### 2.2 Test BusinessX Canada Lead Nurture Flow (Optional)
1. [ ] Create `test_businessx_signup_flow` test (if different from Christmas)
2. [ ] Navigate to BusinessX signup page
3. [ ] Complete signup and assessment
4. [ ] Verify webhook triggered

**Implementation Details**:
```python
# Example test structure (top-down)
def test_complete_christmas_signup_flow(playwright_skill, notion_integration, test_data):
    """HIGH-LEVEL: Complete end-to-end test of Christmas campaign"""
    # 1. Navigate and fill contact form
    contact_data = fill_contact_form_on_website(playwright_skill, test_data)

    # 2. Complete assessment
    assessment_results = complete_assessment_questions(playwright_skill, test_data)

    # 3. Verify results page
    verify_results_page_displayed(playwright_skill, assessment_results)

    # 4. Verify webhook triggered
    verify_webhook_called(test_data['email'])

    # 5. Verify Notion updated
    verify_notion_databases_updated(notion_integration, test_data)

def fill_contact_form_on_website(playwright_skill, test_data):
    """MEDIUM-LEVEL: Fill contact form on landing page"""
    playwright_skill.navigate("file:///Users/sangle/Dev/action/.../xmas-a01/index.html")
    playwright_skill.fill("input[name='email']", test_data['email'])
    playwright_skill.fill("input[name='name']", test_data['name'])
    playwright_skill.click("button[type='submit']")
    return test_data

def complete_assessment_questions(playwright_skill, test_data):
    """MEDIUM-LEVEL: Answer all 16 assessment questions"""
    for i in range(16):
        answer = test_data['answers'][i]  # True/False
        if answer:
            playwright_skill.click(f"[data-question='{i}'] button.yes")
        else:
            playwright_skill.click(f"[data-question='{i}'] button.no")
        playwright_skill.wait_for(f"[data-question='{i+1}']")  # Wait for next question
    return calculate_scores_from_answers(test_data['answers'])
```

**Success Criteria**:
- [ ] Playwright successfully navigates website
- [ ] Contact form submission works
- [ ] All 16 assessment questions answered
- [ ] Results page displays correctly
- [ ] Webhook POST verified in network logs
- [ ] Test data captured for next wave

---

### Wave 3: Webhook & Prefect Flow Testing (2-3 hours)
**Objective**: Verify FastAPI webhook triggers Prefect flows correctly

**Test Flow**:
```
FastAPI Webhook Receives Data
  ↓
Triggers Prefect signup_handler_flow
  ↓
Prefect Flow Creates Notion Records
  ↓
Prefect Flow Schedules 7 Email Flows
  ↓
All Flow Runs Complete Successfully
```

**Tasks**:

#### 3.1 Test FastAPI Webhook Endpoint
1. [ ] Create `test_fastapi_christmas_webhook` test
   ```python
   def test_fastapi_christmas_webhook(test_data):
       """
       Test POST /webhook/christmas-signup directly:
       1. Send POST request with assessment data
       2. Verify 202 Accepted response
       3. Verify response includes flow run ID
       """
       response = requests.post(
           "http://localhost:8000/webhook/christmas-signup",
           json={
               "email": test_data['email'],
               "first_name": test_data['first_name'],
               "business_name": test_data['business_name'],
               "assessment_score": test_data['assessment_score'],
               "red_systems": test_data['red_systems'],
               "orange_systems": test_data['orange_systems'],
               "yellow_systems": test_data['yellow_systems'],
               "green_systems": test_data['green_systems'],
               "gps_score": test_data['gps_score'],
               "money_score": test_data['money_score'],
               "weakest_system_1": test_data['weakest_system_1'],
               "weakest_system_2": test_data['weakest_system_2'],
               "revenue_leak_total": test_data['revenue_leak_total']
           }
       )
       assert response.status_code == 202
       assert response.json()['status'] == 'accepted'
   ```

2. [ ] Verify webhook response structure
3. [ ] Capture flow run ID from response (if provided)

#### 3.2 Test Prefect Flow Execution
1. [ ] Create `test_prefect_signup_handler_flow` test
   ```python
   def test_prefect_signup_handler_flow(test_data, prefect_client):
       """
       Test Prefect signup_handler_flow execution:
       1. Wait for flow run to start
       2. Poll Prefect API for flow completion
       3. Verify flow completed successfully
       4. Verify 7 email flows scheduled
       """
       # Wait for flow to complete (use helper)
       flow_run_id = wait_for_prefect_flow(
           deployment_name="christmas-signup/production",
           email=test_data['email'],
           timeout=300  # 5 minutes
       )

       # Verify flow completed
       assert flow_run.state == "Completed"

       # Verify 7 child flow runs created
       child_runs = get_child_flow_runs(flow_run_id)
       assert len(child_runs) == 7
   ```

2. [ ] Poll Prefect API for flow completion:
   - Use `PREFECT_API_URL=https://prefect.galatek.dev/api`
   - Query flow runs by deployment and parameters
   - Wait up to 5 minutes for completion

3. [ ] Verify flow run logs:
   - Check for success messages
   - Verify no error logs
   - Confirm database operations completed

4. [ ] Verify 7 email flows scheduled:
   - Query Prefect API for child flow runs
   - Verify scheduled times (Day 0, 1, 3, 5, 7, 9, 11)
   - Confirm flow runs in "Scheduled" state

**Integration Points**:
- FastAPI server (POST /webhook/christmas-signup)
- Prefect API (https://prefect.galatek.dev/api)
- Prefect deployments (christmas-signup/production, send-email/production)

**Success Criteria**:
- [ ] Webhook endpoint returns 202 Accepted
- [ ] Prefect flow run starts within 30 seconds
- [ ] Flow run completes successfully within 5 minutes
- [ ] 7 email flows scheduled correctly
- [ ] Flow logs show no errors

---

### Wave 4: Notion Database Verification (1-2 hours)
**Objective**: Use notion-integration skill to verify all database records created correctly

**Test Flow**:
```
Query BusinessX Canada Database
  ↓
Verify Contact Record Created
  ↓
Query Email Sequence Database
  ↓
Verify Sequence Entry Created
  ↓
Query Email Analytics Database
  ↓
Verify Analytics Entry Created
```

**Tasks**:

#### 4.1 Test BusinessX Canada Database
1. [ ] Create `test_notion_businessx_database` test
   ```python
   def test_notion_businessx_database(notion_integration, test_data):
       """
       Verify contact created in BusinessX Canada database:
       1. Query database by email
       2. Verify contact record exists
       3. Verify all fields populated correctly
       """
       contact = notion_integration.query_database(
           database_id=os.getenv("NOTION_BUSINESSX_DB_ID"),
           filter={"property": "Email", "email": {"equals": test_data['email']}}
       )

       assert len(contact['results']) == 1
       record = contact['results'][0]

       # Verify properties
       assert record['properties']['First Name']['title'][0]['text']['content'] == test_data['first_name']
       assert record['properties']['Business Name']['rich_text'][0]['text']['content'] == test_data['business_name']
       assert record['properties']['Assessment Score']['number'] == test_data['assessment_score']
       assert record['properties']['Campaign']['select']['name'] == "Christmas 2025"
   ```

2. [ ] Verify all contact fields:
   - Email (unique identifier)
   - First Name
   - Business Name
   - Assessment Score
   - Red/Orange/Yellow/Green Systems
   - GPS Score, Money Score
   - Weakest System 1, Weakest System 2
   - Revenue Leak Total
   - Campaign = "Christmas 2025"

#### 4.2 Test Email Sequence Database
1. [ ] Create `test_notion_email_sequence_database` test
   ```python
   def test_notion_email_sequence_database(notion_integration, test_data):
       """
       Verify sequence entry created in Email Sequence database:
       1. Query database by email
       2. Verify sequence record exists
       3. Verify all emails scheduled
       """
       sequence = notion_integration.query_database(
           database_id=os.getenv("NOTION_EMAIL_SEQUENCE_DB_ID"),
           filter={"property": "Email", "email": {"equals": test_data['email']}}
       )

       assert len(sequence['results']) == 1
       record = sequence['results'][0]

       # Verify sequence properties
       assert record['properties']['Campaign']['select']['name'] == "Christmas 2025"
       assert record['properties']['Status']['select']['name'] == "Active"
       assert record['properties']['Emails Scheduled']['number'] == 7
       assert record['properties']['Total Emails']['number'] == 7
   ```

2. [ ] Verify sequence entry fields:
   - Email
   - Campaign = "Christmas 2025"
   - Status = "Active"
   - Emails Scheduled = 7
   - Total Emails = 7
   - Sequence ID (UUID)
   - Started Date

#### 4.3 Test Email Analytics Database (Optional)
1. [ ] Create `test_notion_email_analytics_database` test
2. [ ] Verify analytics entry created
3. [ ] Verify initial metrics (emails_sent=0, opens=0, clicks=0)

**Implementation Details**:
```python
# Example Notion verification (top-down)
def verify_notion_databases_updated(notion_integration, test_data):
    """HIGH-LEVEL: Verify all 3 Notion databases updated"""
    contact = verify_contact_in_businessx_db(notion_integration, test_data)
    sequence = verify_sequence_in_email_sequence_db(notion_integration, test_data)
    analytics = verify_analytics_entry(notion_integration, test_data)
    return {"contact": contact, "sequence": sequence, "analytics": analytics}

def verify_contact_in_businessx_db(notion_integration, test_data):
    """MEDIUM-LEVEL: Query and verify contact record"""
    results = query_notion_database(
        notion_integration,
        database_id=os.getenv("NOTION_BUSINESSX_DB_ID"),
        filter_email=test_data['email']
    )
    assert_contact_fields_correct(results[0], test_data)
    return results[0]

def query_notion_database(notion_integration, database_id, filter_email):
    """LOW-LEVEL: Execute Notion database query"""
    return notion_integration.query_database(
        database_id=database_id,
        filter={"property": "Email", "email": {"equals": filter_email}}
    )['results']
```

**Success Criteria**:
- [ ] Contact record found in BusinessX Canada database
- [ ] All contact fields populated correctly
- [ ] Sequence entry found in Email Sequence database
- [ ] Sequence status = "Active", emails_scheduled = 7
- [ ] Analytics entry created (if applicable)
- [ ] No duplicate records created

---

### Wave 5: Test Cleanup & Reporting (45-60 min)
**Objective**: Clean up test data, generate comprehensive test report, finalize documentation

**Tasks**:
1. [ ] Implement cleanup fixtures
   ```python
   @pytest.fixture(scope="function", autouse=True)
   def cleanup_test_data(request, notion_integration, test_data):
       """
       Cleanup fixture that runs after each test:
       1. Delete contact from BusinessX Canada database
       2. Delete sequence from Email Sequence database
       3. Delete analytics entry (if created)
       4. Cancel scheduled Prefect flow runs
       """
       yield  # Test runs here

       # Cleanup after test
       try:
           delete_notion_contact(notion_integration, test_data['email'])
           delete_notion_sequence(notion_integration, test_data['email'])
           cancel_scheduled_flows(test_data['email'])
           print(f"✅ Cleanup complete for {test_data['email']}")
       except Exception as e:
           print(f"⚠️  Cleanup failed: {e}")
   ```

2. [ ] Create test report generator
   ```python
   def generate_test_report(test_results):
       """
       Generate comprehensive test report:
       - Summary (total, passed, failed, skipped)
       - Detailed results per test case
       - Performance metrics (execution time)
       - Notion records created/verified
       - Prefect flow runs created
       - Cleanup status
       """
       report = {
           "summary": {
               "total": len(test_results),
               "passed": sum(1 for r in test_results if r['status'] == 'passed'),
               "failed": sum(1 for r in test_results if r['status'] == 'failed'),
               "execution_time": sum(r['duration'] for r in test_results)
           },
           "details": test_results,
           "notion_records": get_notion_records_summary(),
           "prefect_flows": get_prefect_flows_summary(),
           "cleanup": get_cleanup_summary()
       }
       return report
   ```

3. [ ] Add comprehensive logging
   - Test start/end timestamps
   - Each major step with duration
   - Errors with full stack traces
   - Notion record IDs created
   - Prefect flow run IDs

4. [ ] Create README for test suite
   ```markdown
   # End-to-End Sales Funnel Tests

   ## Overview
   Tests complete sales funnel flow from website to email scheduling.

   ## Prerequisites
   - FastAPI server running (uvicorn server:app --reload)
   - .env file configured with Notion and Resend credentials
   - TESTING_MODE=true for fast execution
   - Prefect connection to https://prefect.galatek.dev

   ## Running Tests
   ```bash
   # Run all E2E tests
   pytest tests/e2e/ -v

   # Run specific test
   pytest tests/e2e/test_sales_funnel_e2e.py::test_complete_christmas_signup_flow -v

   # Run with detailed output
   pytest tests/e2e/ -v -s
   ```

   ## Test Coverage
   - ✅ Website form submission (Playwright)
   - ✅ FastAPI webhook triggering
   - ✅ Prefect flow execution
   - ✅ Notion database updates (3 databases)
   - ✅ Email scheduling (7 emails)
   - ✅ Complete integration flow
   ```

5. [ ] Commit: "test(e2e): add comprehensive end-to-end sales funnel tests"

6. [ ] Final validation:
   - Run all tests: `pytest tests/e2e/ -v`
   - Verify cleanup: Check Notion databases for leftover test data
   - Review test report: Ensure all tests passed
   - Check code quality: Linting, type hints, docstrings

**Documentation Needs**:
- **README.md** in tests/e2e/ directory
- **Inline comments** for complex test logic
- **Docstrings** for all test functions
- **Test data examples** in documentation
- **Troubleshooting guide** for common issues

**Success Criteria**:
- [ ] Cleanup fixtures implemented and working
- [ ] All test data removed after tests
- [ ] Test report generated automatically
- [ ] Comprehensive logging throughout tests
- [ ] README documentation complete
- [ ] All tests passing (100% success rate)
- [ ] Code quality checks passed (linting, type hints)
- [ ] No leftover test data in Notion databases
- [ ] No leftover Prefect flow runs

---

## Quality & Validation Checklist

Before considering complete:
- [ ] All website flows tested (Playwright)
- [ ] All webhook endpoints tested
- [ ] All Prefect flows verified
- [ ] All 3 Notion databases verified
- [ ] Email scheduling verified (7 emails)
- [ ] Test cleanup working correctly
- [ ] No test data left in production databases
- [ ] Test report generated successfully
- [ ] Code quality: Linting passed
- [ ] Code quality: Type hints added
- [ ] Code quality: Docstrings complete
- [ ] Documentation: README complete
- [ ] Documentation: Inline comments added
- [ ] Documentation: Troubleshooting guide included
- [ ] All tests passing (100% success rate)
- [ ] Performance: Tests complete in < 10 minutes
- [ ] Security: No credentials in code
- [ ] Security: Only test emails used

---

## Rollback & Contingency Plan

**If blocked or failed:**

1. **Stop immediately** - Don't continue if stuck

2. **Document blocker** in `BLOCKERS.md` with:
   - What you were trying
   - What failed
   - Error messages
   - What you've tried to fix it

3. **Preserve work**: Commit WIP to branch
   ```bash
   git add .
   git commit -m "wip(e2e): [what was being done]

   Blocked on: [specific issue]
   See BLOCKERS.md for details"
   ```

4. **Offer options**:
   - Option A: Skip Playwright and test webhook directly (faster but less comprehensive)
   - Option B: Use mocked integrations instead of real Notion/Prefect (faster but less realistic)
   - Option C: Test individual components separately (more manageable)
   - Option D: User provides guidance on how to proceed

5. **Don't force it** - Quality over speed

**Common Blockers & Solutions**:

**Blocker 1: Playwright skill not working**
- **Solution A**: Use direct Playwright API instead
- **Solution B**: Test only webhook → Prefect → Notion flow
- **Solution C**: Use Selenium as fallback

**Blocker 2: Notion API rate limits**
- **Solution A**: Add delays between API calls (time.sleep(0.5))
- **Solution B**: Use batch operations
- **Solution C**: Reduce number of test cases

**Blocker 3: Prefect flows not completing**
- **Solution A**: Increase timeout (from 5min to 10min)
- **Solution B**: Use TESTING_MODE=true for faster waits
- **Solution C**: Test with mocked Prefect flows

---

## Dependencies & Risk Management

**External Dependencies**:
- **playwright-skill**: Browser automation
  - Alternatives: Direct Playwright, Selenium
  - Risk: Skill may have limitations
  - Mitigation: Test skill first, have fallback ready

- **notion-integration**: Database verification
  - Alternatives: Direct Notion API calls
  - Risk: Rate limits, skill limitations
  - Mitigation: Add delays, use batch operations

- **FastAPI server**: Must be running on localhost:8000
  - Alternatives: Start server automatically in tests
  - Risk: Server not running, port conflict
  - Mitigation: Health check in test setup

- **Prefect**: Production instance at https://prefect.galatek.dev
  - Alternatives: Use test Prefect instance
  - Risk: Deployment changes, API unavailable
  - Mitigation: Use stable deployment IDs, handle errors gracefully

**Risks**:
- **High Risk**: Test data left in production databases
  - Mitigation: Cleanup fixtures, unique test emails, manual verification
  - Detection: Query Notion for emails containing "test"
  - Recovery: Manual cleanup script

- **High Risk**: Emails sent to real customers
  - Mitigation: Only use test email addresses, verify email before sending
  - Detection: Check Resend dashboard for sent emails
  - Recovery: No recovery needed if using test emails

- **Medium Risk**: Playwright skill limitations
  - Monitoring: Test skill with simple examples first
  - Plan B: Use direct Playwright API
  - Detection: Skill returns errors or unexpected results

- **Medium Risk**: Notion API rate limits
  - Monitoring: Track API call frequency
  - Plan B: Add delays, reduce test cases
  - Detection: Notion API returns 429 errors

- **Low Risk**: Prefect API unavailable
  - Acceptance: Tests will fail, retry later
  - Detection: Connection errors to Prefect API

---

## Success Definition

This plan succeeds when:
- ✅ All 5 waves completed
- ✅ Quality checklist 100% satisfied
- ✅ Comprehensive E2E tests written and passing
- ✅ Playwright successfully tests website flow
- ✅ Notion databases verified correctly
- ✅ Prefect flow scheduling verified
- ✅ Test cleanup working (no leftover data)
- ✅ Test report generated automatically
- ✅ Documentation complete (README, comments, docstrings)
- ✅ Ready for continuous integration (CI/CD)

---

## Usage After Implementation

**Running Tests**:
```bash
# Prerequisites
uvicorn server:app --reload  # Start FastAPI server
export TESTING_MODE=true     # Fast execution

# Run all E2E tests
pytest tests/e2e/ -v

# Run specific test
pytest tests/e2e/test_sales_funnel_e2e.py::test_complete_christmas_signup_flow -v

# Run with detailed output and cleanup verification
pytest tests/e2e/ -v -s --cleanup-verify
```

**Test Report**:
- Automatically generated in `tests/e2e/reports/`
- Includes: summary, detailed results, Notion records, Prefect flows, cleanup status
- View with: `cat tests/e2e/reports/latest_report.json`

**Troubleshooting**:
- See `tests/e2e/README.md` for common issues
- Check `tests/e2e/reports/` for detailed error logs
- Verify prerequisites with `pytest tests/e2e/ --check-prerequisites`
