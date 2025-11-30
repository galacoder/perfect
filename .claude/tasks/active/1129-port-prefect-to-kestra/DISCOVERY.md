# Discovery: Port Prefect Christmas Automation to Kestra

**Task ID**: 1129-port-prefect-to-kestra
**Domain**: CODING
**Started**: 2025-11-29
**Status**: EXPLORE Complete

---

## 1. Domain Detection

**Detected Domain**: CODING (Forced)
**Rationale**: This task involves porting Python workflow automation code from Prefect v3.4.1 to Kestra YAML-based orchestration, requiring code migration, infrastructure setup, and comprehensive testing.

---

## 2. Current State Analysis

### 2.1 Prefect Christmas Campaign Architecture

**Location**: `campaigns/christmas_campaign/`

#### Flows (5 total)
| Flow | File | Purpose | Emails | Trigger |
|------|------|---------|--------|---------|
| **signup_handler_flow** | `flows/signup_handler.py` | Handle assessment completions, schedule 5-email sequence | 5 (E2-E5) | Webhook |
| **send_email_flow** | `flows/send_email_flow.py` | Send individual email from sequence | 1 per run | Scheduled via Prefect |
| **noshow_recovery_handler_flow** | `flows/noshow_recovery_handler.py` | Handle Calendly no-shows | 3 | Webhook |
| **postcall_maybe_handler_flow** | `flows/postcall_maybe_handler.py` | Follow-up after "maybe" calls | 3 | Webhook |
| **onboarding_handler_flow** | `flows/onboarding_handler.py` | Client onboarding after payment | 3 | Webhook |

#### Tasks (3 modules)
| Module | File | Functions |
|--------|------|-----------|
| **notion_operations** | `tasks/notion_operations.py` | 12+ functions: search_contact_by_email, create_email_sequence, update_email_sequence, fetch_email_template, log_email_analytics, etc. |
| **resend_operations** | `tasks/resend_operations.py` | 4 functions: send_email, substitute_variables, send_template_email, get_email_variables |
| **routing** | `tasks/routing.py` | 6 functions: classify_segment, get_email_template_id, should_send_discord_alert, get_segment_priority, get_segment_description, get_sequence_template_id |

#### Secret Management
Current Prefect Secret blocks:
- `notion-token`
- `notion-email-templates-db-id`
- `notion-email-sequence-db-id`
- `notion-businessx-db-id`
- `notion-customer-projects-db-id`
- `notion-email-analytics-db-id`
- `resend-api-key`
- `testing-mode`

### 2.2 Webhook Endpoints (server.py)

| Endpoint | Purpose | Prefect Flow |
|----------|---------|--------------|
| `/webhook/christmas-signup` | Assessment completion | christmas-signup-handler |
| `/webhook/calendly-noshow` | Calendly no-show event | christmas-noshow-recovery-handler |
| `/webhook/postcall-maybe` | Post-call maybe CRM trigger | christmas-postcall-maybe-handler |
| `/webhook/onboarding-start` | DocuSign + payment trigger | christmas-onboarding-handler |
| `/health` | Health check | N/A |

### 2.3 Email Sequence Timing

**Production Mode** (TESTING_MODE=false):
```
Signup Sequence (5-day):
  Email 1: Website (immediate)
  Email 2: +24h (Prefect)
  Email 3: +72h (Day 3)
  Email 4: +96h (Day 4)
  Email 5: +120h (Day 5)

No-Show Recovery (2-day):
  Email 1: +5min
  Email 2: +24h
  Email 3: +48h

Post-Call Maybe (7-day):
  Email 1: +1h
  Email 2: +72h (Day 3)
  Email 3: +168h (Day 7)

Onboarding (3-day):
  Email 1: +1h
  Email 2: +24h
  Email 3: +72h
```

**Testing Mode** (TESTING_MODE=true):
- All sequences: 1min, 2min, 3min intervals

### 2.4 Dependencies

```
# Core Dependencies
prefect==3.4.1
notion-client==2.2.1
resend==2.19.0
httpx==0.27.2
python-dotenv==1.0.1

# API Server
fastapi==0.115.6
uvicorn[standard]==0.34.0
pydantic[email]==2.10.4

# Testing
pytest==8.3.4
pytest-mock==3.14.0
pytest-cov==6.0.0
```

---

## 3. Target State: Kestra Architecture

### 3.1 Kestra vs Prefect Comparison

| Feature | Prefect v3.4.1 | Kestra |
|---------|---------------|--------|
| **Flow Definition** | Python decorators (@flow, @task) | YAML files |
| **Scheduling** | create_flow_run_from_deployment + Scheduled state | Subflow with scheduleDate OR Pause task |
| **Secret Management** | Secret.load("name").get() | `{{ secret('NAME') }}` with SECRET_ prefix |
| **Webhook Triggers** | FastAPI endpoints + manual flow trigger | io.kestra.plugin.core.trigger.Webhook |
| **State Tracking** | External (Notion) | Can use Kestra KV store OR external (Notion) |
| **HTTP Requests** | httpx/requests in Python | io.kestra.plugin.core.http.Request |
| **Python Scripts** | Native Python tasks | io.kestra.plugin.scripts.python.Script |

### 3.2 Kestra Flow Mapping

```yaml
# Prefect Flow -> Kestra Equivalent

signup_handler_flow -> christmas-signup-handler.yml
  - Trigger: Webhook
  - Tasks: HTTP (Notion), Python (business logic), Subflow (schedule emails)

send_email_flow -> christmas-send-email.yml
  - Trigger: Called as subflow with scheduleDate
  - Tasks: HTTP (Notion), HTTP (Resend)

noshow_recovery_handler_flow -> noshow-recovery-handler.yml
  - Trigger: Webhook
  - Tasks: HTTP (Notion), Subflow calls

postcall_maybe_handler_flow -> postcall-maybe-handler.yml
  - Trigger: Webhook
  - Tasks: HTTP (Notion), Subflow calls

onboarding_handler_flow -> onboarding-handler.yml
  - Trigger: Webhook
  - Tasks: HTTP (Notion), Subflow calls
```

### 3.3 Kestra Secret Mapping

```bash
# Prefect Secret -> Kestra Environment Variable
notion-token         -> SECRET_NOTION_TOKEN
notion-email-templates-db-id -> SECRET_NOTION_EMAIL_TEMPLATES_DB_ID
notion-email-sequence-db-id  -> SECRET_NOTION_EMAIL_SEQUENCE_DB_ID
notion-businessx-db-id       -> SECRET_NOTION_BUSINESSX_DB_ID
resend-api-key       -> SECRET_RESEND_API_KEY
testing-mode         -> SECRET_TESTING_MODE
```

### 3.4 Webhook URL Mapping

```
# Prefect (via FastAPI) -> Kestra Native

/webhook/christmas-signup
  -> /api/v1/main/executions/webhook/christmas/signup-handler/{key}

/webhook/calendly-noshow
  -> /api/v1/main/executions/webhook/christmas/noshow-recovery-handler/{key}

/webhook/postcall-maybe
  -> /api/v1/main/executions/webhook/christmas/postcall-maybe-handler/{key}

/webhook/onboarding-start
  -> /api/v1/main/executions/webhook/christmas/onboarding-handler/{key}
```

---

## 4. Key Findings

### 4.1 Migration Challenges

1. **Scheduled Flow Runs**
   - Prefect: Uses `create_flow_run_from_deployment` with `Scheduled(scheduled_time=...)`
   - Kestra: Use `io.kestra.plugin.core.flow.Subflow` with `scheduleDate` property
   - Alternative: Create multiple flows triggered by Schedule trigger with CRON

2. **Template Variable Substitution**
   - Prefect: Python `re.sub()` with `{{variable}}` pattern
   - Kestra: Pebble templating `{{ variable }}` native support

3. **Async/Await Pattern**
   - Prefect: Heavy use of `asyncio.run()` for scheduling
   - Kestra: Declarative, no async needed

4. **Idempotency Checks**
   - Both: Need to query Notion before sending emails
   - Same pattern applies in Kestra via HTTP tasks

### 4.2 Migration Advantages

1. **Simpler YAML Syntax**: No Python decorator complexity
2. **Built-in Webhook Triggers**: No need for separate FastAPI server
3. **Visual UI**: Kestra provides execution visualization
4. **Docker-Native**: Runs in containers by design
5. **Homelab-Friendly**: Self-hosted PostgreSQL + single container

### 4.3 Identified Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| **Kestra Pause task limitations** | Medium | Use scheduleDate on subflows instead |
| **Secret with webhook trigger CPU issue** | High | Test thoroughly, use ENV vars if needed |
| **No direct Python task imports** | Medium | Use HTTP tasks or inline Python scripts |
| **Website integration URL changes** | High | Coordinate with frontend team |

---

## 5. Testing Strategy

### 5.1 Unit Tests (per flow)
- YAML syntax validation (kestra flow validate)
- Task output mocking
- Template variable substitution

### 5.2 Integration Tests
- Webhook endpoint response
- Notion API connectivity
- Resend API connectivity
- Subflow scheduling

### 5.3 E2E Tests
- Complete signup -> email delivery flow
- No-show recovery sequence
- Post-call maybe sequence
- Onboarding sequence

### 5.4 Coverage Target
- Minimum: 80%
- Focus on: Business logic, routing, error handling

---

## 6. Infrastructure Requirements

### 6.1 Local Development (Docker Compose)
```yaml
services:
  kestra:
    image: kestra/kestra:latest
    ports:
      - "8080:8080"
    environment:
      # Secrets with SECRET_ prefix
      SECRET_NOTION_TOKEN: <base64-encoded>
      SECRET_RESEND_API_KEY: <base64-encoded>
      # ...
    volumes:
      - ./flows:/app/flows
    depends_on:
      - postgres

  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: kestra
      POSTGRES_USER: kestra
      POSTGRES_PASSWORD: kestra
```

### 6.2 Production Homelab
- PostgreSQL: External or Docker
- Kestra: Single container (standalone mode)
- Storage: Local filesystem or MinIO
- Secrets: Base64-encoded environment variables

---

## 7. Recommendations

### 7.1 Migration Order
1. **Foundation**: Docker Compose + secrets + health checks
2. **Core Flows**: Start with `send_email_flow` (simplest)
3. **Handlers**: Port signup, noshow, postcall, onboarding
4. **Website Integration**: Update webhook URLs
5. **Production Deploy**: Homelab configuration

### 7.2 Key Decisions Needed
1. **Webhook Server**: Use Kestra native OR keep FastAPI proxy?
   - Recommendation: Kestra native (simplifies architecture)

2. **Scheduling Approach**: Subflow scheduleDate OR Pause task?
   - Recommendation: Subflow with scheduleDate (more robust)

3. **Python Code**: Inline scripts OR HTTP tasks?
   - Recommendation: HTTP tasks for Notion/Resend, inline Python for business logic

---

## 8. Next Steps

1. Create PLAN.md with TDD-focused waves
2. Generate feature_list.json and tests.json
3. Begin Wave 1: Foundation implementation
