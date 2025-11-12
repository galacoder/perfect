# BusOS Email Sequence - Deployment Guide

Complete deployment guide for the Prefect-based email nurture sequence system.

---

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Seeding Email Templates](#seeding-email-templates)
- [Testing](#testing)
- [Deployment Options](#deployment-options)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)

---

## Overview

This system replaces the n8n workflow with a Prefect v3-based solution that provides:

- **3 Prefect Flows**: signup_handler, assessment_handler, email_sequence
- **FastAPI Webhook Server**: Frontend integration via REST API
- **Dynamic Email Templates**: Edit templates in Notion without code changes
- **Testing Mode**: Fast validation (1-4min waits) vs Production (24-48hr waits)
- **Segment-Based Routing**: CRITICAL/URGENT/OPTIMIZE classification

**Architecture**:
```
Frontend → FastAPI Webhooks → Prefect Flows → Notion DB + Resend API
```

---

## Prerequisites

### Required

- **Python 3.11+**
- **Notion Account** with:
  - Contacts Database (existing from n8n)
  - Templates Database (existing from n8n)
  - Integration token with read/write access
- **Resend Account** with API key
- **Git** for version control

### Optional

- **Discord Webhook** for hot lead notifications (CRITICAL segment)
- **Prefect Cloud** account for production orchestration
- **Docker** for containerized deployment

---

## Installation

### 1. Clone Repository

```bash
git clone <repository-url>
cd perfect
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**requirements.txt**:
```
prefect==3.4.1
notion-client==2.2.1
httpx==0.27.2
python-dotenv==1.0.1
fastapi==0.115.6
uvicorn[standard]==0.34.0
pydantic[email]==2.10.4
pytest==8.3.4
pytest-mock==3.14.0
```

### 4. Verify Installation

```bash
python test_flows_dry_run.py
```

Expected output: All 7 test categories pass ✅

---

## Configuration

### 1. Create `.env` File

```bash
cp .env.example .env
```

### 2. Configure Environment Variables

**Required Variables**:

```bash
# Notion Configuration
NOTION_TOKEN=ntn_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
NOTION_CONTACTS_DB_ID=576de1aa-6064-4201-a5e6-623b7f2be79a
NOTION_TEMPLATES_DB_ID=2a87c374-1115-8116-a0c8-f902107e9830

# Resend API
RESEND_API_KEY=re_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Testing vs Production
TESTING_MODE=false  # true = 1-4min waits, false = 24-48hr waits
```

**Optional Variables**:

```bash
# Discord Notifications (for hot leads)
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/xxxxx

# API Server Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

### 3. Verify Configuration

```bash
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('✅ NOTION_TOKEN:', 'Set' if os.getenv('NOTION_TOKEN') else 'Missing')"
```

---

## Seeding Email Templates

The system uses **dynamic email templates** stored in Notion. You need to seed them once.

### 1. Run Seeding Script

```bash
python scripts/seed_templates.py
```

Expected output:
```
🌱 Seeding Email Templates to Notion...
✅ Created template 'email_1' in Notion (page_id: xxx)
✅ Created template 'email_2a_critical' in Notion (page_id: xxx)
...
🎉 Seeded 9 templates to Notion
```

### 2. Verify in Notion

Open your Notion Templates Database and confirm:
- 9 templates exist
- All have `Active` checkbox checked
- Subject and HTML Body fields populated

### 3. Edit Templates (Optional)

You can now edit email copy directly in Notion:
1. Open template page in Notion
2. Edit Subject or HTML Body
3. Changes take effect immediately (no code deployment)
4. Use `{{variable}}` placeholders for personalization

**Available Variables**:
- `{{first_name}}` - Contact's first name
- `{{business_name}}` - Contact's business name
- `{{email}}` - Contact's email

---

## Testing

### 1. Run Unit Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_notion_operations.py -v

# Run with coverage
pytest tests/ --cov=tasks --cov=flows --cov-report=html
```

**Expected**: 93 tests pass ✅

### 2. Run Dry-Run Validation

```bash
python test_flows_dry_run.py
```

Tests flow structure without external API calls.

### 3. Run Integration Tests

```bash
# Mocked APIs (fast, safe)
python test_integration_e2e.py --mode mock

# Real APIs (caution: creates Notion records)
python test_integration_e2e.py --mode real
```

### 4. Test Webhook Server

```bash
# Start server in testing mode
TESTING_MODE=true uvicorn server:app --reload

# In another terminal, test endpoints
curl -X GET http://localhost:8000/health

curl -X POST http://localhost:8000/webhook/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "name": "Test User",
    "first_name": "Test",
    "business_name": "Test Business"
  }'

curl -X POST http://localhost:8000/webhook/assessment \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "red_systems": 2,
    "orange_systems": 1,
    "yellow_systems": 2,
    "green_systems": 3,
    "assessment_score": 65
  }'
```

---

## Deployment Options

### Option 1: Local Development

**Best for**: Testing and development

```bash
# Start webhook server
uvicorn server:app --reload --port 8000

# Flows run automatically when webhooks are triggered
```

### Option 2: Production Server (Recommended)

**Best for**: Production with Prefect Cloud

#### A. Start Webhook Server

```bash
# Production mode (4 workers, no reload)
uvicorn server:app --host 0.0.0.0 --port 8000 --workers 4
```

Or use **systemd** service:

**`/etc/systemd/system/busos-api.service`**:
```ini
[Unit]
Description=BusOS Email Sequence API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/busos-email-sequence
Environment="PATH=/opt/busos-email-sequence/venv/bin"
ExecStart=/opt/busos-email-sequence/venv/bin/uvicorn server:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable busos-api
sudo systemctl start busos-api
sudo systemctl status busos-api
```

#### B. Deploy Prefect Flows

```bash
# Deploy all flows
python flows/deploy.py

# Or deploy specific flow
python flows/deploy.py --flow signup
python flows/deploy.py --flow assessment
```

#### C. Start Prefect Agent (if using Prefect Cloud)

```bash
# Login to Prefect Cloud
prefect cloud login

# Start agent
prefect agent start -q default
```

### Option 3: Docker Deployment

**Best for**: Containerized production environment

#### A. Create Dockerfile

**`Dockerfile`**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run server
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### B. Create docker-compose.yml

**`docker-compose.yml`**:
```yaml
version: '3.8'

services:
  busos-api:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    environment:
      - TESTING_MODE=false
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

#### C. Deploy with Docker

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## Monitoring

### 1. API Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-12T10:30:00Z",
  "environment": {
    "testing_mode": false,
    "notion_configured": true,
    "resend_configured": true,
    "discord_configured": true
  }
}
```

### 2. Prefect UI (if using Prefect Cloud)

- Flow runs: https://app.prefect.cloud/
- Check failed runs
- View logs and execution history

### 3. Application Logs

```bash
# If using systemd
sudo journalctl -u busos-api -f

# If using Docker
docker-compose logs -f

# If running directly
# Logs print to stdout
```

### 4. Discord Notifications

If configured, CRITICAL segment contacts trigger Discord alerts with:
- Email address
- Segment classification
- Number of red systems

---

## Troubleshooting

### Issue: "Missing environment variable"

**Symptom**: Server fails to start with missing NOTION_TOKEN or RESEND_API_KEY

**Solution**:
```bash
# Verify .env file exists
ls -la .env

# Check variables are set
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('NOTION_TOKEN'))"

# Ensure .env is in project root
pwd  # Should be /path/to/perfect
```

### Issue: "Template not found or not active"

**Symptom**: Email sending fails with template error

**Solution**:
```bash
# Re-seed templates
python scripts/seed_templates.py

# Verify templates in Notion
# Open Notion Templates DB and check Active checkbox
```

### Issue: Emails not sending

**Symptom**: Webhook returns success but no emails arrive

**Solution**:
1. Check Resend dashboard for send logs
2. Verify email addresses are valid
3. Check spam folder
4. Review server logs for errors:
   ```bash
   # Look for Resend API errors
   docker-compose logs | grep "resend"
   ```

### Issue: Notion rate limit errors

**Symptom**: "Rate limit exceeded" errors in logs

**Solution**:
- Caching is enabled by default
- If hitting limits, increase `retry_delay_seconds` in task decorators
- Consider upgrading Notion plan

### Issue: Flows running slowly

**Symptom**: Email sequence takes longer than expected

**Solution**:
```bash
# Check TESTING_MODE setting
cat .env | grep TESTING_MODE

# If TESTING_MODE=false, waits are 24-48 hours (by design)
# If TESTING_MODE=true, waits are 1-4 minutes
```

### Issue: Integration test fails

**Symptom**: test_integration_e2e.py fails

**Solution**:
```bash
# Always use --mode mock for testing
python test_integration_e2e.py --mode mock

# If still failing, check individual tests
python test_integration_e2e.py --flow signup
python test_integration_e2e.py --flow webhook
```

---

## Production Checklist

Before going live:

- [ ] `.env` configured with production credentials
- [ ] `TESTING_MODE=false` (24-48hr waits)
- [ ] Email templates seeded to Notion
- [ ] Unit tests pass (`pytest tests/ -v`)
- [ ] Integration tests pass (mocked)
- [ ] Webhook server running with systemd/Docker
- [ ] Prefect flows deployed
- [ ] Prefect agent running (if using Prefect Cloud)
- [ ] Health check endpoint responding
- [ ] Discord notifications configured (optional)
- [ ] Frontend integrated with webhook URLs
- [ ] Monitoring/alerting configured
- [ ] Backup strategy for `.env` file

---

## Support

**Issues**: Report bugs or request features via GitHub Issues

**Email**: sang@sanglescalinglabs.com

**Documentation**: This DEPLOYMENT.md file

---

## Next Steps

1. **Seed Templates**: `python scripts/seed_templates.py`
2. **Test Locally**: `uvicorn server:app --reload`
3. **Run Tests**: `python test_integration_e2e.py --mode mock`
4. **Deploy**: Choose deployment option above
5. **Monitor**: Check `/health` endpoint and logs

🎉 **Your Prefect-based email sequence is ready!**
