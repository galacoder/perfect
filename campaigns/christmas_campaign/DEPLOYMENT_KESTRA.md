# Christmas Campaign - Kestra Deployment Guide

**Last Updated**: 2025-11-30
**Status**: Production Ready
**Environment**: Self-Hosted Kestra + PostgreSQL (Docker Compose)

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Production Deployment](#production-deployment)
4. [Secret Management](#secret-management)
5. [Flow Deployment](#flow-deployment)
6. [Monitoring & Logging](#monitoring--logging)
7. [Backup & Recovery](#backup--recovery)
8. [Troubleshooting](#troubleshooting)
9. [Operational Procedures](#operational-procedures)

---

## Prerequisites

### System Requirements

**Local Development**:
- Docker 20.10+
- Docker Compose 2.0+
- 2GB RAM minimum
- 10GB disk space

**Production Homelab**:
- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum (8GB recommended)
- 50GB disk space (for PostgreSQL data + logs)
- Persistent storage for database volumes

### Required Secrets

Gather these values before deployment:
- [ ] Notion API token (`NOTION_TOKEN`)
- [ ] Notion Contacts database ID (`NOTION_CONTACTS_DB_ID`)
- [ ] Notion Email Templates database ID (`NOTION_TEMPLATES_DB_ID`)
- [ ] Resend API key (`RESEND_API_KEY`)
- [ ] Testing mode flag (`TESTING_MODE` - `true` or `false`)

---

## Local Development Setup

### Step 1: Clone Repository

```bash
cd /path/to/perfect
git pull origin main
```

### Step 2: Create Environment File

```bash
# Copy example file
cp .env.kestra.example .env.kestra

# Edit with your secrets
nano .env.kestra
```

**Required format** (`.env.kestra`):
```bash
# Notion credentials (base64 encoded)
SECRET_NOTION_TOKEN=<base64_encoded_token>
SECRET_NOTION_CONTACTS_DB_ID=<base64_encoded_db_id>
SECRET_NOTION_TEMPLATES_DB_ID=<base64_encoded_db_id>

# Resend credentials (base64 encoded)
SECRET_RESEND_API_KEY=<base64_encoded_api_key>

# Testing mode (true = fast timing, false = production timing)
SECRET_TESTING_MODE=true

# PostgreSQL (for local dev)
POSTGRES_USER=kestra
POSTGRES_PASSWORD=k3str4
POSTGRES_DB=kestra
```

### Step 3: Base64 Encode Secrets

```bash
# Helper script to encode secrets
echo -n "your_secret_value_here" | base64
```

**Example**:
```bash
# Encode Notion token
echo -n "ntn_123456789abcdef" | base64
# Output: bnRuXzEyMzQ1Njc4OWFiY2RlZg==

# Add to .env.kestra
echo "SECRET_NOTION_TOKEN=bnRuXzEyMzQ1Njc4OWFiY2RlZg==" >> .env.kestra
```

### Step 4: Start Kestra

```bash
# Start Kestra + PostgreSQL
docker-compose -f docker-compose.kestra.yml up -d

# Check logs
docker-compose -f docker-compose.kestra.yml logs -f kestra

# Wait for "Kestra server started" message
```

### Step 5: Verify Installation

```bash
# Check containers running
docker-compose -f docker-compose.kestra.yml ps

# Should show:
# - kestra (port 8080)
# - postgres (port 5432)

# Open Kestra UI
open http://localhost:8080
```

### Step 6: Deploy Flows

**Option A: Via UI** (Recommended for development)

1. Open http://localhost:8080
2. Navigate to **Flows** tab
3. Click **Create Flow**
4. Copy/paste YAML from `kestra/flows/christmas/handlers/*.yml`
5. Click **Save**

**Option B: Via API**

```bash
# Deploy all flows at once
for flow in kestra/flows/christmas/handlers/*.yml; do
  curl -X PUT http://localhost:8080/api/v1/flows \
    -H "Content-Type: application/x-yaml" \
    --data-binary @$flow
done

# Deploy send-email flow
curl -X PUT http://localhost:8080/api/v1/flows \
  -H "Content-Type: application/x-yaml" \
  --data-binary @kestra/flows/christmas/send-email.yml

# Deploy schedule flow
curl -X PUT http://localhost:8080/api/v1/flows \
  -H "Content-Type: application/x-yaml" \
  --data-binary @kestra/flows/christmas/schedule-email-sequence.yml
```

### Step 7: Test Webhook

```bash
# Test signup handler
curl -X POST http://localhost:8080/api/v1/executions/webhook/christmas/handlers/signup-handler/signup-webhook-key \
  -H "Content-Type: application/json" \
  -d '{
    "email": "lengobaosang@gmail.com",
    "first_name": "Test",
    "business_name": "Test Corp"
  }'

# Expected: 200 OK + execution ID
```

---

## Production Deployment

### Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     Homelab Server                       │
│                                                           │
│  ┌────────────────────────────────────────────────────┐  │
│  │         Docker Compose Stack                       │  │
│  │                                                     │  │
│  │  ┌──────────────┐         ┌──────────────────┐    │  │
│  │  │   Kestra     │◄───────►│   PostgreSQL     │    │  │
│  │  │   (8080)     │         │   (persistent)   │    │  │
│  │  └──────┬───────┘         └──────────────────┘    │  │
│  │         │                                          │  │
│  │         │ Webhooks                                 │  │
│  └─────────┼──────────────────────────────────────────┘  │
│            │                                              │
└────────────┼──────────────────────────────────────────────┘
             │
             │ HTTPS (via reverse proxy)
             │
     ┌───────▼────────┐
     │   Website      │
     │  (Next.js)     │
     └────────────────┘
```

### Step 1: Prepare Production Server

```bash
# SSH into homelab server
ssh user@homelab.local

# Create project directory
mkdir -p /opt/kestra/christmas-campaign
cd /opt/kestra/christmas-campaign

# Clone repository
git clone https://github.com/galacoder/perfect.git .
```

### Step 2: Create Production Environment File

```bash
# Copy example
cp .env.kestra.example .env.kestra.prod

# Edit with production secrets
nano .env.kestra.prod
```

**Production `.env.kestra.prod`**:
```bash
# Notion credentials (base64 encoded)
SECRET_NOTION_TOKEN=<base64_encoded_production_token>
SECRET_NOTION_CONTACTS_DB_ID=<base64_encoded_production_db_id>
SECRET_NOTION_TEMPLATES_DB_ID=<base64_encoded_production_db_id>

# Resend credentials (base64 encoded)
SECRET_RESEND_API_KEY=<base64_encoded_production_api_key>

# ⚠️ CRITICAL: Production timing (NOT testing mode!)
SECRET_TESTING_MODE=false

# PostgreSQL (production)
POSTGRES_USER=kestra_prod
POSTGRES_PASSWORD=<strong_password_here>
POSTGRES_DB=kestra_prod

# Kestra configuration
KESTRA_CONFIGURATION_PATH=/app/kestra/configuration.yaml
KESTRA_DATABASE_TYPE=postgres
```

### Step 3: Create Production Docker Compose

**File**: `docker-compose.kestra.prod.yml`

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    container_name: kestra_postgres_prod
    restart: always
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data_prod:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - kestra_network

  kestra:
    image: kestra/kestra:latest
    container_name: kestra_prod
    restart: always
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      # Load secrets from .env file
      SECRET_NOTION_TOKEN: ${SECRET_NOTION_TOKEN}
      SECRET_NOTION_CONTACTS_DB_ID: ${SECRET_NOTION_CONTACTS_DB_ID}
      SECRET_NOTION_TEMPLATES_DB_ID: ${SECRET_NOTION_TEMPLATES_DB_ID}
      SECRET_RESEND_API_KEY: ${SECRET_RESEND_API_KEY}
      SECRET_TESTING_MODE: ${SECRET_TESTING_MODE}

      # Kestra database configuration
      KESTRA_DATABASE_TYPE: postgres
      KESTRA_DATABASE_URL: jdbc:postgresql://postgres:5432/${POSTGRES_DB}
      KESTRA_DATABASE_USERNAME: ${POSTGRES_USER}
      KESTRA_DATABASE_PASSWORD: ${POSTGRES_PASSWORD}

      # Kestra server configuration
      KESTRA_SERVER_BASIC_AUTH_ENABLED: false
      MICRONAUT_SERVER_PORT: 8080
    ports:
      - "8080:8080"
    volumes:
      - kestra_data_prod:/app/storage
      - kestra_logs_prod:/app/logs
      - ./kestra/flows:/app/flows:ro
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    networks:
      - kestra_network
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

volumes:
  postgres_data_prod:
    driver: local
  kestra_data_prod:
    driver: local
  kestra_logs_prod:
    driver: local

networks:
  kestra_network:
    driver: bridge
```

### Step 4: Start Production Stack

```bash
# Load environment variables
export $(cat .env.kestra.prod | xargs)

# Start stack
docker-compose -f docker-compose.kestra.prod.yml up -d

# Check logs
docker-compose -f docker-compose.kestra.prod.yml logs -f

# Wait for "Kestra server started"
```

### Step 5: Configure Reverse Proxy (Optional)

**Nginx Configuration** (if using Nginx as reverse proxy):

```nginx
# /etc/nginx/sites-available/kestra.conf

server {
    listen 80;
    server_name kestra.homelab.local;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support for Kestra UI
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/kestra.conf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Step 6: Deploy Flows (Production)

```bash
# Deploy all flows via API
for flow in kestra/flows/christmas/handlers/*.yml; do
  curl -X PUT http://localhost:8080/api/v1/flows \
    -H "Content-Type: application/x-yaml" \
    --data-binary @$flow
done

# Verify flows deployed
curl http://localhost:8080/api/v1/flows | jq '.[] | {id, namespace}'
```

### Step 7: Production Smoke Test

```bash
# Test assessment handler with real email
EMAIL_1_SENT_AT=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

curl -X POST http://localhost:8080/api/v1/executions/webhook/christmas/handlers/assessment-handler/assessment-webhook-key \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"lengobaosang@gmail.com\",
    \"first_name\": \"Production\",
    \"business_name\": \"Test Business\",
    \"red_systems\": 2,
    \"orange_systems\": 1,
    \"yellow_systems\": 2,
    \"green_systems\": 3,
    \"weakest_system_1\": \"GPS\",
    \"revenue_leak_total\": 14700,
    \"email_1_sent_at\": \"$EMAIL_1_SENT_AT\",
    \"email_1_status\": \"sent\"
  }"

# Expected: Emails #2-5 scheduled in production timing (24h, 72h, 96h, 120h)
```

---

## Secret Management

### Encoding Secrets

**Manual Encoding**:
```bash
echo -n "your_secret_value" | base64
```

**Automated Script** (`scripts/encode_secrets.sh`):
```bash
#!/bin/bash
# Encode all secrets for Kestra

set -a && source .env && set +a

echo "SECRET_NOTION_TOKEN=$(echo -n \"$NOTION_TOKEN\" | base64)"
echo "SECRET_NOTION_CONTACTS_DB_ID=$(echo -n \"$NOTION_CONTACTS_DB_ID\" | base64)"
echo "SECRET_NOTION_TEMPLATES_DB_ID=$(echo -n \"$NOTION_TEMPLATES_DB_ID\" | base64)"
echo "SECRET_RESEND_API_KEY=$(echo -n \"$RESEND_API_KEY\" | base64)"
```

### Rotating Secrets

```bash
# 1. Encode new secret
NEW_SECRET=$(echo -n "new_value" | base64)

# 2. Update .env.kestra.prod
nano .env.kestra.prod
# Update: SECRET_NOTION_TOKEN=<new_base64_value>

# 3. Restart Kestra
docker-compose -f docker-compose.kestra.prod.yml restart kestra

# 4. Verify flows can access new secret
curl -X POST http://localhost:8080/api/v1/executions/webhook/...
```

---

## Flow Deployment

### Deployment Methods

**Method 1: UI Upload** (Simple)
1. Open http://localhost:8080
2. Flows → Create Flow
3. Paste YAML
4. Save

**Method 2: API Upload** (Automated)
```bash
curl -X PUT http://localhost:8080/api/v1/flows \
  -H "Content-Type: application/x-yaml" \
  --data-binary @kestra/flows/christmas/handlers/assessment-handler.yml
```

**Method 3: Git Sync** (Advanced - Future)
- Kestra can sync flows from Git repository
- Auto-deploy on git push
- Not implemented yet for this project

### Flow Validation

```bash
# Validate YAML syntax before deployment
python3 -c "import yaml; yaml.safe_load(open('kestra/flows/christmas/handlers/assessment-handler.yml'))"

# Or use yq
yq eval '.' kestra/flows/christmas/handlers/assessment-handler.yml > /dev/null
```

### Flow Versioning

**Best Practice**: Tag flows with version numbers in description

```yaml
id: christmas-assessment-handler
namespace: christmas.handlers
description: "Assessment handler - Emails #2-5 only (v1.0.0 - Nov 2025)"
```

---

## Monitoring & Logging

### Kestra UI Dashboard

**URL**: `http://localhost:8080` (local) or `http://kestra.homelab.local` (production)

**Key Metrics**:
- **Executions**: View all flow runs
- **Logs**: Real-time execution logs
- **Triggers**: Monitor webhook activity
- **Failures**: Track failed executions

### Log Locations

**Kestra Application Logs**:
```bash
# Docker logs
docker-compose -f docker-compose.kestra.prod.yml logs -f kestra

# Persistent logs (volume)
docker exec -it kestra_prod cat /app/logs/kestra.log
```

**PostgreSQL Logs**:
```bash
docker-compose -f docker-compose.kestra.prod.yml logs -f postgres
```

### Execution Logs API

```bash
# List recent executions
curl http://localhost:8080/api/v1/executions | jq '.results[] | {id, state, flowId}'

# Get specific execution logs
curl http://localhost:8080/api/v1/executions/{execution-id}/logs | jq '.[]'
```

### Setting Up Alerts

**Future Implementation**: Kestra supports webhooks on flow failures

```yaml
# In flow definition
on-failure:
  - id: send_alert
    type: io.kestra.plugin.core.http.Request
    uri: "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
    method: POST
    body: |
      {
        "text": "Flow {{ flow.id }} failed: {{ outputs }}"
      }
```

---

## Backup & Recovery

### Database Backup

**Automated Daily Backup** (cron job):

```bash
# /etc/cron.daily/kestra-backup.sh

#!/bin/bash
BACKUP_DIR="/backups/kestra"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup PostgreSQL database
docker exec kestra_postgres_prod pg_dump -U kestra_prod kestra_prod | gzip > "$BACKUP_DIR/kestra_db_$DATE.sql.gz"

# Keep last 30 days
find $BACKUP_DIR -name "kestra_db_*.sql.gz" -mtime +30 -delete

echo "Backup completed: kestra_db_$DATE.sql.gz"
```

**Manual Backup**:
```bash
docker exec kestra_postgres_prod pg_dump -U kestra_prod kestra_prod > kestra_backup.sql
```

### Database Restore

```bash
# Stop Kestra
docker-compose -f docker-compose.kestra.prod.yml stop kestra

# Restore database
cat kestra_backup.sql | docker exec -i kestra_postgres_prod psql -U kestra_prod kestra_prod

# Restart Kestra
docker-compose -f docker-compose.kestra.prod.yml start kestra
```

### Flow Backup

**Flows are code** - stored in Git repository!

```bash
# Flows are in version control
git add kestra/flows/
git commit -m "Update assessment handler flow"
git push
```

**Export All Flows via API**:
```bash
# Export all flows
curl http://localhost:8080/api/v1/flows > flows_backup_$(date +%Y%m%d).json
```

---

## Troubleshooting

### Issue 1: Kestra Won't Start

**Symptoms**: Container exits immediately

**Debug**:
```bash
docker-compose -f docker-compose.kestra.prod.yml logs kestra
```

**Common Causes**:
1. **PostgreSQL not ready**: Increase healthcheck retries
2. **Invalid secrets**: Check base64 encoding
3. **Port conflict**: Port 8080 already in use

**Fix**:
```bash
# Check port
sudo lsof -i :8080

# Check PostgreSQL connection
docker exec -it kestra_postgres_prod psql -U kestra_prod -c "SELECT 1"
```

### Issue 2: Webhooks Return 404

**Symptoms**: `curl` returns 404 Not Found

**Debug**:
```bash
# List all flows
curl http://localhost:8080/api/v1/flows | jq '.[] | {id, namespace}'

# Check flow exists
curl http://localhost:8080/api/v1/flows/christmas.handlers/assessment-handler
```

**Fix**: Verify webhook URL format:
```
http://localhost:8080/api/v1/executions/webhook/{namespace}/{flowId}/{webhook-key}
```

### Issue 3: Secrets Not Found

**Symptoms**: Flow fails with "secret 'SECRET_NOTION_TOKEN' not found"

**Debug**:
```bash
# Check environment variables loaded
docker exec -it kestra_prod env | grep SECRET_

# Should show all SECRET_* variables
```

**Fix**: Restart Kestra after updating `.env.kestra.prod`
```bash
docker-compose -f docker-compose.kestra.prod.yml restart kestra
```

### Issue 4: Emails Not Sending

**Symptoms**: Flow completes but no emails arrive

**Debug**:
1. Check Kestra execution logs
2. Check Resend dashboard
3. Verify Resend API key valid

```bash
# Test Resend API key manually
curl -X POST https://api.resend.com/emails \
  -H "Authorization: Bearer $(echo $SECRET_RESEND_API_KEY | base64 -d)" \
  -H "Content-Type: application/json" \
  -d '{
    "from": "test@sangletech.com",
    "to": "lengobaosang@gmail.com",
    "subject": "Test",
    "html": "<p>Test email</p>"
  }'
```

---

## Operational Procedures

### Starting/Stopping Kestra

**Development**:
```bash
# Start
docker-compose -f docker-compose.kestra.yml up -d

# Stop
docker-compose -f docker-compose.kestra.yml down

# Restart
docker-compose -f docker-compose.kestra.yml restart
```

**Production**:
```bash
# Start
docker-compose -f docker-compose.kestra.prod.yml up -d

# Stop (graceful)
docker-compose -f docker-compose.kestra.prod.yml stop

# Restart
docker-compose -f docker-compose.kestra.prod.yml restart
```

### Updating Kestra Version

```bash
# Pull latest image
docker-compose -f docker-compose.kestra.prod.yml pull

# Restart with new image
docker-compose -f docker-compose.kestra.prod.yml up -d

# Check version
curl http://localhost:8080/api/v1/configs/version
```

### Switching Between Testing and Production Mode

**Development → Production**:
```bash
# 1. Update .env.kestra.prod
nano .env.kestra.prod
# Change: SECRET_TESTING_MODE=false

# 2. Restart Kestra
docker-compose -f docker-compose.kestra.prod.yml restart kestra

# 3. Verify timing in next execution
# Email #2 should be scheduled 24h after Email #1 (not 1 minute)
```

**Production → Development** (for testing):
```bash
# Change: SECRET_TESTING_MODE=true
docker-compose -f docker-compose.kestra.prod.yml restart kestra
```

### Updating Flows

```bash
# 1. Edit flow YAML
nano kestra/flows/christmas/handlers/assessment-handler.yml

# 2. Validate syntax
yq eval '.' kestra/flows/christmas/handlers/assessment-handler.yml > /dev/null

# 3. Deploy update
curl -X PUT http://localhost:8080/api/v1/flows \
  -H "Content-Type: application/x-yaml" \
  --data-binary @kestra/flows/christmas/handlers/assessment-handler.yml

# 4. Verify update
curl http://localhost:8080/api/v1/flows/christmas.handlers/assessment-handler | jq '.revision'
```

### Health Checks

**Kestra Health**:
```bash
curl http://localhost:8080/health

# Expected: {"status":"UP"}
```

**PostgreSQL Health**:
```bash
docker exec kestra_postgres_prod pg_isready -U kestra_prod

# Expected: "accepting connections"
```

**Full Stack Health**:
```bash
docker-compose -f docker-compose.kestra.prod.yml ps

# Expected: All services "Up" and healthy
```

---

## Production Checklist

### Pre-Deployment

- [ ] All secrets base64 encoded
- [ ] `.env.kestra.prod` created with production values
- [ ] `SECRET_TESTING_MODE=false` for production timing
- [ ] PostgreSQL password is strong
- [ ] Persistent volumes configured
- [ ] Backup script configured (cron job)
- [ ] All flows validated (YAML syntax)

### Deployment

- [ ] Docker Compose stack started
- [ ] Kestra UI accessible
- [ ] All flows deployed (5 handlers + send-email + schedule)
- [ ] Webhooks tested with curl
- [ ] Test email sent successfully
- [ ] Notion databases accessible from Kestra
- [ ] Resend API working

### Post-Deployment

- [ ] Monitor first 10 executions
- [ ] Check Notion Sequence Tracker updates
- [ ] Verify email timing correct (24h, not 1min)
- [ ] Set up daily database backup
- [ ] Configure monitoring alerts (future)
- [ ] Document production webhook URLs for website team
- [ ] Test rollback procedure

---

## Support

**Questions?**
- See `KESTRA_MIGRATION.md` for migration details
- See `ARCHITECTURE.md` for system architecture
- See `WEBSITE_INTEGRATION_KESTRA.md` for webhook integration

**Kestra Documentation**: https://kestra.io/docs

**Contact**: sang@sanglescalinglabs.com

---

**Last Updated**: 2025-11-30
**Deployment Status**: Production Ready
**Next Review**: 2026-01-01 (post-campaign analysis)
