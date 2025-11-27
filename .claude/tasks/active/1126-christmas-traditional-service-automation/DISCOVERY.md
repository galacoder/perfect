# Discovery: Christmas Traditional Service Automation

**Task ID**: 1126-christmas-traditional-service-automation
**Domain**: coding
**Exploration Date**: 2025-11-26

---

## 1. Codebase Analysis

### Current Project Structure

```
campaigns/christmas_campaign/
    flows/
        __init__.py
        signup_handler.py          # Main entry - handles assessment completion
        send_email_flow.py         # Single email sender with idempotency
        email_sequence_orchestrator.py
        precall_prep_flow.py
    tasks/
        notion_operations.py       # CRUD for Notion (contacts, templates, sequences)
        resend_operations.py       # Email sending via Resend API
        routing.py                 # Segment classification and template routing
    tests/
        __init__.py
        conftest.py                # Shared fixtures (mocks for Notion, Resend, etc.)
        test_signup_handler.py     # Unit tests for signup flow
        test_routing.py            # Tests for segment classification
        test_seed_email_templates.py
        test_precall_prep_dry_run.py
    diagrams/
        CAMPAIGN_OVERVIEW.txt
```

### Key Patterns Identified

#### 1. Flow Architecture Pattern

**Signup Handler Flow** (`signup_handler.py`):
- Entry point that receives webhook data
- Checks idempotency via Email Sequence DB
- Creates sequence tracking record
- Schedules individual emails via Prefect Deployment

**Send Email Flow** (`send_email_flow.py`):
- Receives single email parameters
- Performs idempotency check (has email X been sent?)
- Fetches template from Notion
- Substitutes variables
- Sends via Resend API
- Updates Email Sequence DB with "Email X Sent" timestamp

#### 2. Secret Block Loading Pattern

```python
# Module-level loading with fallback
try:
    NOTION_TOKEN = Secret.load("notion-token").get()
    print("Loaded from Prefect Secret blocks")
except Exception as e:
    NOTION_TOKEN = os.getenv("NOTION_TOKEN")
```

**Secret Blocks in Use**:
- `notion-token`
- `notion-email-templates-db-id`
- `notion-email-sequence-db-id`
- `notion-businessx-db-id`
- `notion-customer-projects-db-id`
- `notion-email-analytics-db-id`
- `resend-api-key`
- `testing-mode`

#### 3. Email Scheduling Pattern

```python
async def schedule_all_emails():
    async with get_client() as client:
        deployment = await client.read_deployment_by_name("flow-name/deployment-name")

        from prefect.states import Scheduled
        flow_run = await client.create_flow_run_from_deployment(
            deployment_id=deployment.id,
            parameters={...},
            state=Scheduled(scheduled_time=scheduled_time)
        )
```

**Timing Logic**:
- Testing mode: Minutes (1min, 2min, 3min...)
- Production mode: Hours/Days (24h, 72h, 120h...)

#### 4. Template Routing Pattern

```python
def get_email_template_id(email_number: int, segment: str) -> str:
    # Universal emails: christmas_email_1, christmas_email_3, etc.
    # Segment-specific: christmas_email_2a_critical, christmas_email_7c_optimize
```

#### 5. Testing Pattern

**Fixture-based mocking** (`conftest.py`):
- `prefect_test_mode`: Sets ephemeral API URL
- `mock_schedule_email_sequence`: Prevents actual Prefect API calls
- Sample data fixtures: `sample_contact_data`, `sample_assessment_critical`, etc.

**Test structure**:
```python
@patch('campaigns.christmas_campaign.flows.signup_handler.search_email_sequence_by_email')
@patch('campaigns.christmas_campaign.flows.signup_handler.search_contact_by_email')
def test_signup_handler_new_contact_success(mock_search_contact, mock_search_sequence):
    # Setup mocks
    mock_search_sequence.return_value = None
    mock_search_contact.return_value = {"id": "contact-123"}

    # Run flow
    result = signup_handler_flow(...)

    # Assertions
    assert result["status"] == "success"
    mock_search_sequence.assert_called_once_with(...)
```

---

## 2. What Needs to Be Built

### New Sequences Required

| Sequence | Trigger | Emails | Timing (Production) | Timing (Testing) |
|----------|---------|--------|---------------------|------------------|
| No-Show Recovery | Calendly no-show webhook | 3 | 5min, 24h, 48h | 1min, 2min, 3min |
| Post-Call Maybe | Manual/CRM trigger | 3 | 1h, 72h, 168h | 1min, 2min, 3min |
| Onboarding Phase 1 | DocuSign + Payment | 3 | 1h, 24h, 72h | 1min, 2min, 3min |

### Templates Already in Notion

Database ID: `2ab7c374-1115-8115-932c-ca6789c5b87b`

**Template Names**:
- `noshow_recovery_email_1`, `noshow_recovery_email_2`, `noshow_recovery_email_3`
- `postcall_maybe_email_1`, `postcall_maybe_email_2`, `postcall_maybe_email_3`
- `onboarding_phase1_email_1`, `onboarding_phase1_email_2`, `onboarding_phase1_email_3`

### Personalization Variables to Support

**Existing** (from signup_handler):
- `{{first_name}}`, `{{business_name}}`, `{{segment}}`, `{{assessment_score}}`

**New Required**:
- `{{calendly_link}}` - Reschedule link for no-show
- `{{calendly_link_5min}}` - Quick 5-min reschedule option
- `{{call_time}}` - Scheduled meeting time (for reference)
- `{{broken_area_1}}`, `{{broken_area_2}}`, `{{broken_area_3}}` - Problem areas discussed
- `{{observation_dates}}` - Onboarding observation session dates
- `{{start_time}}` - Phase 1 start time
- `{{salon_address}}` - Client business location

---

## 3. Dependencies Identified

### Existing (Reusable)

| Component | Location | Reuse Strategy |
|-----------|----------|----------------|
| `fetch_email_template` | `tasks/notion_operations.py` | Direct reuse |
| `send_template_email` | `tasks/resend_operations.py` | Direct reuse |
| `substitute_variables` | `tasks/resend_operations.py` | Direct reuse |
| `log_email_analytics` | `tasks/notion_operations.py` | Direct reuse |
| `search_contact_by_email` | `tasks/notion_operations.py` | Direct reuse |

### New Required

| Component | Description |
|-----------|-------------|
| `noshow_recovery_handler.py` | Flow to handle Calendly no-show webhook |
| `postcall_maybe_handler.py` | Flow to handle post-call "maybe" responses |
| `onboarding_handler.py` | Flow to handle DocuSign + payment trigger |
| `get_sequence_template_id()` | Template routing for new sequences |
| Webhook endpoints in `server.py` | 3 new endpoints |

---

## 4. Risk Assessment

### Low Risk

| Risk | Mitigation |
|------|------------|
| Template fetching | Existing pattern works - reuse `fetch_email_template` |
| Email sending | Existing pattern works - reuse `send_template_email` |
| Notion operations | All CRUD operations already implemented |

### Medium Risk

| Risk | Mitigation |
|------|------------|
| Calendly webhook integration | Need to research Calendly no-show event payload structure |
| New Email Sequence DB fields | May need to add columns for new sequences |
| Testing mode for different timings | Need separate timing configs per sequence type |

### High Risk

| Risk | Mitigation |
|------|------------|
| DocuSign + Payment dual trigger | Complex - may need intermediate state tracking |
| Multiple active sequences per contact | Need idempotency checks per sequence type |

---

## 5. Recommendations

### Architecture Decisions

1. **Create separate handler flows per sequence type**
   - `noshow_recovery_handler.py` - Single responsibility
   - `postcall_maybe_handler.py` - Single responsibility
   - `onboarding_handler.py` - Single responsibility

2. **Extend routing.py with new function**
   ```python
   def get_sequence_template_id(
       sequence_type: Literal["noshow", "postcall", "onboarding"],
       email_number: int
   ) -> str
   ```

3. **Use existing Email Sequence DB** with new fields
   - Add `Sequence Type` select property
   - Add email tracking fields for each sequence type

4. **Webhook structure**
   - `POST /webhook/calendly-noshow` - Calendly no-show events
   - `POST /webhook/postcall-maybe` - Manual CRM trigger
   - `POST /webhook/onboarding-start` - DocuSign completion

### TDD Strategy

**Wave 1**: Foundation
- Create new flow files with minimal structure
- Add new routing function
- Write unit tests for routing

**Wave 2**: No-Show Recovery (Complete with TDD)
- Tests first for handler logic
- Implement handler
- Add webhook endpoint

**Wave 3**: Post-Call Maybe (Complete with TDD)
- Tests first for handler logic
- Implement handler
- Add webhook endpoint

**Wave 4**: Onboarding (Complete with TDD)
- Tests first for handler logic
- Implement handler
- Add webhook endpoint

**Wave 5**: Integration
- E2E tests
- Deployment configuration
- Documentation

---

## 6. Existing Test Coverage

| File | Tests | Coverage |
|------|-------|----------|
| `test_signup_handler.py` | 12 tests | Signup flow, idempotency, segment classification |
| `test_routing.py` | Segment classification, template routing |
| `conftest.py` | Shared fixtures |

### Test Patterns to Follow

1. Mock Prefect API calls
2. Mock Notion operations
3. Mock Resend operations
4. Test idempotency
5. Test segment classification
6. Test error handling

---

## 7. Key Files Reference

| Purpose | File Path |
|---------|-----------|
| Entry flow template | `flows/signup_handler.py` |
| Email sender template | `flows/send_email_flow.py` |
| Notion operations | `tasks/notion_operations.py` |
| Resend operations | `tasks/resend_operations.py` |
| Routing logic | `tasks/routing.py` |
| Test fixtures | `tests/conftest.py` |
| Webhook server | `server.py` |

---

## Summary

**Status**: EXPLORE phase complete
**Next**: PLAN phase with TDD-focused waves
**Estimated Effort**: 6-8 hours
**Confidence**: High (existing patterns are well-established)
