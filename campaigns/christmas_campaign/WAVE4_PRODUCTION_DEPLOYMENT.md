# Wave 4 Production Deployment Plan - Task 4.3

**Date**: 2025-11-19
**Status**: 🚧 IN PROGRESS
**Task**: 4.3 - Production deployment and monitoring

---

## Overview

This document outlines the complete production deployment strategy for the Christmas Campaign webhook-based email automation system.

**Architecture**:
```
Website (Vercel) → Prefect Server (Homelab) → Notion + Resend
                         ↓
                  Email Sequence DB
```

---

## Prerequisites

### Hardware Requirements (Homelab)

**Minimum Specs**:
- **CPU**: 14-16 threads
- **RAM**: 32-64GB
- **Storage**: 1TB SSD
- **Network**: Stable connection with static IP or dynamic DNS

**Operating System**:
- Ubuntu 22.04 LTS (recommended)
- Or: Debian 11+, CentOS 8+

### Software Requirements

- **Python**: 3.11+
- **PostgreSQL**: 14+ (for Prefect database)
- **Nginx**: Latest (reverse proxy)
- **Certbot**: Latest (SSL certificates)
- **Docker** (optional): Latest (for containerized deployment)

---

## Deployment Architecture

### Option A: Systemd Deployment (Recommended for Homelab)

**Benefits**:
- ✅ Direct control over services
- ✅ Native OS integration
- ✅ Easy troubleshooting
- ✅ Lower resource overhead

**Services**:
1. `prefect-server.service` - Prefect orchestration
2. `prefect-worker.service` - Background task execution
3. `christmas-webhook.service` - FastAPI webhook server

### Option B: Docker Deployment

**Benefits**:
- ✅ Easier migration between servers
- ✅ Isolated environments
- ✅ Simple rollback with container tags

**Containers**:
1. `prefect-server` - Prefect orchestration + PostgreSQL
2. `christmas-webhook` - FastAPI webhook server

---

## Phase 1: Server Preparation

### Step 1.1: Update System

```bash
# Update packages
sudo apt update && sudo apt upgrade -y

# Install essential tools
sudo apt install -y git curl wget vim htop nginx certbot python3-certbot-nginx
```

### Step 1.2: Install Python 3.11+

```bash
# Add deadsnakes PPA (if Ubuntu)
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update

# Install Python 3.11
sudo apt install -y python3.11 python3.11-venv python3.11-dev

# Verify installation
python3.11 --version
```

### Step 1.3: Install PostgreSQL

```bash
# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Start and enable PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create Prefect database
sudo -u postgres psql -c "CREATE DATABASE prefect;"
sudo -u postgres psql -c "CREATE USER prefect WITH PASSWORD 'your_secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE prefect TO prefect;"
```

### Step 1.4: Configure Firewall

```bash
# Allow SSH (if not already)
sudo ufw allow ssh

# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow Prefect UI (optional - can be proxied via Nginx)
sudo ufw allow 4200/tcp

# Enable firewall
sudo ufw enable
```

---

## Phase 2: Application Deployment

### Step 2.1: Clone Repository

```bash
# Create application directory
sudo mkdir -p /opt/christmas-campaign
sudo chown $USER:$USER /opt/christmas-campaign

# Clone repository
cd /opt/christmas-campaign
git clone https://github.com/your-org/perfect.git .

# Or: Copy files via rsync/scp
rsync -avz /Users/sangle/Dev/action/projects/perfect/ user@homelab:/opt/christmas-campaign/
```

### Step 2.2: Create Python Virtual Environment

```bash
cd /opt/christmas-campaign

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 2.3: Configure Environment Variables

```bash
# Create production .env file
cat > /opt/christmas-campaign/.env <<'EOF'
# Prefect Configuration
PREFECT_API_DATABASE_CONNECTION_URL=postgresql+asyncpg://prefect:your_secure_password@localhost/prefect
PREFECT_SERVER_API_HOST=0.0.0.0
PREFECT_SERVER_API_PORT=4200

# Notion Configuration
NOTION_TOKEN=ntn_your_production_token
NOTION_EMAIL_SEQUENCE_DB_ID=your_email_sequence_db_id
NOTION_BUSINESSX_DB_ID=your_businessx_canada_db_id

# Resend Configuration
RESEND_API_KEY=re_your_production_api_key

# Discord Configuration (optional)
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your_webhook

# Application Configuration
TESTING_MODE=false  # IMPORTANT: Production delays (11 days)
API_HOST=0.0.0.0
API_PORT=8000

# Cal.com Configuration (optional)
CALCOM_WEBHOOK_SECRET=your_calcom_secret
EOF

# Secure .env file
chmod 600 /opt/christmas-campaign/.env
```

---

## Phase 3: Systemd Service Configuration

### Step 3.1: Prefect Server Service

```bash
# Create service file
sudo nano /etc/systemd/system/prefect-server.service
```

**Content**:
```ini
[Unit]
Description=Prefect Server
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/christmas-campaign
Environment="PATH=/opt/christmas-campaign/venv/bin"
EnvironmentFile=/opt/christmas-campaign/.env
ExecStart=/opt/christmas-campaign/venv/bin/prefect server start --host 0.0.0.0 --port 4200
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Step 3.2: Prefect Worker Service

```bash
# Create service file
sudo nano /etc/systemd/system/prefect-worker.service
```

**Content**:
```ini
[Unit]
Description=Prefect Worker
After=network.target prefect-server.service
Wants=prefect-server.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/christmas-campaign
Environment="PATH=/opt/christmas-campaign/venv/bin"
EnvironmentFile=/opt/christmas-campaign/.env
ExecStart=/opt/christmas-campaign/venv/bin/prefect worker start --pool default
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Step 3.3: FastAPI Webhook Service

```bash
# Create service file
sudo nano /etc/systemd/system/christmas-webhook.service
```

**Content**:
```ini
[Unit]
Description=Christmas Campaign Webhook Server
After=network.target prefect-server.service
Wants=prefect-server.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/christmas-campaign
Environment="PATH=/opt/christmas-campaign/venv/bin"
EnvironmentFile=/opt/christmas-campaign/.env
ExecStart=/opt/christmas-campaign/venv/bin/uvicorn server:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Step 3.4: Enable and Start Services

```bash
# Reload systemd daemon
sudo systemctl daemon-reload

# Enable services (start on boot)
sudo systemctl enable prefect-server
sudo systemctl enable prefect-worker
sudo systemctl enable christmas-webhook

# Start services
sudo systemctl start prefect-server
sudo systemctl start prefect-worker
sudo systemctl start christmas-webhook

# Check status
sudo systemctl status prefect-server
sudo systemctl status prefect-worker
sudo systemctl status christmas-webhook
```

---

## Phase 4: Nginx Reverse Proxy Configuration

### Step 4.1: Obtain Domain and SSL Certificate

**Prerequisite**: Point your domain to server IP:
```
webhook.yourdomain.com → Your Homelab IP
```

**Obtain SSL Certificate**:
```bash
# Stop nginx if running
sudo systemctl stop nginx

# Obtain certificate
sudo certbot certonly --standalone -d webhook.yourdomain.com

# Certificate will be at:
# /etc/letsencrypt/live/webhook.yourdomain.com/fullchain.pem
# /etc/letsencrypt/live/webhook.yourdomain.com/privkey.pem
```

### Step 4.2: Configure Nginx

```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/christmas-webhook
```

**Content**:
```nginx
# Webhook API (Port 8000)
server {
    listen 80;
    listen [::]:80;
    server_name webhook.yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name webhook.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/webhook.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/webhook.yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Logging
    access_log /var/log/nginx/webhook-access.log;
    error_log /var/log/nginx/webhook-error.log;

    # Webhook endpoints
    location /webhook/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 60s;
        proxy_connect_timeout 60s;
    }

    # Health check
    location /health {
        proxy_pass http://localhost:8000/health;
        access_log off;
    }
}

# Prefect UI (Port 4200) - Optional, can be internal only
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name prefect.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/webhook.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/webhook.yourdomain.com/privkey.pem;

    # Basic Auth (optional security)
    auth_basic "Restricted Access";
    auth_basic_user_file /etc/nginx/.htpasswd;

    location / {
        proxy_pass http://localhost:4200;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support for Prefect UI
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Step 4.3: Enable Nginx Configuration

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/christmas-webhook /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### Step 4.4: Configure Auto-Renewal

```bash
# Test renewal
sudo certbot renew --dry-run

# Certbot will auto-renew via cron/systemd timer
# Verify: systemctl list-timers | grep certbot
```

---

## Phase 5: Deploy Prefect Flows

### Step 5.1: Create Deployment Script

```bash
# Create deployment script
nano /opt/christmas-campaign/deploy_production.py
```

**Content**:
```python
"""
Production deployment script for Christmas Campaign flows.
"""
from prefect.deployments import Deployment
from prefect.server.schemas.schedules import CronSchedule
from campaigns.christmas_campaign.flows.send_email_flow import send_email_flow

def deploy_email_flow():
    """Deploy send_email_flow for production."""
    deployment = Deployment.build_from_flow(
        flow=send_email_flow,
        name="christmas-send-email",
        work_pool_name="default",
        work_queue_name="default",
        version="1.0.0",
        description="Send individual Christmas campaign emails (triggered programmatically)",
        tags=["christmas-2025", "email", "production"],
    )

    deployment_id = deployment.apply()
    print(f"✅ Deployed send_email_flow: {deployment_id}")

    return deployment_id

if __name__ == "__main__":
    print("🚀 Deploying Christmas Campaign flows to production...")
    print()

    # Deploy email sending flow
    email_deployment_id = deploy_email_flow()

    print()
    print("✅ All deployments complete!")
    print()
    print("Next steps:")
    print("1. Verify deployments in Prefect UI: https://prefect.yourdomain.com")
    print("2. Test webhook endpoint: https://webhook.yourdomain.com/webhook/christmas-signup")
    print("3. Update website PREFECT_WEBHOOK_URL to production URL")
```

### Step 5.2: Run Deployment

```bash
cd /opt/christmas-campaign
source venv/bin/activate

# Run deployment script
python deploy_production.py
```

---

## Phase 6: Website Configuration

### Step 6.1: Update Website Environment

**Vercel/Netlify**:
```bash
# Set production webhook URL
vercel env add PREFECT_WEBHOOK_URL production
# Enter: https://webhook.yourdomain.com/webhook/christmas-signup

# Redeploy website
vercel --prod
```

**Or manually in Vercel Dashboard**:
1. Go to Project Settings → Environment Variables
2. Add: `PREFECT_WEBHOOK_URL` = `https://webhook.yourdomain.com/webhook/christmas-signup`
3. Redeploy

### Step 6.2: Test Production Webhook

```bash
# Test from command line
curl -X POST https://webhook.yourdomain.com/webhook/christmas-signup \
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
```

**Expected Response**:
```json
{
  "status": "success",
  "message": "Christmas signup processed successfully",
  "data": {
    "email": "production-test@example.com",
    "segment": "URGENT",
    "sequence_id": "notion-page-id",
    "scheduled_emails": 7
  }
}
```

---

## Phase 7: Monitoring and Logging

### Step 7.1: Configure Log Rotation

```bash
# Create logrotate configuration
sudo nano /etc/logrotate.d/christmas-campaign
```

**Content**:
```
/var/log/nginx/webhook-*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data adm
    sharedscripts
    postrotate
        systemctl reload nginx > /dev/null 2>&1
    endscript
}
```

### Step 7.2: Monitor Services

**View logs**:
```bash
# Prefect server logs
sudo journalctl -u prefect-server -f

# Prefect worker logs
sudo journalctl -u prefect-worker -f

# Webhook server logs
sudo journalctl -u christmas-webhook -f

# Nginx access logs
sudo tail -f /var/log/nginx/webhook-access.log

# Nginx error logs
sudo tail -f /var/log/nginx/webhook-error.log
```

### Step 7.3: Health Check Script

```bash
# Create health check script
nano /opt/christmas-campaign/health_check.sh
```

**Content**:
```bash
#!/bin/bash

echo "🏥 Christmas Campaign Health Check"
echo "==================================="
echo ""

# Check services
echo "Service Status:"
systemctl is-active prefect-server && echo "  ✅ Prefect Server" || echo "  ❌ Prefect Server"
systemctl is-active prefect-worker && echo "  ✅ Prefect Worker" || echo "  ❌ Prefect Worker"
systemctl is-active christmas-webhook && echo "  ✅ Webhook Server" || echo "  ❌ Webhook Server"
systemctl is-active nginx && echo "  ✅ Nginx" || echo "  ❌ Nginx"
systemctl is-active postgresql && echo "  ✅ PostgreSQL" || echo "  ❌ PostgreSQL"

echo ""

# Check endpoints
echo "Endpoint Health:"
curl -sf http://localhost:8000/health >/dev/null && echo "  ✅ Webhook API" || echo "  ❌ Webhook API"
curl -sf http://localhost:4200/api/health >/dev/null && echo "  ✅ Prefect UI" || echo "  ❌ Prefect UI"

echo ""

# Check disk space
echo "Disk Usage:"
df -h / | tail -1 | awk '{print "  Root: " $3 " / " $2 " (" $5 " used)"}'

echo ""

# Check memory
echo "Memory Usage:"
free -h | grep Mem | awk '{print "  " $3 " / " $2 " used"}'
```

```bash
# Make executable
chmod +x /opt/christmas-campaign/health_check.sh

# Run health check
./health_check.sh
```

---

## Phase 8: Production Validation

### Step 8.1: End-to-End Production Test

**Test complete flow**:
1. Go to website: https://yourdomain.com/en/flows/businessX/dfu/xmas-a01/signup
2. Complete signup with test email
3. Complete assessment
4. Verify webhook call succeeds (check Nginx logs)
5. Verify Prefect UI shows scheduled flows
6. Verify Notion Email Sequence DB updated
7. Wait for first email (~1 hour if TESTING_MODE=false, or set to true for fast test)
8. Verify email received in inbox
9. Verify "Email 1 Sent" timestamp in Notion

### Step 8.2: Load Testing (Optional)

```bash
# Install Apache Bench
sudo apt install apache2-utils -y

# Test 100 requests, 10 concurrent
ab -n 100 -c 10 -T application/json -p test_payload.json https://webhook.yourdomain.com/webhook/christmas-signup
```

---

## Maintenance and Operations

### Daily Operations

**Check service health**:
```bash
./health_check.sh
```

**View recent flow runs**:
- Open Prefect UI: https://prefect.yourdomain.com
- Check "Flow Runs" tab
- Filter by "Completed" / "Failed"

**Monitor Notion**:
- Email Sequence DB: Check recent entries
- BusinessX Canada DB: Verify contact updates

**Monitor Resend**:
- Dashboard: https://resend.com/emails
- Check send success rate
- Monitor bounce/complaint rates

### Troubleshooting

**Service won't start**:
```bash
# Check logs
sudo journalctl -u [service-name] -n 50

# Check permissions
ls -la /opt/christmas-campaign

# Check environment
sudo cat /opt/christmas-campaign/.env
```

**Webhook timeouts**:
```bash
# Check worker status
sudo systemctl status prefect-worker

# Increase Nginx timeout
# Edit /etc/nginx/sites-available/christmas-webhook
# proxy_read_timeout 120s;
```

**Email not sending**:
```bash
# Check Resend API key
curl https://api.resend.com/domains -H "Authorization: Bearer $RESEND_API_KEY"

# Check Notion access
# Verify NOTION_TOKEN permissions
```

---

## Rollback Procedure

**If production deployment fails**:

1. **Stop new services**:
   ```bash
   sudo systemctl stop christmas-webhook
   sudo systemctl stop prefect-worker
   sudo systemctl stop prefect-server
   ```

2. **Restore previous configuration** (if applicable):
   ```bash
   cd /opt/christmas-campaign
   git checkout [previous-commit]
   sudo systemctl restart christmas-webhook
   ```

3. **Update website to old webhook** (if needed):
   ```bash
   # Point back to staging/old endpoint
   vercel env add PREFECT_WEBHOOK_URL production
   # Enter old URL
   vercel --prod
   ```

---

## Success Criteria

Production deployment is **COMPLETE** when:

- [ ] ✅ All systemd services running and healthy
- [ ] ✅ Nginx reverse proxy configured with SSL
- [ ] ✅ Prefect flows deployed successfully
- [ ] ✅ Website updated with production webhook URL
- [ ] ✅ End-to-end production test passes
- [ ] ✅ First real email sends successfully
- [ ] ✅ Monitoring and logging configured
- [ ] ✅ Health check script operational

---

## Production Checklist

Use this checklist to track deployment progress:

- [ ] Server preparation (updates, Python, PostgreSQL, firewall)
- [ ] Application deployment (clone repo, venv, dependencies)
- [ ] Environment configuration (.env with production values)
- [ ] Systemd services (create, enable, start)
- [ ] Nginx configuration (reverse proxy, SSL)
- [ ] Prefect flow deployment (run deploy script)
- [ ] Website configuration (update PREFECT_WEBHOOK_URL)
- [ ] Production validation (E2E test)
- [ ] Monitoring setup (logs, health checks)
- [ ] Documentation review (this file)

---

**Deployment Date**: TBD
**Deployed By**: TBD
**Status**: 📋 Ready for execution
