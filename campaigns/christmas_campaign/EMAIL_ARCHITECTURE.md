# Christmas Campaign - Email Architecture & Sequence Documentation

**Last Updated**: 2025-11-28
**Author**: Christmas Campaign Team
**Status**: Production Ready

---

## Overview

The Christmas 2025 Campaign uses a multi-sequence email automation system built on:
- **Frontend**: Next.js website (sangletech.com)
- **Orchestration**: Prefect v3.4.1 (self-hosted at prefect.galatek.dev)
- **Database**: Notion (Templates, Contacts, Sequence Tracking)
- **Email Delivery**: Resend API

---

## Email Sequence Types (5 Active Sequences)

| # | Sequence Name | Templates | Trigger | Total Emails |
|---|---------------|-----------|---------|--------------|
| 1 | **5-Day Lead Nurture** | `5-Day E1` - `5-Day E5` | Assessment completion | 5 |
| 2 | **Lead Nurture** | `lead_nurture_email_1-5` | Initial opt-in | 5 |
| 3 | **No-Show Recovery** | `noshow_recovery_email_1-3` | Missed Calendly call | 3 |
| 4 | **Post-Call Maybe** | `postcall_maybe_email_1-3` | "Need to think" calls | 3 |
| 5 | **Onboarding Phase 1** | `onboarding_phase1_email_1-3` | Payment/DocuSign | 3 |

**Total Active Templates**: 21

---

## Sequence 1: 5-Day Lead Nurture (Primary)

### Funnel Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     CHRISTMAS 2025 LEAD NURTURE FUNNEL                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [Landing Page] ──> [Opt-in Form] ──> [Assessment] ──> [Results Page]      │
│       │                  │                │                 │               │
│       │                  ▼                ▼                 ▼               │
│       │           lead_nurture_1     5-Day E1          Calendly CTA        │
│       │           (confirmation)     (results)         (book call)         │
│       │                  │                │                 │               │
│       │                  │                │                 │               │
│  ┌────┼──────────────────┼────────────────┼─────────────────┼───────────┐  │
│  │    │     PREFECT      │                │                 │           │  │
│  │    │   ORCHESTRATION  │                │                 │           │  │
│  │    │                  ▼                ▼                 ▼           │  │
│  │    │     Day 1: lead_nurture_2    Day 1: 5-Day E2    CALL SCHEDULED │  │
│  │    │     Day 2: lead_nurture_3    Day 2: 5-Day E3         │          │  │
│  │    │     Day 3: lead_nurture_4    Day 3: 5-Day E4         │          │  │
│  │    │     Day 4: lead_nurture_5    Day 4: 5-Day E5         │          │  │
│  │    │                                                      │          │  │
│  └────┼──────────────────────────────────────────────────────┼──────────┘  │
│       │                                                      │             │
│       │                    ┌─────────────────────────────────┘             │
│       │                    │                                               │
│       │                    ▼                                               │
│       │         ┌──────────────────┐                                       │
│       │         │   CALL OUTCOME   │                                       │
│       │         └────────┬─────────┘                                       │
│       │                  │                                                 │
│       │      ┌───────────┼───────────┬───────────┐                        │
│       │      ▼           ▼           ▼           ▼                        │
│       │   NO-SHOW      MAYBE       CLOSE     ONBOARDING                   │
│       │      │           │           │           │                        │
│       │      ▼           ▼           ▼           ▼                        │
│       │   noshow_1   postcall_1   [DONE]    onboard_1                     │
│       │   noshow_2   postcall_2              onboard_2                     │
│       │   noshow_3   postcall_3              onboard_3                     │
│       │                                                                    │
└───────┴────────────────────────────────────────────────────────────────────┘
```

### 5-Day Email Sequence Details

| Day | Email | Template Name | Subject Theme | CTA Level |
|-----|-------|---------------|---------------|-----------|
| 0 | E1 | `5-Day E1: Your Assessment Results + Dec 5 Deadline (GIVE)` | Assessment Results | Info |
| 1 | E2 | `5-Day E2: The $500K Mistake + BusOS Framework (GIVE)` | $500K Mistake | Education |
| 2 | E3 | `5-Day E3: Van Tiny Case Study + Soft ASK` | Van Tiny Story | SOFT ASK |
| 3 | E4 | `5-Day E4: Value Stack + Medium ASK` | Value Stack | MEDIUM ASK |
| 4 | E5 | `5-Day E5: Final Call - HARD ASK (Last Email)` | Final Call | HARD ASK |

### Email Timing

**Production Mode** (TESTING_MODE=false):
- Email 1: Immediate (sent by website)
- Email 2: +24 hours (Day 1)
- Email 3: +72 hours (Day 3)
- Email 4: +96 hours (Day 4)
- Email 5: +120 hours (Day 5)

**Testing Mode** (TESTING_MODE=true):
- Email 1: Immediate
- Email 2: +1 minute
- Email 3: +2 minutes
- Email 4: +3 minutes
- Email 5: +4 minutes

### Segmentation Logic

Users are segmented based on assessment results for personalized Email 2 variants:

| Segment | Condition | Email 2 Variant |
|---------|-----------|-----------------|
| **CRITICAL** | 3+ RED systems OR score ≤40 | `lead_nurture_email_2a_critical` |
| **URGENT** | 1-2 RED OR 2+ ORANGE OR score 41-70 | `lead_nurture_email_2b_urgent` |
| **OPTIMIZE** | 0 RED, 0-1 ORANGE, score 71-100 | `lead_nurture_email_2c_optimize` |

---

## Template Variable Reference

### Required Variables (All Templates)

| Variable | Description | Example |
|----------|-------------|---------|
| `first_name` | Contact first name | "Sarah" |
| `business_name` | Business name | "Sarah's Salon" |
| `calendly_link` | Booking link | "https://cal.com/sangletech/discovery-call" |

### Assessment Variables (5-Day E1)

| Variable | Description | Example |
|----------|-------------|---------|
| `overall_score` | BusOS score (0-100) | "55" |
| `strongest_system` | Best performing system | "GPS" |
| `weakest_system_1` | Worst performing system | "FUEL" |
| `weakest_system_2` | Second worst system | "CREW" |
| `WeakestSystem1` | CamelCase alias | "FUEL" |
| `WeakestSystem2` | CamelCase alias | "CREW" |
| `readiness_zone` | Zone classification | "Orange (Warning)" |
| `TotalRevenueLeak_K` | Revenue leak in $K | "15" |
| `days_to_deadline` | Days to Dec 5 deadline | "7" |
| `deadline_date` | Deadline date string | "December 5, 2025" |
| `personalized_tip_1` | Custom tip #1 | "Track where your clients come from" |
| `personalized_tip_2` | Custom tip #2 | "Write down 3 tasks to delegate" |
| `personalized_tip_3` | Custom tip #3 | "Block 2 hours this weekend" |

### New Variables (E3-E5)

| Variable | Description | Default |
|----------|-------------|---------|
| `pdf_download_link` | Assessment Results Page (stores user's results) | "https://sangletech.com/en/flows/businessX/dfu/xmas-a01/assessment" |
| `spots_remaining` | Dynamic spot counter | "12" |
| `bookings_count` | Bookings this week | "18" |
| `weakest_system` | Alias for weakest_system_1 | Same as weakest_system_1 |

> **Note**: Instead of generating per-user PDFs, we link to the assessment results page which already stores and displays user-specific results with beautiful BusinessX styling.

---

## Sequence 3: No-Show Recovery

**Trigger**: Calendly webhook when invitee doesn't attend scheduled call

**Deployment**: `christmas-noshow-recovery-handler`

| Email | Template | Timing | Subject Theme |
|-------|----------|--------|---------------|
| 1 | `noshow_recovery_email_1` | +5 minutes | "Did something come up?" |
| 2 | `noshow_recovery_email_2` | +24 hours | "Let's reschedule" |
| 3 | `noshow_recovery_email_3` | +48 hours | "Last chance to book" |

---

## Sequence 4: Post-Call Maybe

**Trigger**: CRM status change to "Maybe" after discovery call

**Deployment**: `christmas-postcall-maybe-handler`

| Email | Template | Timing | Subject Theme |
|-------|----------|--------|---------------|
| 1 | `postcall_maybe_email_1` | +1 hour | "Thanks for the call" |
| 2 | `postcall_maybe_email_2` | +3 days | "Quick question" |
| 3 | `postcall_maybe_email_3` | +7 days | "Final follow-up" |

---

## Sequence 5: Onboarding Phase 1

**Trigger**: Payment received or DocuSign completed

**Deployment**: `christmas-onboarding-handler`

| Email | Template | Timing | Subject Theme |
|-------|----------|--------|---------------|
| 1 | `onboarding_phase1_email_1` | +1 hour | "Welcome aboard!" |
| 2 | `onboarding_phase1_email_2` | +1 day | "Your first steps" |
| 3 | `onboarding_phase1_email_3` | +3 days | "Week 1 checklist" |

---

## Prefect Deployments

| Deployment Name | Flow | Webhook Endpoint |
|-----------------|------|------------------|
| `christmas-signup-handler` | `signup_handler_flow` | POST `/webhook/christmas-signup` |
| `christmas-send-email` | `send_email_flow` | N/A (scheduled internally) |
| `christmas-noshow-recovery-handler` | `noshow_recovery_handler_flow` | POST `/webhook/calendly-noshow` |
| `christmas-postcall-maybe-handler` | `postcall_maybe_handler_flow` | POST `/webhook/postcall-maybe` |
| `christmas-onboarding-handler` | `onboarding_handler_flow` | POST `/webhook/onboarding-start` |

### Deployment IDs (Production)

```
christmas-signup-handler:        1ae3a3b3-e076-49c5-9b08-9c176aa47aa0
christmas-noshow-recovery-handler: 3400e152-1cbe-4d8f-9f8a-0dd73569afa1
christmas-postcall-maybe-handler:  ed929cd9-34b3-4655-b128-1a1e08a59cbd
christmas-onboarding-handler:      db47b919-1e55-4de2-b52c-6e2b0b2a2285
```

### Deployment Naming Convention

**Format**: `{campaign}-{flow-type}-{variant}`

**Rationale**:
- **Campaign prefix** (`christmas`) prevents name collisions with other campaigns
- **Flow type** (`signup`, `noshow-recovery`, `postcall-maybe`, `onboarding`) describes purpose
- **Variant** (`handler`, `send-email`) indicates specific implementation

**Multi-Campaign Strategy**:
- Future campaigns use different prefixes: `businessx-signup-handler`, `summer2026-signup-handler`
- Annual campaigns add year suffix: `christmas2025-signup-handler`, `christmas2026-signup-handler`
- A/B testing adds descriptive suffix: `christmas-signup-handler-fast`, `christmas-signup-handler-v2`

**Implementation Rules**:
1. Flow `name` parameter must match deployment name
2. Deployment name format: `{flow_name}/{deployment_name}`
3. Use lowercase with hyphens (no underscores, no camelCase)
4. Check for collisions before deploying

**References**:
- Full convention: `campaigns/christmas_campaign/docs/DEPLOYMENT_NAMING_CONVENTION.md`
- Migration guide: N/A (current naming is correct)

---

## Website Integration

### Architecture (Website-First)

1. **Website sends Email 1** immediately after assessment completion
2. **Website marks "Email 1 Sent"** in Notion Email Sequence DB
3. **Website triggers Prefect** deployment for Emails 2-5
4. **Prefect schedules** Emails 2-5 with appropriate delays

### API Endpoint

```typescript
// POST /api/assessment/complete.page.ts

// 1. Send Email 1 via Resend
const emailResult = await sendEmail1AndMarkSent(email, variables);

// 2. Trigger Prefect for Emails 2-5
const prefectResult = await triggerPrefectDeployment(
  email, firstName, businessName, scores,
  systemCounts, overallScore, strongestSystem,
  weakestSystem1, weakestSystem2, totalRevenueLeak,
  emailSegment  // CRITICAL/URGENT/OPTIMIZE
);
```

---

## Notion Databases

### Email Templates DB
- **ID**: `2ab7c374-1115-8115-932c-ca6789c5b87b`
- **Properties**: Template Name, Subject Line, Email Body HTML, Email Body Plain Text, Status

### Email Sequence DB
- **ID**: `576de1aa-6064-4201-a5e6-623b7f2be79a`
- **Properties**: Email, First Name, Business Name, Campaign, Segment, Email 1-5 Sent dates

### BusinessX Canada DB
- **ID**: (stored in Secret block `notion-db-id`)
- **Properties**: Email, Name, Assessment Score, Segment, System scores

---

## Testing

### Mandatory Test Email
```
lengobaosang@gmail.com
```

### Test Commands

```bash
# Send all 5-Day emails (E1-E5)
PREFECT_API_URL=https://prefect.galatek.dev/api python3 << 'EOF'
# ... test script ...
EOF

# Trigger signup flow
curl -X POST https://prefect.galatek.dev/api/deployments/1ae3a3b3-e076-49c5-9b08-9c176aa47aa0/create_flow_run \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test-signup",
    "parameters": {
      "email": "lengobaosang@gmail.com",
      "first_name": "Test",
      "business_name": "Test Business",
      "assessment_score": 55,
      "red_systems": 2,
      "orange_systems": 1
    }
  }'
```

---

## Key Files

| File | Purpose |
|------|---------|
| `campaigns/christmas_campaign/flows/signup_handler.py` | Main signup flow, schedules Emails 2-5 |
| `campaigns/christmas_campaign/flows/send_email_flow.py` | Sends individual emails |
| `campaigns/christmas_campaign/tasks/resend_operations.py` | Resend API + variable substitution |
| `campaigns/christmas_campaign/tasks/notion_operations.py` | Notion database operations |
| `sangletech-tailwindcss/lib/resend-notion.ts` | Website email functions |
| `sangletech-tailwindcss/pages/api/assessment/complete.page.ts` | Website API endpoint |

---

## Design Decisions

### Why Website-First Architecture?
- **Immediate delivery**: Email 1 sent instantly without Prefect latency
- **Better UX**: User sees results page and gets email simultaneously
- **Fault tolerance**: If Prefect is down, Email 1 still sends

### Why Notion for Templates?
- **Non-technical editing**: Marketing team can update emails without code
- **Version history**: Notion tracks all template changes
- **Rich formatting**: HTML templates with beautiful Alex Hormozi-style design

### Why 5-Day Sequence?
- **Optimal timing**: Research shows 5 touchpoints over 5 days maximizes conversion
- **Christmas deadline**: Aligned with December 5 deadline messaging
- **Balanced urgency**: Progressive CTA escalation (Info → Education → Soft → Medium → Hard)

---

## Troubleshooting

### Emails Not Sending

1. Check Resend API key: `Secret.load("resend-api-key").get()`
2. Verify template exists in Notion
3. Check Prefect flow run logs for errors
4. Confirm variables are being substituted correctly

### Template Variables Not Replaced

1. Check variable naming (snake_case vs CamelCase)
2. Verify variable is in `get_email_variables()` function
3. Check template uses `{{variable}}` syntax

### Prefect Deployment Not Found

1. Confirm deployment exists: `prefect deployment ls`
2. Check deployment ID matches in code
3. Verify git push completed before flow run

---

**Last Verified**: 2025-11-28 (All 5 templates sent successfully)
