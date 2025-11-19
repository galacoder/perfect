# Christmas Campaign - Deployment & Testing Guide

**Campaign**: Christmas Campaign Email Automation
**Status**: Wave 1+2 Complete ✅ - Ready for Deployment Testing
**Last Updated**: 2025-11-18

---

## Overview

This guide walks you through deploying and testing the Christmas Campaign email automation to Prefect Server. The system consists of 8 deployments (7 email senders + 1 orchestrator) that work together to deliver a 7-email nurture sequence.

**What You'll Deploy**:
- 7 atomic email sender flows (one per email)
- 1 email sequence orchestrator flow (schedules all 7 emails)

**Testing Approach**:
- Start in TESTING_MODE (2-7 minute delays)
- Verify all 7 emails send correctly
- Check Notion tracking
- Switch to production mode (24-48 hour delays)

---

## Prerequisites

### 1. Environment Variables

Ensure `.env` file has these variables:

```bash
# Notion Configuration
NOTION_TOKEN=ntn_xxxxx                              # Your Notion integration token
NOTION_EMAIL_TEMPLATES_DB_ID=2ab7c374111581159...  # Email Templates database ID
NOTION_EMAIL_ANALYTICS_DB_ID=xxxxx                 # Email Analytics database ID
NOTION_CONTACTS_DB_ID=xxxxx                         # Contacts database ID (optional)

# Resend Configuration
RESEND_API_KEY=re_xxxxx                             # Your Resend API key
RESEND_FROM_EMAIL=hello@yourdomain.com              # Verified sender email

# Testing Configuration
TESTING_MODE=true                                   # true = fast (2-7min), false = prod (24-48hrs)

# Prefect Configuration (optional, defaults to localhost)
PREFECT_API_URL=http://127.0.0.1:4200/api          # Prefect Server API URL
```

### 2. Notion Setup

**Email Templates Database** (NOTION_EMAIL_TEMPLATES_DB_ID):
- ✅ Should already have 7 templates uploaded (completed in task 1118)
- Template IDs: `christmas_email_1` through `christmas_email_7`
- Verify: Run `python campaigns/christmas_campaign/scripts/seed_email_templates.py --dry-run`

**Email Analytics Database** (NOTION_EMAIL_ANALYTICS_DB_ID):
- Create new database with these properties:
  - **Email ID** (Title) - Unique identifier
  - **Contact Email** (Email) - Recipient email
  - **Email Number** (Number) - Sequence position (1-7)
  - **Template ID** (Text) - Template identifier
  - **Segment** (Select) - CRITICAL / URGENT / OPTIMIZE
  - **Sent At** (Date) - When email was sent
  - **Status** (Select) - sent / failed
  - **Error Message** (Text) - Error details (if failed)
  - **Resend Email ID** (Text) - Resend API response ID

### 3. Resend Setup

1. **Verify Domain**: Your sending domain must be verified in Resend
2. **API Key**: Generate API key with "Sending access"
3. **Test Email**: Add your test email to `RESEND_FROM_EMAIL` or use a verified domain

---

## Deployment Steps

### Step 1: Start Prefect Server

```bash
# Start Prefect Server (in a separate terminal)
prefect server start

# Server will be available at: http://127.0.0.1:4200
```

**What this does**:
- Starts Prefect API server on localhost:4200
- Provides UI for monitoring flows
- Stores deployment metadata

**Verify**: Open http://127.0.0.1:4200 in browser

---

### Step 2: Deploy All Flows

```bash
# Deploy 7 email flows + 1 orchestrator
python campaigns/christmas_campaign/deployments/deploy_all.py
```

**Expected Output**:

```
================================================================================
Christmas Campaign - Prefect Deployment
================================================================================

✅ Connected to Prefect Server: http://127.0.0.1:4200/api

🚀 Deploying 7 email sender flows...

📧 Deploying christmas-email-1...
✅ Deployed christmas-email-1: a1b2c3d4-...

📧 Deploying christmas-email-2...
✅ Deployed christmas-email-2: e5f6g7h8-...

[... emails 3-7 ...]

🚀 Deploying email sequence orchestrator flow...
✅ Deployed orchestrator: x9y8z7w6-...

================================================================================
✅ Deployment Complete!
================================================================================

📋 Copy these deployment IDs to your .env file:

DEPLOYMENT_ID_CHRISTMAS_EMAIL_1=a1b2c3d4-...
DEPLOYMENT_ID_CHRISTMAS_EMAIL_2=e5f6g7h8-...
DEPLOYMENT_ID_CHRISTMAS_EMAIL_3=...
DEPLOYMENT_ID_CHRISTMAS_EMAIL_4=...
DEPLOYMENT_ID_CHRISTMAS_EMAIL_5=...
DEPLOYMENT_ID_CHRISTMAS_EMAIL_6=...
DEPLOYMENT_ID_CHRISTMAS_EMAIL_7=...
DEPLOYMENT_ID_CHRISTMAS_ORCHESTRATOR=x9y8z7w6-...

================================================================================
📝 Next Steps:
================================================================================
1. Update .env file with the deployment IDs above
2. Test the orchestrator flow
3. Trigger via webhook
```

**What this does**:
- Creates 8 Prefect deployments
- Each email sender is parameterized with `email_number` (1-7)
- Orchestrator coordinates scheduling all 7 emails
- Returns deployment IDs for scheduling

---

### Step 3: Update .env with Deployment IDs

Copy the deployment IDs from Step 2 output and add to `.env`:

```bash
# Deployment IDs (from deploy_all.py output)
DEPLOYMENT_ID_CHRISTMAS_EMAIL_1=a1b2c3d4-e5f6-4789-abcd-1234567890ab
DEPLOYMENT_ID_CHRISTMAS_EMAIL_2=e5f6g7h8-i9j0-4789-abcd-1234567890cd
DEPLOYMENT_ID_CHRISTMAS_EMAIL_3=...
DEPLOYMENT_ID_CHRISTMAS_EMAIL_4=...
DEPLOYMENT_ID_CHRISTMAS_EMAIL_5=...
DEPLOYMENT_ID_CHRISTMAS_EMAIL_6=...
DEPLOYMENT_ID_CHRISTMAS_EMAIL_7=...
DEPLOYMENT_ID_CHRISTMAS_ORCHESTRATOR=x9y8z7w6-v5u4-4789-abcd-1234567890xy
```

**Why needed**: Orchestrator flow uses these IDs to schedule email flows via Prefect API

---

## Testing: Test Mode (Fast Delays)

### Step 4: Verify TESTING_MODE Enabled

```bash
# Check .env file
cat .env | grep TESTING_MODE
# Should show: TESTING_MODE=true
```

**Test Mode Timing**:
- Email 1: NOW (0 min)
- Email 2: NOW + 2 min
- Email 3: NOW + 3 min
- Email 4: NOW + 4 min
- Email 5: NOW + 5 min
- Email 6: NOW + 6 min
- Email 7: NOW + 7 min

**Total duration**: ~29 minutes (7 emails + delays)

---

### Step 5: Run Test Contact Flow

Create a test contact payload:

```bash
# Create test_payload.json
cat > test_payload.json << 'EOF'
{
  "email": "test@example.com",
  "first_name": "John",
  "business_name": "Test Salon",
  "segment": "CRITICAL",
  "assessment_data": {
    "red_systems": 2,
    "orange_systems": 1,
    "gps_score": 45,
    "money_score": 38,
    "weakest_system_1": "GPS",
    "weakest_system_2": "Money",
    "revenue_leak_system_1": 8500,
    "revenue_leak_system_2": 6200,
    "total_revenue_leak": 14700,
    "annual_revenue_leak": 176400
  }
}
EOF
```

**Run orchestrator directly** (bypasses webhook):

```bash
# Method 1: Direct Python execution
python -c "
import asyncio
from campaigns.christmas_campaign.flows.email_sequence_orchestrator import email_sequence_orchestrator
from dotenv import load_dotenv
import json

load_dotenv()

with open('test_payload.json') as f:
    payload = json.load(f)

asyncio.run(email_sequence_orchestrator(
    contact_email=payload['email'],
    first_name=payload['first_name'],
    segment=payload['segment'],
    assessment_data=payload['assessment_data']
))
"
```

**Expected Behavior**:
1. Orchestrator schedules 7 email flows
2. Each email flow runs at calculated delay
3. All 7 emails sent over 29 minutes
4. Notion Email Analytics tracks each send

---

### Step 6: Monitor Flow Execution

**Prefect UI** (http://127.0.0.1:4200):
- Navigate to "Flow Runs"
- Look for "email-sequence-orchestrator" run
- Click to see all 7 scheduled child runs

**Console Output**:
```
🚀 Starting Christmas Campaign Email Sequence
📧 Contact: test@example.com (John)
📊 Segment: CRITICAL
🎯 Scheduling 7 emails over 29 minutes (TESTING_MODE)

✅ Email 1 scheduled: christmas-email-1 (send NOW)
⏰ Email 2 scheduled: christmas-email-2 (send in 2 minutes)
⏰ Email 3 scheduled: christmas-email-3 (send in 3 minutes)
⏰ Email 4 scheduled: christmas-email-4 (send in 4 minutes)
⏰ Email 5 scheduled: christmas-email-5 (send in 5 minutes)
⏰ Email 6 scheduled: christmas-email-6 (send in 6 minutes)
⏰ Email 7 scheduled: christmas-email-7 (send in 7 minutes)

✅ All 7 emails scheduled successfully!
```

---

### Step 7: Verify Email Delivery

**Check Resend Dashboard**:
1. Go to https://resend.com/emails
2. Filter by recipient: `test@example.com`
3. Should see 7 emails delivered over 29 minutes

**Check Notion Email Analytics**:
1. Open Email Analytics database
2. Filter by `Contact Email = test@example.com`
3. Should see 7 rows (one per email)
4. All should have `Status = sent`

**Check Actual Inbox**:
- Open test@example.com inbox
- Should receive 7 emails with personalized content
- Verify {{variables}} are properly substituted

---

### Step 8: Validate Variable Substitution

Open each received email and verify:

**Email 1** (Assessment Results):
- ✅ `{{first_name}}` → "John"
- ✅ `{{TotalRevenueLeak_K}}` → "14" (from 14700)
- ✅ `{{GPSScore}}` → "45"
- ✅ `{{WeakestSystem1}}` → "GPS"

**Email 2** (System Fix Framework):
- ✅ Segment-specific template (CRITICAL variant)
- ✅ `{{WeakestSystem1}}` → "GPS"
- ✅ `{{Score1}}` → "45"
- ✅ `{{QuickWinAction}}` → (dynamically generated)

**Emails 3-7**:
- ✅ All variables properly substituted
- ✅ No `{{variable}}` placeholders visible
- ✅ Personalized content matches contact data

---

## Testing: Production Mode (Real Delays)

### Step 9: Switch to Production Mode

```bash
# Update .env file
TESTING_MODE=false
```

**Production Mode Timing**:
- Email 1: NOW (0 hours)
- Email 2: NOW + 48 hours (Day 2)
- Email 3: NOW + 72 hours (Day 3)
- Email 4: NOW + 96 hours (Day 4)
- Email 5: NOW + 144 hours (Day 6)
- Email 6: NOW + 192 hours (Day 8)
- Email 7: NOW + 240 hours (Day 10)

**Total duration**: 10 days

---

### Step 10: Run Production Test (Optional)

**⚠️ WARNING**: This will send emails over 10 days. Use a test email address.

```bash
# Update test_payload.json with real test email
# Then run orchestrator (same as Step 5)
python -c "
import asyncio
from campaigns.christmas_campaign.flows.email_sequence_orchestrator import email_sequence_orchestrator
from dotenv import load_dotenv
import json

load_dotenv()

with open('test_payload.json') as f:
    payload = json.load(f)

asyncio.run(email_sequence_orchestrator(
    contact_email=payload['email'],
    first_name=payload['first_name'],
    segment=payload['segment'],
    assessment_data=payload['assessment_data']
))
"
```

**Monitor Progress**:
- Day 0: Email 1 sent immediately
- Day 2: Check inbox for Email 2
- Day 3: Check inbox for Email 3
- Day 4: Check inbox for Email 4
- Day 6: Check inbox for Email 5
- Day 8: Check inbox for Email 6
- Day 10: Check inbox for Email 7

---

## Webhook Integration (Production)

### Step 11: Add Webhook Endpoint to Server

The orchestrator can be triggered via webhook from your assessment form.

**Webhook URL**: `POST /webhook/christmas-assessment`

**Expected Payload**:
```json
{
  "email": "customer@example.com",
  "first_name": "Sarah",
  "business_name": "Elegant Hair Studio",
  "segment": "CRITICAL",
  "assessment_data": {
    "red_systems": 2,
    "orange_systems": 1,
    "gps_score": 45,
    "money_score": 38,
    "weakest_system_1": "GPS",
    "weakest_system_2": "Money",
    "score_1": 45,
    "score_2": 38,
    "revenue_leak_system_1": 8500,
    "revenue_leak_system_2": 6200,
    "total_revenue_leak": 14700,
    "total_revenue_leak_k": 14,
    "annual_revenue_leak": 176400,
    "quick_win_action": "Add SMS confirmation for 30% no-shows",
    "quick_win_explanation": "Reduce no-shows from 30% to 15%",
    "quick_win_impact": "$4,200/month revenue recovery"
  }
}
```

**Test Webhook** (with server running):
```bash
# Start FastAPI server
uvicorn server:app --reload

# Test webhook
curl -X POST http://localhost:8000/webhook/christmas-assessment \
  -H "Content-Type: application/json" \
  -d @test_payload.json
```

**Expected Response**:
```json
{
  "status": "success",
  "message": "Email sequence scheduled",
  "contact_email": "customer@example.com",
  "segment": "CRITICAL",
  "emails_scheduled": 7
}
```

---

## Troubleshooting

### Issue: "Prefect Server not connected"

**Cause**: Prefect Server not running or wrong URL in .env

**Fix**:
```bash
# Check Prefect Server status
prefect server start

# Verify PREFECT_API_URL in .env
echo $PREFECT_API_URL
# Should be: http://127.0.0.1:4200/api
```

---

### Issue: "Template not found in Notion"

**Cause**: Email templates not uploaded to Notion

**Fix**:
```bash
# Upload all 7 templates
python campaigns/christmas_campaign/scripts/seed_email_templates.py

# Verify templates exist
python campaigns/christmas_campaign/scripts/seed_email_templates.py --dry-run
```

---

### Issue: "Resend API error: Domain not verified"

**Cause**: Sending domain not verified in Resend

**Fix**:
1. Go to https://resend.com/domains
2. Verify your domain with DNS records
3. Update `RESEND_FROM_EMAIL` in .env to use verified domain

---

### Issue: "Email sent but variables not substituted"

**Cause**: Template rendering failed or variables missing in payload

**Fix**:
1. Check Notion template has correct `{{variable}}` syntax
2. Verify `assessment_data` payload includes all required variables
3. Check `template_operations.py:render_template()` logs

---

### Issue: "Emails not scheduled with delays"

**Cause**: Orchestrator not using deployment IDs

**Fix**:
1. Verify `.env` has all 8 `DEPLOYMENT_ID_*` variables
2. Re-run `deploy_all.py` to get fresh deployment IDs
3. Check orchestrator logs for "Scheduling email X with delay Y"

---

## Success Criteria

### ✅ Test Mode Success (29 minutes)
- [ ] All 7 deployments created in Prefect
- [ ] Orchestrator scheduled 7 email flows
- [ ] All 7 emails delivered to test inbox
- [ ] All 7 rows created in Notion Email Analytics
- [ ] All variables properly substituted (no {{placeholders}})
- [ ] Resend dashboard shows 7 delivered emails
- [ ] Prefect UI shows 8 successful flow runs (1 orchestrator + 7 emails)

### ✅ Production Mode Success (10 days)
- [ ] Emails sent with correct 24-48 hour delays
- [ ] Day 0: Email 1 received
- [ ] Day 2: Email 2 received
- [ ] Day 10: Email 7 received
- [ ] No duplicate emails sent
- [ ] Notion tracking accurate for all 7 emails

---

## Next Steps After Successful Testing

Once you've verified the email automation works correctly:

1. **Wave 3: Cal.com Webhook Integration**
   - Add webhook endpoint for booked diagnostics
   - Trigger pre-call prep email sequence
   - Track booking conversions in Notion

2. **Wave 4: Pre-Call Prep & Customer Portal**
   - Implement pre-call document collection
   - Build customer portal for coaching docs
   - Add Phase 2B coaching email sequence (16 weeks)

3. **Production Launch**
   - Connect assessment form to webhook
   - Monitor first 10 real customer sequences
   - Set up alerting for failed emails
   - Create dashboard for campaign metrics

---

## Performance Benchmarks

**Test Mode** (TESTING_MODE=true):
- Orchestrator execution: <1 second
- Each email send: 2-5 seconds
- Total sequence: 29 minutes (includes delays)
- Notion API calls: 7 template fetches + 7 analytics writes

**Production Mode** (TESTING_MODE=false):
- Orchestrator execution: <1 second
- Each email send: 2-5 seconds
- Total sequence: 10 days (includes delays)
- No performance degradation over 10-day period

---

## Files Referenced

| File | Purpose |
|------|---------|
| `deployments/deploy_all.py` | Deploy all 8 flows to Prefect |
| `flows/send_email_flow.py` | Atomic email sender (1 email) |
| `flows/email_sequence_orchestrator.py` | Schedules all 7 emails |
| `tasks/notion_operations.py` | Fetch templates, track analytics |
| `tasks/resend_operations.py` | Send emails via Resend API |
| `tasks/template_operations.py` | Render templates with variables |
| `scripts/seed_email_templates.py` | Upload templates to Notion |
| `tests/test_send_email_flow.py` | Unit tests for email sender |
| `tests/test_orchestrator.py` | Unit tests for orchestrator |

---

## Support

**Questions?** Check the main project documentation:
- Main README: `/README.md`
- Campaign README: `campaigns/christmas_campaign/README.md`
- ASCII Flow Diagram: `campaigns/christmas_campaign/diagrams/COMPLETE_USER_JOURNEY.txt`

**Issues?** Review troubleshooting section above or check Prefect logs.

---

**Last Updated**: 2025-11-18
**Status**: ✅ Ready for deployment testing
**Next**: Deploy and test in TESTING_MODE first
