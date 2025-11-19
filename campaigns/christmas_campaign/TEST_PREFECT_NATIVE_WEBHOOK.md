# Testing Prefect Native Webhook Approach

**Date**: 2025-11-19
**Goal**: Test if we can POST directly to Prefect API to trigger flows (no FastAPI needed)

---

## Understanding Prefect's Flow Run Creation

### Option 1: Direct Flow Run Creation via API

According to Prefect docs, we can create a flow run directly via API:

```bash
POST /api/flows/{flow_id}/flow_runs
```

**Requirements**:
1. Flow must be registered with Prefect
2. Need flow ID
3. POST with parameters in request body

**Benefits**:
- ✅ No separate webhook server needed
- ✅ No Nginx configuration
- ✅ No additional subdomain
- ✅ Use existing `prefect.galatek.dev`

---

## Test Plan

### Step 1: Register Flow with Prefect

```python
# Create a simple test flow
from prefect import flow

@flow
def christmas_signup_handler(
    email: str,
    first_name: str,
    business_name: str,
    assessment_score: int,
    red_systems: int,
    orange_systems: int,
    yellow_systems: int,
    green_systems: int,
    gps_score: int,
    money_score: int,
    marketing_score: int,
    weakest_system_1: str,
    weakest_system_2: str,
    revenue_leak_total: int
):
    """Christmas signup handler flow - can be triggered via Prefect API."""
    print(f"Processing signup for {email}")
    # ... rest of flow logic
    return {"status": "success", "email": email}

# Run once to register with Prefect
if __name__ == "__main__":
    christmas_signup_handler(
        email="test@example.com",
        first_name="Test",
        # ... other params
    )
```

### Step 2: Get Flow ID

```bash
# List flows
curl -s http://localhost:4200/api/flows/filter -X POST \
  -H "Content-Type: application/json" \
  -d '{"limit": 10, "sort": "CREATED_DESC"}' | jq -r '.[] | {name, id}'

# Find christmas-signup-handler flow ID
```

### Step 3: Create Flow Run via API (THIS IS THE KEY TEST!)

```bash
# POST to create flow run
curl -X POST http://localhost:4200/api/flows/{flow_id}/flow_runs \
  -H "Content-Type: application/json" \
  -d '{
    "name": "christmas-signup-test",
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
    },
    "state": {
      "type": "SCHEDULED",
      "message": "Flow run from website webhook"
    }
  }'
```

**Expected Response**:
```json
{
  "id": "flow-run-uuid",
  "flow_id": "flow-uuid",
  "state": {
    "type": "SCHEDULED"
  },
  ...
}
```

### Step 4: Test with Invalid Data

```bash
# Test validation - send invalid email
curl -X POST http://localhost:4200/api/flows/{flow_id}/flow_runs \
  -H "Content-Type: application/json" \
  -d '{
    "parameters": {
      "email": "not-an-email",
      "assessment_score": "not-a-number"
    }
  }'
```

**Question**: Does Prefect validate parameters?
- If yes → HTTP 400/422 error
- If no → Flow run created but fails during execution

---

## Test Results

### Test 1: Can We Create Flow Run via API?

Let me test this now...

```bash
# First, run the flow once to register it
python -c "
from campaigns.christmas_campaign.flows.signup_handler import signup_handler_flow

# Run once to register
signup_handler_flow(
    email='register-flow@example.com',
    first_name='Register',
    business_name='Test',
    assessment_score=50,
    red_systems=0,
    orange_systems=0,
    yellow_systems=0,
    green_systems=8,
    gps_score=80,
    money_score=80,
    marketing_score=80,
    weakest_system_1='none',
    weakest_system_2='none',
    revenue_leak_total=0
)
"
```

### Test 2: Get Flow ID

```bash
curl -s http://localhost:4200/api/flows/filter -X POST \
  -H "Content-Type: application/json" \
  -d '{"limit": 10}' | jq -r '.[] | select(.name | contains("signup")) | {name, id}'
```

### Test 3: Create Flow Run via API

```bash
# Use flow ID from above
FLOW_ID="<from-step-2>"

curl -X POST http://localhost:4200/api/flows/${FLOW_ID}/flow_runs \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test-native-webhook",
    "parameters": {
      "email": "native-test@example.com",
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
```

---

## Evaluation Criteria

### ✅ Prefect Native is GOOD if:

1. **Can create flow run via API** ✅/❌
   - POST to `/api/flows/{id}/flow_runs` works

2. **Accepts all parameters** ✅/❌
   - All 14 parameters accepted in `parameters` field

3. **Validates data** ✅/❌
   - Returns HTTP 400/422 for invalid data
   - OR validates in flow (acceptable)

4. **Returns useful response** ✅/❌
   - Returns flow_run_id and status
   - Website can handle the response

5. **Execution works** ✅/❌
   - Flow run actually executes
   - Notion + Resend operations work

6. **Error handling** ✅/❌
   - Failed flows are trackable
   - Prefect UI shows errors clearly

### ❌ FastAPI is NEEDED if:

1. **Complex validation required** ❌
   - Need to validate data BEFORE creating flow run
   - Prefect doesn't validate parameters well

2. **Data transformation needed** ❌
   - Need to enrich/transform webhook data
   - Can't do this in Prefect flow

3. **Multiple webhook types** ❌
   - Different endpoints for different flows
   - Prefect approach requires one endpoint per flow

4. **Rate limiting required** ❌
   - Need to prevent spam at webhook layer
   - Prefect doesn't have rate limiting

5. **Custom logging needed** ❌
   - Need detailed webhook-layer logs
   - Prefect flow logs not sufficient

---

## Decision Matrix

| Criterion | Prefect Native | FastAPI |
|-----------|----------------|---------|
| **Simplicity** | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **Infrastructure** | ⭐⭐⭐⭐⭐ (1 service) | ⭐⭐ (3 services) |
| **Deployment Time** | ⭐⭐⭐⭐⭐ (10 min) | ⭐⭐ (60-90 min) |
| **Validation** | ⭐⭐⭐ (flow-level) | ⭐⭐⭐⭐⭐ (webhook-level) |
| **Flexibility** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Maintenance** | ⭐⭐⭐⭐⭐ (less to maintain) | ⭐⭐ (more to maintain) |
| **Logging** | ⭐⭐⭐ (flow logs) | ⭐⭐⭐⭐⭐ (webhook + flow logs) |

---

## Recommended Approach

**For Christmas Campaign**, I recommend **Prefect Native** because:

1. ✅ **Simple use case**: Just need to trigger one flow with parameters
2. ✅ **Single flow type**: Only one webhook endpoint needed
3. ✅ **Validation in flow**: Can validate parameters at start of flow
4. ✅ **Faster deployment**: Skip FastAPI/Nginx/DNS setup
5. ✅ **Less maintenance**: One service instead of three

**Website Integration**:
```javascript
// Instead of:
POST https://webhook.galatek.dev/webhook/christmas-signup

// Use:
POST https://prefect.galatek.dev/api/flows/{flow_id}/flow_runs
{
  "parameters": {
    "email": "...",
    "first_name": "...",
    // ... all parameters
  }
}
```

**Advantages**:
- ✅ Use existing `prefect.galatek.dev` domain
- ✅ SSL already configured
- ✅ No Nginx configuration needed
- ✅ No systemd service needed
- ✅ Deploy in 10 minutes instead of 90

**Limitations** (acceptable for this use case):
- ⚠️ Validation happens in flow (not before)
- ⚠️ Need to provide flow_id to website
- ⚠️ Less control over pre-flow logic

---

## Next Steps

1. **Test the approach** (run tests above)
2. **If successful**, update deployment plan:
   - Remove FastAPI server
   - Remove Nginx configuration
   - Remove webhook subdomain
   - Update website integration docs

3. **Deployment becomes**:
   ```bash
   # Just deploy flows to Prefect
   python campaigns/christmas_campaign/deployments/deploy_christmas.py

   # Get flow ID
   FLOW_ID=$(curl -s https://prefect.galatek.dev/api/flows/filter -X POST \
     -H "Content-Type: application/json" \
     -d '{"limit": 1}' | jq -r '.[0].id')

   # Give flow ID to website team
   echo "Website POST to: https://prefect.galatek.dev/api/flows/${FLOW_ID}/flow_runs"
   ```

**Total deployment time**: 10-15 minutes (vs 60-90 with FastAPI)

---

**Let's test this approach!** 🚀
