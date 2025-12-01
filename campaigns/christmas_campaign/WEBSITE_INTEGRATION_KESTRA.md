# Christmas Campaign - Website Integration Guide (Kestra)

**Last Updated**: 2025-11-30
**Status**: Ready for Website Integration (Kestra Migration Complete)
**Migration**: Migrated from Prefect to Kestra (November 2025)

---

## Overview

The Christmas Campaign uses **Kestra self-hosted automation** with **5 webhook endpoints** for website integration.

**CRITICAL CHANGE**: Email #1 of the 5-day sequence is now **sent by the website**, not Kestra!

---

## Email Sending Responsibilities

| Sequence | Email # | Who Sends? | When? | What Website Must Do |
|----------|---------|------------|-------|----------------------|
| **Signup** | - | **Website** | On form submit | Send signup confirmation email |
| **5-Day Assessment** | #1 | **Website** | Immediately after assessment | Send Email #1, record timestamp, include in webhook |
| **5-Day Assessment** | #2-5 | **Kestra** | 24h, 72h, 96h, 120h after Email #1 | Provide `email_1_sent_at` in webhook |
| **No-Show Recovery** | All 3 | **Kestra** | 5min, 24h, 48h | Trigger webhook, Kestra handles all emails |
| **Post-Call Maybe** | All 3 | **Kestra** | 1h, 3d, 7d | Trigger webhook, Kestra handles all emails |
| **Onboarding** | All 3 | **Kestra** | 1h, 1d, 3d | Trigger webhook, Kestra handles all emails |

---

## Production Webhook Endpoints

### Base URL

**Local Development**:
```
http://localhost:8080/api/v1/executions/webhook/christmas/handlers/{handler-name}/{webhook-key}
```

**Production** (adjust domain as needed):
```
https://kestra.galatek.dev/api/v1/executions/webhook/christmas/handlers/{handler-name}/{webhook-key}
```

---

## Endpoint 1: Signup Handler (TRACKING ONLY - NO EMAILS)

### When to Call

✅ **Call this endpoint when**:
- User completes signup form
- You want to track signup in Notion
- Website will send signup confirmation email directly

**CRITICAL**: This handler does **NOT send any emails**. Website handles all signup emails.

### Endpoint Details

**Local URL**:
```
http://localhost:8080/api/v1/executions/webhook/christmas/handlers/signup-handler/signup-webhook-key
```

**Method**: `POST`

**Headers**:
```json
{
  "Content-Type": "application/json"
}
```

**Request Body**:
```json
{
  "email": "customer@example.com",
  "first_name": "Sarah",
  "business_name": "Sarah's Salon"
}
```

### Required Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `email` | string | ✅ Yes | Customer email address | `"sarah@example.com"` |
| `first_name` | string | ✅ Yes | Customer first name | `"Sarah"` |
| `business_name` | string | ✅ Yes | Business name | `"Sarah's Salon"` |

### JavaScript Example

```javascript
async function handleSignup(formData) {
  // 1. Send signup email from website (synchronous)
  await sendEmail({
    template: "signup_confirmation",
    to: formData.email,
    variables: {
      first_name: formData.firstName,
      business_name: formData.businessName
    }
  });

  // 2. Track signup in Kestra (async, non-blocking)
  fetch('http://localhost:8080/api/v1/executions/webhook/christmas/handlers/signup-handler/signup-webhook-key', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email: formData.email,
      first_name: formData.firstName,
      business_name: formData.businessName
    })
  }).catch(err => {
    // Don't block user experience if tracking fails
    console.error('Failed to track signup:', err);
  });

  // 3. Show success message to user
  return { success: true, message: "Check your email for next steps!" };
}
```

### What Happens After You Call This?

1. **Immediately**:
   - Kestra creates/updates contact in Notion Contacts database
   - Logs signup event
   - **NO EMAILS SENT BY KESTRA**

2. **Website Responsibility**:
   - Send signup confirmation email
   - Show success message to user

---

## Endpoint 2: Assessment Handler (Emails #2-5 ONLY)

### When to Call

✅ **Call this endpoint when**:
- User completes BusOS assessment
- **AFTER website has sent Email #1** (assessment results)
- You want Kestra to schedule follow-up emails #2-5

**CRITICAL**: Website must send Email #1 BEFORE calling this webhook!

### Endpoint Details

**Local URL**:
```
http://localhost:8080/api/v1/executions/webhook/christmas/handlers/assessment-handler/assessment-webhook-key
```

**Method**: `POST`

**Headers**:
```json
{
  "Content-Type": "application/json"
}
```

**Request Body**:
```json
{
  "email": "customer@example.com",
  "first_name": "Sarah",
  "business_name": "Sarah's Salon",
  "red_systems": 2,
  "orange_systems": 1,
  "yellow_systems": 2,
  "green_systems": 3,
  "weakest_system_1": "GPS",
  "weakest_system_2": "Money",
  "revenue_leak_total": 14700,
  "email_1_sent_at": "2025-12-01T10:30:00Z",
  "email_1_status": "sent"
}
```

### Required Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `email` | string | ✅ Yes | Customer email address | `"sarah@example.com"` |
| `first_name` | string | ✅ Yes | Customer first name | `"Sarah"` |
| `business_name` | string | ✅ Yes | Business name | `"Sarah's Salon"` |
| `red_systems` | number | ✅ Yes | Number of broken systems (0-8) | `2` |
| `orange_systems` | number | ✅ Yes | Number of struggling systems (0-8) | `1` |
| `yellow_systems` | number | ✅ Yes | Number of functional systems (0-8) | `2` |
| `green_systems` | number | ✅ Yes | Number of optimized systems (0-8) | `3` |
| **`email_1_sent_at`** | **string** | ✅ **CRITICAL** | **ISO 8601 timestamp when Email #1 was sent** | `"2025-12-01T10:30:00Z"` |
| **`email_1_status`** | **string** | ✅ **CRITICAL** | **"sent" to confirm Email #1 delivered** | `"sent"` |

### Optional Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `weakest_system_1` | string | ⭕ Optional | Weakest system name | `"GPS"` |
| `weakest_system_2` | string | ⭕ Optional | Second weakest system | `"Money"` |
| `revenue_leak_total` | number | ⭕ Optional | Total revenue leak estimate | `14700` |

### JavaScript Example (Complete Assessment Flow)

```javascript
async function handleAssessmentCompletion(assessmentData) {
  try {
    // STEP 1: Send Email #1 from website (SYNCHRONOUS - user waits)
    const email1SentAt = new Date().toISOString();

    await sendEmail({
      template: "christmas_email_1",
      to: assessmentData.email,
      variables: {
        first_name: assessmentData.firstName,
        business_name: assessmentData.businessName,
        overall_score: assessmentData.overallScore,
        weakest_system_1: assessmentData.weakestSystem1,
        revenue_leak_total: assessmentData.revenueLeak,
        // ... other assessment variables
      }
    });

    console.log('✅ Email #1 sent at:', email1SentAt);

    // STEP 2: Trigger Kestra for Emails #2-5 (ASYNC - don't wait)
    fetch('http://localhost:8080/api/v1/executions/webhook/christmas/handlers/assessment-handler/assessment-webhook-key', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: assessmentData.email,
        first_name: assessmentData.firstName,
        business_name: assessmentData.businessName,
        red_systems: assessmentData.redCount,
        orange_systems: assessmentData.orangeCount,
        yellow_systems: assessmentData.yellowCount,
        green_systems: assessmentData.greenCount,
        weakest_system_1: assessmentData.weakestSystem1,
        weakest_system_2: assessmentData.weakestSystem2,
        revenue_leak_total: assessmentData.revenueLeak,
        email_1_sent_at: email1SentAt,        // ✅ CRITICAL!
        email_1_status: "sent"                 // ✅ CRITICAL!
      })
    }).catch(err => {
      // Log error but don't block user experience
      console.error('Failed to trigger Kestra follow-up sequence:', err);
      // Optional: Send to error tracking (Sentry, etc.)
    });

    // STEP 3: Show results to user
    return {
      success: true,
      message: "Check your email for your detailed results!",
      overallScore: assessmentData.overallScore,
      weakestSystem: assessmentData.weakestSystem1
    };

  } catch (error) {
    console.error('Assessment completion error:', error);
    throw error;
  }
}
```

### Next.js Server Action Example

```typescript
'use server';

import { z } from 'zod';
import { Resend } from 'resend';

const AssessmentSchema = z.object({
  email: z.string().email(),
  first_name: z.string().min(1),
  business_name: z.string().min(1),
  red_systems: z.number().int().min(0).max(8),
  orange_systems: z.number().int().min(0).max(8),
  yellow_systems: z.number().int().min(0).max(8),
  green_systems: z.number().int().min(0).max(8),
  weakest_system_1: z.string().optional(),
  weakest_system_2: z.string().optional(),
  revenue_leak_total: z.number().int().optional(),
});

export async function completeAssessment(formData: FormData) {
  // Validate input
  const data = AssessmentSchema.parse({
    email: formData.get('email'),
    first_name: formData.get('firstName'),
    business_name: formData.get('businessName'),
    red_systems: Number(formData.get('redSystems')),
    orange_systems: Number(formData.get('orangeSystems')),
    yellow_systems: Number(formData.get('yellowSystems')),
    green_systems: Number(formData.get('greenSystems')),
    weakest_system_1: formData.get('weakestSystem1') || undefined,
    weakest_system_2: formData.get('weakestSystem2') || undefined,
    revenue_leak_total: formData.get('revenueLeak') ? Number(formData.get('revenueLeak')) : undefined,
  });

  // STEP 1: Send Email #1 from website
  const resend = new Resend(process.env.RESEND_API_KEY);
  const email1SentAt = new Date().toISOString();

  const { id: resendId } = await resend.emails.send({
    from: 'BusinessX Canada <noreply@sangletech.com>',
    to: data.email,
    subject: 'Your BusOS Assessment Results',
    html: `<!-- Email #1 template -->`,
    // ... template variables
  });

  console.log('Email #1 sent:', resendId, 'at', email1SentAt);

  // STEP 2: Trigger Kestra for follow-up emails (async)
  const kestraUrl = process.env.KESTRA_WEBHOOK_URL || 'http://localhost:8080/api/v1/executions/webhook/christmas/handlers/assessment-handler/assessment-webhook-key';

  try {
    await fetch(kestraUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ...data,
        email_1_sent_at: email1SentAt,     // ✅ CRITICAL!
        email_1_status: 'sent'              // ✅ CRITICAL!
      })
    });
  } catch (error) {
    // Log but don't throw - user already got Email #1
    console.error('Kestra webhook failed:', error);
  }

  return {
    success: true,
    resendId,
    email1SentAt
  };
}
```

### What Happens After You Call This?

1. **Immediately**:
   - Kestra validates `email_1_sent_at` timestamp
   - Updates Notion Contacts database with assessment data
   - Classifies segment (CRITICAL/URGENT/OPTIMIZE)
   - Records Email #1 in Notion Sequence Tracker as `sent_by='website'`

2. **Scheduled Emails** (relative to `email_1_sent_at`):
   - **Email #2**: `email_1_sent_at + 24 hours` (production) or `+ 1 minute` (testing)
   - **Email #3**: `email_1_sent_at + 72 hours` (production) or `+ 2 minutes` (testing)
   - **Email #4**: `email_1_sent_at + 96 hours` (production) or `+ 3 minutes` (testing)
   - **Email #5**: `email_1_sent_at + 120 hours` (production) or `+ 4 minutes` (testing)

3. **Notion Updates**:
   - Each email updates Notion Sequence Tracker with delivery status
   - Contact database updated with `last_email_sent` timestamp

---

## Endpoint 3: No-Show Recovery Handler

### When to Call

✅ **Call this endpoint when**:
- Customer misses scheduled diagnostic call
- Calendly webhook fires `BOOKING_CANCELLED` or no-show detected
- You want to send 3-email recovery sequence

**Note**: Kestra sends ALL 3 emails for this sequence (no website involvement)

### Endpoint Details

**Local URL**:
```
http://localhost:8080/api/v1/executions/webhook/christmas/handlers/noshow-recovery-handler/noshow-webhook-key
```

**Method**: `POST`

**Request Body**:
```json
{
  "email": "customer@example.com",
  "first_name": "Sarah",
  "calendly_event_id": "evt_123abc",
  "scheduled_time": "2025-12-10T14:00:00Z"
}
```

### Required Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `email` | string | ✅ Yes | Customer email address |
| `first_name` | string | ✅ Yes | Customer first name |
| `calendly_event_id` | string | ✅ Yes | Calendly event ID |
| `scheduled_time` | string | ✅ Yes | ISO 8601 original call time |

### What Happens?

Kestra sends 3 recovery emails:
1. **Email 1**: 5 minutes after no-show
2. **Email 2**: 24 hours after no-show
3. **Email 3**: 48 hours after no-show

---

## Endpoint 4: Post-Call Maybe Handler

### When to Call

✅ **Call this endpoint when**:
- Sales call completed
- Customer said "I need to think about it"
- You want to send 3-email nurture sequence

**Note**: Kestra sends ALL 3 emails for this sequence

### Endpoint Details

**Local URL**:
```
http://localhost:8080/api/v1/executions/webhook/christmas/handlers/postcall-maybe-handler/postcall-webhook-key
```

**Method**: `POST`

**Request Body**:
```json
{
  "email": "customer@example.com",
  "first_name": "Sarah",
  "business_name": "Sarah's Salon",
  "call_date": "2025-12-08T15:00:00Z",
  "interest_level": "medium"
}
```

### What Happens?

Kestra sends 3 follow-up emails:
1. **Email 1**: 1 hour after call
2. **Email 2**: 3 days after call
3. **Email 3**: 7 days after call

---

## Endpoint 5: Onboarding Handler

### When to Call

✅ **Call this endpoint when**:
- Customer completes payment
- DocuSign contract signed
- You want to send 3-email onboarding sequence

**Note**: Kestra sends ALL 3 emails for this sequence

### Endpoint Details

**Local URL**:
```
http://localhost:8080/api/v1/executions/webhook/christmas/handlers/onboarding-handler/onboarding-webhook-key
```

**Method**: `POST`

**Request Body**:
```json
{
  "email": "customer@example.com",
  "first_name": "Sarah",
  "business_name": "Sarah's Salon",
  "payment_status": "paid",
  "payment_date": "2025-12-09T16:30:00Z",
  "package_type": "foundation"
}
```

### What Happens?

Kestra sends 3 onboarding emails:
1. **Email 1**: 1 hour after payment
2. **Email 2**: 1 day after payment
3. **Email 3**: 3 days after payment

---

## Environment Variables for Website

Your website needs these environment variables:

```bash
# Kestra Configuration (Local)
KESTRA_BASE_URL=http://localhost:8080
KESTRA_WEBHOOK_SIGNUP=http://localhost:8080/api/v1/executions/webhook/christmas/handlers/signup-handler/signup-webhook-key
KESTRA_WEBHOOK_ASSESSMENT=http://localhost:8080/api/v1/executions/webhook/christmas/handlers/assessment-handler/assessment-webhook-key
KESTRA_WEBHOOK_NOSHOW=http://localhost:8080/api/v1/executions/webhook/christmas/handlers/noshow-recovery-handler/noshow-webhook-key
KESTRA_WEBHOOK_POSTCALL=http://localhost:8080/api/v1/executions/webhook/christmas/handlers/postcall-maybe-handler/postcall-webhook-key
KESTRA_WEBHOOK_ONBOARDING=http://localhost:8080/api/v1/executions/webhook/christmas/handlers/onboarding-handler/onboarding-webhook-key

# Resend Configuration (for Email #1)
RESEND_API_KEY=re_xxxxx
```

**Production** (adjust domain):
```bash
KESTRA_BASE_URL=https://kestra.galatek.dev
KESTRA_WEBHOOK_SIGNUP=https://kestra.galatek.dev/api/v1/executions/webhook/christmas/handlers/signup-handler/signup-webhook-key
# ... (same pattern for other webhooks)
```

---

## Testing the Integration

### Test 1: Local Kestra Running

```bash
# Start Kestra
docker-compose -f docker-compose.kestra.yml up -d

# Check Kestra UI
open http://localhost:8080

# Verify flows deployed
curl http://localhost:8080/api/v1/flows
```

### Test 2: Signup Handler (No Emails)

```bash
curl -X POST http://localhost:8080/api/v1/executions/webhook/christmas/handlers/signup-handler/signup-webhook-key \
  -H "Content-Type: application/json" \
  -d '{
    "email": "lengobaosang@gmail.com",
    "first_name": "Test",
    "business_name": "Test Business"
  }'
```

**Expected**:
- Kestra execution starts
- Contact created/updated in Notion
- **NO EMAILS SENT**

### Test 3: Assessment Handler (Emails #2-5)

**Pre-requisite**: Website must send Email #1 first

```bash
# Simulate: Website sends Email #1
EMAIL_1_SENT_AT=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Trigger Kestra for Emails #2-5
curl -X POST http://localhost:8080/api/v1/executions/webhook/christmas/handlers/assessment-handler/assessment-webhook-key \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"lengobaosang@gmail.com\",
    \"first_name\": \"Test\",
    \"business_name\": \"Test Business\",
    \"red_systems\": 2,
    \"orange_systems\": 1,
    \"yellow_systems\": 2,
    \"green_systems\": 3,
    \"weakest_system_1\": \"GPS\",
    \"revenue_leak_total\": 14700,
    \"email_1_sent_at\": \"$EMAIL_1_SENT_AT\",
    \"email_1_status\": \"sent\"
  }"
```

**Expected** (TESTING_MODE=true):
- Email #2 scheduled for +1 minute
- Email #3 scheduled for +2 minutes
- Email #4 scheduled for +3 minutes
- Email #5 scheduled for +4 minutes
- Notion shows Email #1 as `sent_by='website'`
- Notion shows Emails #2-5 as `sent_by='kestra'`

---

## Error Handling

### Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| 404 Not Found | Wrong webhook URL or flow not deployed | Verify URL matches flow definition |
| 400 Bad Request | Missing required fields | Check all required parameters sent |
| 500 Internal Server Error | Kestra flow error | Check Kestra execution logs |

### Recommended Error Handling

```javascript
async function triggerKestra(endpoint, payload) {
  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      console.error('Kestra webhook failed:', response.status);
      // Optional: Send to error tracking
      // Don't throw - user experience shouldn't be blocked
      return { success: false, warning: 'Automation may be delayed' };
    }

    return { success: true };
  } catch (error) {
    console.error('Network error:', error);
    return { success: false, warning: 'Automation may be delayed' };
  }
}
```

**Important**: Kestra webhook failures should NOT block user experience!

---

## Monitoring & Debugging

### Check Flow Execution Status

**Kestra UI**:
```
http://localhost:8080/ui/executions
```

**Kestra API**:
```bash
# List recent executions
curl http://localhost:8080/api/v1/executions

# Get execution logs
curl http://localhost:8080/api/v1/executions/{execution-id}/logs
```

### Check Notion Databases

1. **Contacts Database**: Shows contact details, assessment data
2. **Sequence Tracker Database**: Shows email delivery status per email
3. **Email Templates Database**: Stores email content

---

## FAQ

### Q: What if I forget to include email_1_sent_at?

**A**: Kestra will:
1. Log a **WARNING**
2. Use webhook trigger time as fallback
3. Continue execution (doesn't fail)

But emails will be slightly delayed, so always include it!

### Q: Can I test without sending real emails?

**A**: Use `TESTING_MODE=true` in Kestra `.env.kestra` file:
- Fast timing (minutes instead of days)
- Still sends real emails (use test email addresses)

### Q: What if customer completes assessment twice?

**A**: Kestra handles idempotency:
- Updates existing Notion contact record
- Won't create duplicate sequence
- Latest assessment data overwrites previous

### Q: How do I switch from testing to production timing?

**A**: Update `.env.kestra`:
```bash
# Change from:
SECRET_TESTING_MODE=true

# To:
SECRET_TESTING_MODE=false
```

Then restart Kestra:
```bash
docker-compose -f docker-compose.kestra.yml restart
```

---

## Summary Checklist

### For Website Developer

- [ ] Add Kestra webhook URLs to environment variables
- [ ] Implement Email #1 sending from website (Resend API)
- [ ] Record `email_1_sent_at` timestamp when Email #1 sent
- [ ] Include `email_1_sent_at` and `email_1_status` in webhook payload
- [ ] Add error handling (don't block user on webhook failure)
- [ ] Test with local Kestra (docker-compose)
- [ ] Verify Email #1 arrives from website
- [ ] Verify Emails #2-5 scheduled by Kestra
- [ ] Test TESTING_MODE timing
- [ ] Monitor first 10 real assessments

### For Testing

- [ ] Start Kestra locally (`docker-compose up`)
- [ ] Test signup webhook (verify NO emails sent)
- [ ] Test assessment webhook (verify only Emails #2-5 scheduled)
- [ ] Verify `email_1_sent_at` used for delay calculations
- [ ] Check Notion Sequence Tracker shows Email #1 as 'sent_by_website'
- [ ] Test different segments (CRITICAL/URGENT/OPTIMIZE)
- [ ] Test all secondary handlers (noshow, postcall, onboarding)
- [ ] Verify email delivery in Resend dashboard

### For Production Launch

- [ ] Deploy Kestra to production server
- [ ] Update webhook URLs to production domain
- [ ] Switch `TESTING_MODE=false`
- [ ] Monitor Kestra execution dashboard
- [ ] Check Notion databases for delivery tracking
- [ ] Review email delivery rates
- [ ] Collect customer feedback

---

**Questions?** See `KESTRA_MIGRATION.md` for migration details or `ARCHITECTURE.md` for system architecture.

**Kestra UI**: http://localhost:8080 (local) or https://kestra.galatek.dev (production)

**Last Updated**: 2025-11-30
**Migration Status**: Complete (Prefect → Kestra)
