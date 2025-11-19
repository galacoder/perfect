# Discovery: Build Webhook-Based Automation for Christmas Campaign

## Requirements Understanding

### Core Functionality
Build a **fully automated webhook-based email nurture sequence system** for the Christmas campaign that:

1. **Receives customer signups via webhook** from website form
2. **Automatically schedules 7-email sequence** using Prefect flows
3. **Background worker processes scheduled emails** at the correct times
4. **Cal.com webhook integration** for meeting booking reminders
5. **Scales to 100-300 concurrent customers** on homelab server
6. **No manual intervention required** - completely automated

### User Stories

**Story 1: Lead Signup**
- As a **website visitor**, when I **submit the signup form**
- I want **automatic enrollment in 7-email sequence**
- So that I **receive nurture emails over 11 days without any manual work**

**Story 2: Meeting Booking**
- As a **prospect**, when I **book a diagnostic call via Cal.com**
- I want **automatic reminder emails before the meeting**
- So that I **don't miss the appointment**

**Story 3: Business Owner (You)**
- As a **business owner**, when **customers sign up**
- I want **zero manual work** to send sequences
- So that I **can scale to 300 customers without hiring**

### Acceptance Criteria

✅ **Webhook Integration**:
- [ ] Website form → `POST /webhook/christmas-signup` works
- [ ] Cal.com → `POST /webhook/calcom-booking` works
- [ ] Webhook responds in <500ms (immediately queues work)
- [ ] Failed webhooks retry automatically

✅ **Email Scheduling**:
- [ ] All 7 emails scheduled correctly on signup
- [ ] Emails send at exact scheduled times (within 1-minute accuracy)
- [ ] System handles 100-300 concurrent customer sequences
- [ ] No duplicate emails sent
- [ ] Failed sends retry automatically (3 attempts)

✅ **Performance & Scalability**:
- [ ] Webhook endpoint handles 10 req/sec (600 signups/hour)
- [ ] Background worker processes 100+ emails/minute
- [ ] System stable with 300 concurrent sequences (7 days)
- [ ] Resource usage on homelab: <30GB RAM, <50% CPU average

✅ **Observability**:
- [ ] Prefect UI shows all scheduled flows
- [ ] Failed flows visible in dashboard
- [ ] Notion logs every email sent (success/failure)
- [ ] Can pause/resume individual customer sequences

### Constraints

**Technical Constraints**:
- Must use **Prefect 3.4.1** (already installed)
- Must use **Notion** for data storage (no database changes)
- Must use **Resend API** for email delivery
- Must deploy on **homelab server** (32-64GB RAM, 14-16 threads, 1TB storage)
- Must maintain **existing email templates** (7 already created)

**Time Constraints**:
- Build in **waves** (incremental progress)
- Test each wave before moving forward
- Total implementation: 8-12 hours

**Resource Constraints**:
- **RAM**: <30GB used (leave 34GB free for other services)
- **CPU**: <50% average utilization
- **Storage**: <100GB for Prefect database
- **Network**: Minimal (Notion + Resend APIs only)

---

## Codebase Analysis

### Technology Stack

**Backend**:
- **Framework**: FastAPI 0.115.6
- **Language**: Python 3.11+
- **Runtime**: Python virtual environment
- **Workflow Engine**: Prefect 3.4.1
- **API Server**: Uvicorn 0.34.0
- **Database**: Notion (via notion-client 2.2.1)
- **Email Service**: Resend API (via resend 2.19.0)
- **Environment**: python-dotenv 1.0.1

**Testing**:
- **Test Framework**: pytest 8.3.4
- **Mocking**: pytest-mock 3.14.0
- **Coverage**: pytest-cov 6.0.0

**Infrastructure**:
- **Deployment**: Homelab server (self-hosted)
- **Process Manager**: Systemd or Supervisor (TBD)
- **Prefect Server**: Local Prefect Server or Prefect Cloud

### Relevant Files

**Existing Files to Modify**:
- `server.py` - Add Christmas campaign webhook endpoint
- `campaigns/christmas_campaign/flows/email_sequence_orchestrator.py` - Fix scheduling logic
- `campaigns/christmas_campaign/flows/send_email_flow.py` - Individual email flow

**New Files to Create**:
- `campaigns/christmas_campaign/flows/signup_handler.py` - Handle webhook, create customer
- `campaigns/christmas_campaign/deployments/deploy_christmas.py` - Deploy all flows
- `campaigns/christmas_campaign/workers/email_worker.py` - Background worker (if needed)
- `campaigns/christmas_campaign/tasks/webhook_operations.py` - Webhook-specific logic

**Test Files**:
- `campaigns/christmas_campaign/tests/test_signup_handler.py` - Test webhook flow
- `campaigns/christmas_campaign/tests/test_scheduling.py` - Test Prefect scheduling
- `campaigns/christmas_campaign/tests/test_integration_webhook.py` - E2E webhook test

**Configuration Files**:
- `.env` - Add `PREFECT_API_URL`, `PREFECT_API_KEY` (if using Prefect Cloud)
- `requirements.txt` - Already has all dependencies ✅

### Dependencies

**External Packages** (already installed ✅):
- `prefect==3.4.1` - Workflow orchestration
- `notion-client==2.2.1` - Notion API client
- `resend==2.19.0` - Email delivery
- `fastapi==0.115.6` - Webhook server
- `uvicorn[standard]==0.34.0` - ASGI server
- `pydantic[email]==2.10.4` - Request validation
- `httpx==0.27.2` - Async HTTP client
- `python-dotenv==1.0.1` - Environment variables

**Internal Modules**:
- `campaigns.christmas_campaign.tasks.notion_operations` - Notion CRUD operations
- `campaigns.christmas_campaign.tasks.resend_operations` - Email sending tasks
- `campaigns.christmas_campaign.tasks.routing` - Segment classification
- `campaigns.christmas_campaign.flows.send_email_flow` - Individual email flow

**Breaking Changes**: None expected (all dependencies compatible)

### Code Patterns to Reuse

**Pattern 1: BusinessX Campaign Webhook Handler** (`server.py:156-213`)
```python
@app.post("/webhook/signup")
async def signup_webhook(request: SignupRequest, background_tasks: BackgroundTasks):
    # 1. Validate request
    # 2. Queue Prefect flow in background
    background_tasks.add_task(signup_handler_flow, **request.dict())
    # 3. Return 202 Accepted immediately
    return {"status": "accepted", "email": request.email}
```
**Reuse for**: Christmas campaign webhook endpoint

**Pattern 2: Prefect Flow with Retries** (`assessment_handler.py:33-42`)
```python
@flow(name="assessment-handler", log_prints=True)
def assessment_handler_flow(email: str, red_systems: int, ...):
    # Use @flow decorator
    # Return dict with status
    # Call tasks for operations
```
**Reuse for**: Christmas signup handler flow

**Pattern 3: Email Sequence with Waits** (`email_sequence.py:92-150`)
- ❌ **Don't reuse**: Uses `sleep()` - blocks for entire sequence
- ❌ **Problem**: Can't handle 100+ concurrent customers (each blocks for 11 days)
- ✅ **Better approach**: Use Prefect `Deployment` with scheduled runs

**Pattern 4: Template Fetching from Notion** (`template_operations.py`)
- ✅ Fetch templates dynamically from Notion
- ✅ Cache templates to reduce API calls
- ✅ Substitute variables with `{{placeholder}}` syntax

### Architecture Understanding

**Current Architecture (BusinessX Campaign)**:
```
Website Form
    ↓
POST /webhook/signup → FastAPI server.py
    ↓
FastAPI BackgroundTasks → signup_handler_flow (Prefect)
    ↓
Create contact in Notion
    ↓
(Manual trigger for assessment)
    ↓
POST /webhook/assessment
    ↓
assessment_handler_flow → email_sequence_flow
    ↓
Sends 5 emails with sleep() between each (BLOCKING)
```

**Problems with Current Architecture**:
1. ❌ `email_sequence_flow` uses `sleep()` - blocks for entire duration
2. ❌ Can't handle multiple concurrent customers (each blocks a Prefect worker)
3. ❌ If process dies, sequence stops (no fault tolerance)
4. ❌ No way to pause/resume sequences
5. ❌ No visibility into scheduled emails

**Target Architecture (Christmas Campaign)**:
```
Website Form (with assessment data)
    ↓
POST /webhook/christmas-signup → FastAPI server.py
    ↓
FastAPI BackgroundTasks → signup_handler_flow (Prefect)
    ↓
Create contact in Notion
    ↓
Schedule 7 email flows via Prefect Deployment:
  - Email 1: deploy.run(parameters={...}, scheduled_time=NOW)
  - Email 2: deploy.run(parameters={...}, scheduled_time=NOW + 24h)
  - Email 3: deploy.run(parameters={...}, scheduled_time=NOW + 72h)
  - ... (all 7 emails)
    ↓
Prefect Server schedules flows in future
    ↓
At scheduled time, Prefect Worker executes send_email_flow
    ↓
send_email_flow:
  1. Fetch template from Notion
  2. Substitute variables
  3. Send via Resend
  4. Log to Notion Analytics
```

**Key Difference**: Instead of one long-running flow with sleep(), we schedule 7 **separate flow runs** in the future using Prefect Deployments.

### Potential Conflicts

**Conflict 1: Prefect Server vs. Prefect Cloud**
- **Issue**: Need to decide which to use
- **Prefect Server** (self-hosted):
  - ✅ Free, full control, privacy
  - ❌ More setup (PostgreSQL database, Redis for queuing)
  - ❌ Need to maintain infrastructure
- **Prefect Cloud** (hosted):
  - ✅ No infrastructure, easy setup
  - ✅ Better UI, observability
  - ❌ Cost (~$0-50/month for 300 customers)
  - ❌ Data leaves homelab

**Decision**: Use **Prefect Server** (self-hosted) for homelab deployment

**Conflict 2: Deployment Strategy**
- **Issue**: How to deploy 7 separate email flows?
- **Option A**: 7 separate deployments (christmas-email-1, christmas-email-2, ...)
  - ✅ Clear separation
  - ❌ 7 deployments to manage
- **Option B**: 1 deployment with email_number parameter
  - ✅ Single deployment
  - ✅ Easier to manage
  - ✅ **RECOMMENDED**

**Decision**: Use **1 parameterized deployment** (`send_email_flow` with `email_number` parameter)

**Conflict 3: Background Worker**
- **Issue**: Do we need a separate background worker?
- **Answer**: **No**, Prefect Worker is sufficient
  - Prefect Worker polls Prefect Server for scheduled flows
  - Executes flows at scheduled time
  - Handles retries, logging, etc.

**Decision**: Use **Prefect Worker** (no custom background worker needed)

---

## Technical Constraints

### Performance Requirements

**Latency**:
- Webhook response: <500ms (accept and queue immediately)
- Email send: <5 seconds per email
- Prefect flow scheduling: <2 seconds to schedule 7 emails

**Throughput**:
- Webhook: 10 req/sec (600 signups/hour)
- Email worker: 100 emails/minute (sufficient for 300 customers × 7 emails = 2100 emails over 11 days)

**Memory**:
- FastAPI server: ~200MB
- Prefect Server: ~1-2GB
- Prefect Worker (1): ~500MB per worker
- PostgreSQL (Prefect DB): ~500MB-1GB
- **Total**: ~3-4GB (well within 32-64GB homelab capacity)

**Concurrency**:
- 300 customers × 7 emails = 2100 scheduled flow runs
- Prefect handles this easily (stores in PostgreSQL)
- Worker processes flows sequentially as they become due

### Browser/Device Support

Not applicable (backend service only)

### Security Considerations

**OWASP Top 10**:
1. **Injection**: ✅ Pydantic validates all webhook inputs
2. **Broken Authentication**: N/A (no auth required for webhooks - public endpoints)
3. **Sensitive Data Exposure**: ✅ API keys in `.env`, never committed
4. **XML External Entities**: N/A (JSON only)
5. **Broken Access Control**: ⚠️ Consider webhook signatures (Cal.com, website)
6. **Security Misconfiguration**: ✅ Use HTTPS in production
7. **XSS**: N/A (no HTML rendering)
8. **Insecure Deserialization**: ✅ Pydantic validates
9. **Using Components with Known Vulnerabilities**: ✅ Latest dependencies
10. **Insufficient Logging**: ✅ Prefect logs all flows, Notion logs all emails

**Additional Security**:
- **Rate Limiting**: Add FastAPI rate limiter (10 req/sec per IP)
- **Webhook Signatures**: Verify Cal.com webhook signature
- **CORS**: Already configured in server.py
- **Environment Variables**: Never commit `.env` file

### Scalability

**Current Scale**: 0 customers (not deployed yet)

**Target Scale**: 100-300 concurrent customers

**Scaling Math**:
- 300 customers sign up
- Each gets 7 emails over 11 days
- Total: 2100 emails
- Distribution: ~200 emails/day (~8 emails/hour)
- Peak load: Assume 3X average = 24 emails/hour (manageable)

**Resource Usage at Target Scale**:
- **Memory**: 3-4GB (for Prefect + FastAPI + PostgreSQL)
- **CPU**: <10% average (mostly idle, spikes during email sends)
- **Storage**: <10GB (PostgreSQL stores flow run history)
- **Network**: Minimal (Notion + Resend API calls)

**Scaling Headroom**:
- Homelab: 32-64GB RAM, 14-16 threads, 1TB storage
- Used: ~4GB RAM, <10% CPU, <10GB storage
- **Headroom**: Can easily scale to 1000+ customers

### Maintainability

**Code Quality**:
- Use type hints (Python 3.11+)
- Add docstrings to all functions
- Follow PEP 8 style guide
- Use Pydantic for validation

**Testing**:
- Unit tests for all tasks (pytest)
- Integration tests for flows (pytest with mocks)
- E2E tests for webhooks (pytest with live server)
- Minimum 80% code coverage

**Documentation**:
- Inline comments for complex logic
- README for deployment instructions
- Architecture diagram (ASCII art)
- Troubleshooting guide

**Monitoring**:
- Prefect UI for flow runs
- Notion for email logs
- systemd logs for FastAPI server
- PostgreSQL logs for Prefect Server

---

## Risk Assessment

### High Risk Areas

**Risk 1: Prefect Server Stability**
- **Description**: Prefect Server crashes or becomes unavailable
- **Impact**: No new flows scheduled, existing scheduled flows don't run
- **Likelihood**: Medium (database locks, resource exhaustion)
- **Mitigation**:
  - Use PostgreSQL (not SQLite) for Prefect database
  - Monitor Prefect Server logs with systemd
  - Set up restart policy (systemd auto-restart)
  - Add health check endpoint (`GET /api/health`)
- **Detection**: Monitor Prefect UI, set up Uptime Kuma alert

**Risk 2: Duplicate Email Sends**
- **Description**: Email sent twice to same customer (bug in scheduling)
- **Impact**: Customer receives duplicate emails, unprofessional
- **Likelihood**: Medium (if idempotency not handled)
- **Mitigation**:
  - Check Notion "Email X Sent" flag before sending
  - Use Prefect's idempotency key (flow run ID)
  - Add database constraint (unique per customer per email_number)
- **Detection**: Monitor Notion logs for duplicate entries

**Risk 3: Failed Email Sends**
- **Description**: Resend API fails, email not delivered
- **Impact**: Customer doesn't receive email in sequence
- **Likelihood**: Low (Resend has 99.9% uptime)
- **Mitigation**:
  - Prefect retries (3 attempts with exponential backoff)
  - Log all failures to Notion with error message
  - Manual review dashboard in Notion
- **Detection**: Prefect UI shows failed flows, Notion shows failed status

### Medium Risk Areas

**Risk 4: Resource Exhaustion (Homelab)**
- **Description**: Homelab runs out of RAM or CPU
- **Impact**: Prefect Server/Worker crashes, emails delayed
- **Likelihood**: Low (only 4GB used out of 32-64GB)
- **Mitigation**:
  - Monitor resource usage (htop, Grafana)
  - Set memory limits for Docker containers
  - Add swap space if needed
- **Detection**: System monitoring tools, systemd alerts

**Risk 5: Cal.com Webhook Signature Verification**
- **Description**: Webhook signature invalid or expired
- **Impact**: Can't process meeting bookings
- **Likelihood**: Low (Cal.com has good docs)
- **Mitigation**:
  - Follow Cal.com docs exactly
  - Test with ngrok before production
  - Log signature verification failures
- **Detection**: Prefect logs show signature errors

### Low Risk Areas

**Risk 6: Notion API Rate Limits**
- **Description**: Exceed Notion API rate limits (3 req/sec)
- **Impact**: API calls fail, need to retry
- **Likelihood**: Very Low (we send <1 email/minute on average)
- **Mitigation**:
  - Respect rate limits (built into notion-client)
  - Use exponential backoff for retries
- **Detection**: Notion API errors in Prefect logs

**Risk 7: Email Content Errors**
- **Description**: Template variables not substituted correctly
- **Impact**: Customer sees `{{placeholder}}` in email
- **Likelihood**: Very Low (already tested all 7 templates)
- **Mitigation**:
  - Test all templates before deployment
  - Add validation to check for `{{` in final email
- **Detection**: Manual review of sent emails

---

## Testing Strategy

### Unit Tests

**Test Coverage**:
- `tasks/notion_operations.py` - Mock Notion API
- `tasks/resend_operations.py` - Mock Resend API
- `tasks/routing.py` - Test segment classification logic
- `tasks/webhook_operations.py` - Test webhook payload validation

**Example**:
```python
def test_classify_segment_critical():
    segment = classify_segment(red_systems=2, orange_systems=1)
    assert segment == "CRITICAL"

def test_send_email_with_template(mock_resend):
    result = send_email(to="test@example.com", template_id="christmas_email_1", variables={})
    assert result["status"] == "sent"
    mock_resend.assert_called_once()
```

### Integration Tests

**Test Coverage**:
- `flows/signup_handler.py` - Test full signup flow with mocked Notion
- `flows/send_email_flow.py` - Test email flow with mocked Resend
- Scheduling logic - Test Prefect deployment scheduling

**Example**:
```python
@pytest.mark.integration
def test_signup_handler_flow_creates_contact(mock_notion):
    result = signup_handler_flow(email="test@example.com", first_name="Test")
    assert result["status"] == "success"
    mock_notion.create_page.assert_called_once()
```

### E2E Tests

**Test Coverage**:
- Webhook endpoint → Prefect flow → Scheduled emails
- Full sequence from signup to all 7 emails sent

**Example**:
```python
@pytest.mark.e2e
def test_webhook_triggers_email_sequence(test_client, prefect_test_server):
    response = test_client.post("/webhook/christmas-signup", json={
        "email": "test@example.com",
        "first_name": "Test",
        "assessment_score": 45
    })
    assert response.status_code == 202

    # Verify 7 flows scheduled in Prefect
    scheduled_flows = prefect_test_server.get_scheduled_flows()
    assert len(scheduled_flows) == 7
```

### Manual Testing

**Test Scenarios**:
1. **Happy Path**: Sign up → Receive all 7 emails over 11 days
2. **Error Handling**: Resend API fails → Retry 3 times → Log failure
3. **Duplicate Prevention**: Sign up twice → Only 1 sequence triggered
4. **Cal.com Integration**: Book meeting → Receive reminder emails
5. **Performance**: 10 signups/minute → All scheduled correctly

---

## Development Environment

### Setup Required

```bash
# 1. Clone repository (already done)
cd /Users/sangle/Dev/action/projects/perfect

# 2. Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with real API keys

# 5. Start Prefect Server (homelab)
prefect server start --host 0.0.0.0

# 6. Start Prefect Worker (separate terminal)
prefect worker start --pool default-pool

# 7. Deploy flows (separate terminal)
python campaigns/christmas_campaign/deployments/deploy_christmas.py

# 8. Start FastAPI webhook server
uvicorn server:app --reload --port 8000
```

### Run Command

**Development** (with auto-reload):
```bash
# Terminal 1: Prefect Server
prefect server start

# Terminal 2: Prefect Worker
prefect worker start --pool default-pool

# Terminal 3: FastAPI Server
uvicorn server:app --reload
```

**Production** (homelab with systemd):
```bash
# Prefect Server
sudo systemctl start prefect-server

# Prefect Worker
sudo systemctl start prefect-worker

# FastAPI Server
sudo systemctl start perfect-api
```

### Test Command

```bash
# Unit tests
pytest campaigns/christmas_campaign/tests/ -v

# Integration tests
pytest campaigns/christmas_campaign/tests/ -v --integration

# E2E tests
pytest campaigns/christmas_campaign/tests/ -v --e2e

# Coverage report
pytest campaigns/christmas_campaign/tests/ --cov --cov-report=html
```

### Build Command

Not applicable (Python project, no build step)

---

## Homelab Capacity Analysis

### Server Specs
- **RAM**: 32-64GB
- **CPU**: 14-16 threads
- **Storage**: 1TB SSD

### Estimated Resource Usage

**Per Customer**:
- RAM: ~10KB (Prefect flow run metadata)
- CPU: ~1 second total (spread over 11 days)
- Storage: ~1KB (Prefect database row)

**For 300 Customers**:
- RAM: ~3MB (300 × 10KB) - **negligible**
- CPU: ~5 minutes total (spread over 11 days) - **<0.1% utilization**
- Storage: ~300KB (300 × 1KB) - **negligible**

**Infrastructure Overhead**:
- Prefect Server: ~1-2GB RAM, ~100MB storage
- PostgreSQL: ~500MB-1GB RAM, ~5-10GB storage
- FastAPI: ~200MB RAM
- Prefect Worker: ~500MB RAM × number of workers

**Total at 300 Customers**:
- **RAM**: ~3-4GB (Prefect Server + PostgreSQL + FastAPI + 1 worker)
- **CPU**: <10% average (spikes during email sends)
- **Storage**: ~15GB (PostgreSQL flow history)

### Scaling Capacity

**Can Homelab Handle Target Load?** ✅ **YES!**

**Headroom Analysis**:
- **RAM**: 4GB used / 32-64GB available = **6-12% utilization**
- **CPU**: <10% average / 100% available = **<10% utilization**
- **Storage**: 15GB used / 1TB available = **1.5% utilization**

**Maximum Capacity**:
- With current architecture: **1000+ customers** (10X current target)
- Bottleneck: Resend API rate limits (not homelab resources)

**Scaling Beyond 1000 Customers**:
- Add more Prefect Workers (horizontal scaling)
- Use Redis for work queue (instead of PostgreSQL polling)
- Consider Prefect Cloud for distributed deployment

---

## Next Steps

1. Create detailed PLAN.md with 4 implementation waves
2. Design Prefect deployment strategy (parameterized vs. separate)
3. Define exact Notion database schemas needed
4. Plan testing strategy for each wave
5. Get user approval before proceeding to implementation

---

**Discovery Complete**: 2025-11-19
**Status**: Ready for PLANNING phase
**Confidence**: High (all technical constraints understood)
