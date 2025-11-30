# Discovery: Deploy Kestra with Dokploy + E2E Tests

**Task ID**: 1130-deploy-kestra-dokploy-e2e-tests
**Domain**: CODING (Forced)
**Discovery Date**: 2025-11-30

---

## 1. Domain Detection

**Forced Domain**: CODING

This task involves:
- Infrastructure deployment (Kestra to Dokploy)
- E2E test implementation (Puppeteer/Playwright)
- Docker Compose configuration
- Secret management
- SSL/domain setup

---

## 2. Project Context Analysis

### 2.1 Task 1129 Status (Prerequisite)

**Status**: 81.48% complete (22/27 features)

**Completed Work**:
- Waves 1-3: All Kestra flows implemented
- Wave 4 partial: Documentation + production docker-compose

**Pending Features (5 E2E tests)**:
| Feature ID | Description | Status |
|------------|-------------|--------|
| 4.4 | E2E test: Assessment handler (Emails #2-5) | pending |
| 4.5 | E2E test: All handler flows | pending |
| 4.7 | Puppeteer E2E: Assessment funnel | pending |
| 4.8 | Puppeteer E2E: Signup handler (tracking only) | pending |
| 4.9 | Puppeteer E2E: Secondary funnels | pending |

### 2.2 Existing Kestra Infrastructure

**Flows Implemented** (13 flows):
```
kestra/flows/christmas/
  - health-check.yml
  - send-email.yml
  - schedule-email-sequence.yml
  - tasks/notion_*.yml (4 tasks)
  - tasks/resend_send_email.yml
  - handlers/signup-handler.yml
  - handlers/assessment-handler.yml
  - handlers/noshow-recovery-handler.yml
  - handlers/postcall-maybe-handler.yml
  - handlers/onboarding-handler.yml
```

**Docker Compose Files**:
- `docker-compose.kestra.yml` - Local development
- `docker-compose.kestra.prod.yml` - Production ready (exists!)

**Unit Tests**: 230+ tests passing (tests/kestra/)

---

## 3. Deployment Requirements

### 3.1 Dokploy Integration Analysis

**Skill Available**: dokploy-integration (loaded)

**Key Patterns Required**:
1. **dokploy-network** - External network for Traefik routing
2. **Traefik labels** - HTTP/HTTPS routing with Let's Encrypt
3. **Health checks** - Required for monitoring
4. **Volume mounts** - Persistent data storage

**Production Compose Ready**: `docker-compose.kestra.prod.yml` already exists with:
- PostgreSQL 16 Alpine
- Kestra with JVM optimization
- Health checks
- Resource limits
- Logging configuration
- Prometheus metrics

**Missing for Dokploy**:
1. `dokploy-network` configuration (currently uses custom network)
2. Traefik labels for `kestra.galatek.dev`
3. Domain/SSL configuration

### 3.2 Secrets Required

From `.env.kestra.prod.example`:

| Secret | Purpose | Status |
|--------|---------|--------|
| POSTGRES_PASSWORD | Database auth | Required |
| SECRET_NOTION_TOKEN | Notion API | Base64 encoded |
| SECRET_NOTION_CONTACTS_DB_ID | Contacts DB | Base64 encoded |
| SECRET_NOTION_TEMPLATES_DB_ID | Templates DB | Base64 encoded |
| SECRET_RESEND_API_KEY | Email API | Base64 encoded |
| SECRET_TESTING_MODE | Timing control | "false" for prod |
| KESTRA_ENCRYPTION_SECRET_KEY | Data encryption | Generate random |

### 3.3 Domain Configuration

**Target Domain**: kestra.galatek.dev

**Requirements**:
- Wildcard DNS: *.galatek.dev -> Dokploy server IP
- Let's Encrypt HTTP-01 challenge
- HTTPS required
- Port 80/443 accessible

---

## 4. E2E Testing Requirements

### 4.1 Test Infrastructure Analysis

**Existing E2E Test Structure**:
```
tests/e2e/
  - conftest.py          # Shared fixtures, cleanup
  - helpers.py           # Test utilities
  - test_sales_funnel_e2e.py
  - test_webhook_integration.py
  - test_notion_verification.py
```

**Existing Fixtures**:
- `api_base_url` - FastAPI server URL
- `notion_client` - Notion API client
- `test_email` - Unique email generator
- `assessment_test_data` - Complete test payload
- `cleanup_notion_contact` - Automatic cleanup
- `cleanup_notion_sequence` - Sequence cleanup

### 4.2 Browser Automation Options

**Option 1: Puppeteer MCP (Available)**
- Tools: `mcp__puppeteer__puppeteer_*`
- Functions: navigate, screenshot, click, fill, evaluate
- Pro: MCP integration, direct control
- Con: Limited test framework integration

**Option 2: Playwright Skill (Available)**
- Skill: playwright-skill
- Pro: Full test framework, assertions, auto-wait
- Con: Separate skill invocation

**Recommendation**: Use Puppeteer MCP for direct browser control, with Python pytest wrapper for test organization.

### 4.3 Test Email Requirement

**MANDATORY**: Use `lengobaosang@gmail.com` for all E2E tests

### 4.4 URLs to Test

| Environment | URL |
|-------------|-----|
| Local Dev (Website) | http://localhost:3005/en/flows/businessX/dfu/xmas-a01 |
| Production (Website) | https://sangletech.com/en/flows/businessX/dfu/xmas-a01 |
| Local Kestra | http://localhost:8080 |
| Production Kestra | https://kestra.galatek.dev |

### 4.5 Webhook Endpoints

From `WEBHOOK_ENDPOINTS.md`:

| Handler | Webhook URL Pattern |
|---------|---------------------|
| Signup | /api/v1/executions/webhook/christmas/handlers/signup-handler/signup-webhook-key |
| Assessment | /api/v1/executions/webhook/christmas/handlers/assessment-handler/assessment-webhook-key |
| No-Show | /api/v1/executions/webhook/christmas/handlers/noshow-recovery-handler/noshow-webhook-key |
| Post-Call | /api/v1/executions/webhook/christmas/handlers/postcall-maybe-handler/postcall-webhook-key |
| Onboarding | /api/v1/executions/webhook/christmas/handlers/onboarding-handler/onboarding-webhook-key |

---

## 5. Email Responsibility Split (CRITICAL)

**Website Sends**:
- Signup confirmation email
- 5-day sequence Email #1

**Kestra Sends**:
- 5-day sequence Emails #2-5
- No-show recovery (all 3 emails)
- Post-call maybe (all 3 emails)
- Onboarding (all 3 emails)

**Webhook Payload Requirement**:
- Assessment webhook MUST include `email_1_sent_at` timestamp
- Kestra schedules Emails #2-5 relative to this timestamp

---

## 6. Risk Assessment

### High Risk
1. **Dokploy Network Configuration** - Must modify prod compose for dokploy-network
2. **SSL Certificate Issuance** - Let's Encrypt rate limits (50 certs/week)
3. **DNS Propagation** - Wildcard DNS must be configured

### Medium Risk
1. **Secret Migration** - Base64 encoding must be correct
2. **E2E Test Flakiness** - Browser tests can be timing-sensitive
3. **Kestra Flow Verification** - Flows must be deployed before E2E tests

### Low Risk
1. **Health Checks** - Already implemented in prod compose
2. **Unit Tests** - 230+ tests already passing
3. **Documentation** - Comprehensive docs exist

---

## 7. Dependencies

### External Dependencies
- Dokploy instance running at `dokploy.galatek.dev`
- DNS configured for `*.galatek.dev`
- Port 80/443 open for Let's Encrypt
- Notion databases accessible
- Resend API operational

### Internal Dependencies
- Task 1129 Wave 4 completion (features 4.1-4.3, 4.6 done)
- Kestra flows deployed
- PostgreSQL database initialized

---

## 8. Recommendations

### Deployment Strategy
1. Modify `docker-compose.kestra.prod.yml` for Dokploy compatibility
2. Add Traefik labels for `kestra.galatek.dev`
3. Configure secrets via Dokploy UI
4. Deploy via Dokploy Docker Compose service
5. Verify health check and SSL

### E2E Testing Strategy
1. Create Kestra-specific E2E test directory: `tests/kestra/e2e/`
2. Use existing fixtures from `tests/e2e/conftest.py`
3. Implement tests with Puppeteer MCP for browser control
4. Add verification helpers for Kestra API and Notion

### TDD Approach
1. Write E2E tests first (they will fail without deployment)
2. Deploy Kestra to Dokploy
3. Run E2E tests to verify deployment
4. Iterate on fixes

---

## 9. Estimated Effort

| Wave | Description | Hours |
|------|-------------|-------|
| 1 | Dokploy Deployment | 4-6h |
| 2 | E2E Test Infrastructure | 2-3h |
| 3 | Handler Flow E2E Tests | 3-4h |
| 4 | Puppeteer Sales Funnel Tests | 4-5h |

**Total Estimated**: 13-18 hours

---

## 10. Files to Create/Modify

### Create
- `tests/kestra/e2e/conftest.py` - E2E test fixtures
- `tests/kestra/e2e/test_assessment_e2e.py` - Feature 4.4
- `tests/kestra/e2e/test_all_handlers_e2e.py` - Feature 4.5
- `tests/kestra/e2e/test_puppeteer_assessment_funnel.py` - Feature 4.7
- `tests/kestra/e2e/test_puppeteer_signup_funnel.py` - Feature 4.8
- `tests/kestra/e2e/test_puppeteer_secondary_funnels.py` - Feature 4.9
- `docker-compose.kestra.dokploy.yml` - Dokploy-compatible compose

### Modify
- `docker-compose.kestra.prod.yml` - Add Traefik labels (or create new file)

---

**Discovery Status**: COMPLETE
**Next Phase**: PLAN
