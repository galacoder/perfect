# Christmas Campaign - Simplified Deployment Guide

**Deployment Method**: Prefect Native API (No FastAPI webhook server)
**Deployment Time**: 15 minutes
**Infrastructure**: 1 service (Prefect only)
**Date**: 2025-11-19

---

## 🎯 Overview

Based on user feedback, we're using **Prefect's native API** to trigger flows directly, eliminating the need for:
- ❌ FastAPI webhook server
- ❌ Nginx reverse proxy
- ❌ Webhook subdomain (webhook.galatek.dev)
- ❌ Additional SSL certificates
- ❌ Systemd service for webhook

**Instead**: Website POSTs directly to `https://prefect.galatek.dev/api/flow_runs/`

**Time saved**: 75 minutes deployment + ongoing maintenance simplification

---

## ✅ Prerequisites

- [x] Prefect server running at `https://prefect.galatek.dev/`
- [x] SSH access to server
- [x] Prefect worker running (to execute flows)
- [x] Environment variables ready (Notion, Resend credentials)

---

## 📋 Deployment Steps

### Step 1: Deploy Flow to Prefect (5 minutes)

```bash
# SSH to server
ssh your-username@galatek.dev

# Navigate to project directory
cd /path/to/perfect

# Set Python path
export PYTHONPATH=/path/to/perfect

# Run flow once to register it with Prefect
python -c "
from campaigns.christmas_campaign.flows.signup_handler import signup_handler_flow

signup_handler_flow(
    email='deploy-test@example.com',
    first_name='Deploy',
    business_name='Test Registration',
    assessment_score=50,
    red_systems=0,
    orange_systems=0,
    yellow_systems=0,
    green_systems=8
)
print('✅ Flow registered with Prefect')
"
```

**Expected Output**:
```
✅ Flow registered with Prefect
```

**What this does**:
- Runs the flow once
- Registers flow with Prefect server
- Creates flow record in Prefect database
- Flow becomes available via API

---

### Step 2: Get Flow ID (2 minutes)

```bash
# Query Prefect API for flow ID
curl -s https://prefect.galatek.dev/api/flows/filter -X POST \
  -H "Content-Type: application/json" \
  -d '{"limit": 10}' | python -c "
import sys, json
data = json.load(sys.stdin)
for flow in data:
    if flow['name'] == 'christmas-signup-handler':
        print(f\"Flow Name: {flow['name']}\")
        print(f\"Flow ID: {flow['id']}\")
        print(f\"\nWebsite should POST to:\")
        print(f\"https://prefect.galatek.dev/api/flow_runs/\")
        print(f\"\nWith flow_id: {flow['id']}\")
"
```

**Expected Output**:
```
Flow Name: christmas-signup-handler
Flow ID: bd0a3aaa-3650-4e30-89c4-27d4172c2460

Website should POST to:
https://prefect.galatek.dev/api/flow_runs/

With flow_id: bd0a3aaa-3650-4e30-89c4-27d4172c2460
```

**Save this flow_id** - you'll need it for the website configuration.

---

### Step 3: Test Flow Run Creation via API (3 minutes)

```bash
# Test creating a flow run via Prefect API
curl -X POST https://prefect.galatek.dev/api/flow_runs/ \
  -H "Content-Type: application/json" \
  -d '{
    "flow_id": "bd0a3aaa-3650-4e30-89c4-27d4172c2460",
    "name": "test-production-webhook",
    "parameters": {
      "email": "production-test@example.com",
      "first_name": "Production",
      "business_name": "Test Corp",
      "assessment_score": 65,
      "red_systems": 1,
      "orange_systems": 1,
      "yellow_systems": 1,
      "green_systems": 0,
      "gps_score": 50,
      "money_score": 70,
      "weakest_system_1": "GPS System",
      "weakest_system_2": "Money System",
      "revenue_leak_total": 624
    },
    "state": {
      "type": "SCHEDULED"
    }
  }'
```

**Expected Response** (HTTP 201):
```json
{
  "id": "flow-run-uuid",
  "created": "2025-11-19T...",
  "name": "test-production-webhook",
  "flow_id": "bd0a3aaa-3650-4e30-89c4-27d4172c2460",
  "state": {
    "type": "SCHEDULED"
  },
  "parameters": {
    "email": "production-test@example.com",
    ...
  }
}
```

✅ **If you see HTTP 201 and a flow_run_id, it's working!**

---

### Step 4: Verify Flow Run in Prefect UI (2 minutes)

```bash
# Open Prefect UI in browser
open https://prefect.galatek.dev/

# Or visit manually and check:
# 1. Navigate to "Flow Runs"
# 2. Look for "test-production-webhook"
# 3. Check state: SCHEDULED → RUNNING → COMPLETED
# 4. View logs to see flow execution
```

**What to check**:
- ✅ Flow run appears in UI
- ✅ State transitions: SCHEDULED → RUNNING → COMPLETED
- ✅ Logs show flow execution steps
- ✅ No errors in logs

---

### Step 5: Update Website Configuration (5 minutes)

#### Option A: Vercel Environment Variables

```bash
# In Vercel dashboard → Project → Settings → Environment Variables
# Add:

PREFECT_API_URL=https://prefect.galatek.dev/api/flow_runs/
CHRISTMAS_FLOW_ID=bd0a3aaa-3650-4e30-89c4-27d4172c2460
```

#### Option B: `.env.production` File

```bash
# In your website repository
# Edit .env.production:

PREFECT_API_URL=https://prefect.galatek.dev/api/flow_runs/
CHRISTMAS_FLOW_ID=bd0a3aaa-3650-4e30-89c4-27d4172c2460
```

#### Update Form Handler Code

```javascript
// In your Christmas signup form handler
async function handleChristmasSignup(formData) {
  try {
    const response = await fetch(process.env.PREFECT_API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        flow_id: process.env.CHRISTMAS_FLOW_ID,
        name: `christmas-signup-${Date.now()}`,
        parameters: {
          email: formData.email,
          first_name: formData.firstName,
          business_name: formData.businessName,
          assessment_score: formData.assessmentScore,
          red_systems: formData.redSystems,
          orange_systems: formData.orangeSystems,
          yellow_systems: formData.yellowSystems,
          green_systems: formData.greenSystems,
          gps_score: formData.gpsScore,
          money_score: formData.moneyScore,
          weakest_system_1: formData.weakestSystem1,
          weakest_system_2: formData.weakestSystem2,
          revenue_leak_total: formData.revenueLeakTotal
        },
        state: {
          type: 'SCHEDULED'
        }
      })
    });

    if (response.ok) {
      const data = await response.json();
      console.log('Flow run created:', data.id);
      // Show success message to user
      return { success: true, flowRunId: data.id };
    } else {
      console.error('Failed to create flow run:', response.status);
      // Show error message to user
      return { success: false, error: 'Failed to start email sequence' };
    }
  } catch (error) {
    console.error('Error:', error);
    return { success: false, error: error.message };
  }
}
```

#### Redeploy Website

```bash
# Commit changes
git add .
git commit -m "feat: integrate Prefect native webhook for Christmas campaign"

# Deploy to Vercel
vercel --prod

# Or if using auto-deploy:
git push origin main
```

---

## ✅ Success Criteria

After deployment, verify:

### 1. Flow Run Creation
```bash
# Test via curl
curl -X POST https://prefect.galatek.dev/api/flow_runs/ \
  -H "Content-Type: application/json" \
  -d '{"flow_id":"<flow-id>","name":"test","parameters":{...}}'

# Expected: HTTP 201 with flow_run_id
```

### 2. Flow Execution
- ✅ Flow run appears in Prefect UI
- ✅ State: SCHEDULED → RUNNING → COMPLETED
- ✅ No errors in logs

### 3. Notion Integration
- ✅ Record created in Email Sequence DB
- ✅ Segment classification correct (CRITICAL/URGENT/OPTIMIZE)
- ✅ Contact exists in BusinessX Canada DB

### 4. Email Sending
- ✅ First email sends within 1 minute (TESTING_MODE=true)
- ✅ Email visible in Resend dashboard
- ✅ Email received in test inbox

### 5. Website Integration
- ✅ Form submission triggers flow run
- ✅ User sees success message
- ✅ Flow run appears in Prefect UI with correct parameters

---

## 🔧 Monitoring

### Prefect UI

**URL**: https://prefect.galatek.dev/

**What to monitor**:
- Flow runs (SCHEDULED, RUNNING, COMPLETED, FAILED)
- Logs for each flow run
- Parameters passed to each run
- Execution duration
- Error messages (if any)

### Notion Email Sequence DB

**Check**:
- New records created for each signup
- Segment classification (CRITICAL/URGENT/OPTIMIZE)
- Email send timestamps
- Email delivery status

### Resend Dashboard

**Check**:
- Emails sent
- Delivery status
- Bounce/spam rates
- Open rates (if tracking enabled)

### Server Logs

```bash
# Prefect server logs
sudo journalctl -u prefect-server -f

# Prefect worker logs
sudo journalctl -u prefect-worker -f
```

---

## 🆘 Troubleshooting

### Issue 1: Flow Not Registered

**Symptom**: `curl` returns 404 when querying for flow

**Solution**:
```bash
# Run flow once to register
python -c "from campaigns.christmas_campaign.flows.signup_handler import signup_handler_flow; signup_handler_flow(...)"

# Verify registration
curl -s https://prefect.galatek.dev/api/flows/filter -X POST \
  -H "Content-Type: application/json" \
  -d '{"limit": 10}' | grep -i christmas
```

### Issue 2: Flow Run Created But Not Executing

**Symptom**: Flow run stuck in SCHEDULED state

**Cause**: No Prefect worker running

**Solution**:
```bash
# Check worker status
sudo systemctl status prefect-worker

# Start worker if not running
sudo systemctl start prefect-worker

# View worker logs
sudo journalctl -u prefect-worker -f
```

### Issue 3: Flow Run Fails with Parameter Error

**Symptom**: Flow run state = FAILED, error about parameters

**Cause**: Invalid parameter names or types

**Solution**:
```bash
# Check flow signature
python -c "
from campaigns.christmas_campaign.flows.signup_handler import signup_handler_flow
import inspect
print(inspect.signature(signup_handler_flow))
"

# Ensure all parameters match signature
# Required: email, first_name, business_name, assessment_score
# Optional: red_systems, orange_systems, yellow_systems, green_systems, etc.
```

### Issue 4: Website Can't Create Flow Runs

**Symptom**: Website POST returns 404 or 500

**Possible Causes**:
1. Wrong API URL
2. Wrong flow_id
3. CORS issues
4. Invalid JSON payload

**Solution**:
```bash
# 1. Verify API URL
curl -I https://prefect.galatek.dev/api/flows/filter
# Expected: HTTP 200 or 405 (POST required)

# 2. Verify flow_id
curl -s https://prefect.galatek.dev/api/flows/filter -X POST \
  -H "Content-Type: application/json" \
  -d '{"limit": 10}' | grep -i christmas

# 3. Check CORS (if accessing from browser)
# Prefect may need CORS configuration for browser requests

# 4. Validate JSON payload
echo '{"flow_id":"...","parameters":{...}}' | python -m json.tool
```

### Issue 5: Emails Not Sending

**Symptom**: Flow completes but no emails sent

**Possible Causes**:
1. Resend API key invalid
2. Notion Email Sequence DB not updated
3. Email scheduling logic error

**Solution**:
```bash
# Check Prefect flow logs
# Navigate to: https://prefect.galatek.dev/
# Click on flow run → Logs tab
# Look for email sending errors

# Check environment variables
cat /path/to/perfect/.env | grep RESEND
cat /path/to/perfect/.env | grep NOTION

# Test Resend API manually
python -c "
from resend import Resend
import os
from dotenv import load_dotenv
load_dotenv()
client = Resend(api_key=os.getenv('RESEND_API_KEY'))
print('Resend API key valid:', client.api_key[:10] + '...')
"
```

---

## 📊 Comparison: Old vs New Approach

| Aspect | Old (FastAPI) | New (Prefect Native) |
|--------|---------------|----------------------|
| **Services** | 3 (FastAPI, Nginx, Prefect) | 1 (Prefect) |
| **Deployment Time** | 60-90 minutes | 15 minutes |
| **Infrastructure** | Complex | Simple |
| **Subdomain** | webhook.galatek.dev | prefect.galatek.dev |
| **SSL Setup** | New certificate needed | Already configured |
| **Nginx Config** | Required | Not needed |
| **Systemd Service** | christmas-webhook | Not needed |
| **Maintenance** | High (3 services) | Low (1 service) |
| **Failure Points** | Many | Few |
| **Debugging** | Multiple log locations | Single Prefect UI |
| **Validation** | Pydantic (pre-flow) | Prefect (in-flow) |
| **Flexibility** | High | Medium |
| **Simplicity** | Low | High ✅ |
| **Total Cost** | Higher | Lower ✅ |

---

## 🎉 Deployment Complete!

After completing all steps, you should have:

✅ Flow registered with Prefect
✅ Flow ID obtained
✅ API endpoint tested
✅ Website configured
✅ End-to-end flow working

**Test the complete flow**:
1. Go to website Christmas signup form
2. Fill out form and submit
3. Check Prefect UI for new flow run
4. Wait 1 minute (TESTING_MODE=true)
5. Check email inbox for first email
6. Verify Notion records created

**Monitor for 24-48 hours**:
- Check Prefect UI daily
- Monitor Resend dashboard
- Review Notion Email Sequence DB
- Watch for any failed flow runs

**After validation, switch to production timing**:
```bash
# Edit .env on server
TESTING_MODE=false  # 24h, 72h, 120h, 168h, 216h, 264h delays

# Restart Prefect worker (if using environment variables)
sudo systemctl restart prefect-worker
```

---

## 📝 Next Steps

### Immediate (First Week)
- [ ] Monitor daily for failed flow runs
- [ ] Check email delivery rates
- [ ] Validate segment classification accuracy
- [ ] Ensure idempotency working (no duplicate emails)

### Short-term (First Month)
- [ ] Analyze email open/click rates
- [ ] Adjust email content based on engagement
- [ ] Monitor Notion data quality
- [ ] Optimize email timing if needed

### Long-term (Ongoing)
- [ ] Scale to handle more signups
- [ ] Add more campaigns using same pattern
- [ ] Integrate with CRM/analytics
- [ ] A/B test email variations

---

**Deployment Status**: ✅ Ready to Deploy
**Estimated Time**: 15 minutes
**Complexity**: Low
**Confidence**: High

**Credit**: Thanks to user for suggesting Prefect native approach - saved 75 minutes and significant complexity!
