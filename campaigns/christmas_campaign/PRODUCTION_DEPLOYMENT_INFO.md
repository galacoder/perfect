# 🚀 Production Deployment Information - Christmas Campaign

**Date**: 2025-11-19
**Status**: ✅ Deployed and Tested Locally
**Deployment Method**: Prefect CLI + Native API
**Ready for**: Production deployment to prefect.galatek.dev

---

## ✅ Deployment Summary

### Flow Deployed
- **Flow Name**: `christmas-signup-handler`
- **Flow ID**: `bd0a3aaa-3650-4e30-89c4-27d4172c2460`
- **Deployment Name**: `christmas-signup-handler/christmas-signup-handler`
- **Deployment ID**: `7fb3ae2c-3a3b-43cc-b1d4-a1078e61c403`
- **Work Pool**: `default-pool` (type: process)
- **Tags**: `christmas`, `christmas-2025`, `email-nurture`
- **Version**: `1.0.0`

### Deployment Command Used
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

### Test Results
✅ **Flow run created successfully via API**
- HTTP 201 Created
- Flow run ID: `2ca35873-f9fe-40d5-a7fa-fcc326c26b03`
- State: SCHEDULED → RUNNING
- Worker picked up and executed flow
- Flow logs showing correct execution

---

## 🌐 Website Integration

### Production Endpoint

**Website should POST to**:
```
https://prefect.galatek.dev/api/deployments/7fb3ae2c-3a3b-43cc-b1d4-a1078e61c403/create_flow_run
```

### Request Format

```javascript
// Website form handler
const response = await fetch('https://prefect.galatek.dev/api/deployments/7fb3ae2c-3a3b-43cc-b1d4-a1078e61c403/create_flow_run', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
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

### Response Format

**Success (HTTP 201)**:
```json
{
  "id": "flow-run-uuid",
  "created": "2025-11-19T23:29:06.951Z",
  "name": "christmas-signup-1732059123",
  "flow_id": "bd0a3aaa-3650-4e30-89c4-27d4172c2460",
  "deployment_id": "7fb3ae2c-3a3b-43cc-b1d4-a1078e61c403",
  "state": {
    "type": "SCHEDULED",
    "message": "Flow run scheduled"
  },
  "parameters": {
    "email": "test@example.com",
    ...
  }
}
```

---

## 🔧 Production Deployment Steps

### For Production at prefect.galatek.dev

#### Step 1: SSH to Server (2 minutes)
```bash
ssh your-username@galatek.dev
cd /path/to/perfect
```

#### Step 2: Create Work Pool (if needed) (1 minute)
```bash
# Check if work pool exists
prefect work-pool ls

# If not exists, create it
prefect work-pool create default-pool --type process
```

#### Step 3: Deploy Flow (2 minutes)
```bash
# Set Python path
export PYTHONPATH=/path/to/perfect

# Deploy using Prefect CLI
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
Deployment 'christmas-signup-handler/christmas-signup-handler' successfully created with id '...'
```

**Save the deployment ID** from the output!

#### Step 4: Start Worker (2 minutes)
```bash
# Start worker (run in background or as systemd service)
nohup prefect worker start --pool default-pool > /var/log/prefect-worker.log 2>&1 &

# OR create systemd service (recommended for production)
sudo tee /etc/systemd/system/prefect-worker.service > /dev/null <<EOF
[Unit]
Description=Prefect Worker for default-pool
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/perfect
Environment="PYTHONPATH=/path/to/perfect"
Environment="PREFECT_API_URL=https://prefect.galatek.dev/api"
ExecStart=/path/to/venv/bin/prefect worker start --pool default-pool
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl enable prefect-worker
sudo systemctl start prefect-worker
sudo systemctl status prefect-worker
```

#### Step 5: Get Deployment ID (1 minute)
```bash
# Query deployments to get ID
prefect deployment ls | grep christmas-signup-handler

# Or via API
curl -s https://prefect.galatek.dev/api/deployments/filter -X POST \
  -H "Content-Type: application/json" \
  -d '{"limit": 10}' | jq -r '.[] | select(.name == "christmas-signup-handler") | {name, id}'
```

#### Step 6: Test Flow Run Creation (2 minutes)
```bash
# Test via Prefect CLI
prefect deployment run christmas-signup-handler/christmas-signup-handler \
  --param email=test@example.com \
  --param first_name=Test \
  --param business_name="Test Corp" \
  --param assessment_score=65 \
  --param red_systems=1 \
  --param orange_systems=1 \
  --param yellow_systems=1 \
  --param green_systems=0

# OR test via API
curl -X POST https://prefect.galatek.dev/api/deployments/{DEPLOYMENT_ID}/create_flow_run \
  -H "Content-Type: application/json" \
  -d '{
    "name": "production-test",
    "parameters": {
      "email": "test@example.com",
      "first_name": "Test",
      "business_name": "Test Corp",
      "assessment_score": 65,
      "red_systems": 1,
      "orange_systems": 1,
      "yellow_systems": 1,
      "green_systems": 0
    }
  }'
```

#### Step 7: Verify in Prefect UI (2 minutes)
```bash
# Open Prefect UI
open https://prefect.galatek.dev/

# Check:
# - Deployments → christmas-signup-handler
# - Flow Runs → Recent runs
# - Worker → Status: Running
```

#### Step 8: Update Website Config (5 minutes)
```bash
# In Vercel dashboard or .env.production
PREFECT_DEPLOYMENT_URL=https://prefect.galatek.dev/api/deployments/{DEPLOYMENT_ID}/create_flow_run

# Or store separately:
PREFECT_API_URL=https://prefect.galatek.dev/api
CHRISTMAS_DEPLOYMENT_ID={DEPLOYMENT_ID}

# In website code:
const deploymentUrl = `${process.env.PREFECT_API_URL}/deployments/${process.env.CHRISTMAS_DEPLOYMENT_ID}/create_flow_run`;
```

**Total Time**: ~15-20 minutes

---

## 📊 Monitoring

### Prefect UI
**URL**: https://prefect.galatek.dev/

**Monitor**:
- Deployments → christmas-signup-handler
- Flow Runs → All runs for this deployment
- Workers → default-pool worker status
- Logs → Flow run execution logs

### Systemd Logs (if using systemd service)
```bash
# Worker logs
sudo journalctl -u prefect-worker -f

# Recent logs
sudo journalctl -u prefect-worker -n 100
```

### Notion Email Sequence DB
- Check for new records
- Verify segment classification
- Monitor email send status

### Resend Dashboard
- View sent emails
- Check delivery rates
- Monitor bounces/spam

---

## 🔐 Environment Variables

### Required on Production Server

Create `/path/to/perfect/.env`:

```bash
# Prefect Configuration
PREFECT_API_URL=https://prefect.galatek.dev/api

# Notion Configuration
NOTION_TOKEN=ntn_...
NOTION_EMAIL_SEQUENCE_DB_ID=576de1aa-...
NOTION_BUSINESSX_DB_ID=199c97e4c0a0...

# Resend Configuration
RESEND_API_KEY=re_...
RESEND_FROM_EMAIL=value@galatek.dev

# Application Configuration
TESTING_MODE=true  # Start with true, switch to false after validation

# Optional: Discord
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

---

## ✅ Success Criteria

After deployment, verify:

- [ ] **Deployment exists**: `prefect deployment ls | grep christmas-signup-handler`
- [ ] **Worker running**: `sudo systemctl status prefect-worker`
- [ ] **Work pool active**: `prefect work-pool ls` shows default-pool
- [ ] **Flow run creation works**: Test via API returns HTTP 201
- [ ] **Flow execution works**: Flow run completes without errors
- [ ] **Notion integration**: Records created in Email Sequence DB
- [ ] **Email sending**: Emails sent via Resend
- [ ] **Website integration**: Form submission creates flow runs

---

## 🆘 Troubleshooting

### Issue: Deployment not found

**Symptom**: `prefect deployment ls` doesn't show christmas-signup-handler

**Solution**:
```bash
# Re-deploy
cd /path/to/perfect
export PYTHONPATH=/path/to/perfect
prefect deploy campaigns/christmas_campaign/flows/signup_handler.py:signup_handler_flow \
  --name christmas-signup-handler \
  --pool default-pool
```

### Issue: Worker not picking up flows

**Symptom**: Flow runs stuck in SCHEDULED state

**Solution**:
```bash
# Check worker status
prefect work-pool inspect default-pool

# Restart worker
sudo systemctl restart prefect-worker

# Check worker logs
sudo journalctl -u prefect-worker -f
```

### Issue: Flow run fails with import error

**Symptom**: Flow run fails with "ModuleNotFoundError"

**Solution**:
```bash
# Ensure PYTHONPATH is set in worker service
# Edit /etc/systemd/system/prefect-worker.service
Environment="PYTHONPATH=/path/to/perfect"

# Reload and restart
sudo systemctl daemon-reload
sudo systemctl restart prefect-worker
```

### Issue: Website can't create flow runs

**Symptom**: POST returns 404 or 403

**Solution**:
```bash
# 1. Verify deployment ID
prefect deployment ls | grep christmas-signup-handler

# 2. Test API endpoint manually
curl -X POST https://prefect.galatek.dev/api/deployments/{DEPLOYMENT_ID}/create_flow_run \
  -H "Content-Type: application/json" \
  -d '{"name":"test","parameters":{...}}'

# 3. Check CORS (if needed)
# Prefect should allow CORS by default, but verify
```

---

## 🎯 Local vs Production Comparison

| Aspect | Local (Tested) | Production (To Deploy) |
|--------|---------------|------------------------|
| **Prefect Server** | http://localhost:4200 | https://prefect.galatek.dev |
| **Deployment ID** | 7fb3ae2c-3a3b-43cc-b1d4-a1078e61c403 | Will be different |
| **Work Pool** | default-pool | default-pool (same) |
| **Worker** | Running in background | Systemd service |
| **API Endpoint** | http://localhost:4200/api | https://prefect.galatek.dev/api |
| **SSL** | None | Yes (already configured) |

---

## 📝 Next Steps

1. **Deploy to prefect.galatek.dev** (15-20 minutes)
   - Follow Step 1-7 above
   - Get production deployment ID
   - Start worker as systemd service

2. **Update website** (5 minutes)
   - Add PREFECT_DEPLOYMENT_URL to environment
   - Deploy website to Vercel

3. **Test end-to-end** (10 minutes)
   - Submit test form on website
   - Verify flow run created
   - Check Notion + Resend
   - Confirm email received

4. **Monitor** (24-48 hours)
   - Watch Prefect UI for runs
   - Check email delivery rates
   - Verify idempotency
   - Monitor for errors

5. **Switch to production timing** (after validation)
   ```bash
   # Edit .env on server
   TESTING_MODE=false

   # Restart worker
   sudo systemctl restart prefect-worker
   ```

---

## 🎉 Summary

✅ **Local Deployment Complete**:
- Flow deployed via Prefect CLI
- Deployment ID: `7fb3ae2c-3a3b-43cc-b1d4-a1078e61c403`
- Worker running and executing flows
- API endpoint tested and working
- Flow execution verified

🚀 **Ready for Production**:
- Use same `prefect deploy` command on server
- Get new deployment ID for production
- Update website with production deployment URL
- Total deployment time: ~20 minutes

📚 **Documentation Complete**:
- Deployment guide: `DEPLOYMENT_GUIDE_SIMPLIFIED.md`
- Architecture decision: `SIMPLIFIED_ARCHITECTURE_DECISION.md`
- This file: Production deployment info

**Credit**: Thanks to user for suggesting Prefect CLI deployment! Much simpler than FastAPI approach.
