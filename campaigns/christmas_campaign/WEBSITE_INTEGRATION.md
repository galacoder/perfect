# Christmas Campaign - Website Integration Guide

**Last Updated**: 2025-11-19
**Status**: Ready for Website Integration

---

## Overview

The Christmas Campaign has **2 production-ready webhook endpoints** that your website needs to call:

1. **`POST /webhook/christmas-signup`** - Main signup endpoint (triggers 7-email sequence)
2. **`POST /webhook/calcom-booking`** - Diagnostic call booking handler (triggers 3-email pre-call prep)

---

## Production Endpoints

### Base URL

```
https://prefect.galatek.dev/api
```

**Important**: These are NOT FastAPI endpoints - they're **Prefect deployment triggers** that create flow runs.

---

## Endpoint 1: Christmas Signup (PRIMARY)

### When to Call

✅ **Call this endpoint when**:
- Customer completes BusOS assessment
- Customer agrees to receive Christmas campaign emails
- You have their email, name, business name, and assessment scores

### Endpoint Details

**URL**: `https://prefect.galatek.dev/api/deployments/1ae3a3b3-e076-49c5-9b08-9c176aa47aa0/create_flow_run`

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
  "name": "christmas-signup-{timestamp}",
  "parameters": {
    "email": "customer@example.com",
    "first_name": "Sarah",
    "business_name": "Sarah's Salon",
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
}
```

### Required Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `email` | string | ✅ Yes | Customer email address | `"sarah@example.com"` |
| `first_name` | string | ✅ Yes | Customer first name | `"Sarah"` |
| `business_name` | string | ✅ Yes | Business name | `"Sarah's Salon"` |
| `assessment_score` | number | ✅ Yes | Overall BusOS score (0-100) | `52` |
| `red_systems` | number | ✅ Yes | Number of broken systems (0-8) | `2` |
| `orange_systems` | number | ✅ Yes | Number of struggling systems (0-8) | `1` |
| `yellow_systems` | number | ✅ Yes | Number of functional systems (0-8) | `2` |
| `green_systems` | number | ✅ Yes | Number of optimized systems (0-8) | `3` |

### Optional Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `gps_score` | number | ⭕ Optional | GPS system score (0-100) | `45` |
| `money_score` | number | ⭕ Optional | Money system score (0-100) | `38` |
| `weakest_system_1` | string | ⭕ Optional | Weakest system name | `"GPS"` |
| `weakest_system_2` | string | ⭕ Optional | Second weakest system | `"Money"` |
| `revenue_leak_total` | number | ⭕ Optional | Total revenue leak estimate | `14700` |

### JavaScript Example (Fetch API)

```javascript
async function triggerChristmasSequence(assessmentData) {
  const response = await fetch(
    'https://prefect.galatek.dev/api/deployments/1ae3a3b3-e076-49c5-9b08-9c176aa47aa0/create_flow_run',
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name: `christmas-signup-${Date.now()}`,
        parameters: {
          email: assessmentData.email,
          first_name: assessmentData.firstName,
          business_name: assessmentData.businessName,
          assessment_score: assessmentData.overallScore,
          red_systems: assessmentData.redCount,
          orange_systems: assessmentData.orangeCount,
          yellow_systems: assessmentData.yellowCount,
          green_systems: assessmentData.greenCount,
          gps_score: assessmentData.gpsScore,
          money_score: assessmentData.moneyScore,
          weakest_system_1: assessmentData.weakestSystem1,
          weakest_system_2: assessmentData.weakestSystem2,
          revenue_leak_total: assessmentData.revenueLeak
        }
      })
    }
  );

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const result = await response.json();
  console.log('Christmas sequence started:', result.id);
  return result;
}
```

### TypeScript Example (with Axios)

```typescript
import axios from 'axios';

interface ChristmasSignupParams {
  email: string;
  first_name: string;
  business_name: string;
  assessment_score: number;
  red_systems: number;
  orange_systems: number;
  yellow_systems: number;
  green_systems: number;
  gps_score?: number;
  money_score?: number;
  weakest_system_1?: string;
  weakest_system_2?: string;
  revenue_leak_total?: number;
}

async function triggerChristmasSequence(params: ChristmasSignupParams) {
  const response = await axios.post(
    'https://prefect.galatek.dev/api/deployments/1ae3a3b3-e076-49c5-9b08-9c176aa47aa0/create_flow_run',
    {
      name: `christmas-signup-${Date.now()}`,
      parameters: params
    }
  );

  return response.data;
}

// Usage
const result = await triggerChristmasSequence({
  email: 'sarah@example.com',
  first_name: 'Sarah',
  business_name: "Sarah's Salon",
  assessment_score: 52,
  red_systems: 2,
  orange_systems: 1,
  yellow_systems: 2,
  green_systems: 3,
  gps_score: 45,
  money_score: 38,
  weakest_system_1: 'GPS',
  weakest_system_2: 'Money',
  revenue_leak_total: 14700
});
```

### Next.js Server Action Example

```typescript
'use server';

import { z } from 'zod';

const ChristmasSignupSchema = z.object({
  email: z.string().email(),
  first_name: z.string().min(1),
  business_name: z.string().min(1),
  assessment_score: z.number().int().min(0).max(100),
  red_systems: z.number().int().min(0).max(8),
  orange_systems: z.number().int().min(0).max(8),
  yellow_systems: z.number().int().min(0).max(8),
  green_systems: z.number().int().min(0).max(8),
  gps_score: z.number().int().min(0).max(100).optional(),
  money_score: z.number().int().min(0).max(100).optional(),
  weakest_system_1: z.string().optional(),
  weakest_system_2: z.string().optional(),
  revenue_leak_total: z.number().int().optional(),
});

export async function startChristmasSequence(formData: FormData) {
  // Validate input
  const data = ChristmasSignupSchema.parse({
    email: formData.get('email'),
    first_name: formData.get('firstName'),
    business_name: formData.get('businessName'),
    assessment_score: Number(formData.get('assessmentScore')),
    red_systems: Number(formData.get('redSystems')),
    orange_systems: Number(formData.get('orangeSystems')),
    yellow_systems: Number(formData.get('yellowSystems')),
    green_systems: Number(formData.get('greenSystems')),
    gps_score: formData.get('gpsScore') ? Number(formData.get('gpsScore')) : undefined,
    money_score: formData.get('moneyScore') ? Number(formData.get('moneyScore')) : undefined,
    weakest_system_1: formData.get('weakestSystem1') || undefined,
    weakest_system_2: formData.get('weakestSystem2') || undefined,
    revenue_leak_total: formData.get('revenueLeak') ? Number(formData.get('revenueLeak')) : undefined,
  });

  // Trigger Prefect flow
  const response = await fetch(
    'https://prefect.galatek.dev/api/deployments/1ae3a3b3-e076-49c5-9b08-9c176aa47aa0/create_flow_run',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: `christmas-signup-${Date.now()}`,
        parameters: data
      })
    }
  );

  if (!response.ok) {
    throw new Error('Failed to start Christmas sequence');
  }

  const result = await response.json();
  return { success: true, flowRunId: result.id };
}
```

### Expected Response

**Success (201 Created)**:
```json
{
  "id": "03c4c37f-c2de-496a-9a66-8fee56410fcd",
  "created": "2025-11-20T03:11:41.676158Z",
  "name": "christmas-signup-1732073501676",
  "flow_id": "abb1e895-1649-4d56-9a98-6c9e38a93a44",
  "deployment_id": "1ae3a3b3-e076-49c5-9b08-9c176aa47aa0",
  "state_type": "SCHEDULED",
  "state_name": "Scheduled",
  "parameters": {
    "email": "sarah@example.com",
    "first_name": "Sarah",
    "business_name": "Sarah's Salon",
    "assessment_score": 52,
    "red_systems": 2,
    "orange_systems": 1,
    "yellow_systems": 2,
    "green_systems": 3
  }
}
```

**Error (400/500)**:
```json
{
  "detail": "Error message here"
}
```

### What Happens After You Call This?

1. **Immediately** (0-5 seconds):
   - Prefect worker picks up the flow run
   - Creates entry in "Email Sequence" Notion database
   - Checks if already in sequence (idempotent - won't send duplicates!)
   - Creates entry in "BusinessX Canada" Notion database (if doesn't exist)
   - Classifies segment: CRITICAL / URGENT / OPTIMIZE

2. **Within 1 minute** (testing mode) or **immediately** (production mode):
   - Email 1 sent: "Your BusOS Assessment Results"
   - Notion updated with "Email 1 Sent" timestamp

3. **Next 6 emails scheduled**:
   - **Testing mode**: 1min, 2min, 3min, 4min, 5min, 6min intervals (total ~21min)
   - **Production mode**: 24h, 72h, 120h, 168h, 216h, 264h intervals (total 11 days)

4. **Segment-specific content**:
   - **CRITICAL** (2+ red systems): Urgent tone, diagnostic call emphasis
   - **URGENT** (1 red OR 2+ orange): Balanced urgency, implementation focus
   - **OPTIMIZE** (all others): Optimization tone, DIY resources

---

## Endpoint 2: Diagnostic Call Booking (SECONDARY)

### When to Call

✅ **Call this endpoint when**:
- Customer books a diagnostic call via Cal.com
- Cal.com webhook fires `BOOKING_CREATED` event
- You need to send pre-call prep emails

### Endpoint Details

**URL**: `https://prefect.galatek.dev/api/deployments/5445a75a-ae20-4d65-8120-7237e68ae0d5/create_flow_run`

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
  "name": "calcom-booking-{timestamp}",
  "parameters": {
    "email": "customer@example.com",
    "name": "Customer Name",
    "meeting_time": "2025-11-25T14:00:00.000Z"
  }
}
```

### Required Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `email` | string | ✅ Yes | Customer email address | `"customer@example.com"` |
| `name` | string | ✅ Yes | Customer full name | `"Sarah Johnson"` |
| `meeting_time` | string | ✅ Yes | ISO 8601 timestamp of call | `"2025-11-25T14:00:00.000Z"` |

### JavaScript Example

```javascript
async function handleCalcomBooking(calcomWebhook) {
  // Extract data from Cal.com webhook payload
  const booking = calcomWebhook.payload.booking;
  const customer = booking.attendees[0];

  const response = await fetch(
    'https://prefect.galatek.dev/api/deployments/5445a75a-ae20-4d65-8120-7237e68ae0d5/create_flow_run',
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name: `calcom-booking-${Date.now()}`,
        parameters: {
          email: customer.email,
          name: customer.name,
          meeting_time: booking.startTime
        }
      })
    }
  );

  return await response.json();
}
```

### What Happens After You Call This?

1. **Immediately**:
   - Updates Notion "BusinessX Canada" record with booking status
   - Sets "Booking Status" = "Booked"
   - Sets "Diagnostic Call Date" = meeting date
   - Updates "Phase" = "Phase 1 Diagnostic"

2. **Within 5 minutes**:
   - Pre-call prep email 1: "Getting Ready for Your Call"

3. **Scheduled emails**:
   - **Day before call**: "Tomorrow's Your Day!"
   - **2 hours before call**: "Final Reminder + Zoom Link"

---

## Environment Variables for Website

Your website (Vercel) needs these environment variables:

```bash
# Prefect API Configuration
PREFECT_API_URL=https://prefect.galatek.dev/api

# Christmas Campaign Deployment IDs
CHRISTMAS_SIGNUP_DEPLOYMENT_ID=1ae3a3b3-e076-49c5-9b08-9c176aa47aa0
CHRISTMAS_BOOKING_DEPLOYMENT_ID=5445a75a-ae20-4d65-8120-7237e68ae0d5
```

**How to add in Vercel**:
1. Go to Project Settings → Environment Variables
2. Add each variable
3. Redeploy

---

## Testing the Integration

### Test 1: Manual Trigger (Development)

```bash
# Test Christmas signup
curl -X POST https://prefect.galatek.dev/api/deployments/1ae3a3b3-e076-49c5-9b08-9c176aa47aa0/create_flow_run \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test-signup",
    "parameters": {
      "email": "test@example.com",
      "first_name": "Test",
      "business_name": "Test Business",
      "assessment_score": 75,
      "red_systems": 1,
      "orange_systems": 2,
      "yellow_systems": 1,
      "green_systems": 0
    }
  }'
```

**Expected result**:
- Returns flow run ID
- Check Notion "Email Sequence" database for new entry
- Check email inbox for first email

### Test 2: Website Integration (Staging)

1. Deploy website to staging
2. Complete assessment form
3. Submit form
4. Check browser console for API response
5. Check Notion database for new entry
6. Check email inbox

### Test 3: Production Smoke Test

1. Use real email address
2. Complete full assessment
3. Verify all 7 emails received
4. Check timing (testing mode = ~21min total)

---

## Error Handling

### Common Errors

| Status Code | Error | Cause | Fix |
|-------------|-------|-------|-----|
| 400 | Bad Request | Missing required parameters | Check all required fields are sent |
| 404 | Not Found | Wrong deployment ID | Verify deployment ID from this guide |
| 500 | Internal Server Error | Prefect worker down or flow error | Check Prefect logs, contact admin |

### Recommended Error Handling

```javascript
async function triggerChristmasSequence(data) {
  try {
    const response = await fetch(ENDPOINT_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: `christmas-signup-${Date.now()}`,
        parameters: data
      })
    });

    if (!response.ok) {
      // Log error but don't block user
      console.error('Failed to start email sequence:', response.status);

      // Optional: Send to error tracking (Sentry, etc.)
      // Sentry.captureException(new Error(`Email sequence failed: ${response.status}`));

      // Still show success to user - they completed assessment!
      return { success: true, warning: 'Email sequence may be delayed' };
    }

    const result = await response.json();
    return { success: true, flowRunId: result.id };

  } catch (error) {
    console.error('Network error triggering sequence:', error);

    // Don't block user experience for email sequence failures
    return { success: true, warning: 'Email sequence may be delayed' };
  }
}
```

**Important**: Email sequence failures should NOT block the user's assessment completion experience!

---

## Monitoring & Debugging

### Check Flow Run Status

```bash
# Get flow run logs
PREFECT_API_URL=https://prefect.galatek.dev/api prefect flow-run logs <flow-run-id>
```

### Check Notion Databases

1. **Email Sequence Database**: Shows all contacts in sequence, which emails sent
2. **BusinessX Canada Database**: Shows contact details, segment, booking status

### Prefect UI

- **URL**: https://prefect.galatek.dev
- **Flow Runs**: See all executions, logs, failures
- **Deployments**: View Christmas campaign deployments

---

## FAQ

### Q: Can I test without sending real emails?

**A**: Yes! The system is currently in `TESTING_MODE=true`, which:
- Sends emails to real addresses (so use test emails)
- Uses fast timing (minutes instead of days)
- Allows rapid testing

To avoid sending emails entirely, you'd need to mock the Resend API in the flow code.

### Q: What if customer completes assessment twice?

**A**: The flow is **idempotent**:
- Checks if email already exists in "Email Sequence" database
- Won't start duplicate sequences
- Updates existing record if found

### Q: Can I customize email content without redeploying?

**A**: Yes! Email templates are stored in Notion "Email Templates" database:
- Edit template in Notion
- Changes apply on next flow run
- No code deployment needed

### Q: How do I switch from testing to production timing?

**A**: Change environment variable on production worker:
```bash
# On production server
sudo nano /etc/systemd/system/prefect-worker.service
# Change: Environment="TESTING_MODE=true"
# To:     Environment="TESTING_MODE=false"
sudo systemctl daemon-reload
sudo systemctl restart prefect-worker
```

### Q: What segment gets which emails?

**A**: All segments get same 7-email structure, but content varies:
- **Email 1**: Universal (assessment results)
- **Email 2**: Segment-specific (2A/2B/2C based on CRITICAL/URGENT/OPTIMIZE)
- **Email 3-6**: Universal (educational content)
- **Email 7**: Segment-specific (7A/7B/7C based on segment)

Segment logic:
```javascript
function classifySegment(redSystems, orangeSystems) {
  if (redSystems >= 2) return 'CRITICAL';
  if (redSystems === 1 || orangeSystems >= 2) return 'URGENT';
  return 'OPTIMIZE';
}
```

---

## Summary Checklist

### For Website Developer

- [ ] Add environment variables to Vercel
- [ ] Implement POST request to Christmas signup endpoint
- [ ] Pass all required parameters from assessment form
- [ ] Add error handling (don't block user on API failure)
- [ ] Test with staging deployment first
- [ ] Verify emails arrive in inbox
- [ ] Monitor first 10 real signups

### For Testing

- [ ] Test signup flow end-to-end
- [ ] Verify Notion records created
- [ ] Check all 7 emails arrive
- [ ] Test error cases (invalid email, missing fields)
- [ ] Verify idempotency (same email twice)
- [ ] Test different segments (CRITICAL/URGENT/OPTIMIZE)

### For Production Launch

- [ ] Switch `TESTING_MODE=false` on production worker
- [ ] Monitor Prefect UI for failures
- [ ] Check Notion databases daily
- [ ] Review email delivery rates
- [ ] Collect customer feedback on timing/content

---

**Questions?** See `STATUS.md` for deployment status or `DEPLOYMENT_COMPLETE.md` for architecture details.

**Last Updated**: 2025-11-19
**Deployment IDs**: christmas-signup (`1ae3a3b3...`), christmas-booking (`5445a75a...`)
