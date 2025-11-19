# 🚀 Production Deployment Execution Guide

**Date**: 2025-11-19
**Target Server**: prefect.galatek.dev
**Deployment Method**: Prefect CLI (Simplified Architecture)
**Estimated Time**: 15-20 minutes

---

## Prerequisites Checklist

Before starting, verify:

- [ ] SSH access to prefect.galatek.dev server
- [ ] Prefect server running at `https://prefect.galatek.dev/`
- [ ] `.env` file ready with all credentials:
  - `NOTION_TOKEN`
  - `NOTION_EMAIL_SEQUENCE_DB_ID`
  - `NOTION_BUSINESSX_DB_ID`
  - `RESEND_API_KEY`
  - `RESEND_FROM_EMAIL`
  - `TESTING_MODE=true` (start with true, switch to false after validation)
- [ ] Project code synced to production server
- [ ] Python 3.11+ installed on server
- [ ] Prefect CLI installed on server

---

## Phase 1: SSH and Environment Setup (2-3 minutes)

### Step 1.1: Connect to Server

```bash
# SSH to production server
ssh your-username@galatek.dev

# Navigate to project directory
cd /path/to/perfect

# Verify project exists
ls -la campaigns/christmas_campaign/flows/signup_handler.py
```

**Expected**: File exists at specified path

### Step 1.2: Verify Environment Variables

```bash
# Check if .env exists
cat .env | grep -E "NOTION_TOKEN|RESEND_API_KEY|PREFECT_API_URL"

# Verify required variables
cat .env
```

**Required Variables**:
```bash
# Prefect Configuration
PREFECT_API_URL=https://prefect.galatek.dev/api

# Notion Configuration
NOTION_TOKEN=ntn_xxxxx
NOTION_EMAIL_SEQUENCE_DB_ID=576de1aa-...
NOTION_BUSINESSX_DB_ID=199c97e4c0a0...

# Resend Configuration
RESEND_API_KEY=re_xxxxx
RESEND_FROM_EMAIL=value@galatek.dev

# Application Configuration
TESTING_MODE=true  # Start with true for testing
```

### Step 1.3: Set Python Path

```bash
# Export PYTHONPATH
export PYTHONPATH=/path/to/perfect

# Verify Python can find modules
python -c "from campaigns.christmas_campaign.flows.signup_handler import signup_handler_flow; print('✅ Import successful')"
```

**Expected**: `✅ Import successful`

---

## Phase 2: Work Pool Creation (1-2 minutes)

### Step 2.1: Check Existing Work Pools

```bash
# List existing work pools
prefect work-pool ls
```

### Step 2.2: Create Work Pool (if needed)

```bash
# Create work pool
prefect work-pool create default-pool --type process
```

**Expected Output**:
```
Created work pool 'default-pool' of type 'process'
```

### Step 2.3: Verify Work Pool

```bash
# Verify creation
prefect work-pool ls | grep default-pool
```

---

## Phase 3: Flow Deployment (3-5 minutes)

### Step 3.1: Deploy Flow via Prefect CLI

```bash
# Deploy the Christmas signup handler flow
prefect deploy \
  campaigns/christmas_campaign/flows/signup_handler.py:signup_handler_flow \
  --name christmas-signup-handler \
  --pool default-pool \
  --tag christmas \
  --tag christmas-2025 \
  --tag email-nurture \
  --description "Christmas Campaign signup handler - creates email sequence for new signups" \
  --version 1.0.0
```

**Expected Output**:
```
Deployment 'christmas-signup-handler/christmas-signup-handler' successfully created with id 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'

To execute flow runs from this deployment, start a worker in a separate terminal that pulls work from the 'default-pool' work pool:

        $ prefect worker start --pool default-pool
```

**IMPORTANT**: Save the deployment ID from the output!

### Step 3.2: Verify Deployment

```bash
# List deployments
prefect deployment ls | grep christmas-signup-handler

# Get detailed deployment info
prefect deployment inspect christmas-signup-handler/christmas-signup-handler
```

---

## Phase 4: Worker Setup as Systemd Service (3-5 minutes)

### Step 4.1: Create Systemd Service File

```bash
# Create service file
sudo tee /etc/systemd/system/prefect-worker.service > /dev/null <<'EOF'
[Unit]
Description=Prefect Worker for default-pool
After=network.target

[Service]
Type=simple
User=sangle
WorkingDirectory=/home/sangle/perfect
Environment="PYTHONPATH=/home/sangle/perfect"
Environment="PREFECT_API_URL=https://prefect.galatek.dev/api"
ExecStart=/home/sangle/.local/bin/prefect worker start --pool default-pool
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
```

**Note**: Adjust paths based on your actual setup:
- `User=your-username`
- `WorkingDirectory=/path/to/perfect`
- `ExecStart=/path/to/venv/bin/prefect` (or wherever Prefect is installed)

### Step 4.2: Enable and Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable prefect-worker

# Start service
sudo systemctl start prefect-worker

# Check status
sudo systemctl status prefect-worker
```

**Expected Output**:
```
● prefect-worker.service - Prefect Worker for default-pool
     Loaded: loaded (/etc/systemd/system/prefect-worker.service; enabled)
     Active: active (running) since ...
```

### Step 4.3: Monitor Worker Logs

```bash
# Follow worker logs
sudo journalctl -u prefect-worker -f

# Press Ctrl+C to stop following
```

**Expected Logs**:
```
Starting worker...
Worker 'ProcessWorker ...' started!
Worker polling for flow runs...
```

---

## Phase 5: Get Production Deployment ID (1-2 minutes)

### Method 1: Via Prefect CLI

```bash
# List deployments with IDs
prefect deployment ls
```

**Look for**: `christmas-signup-handler/christmas-signup-handler` and note the ID

### Method 2: Via API

```bash
# Query deployments via API
curl -s https://prefect.galatek.dev/api/deployments/filter -X POST \
  -H "Content-Type: application/json" \
  -d '{"limit": 10}' | jq -r '.[] | select(.name == "christmas-signup-handler") | {name, id}'
```

**Save the deployment ID** - you'll need it for website configuration!

Example: `7fb3ae2c-3a3b-43cc-b1d4-a1078e61c403`

---

## Phase 6: Test Production Endpoint (2-3 minutes)

### Step 6.1: Test Flow Run Creation

```bash
# Replace {DEPLOYMENT_ID} with actual deployment ID from Phase 5
DEPLOYMENT_ID="your-deployment-id-here"

# Create test flow run
curl -X POST https://prefect.galatek.dev/api/deployments/${DEPLOYMENT_ID}/create_flow_run \
  -H "Content-Type: application/json" \
  -d '{
    "name": "production-test-001",
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
    }
  }'
```

**Expected Response**: HTTP 201 Created

```json
{
  "id": "flow-run-uuid",
  "created": "2025-11-19T...",
  "name": "production-test-001",
  "flow_id": "bd0a3aaa-3650-4e30-89c4-27d4172c2460",
  "deployment_id": "7fb3ae2c-3a3b-43cc-b1d4-a1078e61c403",
  "state": {
    "type": "SCHEDULED",
    "message": "Flow run scheduled"
  },
  "parameters": {
    "email": "production-test@example.com",
    ...
  }
}
```

### Step 6.2: Verify in Prefect UI

```bash
# Open Prefect UI in browser
open https://prefect.galatek.dev/

# Or print URL
echo "Open: https://prefect.galatek.dev/"
```

**Check**:
1. Navigate to "Deployments"
2. Click on "christmas-signup-handler"
3. Navigate to "Flow Runs"
4. Look for "production-test-001"
5. Verify state: SCHEDULED → RUNNING → COMPLETED
6. Check logs for execution details

### Step 6.3: Verify Worker Picked Up Flow

```bash
# Check worker logs
sudo journalctl -u prefect-worker -n 50

# Look for:
# - "Worker submitting flow run ..."
# - "Flow run 'production-test-001' started"
# - "Flow run 'production-test-001' completed"
```

---

## Phase 7: Verify Notion Integration (2-3 minutes)

### Step 7.1: Check Email Sequence DB

1. Open Notion Email Sequence database
2. Look for record with email: `production-test@example.com`
3. Verify fields:
   - Email: `production-test@example.com`
   - First Name: `Production`
   - Business Name: `Test Corp`
   - Segment: `CRITICAL` (or expected segment)
   - Campaign: `Christmas 2025`
   - All "Email X Sent" fields initially empty

### Step 7.2: Check BusinessX Canada DB (if applicable)

1. Open BusinessX Canada database
2. Search for contact: `production-test@example.com`
3. Verify contact updated/created

---

## Phase 8: Update Website Configuration (3-5 minutes)

### Step 8.1: Add Environment Variables to Vercel

**Option A: Vercel Dashboard**

1. Go to Vercel project settings
2. Navigate to "Environment Variables"
3. Add variables:

```bash
PREFECT_API_URL=https://prefect.galatek.dev/api
CHRISTMAS_DEPLOYMENT_ID=<deployment-id-from-phase-5>
```

**Option B: Vercel CLI**

```bash
# Add production environment variables
vercel env add PREFECT_API_URL production
# Enter: https://prefect.galatek.dev/api

vercel env add CHRISTMAS_DEPLOYMENT_ID production
# Enter: <deployment-id-from-phase-5>
```

### Step 8.2: Verify Website Integration Code

Check that website code uses the environment variables:

```javascript
// In form handler
const deploymentUrl = `${process.env.PREFECT_API_URL}/deployments/${process.env.CHRISTMAS_DEPLOYMENT_ID}/create_flow_run`;

const response = await fetch(deploymentUrl, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
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
    }
  })
});
```

### Step 8.3: Deploy Website Updates

```bash
# If using Vercel auto-deploy:
git add .
git commit -m "feat: integrate Prefect production deployment for Christmas campaign"
git push origin main

# Or manual deploy:
vercel --prod
```

---

## Phase 9: End-to-End Production Testing (5-10 minutes)

### Test Scenario 1: CRITICAL Segment (Red >= 2)

```bash
curl -X POST https://prefect.galatek.dev/api/deployments/${DEPLOYMENT_ID}/create_flow_run \
  -H "Content-Type: application/json" \
  -d '{
    "name": "e2e-critical",
    "parameters": {
      "email": "critical-test@example.com",
      "first_name": "Critical",
      "business_name": "Critical Corp",
      "assessment_score": 45,
      "red_systems": 3,
      "orange_systems": 2,
      "yellow_systems": 1,
      "green_systems": 0
    }
  }'
```

**Verify**:
- [ ] Flow run created (HTTP 201)
- [ ] Prefect UI shows flow running
- [ ] Notion Email Sequence DB: Segment = "CRITICAL"
- [ ] Email 1 sent within 1 minute (TESTING_MODE=true)

### Test Scenario 2: URGENT Segment (Red = 1 OR Orange >= 2)

```bash
curl -X POST https://prefect.galatek.dev/api/deployments/${DEPLOYMENT_ID}/create_flow_run \
  -H "Content-Type: application/json" \
  -d '{
    "name": "e2e-urgent",
    "parameters": {
      "email": "urgent-test@example.com",
      "first_name": "Urgent",
      "business_name": "Urgent Corp",
      "assessment_score": 55,
      "red_systems": 1,
      "orange_systems": 3,
      "yellow_systems": 2,
      "green_systems": 0
    }
  }'
```

**Verify**:
- [ ] Notion Email Sequence DB: Segment = "URGENT"

### Test Scenario 3: OPTIMIZE Segment (All Others)

```bash
curl -X POST https://prefect.galatek.dev/api/deployments/${DEPLOYMENT_ID}/create_flow_run \
  -H "Content-Type: application/json" \
  -d '{
    "name": "e2e-optimize",
    "parameters": {
      "email": "optimize-test@example.com",
      "first_name": "Optimize",
      "business_name": "Optimize Corp",
      "assessment_score": 75,
      "red_systems": 0,
      "orange_systems": 1,
      "yellow_systems": 3,
      "green_systems": 4
    }
  }'
```

**Verify**:
- [ ] Notion Email Sequence DB: Segment = "OPTIMIZE"

### Test Scenario 4: Idempotency (Duplicate Prevention)

```bash
# Send same email twice
curl -X POST https://prefect.galatek.dev/api/deployments/${DEPLOYMENT_ID}/create_flow_run \
  -H "Content-Type: application/json" \
  -d '{
    "name": "e2e-duplicate-1",
    "parameters": {
      "email": "duplicate-test@example.com",
      "first_name": "Duplicate",
      "business_name": "Duplicate Corp",
      "assessment_score": 60,
      "red_systems": 1,
      "orange_systems": 1,
      "yellow_systems": 1,
      "green_systems": 1
    }
  }'

# Wait 5 seconds, then send again with same email
sleep 5

curl -X POST https://prefect.galatek.dev/api/deployments/${DEPLOYMENT_ID}/create_flow_run \
  -H "Content-Type: application/json" \
  -d '{
    "name": "e2e-duplicate-2",
    "parameters": {
      "email": "duplicate-test@example.com",
      "first_name": "Duplicate",
      "business_name": "Duplicate Corp",
      "assessment_score": 60,
      "red_systems": 1,
      "orange_systems": 1,
      "yellow_systems": 1,
      "green_systems": 1
    }
  }'
```

**Verify**:
- [ ] First request: Email sequence created
- [ ] Second request: Idempotency check prevents duplicate
- [ ] Only ONE email sent to duplicate-test@example.com

---

## Phase 10: Monitoring Setup (3-5 minutes)

### Step 10.1: Create Health Check Script

```bash
# Create health check script on server
cat > /home/sangle/perfect/scripts/health_check.sh <<'EOF'
#!/bin/bash

echo "=== Prefect Worker Health Check ==="
echo "Time: $(date)"
echo ""

# Check worker service
echo "1. Worker Service Status:"
sudo systemctl status prefect-worker | grep "Active:"
echo ""

# Check work pool
echo "2. Work Pool Status:"
prefect work-pool ls | grep default-pool
echo ""

# Check recent flow runs
echo "3. Recent Flow Runs (last 5):"
curl -s https://prefect.galatek.dev/api/flow_runs/filter -X POST \
  -H "Content-Type: application/json" \
  -d '{"limit": 5, "sort": "CREATED_DESC"}' | \
  jq -r '.[] | "\(.name) - \(.state.type) - \(.created)"'
echo ""

echo "=== Health Check Complete ==="
EOF

chmod +x /home/sangle/perfect/scripts/health_check.sh
```

### Step 10.2: Run Health Check

```bash
# Run health check
/home/sangle/perfect/scripts/health_check.sh
```

### Step 10.3: Setup Cron for Daily Health Checks (Optional)

```bash
# Add to crontab
(crontab -l 2>/dev/null; echo "0 9 * * * /home/sangle/perfect/scripts/health_check.sh >> /var/log/prefect-health.log 2>&1") | crontab -

# Verify cron entry
crontab -l | grep health_check
```

---

## Success Criteria ✅

After completing all phases, verify:

- [ ] **Deployment exists**: `prefect deployment ls | grep christmas-signup-handler` shows deployment
- [ ] **Worker running**: `sudo systemctl status prefect-worker` shows "active (running)"
- [ ] **Work pool active**: `prefect work-pool ls` shows default-pool
- [ ] **Flow run creation works**: Test via API returns HTTP 201
- [ ] **Flow execution works**: Flow run completes without errors in Prefect UI
- [ ] **Notion integration**: Records created in Email Sequence DB with correct segment
- [ ] **Email sending**: Email 1 sent within 1 minute (TESTING_MODE=true)
- [ ] **Idempotency**: Duplicate signups prevented
- [ ] **Website integration**: Form submission creates flow runs
- [ ] **Monitoring**: Health check script runs successfully

---

## Post-Deployment Tasks

### Switch to Production Timing (After 24-48 hour validation)

```bash
# SSH to server
ssh your-username@galatek.dev

# Edit .env file
nano /path/to/perfect/.env

# Change:
TESTING_MODE=false  # Production delays: 24h, 72h, 120h, 168h, 216h, 264h

# Save and exit

# Restart worker to pick up new environment
sudo systemctl restart prefect-worker

# Verify worker restarted
sudo systemctl status prefect-worker
```

### Monitor Production for First Week

**Daily Checks**:
1. Run health check script
2. Check Prefect UI for failed flow runs
3. Verify email delivery in Resend dashboard
4. Check Notion Email Sequence DB for records
5. Monitor worker logs for errors

**Monitoring Commands**:
```bash
# Check worker logs
sudo journalctl -u prefect-worker -n 100

# Check recent flow runs
prefect flow-run ls --limit 20

# Check for failures
prefect flow-run ls --state-type FAILED --limit 10
```

---

## Troubleshooting

### Issue: Worker Not Picking Up Flows

**Symptom**: Flow runs stuck in SCHEDULED state

**Solution**:
```bash
# Check worker status
sudo systemctl status prefect-worker

# Restart worker
sudo systemctl restart prefect-worker

# Check logs
sudo journalctl -u prefect-worker -f
```

### Issue: Deployment Not Found

**Symptom**: API returns 404 when creating flow run

**Solution**:
```bash
# Re-deploy flow
cd /path/to/perfect
export PYTHONPATH=/path/to/perfect

prefect deploy \
  campaigns/christmas_campaign/flows/signup_handler.py:signup_handler_flow \
  --name christmas-signup-handler \
  --pool default-pool

# Get new deployment ID
prefect deployment ls | grep christmas-signup-handler
```

### Issue: Environment Variables Not Loaded

**Symptom**: Flow fails with missing credentials

**Solution**:
```bash
# Check .env file
cat /path/to/perfect/.env

# Verify systemd service loads .env
# Edit service file to add:
EnvironmentFile=/path/to/perfect/.env

# Reload and restart
sudo systemctl daemon-reload
sudo systemctl restart prefect-worker
```

---

## Rollback Procedure

If deployment fails and needs rollback:

```bash
# Stop worker
sudo systemctl stop prefect-worker

# Delete deployment
prefect deployment delete christmas-signup-handler/christmas-signup-handler

# Revert code changes (if needed)
git checkout HEAD~1

# Re-run previous deployment or fix issues
```

---

## Summary

**Deployment Time**: 15-20 minutes
**Services Required**: 1 (Prefect with worker)
**Infrastructure**: Simplified (no FastAPI, no Nginx, no webhook subdomain)
**Monitoring**: Health check script + Prefect UI
**Maintenance**: Low (single service to monitor)

**Production Endpoint**:
```
https://prefect.galatek.dev/api/deployments/{DEPLOYMENT_ID}/create_flow_run
```

**Status**: ✅ Ready for Production Deployment

---

**Next Steps**: Execute phases 1-10 in order, verify success criteria, then monitor for 24-48 hours before switching to production timing.
