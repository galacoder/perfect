# Plan: Port Prefect Christmas Automation to Kestra

**Task ID**: 1129-port-prefect-to-kestra
**Domain**: CODING
**Source**: feature_list.json
**Estimated Effort**: 34 hours

---

## CRITICAL ARCHITECTURAL DECISION: Website/Kestra Email Responsibility Split

**Decision Date**: 2025-11-29
**Impact**: Affects all handler flows and E2E testing

### Email Responsibility Matrix

| Sequence Type | Email | Sent By | Notes |
|--------------|-------|---------|-------|
| **Signup** | Confirmation | Website | Immediate on form submit |
| **5-Day Nurture** | Email #1 | Website | Immediate after assessment |
| **5-Day Nurture** | Emails #2-5 | Kestra | Scheduled from email_1_sent_at |
| **No-Show Recovery** | All 3 | Kestra | Triggered by Calendly webhook |
| **Post-Call Maybe** | All 3 | Kestra | Triggered by CRM webhook |
| **Onboarding** | All 3 | Kestra | Triggered by payment webhook |

### Webhook Payload Requirement

Assessment webhook MUST include `email_1_sent_at` timestamp:

```json
{
  "email": "user@example.com",
  "red_systems": 2,
  "orange_systems": 1,
  "email_1_sent_at": "2025-11-29T10:30:00Z",
  "email_1_status": "sent"
}
```

### Why This Matters

- Prevents duplicate emails (website + Kestra both sending Email #1)
- Ensures proper sequencing (Email #2 timing based on Email #1 send time)
- Simplifies Kestra flows (less email sending logic)
- Signup handler becomes tracking-only (no email responsibility)

---

## Overview

This plan migrates the Christmas Campaign marketing automation from Prefect v3.4.1 to Kestra, a YAML-based orchestration platform. The migration includes 5 Prefect flows, 3 task modules, webhook server integration, and comprehensive testing.

---

## Wave 1: Foundation
**Objective**: Set up Kestra Docker Compose infrastructure, secrets management, and basic health checks
**Estimated Hours**: 4
**Status**: Pending

### Tasks

- [ ] **1.1**: Create Docker Compose for Kestra + PostgreSQL [HIGH]
  - Test: `tests/kestra/test_docker_compose.py`
  - Create `docker-compose.yml` with Kestra and PostgreSQL services
  - Configure networking and volume mounts
  - Verify container startup

- [ ] **1.2**: Configure Kestra secrets from Prefect Secret blocks [HIGH]
  - Test: `tests/kestra/test_secrets.py`
  - Create `.env.kestra` with base64-encoded secrets
  - Map Prefect secrets to Kestra SECRET_ prefix format
  - Required secrets: NOTION_TOKEN, RESEND_API_KEY, DB IDs, TESTING_MODE

- [ ] **1.3**: Create Kestra health check flow [MEDIUM]
  - Test: `tests/kestra/test_health_flow.py`
  - Create `kestra/flows/christmas/health-check.yml`
  - Verify secret access and API connectivity

- [ ] **1.4**: Set up Kestra flow directory structure [MEDIUM]
  - Create `kestra/flows/christmas/` directory
  - Configure namespace: `christmas`

### Success Criteria
- [ ] Docker Compose starts without errors
- [ ] Kestra UI accessible at http://localhost:8080
- [ ] Health check flow executes successfully
- [ ] All secrets resolve correctly

---

## Wave 2: Core Flow Migration
**Objective**: Port send_email_flow, routing logic, and Email #1 skip logic to Kestra YAML
**Estimated Hours**: 10
**Status**: Pending

### Tasks

- [ ] **2.1**: Port routing.py logic to Kestra-compatible format [HIGH]
  - Test: `tests/kestra/test_routing.py`
  - Convert `classify_segment()` to Python script task
  - Convert `get_email_template_id()` to lookup table
  - Handle segment classification: CRITICAL/URGENT/OPTIMIZE

- [ ] **2.2**: Create Notion HTTP tasks (search, create, update, sequence tracker) [HIGH] **(MODIFIED)**
  - Test: `tests/kestra/test_notion_tasks.py`
  - Create reusable HTTP Request tasks for:
    - `search_contact_by_email`
    - `create_email_sequence`
    - `update_email_sequence`
    - `fetch_email_template`
    - `update_sequence_tracker_per_email` **(NEW)** - Called AFTER each email send
  - **Test Requirements**:
    - Test Notion update payload structure for sequence tracker
    - Test email_number field populated correctly
    - Test sent_at timestamp in ISO 8601 format
    - Test sent_by='kestra' for all Kestra-sent emails
    - Test resend_id captured from Resend API response

- [ ] **2.3**: Create Resend HTTP tasks (send email) [HIGH]
  - Test: `tests/kestra/test_resend_tasks.py`
  - Create HTTP POST task for Resend API
  - Handle template variable substitution
  - Configure From/To email headers

- [ ] **2.4**: Port send_email_flow to Kestra YAML with Notion tracking [HIGH] **(MODIFIED)**
  - Test: `tests/kestra/test_send_email_flow.py`
  - Create `kestra/flows/christmas/send-email.yml`
  - Implement:
    - Idempotency check (query Notion first)
    - Template fetch from Notion
    - Variable substitution
    - Send via Resend
    - **CRITICAL**: Update Notion Sequence Tracker AFTER each successful email send
    - **CRITICAL**: Update Contact database with last_email_sent timestamp
  - **Notion Sequence Tracker Update Payload**:
    ```json
    {
      "email_number": 2,
      "sent_at": "2025-11-29T10:30:00Z",
      "status": "sent",
      "resend_id": "email_xyz123",
      "sent_by": "kestra"
    }
    ```
  - **Error Handling**: Notion update failure logs error but does NOT block email flow

- [ ] **2.5**: Create email scheduling subflow mechanism (Emails #2-5 only) [HIGH] **(MODIFIED)**
  - Test: `tests/kestra/test_email_scheduling.py`
  - Use `io.kestra.plugin.core.flow.Subflow` with `scheduleDate`
  - **CRITICAL**: For 5-day sequence, schedule only Emails #2-5 (Email #1 sent by website)
  - Calculate delays relative to `email_1_sent_at` timestamp from webhook payload
  - Production: Email #2 at +24h, #3 at +72h, #4 at +96h, #5 at +120h from email_1_sent_at
  - Testing: #2 at +1min, #3 at +2min, #4 at +3min, #5 at +4min
  - **Test Requirements**:
    - Test scheduling starts from Email #2 (not Email #1)
    - Test Email #2 delay calculated from email_1_sent_at timestamp
    - Test missing email_1_sent_at defaults to webhook trigger time

- [ ] **2.6**: Implement Notion template fetching with fallback [HIGH]
  - Test: `tests/kestra/test_notion_templates.py`
  - Fetch email templates dynamically from Notion Templates database
  - Support all sequences: 5-day nurture, no-show recovery, post-call maybe, onboarding
  - Implement fallback to static templates if Notion fetch fails
  - Handle personalization variable substitution (first_name, business_name, segment)
  - **Dependencies**: 2.2 (Notion HTTP tasks)
  - **Test Requirements**:
    - Mock Notion template API responses
    - Test template rendering with personalization variables
    - Test fallback to static templates on API failure
    - Test all 4 sequence types
    - Test empty template handling

- [ ] **2.7**: Create webhook payload validator with email_1_sent_at support [HIGH] **(NEW)**
  - Test: `tests/kestra/test_webhook_payload_validator.py`
  - Validate incoming webhook payloads for assessment handler
  - **CRITICAL**: Accept `email_1_sent_at` timestamp and `email_1_status` fields from website
  - Validate timestamp format (ISO 8601)
  - Fall back to webhook trigger time if `email_1_sent_at` missing (with warning log)
  - **Test Requirements**:
    - Test valid payload with email_1_sent_at ISO 8601 timestamp
    - Test valid payload with email_1_status='sent'
    - Test missing email_1_sent_at defaults to current time with warning log
    - Test invalid timestamp format rejected with error
    - Test payload schema validation for assessment data (red_systems, orange_systems)
    - Test email_1_sent_at used to calculate Email #2 schedule time

- [ ] **2.8**: Create dedicated Notion Sequence Tracker update task [HIGH] **(NEW)**
  - Test: `tests/kestra/test_notion_sequence_tracker.py`
  - Create reusable Kestra task for updating Notion Sequence Tracker after EVERY email send
  - Called by send_email_flow and all handler flows
  - **Payload Structure**:
    ```json
    {
      "properties": {
        "Email Number": { "number": 2 },
        "Sent At": { "date": { "start": "2025-11-29T10:30:00Z" } },
        "Status": { "select": { "name": "sent" } },
        "Sent By": { "select": { "name": "kestra" } },
        "Resend ID": { "rich_text": [{ "text": { "content": "email_xyz" } }] },
        "Sequence Type": { "select": { "name": "5day" } }
      }
    }
    ```
  - **Error Handling**: Log failure but return success to not block email flow
  - Also updates Contact database with `last_email_sent` timestamp
  - **Test Requirements**:
    - Test payload structure for Notion API
    - Test all sequence types: 5day, noshow, postcall, onboarding
    - Test sent_by='kestra' for Kestra emails, 'website' for Email #1
    - Test API failure returns success (does not block email)
    - Test idempotency on duplicate updates

### Success Criteria
- [ ] Routing logic matches Prefect behavior
- [ ] Notion API tasks work with authentication
- [ ] Resend API sends emails correctly
- [ ] Email scheduling respects delays relative to email_1_sent_at
- [ ] send_email_flow passes all tests
- [ ] Templates fetched from Notion (not hardcoded)
- [ ] Fallback to static templates works on API failure
- [ ] Webhook payload validator accepts email_1_sent_at
- [ ] **Notion Sequence Tracker updated after EVERY email send** **(NEW)**
- [ ] **Contact database updated with last_email_sent** **(NEW)**
- [ ] **Notion update failure does NOT block email sending** **(NEW)**

---

## Wave 3: Handler Flows Migration
**Objective**: Port all 4 handler flows (signup=tracking only, assessment=Emails #2-5, noshow, postcall, onboarding) to Kestra
**Estimated Hours**: 10
**Status**: Pending

### Tasks

- [ ] **3.1**: Port signup_handler_flow to Kestra YAML (TRACKING ONLY - NO EMAIL) [HIGH] **(MODIFIED)**
  - Test: `tests/kestra/test_signup_handler_flow.py`
  - Create `kestra/flows/christmas/signup-handler.yml`
  - Webhook trigger configuration
  - **CRITICAL CHANGE**: This handler does NOT send any emails
  - Website handles signup confirmation email directly
  - Steps:
    1. Parse webhook body (email, first_name, business_name)
    2. Search/create contact in Notion
    3. Log signup event for analytics
    4. **NO email scheduling**
  - **Test Requirements**:
    - Test webhook trigger parses payload correctly
    - Test contact created/updated in Notion
    - Test NO emails are sent or scheduled by this handler
    - Test signup event logged for analytics
    - Test idempotency (duplicate signups handled)

- [ ] **3.2**: Port noshow_recovery_handler_flow to Kestra YAML with Notion tracking [MEDIUM] **(MODIFIED)**
  - Test: `tests/kestra/test_noshow_handler_flow.py`
  - Create `kestra/flows/christmas/noshow-recovery-handler.yml`
  - Webhook trigger for Calendly no-show events
  - **Kestra handles ALL 3 emails** for this sequence (no website involvement)
  - Schedule 3-email recovery sequence (5min, 24h, 48h)
  - **CRITICAL**: Each email MUST update Notion Sequence Tracker after successful send
  - **Test Requirements**:
    - Test Email #1 updates Notion Sequence Tracker with email_number=1, sent_by='kestra'
    - Test Email #2 updates Notion Sequence Tracker with email_number=2, sent_by='kestra'
    - Test Email #3 updates Notion Sequence Tracker with email_number=3, sent_by='kestra'
    - Test Notion update failure does NOT block email sending

- [ ] **3.3**: Port postcall_maybe_handler_flow to Kestra YAML with Notion tracking [MEDIUM] **(MODIFIED)**
  - Test: `tests/kestra/test_postcall_handler_flow.py`
  - Create `kestra/flows/christmas/postcall-maybe-handler.yml`
  - Webhook trigger for CRM "maybe" outcome
  - **Kestra handles ALL 3 emails** for this sequence (no website involvement)
  - Schedule 3-email follow-up (1h, 72h, 168h)
  - **CRITICAL**: Each email MUST update Notion Sequence Tracker after successful send
  - **Test Requirements**:
    - Test Email #1 updates Notion Sequence Tracker with email_number=1, sent_by='kestra'
    - Test Email #2 updates Notion Sequence Tracker with email_number=2, sent_by='kestra'
    - Test Email #3 updates Notion Sequence Tracker with email_number=3, sent_by='kestra'
    - Test Notion update failure does NOT block email sending

- [ ] **3.4**: Port onboarding_handler_flow to Kestra YAML with Notion tracking [MEDIUM] **(MODIFIED)**
  - Test: `tests/kestra/test_onboarding_handler_flow.py`
  - Create `kestra/flows/christmas/onboarding-handler.yml`
  - Webhook trigger for DocuSign + payment
  - Validate payment before proceeding
  - **Kestra handles ALL 3 emails** for this sequence (no website involvement)
  - Schedule 3-email welcome sequence (1h, 24h, 72h)
  - **CRITICAL**: Each email MUST update Notion Sequence Tracker after successful send
  - **Test Requirements**:
    - Test Email #1 updates Notion Sequence Tracker with email_number=1, sent_by='kestra'
    - Test Email #2 updates Notion Sequence Tracker with email_number=2, sent_by='kestra'
    - Test Email #3 updates Notion Sequence Tracker with email_number=3, sent_by='kestra'
    - Test Notion update failure does NOT block email sending

- [ ] **3.5**: Create assessment_handler_flow for 5-day sequence (Emails #2-5 only) with per-email Notion tracking [HIGH] **(MODIFIED)**
  - Test: `tests/kestra/test_assessment_handler_flow.py`
  - Create `kestra/flows/christmas/assessment-handler.yml`
  - **CRITICAL**: Website sends Email #1 immediately after assessment
  - This handler receives assessment data WITH `email_1_sent_at` timestamp
  - Steps:
    1. Parse webhook with email_1_sent_at timestamp
    2. Validate Email #1 was sent by website
    3. Classify segment (CRITICAL/URGENT/OPTIMIZE)
    4. Update Notion sequence tracker (mark Email #1 as 'sent_by_website')
    5. Schedule Emails #2-5 with delays relative to email_1_sent_at
    6. **CRITICAL**: Each of Emails #2-5 MUST update Notion Sequence Tracker after send
  - **Test Requirements**:
    - Test webhook parses email_1_sent_at timestamp correctly
    - Test segment classification (CRITICAL/URGENT/OPTIMIZE)
    - Test Notion sequence tracker shows Email #1 as 'sent_by_website'
    - Test only Emails #2-5 are scheduled (NOT Email #1)
    - Test Email #2 scheduled at email_1_sent_at + 24h (production)
    - Test Email #2 scheduled at email_1_sent_at + 1min (testing mode)
    - Test missing email_1_sent_at logs warning and uses webhook time
    - Test idempotency (duplicate assessments handled)
    - **Test Email #2 updates Notion Sequence Tracker with email_number=2, sent_by='kestra'** **(NEW)**
    - **Test Email #3 updates Notion Sequence Tracker with email_number=3, sent_by='kestra'** **(NEW)**
    - **Test Email #4 updates Notion Sequence Tracker with email_number=4, sent_by='kestra'** **(NEW)**
    - **Test Email #5 updates Notion Sequence Tracker with email_number=5, sent_by='kestra'** **(NEW)**
    - **Test Contact database updated with last_email_sent after each email** **(NEW)**
    - **Test Notion update failure does NOT block email sending** **(NEW)**

- [ ] **3.6**: Create email analytics logging task [LOW] **(MODIFIED)**
  - Test: `tests/kestra/test_analytics_task.py`
  - HTTP POST to Notion Email Analytics database
  - Log: email, template_id, email_number, status, timestamp
  - **NEW**: Include `sent_by` field to distinguish website-sent vs Kestra-sent emails

### Success Criteria
- [ ] Signup handler creates contacts but does NOT send emails
- [ ] Assessment handler schedules only Emails #2-5 based on email_1_sent_at
- [ ] Secondary handlers (noshow, postcall, onboarding) send ALL their emails
- [ ] Idempotency works for all flows
- [ ] Error handling matches Prefect behavior
- [ ] Notion sequence tracker shows Email #1 as 'sent_by_website'
- [ ] **Every email sent by Kestra updates Notion Sequence Tracker** **(NEW)**
- [ ] **Notion tracker shows correct email_number for each email** **(NEW)**
- [ ] **Notion tracker shows sent_by='kestra' for Kestra-sent emails** **(NEW)**
- [ ] **Contact database updated with last_email_sent after each email** **(NEW)**
- [ ] **Notion update failures do NOT block email sending** **(NEW)**

---

## Wave 4: Website Integration & Deployment
**Objective**: Update webhook URLs, production deployment, E2E testing with website/Kestra email split
**Estimated Hours**: 10
**Status**: Pending

### Tasks

- [ ] **4.1**: Create FastAPI proxy for Kestra webhooks (optional) [MEDIUM]
  - Test: `tests/kestra/test_webhook_proxy.py`
  - Option A: Update server.py to proxy to Kestra webhooks
  - Option B: Document direct Kestra webhook URLs
  - Decision: Depends on existing infrastructure

- [ ] **4.2**: Update sangletech-tailwindcss webhook URLs [HIGH]
  - No test (documentation only)
  - Document URL changes for frontend team:
    - `/webhook/christmas-signup` -> Kestra URL (tracking only)
    - `/webhook/christmas-assessment` -> Kestra URL (schedules Emails #2-5)
    - `/webhook/calendly-noshow` -> Kestra URL
    - etc.

- [ ] **4.3**: Create production docker-compose for homelab [HIGH]
  - Test: `tests/kestra/test_production_compose.py`
  - Create `docker-compose.prod.yml`
  - External PostgreSQL configuration
  - Persistent storage volumes
  - Production secrets management

- [ ] **4.4**: E2E test: Assessment to email delivery (Emails #2-5 only) [HIGH] **(MODIFIED)**
  - Test: `tests/kestra/e2e/test_assessment_e2e.py`
  - **CRITICAL**: Mock website sending Email #1 first
  - Full flow test:
    1. Mock website sending Email #1
    2. POST assessment webhook with email_1_sent_at timestamp
    3. Verify Notion sequence shows Email #1 as 'sent_by_website'
    4. Verify only 4 emails scheduled by Kestra (#2-5)
    5. Verify Email #2 timing relative to email_1_sent_at
    6. Verify Resend delivery for Email #2

- [ ] **4.5**: E2E test: All handler flows [MEDIUM]
  - Test: `tests/kestra/e2e/test_all_handlers_e2e.py`
  - Test noshow, postcall, onboarding handlers
  - Verify complete flow execution (all emails from Kestra)

- [ ] **4.6**: Documentation: Website/Kestra responsibility split + migration guide [HIGH] **(MODIFIED)**
  - No test (documentation)
  - Create `KESTRA_MIGRATION.md`
  - **CRITICAL**: Include clear documentation of email responsibility split
  - Document:
    - Migration patterns
    - Prefect -> Kestra mapping
    - Email responsibility matrix (website vs Kestra)
    - Webhook payload schema with email_1_sent_at
    - Sequence diagrams showing website->Kestra handoff
    - Maintenance procedures
    - Rollback plan

- [ ] **4.7**: Puppeteer E2E: Assessment sales funnel (website + Kestra split) [HIGH] **(MODIFIED)**
  - Test: `tests/kestra/e2e/test_puppeteer_assessment_funnel.py`
  - Automated browser testing for complete assessment funnel
  - **CRITICAL**: Verify website sends Email #1, then Kestra sends Emails #2-5
  - **Test Requirements**:
    - Navigate to funnel URL (localhost:3005 or sangletech.com)
    - Fill assessment form with test data (lengobaosang@gmail.com)
    - Submit form and verify website sends Email #1 immediately
    - Verify webhook to Kestra includes email_1_sent_at timestamp
    - Verify Kestra flow triggered via API
    - Verify Notion sequence shows Email #1 as 'sent_by_website'
    - Verify only 4 emails scheduled by Kestra (#2-5)
    - Test TESTING_MODE=true (Email #2 at +1min from Email #1)
    - Test TESTING_MODE=false (Email #2 at +24h from Email #1)
    - Verify Email #2 delivered to Resend

- [ ] **4.8**: Puppeteer E2E: Signup handler (tracking only, no emails) [MEDIUM] **(NEW)**
  - Test: `tests/kestra/e2e/test_puppeteer_signup_funnel.py`
  - Automated browser testing for signup handler
  - **CRITICAL**: Verify signup webhook does NOT trigger any emails from Kestra
  - **Test Requirements**:
    - Navigate to signup page
    - Fill signup form with test data (lengobaosang@gmail.com)
    - Submit form and capture webhook payload
    - Verify Kestra flow triggered
    - Verify NO emails scheduled by Kestra (zero)
    - Verify contact created/updated in Notion
    - Verify website sends signup confirmation (mock/verify)
    - Test idempotency (duplicate signups)

- [ ] **4.9**: Puppeteer E2E: All secondary funnels (noshow, postcall, onboarding) [MEDIUM]
  - Test: `tests/kestra/e2e/test_puppeteer_secondary_funnels.py`
  - Automated browser testing for calendly-noshow, postcall-maybe, onboarding-start
  - **Kestra handles ALL emails** for these sequences (no website involvement)
  - **Dependencies**: 4.7 (reuses Puppeteer setup patterns)
  - **Test Requirements**:
    - Test calendly-noshow funnel (3-email recovery sequence - ALL from Kestra)
    - Test postcall-maybe funnel (3-email follow-up sequence - ALL from Kestra)
    - Test onboarding-start funnel (3-email welcome sequence - ALL from Kestra)
    - Verify each customer gets properly scheduled emails
    - Validate webhook payloads reach Kestra correctly
    - Check email scheduling timing matches expected delays
    - Verify Notion sequence tracker updates for all funnels
    - Test idempotency (duplicate submissions handled)

- [ ] **4.10**: Puppeteer E2E: Complete Sales Funnel Integration (Signup -> Assessment -> Email Sequence) [HIGH] **(NEW)**
  - Test: `tests/kestra/e2e/test_puppeteer_complete_funnel.py`
  - **CRITICAL**: Comprehensive end-to-end Puppeteer MCP testing for complete Kestra sales funnel
  - Tests FULL user journey: website signup -> assessment completion -> webhook triggers Kestra -> email sequence scheduling -> Notion tracking
  - **MANDATORY**: Uses lengobaosang@gmail.com per CLAUDE.md requirements
  - **Dependencies**: 4.4, 4.7, 4.8
  - **Test Requirements**:
    - Navigate to frontend funnel page (localhost:3005 or sangletech.com)
    - Complete signup form with lengobaosang@gmail.com test data
    - Verify signup webhook triggers Kestra signup-handler flow
    - Verify contact created/updated in Notion Contacts database
    - Navigate to assessment page and complete BusOS assessment
    - Verify website sends Email #1 immediately after assessment
    - Verify assessment webhook includes email_1_sent_at timestamp
    - Verify Kestra assessment-handler flow triggered via API
    - Verify segment classification (CRITICAL/URGENT/OPTIMIZE) correct
    - Verify Notion Sequence Tracker shows Email #1 as 'sent_by_website'
    - Verify only Emails #2-5 scheduled by Kestra (not Email #1)
    - Verify Email #2 scheduled at correct delay from email_1_sent_at
    - Verify Notion Sequence Tracker updated for scheduled emails
    - Wait for Email #2 delivery (TESTING_MODE=true for +1min delay)
    - Verify Email #2 delivered via Resend API
    - Verify Notion Sequence Tracker updated with email_number=2, sent_by='kestra'
    - Verify Contact database updated with last_email_sent timestamp
    - Test idempotency: duplicate signup/assessment submissions handled
    - Test error handling: invalid email format, missing required fields
    - Capture screenshots at each step for debugging
  - **Puppeteer MCP Steps**:
    - puppeteer_navigate to frontend funnel URL
    - puppeteer_fill signup form fields
    - puppeteer_click submit button
    - puppeteer_screenshot capture signup confirmation
    - puppeteer_navigate to assessment page
    - puppeteer_fill assessment questions
    - puppeteer_click submit assessment
    - puppeteer_screenshot capture assessment completion
    - puppeteer_evaluate check webhook payloads in browser network tab

- [ ] **4.11**: E2E Test: Webhook-to-Kestra Flow Integration Verification [HIGH] **(NEW)**
  - Test: `tests/kestra/e2e/test_webhook_kestra_integration.py`
  - Direct API-level E2E testing to verify webhooks correctly trigger Kestra flows
  - Complements Puppeteer browser tests with programmatic verification
  - **MANDATORY**: Uses lengobaosang@gmail.com per CLAUDE.md requirements
  - **Dependencies**: 4.4, 4.5
  - **Test Requirements**:
    - POST to /webhook/christmas-signup and verify Kestra flow triggered
    - Verify signup handler creates contact in Notion (NO emails scheduled)
    - POST to /webhook/christmas-assessment with email_1_sent_at payload
    - Verify assessment handler schedules Emails #2-5 only
    - Query Kestra API to verify scheduled subflow executions
    - Query Notion Sequence Tracker to verify email scheduling records
    - Verify Email #1 marked as 'sent_by_website' in Notion
    - Verify Emails #2-5 marked as 'pending' in Notion initially
    - Wait for Email #2 execution (TESTING_MODE timing)
    - Verify Email #2 status updated to 'sent' with resend_id
    - Verify sent_by='kestra' for Kestra-sent emails
    - Test all webhook endpoints: signup, assessment, noshow, postcall, onboarding
    - Verify Notion Contact database updated with last_email_sent
    - Test error responses for invalid webhook payloads
    - Test authentication/authorization for webhook endpoints
  - **Webhook Endpoints Tested**:
    - /webhook/christmas-signup
    - /webhook/christmas-assessment
    - /webhook/calendly-noshow
    - /webhook/postcall-maybe
    - /webhook/onboarding-start

- [ ] **4.12**: E2E Test: Notion Email Sequence Tracker Verification [MEDIUM] **(NEW)**
  - Test: `tests/kestra/e2e/test_notion_sequence_tracker_e2e.py`
  - Dedicated E2E tests for Notion Sequence Tracker database updates
  - Verifies email scheduling records are correctly created and updated throughout funnel lifecycle
  - **MANDATORY**: Uses lengobaosang@gmail.com per CLAUDE.md requirements
  - **Dependencies**: 2.8, 4.10
  - **Test Requirements**:
    - Query Notion Sequence Tracker for test email contact
    - Verify sequence record created after assessment webhook
    - Verify Email #1 record shows sent_by='website', status='sent'
    - Verify Email #2-5 records show sent_by='kestra', status='scheduled'
    - After Email #2 delivery, verify status updated to 'sent'
    - Verify resend_id captured from Resend API response
    - Verify sent_at timestamp matches actual send time
    - Verify email_number field correct for each email (1-5)
    - Verify sequence_type='5day' for nurture sequence
    - Test noshow/postcall/onboarding sequence tracking
    - Verify Contact database last_email_sent updated
    - Test Notion API rate limiting handling
    - Test idempotency: duplicate tracker updates handled gracefully
  - **Notion Fields Verified**:
    - Email Number (number)
    - Sent At (date)
    - Status (select: scheduled/sent/failed)
    - Sent By (select: website/kestra)
    - Resend ID (rich_text)
    - Sequence Type (select: 5day/noshow/postcall/onboarding)

### Success Criteria
- [ ] Website can trigger Kestra flows
- [ ] Production deployment is stable
- [ ] All E2E tests pass
- [ ] Documentation complete with responsibility split
- [ ] Puppeteer E2E validates website sends Email #1, Kestra sends #2-5
- [ ] Signup handler verified as tracking-only (no emails)
- [ ] All secondary funnels tested end-to-end
- [ ] **Complete sales funnel E2E passes (signup -> assessment -> email sequence)** **(NEW)**
- [ ] **Webhook-to-Kestra integration verified for all 5 endpoints** **(NEW)**
- [ ] **Notion Sequence Tracker updates verified throughout funnel lifecycle** **(NEW)**
- [ ] **All tests use lengobaosang@gmail.com per CLAUDE.md requirements** **(NEW)**

---

## Testing Strategy

### TDD Approach
1. Write tests FIRST for each feature
2. Run tests (expect failure)
3. Implement feature
4. Run tests (expect pass)
5. Refactor if needed

### Test Categories

| Category | Purpose | Location |
|----------|---------|----------|
| **Unit** | Validate YAML syntax, task configuration | `tests/kestra/test_*.py` |
| **Integration** | API connectivity, secret access | `tests/kestra/test_*_tasks.py` |
| **E2E** | Complete flow execution | `tests/kestra/e2e/test_*_e2e.py` |

### Coverage Target: >=80%

### Test Email
**MANDATORY**: Use `lengobaosang@gmail.com` for ALL testing

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Kestra secret + webhook CPU issue | Test with ENV vars first, migrate to secrets carefully |
| Website integration downtime | Use blue-green deployment with old Prefect running |
| Email scheduling differences | Comprehensive delay testing using email_1_sent_at |
| Notion API rate limits | Implement retry logic in HTTP tasks |
| Duplicate Email #1 | Webhook payload validation ensures email_1_sent_at present |
| Missing email_1_sent_at | Default to webhook time with warning log |

---

## Rollback Plan

1. Keep Prefect flows intact during migration
2. Run both systems in parallel during Wave 4
3. If Kestra fails, redirect webhooks back to Prefect
4. Document rollback commands in KESTRA_MIGRATION.md

---

## Dependencies

### External Services
- Notion API (contacts, templates, sequences)
- Resend API (email delivery)
- PostgreSQL (Kestra backend)

### Infrastructure
- Docker & Docker Compose
- Local development machine
- Homelab production server

---

## Summary of Changes (2025-11-29 12:00)

### Features Modified
| Feature | Change |
|---------|--------|
| **2.5** | Email scheduling now calculates delays from email_1_sent_at, skips Email #1 |
| **3.1** | Signup handler now TRACKING ONLY (no email sending) |
| **3.6** | Analytics task includes sent_by field (website vs Kestra) |
| **4.4** | Renamed to assessment E2E, mocks website Email #1 |
| **4.6** | Elevated to HIGH priority, includes responsibility matrix |
| **4.7** | Updated to test website/Kestra email split |

### Features Added
| Feature | Description | Wave |
|---------|-------------|------|
| **2.7** | Webhook payload validator with email_1_sent_at support | 2 |
| **3.5** | Assessment handler for 5-day sequence (Emails #2-5 only) | 3 |
| **4.8** | Puppeteer E2E for signup (tracking only verification) | 4 |
| **4.9** | Puppeteer E2E for secondary funnels | 4 |

### Impact
- **Previous Features**: 23
- **New Features**: 26 (+3)
- **Previous Estimate**: 30 hours
- **New Estimate**: 34 hours (+4)

---

## Summary of Changes (2025-11-29 14:00)

### CRITICAL REQUIREMENT: Notion Database Updates Per Email

For EVERY email sent by Kestra, the system MUST update Notion databases to track delivery status.

### Features Modified
| Feature | Change |
|---------|--------|
| **2.2** | Added `update_sequence_tracker_per_email` function to Notion HTTP tasks |
| **2.4** | send_email_flow now includes Notion Sequence Tracker update after each send |
| **3.2** | noshow_recovery_handler updated with per-email Notion tracking (3 emails) |
| **3.3** | postcall_maybe_handler updated with per-email Notion tracking (3 emails) |
| **3.4** | onboarding_handler updated with per-email Notion tracking (3 emails) |
| **3.5** | assessment_handler updated with per-email Notion tracking (Emails #2-5) |

### Features Added
| Feature | Description | Wave |
|---------|-------------|------|
| **2.8** | Dedicated Notion Sequence Tracker update task | 2 |

### Notion Update Payload Structure
```json
{
  "properties": {
    "Email Number": { "number": 2 },
    "Sent At": { "date": { "start": "2025-11-29T10:30:00Z" } },
    "Status": { "select": { "name": "sent" } },
    "Sent By": { "select": { "name": "kestra" } },
    "Resend ID": { "rich_text": [{ "text": { "content": "email_xyz" } }] }
  }
}
```

### Error Handling Strategy
- Email delivery is PRIMARY - MUST succeed
- Notion tracking is SECONDARY - log failures but don't block
- Notion update failures return success to not interrupt email flow

### Databases Updated
1. **Notion Sequence Tracker** - email_number, sent_at, status, resend_id, sent_by
2. **Notion Contact Database** - last_email_sent timestamp

### Test Requirements Added
- 47 new test cases across modified features
- Tests for Notion Sequence Tracker updates per email
- Tests for error handling (Notion failure does not block email)
- Tests for correct email_number and sent_by fields

### Impact
- **Previous Features**: 26
- **New Features**: 27 (+1)
- **Previous Estimate**: 34 hours
- **New Estimate**: 36 hours (+2)

---

## Summary of Changes (2025-11-30 20:00)

### E2E Testing Enhancement via /add-tasks-coding

Comprehensive E2E tests added for Kestra sales funnel flows using Puppeteer MCP.

### Features Added
| Feature | Description | Wave | Priority |
|---------|-------------|------|----------|
| **4.10** | Puppeteer E2E: Complete Sales Funnel Integration (Signup -> Assessment -> Email Sequence) | 4 | HIGH |
| **4.11** | E2E Test: Webhook-to-Kestra Flow Integration Verification | 4 | HIGH |
| **4.12** | E2E Test: Notion Email Sequence Tracker Verification | 4 | MEDIUM |

### Key Test Coverage Added
- **Complete User Journey**: Website signup -> assessment -> webhook -> Kestra -> email sequence -> Notion tracking
- **Webhook Integration**: All 5 webhook endpoints tested programmatically
- **Notion Tracking**: Sequence Tracker database updates verified at each step
- **Puppeteer MCP Integration**: Browser automation for form filling, screenshots, network inspection

### Test Files Added
```
tests/kestra/e2e/
  test_puppeteer_complete_funnel.py      # Feature 4.10 - 20 test cases
  test_webhook_kestra_integration.py     # Feature 4.11 - 19 test cases
  test_notion_sequence_tracker_e2e.py    # Feature 4.12 - 15 test cases
```

### Mandatory Test Email
All E2E tests MUST use: `lengobaosang@gmail.com` (per CLAUDE.md requirements)

### Dependencies
- Feature 4.10 depends on: 4.4, 4.7, 4.8
- Feature 4.11 depends on: 4.4, 4.5
- Feature 4.12 depends on: 2.8, 4.10

### Impact
- **Previous Features**: 27
- **New Features**: 30 (+3)
- **Previous Estimate**: 36 hours
- **New Estimate**: 42 hours (+6)
- **Test Cases Added**: 54

---

## Next Steps

1. Review and approve this plan
2. Run `/execute-coding` to begin Wave 1
3. Monitor progress via feature_list.json
