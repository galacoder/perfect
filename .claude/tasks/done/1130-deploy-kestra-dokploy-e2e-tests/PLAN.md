# Plan: Deploy Kestra with Dokploy + E2E Tests

**Task ID**: 1130-deploy-kestra-dokploy-e2e-tests
**Domain**: CODING
**Source**: feature_list.json

---

## Overview

This task completes the Kestra migration by:
1. **FIRST**: Extracting Kestra to standalone repository with git history preserved
2. Deploying Kestra to production (kestra.galatek.dev) via Dokploy
3. Implementing 5 pending E2E test features from task 1129 (4.4, 4.5, 4.7, 4.8, 4.9)

**Total Features**: 23
**Estimated Hours**: 18

---

## Wave 0: Repository Extraction
**Objective**: Extract Kestra to standalone repository with preserved git commit history
**Status**: Pending
**Estimated Hours**: 2

### Tasks

- [ ] **0.1**: Analyze git commits for Kestra-related changes
  - Use `git log` to identify all commits from task 1129
  - Extract commit SHAs, messages, and file changes
  - Understand full commit history to preserve

- [ ] **0.2**: Create kestra-automation repository structure
  - Create `/Users/sangle/Dev/action/projects/kestra-automation/`
  - Set up: flows/, tests/, docker-compose files, docs
  - Add .gitignore, README.md

- [ ] **0.3**: Extract Kestra files using git filter-branch
  - Use `git filter-branch` or `git subtree split`
  - Extract kestra/, tests/kestra/, docker-compose.kestra*.yml
  - Preserve full commit history

- [ ] **0.4**: Initialize new kestra-automation git repository
  - Run `git init` in kestra-automation/
  - Set up remote (if applicable)
  - Verify commit history with `git log`

- [ ] **0.5**: Update documentation and paths
  - Fix all relative paths in extracted repository
  - Update README for standalone structure
  - Add deployment documentation

- [ ] **0.6**: Verify extracted repository integrity
  - Verify all 13 Kestra flows present
  - Verify all tests copied correctly
  - Verify docker-compose files valid
  - Verify git history preserved (compare commit messages)
  - **Test File**: kestra-automation/verify_extraction.py

### Success Criteria
- [ ] New repository at /Users/sangle/Dev/action/projects/kestra-automation/
- [ ] All 13 flows, tests, docker-compose files extracted
- [ ] Git history preserved (all task 1129 commits visible)
- [ ] No broken file references
- [ ] Documentation updated for standalone repo

---

## Wave 1: Dokploy Deployment
**Objective**: Deploy Kestra to kestra.galatek.dev with PostgreSQL, SSL, secrets, and health monitoring
**Status**: Pending
**Estimated Hours**: 5

### Tasks

- [ ] **1.1**: Create Dokploy-compatible docker-compose.kestra.dokploy.yml
  - Modify existing prod compose for Dokploy
  - Add `dokploy-network` (external)
  - Add Traefik labels for HTTP/HTTPS
  - Configure Let's Encrypt certresolver
  - **Test File**: tests/kestra/e2e/test_dokploy_compose.py

- [ ] **1.2**: Configure Dokploy secrets for Kestra
  - Document all required secrets
  - Configure via Dokploy UI
  - Base64 encode Notion/Resend tokens

- [ ] **1.3**: Deploy Kestra via Dokploy Docker Compose
  - Use dokploy-integration skill
  - Create Docker Compose service
  - Upload compose file and deploy
  - **Test File**: tests/kestra/e2e/test_deployment_health.py

- [ ] **1.4**: Verify Kestra deployment health and SSL
  - HTTPS accessible at kestra.galatek.dev
  - Valid SSL certificate
  - All 13 flows deployed
  - **Test File**: tests/kestra/e2e/test_deployment_health.py

- [ ] **1.5**: Test webhook endpoints accessibility
  - All 5 webhooks respond
  - POST creates execution
  - Invalid payload returns 400
  - **Test File**: tests/kestra/e2e/test_webhook_accessibility.py

### Success Criteria
- [ ] Kestra UI accessible at https://kestra.galatek.dev
- [ ] Valid SSL certificate (Let's Encrypt)
- [ ] All 5 webhook endpoints functional
- [ ] Health check returns OK
- [ ] 13 flows visible in Kestra UI

---

## Wave 2: E2E Test Infrastructure
**Objective**: Set up Puppeteer test environment, fixtures, utilities, and test data
**Status**: Pending
**Estimated Hours**: 3

### Tasks

- [ ] **2.1**: Create Kestra E2E test directory and conftest
  - Create tests/kestra/e2e/
  - Implement conftest.py with fixtures
  - Add Kestra API client
  - Add cleanup hooks

- [ ] **2.2**: Implement Kestra API helper functions
  - trigger_webhook()
  - get_execution_status()
  - wait_for_execution_complete()
  - get_execution_logs()
  - list_scheduled_subflows()
  - **Test File**: tests/kestra/e2e/test_kestra_helpers.py

- [ ] **2.3**: Implement Notion verification helpers
  - verify_sequence_created()
  - verify_email_tracked()
  - get_sequence_by_email()
  - cleanup_test_sequences()
  - **Test File**: tests/kestra/e2e/test_notion_helpers.py

- [ ] **2.4**: Create test data fixtures for E2E tests
  - assessment_payload_critical
  - assessment_payload_urgent
  - assessment_payload_optimize
  - noshow_payload, postcall_payload, onboarding_payload
  - Use lengobaosang@gmail.com for all

### Success Criteria
- [ ] conftest.py with all required fixtures
- [ ] Helper functions tested and working
- [ ] Test data using mandatory test email
- [ ] Cleanup hooks prevent test data accumulation

---

## Wave 3: Handler Flow E2E Tests
**Objective**: Implement E2E tests for assessment handler and all handler flows
**Status**: Pending
**Estimated Hours**: 4

### Tasks

- [ ] **3.1**: Feature 4.4 - E2E test: Assessment handler (Emails #2-5)
  - Mock website sending Email #1
  - POST assessment webhook with email_1_sent_at
  - Verify only Emails #2-5 scheduled
  - Verify Notion tracking
  - **Test File**: tests/kestra/e2e/test_assessment_e2e.py

- [ ] **3.2**: Feature 4.5 - E2E test: All handler flows
  - Test noshow-recovery handler (3 emails)
  - Test postcall-maybe handler (3 emails)
  - Test onboarding handler (3 emails)
  - Verify Notion Sequence Tracker
  - **Test File**: tests/kestra/e2e/test_all_handlers_e2e.py

- [ ] **3.3**: Verify email responsibility split
  - Signup webhook = NO emails from Kestra
  - Assessment webhook = Emails #2-5 only
  - Secondary sequences = ALL emails from Kestra
  - **Test File**: tests/kestra/e2e/test_email_split_verification.py

### Success Criteria
- [ ] Assessment E2E test passes
- [ ] All handler E2E tests pass
- [ ] Email responsibility split verified
- [ ] Notion tracking verified for all sequences

---

## Wave 4: Puppeteer Sales Funnel Tests
**Objective**: Complete browser automation tests for full sales funnel verification
**Status**: Pending
**Estimated Hours**: 4

### Tasks

- [ ] **4.1**: Feature 4.7 - Puppeteer E2E: Assessment funnel
  - Navigate to funnel URL
  - Fill assessment form (lengobaosang@gmail.com)
  - Submit and verify Email #1 from website
  - Verify webhook with email_1_sent_at
  - Verify Kestra schedules Emails #2-5
  - **Test File**: tests/kestra/e2e/test_puppeteer_assessment_funnel.py

- [ ] **4.2**: Feature 4.8 - Puppeteer E2E: Signup handler (tracking only)
  - Fill signup form
  - Verify NO emails from Kestra
  - Verify contact created in Notion
  - Test idempotency
  - **Test File**: tests/kestra/e2e/test_puppeteer_signup_funnel.py

- [ ] **4.3**: Feature 4.9 - Puppeteer E2E: Secondary funnels
  - Test calendly-noshow (3 emails from Kestra)
  - Test postcall-maybe (3 emails from Kestra)
  - Test onboarding-start (3 emails from Kestra)
  - Verify timing and Notion tracking
  - **Test File**: tests/kestra/e2e/test_puppeteer_secondary_funnels.py

- [ ] **4.4**: Create E2E test runner and CI integration
  - Setup/teardown automation
  - Timeout handling
  - Result reporting

### Success Criteria
- [ ] Assessment funnel browser test passes
- [ ] Signup funnel test verifies no emails
- [ ] All secondary funnel tests pass
- [ ] Complete funnel flow verified end-to-end

---

## TDD Approach

### For Each Feature:
1. **Write test first** - Define expected behavior
2. **Run test** - Confirm it fails (no implementation)
3. **Implement** - Build the feature
4. **Run test** - Confirm it passes
5. **Refactor** - Clean up code
6. **Commit** - With test file path

### Test Coverage Targets:
- Wave 1: Deployment verification tests
- Wave 2: Helper function unit tests
- Wave 3: E2E integration tests
- Wave 4: Full browser automation tests

---

## Dependencies

### External
- Dokploy instance at dokploy.galatek.dev
- DNS for *.galatek.dev
- Let's Encrypt (port 80/443)
- Notion databases
- Resend API

### Internal
- Task 1129 flows deployed
- docker-compose.kestra.prod.yml
- Existing E2E test fixtures

---

## Skills Required

| Skill | Purpose |
|-------|---------|
| dokploy-integration | Deploy via Dokploy API |
| playwright-skill (optional) | Browser automation alternative |
| Puppeteer MCP | Browser control (mcp__puppeteer__*) |

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| SSL rate limits | Deploy in off-hours, use staging first |
| Browser test flakiness | Add retries, explicit waits |
| Timing issues | Use TESTING_MODE for fast delays |
| Secret misconfiguration | Verify with health check before E2E |

---

## Execution Order

1. **Wave 0 (Repository Extraction)** - MUST complete first (prerequisite for all other waves)
2. Wave 1 (Deployment) - After repository extracted
3. Wave 2 (Infrastructure) - Parallel with Wave 1 prep
4. Wave 3 (Handler E2E) - After deployment verified
5. Wave 4 (Puppeteer) - After Wave 3 complete

---

**Plan Status**: COMPLETE
**Next Step**: User approval, then run `/execute-coding`
