# Plan: Christmas Traditional Service Campaign - Complete Email Automation

**Task ID**: 1126-christmas-traditional-service-automation
**Domain**: coding
**Source**: feature_list.json

---

## Wave 0: Lead Nurture Verification (NEW - Added via /add-tasks-coding)

**Objective**: Verify 7 lead nurture templates are accessible and working from new Notion database before implementing new sequences
**Status**: Pending
**Estimated Time**: 2 hours
**Added**: 2025-11-26T23:45:00Z

### Context

The 7 lead nurture email templates have been archived and updated in a NEW Notion database:
- **New Database ID**: `2ab7c374-1115-8115-932c-ca6789c5b87b`
- **New Template Format**: `lead_nurture_email_X` (replacing `christmas_email_X`)

### Template Name Mapping

| Old Name | New Name |
|----------|----------|
| `christmas_email_1` | `lead_nurture_email_1` |
| `christmas_email_2a_critical` | `lead_nurture_email_2a_critical` |
| `christmas_email_2b_urgent` | `lead_nurture_email_2b_urgent` |
| `christmas_email_2c_optimize` | `lead_nurture_email_2c_optimize` |
| `christmas_email_3` | `lead_nurture_email_3` |
| `christmas_email_4` | `lead_nurture_email_4` |
| `christmas_email_5` | `lead_nurture_email_5` |

### Personalization Variables

- `{{first_name}}` - Contact's first name
- `{{top_red_system}}` - Highest priority red system
- `{{segment}}` - Contact segment (CRITICAL, URGENT, OPTIMIZE)
- `{{scorecard_url}}` - Link to personalized scorecard
- `{{calendly_link}}` - Booking link for discovery call

### Tasks

- [ ] 0.1: Verify 7 lead nurture templates accessible from new Notion database
  - Database ID: `2ab7c374-1115-8115-932c-ca6789c5b87b`
  - Test file: `test_notion_operations.py`
  - **Test Scenarios**:
    - `test_fetch_template_lead_nurture_email_1_exists`
    - `test_fetch_template_lead_nurture_email_2a_critical_exists`
    - `test_fetch_template_lead_nurture_email_2b_urgent_exists`
    - `test_fetch_template_lead_nurture_email_2c_optimize_exists`
    - `test_fetch_template_lead_nurture_email_3_exists`
    - `test_fetch_template_lead_nurture_email_4_exists`
    - `test_fetch_template_lead_nurture_email_5_exists`
    - `test_fetch_template_returns_correct_properties`
    - `test_fetch_template_active_status_filter`

- [ ] 0.2: Update template fetching for new Template Name format
  - Update `notion_operations.py` for new naming format
  - Test file: `test_notion_operations.py`
  - **Test Scenarios**:
    - `test_fetch_template_new_naming_format`
    - `test_fetch_template_segment_specific_2a_2b_2c`
    - `test_fetch_template_backward_compatibility`
    - `test_fetch_template_invalid_name_returns_none`

- [ ] 0.3: Test all 7 nurture emails send correctly with updated content
  - Verify via Resend API
  - Test file: `test_resend_operations.py`
  - **Test Scenarios**:
    - `test_send_lead_nurture_email_1_success`
    - `test_send_lead_nurture_email_2a_critical_success`
    - `test_send_lead_nurture_email_2b_urgent_success`
    - `test_send_lead_nurture_email_2c_optimize_success`
    - `test_send_lead_nurture_email_3_success`
    - `test_send_lead_nurture_email_4_success`
    - `test_send_lead_nurture_email_5_success`
    - `test_send_email_correct_subject_line`
    - `test_send_email_correct_body_content`

- [ ] 0.4: Verify personalization variables render correctly in updated templates
  - Ensure all variables substituted
  - Test file: `test_template_rendering.py`
  - **Test Scenarios**:
    - `test_render_first_name_variable`
    - `test_render_top_red_system_variable`
    - `test_render_segment_variable`
    - `test_render_scorecard_url_variable`
    - `test_render_calendly_link_variable`
    - `test_render_all_variables_replaced`
    - `test_render_no_unreplaced_variables_in_output`
    - `test_render_missing_variable_fallback`

### Success Criteria

- [ ] All 7 templates queryable from new Notion database
- [ ] Template fetching works with new naming format
- [ ] All 7 emails can be sent via Resend API
- [ ] All personalization variables render correctly
- [ ] No `{{variable}}` placeholders remain in output
- [ ] All 30 tests passing

---

## Wave 1: Foundation

**Objective**: Create new flow files, extend routing module, and establish test infrastructure
**Status**: Pending
**Estimated Time**: 1.5 hours

### Tasks

- [ ] 1.1: Create routing extension for new sequence types
  - Add `get_sequence_template_id()` function to `routing.py`
  - Support: noshow, postcall, onboarding sequence types
  - Test file: `test_routing.py`

- [ ] 1.2: Create no-show recovery handler flow skeleton
  - Create `noshow_recovery_handler.py` with flow decorator and parameters
  - Test file: `test_noshow_recovery_handler.py`

- [ ] 1.3: Create post-call maybe handler flow skeleton
  - Create `postcall_maybe_handler.py` with flow decorator and parameters
  - Test file: `test_postcall_maybe_handler.py`

- [ ] 1.4: Create onboarding handler flow skeleton
  - Create `onboarding_handler.py` with flow decorator and parameters
  - Test file: `test_onboarding_handler.py`

- [ ] 1.5: Add test fixtures for new sequences
  - Add Calendly no-show payload fixture
  - Add post-call data fixture
  - Add onboarding data fixture

### Success Criteria

- [ ] All new flow files created with proper structure
- [ ] `get_sequence_template_id()` returns correct templates
- [ ] Test fixtures available in `conftest.py`
- [ ] All tests passing

---

## Wave 2: No-Show Recovery Sequence

**Objective**: Implement complete no-show recovery flow with TDD (3 emails: 5min, 24h, 48h)
**Status**: Pending
**Estimated Time**: 2 hours

### Email Sequence

| Email | Template | Production Timing | Testing Timing |
|-------|----------|-------------------|----------------|
| 1 | `noshow_recovery_email_1` | 5 minutes | 1 minute |
| 2 | `noshow_recovery_email_2` | 24 hours | 2 minutes |
| 3 | `noshow_recovery_email_3` | 48 hours | 3 minutes |

### Tasks

- [ ] 2.1: Write tests for no-show recovery handler (TDD FIRST)
  - Test successful flow execution
  - Test contact not found handling
  - Test idempotency (skip if emails already sent)
  - Test Calendly payload parsing

- [ ] 2.2: Implement no-show recovery handler flow
  - Receive Calendly no-show webhook data
  - Search for contact by email
  - Create sequence tracking record

- [ ] 2.3: Implement no-show email scheduling logic
  - `schedule_noshow_emails()` function
  - Production timing: 5min, 24h, 48h
  - Testing timing: 1min, 2min, 3min

- [ ] 2.4: Add idempotency check for no-show sequence
  - Check if no-show sequence already exists for contact
  - Skip if any no-show emails already sent

### Success Criteria

- [ ] All 8 tests passing
- [ ] Idempotency prevents duplicate sequences
- [ ] Correct template IDs used
- [ ] Timing correct for both modes

---

## Wave 3: Post-Call Maybe Sequence

**Objective**: Implement post-call maybe flow with TDD (3 emails: 1h, Day 3, Day 7)
**Status**: Pending
**Estimated Time**: 2 hours

### Email Sequence

| Email | Template | Production Timing | Testing Timing |
|-------|----------|-------------------|----------------|
| 1 | `postcall_maybe_email_1` | 1 hour | 1 minute |
| 2 | `postcall_maybe_email_2` | 72 hours (Day 3) | 2 minutes |
| 3 | `postcall_maybe_email_3` | 168 hours (Day 7) | 3 minutes |

### Tasks

- [ ] 3.1: Write tests for post-call maybe handler (TDD FIRST)
  - Test successful flow execution
  - Test contact not found handling
  - Test idempotency (skip if emails already sent)
  - Test call notes variable substitution

- [ ] 3.2: Implement post-call maybe handler flow
  - Receive post-call trigger with call notes
  - Search for contact by email
  - Create sequence tracking record

- [ ] 3.3: Implement post-call email scheduling logic
  - `schedule_postcall_emails()` function
  - Production timing: 1h, 72h, 168h
  - Testing timing: 1min, 2min, 3min

- [ ] 3.4: Add idempotency check for post-call sequence
  - Check if post-call sequence already exists for contact
  - Skip if any post-call emails already sent

### Success Criteria

- [ ] All 8 tests passing
- [ ] Idempotency prevents duplicate sequences
- [ ] Call notes properly stored for template substitution
- [ ] Timing correct for both modes

---

## Wave 4: Onboarding Phase 1 Sequence

**Objective**: Implement onboarding flow with TDD (3 emails: 1h, Day 1, Day 3)
**Status**: Pending
**Estimated Time**: 2 hours

### Email Sequence

| Email | Template | Production Timing | Testing Timing |
|-------|----------|-------------------|----------------|
| 1 | `onboarding_phase1_email_1` | 1 hour | 1 minute |
| 2 | `onboarding_phase1_email_2` | 24 hours (Day 1) | 2 minutes |
| 3 | `onboarding_phase1_email_3` | 72 hours (Day 3) | 3 minutes |

### Personalization Variables

- `{{first_name}}` - Client first name
- `{{business_name}}` - Salon name
- `{{observation_dates}}` - Scheduled observation session dates
- `{{start_time}}` - Phase 1 start time
- `{{salon_address}}` - Client business location

### Tasks

- [ ] 4.1: Write tests for onboarding handler (TDD FIRST)
  - Test successful flow execution
  - Test contact not found handling
  - Test idempotency (skip if emails already sent)
  - Test all personalization variables

- [ ] 4.2: Implement onboarding handler flow
  - Receive DocuSign+payment trigger
  - Search for contact by email
  - Create sequence tracking record with onboarding data

- [ ] 4.3: Implement onboarding email scheduling logic
  - `schedule_onboarding_emails()` function
  - Production timing: 1h, 24h, 72h
  - Testing timing: 1min, 2min, 3min

- [ ] 4.4: Add idempotency check for onboarding sequence
  - Check if onboarding sequence already exists for contact
  - Skip if any onboarding emails already sent

### Success Criteria

- [ ] All 8 tests passing
- [ ] Idempotency prevents duplicate sequences
- [ ] All onboarding variables properly substituted
- [ ] Timing correct for both modes

---

## Wave 5: Integration & Webhooks

**Objective**: Add webhook endpoints to server.py, create deployments, documentation
**Status**: Pending
**Estimated Time**: 1 hour

### Tasks

- [ ] 5.1: Add Calendly no-show webhook endpoint
  - `POST /webhook/calendly-noshow`
  - Pydantic model: `CalendlyNoShowRequest`
  - Trigger: `noshow_recovery_handler_flow`

- [ ] 5.2: Add post-call maybe webhook endpoint
  - `POST /webhook/postcall-maybe`
  - Pydantic model: `PostCallMaybeRequest`
  - Trigger: `postcall_maybe_handler_flow`

- [ ] 5.3: Add onboarding start webhook endpoint
  - `POST /webhook/onboarding-start`
  - Pydantic model: `OnboardingStartRequest`
  - Trigger: `onboarding_handler_flow`

- [ ] 5.4: Create Prefect deployment configurations
  - Deploy script for all 3 new flows
  - Configure work pool: `default`
  - Enable git-based deployment

- [ ] 5.5: Update campaign documentation
  - Update `README.md` with new sequences
  - Update `STATUS.md` with deployment status

### Success Criteria

- [ ] All 3 webhook endpoints functional
- [ ] Pydantic validation working
- [ ] Deployments created on Prefect server
- [ ] Documentation updated

---

## Wave 6: E2E Testing - Lead Nurture Funnel (NEW - Added via /add-tasks-coding)

**Objective**: End-to-end browser automation testing of complete lead nurture funnel with new templates using Puppeteer
**Status**: Pending
**Estimated Time**: 1.5 hours
**Added**: 2025-11-27T00:15:00Z

### E2E Test Approach

- **Browser Automation**: Puppeteer via MCP for landing page to book-call funnel
- **API Testing**: requests library for webhook endpoint validation
- **Sequence Verification**: Notion API + Resend API monitoring

### Tasks

- [ ] 6.1: E2E: Lead nurture funnel with new templates
  - **Test Type**: Browser Automation
  - **Test File**: `e2e/test_lead_nurture_funnel.py`
  - **Verification Steps**:
    1. Navigate to localhost:3005/en/flows/businessX/dfu/xmas-a01
    2. Fill opt-in form with unique test email
    3. Complete 16-question assessment with CRITICAL segment answers
    4. Capture screenshots at landing, opt-in, questions, results
    5. Verify Prefect flow run created via API
    6. Query Notion for sequence record
    7. Monitor Resend API for 7 emails (TESTING_MODE timing)
    8. Verify personalization variables filled in emails
  - **Test Scenarios**:
    - `test_e2e_navigate_to_landing_page`
    - `test_e2e_fill_optin_form_with_test_email`
    - `test_e2e_complete_16_question_assessment`
    - `test_e2e_verify_results_page_displayed`
    - `test_e2e_verify_webhook_triggers_signup_handler`
    - `test_e2e_verify_email_sequence_created_in_notion`
    - `test_e2e_monitor_7_nurture_emails_sent`
    - `test_e2e_verify_new_template_content_in_emails`
    - `test_e2e_screenshots_at_each_step`

- [ ] 6.2: Create E2E test infrastructure
  - **Deliverables**:
    - `campaigns/christmas_campaign/tests/e2e/__init__.py`
    - `campaigns/christmas_campaign/tests/e2e/e2e_test_runner.py`
    - `campaigns/christmas_campaign/tests/e2e/conftest_e2e.py`
    - `campaigns/christmas_campaign/tests/e2e/fixtures/calendly_noshow_payload.json`
    - `campaigns/christmas_campaign/tests/e2e/fixtures/crm_postcall_payload.json`
    - `campaigns/christmas_campaign/tests/e2e/fixtures/docusign_completion_payload.json`
    - `campaigns/christmas_campaign/tests/e2e/fixtures/test_customer_data.json`

### Success Criteria

- [ ] Browser automation navigates full funnel
- [ ] Screenshots captured at each step
- [ ] Webhook triggers verified
- [ ] Email sequence monitored
- [ ] All 9 E2E tests passing

---

## Wave 7: E2E Testing - No-Show Recovery Sequence (NEW - Added via /add-tasks-coding)

**Objective**: End-to-end testing of no-show webhook integration and 3-email recovery sequence
**Status**: Pending
**Estimated Time**: 1.5 hours
**Added**: 2025-11-27T00:15:00Z

### Tasks

- [ ] 7.1: E2E: No-show recovery webhook integration
  - **Test Type**: API Integration
  - **Test File**: `e2e/test_noshow_recovery_e2e.py`
  - **Verification Steps**:
    1. POST valid Calendly no-show payload to /webhook/calendly-noshow
    2. Verify 200 response with flow_run_id
    3. POST invalid payload, verify 422 validation error
    4. POST payload missing email, verify rejection
    5. Query Prefect API for flow run status
    6. Verify flow parameters match webhook payload
  - **Test Scenarios**:
    - `test_e2e_noshow_webhook_valid_payload_accepted`
    - `test_e2e_noshow_webhook_invalid_payload_rejected`
    - `test_e2e_noshow_webhook_missing_email_rejected`
    - `test_e2e_noshow_webhook_missing_event_uri_rejected`
    - `test_e2e_noshow_webhook_triggers_prefect_flow`
    - `test_e2e_noshow_flow_run_id_returned`

- [ ] 7.2: E2E: No-show recovery email sequence
  - **Test Type**: Sequence Verification
  - **Test File**: `e2e/test_noshow_recovery_e2e.py`
  - **Expected Timing (TESTING_MODE)**:
    - Email 1: 1 minute
    - Email 2: 2 minutes
    - Email 3: 3 minutes
  - **Verification Steps**:
    1. Trigger noshow webhook with test data
    2. Query Notion for sequence record with Template Type: No-Show Recovery
    3. Wait and verify noshow_recovery_email_1 sent
    4. Wait and verify noshow_recovery_email_2 sent
    5. Wait and verify noshow_recovery_email_3 sent
    6. Verify all personalization variables filled
    7. Document flow run ID for audit
  - **Test Scenarios**:
    - `test_e2e_noshow_sequence_record_created_in_notion`
    - `test_e2e_noshow_template_type_is_noshow_recovery`
    - `test_e2e_noshow_email_1_sent_after_1min`
    - `test_e2e_noshow_email_2_sent_after_2min`
    - `test_e2e_noshow_email_3_sent_after_3min`
    - `test_e2e_noshow_correct_templates_used`
    - `test_e2e_noshow_personalization_filled`

### Success Criteria

- [ ] Webhook accepts valid Calendly payload
- [ ] Invalid payloads rejected with proper errors
- [ ] Notion sequence record created with correct Template Type
- [ ] All 3 emails sent with correct timing
- [ ] Personalization variables filled
- [ ] All 13 E2E tests passing

---

## Wave 8: E2E Testing - Post-Call Maybe Sequence (NEW - Added via /add-tasks-coding)

**Objective**: End-to-end testing of post-call webhook integration and 3-email follow-up sequence
**Status**: Pending
**Estimated Time**: 1.5 hours
**Added**: 2025-11-27T00:15:00Z

### Tasks

- [ ] 8.1: E2E: Post-call maybe webhook integration
  - **Test Type**: API Integration
  - **Test File**: `e2e/test_postcall_maybe_e2e.py`
  - **Verification Steps**:
    1. POST valid CRM post-call payload to /webhook/postcall-maybe
    2. Verify 200 response with flow_run_id
    3. POST payload with call_notes field, verify accepted
    4. POST payload with objections array, verify captured
    5. Query Prefect API for flow run status
    6. Verify call notes stored in flow parameters
  - **Test Scenarios**:
    - `test_e2e_postcall_webhook_valid_payload_accepted`
    - `test_e2e_postcall_webhook_invalid_payload_rejected`
    - `test_e2e_postcall_webhook_with_call_notes`
    - `test_e2e_postcall_webhook_with_objections`
    - `test_e2e_postcall_webhook_triggers_prefect_flow`
    - `test_e2e_postcall_flow_run_id_returned`

- [ ] 8.2: E2E: Post-call maybe email sequence
  - **Test Type**: Sequence Verification
  - **Test File**: `e2e/test_postcall_maybe_e2e.py`
  - **Expected Timing (TESTING_MODE)**:
    - Email 1: 1 minute
    - Email 2: 2 minutes
    - Email 3: 3 minutes
  - **Verification Steps**:
    1. Trigger postcall webhook with test data including call notes
    2. Query Notion for sequence record with Template Type: Post-Call Follow-Up
    3. Wait and verify postcall_maybe_email_1 sent
    4. Wait and verify postcall_maybe_email_2 sent
    5. Wait and verify postcall_maybe_email_3 sent
    6. Verify call notes appear in email content
    7. Document flow run ID for audit
  - **Test Scenarios**:
    - `test_e2e_postcall_sequence_record_created_in_notion`
    - `test_e2e_postcall_template_type_is_postcall_followup`
    - `test_e2e_postcall_email_1_sent_after_1min`
    - `test_e2e_postcall_email_2_sent_after_2min`
    - `test_e2e_postcall_email_3_sent_after_3min`
    - `test_e2e_postcall_correct_templates_used`
    - `test_e2e_postcall_call_notes_in_personalization`

### Success Criteria

- [ ] Webhook accepts valid CRM payload with call notes
- [ ] Objections array captured correctly
- [ ] Notion sequence record created with correct Template Type
- [ ] All 3 emails sent with correct timing
- [ ] Call notes appear in email personalization
- [ ] All 13 E2E tests passing

---

## Wave 9: E2E Testing - Onboarding Sequence (NEW - Added via /add-tasks-coding)

**Objective**: End-to-end testing of onboarding webhook integration and 3-email welcome sequence
**Status**: Pending
**Estimated Time**: 1.5 hours
**Added**: 2025-11-27T00:15:00Z

### Tasks

- [ ] 9.1: E2E: Onboarding webhook integration
  - **Test Type**: API Integration
  - **Test File**: `e2e/test_onboarding_e2e.py`
  - **Verification Steps**:
    1. POST valid DocuSign + payment payload to /webhook/onboarding-start
    2. Verify 200 response with flow_run_id
    3. POST payload missing payment_confirmed, verify rejection
    4. POST partial payload, verify graceful handling
    5. Query Prefect API for flow run status
    6. Verify client data stored in flow parameters
  - **Test Scenarios**:
    - `test_e2e_onboarding_webhook_valid_payload_accepted`
    - `test_e2e_onboarding_webhook_invalid_payload_rejected`
    - `test_e2e_onboarding_webhook_missing_payment_rejected`
    - `test_e2e_onboarding_webhook_partial_data_handled`
    - `test_e2e_onboarding_webhook_triggers_prefect_flow`
    - `test_e2e_onboarding_flow_run_id_returned`

- [ ] 9.2: E2E: Onboarding email sequence
  - **Test Type**: Sequence Verification
  - **Test File**: `e2e/test_onboarding_e2e.py`
  - **Expected Timing (TESTING_MODE)**:
    - Email 1: 1 minute
    - Email 2: 2 minutes
    - Email 3: 3 minutes
  - **Verification Steps**:
    1. Trigger onboarding webhook with test client data
    2. Query Notion for sequence record with Template Type: Onboarding
    3. Wait and verify onboarding_phase1_email_1 sent
    4. Wait and verify onboarding_phase1_email_2 sent
    5. Wait and verify onboarding_phase1_email_3 sent
    6. Verify salon_address appears in email
    7. Verify observation_dates appears in email
    8. Document flow run ID for audit
  - **Test Scenarios**:
    - `test_e2e_onboarding_sequence_record_created_in_notion`
    - `test_e2e_onboarding_template_type_is_onboarding`
    - `test_e2e_onboarding_email_1_sent_after_1min`
    - `test_e2e_onboarding_email_2_sent_after_2min`
    - `test_e2e_onboarding_email_3_sent_after_3min`
    - `test_e2e_onboarding_correct_templates_used`
    - `test_e2e_onboarding_salon_address_in_personalization`
    - `test_e2e_onboarding_observation_dates_in_personalization`

### Success Criteria

- [ ] Webhook accepts valid DocuSign + payment payload
- [ ] Missing payment rejected appropriately
- [ ] Notion sequence record created with correct Template Type
- [ ] All 3 emails sent with correct timing
- [ ] salon_address and observation_dates personalization filled
- [ ] All 14 E2E tests passing

---

## Wave 10: E2E Testing - Full Integration & Production Readiness (NEW - Added via /add-tasks-coding)

**Objective**: Complete multi-sequence scenario testing, production deployment verification, and E2E summary report
**Status**: Pending
**Estimated Time**: 1.5 hours
**Added**: 2025-11-27T00:15:00Z

### Tasks

- [ ] 10.1: E2E: Complete multi-sequence scenario
  - **Test Type**: Full Integration
  - **Test File**: `e2e/test_full_integration_e2e.py`
  - **Verification Steps**:
    1. Create test contact via opt-in funnel
    2. Trigger no-show webhook for same contact
    3. Verify no-show sequence starts without breaking nurture
    4. Trigger post-call maybe webhook
    5. Verify post-call sequence tracked separately
    6. Trigger onboarding webhook (simulating close)
    7. Verify all 4 sequence types have separate records
    8. Document all flow run IDs
  - **Test Scenarios**:
    - `test_e2e_full_journey_optin_to_nurture`
    - `test_e2e_full_journey_noshow_after_booking`
    - `test_e2e_full_journey_maybe_after_call`
    - `test_e2e_full_journey_onboarding_after_close`
    - `test_e2e_sequences_dont_conflict`
    - `test_e2e_idempotency_prevents_duplicates`
    - `test_e2e_proper_handoff_between_sequences`

- [ ] 10.2: E2E: Production deployment verification
  - **Test Type**: Production Verification
  - **Test File**: `e2e/test_production_readiness_e2e.py`
  - **Production API URL**: `https://prefect.galatek.dev/api`
  - **Verification Steps**:
    1. Query prefect.galatek.dev/api for deployment list
    2. Verify signup_handler deployment exists
    3. Verify noshow_recovery_handler deployment exists
    4. Verify postcall_maybe_handler deployment exists
    5. Verify onboarding_handler deployment exists
    6. Test /health endpoint on production server
    7. Verify Secret blocks: notion-token, resend-api-key, notion-db-id
    8. Verify git_clone pull step configured
  - **Test Scenarios**:
    - `test_e2e_production_signup_deployment_exists`
    - `test_e2e_production_noshow_deployment_exists`
    - `test_e2e_production_postcall_deployment_exists`
    - `test_e2e_production_onboarding_deployment_exists`
    - `test_e2e_production_health_endpoint_responds`
    - `test_e2e_production_secret_blocks_accessible`
    - `test_e2e_production_git_deployment_configured`

- [ ] 10.3: Generate E2E_TEST_SUMMARY.md report
  - **Deliverables**:
    - `E2E_TEST_SUMMARY.md` with all test results
    - Screenshots organized in `campaigns/christmas_campaign/tests/e2e/screenshots/`
    - JSON test results in `campaigns/christmas_campaign/tests/e2e/results/`
  - **Report Sections**:
    - Executive Summary
    - Test Environment Configuration
    - Lead Nurture Funnel Results
    - No-Show Recovery Sequence Results
    - Post-Call Maybe Sequence Results
    - Onboarding Sequence Results
    - Multi-Sequence Integration Results
    - Production Deployment Verification
    - Flow Run ID Audit Trail
    - Screenshots Gallery
    - Issues and Observations
    - Production Readiness Checklist

### Success Criteria

- [ ] Full customer journey simulated without conflicts
- [ ] All 4 sequence types tracked separately
- [ ] Idempotency prevents duplicates
- [ ] All 4 deployments exist on production
- [ ] Secret blocks accessible
- [ ] E2E_TEST_SUMMARY.md generated with all results
- [ ] All 14 E2E tests passing

---

## TDD Approach Summary

### Test-First Requirements

For each wave (0, 2, 3, 4):
1. **Write tests BEFORE implementation**
2. **Run tests to see them FAIL** (Red phase)
3. **Implement minimal code to pass** (Green phase)
4. **Refactor if needed** (Refactor phase)

### Test Coverage Targets

| Module | Target Coverage |
|--------|-----------------|
| `notion_operations.py` (lead nurture) | >= 80% |
| `resend_operations.py` (lead nurture) | >= 80% |
| `template_operations.py` | >= 80% |
| `noshow_recovery_handler.py` | >= 80% |
| `postcall_maybe_handler.py` | >= 80% |
| `onboarding_handler.py` | >= 80% |
| `routing.py` (extensions) | >= 90% |

### Test Commands

```bash
# Unit tests
pytest campaigns/christmas_campaign/tests/ -v --tb=short --cov=campaigns/christmas_campaign

# E2E tests
pytest campaigns/christmas_campaign/tests/e2e/ -v --tb=short -s
```

---

## Dependencies Between Waves

```
Wave 0 (Lead Nurture Verification) --- MUST COMPLETE FIRST
    |
    v
Wave 1 (Foundation)
    |
    +---> Wave 2 (No-Show) ----+
    |                          |
    +---> Wave 3 (Post-Call) --+---> Wave 5 (Integration)
    |                          |          |
    +---> Wave 4 (Onboarding) -+          |
                                          v
                               Wave 6 (E2E: Lead Nurture) ---+
                                                              |
                               Wave 7 (E2E: No-Show) ---------+
                                                              |
                               Wave 8 (E2E: Post-Call) -------+
                                                              |
                               Wave 9 (E2E: Onboarding) ------+
                                                              |
                                                              v
                               Wave 10 (E2E: Full Integration + Production)
```

**Note**:
- Wave 0 must complete first to verify template infrastructure
- Waves 2, 3, 4 can be executed in parallel after Wave 1 completes
- E2E waves (6-10) depend on implementation waves (0-5)

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| New Notion database access issues | Verify database ID and permissions in Wave 0 |
| Template naming format mismatch | Test all 7 templates explicitly in Wave 0 |
| Personalization variables missing | Test each variable renders correctly |
| Calendly webhook format unknown | Research Calendly API docs, add flexible payload parsing |
| DocuSign integration complexity | Start with manual trigger, add DocuSign webhook later |
| Multiple sequences for same contact | Each sequence type has separate tracking fields |
| E2E test flakiness | Use explicit waits, retry mechanisms, clear test isolation |
| Production deployment verification fails | Ensure Secret blocks created before testing |

---

## Estimated Total Time

| Wave | Name | Time |
|------|------|------|
| Wave 0 | Lead Nurture Verification | 2 hours |
| Wave 1 | Foundation | 1.5 hours |
| Wave 2 | No-Show Recovery | 2 hours |
| Wave 3 | Post-Call Maybe | 2 hours |
| Wave 4 | Onboarding | 2 hours |
| Wave 5 | Integration | 1 hour |
| Wave 6 | E2E: Lead Nurture Funnel | 1.5 hours |
| Wave 7 | E2E: No-Show Recovery | 1.5 hours |
| Wave 8 | E2E: Post-Call Maybe | 1.5 hours |
| Wave 9 | E2E: Onboarding | 1.5 hours |
| Wave 10 | E2E: Full Integration | 1.5 hours |
| **Total** | | **18 hours** |

---

## E2E Test Files Structure

```
campaigns/christmas_campaign/tests/
    e2e/
        __init__.py
        conftest_e2e.py                    # E2E-specific fixtures
        e2e_test_runner.py                 # Main test runner script
        test_lead_nurture_funnel.py        # Wave 6
        test_noshow_recovery_e2e.py        # Wave 7
        test_postcall_maybe_e2e.py         # Wave 8
        test_onboarding_e2e.py             # Wave 9
        test_full_integration_e2e.py       # Wave 10
        test_production_readiness_e2e.py   # Wave 10
        fixtures/
            calendly_noshow_payload.json
            crm_postcall_payload.json
            docusign_completion_payload.json
            test_customer_data.json
        screenshots/                       # Captured during tests
        results/                           # JSON test results
```
