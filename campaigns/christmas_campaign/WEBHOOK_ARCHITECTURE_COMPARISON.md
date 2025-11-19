# Webhook Architecture Comparison

**Date**: 2025-11-19
**Decision**: Choose between Prefect native webhooks vs FastAPI webhook server

---

## Current Approach (FastAPI Webhook Server)

### Architecture
```
Website Form (Vercel)
    ↓ POST
webhook.galatek.dev (FastAPI on port 8000)
    ↓ Triggers
prefect.galatek.dev (Prefect API)
    ↓ Executes
Flow Run → Notion + Resend
```

### Components Required
1. **FastAPI Server** (`server.py`)
   - Custom webhook endpoint: `/webhook/christmas-signup`
   - Validation via Pydantic models
   - Background task triggering
   - Port 8000

2. **Systemd Service** (`christmas-webhook.service`)
   - Auto-start on boot
   - Service management
   - Log rotation

3. **Nginx Configuration**
   - Reverse proxy for webhook.galatek.dev
   - SSL/TLS termination
   - Security headers
   - Rate limiting

4. **DNS Configuration**
   - A record: webhook.galatek.dev → server IP
   - SSL certificate via Certbot

5. **Deployment Script**
   - Install dependencies
   - Configure services
   - Deploy flows

### Pros ✅
- **Full control** over webhook logic
- **Custom validation** with Pydantic
- **Flexible routing** (can handle multiple webhook types)
- **Independent scaling** (webhook server separate from Prefect)
- **Better logging** at webhook layer
- **Error handling** before triggering flows
- **Familiar tech stack** (FastAPI is well-known)

### Cons ❌
- **Extra complexity** (additional service to maintain)
- **Extra subdomain** (webhook.galatek.dev)
- **Extra Nginx config** (reverse proxy setup)
- **More infrastructure** (systemd service, monitoring)
- **More failure points** (FastAPI, Nginx, DNS)

---

## Alternative Approach (Prefect Native Webhooks)

### Research Needed 🔍

Let me investigate Prefect v3.4.1 webhook capabilities:

**Question 1**: Does Prefect support HTTP webhook triggers?
- Prefect has **Automations** with **EventTriggers**
- Can we POST to a Prefect endpoint to trigger a flow?

**Question 2**: What's the endpoint URL format?
- Is it: `https://prefect.galatek.dev/api/automations/trigger/{id}` ?
- Or: `https://prefect.galatek.dev/api/webhooks/{deployment_id}` ?

**Question 3**: Can we validate payload before flow execution?
- Prefect automations use event matching
- Can we validate complex Pydantic models?

**Question 4**: How do we create the webhook?
- Via Prefect UI?
- Via Python API?
- Via deployment configuration?

---

## Investigation: Prefect Webhook Capabilities

### Prefect v3.4.1 Features

**Automations** (`/api/automations/`):
- Create automation with trigger
- EventTrigger matches events
- CompoundTrigger combines multiple triggers
- Actions: RunDeployment, CallWebhook, CancelFlowRun, etc.

**Events** (Prefect's event system):
- Flows emit events
- Automations react to events
- Custom events can be emitted

**Potential Webhook Flow**:
```
Website Form
    ↓ POST (custom event)
Prefect Event API
    ↓ Triggers
Automation (EventTrigger)
    ↓ Executes
RunDeployment Action
    ↓ Starts
Flow Run → Notion + Resend
```

### Questions to Answer

1. **Can we POST directly to Prefect to trigger a flow?**
   - Check: `/api/deployments/{id}/trigger` endpoint
   - Check: Custom event emission via API

2. **Can we validate payload at Prefect layer?**
   - Prefect deployments accept parameters
   - Can we use Pydantic models in deployment parameters?

3. **What's the URL the website would POST to?**
   - `https://prefect.galatek.dev/api/deployments/{deployment_id}/create_flow_run` ?
   - With payload in request body?

4. **Do we lose any functionality?**
   - Custom validation logic
   - Error handling before flow execution
   - Logging/monitoring at webhook layer

---

## Let's Test Prefect Native Approach

### Test 1: Trigger Deployment via API

```bash
# Create a test flow run via Prefect API
curl -X POST https://prefect.galatek.dev/api/deployments/{deployment_id}/create_flow_run \
  -H "Content-Type: application/json" \
  -d '{
    "parameters": {
      "email": "test@example.com",
      "first_name": "Test",
      "business_name": "Test Corp"
    }
  }'
```

**If this works**, we could use Prefect's native flow run creation instead of FastAPI!

### Test 2: Check if Prefect validates parameters

```python
# In our deployment
@flow
def christmas_signup_handler(
    email: str,
    first_name: str,
    business_name: str,
    # ... all parameters with type hints
):
    # Prefect should validate types
    pass
```

**If Prefect validates**, we might not need FastAPI validation layer.

### Test 3: Error handling

**Question**: If we POST invalid data to `/api/deployments/.../create_flow_run`, what happens?
- Does Prefect return 400 Bad Request?
- Or does it create flow run that fails immediately?

---

## Comparison Matrix

| Feature | FastAPI Approach | Prefect Native |
|---------|-----------------|----------------|
| **Infrastructure** | FastAPI + Nginx + DNS | Prefect only ✅ |
| **Validation** | Pydantic (full control) ✅ | Prefect validation (limited?) |
| **Error Handling** | Pre-flow validation ✅ | Flow-level handling |
| **Logging** | Webhook layer logs ✅ | Flow logs only |
| **Complexity** | High (3 services) | Low (1 service) ✅ |
| **Flexibility** | Very flexible ✅ | Limited to Prefect features |
| **Maintenance** | More to maintain | Less to maintain ✅ |
| **Scaling** | Independent scaling ✅ | Coupled with Prefect |
| **URL** | webhook.galatek.dev | prefect.galatek.dev ✅ |
| **SSL** | Separate Certbot | Already configured ✅ |

---

## Recommendation Pending Investigation

### If Prefect Native Works Well:

**Use Prefect Native** if:
- ✅ Can POST to `/api/deployments/{id}/create_flow_run`
- ✅ Prefect validates parameters (rejects invalid data)
- ✅ Returns proper HTTP error codes (400, 422, etc.)
- ✅ Website can handle Prefect's response format
- ✅ You're OK with less pre-flow validation control

**Benefits**:
- 🚀 **Simpler deployment** (no FastAPI, no Nginx, no DNS)
- 🚀 **Less infrastructure** (one less service to maintain)
- 🚀 **Faster deployment** (skip FastAPI setup entirely)
- 🚀 **Use existing URL** (prefect.galatek.dev already configured)

### If Prefect Native Has Limitations:

**Use FastAPI Approach** if:
- ❌ Prefect doesn't validate parameters well
- ❌ Need custom validation logic before flow execution
- ❌ Want detailed webhook-layer logging
- ❌ Need to transform/enrich data before triggering flow
- ❌ Want rate limiting at webhook layer
- ❌ Need multiple webhook types with different validation

---

## Action Plan

### Step 1: Test Prefect Native Approach (10 minutes)

```bash
# 1. Deploy Christmas signup flow
python campaigns/christmas_campaign/deployments/deploy_christmas.py

# 2. Get deployment ID
curl -s http://localhost:4200/api/deployments/filter -X POST \
  -H "Content-Type: application/json" \
  -d '{"limit": 1, "sort": "CREATED_DESC"}' | jq -r '.[0].id'

# 3. Trigger flow run via API
curl -X POST http://localhost:4200/api/deployments/{deployment_id}/create_flow_run \
  -H "Content-Type: application/json" \
  -d '{
    "parameters": {
      "email": "test-native@example.com",
      "first_name": "Native",
      "business_name": "Test Corp",
      "assessment_score": 65,
      "red_systems": 1,
      "orange_systems": 1,
      "yellow_systems": 1,
      "green_systems": 0,
      "gps_score": 50,
      "money_score": 70,
      "marketing_score": 75,
      "weakest_system_1": "GPS",
      "weakest_system_2": "Money",
      "revenue_leak_total": 624
    }
  }'

# 4. Check response
# - HTTP 200/201? ✅ Success
# - HTTP 400/422? ❌ Validation error
# - Flow run created? Check Prefect UI

# 5. Test invalid data
curl -X POST http://localhost:4200/api/deployments/{deployment_id}/create_flow_run \
  -H "Content-Type: application/json" \
  -d '{
    "parameters": {
      "email": "invalid-email",
      "assessment_score": "not-a-number"
    }
  }'

# Expected: HTTP 400 or 422 if Prefect validates
```

### Step 2: Make Decision (5 minutes)

**If Prefect native works**:
- ✅ Use `https://prefect.galatek.dev/api/deployments/{id}/create_flow_run`
- ✅ Update website to POST directly to Prefect
- ✅ Skip FastAPI/Nginx/DNS setup entirely
- ✅ Deploy flows only

**If Prefect native has limitations**:
- ✅ Continue with FastAPI approach
- ✅ Benefits outweigh complexity
- ✅ Use existing deployment scripts

### Step 3: Update Deployment Plan (10 minutes)

Based on decision, update:
- `GALATEK_DEPLOYMENT_PLAN.md`
- `GALATEK_DEPLOYMENT_SCRIPT.sh`
- `GALATEK_DEPLOYMENT_READY.md`

Either:
- **Simplify** (remove FastAPI/Nginx sections)
- **Continue** (keep existing plan)

---

## User's Point

> "I don't get why you need to use Nginx for webhook.galatek.dev. Why don't you just use the Prefect one? Because if you use the Prefect skill, you see that actually webhook is supported in Prefect."

**You're absolutely right!** Let's test Prefect's native capabilities first before adding complexity.

---

## Next Steps

1. **Test Prefect native webhook** (create flow run via API)
2. **Validate parameters** (ensure Prefect rejects invalid data)
3. **Check response format** (ensure website can handle it)
4. **Make decision** (Prefect native vs FastAPI)
5. **Update deployment plan** accordingly

**Let's test now!** 🚀

---

**Status**: 🔍 Investigation in progress
**Decision**: Pending test results
**Recommended**: Test Prefect native first (simpler is better!)
