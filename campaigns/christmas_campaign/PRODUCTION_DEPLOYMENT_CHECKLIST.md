# Production Deployment Checklist - Christmas Campaign

**Status**: ✅ Local testing complete | 🚀 Ready for production
**Date**: 2025-11-19

---

## Pre-Deployment Verification

### ✅ Local Testing Complete

- [x] Prefect server running locally
- [x] FastAPI webhook server running locally
- [x] E2E test suite passing (all 5 tests)
- [x] Flows scheduled successfully
- [x] Test emails sent to 4 test addresses
- [x] Code committed to Git (commit: d664e38)

---

## Production Deployment Steps

### Phase 1: Server Preparation

**Prerequisites**:
- [ ] Production server access (SSH)
- [ ] Server OS: Ubuntu 22.04+ or Debian 11+
- [ ] sudo privileges
- [ ] Domain name configured (e.g., webhook.yourdomain.com)

**Server Specs (Minimum)**:
- CPU: 2 cores
- RAM: 4GB
- Storage: 20GB
- Network: Static IP or domain

---

### Phase 2: Run Deployment Script

**On your production server**, run:

```bash
# 1. Clone repository to server
ssh user@your-server
cd /opt
sudo git clone https://github.com/your-org/perfect.git christmas-campaign
cd christmas-campaign

# 2. Make deployment script executable
chmod +x campaigns/christmas_campaign/scripts/deploy_production.sh

# 3. Run deployment script
./campaigns/christmas_campaign/scripts/deploy_production.sh
```

**The script will**:
1. Update system packages
2. Install Python 3.11+, PostgreSQL, Nginx
3. Create virtual environment
4. Install Python dependencies
5. Create .env file (interactive prompts)
6. Configure systemd services (Prefect server, worker, webhook)
7. Deploy Prefect flows

**You'll need these credentials ready**:
- Notion API token (`ntn_...`)
- Notion Email Sequence DB ID
- Notion BusinessX Canada DB ID
- Resend API key (`re_...`)
- Discord webhook URL (optional)

---

### Phase 3: Configure Domain and SSL

**After deployment script completes**:

```bash
# 1. Point your domain to server IP
# In your DNS provider (Cloudflare, etc.):
# Add A record: webhook.yourdomain.com → server_IP

# 2. Configure Nginx
sudo nano /etc/nginx/sites-available/christmas-webhook

# Paste this config:
server {
    listen 80;
    server_name webhook.yourdomain.com;

    location /webhook/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /health {
        proxy_pass http://localhost:8000/health;
    }
}

# 3. Enable site
sudo ln -s /etc/nginx/sites-available/christmas-webhook /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# 4. Get SSL certificate
sudo certbot --nginx -d webhook.yourdomain.com
```

---

### Phase 4: Update Website Configuration

**In your website repository** (@new-websites/sangletech-tailwindcss):

```bash
# 1. Update production environment variables
# File: .env.production

PREFECT_WEBHOOK_URL=https://webhook.yourdomain.com/webhook/christmas-signup

# 2. Deploy website to production
vercel --prod
# or: git push (if using auto-deploy)
```

---

### Phase 5: Production Testing

**Run E2E tests against production**:

```bash
# On your local machine
export PREFECT_WEBHOOK_URL=https://webhook.yourdomain.com/webhook/christmas-signup

# Test production webhook
curl -X POST $PREFECT_WEBHOOK_URL \
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
#   ...
# }
```

**Verify**:
- [ ] Webhook returns 202 Accepted
- [ ] Prefect UI shows new flow run (http://your-server:4200)
- [ ] Notion Email Sequence DB has new record
- [ ] First email sent within 1 minute (check Resend dashboard)

---

### Phase 6: Monitoring (First 24-48 Hours)

**Service Health**:
```bash
# On production server
sudo systemctl status prefect-server
sudo systemctl status prefect-worker
sudo systemctl status christmas-webhook

# Check logs
sudo journalctl -u christmas-webhook -f
sudo journalctl -u prefect-server -f
```

**Application Monitoring**:
- [ ] Prefect UI accessible: http://your-server:4200 (internal only)
- [ ] Webhook health check: https://webhook.yourdomain.com/health
- [ ] Monitor flow runs: Check for failures in Prefect UI
- [ ] Email delivery: Monitor Resend dashboard for bounces/failures
- [ ] Notion tracking: Verify "Email X Sent" timestamps updating

**Alerts to Watch For**:
- Failed flow runs in Prefect UI
- Email bounces in Resend dashboard
- Notion API rate limits (600 requests/minute)
- Disk space on server (logs can grow)

---

## Rollback Procedure (If Needed)

**If production deployment fails**:

```bash
# Stop services
sudo systemctl stop christmas-webhook prefect-worker prefect-server

# Revert website webhook URL
# In website .env.production:
PREFECT_WEBHOOK_URL=  # Leave empty or comment out

# Re-deploy website
vercel --prod

# Investigate logs
sudo journalctl -u christmas-webhook --since "1 hour ago"
sudo journalctl -u prefect-server --since "1 hour ago"

# Fix issues and restart
sudo systemctl start prefect-server
sudo systemctl start prefect-worker
sudo systemctl start christmas-webhook
```

---

## Post-Deployment Validation

### Success Criteria

- [ ] ✅ All 3 services running (prefect-server, prefect-worker, christmas-webhook)
- [ ] ✅ Webhook accessible via HTTPS with valid SSL cert
- [ ] ✅ Test signup completes successfully
- [ ] ✅ Flow runs appear in Prefect UI
- [ ] ✅ Notion records created correctly
- [ ] ✅ Email 1 sends immediately after signup
- [ ] ✅ Emails 2-7 scheduled correctly (check scheduled times)
- [ ] ✅ No errors in service logs

### Daily Operations

**Maintenance Commands**:
```bash
# View webhook logs
sudo journalctl -u christmas-webhook -n 100 --no-pager

# Check service uptime
sudo systemctl status christmas-webhook prefect-server prefect-worker

# Monitor disk usage
df -h /

# Check database size (PostgreSQL)
sudo -u postgres psql -c "SELECT pg_size_pretty(pg_database_size('prefect'));"

# Restart services (if needed)
sudo systemctl restart christmas-webhook
```

**Weekly Tasks**:
- Review flow run success rates in Prefect UI
- Check email delivery rates in Resend dashboard
- Verify Notion database hasn't hit size limits
- Review server resource usage (CPU/RAM/disk)

---

## Troubleshooting Guide

### Issue: Webhook returns 500 error

**Symptoms**: Website shows "Failed to trigger email sequence"

**Fix**:
```bash
# Check service status
sudo systemctl status christmas-webhook

# Check logs
sudo journalctl -u christmas-webhook -n 50

# Restart service
sudo systemctl restart christmas-webhook
```

---

### Issue: Emails not sending

**Symptoms**: Flow runs complete but no emails arrive

**Fix**:
1. Check Resend API key is valid in .env
2. Verify sender email (value@galatek.dev) is verified in Resend
3. Check Resend dashboard for error logs
4. Verify Prefect worker is running: `sudo systemctl status prefect-worker`

---

### Issue: Duplicate emails sent

**Symptoms**: Customer receives same email multiple times

**Fix**:
1. Check Notion Email Sequence DB for duplicate records
2. Review flow logs for idempotency warnings
3. Verify only one Prefect worker is running
4. Check `search_email_sequence_by_email()` function is working

---

### Issue: Flows stuck in SCHEDULED state

**Symptoms**: Flow runs appear in UI but never execute

**Fix**:
```bash
# Check Prefect worker status
sudo systemctl status prefect-worker

# Restart worker
sudo systemctl restart prefect-worker

# Check worker logs
sudo journalctl -u prefect-worker -f
```

---

## Environment-Specific Notes

### Production vs Testing Mode

**Current `.env` setting**: `TESTING_MODE=true` (fast delays for testing)

**For production launch**, update `.env`:
```bash
# On production server
sudo nano /opt/christmas-campaign/.env

# Change:
TESTING_MODE=false

# Restart services
sudo systemctl restart christmas-webhook prefect-worker
```

**Email Timing**:
- Testing mode: [0min, 1min, 2min, 3min, 4min, 5min, 6min] (6 minutes total)
- Production mode: [0h, 24h, 72h, 120h, 168h, 216h, 264h] (11 days total)

---

## Security Checklist

- [ ] SSL certificate valid and auto-renews
- [ ] Firewall configured (allow 80, 443; block 4200, 8000 from public)
- [ ] .env file has 600 permissions (not world-readable)
- [ ] Services running as www-data (not root)
- [ ] PostgreSQL only listening on localhost
- [ ] Notion API token stored securely
- [ ] Resend API key stored securely
- [ ] Server updates enabled (unattended-upgrades)

---

## Quick Reference

| Resource | URL/Command |
|----------|-------------|
| **Webhook Health** | https://webhook.yourdomain.com/health |
| **Prefect UI** | http://server-ip:4200 (internal only) |
| **Service Logs** | `sudo journalctl -u christmas-webhook -f` |
| **Restart Services** | `sudo systemctl restart christmas-webhook` |
| **Deployment Guide** | `campaigns/christmas_campaign/WAVE4_PRODUCTION_DEPLOYMENT.md` |
| **Testing Guide** | `campaigns/christmas_campaign/WAVE4_TESTING_GUIDE.md` |

---

## Support

**If you encounter issues**:

1. **Check service logs** first:
   ```bash
   sudo journalctl -u christmas-webhook -n 100
   sudo journalctl -u prefect-server -n 100
   ```

2. **Review error documentation**:
   - `campaigns/christmas_campaign/WAVE4_PRODUCTION_DEPLOYMENT.md` (Phase 8: Troubleshooting)
   - `campaigns/christmas_campaign/WAVE4_TESTING_GUIDE.md` (Troubleshooting section)

3. **Verify environment**:
   ```bash
   cat /opt/christmas-campaign/.env | grep -v "TOKEN\|API_KEY"
   ```

4. **Test individual components**:
   - Webhook: `curl https://webhook.yourdomain.com/health`
   - Prefect: `curl http://localhost:4200/api/health`
   - Notion: Check API status at https://www.notion.so/
   - Resend: Check dashboard at https://resend.com/

---

**Last Updated**: 2025-11-19
**Deployment Script**: `campaigns/christmas_campaign/scripts/deploy_production.sh`
**Status**: Ready for production deployment
