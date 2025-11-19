# 🚀 Galatek.dev Deployment - READY TO EXECUTE

**Status**: ✅ All scripts and documentation complete
**Target**: webhook.galatek.dev (connects to existing prefect.galatek.dev)
**Date**: 2025-11-19

---

## ✅ What's Complete

### Code & Testing
- [x] Wave 1-4 implementation complete
- [x] Local testing successful (5/5 E2E tests passing)
- [x] Webhook server tested (FastAPI on port 8000)
- [x] Prefect flows tested (email sequences scheduling correctly)
- [x] Idempotency verified
- [x] Segment classification tested (CRITICAL/URGENT/OPTIMIZE)

### Deployment Automation
- [x] **GALATEK_DEPLOYMENT_SCRIPT.sh** - Automated 6-phase deployment
- [x] **GALATEK_DEPLOYMENT_PLAN.md** - Architecture and deployment options
- [x] **GALATEK_NGINX_CONFIG.md** - Complete Nginx configuration guide
- [x] **DEPLOYMENT_QUICK_START.md** - Step-by-step execution guide

### Infrastructure Discovery
- [x] Confirmed Prefect running at https://prefect.galatek.dev/
- [x] Verified Prefect API accessible at https://prefect.galatek.dev/api
- [x] Confirmed Uvicorn server (Python ASGI)
- [x] Health endpoint responding correctly

### Credentials Confirmed
- [x] Using local .env credentials for production
- [x] TESTING_MODE=true for initial validation
- [x] Discord notifications enabled (URL pending)

---

## ⏳ What We Need to Execute

### Critical Information (Required)

**1. SSH Access Details**:
```bash
# Need this information:
SSH_USER="?"           # Your SSH username
SSH_HOST="?"           # Server IP or hostname (where Prefect runs)
SSH_PORT="22"          # SSH port (usually 22)

# Example:
# ssh sang@galatek.dev
# OR
# ssh root@203.0.113.50
```

**2. Server Confirmation**:
- [ ] Confirm webhook server can run on same machine as Prefect (Option A - recommended)
- [ ] OR specify different server for webhook (Option B - more complex)

**3. Discord Webhook URL** (optional):
```bash
# For CRITICAL segment notifications
DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."
# OR skip: we can add this later
```

---

## 🎯 Deployment Execution Plan

Once you provide SSH access, here's the exact process:

### Phase 1: SSH and Setup (5 minutes)

```bash
# 1. SSH to server
ssh your-username@server-ip

# 2. Navigate to deployment location
cd /opt

# 3. Clone repository (if not already there)
sudo git clone https://github.com/your-org/perfect.git christmas-campaign

# 4. Enter directory
cd christmas-campaign
```

### Phase 2: Run Deployment Script (15-20 minutes)

```bash
# 5. Make script executable
chmod +x campaigns/christmas_campaign/GALATEK_DEPLOYMENT_SCRIPT.sh

# 6. Run deployment script
./campaigns/christmas_campaign/GALATEK_DEPLOYMENT_SCRIPT.sh
```

**Script will prompt for**:
- Notion API Token (from your .env: `secret_eXSRJe3C3J2CAgE4AjG25HzplCiXVIIxFwO2AsQVysM`)
- Notion Email Sequence DB ID (from your .env: `576de1aa-6064-4201-a5e6-623b7f2be79a`)
- Notion BusinessX DB ID (from your .env: `199c97e4c0a045278086941b7cca62f1`)
- Resend API Key (from your .env: `re_e5qfBYsX_B9wNs12TKG82XoSi79kuMyWe`)
- Resend From Email (from your .env: `value@galatek.dev`)
- Discord Webhook URL (optional - press Enter to skip)

**Script will automatically**:
1. ✅ Check Prefect connectivity at https://prefect.galatek.dev/api
2. ✅ Install system dependencies (Python 3.11, git, curl, jq)
3. ✅ Create virtual environment in /opt/christmas-campaign
4. ✅ Install Python packages (Prefect, FastAPI, Resend, Notion)
5. ✅ Create .env file with your credentials
6. ✅ Create systemd service: christmas-webhook.service
7. ✅ Deploy Prefect flows to existing Prefect server
8. ✅ Start webhook server on port 8000

### Phase 3: DNS Configuration (5-10 minutes)

```bash
# 7. In your DNS provider (Cloudflare, etc.)
# Add A record:
#   Name: webhook.galatek.dev
#   Type: A
#   Value: [server-ip]
#   TTL: Auto (or 300)

# 8. Wait 5-10 minutes for DNS propagation

# 9. Verify DNS resolution
dig webhook.galatek.dev
# Should show your server IP in the ANSWER section
```

### Phase 4: Nginx Configuration (5-10 minutes)

```bash
# 10. Create Nginx config
sudo nano /etc/nginx/sites-available/christmas-webhook

# 11. Paste config from GALATEK_NGINX_CONFIG.md (provided in repo)

# 12. Enable site
sudo ln -s /etc/nginx/sites-available/christmas-webhook /etc/nginx/sites-enabled/

# 13. Test config
sudo nginx -t

# 14. Reload Nginx
sudo systemctl reload nginx

# 15. Test HTTP endpoint
curl http://webhook.galatek.dev/health
# Should return: {"status":"healthy",...}
```

### Phase 5: SSL Certificate (5 minutes)

```bash
# 16. Run Certbot (auto-configures Nginx for HTTPS)
sudo certbot --nginx -d webhook.galatek.dev

# 17. Test HTTPS endpoint
curl https://webhook.galatek.dev/health
# Should return: {"status":"healthy",...}
```

### Phase 6: Production Testing (10-15 minutes)

```bash
# 18. Test production webhook
curl -X POST https://webhook.galatek.dev/webhook/christmas-signup \
  -H "Content-Type: application/json" \
  -d '{
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
    "marketing_score": 75,
    "weakest_system_1": "GPS System",
    "weakest_system_2": "Money System",
    "revenue_leak_total": 624
  }'

# Expected response:
# {
#   "status": "accepted",
#   "message": "Christmas signup received and email sequence will begin shortly",
#   "email": "production-test@example.com",
#   "campaign": "Christmas 2025",
#   "timestamp": "2025-11-19T..."
# }

# 19. Check Prefect UI for flow run
# Open: https://prefect.galatek.dev/
# Look for: "christmas-signup-handler" flow run
# Email: production-test@example.com
# Status: SCHEDULED or RUNNING

# 20. Check Notion Email Sequence DB
# Should have new record with segment and scheduled emails

# 21. Wait 1 minute (TESTING_MODE=true)
# Check Resend dashboard for first email delivery
```

### Phase 7: Website Integration (10-15 minutes)

```bash
# 22. Update website environment variable
# In your Vercel project settings or .env.production:
PREFECT_WEBHOOK_URL=https://webhook.galatek.dev/webhook/christmas-signup

# 23. Redeploy website
vercel --prod
# OR git push (if auto-deploy enabled)

# 24. Test from actual website form
# Fill out Christmas signup form
# Submit
# Verify email arrives in test inbox
```

---

## 📊 Success Criteria

After deployment, verify these checks:

- [ ] **Webhook server running**: `sudo systemctl status christmas-webhook` shows "active (running)"
- [ ] **HTTP health check**: `curl http://webhook.galatek.dev/health` returns 200 OK
- [ ] **HTTPS health check**: `curl https://webhook.galatek.dev/health` returns 200 OK
- [ ] **Webhook POST test**: Returns `{"status":"accepted",...}`
- [ ] **Prefect flow run**: Appears in https://prefect.galatek.dev/ UI
- [ ] **Notion tracking**: Record created in Email Sequence DB
- [ ] **Email delivery**: First email sends within 1 minute (TESTING_MODE=true)
- [ ] **Website integration**: Form submission triggers webhook successfully
- [ ] **Service logs clean**: `sudo journalctl -u christmas-webhook -n 50` shows no errors

---

## 🔧 Monitoring Commands

### View Webhook Service Logs
```bash
# Real-time logs
sudo journalctl -u christmas-webhook -f

# Last 50 lines
sudo journalctl -u christmas-webhook -n 50

# Filter for specific email
sudo journalctl -u christmas-webhook | grep "test@example.com"
```

### View Nginx Logs
```bash
# Access log (requests)
sudo tail -f /var/log/nginx/christmas-webhook-access.log

# Error log (issues)
sudo tail -f /var/log/nginx/christmas-webhook-error.log
```

### Check Service Status
```bash
# All services
sudo systemctl status christmas-webhook
sudo systemctl status nginx

# Restart if needed
sudo systemctl restart christmas-webhook
sudo systemctl reload nginx
```

### Check Prefect UI
```bash
# Open in browser:
https://prefect.galatek.dev/

# Navigate to:
# Flows → christmas-signup-handler → Flow Runs
# Check for recent runs and their status
```

---

## 🆘 Troubleshooting Quick Reference

### Webhook service won't start
```bash
# Check logs
sudo journalctl -u christmas-webhook -n 50

# Common issues:
# 1. Port 8000 already in use
# 2. Missing .env file
# 3. Python package installation failed

# Fix: Check .env exists
ls -la /opt/christmas-campaign/.env

# Fix: Reinstall packages
cd /opt/christmas-campaign
source venv/bin/activate
pip install -r requirements.txt
```

### Nginx 502 Bad Gateway
```bash
# Cause: Webhook server not running

# Fix: Start service
sudo systemctl start christmas-webhook

# Verify it's listening on port 8000
sudo netstat -tulpn | grep 8000
# Should show: tcp 0 0 0.0.0.0:8000 ... python
```

### DNS not resolving
```bash
# Check DNS propagation
dig webhook.galatek.dev

# If no result:
# - Verify A record created in DNS provider
# - Wait 5-10 more minutes
# - Check DNS provider's control panel
```

### SSL certificate fails
```bash
# Certbot error: "DNS problem: NXDOMAIN"
# Cause: DNS not propagated yet

# Fix: Wait for DNS propagation, then retry:
sudo certbot --nginx -d webhook.galatek.dev
```

### Emails not sending
```bash
# Check Prefect flow runs
# https://prefect.galatek.dev/
# Look for failed or pending flows

# Check flow logs
# Click on flow run → Logs tab
# Look for Resend API errors

# Check Resend dashboard
# https://resend.com/emails
# Verify API key is valid and emails showing there
```

---

## 📁 Deployment Files Reference

**Location**: `campaigns/christmas_campaign/`

| File | Purpose |
|------|---------|
| `GALATEK_DEPLOYMENT_SCRIPT.sh` | Automated deployment script (execute this) |
| `GALATEK_DEPLOYMENT_PLAN.md` | Architecture and deployment options |
| `GALATEK_NGINX_CONFIG.md` | Complete Nginx configuration guide |
| `DEPLOYMENT_QUICK_START.md` | Step-by-step execution guide |
| `GALATEK_DEPLOYMENT_READY.md` | This file - execution checklist |
| `PRODUCTION_DEPLOYMENT_CHECKLIST.md` | Generic production checklist |
| `LOCAL_TESTING_SESSION_SUMMARY.md` | Local testing results |

---

## 🎁 Environment Variables Summary

**Production .env** (will be created by deployment script):

```bash
# Prefect Configuration
PREFECT_API_URL=https://prefect.galatek.dev/api

# Notion Configuration
NOTION_TOKEN=secret_eXSRJe3C3J2CAgE4AjG25HzplCiXVIIxFwO2AsQVysM
NOTION_EMAIL_SEQUENCE_DB_ID=576de1aa-6064-4201-a5e6-623b7f2be79a
NOTION_BUSINESSX_DB_ID=199c97e4c0a045278086941b7cca62f1

# Resend Configuration
RESEND_API_KEY=re_e5qfBYsX_B9wNs12TKG82XoSi79kuMyWe
RESEND_FROM_EMAIL=value@galatek.dev

# Discord Configuration (optional)
DISCORD_WEBHOOK_URL=  # Add your Discord webhook URL or leave empty

# Application Configuration
TESTING_MODE=true      # Start with fast timing for validation
API_HOST=0.0.0.0
API_PORT=8000
```

**After validation** (24-48 hours), change:
```bash
TESTING_MODE=false  # Switch to production timing (24h, 72h, etc.)
```

---

## ⏱️ Time Estimate

**Total deployment time**: 60-90 minutes

**Breakdown**:
1. SSH and setup: 5 minutes
2. Run deployment script: 15-20 minutes
3. DNS configuration: 5-10 minutes (mostly waiting)
4. Nginx configuration: 5-10 minutes
5. SSL certificate: 5 minutes
6. Production testing: 10-15 minutes
7. Website integration: 10-15 minutes

**Most automated!** The deployment script handles 80% of the work.

---

## 🚀 Ready to Deploy!

**What I need from you**:

1. **SSH Access Details**:
   ```
   Username: ?
   Host: ? (IP or hostname of server running prefect.galatek.dev)
   Port: ? (usually 22)
   ```

2. **Confirmation**:
   - [ ] Deploy webhook to same server as Prefect? (Option A - recommended)
   - [ ] OR deploy to different server? (Option B - need different IP)

3. **Optional**:
   - Discord webhook URL (for CRITICAL segment alerts)
   - OR we can add this after deployment

**Once you provide SSH access details, we can execute the deployment in the next 60-90 minutes.**

---

## 📞 Next Steps

**Option 1: Provide SSH Access Now**
```
Reply with:
- SSH username: [username]
- SSH host: [IP or hostname]
- SSH port: [22 or custom]
- Same server as Prefect: yes
- Discord webhook: [URL or "skip for now"]
```

**Option 2: Schedule Deployment**
```
Let me know when you're ready to deploy:
- "Let's deploy tomorrow at [time]"
- "I'll prepare SSH access and let you know"
- etc.
```

**Option 3: Deploy Yourself**
```
Use the deployment script:
1. SSH to server
2. Clone repo
3. Run: ./campaigns/christmas_campaign/GALATEK_DEPLOYMENT_SCRIPT.sh
4. Follow prompts
5. Use GALATEK_NGINX_CONFIG.md for Nginx setup
```

---

**Status**: ✅ Ready to Execute
**Waiting On**: SSH access details from you
**Next Action**: You provide SSH → I guide deployment → Go live in 60-90 minutes

🎄 Let's deploy this Christmas Campaign! 🎄
