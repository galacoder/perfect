# Christmas Campaign 2025 - Technical Architecture

**Campaign**: Christmas 2025
**Last Updated**: 2025-11-30
**Status**: Production (Active) - Migrated to Kestra
**Tech Stack**: Kestra (self-hosted), Notion API, Resend API, Next.js Website

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Email Responsibility Matrix](#email-responsibility-matrix)
3. [Email Funnel Flow](#email-funnel-flow)
4. [5 Email Sequence Types](#5-email-sequence-types)
5. [Complete Template Reference](#complete-template-reference)
6. [Webhook Integration](#webhook-integration)
7. [Data Flow Architecture](#data-flow-architecture)
8. [Deployment Registry](#deployment-registry)

---

## System Overview

The Christmas Campaign is a multi-sequence email automation system built on Prefect v3 that manages 21 email templates across 5 distinct nurture sequences.

### Key Metrics

- **Total Sequences**: 5 (Lead Nurture, 5-Day, No-Show, Post-Call, Onboarding)
- **Total Templates**: 21 active email templates in Notion
- **Triggers**: 5 webhook endpoints
- **Deployments**: 4 Prefect flow deployments
- **Testing Mode**: 1-minute intervals (production: day-based intervals)

### Core Components

1. **Kestra Flows**: Orchestrate email sequences with YAML-based workflows
2. **Notion Database**: Store email templates (dynamic content) and sequence tracker
3. **Resend API**: Deliver emails with tracking
4. **Website (Next.js)**: Sends signup and Email #1, triggers Kestra webhooks
5. **Secret Management**: Docker Compose environment variables

---

## Email Responsibility Matrix

**CRITICAL ARCHITECTURAL DECISION** (November 2025): Email sending responsibility is split between Website and Kestra to prevent duplicates and ensure proper sequencing.

### Who Sends Which Email?

| Sequence | Email # | Sent By | Timing | Payload Requirement |
|----------|---------|---------|--------|---------------------|
| **Signup** | - | **Website** | Immediate (on form submit) | N/A |
| **5-Day Assessment** | #1 | **Website** | Immediate (after assessment) | ✅ Must provide `email_1_sent_at` |
| **5-Day Assessment** | #2 | **Kestra** | `email_1_sent_at` + 24h | ✅ Requires `email_1_sent_at` |
| **5-Day Assessment** | #3 | **Kestra** | `email_1_sent_at` + 72h (3d) | ✅ Requires `email_1_sent_at` |
| **5-Day Assessment** | #4 | **Kestra** | `email_1_sent_at` + 96h (4d) | ✅ Requires `email_1_sent_at` |
| **5-Day Assessment** | #5 | **Kestra** | `email_1_sent_at` + 120h (5d) | ✅ Requires `email_1_sent_at` |
| **No-Show Recovery** | All 3 | **Kestra** | 5min, 24h, 48h | ❌ No `email_1_sent_at` needed |
| **Post-Call Maybe** | All 3 | **Kestra** | 1h, 3d, 7d | ❌ No `email_1_sent_at` needed |
| **Onboarding** | All 3 | **Kestra** | 1h, 1d, 3d | ❌ No `email_1_sent_at` needed |

### Why This Split?

**Problem**: Original Prefect architecture sent ALL emails from backend, including Email #1 after assessment.

**Issues**:
1. **Race condition**: Website shows "Assessment complete!" but email not sent yet
2. **Delay**: Email #1 could be delayed if Prefect worker is busy
3. **User confusion**: "Where's my email?" if backend is slow

**Solution**: Website sends Email #1 synchronously, then tells Kestra to handle follow-ups.

**Benefits**:
- ✅ Email #1 arrives instantly (user sees it while reading results)
- ✅ No race conditions
- ✅ Clear handoff: Website owns first touch, Kestra owns nurture
- ✅ Prevents duplicate Email #1 sends

### Critical Requirement: email_1_sent_at

**For 5-Day Assessment Sequence**, website MUST:

1. **Send Email #1** using own email service (Resend API from Next.js)
2. **Record timestamp** when Email #1 was sent
3. **Include `email_1_sent_at`** in webhook payload to Kestra (ISO 8601 format)
4. **Include `email_1_status`** = "sent" to confirm delivery

**Example Webhook Payload**:
```json
{
  "email": "customer@example.com",
  "first_name": "Sarah",
  "business_name": "Sarah's Salon",
  "red_systems": 2,
  "orange_systems": 1,
  "weakest_system_1": "GPS",
  "revenue_leak_total": 14700,
  "email_1_sent_at": "2025-12-01T10:30:00Z",    // CRITICAL!
  "email_1_status": "sent"                        // CRITICAL!
}
```

### What Kestra Does With email_1_sent_at

1. **Validates** timestamp format (ISO 8601)
2. **Records** Email #1 in Notion Sequence Tracker as `sent_by='website'`
3. **Calculates delays** for Emails #2-5 relative to this timestamp:
   - Email #2: `email_1_sent_at + 24 hours`
   - Email #3: `email_1_sent_at + 72 hours`
   - Email #4: `email_1_sent_at + 96 hours`
   - Email #5: `email_1_sent_at + 120 hours`

### Fallback Behavior

If `email_1_sent_at` is **missing**:
- Kestra logs **WARNING**
- Uses **webhook trigger time** as fallback
- Continues execution (doesn't fail)

---

## Email Funnel Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CHRISTMAS CAMPAIGN EMAIL FUNNEL                      │
└─────────────────────────────────────────────────────────────────────────────┘

                             ┌──────────────┐
                             │   OPT-IN     │
                             │  (Website)   │
                             └──────┬───────┘
                                    │
                 ┌──────────────────┴──────────────────┐
                 │                                     │
          ┌──────▼──────┐                      ┌──────▼──────┐
          │  Lead Nurture│                      │  5-Day E1   │
          │  Sequence    │                      │  (Direct)   │
          │  (5 emails)  │                      └──────┬──────┘
          └──────┬───────┘                             │
                 │                                     │
                 │  ┌─────────────────────────┐        │
                 └──►     ASSESSMENT          │◄───────┘
                    │   (Website Page)        │
                    └──────────┬──────────────┘
                               │
                        ┌──────▼───────┐
                        │  Assessment   │
                        │  Completed    │
                        └──────┬────────┘
                               │
                    ┌──────────▼──────────┐
                    │   5-Day Sequence    │
                    │   (E2, E3, E4, E5)  │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   BOOK CALL         │
                    │   (Calendly)        │
                    └──────┬───────────────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
    ┌─────▼─────┐    ┌────▼─────┐    ┌─────▼─────┐
    │  No-Show  │    │   CALL   │    │   Maybe   │
    │  Recovery │    │ HAPPENED │    │ Follow-Up │
    │ (3 emails)│    └────┬─────┘    │ (3 emails)│
    └───────────┘         │          └───────────┘
                          │
                    ┌─────▼──────┐
                    │   CLOSED   │
                    │  (Payment) │
                    └─────┬──────┘
                          │
                   ┌──────▼──────┐
                   │ Onboarding  │
                   │  Phase 1    │
                   │ (3 emails)  │
                   └─────────────┘
```

---

## 5 Email Sequence Types

### 1. Lead Nurture Sequence (Pre-Assessment)

**Purpose**: Warm up leads and drive assessment completion
**Trigger**: Initial opt-in via website form
**Template Prefix**: `lead_nurture_email_*`
**Email Count**: 5
**Timing**: Day 0, Day 2, Day 4, Day 6, Day 8

| Email | Template ID | Subject | Goal |
|-------|-------------|---------|------|
| 1 | `lead_nurture_email_1` | Welcome + Assessment Link | Deliver assessment link |
| 2 | `lead_nurture_email_2` | Why Assessment Matters | Build value |
| 3 | `lead_nurture_email_3` | Success Story | Social proof |
| 4 | `lead_nurture_email_4` | Common Mistakes | Create urgency |
| 5 | `lead_nurture_email_5` | Final Reminder | Last push |

**Flow**: `signup_handler.py` → Sends lead_nurture_email_1-5 + immediate christmas_email_1

---

### 2. 5-Day Assessment Sequence (Post-Assessment)

**Purpose**: Nurture assessed leads to book diagnostic call
**Trigger**: Assessment completion
**Template Prefix**: `christmas_email_*`
**Email Count**: 5
**Timing**: Day 0 (E1), Day 2 (E2), Day 4 (E3), Day 6 (E4), Day 8 (E5)

| Email | Template ID | Subject | Key Variables | Goal |
|-------|-------------|---------|---------------|------|
| E1 | `christmas_email_1` | Your Results Are In | `overall_score`, `TotalRevenueLeak_K`, `weakest_system_1` | Deliver results + book call |
| E2 | `christmas_email_2` | Fix Your [WeakestSystem] | `WeakestSystem1`, `personalized_tip_1` | Focus on biggest pain |
| E3 | `christmas_email_3` | The Christmas Surge Playbook | `pdf_download_link`, `spots_remaining` | Deliver value + scarcity |
| E4 | `christmas_email_4` | Case Study: $44K in 30 Days | `spots_remaining`, `days_to_deadline` | Social proof + urgency |
| E5 | `christmas_email_5` | Final Call (Literally) | `bookings_count`, `calendly_link` | Last chance to book |

**Flow**: `signup_handler.py` → Sends christmas_email_1 immediately after assessment

**Timing (Production)**:
- E1: Immediate (Day 0)
- E2: 2 days later
- E3: 4 days later (Day 4 total)
- E4: 6 days later (Day 6 total)
- E5: 8 days later (Day 8 total)

**Timing (Testing Mode)**:
- E1: Immediate
- E2: 1 minute later
- E3: 2 minutes later (3 min total)
- E4: 3 minutes later (6 min total)
- E5: 4 minutes later (10 min total)

---

### 3. No-Show Recovery Sequence

**Purpose**: Re-engage leads who missed their diagnostic call
**Trigger**: Calendly webhook (no-show event)
**Template Prefix**: `noshow_recovery_email_*`
**Email Count**: 3
**Timing**: 5 min, 24 hours, 48 hours

| Email | Template ID | Subject | Timing | Goal |
|-------|-------------|---------|--------|------|
| 1 | `noshow_recovery_email_1` | We Missed You | 5 minutes after | Immediate reschedule |
| 2 | `noshow_recovery_email_2` | Your Spot is Still Available | 24 hours after | Gentle reminder |
| 3 | `noshow_recovery_email_3` | Last Chance to Rebook | 48 hours after | Final attempt |

**Flow**: `noshow_recovery_handler.py`
**Webhook**: `POST /webhook/calendly-noshow`

**Key Variables**: `first_name`, `calendly_link`, `diagnostic_call_date`

---

### 4. Post-Call Maybe Sequence

**Purpose**: Nurture "I need to think about it" leads
**Trigger**: Manual webhook after sales call
**Template Prefix**: `postcall_maybe_email_*`
**Email Count**: 3
**Timing**: 1 hour, Day 3, Day 7

| Email | Template ID | Subject | Timing | Goal |
|-------|-------------|---------|--------|------|
| 1 | `postcall_maybe_email_1` | Quick Follow-Up | 1 hour after call | Address concerns |
| 2 | `postcall_maybe_email_2` | Common Questions Answered | Day 3 | Overcome objections |
| 3 | `postcall_maybe_email_3` | Ready When You Are | Day 7 | Keep door open |

**Flow**: `postcall_maybe_handler.py`
**Webhook**: `POST /webhook/postcall-maybe`

**Key Variables**: `first_name`, `business_name`, `calendly_link`

---

### 5. Onboarding Phase 1 Sequence

**Purpose**: Onboard new clients after payment
**Trigger**: Payment/DocuSign completion
**Template Prefix**: `onboarding_phase1_email_*`
**Email Count**: 3
**Timing**: 1 hour, Day 1, Day 3

| Email | Template ID | Subject | Timing | Goal |
|-------|-------------|---------|--------|------|
| 1 | `onboarding_phase1_email_1` | Welcome to BusinessX! | 1 hour after payment | Portal access + next steps |
| 2 | `onboarding_phase1_email_2` | Your First Week Checklist | Day 1 | Set expectations |
| 3 | `onboarding_phase1_email_3` | Prep for Kickoff Call | Day 3 | Prepare for diagnostic |

**Flow**: `onboarding_handler.py`
**Webhook**: `POST /webhook/onboarding-start`

**Key Variables**: `first_name`, `business_name`, `portal_url`, `diagnostic_call_date`

---

## Complete Template Reference

### All 21 Active Templates in Notion

| # | Template ID | Sequence | Email # | Timing | Key Variables |
|---|-------------|----------|---------|--------|---------------|
| 1 | `lead_nurture_email_1` | Lead Nurture | 1/5 | Day 0 | `first_name`, `business_name` |
| 2 | `lead_nurture_email_2` | Lead Nurture | 2/5 | Day 2 | `first_name` |
| 3 | `lead_nurture_email_3` | Lead Nurture | 3/5 | Day 4 | `first_name` |
| 4 | `lead_nurture_email_4` | Lead Nurture | 4/5 | Day 6 | `first_name` |
| 5 | `lead_nurture_email_5` | Lead Nurture | 5/5 | Day 8 | `first_name` |
| 6 | `christmas_email_1` | 5-Day (E1) | 1/5 | Day 0 | `first_name`, `overall_score`, `TotalRevenueLeak_K`, `weakest_system_1` |
| 7 | `christmas_email_2` | 5-Day (E2) | 2/5 | Day 2 | `first_name`, `WeakestSystem1`, `personalized_tip_1` |
| 8 | `christmas_email_3` | 5-Day (E3) | 3/5 | Day 4 | `first_name`, `pdf_download_link`, `spots_remaining` |
| 9 | `christmas_email_4` | 5-Day (E4) | 4/5 | Day 6 | `first_name`, `spots_remaining`, `days_to_deadline` |
| 10 | `christmas_email_5` | 5-Day (E5) | 5/5 | Day 8 | `first_name`, `bookings_count`, `calendly_link`, `deadline_date` |
| 11 | `noshow_recovery_email_1` | No-Show | 1/3 | 5 min | `first_name`, `calendly_link` |
| 12 | `noshow_recovery_email_2` | No-Show | 2/3 | 24 hr | `first_name`, `calendly_link` |
| 13 | `noshow_recovery_email_3` | No-Show | 3/3 | 48 hr | `first_name`, `calendly_link` |
| 14 | `postcall_maybe_email_1` | Post-Call | 1/3 | 1 hr | `first_name`, `business_name` |
| 15 | `postcall_maybe_email_2` | Post-Call | 2/3 | Day 3 | `first_name` |
| 16 | `postcall_maybe_email_3` | Post-Call | 3/3 | Day 7 | `first_name`, `calendly_link` |
| 17 | `onboarding_phase1_email_1` | Onboarding | 1/3 | 1 hr | `first_name`, `business_name`, `portal_url` |
| 18 | `onboarding_phase1_email_2` | Onboarding | 2/3 | Day 1 | `first_name`, `portal_url` |
| 19 | `onboarding_phase1_email_3` | Onboarding | 3/3 | Day 3 | `first_name`, `diagnostic_call_date` |
| 20-21 | *(Reserved for future sequences)* | - | - | - | - |

**Notion Database**: All templates stored in `notion-email-templates-db-id` Secret block

---

## Webhook Integration

### Website → Prefect Flow Mapping

| Webhook Endpoint | Prefect Deployment | Sequences Triggered | Response |
|-----------------|-------------------|---------------------|----------|
| `POST /webhook/christmas-signup` | `christmas-signup-handler` | Lead Nurture (5) + 5-Day E1 (1) | 200 OK + contact_id |
| `POST /webhook/calendly-noshow` | `christmas-noshow-recovery-handler` | No-Show Recovery (3) | 200 OK + sequence_id |
| `POST /webhook/postcall-maybe` | `christmas-postcall-maybe-handler` | Post-Call Maybe (3) | 200 OK + sequence_id |
| `POST /webhook/onboarding-start` | `christmas-onboarding-handler` | Onboarding Phase 1 (3) | 200 OK + sequence_id |

### Webhook Payload Examples

#### Christmas Signup
```json
{
  "email": "sarah@sarahssalon.com",
  "first_name": "Sarah",
  "business_name": "Sarah's Salon",
  "red_systems": 2,
  "orange_systems": 1,
  "yellow_systems": 2,
  "green_systems": 3,
  "weakest_system_1": "GPS",
  "weakest_system_2": "FUEL",
  "strongest_system": "CABIN",
  "revenue_leak_total": 14700
}
```

#### Calendly No-Show
```json
{
  "email": "sarah@sarahssalon.com",
  "first_name": "Sarah",
  "calendly_event_id": "evt_123abc",
  "scheduled_time": "2025-12-10T14:00:00Z"
}
```

#### Post-Call Maybe
```json
{
  "email": "sarah@sarahssalon.com",
  "first_name": "Sarah",
  "business_name": "Sarah's Salon",
  "call_date": "2025-12-08T15:00:00Z",
  "objection": "need_to_think"
}
```

#### Onboarding Start
```json
{
  "email": "sarah@sarahssalon.com",
  "first_name": "Sarah",
  "business_name": "Sarah's Salon",
  "payment_date": "2025-12-09T16:30:00Z",
  "portal_url": "https://portal.sangletech.com/sarah",
  "diagnostic_call_date": "2025-12-12T10:00:00Z"
}
```

---

## Data Flow Architecture

### Complete Email Sending Flow

```
┌─────────────┐
│   Website   │
│   Form      │
└──────┬──────┘
       │ POST /webhook/christmas-signup
       │
┌──────▼──────────────────────────────────────────────────────────┐
│                    FastAPI Webhook Server                       │
│  (server.py)                                                    │
│                                                                  │
│  1. Validate payload                                            │
│  2. Trigger Prefect deployment via API                          │
│  3. Return 200 OK                                               │
└──────┬──────────────────────────────────────────────────────────┘
       │
       │ Prefect API call
       │
┌──────▼──────────────────────────────────────────────────────────┐
│              Prefect Flow (signup_handler.py)                   │
│                                                                  │
│  1. search_contact_by_email() → Notion Contacts DB              │
│  2. create_or_update_contact() → Notion Contacts DB             │
│  3. get_email_variables() → Build template variables            │
│  4. FOR EACH email in sequence:                                 │
│     a. fetch_template_from_notion() → Notion Templates DB       │
│     b. substitute_variables() → Replace {{vars}}                │
│     c. send_template_email() → Resend API                       │
│     d. sleep() → Wait for next email                            │
└─────────────────────────────────────────────────────────────────┘
```

### Key Functions by Module

**`tasks/notion_operations.py`**:
- `search_contact_by_email()` - Find existing contact
- `create_contact()` - Create new contact record
- `update_contact()` - Update contact with assessment data
- `fetch_template_from_notion()` - Get email template by name

**`tasks/resend_operations.py`**:
- `get_email_variables()` - Build template variables dict
- `substitute_variables()` - Replace {{vars}} in template
- `send_email()` - Send via Resend API
- `send_template_email()` - Combined substitution + send

**`flows/signup_handler.py`**:
- `signup_handler_flow()` - Main orchestration flow
- Handles both Lead Nurture + 5-Day E1 sequences

---

## Deployment Registry

### Active Prefect Deployments

| Deployment Name | Flow File | Entrypoint | Trigger | Status |
|----------------|-----------|------------|---------|--------|
| `christmas-signup-handler` | `signup_handler.py` | `signup_handler_flow` | Webhook | ✅ Active |
| `christmas-noshow-recovery-handler` | `noshow_recovery_handler.py` | `noshow_recovery_flow` | Webhook | ✅ Active |
| `christmas-postcall-maybe-handler` | `postcall_maybe_handler.py` | `postcall_maybe_flow` | Webhook | ✅ Active |
| `christmas-onboarding-handler` | `onboarding_handler.py` | `onboarding_flow` | Webhook | ✅ Active |

**Prefect Server**: https://prefect.galatek.dev/api
**Worker**: Python 3.11 on production server
**Work Pool**: `default-agent-pool`

### Deployment Configuration

**Naming Convention**: `christmas-{sequence-name}-handler`

**Pull Strategy**: Git-based (auto-pull from GitHub on each run)

**Repository**: https://github.com/galacoder/perfect.git

**Branch**: `main`

**Secret Blocks Required**:
- `notion-token` - Notion API integration token
- `notion-contacts-db-id` - Contacts database ID
- `notion-email-templates-db-id` - Email templates database ID
- `resend-api-key` - Resend API key
- `testing-mode` - "true" or "false" for timing control

---

## Testing Mode

### Production vs Testing Timing

**Production Mode** (`TESTING_MODE=false`):
- Lead Nurture: Day 0, 2, 4, 6, 8
- 5-Day Sequence: Day 0, 2, 4, 6, 8
- No-Show: 5 min, 24hr, 48hr
- Post-Call: 1hr, Day 3, Day 7
- Onboarding: 1hr, Day 1, Day 3

**Testing Mode** (`TESTING_MODE=true`):
- Lead Nurture: 0min, 1min, 2min, 3min, 4min
- 5-Day Sequence: 0min, 1min, 2min, 3min, 4min
- No-Show: 1min, 2min, 3min
- Post-Call: 1min, 2min, 3min
- Onboarding: 1min, 2min, 3min

**To Enable Testing Mode**:
```bash
PREFECT_API_URL=https://prefect.galatek.dev/api python3 -c "
from prefect.blocks.system import Secret
Secret(value='true').save('testing-mode', overwrite=True)
"
```

**To Disable Testing Mode (Production)**:
```bash
PREFECT_API_URL=https://prefect.galatek.dev/api python3 -c "
from prefect.blocks.system import Secret
Secret(value='false').save('testing-mode', overwrite=True)
"
```

---

## Monitoring & Observability

### Prefect Dashboard

**URL**: https://prefect.galatek.dev

**Key Metrics**:
- Flow run status (success/failure)
- Email send counts
- Sequence completion rates
- Error logs

### Resend Dashboard

**Email Delivery Tracking**:
- Sent count
- Delivered rate
- Bounce rate
- Open rate (if tracking enabled)

### Notion Database Queries

**Contacts Database**:
- Total signups
- Assessment completion rate
- Segment distribution (CRITICAL/URGENT/OPTIMIZE)

**Email Sequence Tracker**:
- Scheduled emails per contact
- Email send status
- Sequence progress

---

## Error Handling

### Retry Logic

**Notion API**: 3 retries, 60s delay
**Resend API**: 3 retries, 30s delay
**Prefect Tasks**: Automatic retry with exponential backoff

### Failure Modes

| Failure | Behavior | Recovery |
|---------|----------|----------|
| Notion API down | Flow fails, logs error, retries | Manual re-run after API recovery |
| Resend API down | Email skipped, logged | Manual re-send after API recovery |
| Template not found | Uses fallback static template | Update Notion template DB |
| Contact not found | Creates new contact record | No action needed (auto-recovery) |
| Invalid email | Flow logs error, continues | Fix email address, re-trigger |

---

## Related Documentation

- **Template Variables**: `docs/TEMPLATE_VARIABLES.md`
- **Website Integration**: `WEBSITE_INTEGRATION.md`
- **Deployment Guide**: `STATUS.md`
- **Variable Testing**: `campaigns/christmas_campaign/tests/test_resend_operations.py`

---

## Maintenance Notes

**When Adding New Sequence**:
1. Create new flow file (e.g., `new_sequence_handler.py`)
2. Add templates to Notion Email Templates DB
3. Create Prefect deployment
4. Add webhook endpoint to `server.py`
5. Update this ARCHITECTURE.md
6. Test with TESTING_MODE=true

**When Modifying Timing**:
1. Update `TESTING_MODE` logic in flow
2. Document changes in this file
3. Test both production and testing modes

**When Adding New Template**:
1. Create template in Notion Email Templates DB
2. Add template ID to sequence flow
3. Update Complete Template Reference table above
4. Test variable substitution

---

**Questions?** Contact: sang@sanglescalinglabs.com

**Last Reviewed**: 2025-11-28
**Next Review**: 2026-01-01 (post-campaign analysis)
