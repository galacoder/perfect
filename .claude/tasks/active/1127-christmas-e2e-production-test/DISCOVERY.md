# Discovery: Christmas Campaign E2E Production Test

**Task ID**: 1127-christmas-e2e-production-test
**Domain**: CODING (E2E Testing)
**Date**: 2025-11-27

---

## 1. Production Funnel Analysis

### URL Structure
- **Production URL**: https://sangletech.com/en/flows/businessX/dfu/xmas-a01
- **Prefect API**: https://prefect.galatek.dev/api

### Form Fields Discovered (Phase 1/3)

| Field | ID | Type | Required | Options/Placeholder |
|-------|-----|------|----------|---------------------|
| Full Name | `firstName` | text | Yes | "Jane Smith" |
| Email | `email` | email | Yes | "jane@salon.com" |
| Monthly Revenue | `monthlyRevenue` | select | Yes | under-5k, 5k-10k, 10k-20k, 20k-50k, 50k-100k, over-100k |
| Biggest Challenge | `biggestChallenge` | select | Yes | no-shows, pricing, retention, staffing, marketing, scaling, systems, time |
| Privacy | `privacy` | checkbox | Yes | Email consent |
| Submit | - | submit | - | "Get My Free Assessment" |

### Form Flow
1. User fills form on landing page
2. Submits to start 8-minute assessment
3. Assessment completion triggers webhook to Prefect
4. Prefect schedules 7-email nurture sequence

---

## 2. Webhook Endpoints Analysis

### Primary Webhooks (Christmas Campaign)

| Endpoint | Flow | Deployment ID | Emails | Timing (Test Mode) |
|----------|------|---------------|--------|-------------------|
| `POST /webhook/christmas-signup` | `signup_handler_flow` | `1ae3a3b3-e076-49c5-9b08-9c176aa47aa0` | 7 | 0, 1, 2, 3, 4, 5, 6 min |
| `POST /webhook/calendly-noshow` | `noshow_recovery_handler_flow` | TBD | 3 | 1, 2, 3 min |
| `POST /webhook/postcall-maybe` | `postcall_maybe_handler_flow` | TBD | 3 | 1, 2, 3 min |
| `POST /webhook/onboarding-start` | `onboarding_handler_flow` | TBD | 3 | 1, 2, 3 min |

### Christmas Signup Webhook Payload

```json
{
  "email": "lengobaosang@gmail.com",
  "first_name": "E2E Test",
  "business_name": "Test Salon E2E",
  "assessment_score": 52,
  "red_systems": 2,
  "orange_systems": 1,
  "yellow_systems": 2,
  "green_systems": 3,
  "gps_score": 45,
  "money_score": 38,
  "weakest_system_1": "GPS",
  "weakest_system_2": "Money",
  "revenue_leak_total": 14700
}
```

### No-Show Webhook Payload

```json
{
  "email": "lengobaosang@gmail.com",
  "first_name": "E2E Test",
  "business_name": "Test Salon E2E",
  "calendly_event_uri": "https://calendly.com/events/E2E-TEST-123",
  "scheduled_time": "2025-11-27T14:00:00Z",
  "event_type": "Discovery Call - $2997 Diagnostic",
  "reschedule_url": "https://calendly.com/reschedule/E2E-TEST-123"
}
```

### Post-Call Maybe Webhook Payload

```json
{
  "email": "lengobaosang@gmail.com",
  "first_name": "E2E Test",
  "business_name": "Test Salon E2E",
  "call_date": "2025-11-27T14:30:00Z",
  "call_outcome": "Maybe",
  "call_notes": "E2E Test - Interested but needs budget approval",
  "objections": ["Price", "Timing"],
  "follow_up_priority": "High"
}
```

### Onboarding Webhook Payload

```json
{
  "email": "lengobaosang@gmail.com",
  "first_name": "E2E Test",
  "business_name": "Test Salon E2E",
  "payment_confirmed": true,
  "payment_amount": 2997.00,
  "payment_date": "2025-11-27T15:00:00Z",
  "docusign_completed": true,
  "salon_address": "123 Test St, Toronto, ON",
  "observation_dates": ["2025-12-10", "2025-12-17"],
  "start_date": "2025-12-10",
  "package_type": "Phase 1 - Traditional Service Diagnostic"
}
```

---

## 3. Flow Architecture

### Christmas Signup Flow (7 emails)

```
Website Form Submission
        |
        v
POST /webhook/christmas-signup
        |
        v
signup_handler_flow
    |-- Check idempotency (existing sequence?)
    |-- Classify segment (CRITICAL/URGENT/OPTIMIZE)
    |-- Create/update BusinessX Canada contact
    |-- Create Email Sequence record in Notion
    |-- Schedule 7 emails via Prefect Deployment
        |
        v
christmas-send-email (Deployment ID: 5445a75a-ae20-4d65-8120-7237e68ae0d5)
    |-- Email 1: Immediate (christmas_email_1)
    |-- Email 2: +1 min (christmas_email_2_{segment})
    |-- Email 3: +2 min (christmas_email_3)
    |-- Email 4: +3 min (christmas_email_4)
    |-- Email 5: +4 min (christmas_email_5)
    |-- Email 6: +5 min (christmas_email_6)
    |-- Email 7: +6 min (christmas_email_7_{segment})
```

### TESTING_MODE Timing

| Email | Test Mode | Production Mode |
|-------|-----------|-----------------|
| Email 1 | 0 min (immediate) | Day 0 |
| Email 2 | +1 min | +24h (Day 1) |
| Email 3 | +2 min | +72h (Day 3) |
| Email 4 | +3 min | +120h (Day 5) |
| Email 5 | +4 min | +168h (Day 7) |
| Email 6 | +5 min | +216h (Day 9) |
| Email 7 | +6 min | +264h (Day 11) |

---

## 4. Key Files Analyzed

### Flow Files
- `/campaigns/christmas_campaign/flows/signup_handler.py` - Main signup flow
- `/campaigns/christmas_campaign/flows/send_email_flow.py` - Email sending flow
- `/campaigns/christmas_campaign/flows/noshow_recovery_handler.py` - No-show recovery
- `/campaigns/christmas_campaign/flows/postcall_maybe_handler.py` - Post-call follow-up
- `/campaigns/christmas_campaign/flows/onboarding_handler.py` - Client onboarding

### Server File
- `/server.py` - FastAPI webhook server with all endpoints

### Documentation
- `/campaigns/christmas_campaign/STATUS.md` - Production deployment status
- `/campaigns/christmas_campaign/WEBSITE_INTEGRATION.md` - API integration guide

---

## 5. Testing Requirements

### Mandatory Test Email
```
lengobaosang@gmail.com
```
**CRITICAL**: All E2E tests MUST use this email address.

### Secret Blocks (Production Prefect)

| Block Name | Purpose |
|------------|---------|
| `notion-token` | Notion API authentication |
| `notion-email-templates-db-id` | Email templates database |
| `notion-email-sequence-db-id` | Sequence tracking database |
| `notion-businessx-db-id` | BusinessX contacts database |
| `resend-api-key` | Email sending via Resend |
| `testing-mode` | Enable fast email timing |

---

## 6. Known Issues & Risks

### Python 3.12 asyncio Issue
- **Issue**: Email 1 sometimes crashes due to asyncio event loop handling
- **Success Rate**: 85.71% (6/7 emails)
- **Workaround**: Flow handles gracefully with error logging

### Template Source
- **Change**: Fallback templates removed (Nov 27, 2025)
- **Current**: Templates MUST exist in Notion database
- **Risk**: Missing template = flow failure with clear error

### Idempotency
- **Protection**: Flow checks for existing sequences before creating
- **Safe**: Duplicate webhooks won't create duplicate email sequences

---

## 7. Verification Checkpoints

### Post-Webhook Verification
1. Flow run appears in Prefect dashboard
2. Email sequence record created in Notion
3. Contact record created/updated in BusinessX Canada
4. 7 scheduled flow runs visible in Prefect
5. Emails delivered to test inbox

### Email Verification
1. Subject line matches template
2. HTML content renders correctly
3. Personalization tokens replaced
4. Links work correctly
5. Timing matches expected schedule

---

## 8. Dependencies

### External Services
- **Prefect Server**: https://prefect.galatek.dev
- **Notion API**: Database operations
- **Resend API**: Email delivery
- **Website**: https://sangletech.com

### Worker Status
- **Work Pool**: `default`
- **Workers**: Active (worker1)
- **Pull Method**: Git clone from GitHub

---

**Discovery Complete**: Ready for PLAN phase
