# 🚀 Deploy Christmas Campaign to Production - NOW

**Target**: prefect.galatek.dev
**Time**: 15-20 minutes
**Method**: Copy-paste commands below

---

## Prerequisites Check

Before starting, verify you have:
- [ ] SSH access to prefect.galatek.dev
- [ ] Project synced to production server at `/home/sangle/perfect`
- [ ] `.env` file on server with all credentials

---

## Deployment Commands (Copy-Paste Ready)

### Step 1: Connect to Server

```bash
ssh sangle@galatek.dev
```

### Step 2: Navigate to Project

```bash
cd /home/sangle/perfect
```

### Step 3: Verify Environment

```bash
# Check .env exists
ls -la .env

# Verify required variables (should show your tokens)
grep -E "NOTION_TOKEN|RESEND_API_KEY|PREFECT_API_URL" .env

# Set Python path
export PYTHONPATH=/home/sangle/perfect
```

### Step 4: Test Flow Import

```bash
python -c "from campaigns.christmas_campaign.flows.signup_handler import signup_handler_flow; print('✅ Import successful')"
```

**Expected**: `✅ Import successful`

### Step 5: Create Work Pool

```bash
prefect work-pool create default-pool --type process
```

**Expected**: `Created work pool 'default-pool'`

If it says "already exists", that's fine! Continue to next step.

### Step 6: Deploy Flow (THE MAIN COMMAND)

```bash
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

**IMPORTANT**: Save the output! It will show the deployment ID.

Look for line like:
```
Deployment 'christmas-signup-handler/christmas-signup-handler' successfully created with id 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'
```

**Copy that ID** - you'll need it for the website!

### Step 7: Get Deployment ID (if you missed it)

```bash
prefect deployment ls | grep christmas-signup-handler
```

This will show you the deployment ID.

### Step 8: Start Worker as Systemd Service

First, create the service file:

```bash
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
ExecStart=/usr/local/bin/prefect worker start --pool default-pool
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
```

**Note**: Adjust the `ExecStart` path if `prefect` is installed elsewhere. Find it with: `which prefect`

Then enable and start the service:

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

**Expected**: Status shows "active (running)"

### Step 9: Test Production Endpoint

Replace `{DEPLOYMENT_ID}` with your actual deployment ID from Step 6 or 7:

```bash
# Set your deployment ID here
DEPLOYMENT_ID="paste-your-deployment-id-here"

# Test the endpoint
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

**Expected Response**: HTTP 201 with flow run details

### Step 10: Verify in Prefect UI

```bash
# Open in browser (or paste this URL)
echo "https://prefect.galatek.dev/"
```

**Check**:
1. Go to "Deployments" → Should see `christmas-signup-handler`
2. Go to "Flow Runs" → Should see `production-test-001`
3. Check state: SCHEDULED → RUNNING → COMPLETED
4. View logs to verify execution

### Step 11: Monitor Worker Logs

```bash
# Watch worker logs in real-time
sudo journalctl -u prefect-worker -f

# Press Ctrl+C to stop watching
```

**Look for**:
- "Worker submitting flow run..."
- "Flow run 'production-test-001' started"
- "Segment: CRITICAL" (or URGENT/OPTIMIZE)
- "Flow run completed"

---

## ✅ Deployment Complete!

If all steps above succeeded, your deployment is live!

**Save this information**:
- Deployment ID: `_______________________________`
- Production Endpoint: `https://prefect.galatek.dev/api/deployments/{DEPLOYMENT_ID}/create_flow_run`

---

## Next Steps: Update Website

### Step 1: Add Environment Variables to Vercel

Go to your Vercel project settings and add:

```
PREFECT_API_URL=https://prefect.galatek.dev/api
CHRISTMAS_DEPLOYMENT_ID={your-deployment-id-from-above}
```

**OR** use Vercel CLI:

```bash
vercel env add PREFECT_API_URL production
# Enter: https://prefect.galatek.dev/api

vercel env add CHRISTMAS_DEPLOYMENT_ID production
# Enter: {your-deployment-id}
```

### Step 2: Verify Website Code

Your website should already have this code (already updated in Wave 4):

```javascript
// In assessment/complete.ts
const deploymentUrl = `${process.env.PREFECT_API_URL}/deployments/${process.env.CHRISTMAS_DEPLOYMENT_ID}/create_flow_run`;
```

### Step 3: Deploy Website

```bash
# Trigger Vercel deployment (if auto-deploy enabled)
git push origin main

# OR manual deploy
vercel --prod
```

---

## 🧪 End-to-End Testing

After website is deployed, test the complete flow:

1. Go to Christmas assessment page on your website
2. Fill out the form with test data:
   - Email: `e2e-test@example.com`
   - Business name: `E2E Test Corp`
   - Complete the assessment
3. Submit the form
4. **Verify**:
   - ✅ Success message shown on website
   - ✅ Check Prefect UI: New flow run appears
   - ✅ Check Notion Email Sequence DB: New record created
   - ✅ Check email inbox: First email received within 1 minute (TESTING_MODE=true)
   - ✅ Check Resend dashboard: Email sent

---

## 📊 Validation Checklist

After deployment, verify all these:

- [ ] Deployment exists in Prefect UI
- [ ] Worker running: `sudo systemctl status prefect-worker`
- [ ] Test flow run completed successfully
- [ ] Notion Email Sequence DB record created
- [ ] Segment classification correct (CRITICAL/URGENT/OPTIMIZE)
- [ ] Email sent via Resend
- [ ] Email received in inbox
- [ ] Website form submission works
- [ ] Idempotency working (submit same email twice - should prevent duplicate)

---

## 🆘 Troubleshooting

### Issue: Worker Not Running

```bash
# Check status
sudo systemctl status prefect-worker

# View logs
sudo journalctl -u prefect-worker -n 50

# Restart worker
sudo systemctl restart prefect-worker
```

### Issue: Flow Run Fails

```bash
# Check Prefect UI logs
# Go to: https://prefect.galatek.dev/ → Flow Runs → Click failed run → View logs

# Check environment variables
cat /home/sangle/perfect/.env | grep -E "NOTION|RESEND"
```

### Issue: Deployment Not Found

```bash
# List all deployments
prefect deployment ls

# Re-deploy if needed
prefect deploy \
  campaigns/christmas_campaign/flows/signup_handler.py:signup_handler_flow \
  --name christmas-signup-handler \
  --pool default-pool
```

---

## 🎯 Success Criteria

✅ **Deployment is successful when**:
- All 11 deployment steps completed
- Test flow run shows "COMPLETED" in Prefect UI
- Notion record created with correct segment
- Email sent and received
- Website form submission creates flow runs
- Worker service running and healthy

---

## 📝 After Validation (24-48 hours)

Once you've confirmed everything works for 24-48 hours with `TESTING_MODE=true`, switch to production timing:

```bash
# SSH to server
ssh sangle@galatek.dev
cd /home/sangle/perfect

# Edit .env
nano .env

# Change this line:
# FROM: TESTING_MODE=true
# TO:   TESTING_MODE=false

# Save and exit (Ctrl+X, Y, Enter)

# Restart worker
sudo systemctl restart prefect-worker
```

**Production Email Timing**:
- Email 1: 0 hours (immediate)
- Email 2: 24 hours
- Email 3: 72 hours (3 days)
- Email 4: 120 hours (5 days)
- Email 5: 168 hours (7 days)
- Email 6: 216 hours (9 days)
- Email 7: 264 hours (11 days)

**Total sequence**: 11 days

---

## 🎉 You're Live!

Once all steps are complete and validated, your Christmas Campaign is **LIVE IN PRODUCTION**! 🚀

**Support**: If you encounter any issues, check the troubleshooting guides in:
- `PRODUCTION_DEPLOYMENT_EXECUTION.md`
- `FINAL_DEPLOYMENT_CHECKLIST.md`

**Monitoring**:
- Prefect UI: https://prefect.galatek.dev/
- Worker logs: `sudo journalctl -u prefect-worker -f`
- Notion Email Sequence DB: Check daily
- Resend dashboard: Monitor email delivery

---

**Questions?** All documentation is in `campaigns/christmas_campaign/`
