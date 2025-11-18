# Discovery: Christmas Campaign Email Automation

## Requirements Understanding

### Core Functionality
Build automated email workflows for Christmas Campaign (Model 16 - Traditional Service $2,997) including:

1. **7-Email Nurture Sequence** (Assessment → Diagnostic Booking)
   - Email 1: Results (immediate after assessment)
   - Email 2: Quick Wins (Day 2, +48h)
   - Email 3: Horror Story (Day 3, +24h)
   - Email 4: First Ask (Day 4, +24h)
   - Email 5: Case Study (Day 6, +48h)
   - Email 6: Checklist (Day 8, +48h)
   - Email 7: Final Ask (Day 10, +48h)

2. **Pre-Call Prep Sequence** (3 emails after booking)
   - Email 1: Booking confirmation (immediate)
   - Email 2: Questionnaire reminder (24h before call)
   - Email 3: Final reminder (2h before call)

3. **Customer Portal Delivery** (60-second automation)
   - Trigger: Diagnostic call completion
   - Create Notion portal page
   - Upload diagnostic report
   - Create 90-day timeline
   - Send portal access email

4. **Exit Condition Logic**
   - Booking exit: Stop nurture, start pre-call prep
   - Unsubscribe exit: Remove from all sequences
   - Sequence complete exit: Move to long-term nurture

5. **Phase 2 Transition** (Day 14 decision email)
   - Triggered 14 days after diagnostic call
   - Present 3-tier Phase 2 options (2A/2B/2C)

6. **Phase 2B Coaching Emails** (12-week program)
   - Welcome email (enrollment)
   - Weekly prep emails (24h before coaching call)
   - Homework reminders (3 days after call)
   - Monthly progress reports (Week 4, 8, 12)
   - Completion email (Week 12)

### User Stories
- **As a lead**, I receive personalized email sequence based on my assessment results
- **As a business owner**, I see automated customer portal created within 60 seconds of diagnostic call
- **As a Phase 2B customer**, I receive structured coaching support emails throughout 12-week program
- **As admin**, I can edit email templates in Notion without code deployment

### Acceptance Criteria
- [ ] 7-email nurture sequence sends at correct intervals (immediate, +48h, +24h, +24h, +48h, +48h, +48h)
- [ ] Email personalization works ({{first_name}}, {{business_name}}, etc.)
- [ ] Exit conditions properly stop/redirect sequences
- [ ] Customer portal created <60 seconds after diagnostic call
- [ ] All emails stored in Notion templates (dynamic)
- [ ] Cal.com booking triggers pre-call prep sequence
- [ ] Day 14 decision email triggered automatically
- [ ] Phase 2B emails scheduled based on coaching call dates
- [ ] Testing mode uses fast waits (minutes instead of days)
- [ ] Production mode uses real waits (hours/days)

### Constraints
- **Technical**: Must use existing Prefect + FastAPI + Notion + Resend stack
- **Time**: 13-20 hours total implementation
- **Compatibility**: Must integrate with existing `businessx_canada_lead_nurture` campaign
- **No breaking changes**: Existing 5-email sequence must continue working

---

## Codebase Analysis

### Technology Stack
- **Framework**: Prefect v3 (workflow orchestration)
- **Language**: Python 3.x
- **Runtime**: Python venv
- **Database**: Notion API (contacts, templates, customer portals)
- **Email Service**: Resend API (already integrated)
- **API Server**: FastAPI + Uvicorn
- **Testing**: pytest, pytest-mock, pytest-cov
- **Calendar**: Cal.com (webhooks for booking events)

### Relevant Files

**Primary files to modify:**
- `campaigns/businessx_canada_lead_nurture/flows/` - Need to add new flows
- `campaigns/businessx_canada_lead_nurture/tasks/` - May need new task modules
- `server.py` - Add new webhook endpoints for Cal.com
- `.env` - Add new environment variables (CAL_WEBHOOK_SECRET, etc.)

**Test files:**
- `campaigns/businessx_canada_lead_nurture/tests/` - Add new test modules

**Configuration files:**
- `requirements.txt` - May need to add dependencies
- `.env` - Environment variables

### Dependencies

**External packages (already installed):**
- `prefect==3.4.1` - Workflow orchestration
- `notion-client==2.2.1` - Notion API
- `httpx==0.27.2` - HTTP client for Resend API
- `fastapi==0.115.6` - API server
- `uvicorn[standard]==0.34.0` - ASGI server
- `pydantic[email]==2.10.4` - Data validation
- `python-dotenv==1.0.1` - Environment variables
- `pytest==8.3.4` - Testing

**External packages (may need to add):**
- None! All required packages already installed

**Internal modules (existing):**
- `campaigns.businessx_canada_lead_nurture.flows.signup_handler` - Signup flow pattern
- `campaigns.businessx_canada_lead_nurture.flows.assessment_handler` - Assessment flow pattern
- `campaigns.businessx_canada_lead_nurture.flows.email_sequence` - Email sequence pattern (5 emails)
- `campaigns.businessx_canada_lead_nurture.tasks.notion_operations` - Notion CRUD
- `campaigns.businessx_canada_lead_nurture.tasks.resend_operations` - Email sending
- `campaigns.businessx_canada_lead_nurture.tasks.template_operations` - Template fetching
- `campaigns.businessx_canada_lead_nurture.tasks.routing` - Segment classification

**Breaking changes**: None expected

### Code Patterns to Reuse

**Existing patterns to follow:**

1. **Prefect Flow Pattern** (from `email_sequence.py`):
```python
@flow(name="flow-name", log_prints=True)
def my_flow(contact_page_id: str, email: str, ...):
    """Flow with parameters and return dict"""
    # Use tasks
    result = some_task(params)
    # Wait logic
    from time import sleep
    wait_duration = get_wait_duration(email_number=1, testing_mode=TESTING_MODE)
    sleep(wait_duration)
    # Return summary
    return {"success": True, "email_ids": [...]}
```

2. **Prefect Task Pattern** (from `resend_operations.py`):
```python
@task(retries=3, retry_delay_seconds=60, name="task-name")
def my_task(param: str) -> Dict[str, Any]:
    """Task with retry logic and error handling"""
    try:
        # Implementation
        return result
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
```

3. **Template Variable Substitution** (from `template_operations.py`):
```python
template_vars = {
    "first_name": first_name,
    "business_name": business_name,
    "email": email
}
final_html = substitute_variables(template, template_vars)
```

4. **Notion Update Pattern** (from `email_sequence.py`):
```python
update_contact(
    page_id=contact_page_id,
    properties={
        "Field Name": {"checkbox": True},
        "Date Field": {"date": {"start": datetime.now().isoformat()}}
    }
)
```

5. **FastAPI Webhook Pattern** (from `server.py`):
```python
@app.post("/webhook/endpoint")
async def handle_webhook(request: RequestModel, background_tasks: BackgroundTasks):
    """Webhook handler with background task execution"""
    # Validate payload
    # Trigger flow in background
    background_tasks.add_task(my_flow, **params)
    # Return immediate response
    return {"status": "accepted", "message": "Processing..."}
```

**Anti-patterns to avoid:**
- ❌ Don't use synchronous API calls without retry logic
- ❌ Don't hardcode email templates (use Notion templates)
- ❌ Don't skip environment variable validation
- ❌ Don't mix flow logic with task logic (keep separation)

### Architecture Understanding

**Data Flow:**
```
Assessment Completed → Webhook → FastAPI → Prefect Flow
  ↓
7-Email Nurture Sequence (10 days)
  ↓
  ├─> Booking? → Stop nurture → Pre-Call Prep (3 emails)
  │                ↓
  │           Diagnostic Call → Customer Portal (60s) → Day 14 Decision Email
  │                                                          ↓
  │                                                     Phase 2B? → 12-Week Coaching Emails
  │
  ├─> Unsubscribe? → Stop all sequences
  │
  └─> Sequence Complete? → Long-Term Nurture
```

**Module Organization:**
- **Flows** (`campaigns/.../flows/`): High-level workflows, orchestrate tasks, handle waits
- **Tasks** (`campaigns/.../tasks/`): Atomic operations (send email, update Notion, fetch template)
- **Server** (`server.py`): Webhook endpoints, trigger flows in background
- **Config** (`.env`): Environment variables, API keys

**Integration Points:**
- **Notion Templates DB**: Dynamic email templates (fetch via `template_operations.py`)
- **Notion Contacts DB**: Contact management (CRUD via `notion_operations.py`)
- **Notion Customer Portal DB**: NEW - customer portal pages (need to create)
- **Resend API**: Email delivery (via `resend_operations.py`)
- **Cal.com Webhooks**: Booking events (NEW - need webhook handler)

**API Contracts:**
- **Resend API**: POST /emails (already integrated)
- **Notion API**: Query/Create/Update pages (already integrated)
- **Cal.com Webhook**: POST /webhook/booking-complete (NEW)

### Potential Conflicts

**Breaking Changes:**
- None expected - this is additive work

**API Changes:**
- NEW webhook endpoint: `/webhook/booking-complete` for Cal.com
- NEW webhook endpoint: `/webhook/call-complete` for diagnostic call completion
- NEW environment variables: `CAL_WEBHOOK_SECRET`, `NOTION_CUSTOMER_PORTAL_DB_ID`

**Database Migrations:**
- NEW Notion database: "Customer Portal" (need to create in Notion)
- NEW properties in Contacts DB:
  - "Phase" (select: Phase 1 Assessment, Phase 1 Diagnostic, Phase 2A, Phase 2B, Phase 2C)
  - "Diagnostic Call Date" (date)
  - "Booking Status" (select: Not Booked, Booked, Completed, No-Show)
  - "Phase 2 Decision Date" (date)

**Deprecations:**
- None

---

## Technical Constraints

### Performance Requirements
- **Email delivery**: <5 seconds per email
- **Customer portal creation**: <60 seconds total (critical!)
- **Webhook response**: <1 second (202 Accepted)
- **Wait accuracy**: ±5 minutes for scheduled emails

### Browser/Device Support
- N/A (server-side only)

### Security Considerations
- **Webhook authentication**: Verify Cal.com webhook signatures
- **API keys**: Store in `.env`, never commit to git
- **Email validation**: Use Pydantic EmailStr validation
- **OWASP Top 10**:
  - No SQL injection (using Notion API, not SQL)
  - No XSS (server-side only, no user input rendering)
  - Secure API keys (environment variables)

### Scalability
- **Concurrent users**: 100+ simultaneous email sequences
- **Data volume**: 1000+ contacts per month
- **Email throughput**: Resend API limits (3,000/month free tier, then paid)

### Maintainability
- **Tech debt**: Keep flows modular, tasks atomic
- **Documentation**: JSDoc-style comments for all flows/tasks
- **Testing**: >80% code coverage

---

## Risk Assessment

### High Risk Areas
- **Customer portal 60-second delivery**: Notion API latency can spike
  - **Mitigation**: Use async operations, parallel API calls where possible
  - **Fallback**: Email portal URL even if not fully ready, finish setup in background

- **Cal.com webhook reliability**: Webhooks can fail or be delayed
  - **Mitigation**: Implement webhook signature verification, idempotency keys
  - **Fallback**: Manual trigger endpoint for admins

- **Email deliverability**: Spam filters, bounces
  - **Mitigation**: Use Resend (good reputation), proper SPF/DKIM/DMARC
  - **Monitoring**: Track bounce/spam rates via Resend dashboard

### Medium Risk Areas
- **Wait time accuracy**: Sleep-based waits can drift over long sequences
  - **Mitigation**: Use Prefect scheduled runs instead of sleep for long waits
  - **Monitoring**: Log actual send times vs expected

- **Template variable errors**: Missing placeholders break emails
  - **Mitigation**: Validate templates before sending, provide defaults
  - **Monitoring**: Test all templates in pre-launch checklist

- **Notion API rate limits**: 3 requests/second
  - **Mitigation**: Use retries with backoff, batch operations
  - **Monitoring**: Log API errors, alert on rate limit hits

### Low Risk Areas
- **Package dependencies**: All already installed and stable
- **Python version compatibility**: Python 3.x standard library only
- **Code complexity**: Following existing patterns, low novelty

---

## Testing Strategy

### Unit Tests
- **What to test in isolation**:
  - New task functions (send email, create portal, schedule email)
  - Template variable substitution for Christmas emails
  - Segment classification for Christmas campaign
  - Wait duration calculation

### Integration Tests
- **Component interactions to verify**:
  - 7-email sequence flow end-to-end (mocked waits)
  - Pre-call prep sequence trigger from booking webhook
  - Customer portal creation flow
  - Day 14 decision email trigger
  - Phase 2B weekly email scheduling

### E2E Tests
- **User flows to validate**:
  - Complete assessment → 7 emails → booking → pre-call → portal delivery
  - Assessment → no booking → long-term nurture
  - Unsubscribe at Email 3 → all sequences stop

### Manual Testing
- **Specific scenarios to check**:
  - Send all 7 emails to mail-tester.com (spam score 8/10+)
  - Test customer portal creation speed (<60s)
  - Verify Cal.com webhook triggers correctly
  - Check all template variables replaced (no `{{}}` in sent emails)

### Regression Tests
- **Existing features to verify still work**:
  - Original 5-email sequence (businessx_canada_lead_nurture)
  - Signup handler flow
  - Assessment handler flow
  - Notion template fetching
  - Resend email sending

---

## Development Environment

### Setup Required
```bash
# Already installed, just verify
pip install -r requirements.txt

# Add new environment variables to .env
CAL_WEBHOOK_SECRET=xxxxxx (get from Cal.com)
NOTION_CUSTOMER_PORTAL_DB_ID=xxxxxx (create in Notion)

# Create Notion databases
# 1. Customer Portal database (copy from template)
# 2. Update Contacts DB with new properties (Phase, Diagnostic Call Date, etc.)
```

### Run Command
```bash
# Development server (with auto-reload)
uvicorn server:app --reload --port 8000

# Test specific flow
python -c "from campaigns.christmas_campaign.flows.nurture_sequence import christmas_nurture_flow; christmas_nurture_flow(...)"
```

### Test Command
```bash
# All tests
pytest campaigns/christmas_campaign/tests/ -v

# Specific test file
pytest campaigns/christmas_campaign/tests/test_nurture_sequence.py -v

# With coverage
pytest campaigns/christmas_campaign/tests/ --cov=campaigns.christmas_campaign --cov-report=html
```

### Build Command
N/A (Python doesn't require build step)

---

## Key Decisions

1. **New campaign directory vs extend existing?**
   - **Decision**: Create new campaign `campaigns/christmas_campaign/`
   - **Rationale**: Christmas campaign has different structure (7 emails vs 5, new flows for portal/coaching)
   - **Tradeoff**: Some code duplication, but cleaner separation of concerns

2. **Use Prefect scheduled runs or sleep for waits?**
   - **Decision**: Use `time.sleep()` like existing code
   - **Rationale**: Simpler, consistent with existing pattern, good enough for 10-day sequence
   - **Tradeoff**: Less accurate for very long waits, but acceptable for this use case

3. **Store Cal.com booking data in Notion or Supabase?**
   - **Decision**: Store in Notion Contacts DB (existing)
   - **Rationale**: Minimize new dependencies, Notion already used for contacts
   - **Tradeoff**: Notion API slower than Supabase, but good enough for this volume

4. **60-second customer portal delivery: Synchronous or async?**
   - **Decision**: Synchronous with background task
   - **Rationale**: Webhook returns immediately (202), portal creation happens in background, email sent when ready
   - **Tradeoff**: If portal takes >60s, email still sent (with partial portal), finish setup in background

---

## Next Steps

After EXPLORE phase completion:
1. Create detailed implementation plan (PLAN phase)
2. Break down into 4 waves
3. Define TDD approach for each wave
4. Get user approval
5. Proceed to CODE phase via `/execute-coding`
