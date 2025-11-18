# Deployment Guide - Self-Hosted Prefect

Complete guide to deploying marketing automation flows to your self-hosted Prefect server.

---

## Table of Contents

1. [Prefect Server Setup](#prefect-server-setup)
2. [Flow Deployment Strategies](#flow-deployment-strategies)
3. [Production Configuration](#production-configuration)
4. [Environment Management](#environment-management)
5. [Monitoring & Observability](#monitoring--observability)
6. [Scaling Considerations](#scaling-considerations)
7. [CI/CD Integration](#cicd-integration)

---

## Prefect Server Setup

### Option 1: Docker Compose (Recommended)

Create `docker-compose.yml` for your Prefect server:

```yaml
# docker-compose.yml
version: "3.8"

services:
  prefect-server:
    image: prefecthq/prefect:3.4-python3.11
    command: prefect server start --host 0.0.0.0
    ports:
      - "4200:4200"
    environment:
      - PREFECT_API_URL=http://localhost:4200/api
      - PREFECT_SERVER_API_HOST=0.0.0.0
      - PREFECT_UI_API_URL=http://localhost:4200/api
    volumes:
      - prefect-data:/root/.prefect
    restart: unless-stopped

  prefect-postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: prefect
      POSTGRES_PASSWORD: prefect_password
      POSTGRES_DB: prefect
    volumes:
      - postgres-data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  prefect-data:
  postgres-data:
```

**Start the server:**

```bash
docker compose up -d
```

**Verify server is running:**

```bash
curl http://localhost:4200/api/health
# Expected: {"status": "ok"}
```

### Option 2: Native Installation

```bash
# Install Prefect
pip install prefect>=3.4.1

# Configure database URL (optional, defaults to SQLite)
export PREFECT_API_DATABASE_CONNECTION_URL="postgresql+asyncpg://prefect:password@localhost:5432/prefect"

# Start the server
prefect server start
```

---

## Flow Deployment Strategies

### Strategy 1: Long-Running Serve (Simple)

Best for: Development, small-scale production, single server

```python
# my_flow.py
from prefect import flow, task

@flow(name="my-marketing-flow")
def my_marketing_flow():
    # Flow logic here
    pass

if __name__ == "__main__":
    # Serve the flow (keeps process running)
    my_marketing_flow.serve(
        name="my-deployment",
        cron="0 9 * * *",  # Run daily at 9 AM
        tags=["marketing", "production"]
    )
```

**Deploy:**

```bash
# Run in background with nohup
nohup python my_flow.py > flow.log 2>&1 &

# Or use systemd (see below)
```

**Pros:**
- ✅ Simple, minimal setup
- ✅ Good for development
- ✅ Easy to debug

**Cons:**
- ❌ Process must stay running
- ❌ No built-in process management
- ❌ Single point of failure

### Strategy 2: Work Pool + Workers (Production)

Best for: Production, multi-flow deployments, scalability

#### Step 1: Create Work Pool

```bash
# Create a process work pool
prefect work-pool create marketing-pool --type process
```

#### Step 2: Deploy Flows with build/push

```python
# my_flow.py
from prefect import flow

@flow(name="my-marketing-flow")
def my_marketing_flow():
    # Flow logic
    pass

if __name__ == "__main__":
    # Deploy to work pool (does NOT keep process running)
    my_marketing_flow.deploy(
        name="my-deployment",
        work_pool_name="marketing-pool",
        cron="0 9 * * *",
        tags=["marketing", "production"]
    )
```

**Deploy:**

```bash
python my_flow.py
```

#### Step 3: Start Workers

```bash
# Start 3 workers for the marketing-pool
prefect worker start --pool marketing-pool --limit 10 &
prefect worker start --pool marketing-pool --limit 10 &
prefect worker start --pool marketing-pool --limit 10 &
```

**Pros:**
- ✅ Production-ready
- ✅ Multiple workers (scalability)
- ✅ Work queue management
- ✅ Graceful shutdown

**Cons:**
- ❌ More complex setup
- ❌ Requires work pool management

### Strategy 3: Event-Driven (Webhooks)

Best for: Real-time triggers from external systems

```python
from prefect import flow
from prefect.events import DeploymentEventTrigger

@flow(name="lead-optin-handler")
def handle_lead_optin(email: str, first_name: str):
    # Process lead opt-in
    pass

if __name__ == "__main__":
    handle_lead_optin.serve(
        name="lead-optin-deployment",
        triggers=[
            DeploymentEventTrigger(
                match={"prefect.resource.id": "lead.*"},
                expect=["lead.opted_in"],
                parameters={
                    "email": "{{ event.payload.email }}",
                    "first_name": "{{ event.payload.first_name }}"
                }
            )
        ]
    )
```

**Trigger from external system:**

```bash
curl -X POST http://localhost:4200/api/events \
  -H "Content-Type: application/json" \
  -d '{
    "event": "lead.opted_in",
    "resource": {"prefect.resource.id": "lead.12345"},
    "payload": {
      "email": "user@example.com",
      "first_name": "John"
    }
  }'
```

---

## Production Configuration

### Directory Structure

```
/opt/marketing-automation/
├── flows/
│   ├── nurture_sequence.py
│   ├── lead_scoring.py
│   ├── retargeting.py
│   └── analytics.py
├── .env                      # Environment variables
├── requirements.txt          # Dependencies
├── docker-compose.yml        # Prefect server
└── systemd/
    ├── flow-nurture.service
    ├── flow-scoring.service
    └── prefect-worker.service
```

### Environment Variables (.env)

```bash
# .env
# Prefect Configuration
PREFECT_API_URL=http://localhost:4200/api
PREFECT_LOGGING_LEVEL=INFO

# Marketing Tools
LOOPS_API_KEY=loops_sk_...
NOTION_API_KEY=secret_...
NOTION_DATABASE_ID=...
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...

# Social Media
FACEBOOK_ACCESS_TOKEN=...
FACEBOOK_APP_ID=...
FACEBOOK_APP_SECRET=...
TWITTER_API_KEY=...
TWITTER_API_SECRET=...
TWITTER_ACCESS_TOKEN=...
TWITTER_ACCESS_SECRET=...
LINKEDIN_ACCESS_TOKEN=...
LINKEDIN_ORG_ID=...

# Security
WEBHOOK_SECRET_KEY=your_secret_key_here  # For webhook signature verification
```

**Load in flows:**

```python
from dotenv import load_dotenv
import os

load_dotenv()

LOOPS_API_KEY = os.getenv("LOOPS_API_KEY")
```

### Dependencies (requirements.txt)

```txt
prefect>=3.4.1
httpx>=0.27.0
notion-client>=2.2.1
python-dotenv>=1.0.0
requests-oauthlib>=1.3.1
```

---

## Systemd Service Management

### Flow Service

Create `/etc/systemd/system/flow-nurture.service`:

```ini
[Unit]
Description=Prefect Marketing Automation - Nurture Sequence
After=network.target docker.service
Requires=docker.service

[Service]
Type=simple
User=marketing
WorkingDirectory=/opt/marketing-automation
EnvironmentFile=/opt/marketing-automation/.env
ExecStart=/usr/bin/python3 /opt/marketing-automation/flows/nurture_sequence.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable flow-nurture.service
sudo systemctl start flow-nurture.service
sudo systemctl status flow-nurture.service
```

### Worker Service

Create `/etc/systemd/system/prefect-worker.service`:

```ini
[Unit]
Description=Prefect Worker - Marketing Pool
After=network.target

[Service]
Type=simple
User=marketing
WorkingDirectory=/opt/marketing-automation
EnvironmentFile=/opt/marketing-automation/.env
ExecStart=/usr/local/bin/prefect worker start --pool marketing-pool --limit 10
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

---

## Monitoring & Observability

### Flow-Level Logging

```python
from prefect import flow, task, get_run_logger

@task
def send_email(email: str):
    logger = get_run_logger()
    logger.info(f"Sending email to {email}")
    try:
        # Send email logic
        logger.info(f"Email sent successfully to {email}")
    except Exception as e:
        logger.error(f"Failed to send email to {email}: {str(e)}")
        raise

@flow(name="monitored-flow", log_prints=True)
def monitored_flow():
    logger = get_run_logger()
    logger.info("Flow started")
    send_email("test@example.com")
    logger.info("Flow completed")
```

### Discord Notifications

```python
@task
def send_discord_alert(title: str, message: str, color: int = 0x00ff00):
    """Send alert to Discord channel."""
    httpx.post(
        os.getenv("DISCORD_WEBHOOK_URL"),
        json={
            "embeds": [{
                "title": title,
                "description": message,
                "color": color,
                "timestamp": datetime.now().isoformat()
            }]
        }
    )

@flow(name="flow-with-alerts")
def flow_with_alerts():
    try:
        send_discord_alert("🚀 Flow Started", "Campaign execution beginning", color=0x0099ff)
        # Flow logic
        send_discord_alert("✅ Flow Complete", "Campaign executed successfully", color=0x00ff00)
    except Exception as e:
        send_discord_alert("❌ Flow Failed", f"Error: {str(e)}", color=0xff0000)
        raise
```

### Prometheus Metrics (Advanced)

```python
from prometheus_client import Counter, Histogram, start_http_server

# Define metrics
emails_sent = Counter('emails_sent_total', 'Total emails sent')
flow_duration = Histogram('flow_duration_seconds', 'Flow execution duration')

@task
def send_email_with_metrics(email: str):
    send_email(email)
    emails_sent.inc()

@flow
def flow_with_metrics():
    with flow_duration.time():
        # Flow logic
        pass

# Start Prometheus metrics server
start_http_server(8000)
```

---

## Scaling Considerations

### Horizontal Scaling (Multiple Workers)

```bash
# Start 5 workers across different servers
# Server 1
prefect worker start --pool marketing-pool --limit 10 --name worker-1 &

# Server 2
prefect worker start --pool marketing-pool --limit 10 --name worker-2 &

# Server 3
prefect worker start --pool marketing-pool --limit 10 --name worker-3 &
```

### Rate Limiting

```python
from prefect import task
from prefect.concurrency import rate_limit

@task
async def send_email_rate_limited(email: str):
    # Limit to 5 emails per minute
    async with rate_limit("loops_email", 5, per="minute"):
        send_email(email)
```

### Task Concurrency

```python
from prefect import flow, task

@task
async def process_lead(lead: dict):
    # Process individual lead
    pass

@flow
async def process_leads_concurrently(leads: list):
    # Process up to 10 leads concurrently
    await asyncio.gather(*[process_lead(lead) for lead in leads[:10]])
```

### Database Connection Pooling

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

# Create connection pool
engine = create_engine(
    os.getenv("DATABASE_URL"),
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30
)
```

---

## CI/CD Integration

### GitHub Actions

Create `.github/workflows/deploy-flows.yml`:

```yaml
name: Deploy Prefect Flows

on:
  push:
    branches: [main]
    paths:
      - 'flows/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install prefect>=3.4.1 -r requirements.txt

      - name: Configure Prefect
        env:
          PREFECT_API_URL: ${{ secrets.PREFECT_API_URL }}
        run: |
          prefect config set PREFECT_API_URL=$PREFECT_API_URL

      - name: Deploy flows
        env:
          LOOPS_API_KEY: ${{ secrets.LOOPS_API_KEY }}
          NOTION_API_KEY: ${{ secrets.NOTION_API_KEY }}
        run: |
          python flows/nurture_sequence.py
          python flows/lead_scoring.py
          python flows/retargeting.py
```

### GitLab CI

Create `.gitlab-ci.yml`:

```yaml
deploy-flows:
  stage: deploy
  image: python:3.11
  only:
    - main
  script:
    - pip install prefect>=3.4.1 -r requirements.txt
    - export PREFECT_API_URL=$PREFECT_API_URL
    - python flows/nurture_sequence.py
    - python flows/lead_scoring.py
```

---

## Security Best Practices

### 1. Secrets Management

**Use environment variables, never hardcode:**

```python
# ❌ BAD
LOOPS_API_KEY = "loops_sk_abc123..."

# ✅ GOOD
LOOPS_API_KEY = os.getenv("LOOPS_API_KEY")
```

### 2. Webhook Signature Verification

```python
import hmac
import hashlib

def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify webhook signature for security."""
    expected_signature = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected_signature)
```

### 3. Rate Limiting (Prevent Abuse)

```python
from prefect.concurrency import rate_limit

@task
async def handle_webhook(payload: dict):
    # Limit webhook processing to 100/minute
    async with rate_limit("webhook_processing", 100, per="minute"):
        process_webhook(payload)
```

### 4. Network Security

```bash
# Restrict Prefect UI access (nginx reverse proxy)
server {
    listen 443 ssl;
    server_name prefect.yourdomain.com;

    location / {
        proxy_pass http://localhost:4200;
        allow 10.0.0.0/8;  # Internal network only
        deny all;
    }
}
```

---

## Troubleshooting Deployment

### Issue: Flow not appearing in UI

**Solution:**
```bash
# Check Prefect API URL
prefect config view

# Verify server is reachable
curl http://localhost:4200/api/health

# Re-deploy flow
python my_flow.py
```

### Issue: Worker not picking up runs

**Solution:**
```bash
# Check work pool exists
prefect work-pool ls

# Check worker status
prefect worker ls

# Start worker with verbose logging
prefect worker start --pool marketing-pool --log-level DEBUG
```

### Issue: Environment variables not loading

**Solution:**
```python
# Add debug logging
from dotenv import load_dotenv
import os

load_dotenv()
print(f"LOOPS_API_KEY loaded: {os.getenv('LOOPS_API_KEY') is not None}")
```

---

## Production Checklist

Before going live, verify:

- [ ] Prefect server is running and accessible
- [ ] Database is configured (PostgreSQL recommended)
- [ ] All environment variables are set
- [ ] Flows are deployed and visible in UI
- [ ] Workers are running and picking up runs
- [ ] Monitoring/alerts are configured
- [ ] Rate limits are set for external APIs
- [ ] Error handling and retries are implemented
- [ ] Logs are being collected
- [ ] Backups are configured
- [ ] Security: secrets, network, webhooks
- [ ] CI/CD pipeline is working

---

## Next Steps

- Review [Best Practices Guide](./best-practices.md) for optimization
- Set up [Monitoring & Alerts](../patterns/monitoring-alerts.md)
- Configure [Retry Strategies](../patterns/retry-strategies.md)
- Implement [Rate Limiting](../patterns/concurrency-limits.md)
