# Christmas Campaign - Worker Environment Setup

**Last Updated**: 2025-11-19
**Status**: Production deployment ready

---

## Overview

The Christmas Campaign flows use a **hybrid secrets approach**:

1. **Prefect Secret Blocks** (encrypted, production-ready):
   - `NOTION_TOKEN` - Notion integration token ✅
   - `NOTION_EMAIL_TEMPLATES_DB_ID` - Email templates database ✅
   - `NOTION_EMAIL_SEQUENCE_DB_ID` - Email sequence tracking database ✅
   - `RESEND_API_KEY` - Resend API key for email sending ✅

2. **Environment Variables** (non-sensitive database IDs):
   - `NOTION_BUSINESSX_DB_ID` - BusinessX Canada contacts database
   - `NOTION_CUSTOMER_PROJECTS_DB_ID` - Customer portal pages
   - `NOTION_EMAIL_ANALYTICS_DB_ID` - Email analytics tracking
   - `TESTING_MODE` - Fast waits (true) vs production timing (false)

---

## Why This Approach?

**Secret Blocks** for sensitive credentials:
- ✅ Encrypted storage
- ✅ Centralized management
- ✅ No credentials in git
- ✅ Easy rotation

**Environment Variables** for non-sensitive IDs:
- ✅ Database IDs are not secret (they're in Notion URLs)
- ✅ Simpler to configure
- ✅ No performance overhead loading from blocks
- ✅ Fallback for local development

---

## Production Worker Setup

### Step 1: SSH to Production Server

```bash
ssh sangle@galatek.dev
```

### Step 2: Set Environment Variables

You have two options:

#### Option A: Add to Worker Service File (Recommended)

If you're running the worker as a systemd service:

```bash
# Edit the service file
sudo nano /etc/systemd/system/prefect-worker.service
```

Add these environment variables in the `[Service]` section:

```ini
[Service]
Type=simple
User=sangle
WorkingDirectory=/home/sangle/perfect
Environment="PYTHONPATH=/home/sangle/perfect"
Environment="PREFECT_API_URL=https://prefect.galatek.dev/api"
Environment="NOTION_BUSINESSX_DB_ID=199c97e4c0a045278086941b7cca62f1"
Environment="NOTION_CUSTOMER_PROJECTS_DB_ID=2ab7c374-1115-8176-961f-d8e192e56c4b"
Environment="NOTION_EMAIL_ANALYTICS_DB_ID=2ab7c374-1115-8145-acd4-e2963bc3e441"
Environment="TESTING_MODE=true"
ExecStart=/usr/local/bin/prefect worker start --pool default
Restart=always
RestartSec=10
```

Then reload and restart:

```bash
sudo systemctl daemon-reload
sudo systemctl restart prefect-worker
sudo systemctl status prefect-worker
```

#### Option B: Add to User Profile (Alternative)

If you're running the worker manually in a shell:

```bash
# Add to ~/.bashrc or ~/.profile
cat >> ~/.bashrc <<'EOF'

# Christmas Campaign Environment Variables (Non-Secret)
export NOTION_BUSINESSX_DB_ID="199c97e4c0a045278086941b7cca62f1"
export NOTION_CUSTOMER_PROJECTS_DB_ID="2ab7c374-1115-8176-961f-d8e192e56c4b"
export NOTION_EMAIL_ANALYTICS_DB_ID="2ab7c374-1115-8145-acd4-e2963bc3e441"
export TESTING_MODE="true"
EOF

# Reload
source ~/.bashrc

# Restart worker (if running)
pkill -f "prefect worker" && prefect worker start --pool default
```

---

## Environment Variables Reference

| Variable | Value | Purpose |
|----------|-------|---------|
| `NOTION_BUSINESSX_DB_ID` | `199c97e4c0a045278086941b7cca62f1` | BusinessX Canada contacts database |
| `NOTION_CUSTOMER_PROJECTS_DB_ID` | `2ab7c374-1115-8176-961f-d8e192e56c4b` | Customer portal pages database |
| `NOTION_EMAIL_ANALYTICS_DB_ID` | `2ab7c374-1115-8145-acd4-e2963bc3e441` | Email analytics tracking database |
| `TESTING_MODE` | `true` or `false` | Fast waits (true) vs production timing (false) |

**Important**: These values are from your actual `.env` file and are specific to your Notion workspace.

---

## Testing After Setup

### Trigger Test Flow Run

```bash
curl -X POST https://prefect.galatek.dev/api/deployments/1ae3a3b3-e076-49c5-9b08-9c176aa47aa0/create_flow_run \
  -H "Content-Type: application/json" \
  -d '{
    "name": "worker-env-test",
    "parameters": {
      "email": "worker-test@example.com",
      "first_name": "WorkerTest",
      "business_name": "Testing Worker Env",
      "assessment_score": 80,
      "red_systems": 1,
      "orange_systems": 1,
      "yellow_systems": 1,
      "green_systems": 0
    }
  }'
```

### Check Logs

```bash
# Get the flow run ID from the response above, then:
PREFECT_API_URL=https://prefect.galatek.dev/api prefect flow-run logs <flow-run-id>
```

### Expected Success Indicators

✅ **You should see**:
- "✅ Loaded Notion credentials from Prefect Secret blocks"
- "✅ Loaded Resend API key from Prefect Secret blocks"
- Flow completes successfully
- Email sequence record created in Notion
- 7 send_email flows scheduled

❌ **You should NOT see**:
- "API token is invalid"
- "Could not find database with ID: None"
- "Failed to load from Secret blocks"

---

## Troubleshooting

### "Could not find database with ID: None"

**Cause**: Environment variables not set on worker.

**Fix**: Follow Step 2 above to set environment variables, then restart worker.

### "API token is invalid"

**Cause**: Prefect Secret blocks not created or not accessible.

**Fix**: Run the setup script again:

```bash
cd /Users/sangle/Dev/action/projects/perfect
set -a && source .env && set +a
PREFECT_API_URL=https://prefect.galatek.dev/api python3 scripts/setup_secrets.py
```

### "Failed to load from Secret blocks, using environment variables"

**Cause**: Secret blocks don't exist on this Prefect server.

**Fix**: This is expected for local development. For production, run setup script above.

### Worker Not Picking Up New Environment Variables

**Cause**: Worker service not restarted.

**Fix**:
```bash
# For systemd service
sudo systemctl restart prefect-worker

# For manual process
pkill -f "prefect worker" && prefect worker start --pool default
```

---

## Switching from Testing to Production Mode

### Current State (Testing Mode)

Email sequence timing:
- Email 1: 0 minutes (immediate)
- Email 2: 1 minute
- Email 3: 2 minutes
- Email 4: 3 minutes
- Email 5: 4 minutes
- Email 6: 5 minutes
- Email 7: 6 minutes

**Total**: ~6 minutes

### Production Mode

Email sequence timing:
- Email 1: 0 hours (immediate)
- Email 2: 24 hours
- Email 3: 72 hours (3 days)
- Email 4: 120 hours (5 days)
- Email 5: 168 hours (7 days)
- Email 6: 216 hours (9 days)
- Email 7: 264 hours (11 days)

**Total**: 11 days

### How to Switch

**On production server**:

```bash
ssh sangle@galatek.dev

# Option A: Update service file
sudo nano /etc/systemd/system/prefect-worker.service
# Change: Environment="TESTING_MODE=true"
# To:     Environment="TESTING_MODE=false"
sudo systemctl daemon-reload
sudo systemctl restart prefect-worker

# Option B: Update profile
nano ~/.bashrc
# Change: export TESTING_MODE="true"
# To:     export TESTING_MODE="false"
source ~/.bashrc
# Restart worker
```

**Recommendation**: Only switch to production mode after 24-48 hours of successful testing in testing mode.

---

## Security Notes

### What's Safe to Share

✅ **Database IDs**: These are just Notion database identifiers, not secret
- They're visible in Notion URLs anyway
- No security risk if exposed
- Can be committed to git

❌ **Never Commit These**:
- `NOTION_TOKEN` - Gives full access to your Notion workspace
- `RESEND_API_KEY` - Can send unlimited emails from your account
- These are stored in Prefect Secret blocks (encrypted)

### Credential Rotation

If you need to rotate credentials:

1. **Notion Token**:
   ```bash
   # Create new token in Notion integrations
   # Update Secret block
   PREFECT_API_URL=https://prefect.galatek.dev/api python3 -c "
   from prefect.blocks.system import Secret
   Secret(value='new_token_here').save('notion-token', overwrite=True)
   "
   ```

2. **Resend API Key**:
   ```bash
   # Generate new key in Resend dashboard
   # Update Secret block
   PREFECT_API_URL=https://prefect.galatek.dev/api python3 -c "
   from prefect.blocks.system import Secret
   Secret(value='new_key_here').save('resend-api-key', overwrite=True)
   "
   ```

No need to restart worker - Secret blocks are loaded fresh on each flow run!

---

## Summary

**What you did**:
1. ✅ Created Prefect Secret blocks for sensitive credentials
2. ✅ Updated flow code to load from Secret blocks
3. ⏳ Need to set environment variables on production worker

**Next steps**:
1. SSH to production server
2. Add 4 environment variables to worker configuration
3. Restart worker
4. Test flow execution
5. Verify success in logs

**Expected result**: Christmas Campaign flows will execute successfully, creating Notion records and sending emails via Resend!

---

## Quick Reference

### Database IDs (from .env)
```bash
NOTION_BUSINESSX_DB_ID=199c97e4c0a045278086941b7cca62f1
NOTION_CUSTOMER_PROJECTS_DB_ID=2ab7c374-1115-8176-961f-d8e192e56c4b
NOTION_EMAIL_ANALYTICS_DB_ID=2ab7c374-1115-8145-acd4-e2963bc3e441
TESTING_MODE=true
```

### Test Command
```bash
curl -X POST https://prefect.galatek.dev/api/deployments/1ae3a3b3-e076-49c5-9b08-9c176aa47aa0/create_flow_run \
  -H "Content-Type: application/json" \
  -d '{"name":"test","parameters":{"email":"test@example.com","first_name":"Test","business_name":"Test","assessment_score":50,"red_systems":1,"orange_systems":0,"yellow_systems":0,"green_systems":0}}'
```

---

**Questions?** See `STATUS.md` for deployment status or `DEPLOYMENT_COMPLETE.md` for comprehensive guide.
