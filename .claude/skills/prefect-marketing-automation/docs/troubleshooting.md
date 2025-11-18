# Troubleshooting Guide - Prefect Marketing Automation

Common issues and solutions for Prefect marketing automation flows.

---

## Table of Contents

1. [Prefect Server Issues](#prefect-server-issues)
2. [Flow Deployment Problems](#flow-deployment-problems)
3. [API Integration Errors](#api-integration-errors)
4. [Event Trigger Issues](#event-trigger-issues)
5. [Scheduling Problems](#scheduling-problems)
6. [Performance & Rate Limiting](#performance--rate-limiting)
7. [Data & CRM Issues](#data--crm-issues)
8. [Debugging Techniques](#debugging-techniques)

---

## Prefect Server Issues

### Issue: "Connection refused" when running flow

**Symptoms:**
```
prefect.exceptions.PrefectHTTPStatusError: Client error '404 Not Found'
```

**Cause:** Prefect server not running or wrong API URL

**Solutions:**

1. **Check if Prefect server is running:**
```bash
curl http://localhost:4200/api/health
# Expected: {"status": "ok"}
```

2. **Start the server if not running:**
```bash
# Option 1: Direct start
prefect server start

# Option 2: Docker Compose
docker compose up -d prefect-server
```

3. **Verify API URL configuration:**
```bash
prefect config view
# Should show: PREFECT_API_URL='http://localhost:4200/api'

# If wrong, set it:
prefect config set PREFECT_API_URL=http://localhost:4200/api
```

4. **Check environment variables:**
```python
import os
print(os.getenv("PREFECT_API_URL"))
# Should output: http://localhost:4200/api
```

---

### Issue: Prefect UI not accessible

**Symptoms:**
- Browser shows "This site can't be reached"
- `curl http://localhost:4200` fails

**Solutions:**

1. **Check if port 4200 is in use:**
```bash
lsof -i :4200
# or
netstat -an | grep 4200
```

2. **Check Docker container status:**
```bash
docker ps | grep prefect
# Should show prefect-server running

# If not running:
docker compose logs prefect-server
```

3. **Check firewall rules:**
```bash
# Allow port 4200
sudo ufw allow 4200/tcp
```

4. **Access UI on correct host:**
```
# If running in Docker:
http://localhost:4200

# If running on remote server:
http://YOUR_SERVER_IP:4200
```

---

### Issue: Database connection errors

**Symptoms:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solutions:**

1. **Check PostgreSQL is running:**
```bash
docker ps | grep postgres
# or
systemctl status postgresql
```

2. **Verify database URL:**
```bash
echo $PREFECT_API_DATABASE_CONNECTION_URL
# Should be: postgresql+asyncpg://user:password@host:5432/prefect
```

3. **Test database connection:**
```bash
psql -h localhost -U prefect -d prefect
# Enter password when prompted
```

4. **Reset database (⚠️ DELETES ALL DATA):**
```bash
prefect server database reset --yes
```

---

## Flow Deployment Problems

### Issue: Flow not appearing in Prefect UI

**Symptoms:**
- Flow runs successfully locally
- Not visible in Deployments tab

**Solutions:**

1. **Verify deployment was created:**
```bash
prefect deployment ls
# Should show your deployment
```

2. **Check if flow.serve() is being called:**
```python
if __name__ == "__main__":
    my_flow.serve(name="my-deployment")  # ✅ CORRECT

    # ❌ WRONG - only runs the flow, doesn't deploy
    # my_flow()
```

3. **Re-deploy the flow:**
```bash
python my_flow.py
# Should output: "Your flow 'my-flow' is being served..."
```

4. **Check for errors in deployment:**
```bash
# Enable debug logging
export PREFECT_LOGGING_LEVEL=DEBUG
python my_flow.py
```

---

### Issue: "No workers available" error

**Symptoms:**
```
No workers available for work pool 'marketing-pool'
```

**Cause:** No workers are running for the work pool

**Solutions:**

1. **Start a worker:**
```bash
prefect worker start --pool marketing-pool
```

2. **Check worker status:**
```bash
prefect worker ls
# Should show active workers
```

3. **Switch to .serve() instead of .deploy():**
```python
# Instead of:
my_flow.deploy(work_pool_name="marketing-pool")  # Requires worker

# Use:
my_flow.serve(name="my-deployment")  # No worker needed
```

---

### Issue: Deployment exists but runs fail immediately

**Symptoms:**
- Deployment shows in UI
- Runs fail within seconds
- Error: "ModuleNotFoundError" or import errors

**Cause:** Dependencies not installed in worker environment

**Solutions:**

1. **Install dependencies where worker runs:**
```bash
pip install prefect httpx notion-client python-dotenv
```

2. **Verify imports work:**
```python
python -c "import httpx; import notion_client; print('OK')"
```

3. **Use requirements.txt:**
```bash
pip install -r requirements.txt
```

---

## API Integration Errors

### Issue: Loops.so "401 Unauthorized"

**Symptoms:**
```
httpx.HTTPStatusError: Client error '401 Unauthorized'
```

**Solutions:**

1. **Verify API key is set:**
```python
import os
print(f"LOOPS_API_KEY: {os.getenv('LOOPS_API_KEY')[:10]}...")
# Should show first 10 chars
```

2. **Check API key format:**
```bash
# Loops.so API keys start with "loops_sk_"
echo $LOOPS_API_KEY
# Should output: loops_sk_...
```

3. **Test API key directly:**
```bash
curl https://app.loops.so/api/v1/api-key \
  -H "Authorization: Bearer $LOOPS_API_KEY"
# Should return: {"success": true}
```

4. **Regenerate API key:**
- Go to [Loops.so Settings](https://loops.so/settings/api)
- Create new API key
- Update `.env` file

---

### Issue: Notion "object not found" error

**Symptoms:**
```
notion_client.errors.ObjectNotFound: Could not find database with ID: ...
```

**Solutions:**

1. **Verify database ID:**
```python
import os
print(f"Database ID: {os.getenv('NOTION_DATABASE_ID')}")
```

2. **Share database with integration:**
- Open Notion database
- Click "..." → Add connections
- Select your integration

3. **Verify integration has correct permissions:**
- Go to [Notion Integrations](https://www.notion.so/my-integrations)
- Check "Read content", "Update content", "Insert content"

4. **Test Notion API:**
```python
from notion_client import Client
notion = Client(auth=os.getenv("NOTION_API_KEY"))
result = notion.databases.query(database_id=os.getenv("NOTION_DATABASE_ID"))
print(f"Found {len(result['results'])} pages")
```

---

### Issue: Discord webhook "400 Bad Request"

**Symptoms:**
```
httpx.HTTPStatusError: Client error '400 Bad Request'
```

**Solutions:**

1. **Verify webhook URL format:**
```python
import os
url = os.getenv("DISCORD_WEBHOOK_URL")
assert url.startswith("https://discord.com/api/webhooks/"), "Invalid webhook URL"
```

2. **Test webhook manually:**
```bash
curl -X POST $DISCORD_WEBHOOK_URL \
  -H "Content-Type: application/json" \
  -d '{"content": "Test message"}'
```

3. **Check JSON payload structure:**
```python
# ✅ CORRECT
payload = {"content": "Message"}

# ❌ WRONG - missing content
payload = {"text": "Message"}
```

4. **Verify webhook is not deleted:**
- Go to Discord channel
- Settings → Integrations → Webhooks
- Regenerate webhook if missing

---

### Issue: Facebook Ads "Invalid OAuth access token"

**Symptoms:**
```
facebook_business.exceptions.FacebookRequestError: Invalid OAuth access token
```

**Solutions:**

1. **Check token expiration:**
```bash
curl "https://graph.facebook.com/debug_token?input_token=$FACEBOOK_ACCESS_TOKEN&access_token=$FACEBOOK_APP_ID|$FACEBOOK_APP_SECRET"
# Check "expires_at" field
```

2. **Regenerate long-lived token:**
```bash
curl "https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=$FACEBOOK_APP_ID&client_secret=$FACEBOOK_APP_SECRET&fb_exchange_token=$SHORT_LIVED_TOKEN"
```

3. **Verify token has required permissions:**
- ads_management
- ads_read
- business_management

4. **Use Graph API Explorer to test:**
- Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
- Test your access token

---

## Event Trigger Issues

### Issue: Webhook not triggering flow

**Symptoms:**
- Webhook receives request
- Flow doesn't execute

**Solutions:**

1. **Verify event trigger configuration:**
```python
from prefect.events import DeploymentEventTrigger

# Check match and expect fields
my_flow.serve(
    name="my-deployment",
    triggers=[
        DeploymentEventTrigger(
            match={"prefect.resource.id": "lead.*"},  # Must match event
            expect=["lead.opted_in"],  # Must match event name
            parameters={
                "email": "{{ event.payload.email }}"  # Check template syntax
            }
        )
    ]
)
```

2. **Test event emission manually:**
```bash
curl -X POST http://localhost:4200/api/events \
  -H "Content-Type: application/json" \
  -d '{
    "event": "lead.opted_in",
    "resource": {"prefect.resource.id": "lead.12345"},
    "payload": {"email": "test@example.com"}
  }'
```

3. **Check event logs in Prefect UI:**
- Navigate to Events tab
- Verify event was received
- Check if event matched trigger

4. **Enable debug logging:**
```python
import logging
logging.getLogger("prefect.events").setLevel(logging.DEBUG)
```

---

### Issue: Event parameters not mapping correctly

**Symptoms:**
- Flow triggers
- Parameters are None or wrong values

**Cause:** Incorrect template syntax in event trigger

**Solutions:**

1. **Use correct template syntax:**
```python
# ✅ CORRECT
parameters={
    "email": "{{ event.payload.email }}",
    "first_name": "{{ event.payload.first_name }}"
}

# ❌ WRONG - missing event prefix
parameters={
    "email": "{{ payload.email }}"
}
```

2. **Match payload structure:**
```python
# If webhook sends:
{"data": {"user": {"email": "test@example.com"}}}

# Template should be:
"email": "{{ event.payload.data.user.email }}"
```

3. **Add default values:**
```python
parameters={
    "email": "{{ event.payload.email | default('unknown@example.com') }}"
}
```

---

## Scheduling Problems

### Issue: Scheduled flow not running at expected time

**Symptoms:**
- Cron schedule set
- Flow doesn't execute

**Solutions:**

1. **Verify deployment is running:**
```bash
# Check if serve() process is still running
ps aux | grep python | grep my_flow.py

# Or check systemd service
systemctl status flow-my-deployment.service
```

2. **Check cron expression:**
```python
# Test cron expression at https://crontab.guru/
my_flow.serve(name="my-deployment", cron="0 9 * * *")  # Every day at 9 AM

# Verify timezone
import datetime
print(f"Server time: {datetime.datetime.now()}")
```

3. **Check Prefect UI for scheduled runs:**
- Deployments → Your deployment
- Check "Next Scheduled Run"

4. **Enable schedule:**
```python
my_flow.serve(
    name="my-deployment",
    cron="0 9 * * *",
    paused=False  # Ensure not paused
)
```

---

### Issue: Flow running too frequently

**Symptoms:**
- Flow executes more than expected
- Multiple runs overlapping

**Solutions:**

1. **Check for multiple deployments:**
```bash
prefect deployment ls | grep my-flow
# Should show only one deployment
```

2. **Add concurrency limit:**
```python
from prefect import flow

@flow(name="my-flow", task_runner_max_concurrency=1)
def my_flow():
    pass
```

3. **Use deployment concurrency limit:**
```bash
prefect deployment set-concurrency-limit my-flow/my-deployment 1
```

---

## Performance & Rate Limiting

### Issue: "Rate limit exceeded" from external API

**Symptoms:**
```
httpx.HTTPStatusError: Client error '429 Too Many Requests'
```

**Solutions:**

1. **Add rate limiting:**
```python
from prefect.concurrency import rate_limit

@task
async def send_email(email: str):
    # Limit to 5 emails per minute
    async with rate_limit("loops_email", 5, per="minute"):
        # Send email logic
        pass
```

2. **Add retry with exponential backoff:**
```python
@task(retries=3, retry_delay_seconds=60, retry_jitter_factor=0.5)
def send_email(email: str):
    # Will retry with increasing delays: 60s, 120s, 240s
    pass
```

3. **Process in batches:**
```python
@flow
def process_leads(leads: list):
    # Process 10 at a time with 1-minute delay between batches
    for batch in [leads[i:i+10] for i in range(0, len(leads), 10)]:
        process_batch(batch)
        time.sleep(60)
```

---

### Issue: Flow taking too long to execute

**Symptoms:**
- Flow timeout errors
- Slow performance

**Solutions:**

1. **Use async tasks for I/O-bound operations:**
```python
import asyncio

@task
async def send_email_async(email: str):
    async with httpx.AsyncClient() as client:
        await client.post(...)

@flow
async def send_emails_parallel(emails: list):
    # Send 10 emails concurrently
    await asyncio.gather(*[send_email_async(email) for email in emails[:10]])
```

2. **Increase timeout:**
```python
@flow(timeout_seconds=3600)  # 1 hour timeout
def long_running_flow():
    pass
```

3. **Profile slow tasks:**
```python
import time

@task
def slow_task():
    start = time.time()
    # Task logic
    logger = get_run_logger()
    logger.info(f"Task took {time.time() - start:.2f} seconds")
```

---

## Data & CRM Issues

### Issue: Duplicate leads in Notion

**Symptoms:**
- Same lead created multiple times
- No deduplication

**Solutions:**

1. **Check for existing lead before creating:**
```python
@task
def create_lead_if_not_exists(email: str, first_name: str):
    notion = Client(auth=os.getenv("NOTION_API_KEY"))

    # Search for existing lead
    existing = notion.databases.query(
        database_id=os.getenv("NOTION_DATABASE_ID"),
        filter={"property": "Email", "email": {"equals": email}}
    )

    if existing["results"]:
        logger.info(f"Lead {email} already exists")
        return existing["results"][0]["id"]

    # Create new lead
    return notion.pages.create(...)
```

2. **Use email as unique identifier:**
```python
# Add unique constraint in Notion database schema
# Or use external ID field
```

---

### Issue: Lead score not updating

**Symptoms:**
- Score calculation runs
- Notion database not updated

**Solutions:**

1. **Verify Notion update syntax:**
```python
@task
def update_lead_score(notion_id: str, score: int):
    notion = Client(auth=os.getenv("NOTION_API_KEY"))

    notion.pages.update(
        page_id=notion_id,
        properties={
            "Lead Score": {"number": score}  # Must match property name exactly
        }
    )
```

2. **Check property type matches:**
```python
# If property is "Number", use:
{"Lead Score": {"number": 85}}

# If property is "Text", use:
{"Lead Score": {"rich_text": [{"text": {"content": "85"}}]}}
```

3. **Add error handling:**
```python
@task(retries=2, retry_delay_seconds=5)
def update_lead_score(notion_id: str, score: int):
    try:
        notion.pages.update(...)
    except Exception as e:
        logger.error(f"Failed to update score: {e}")
        raise
```

---

## Debugging Techniques

### Enable Debug Logging

```python
import logging
from prefect import flow, get_run_logger

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

@flow
def debug_flow():
    logger = get_run_logger()
    logger.debug("Debug message")
    logger.info("Info message")
    logger.error("Error message")
```

### Use Breakpoints (Local Testing)

```python
@task
def debug_task():
    import pdb; pdb.set_trace()  # Python debugger
    # Or use breakpoint()
```

### Inspect Flow State

```python
from prefect import flow, get_run_logger

@flow
def inspect_flow():
    logger = get_run_logger()

    # Log all environment variables
    import os
    for key, value in os.environ.items():
        if "API" in key or "TOKEN" in key:
            logger.debug(f"{key}: {value[:10]}...")  # First 10 chars only
```

### Test Tasks Independently

```python
# Test task without running full flow
from my_flow import send_email

result = send_email("test@example.com")
print(result)
```

### Check Prefect Logs

```bash
# View flow run logs
prefect flow-run logs <flow-run-id>

# View all recent logs
prefect flow-run ls --limit 10

# Follow logs in real-time
tail -f ~/.prefect/prefect.log
```

---

## Getting Additional Help

**If issue persists:**

1. **Check Prefect Documentation:**
   - https://docs.prefect.io

2. **Search Prefect Community:**
   - https://discourse.prefect.io

3. **Review Integration Guides:**
   - `integrations/loops-setup.md`
   - `integrations/notion-connector.md`
   - `integrations/discord-webhooks.md`

4. **Enable verbose logging and share:**
```bash
export PREFECT_LOGGING_LEVEL=DEBUG
python my_flow.py 2>&1 | tee debug.log
```

5. **Check GitHub Issues:**
   - Prefect: https://github.com/PrefectHQ/prefect/issues
   - Notion SDK: https://github.com/ramnes/notion-sdk-py/issues
