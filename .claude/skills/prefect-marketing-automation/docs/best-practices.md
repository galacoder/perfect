# Best Practices Guide - Prefect Marketing Automation

Production-ready patterns and recommendations for building reliable marketing automation systems.

---

## Table of Contents

1. [Flow Design Principles](#flow-design-principles)
2. [Error Handling & Resilience](#error-handling--resilience)
3. [Performance Optimization](#performance-optimization)
4. [Security & Secrets Management](#security--secrets-management)
5. [Monitoring & Observability](#monitoring--observability)
6. [Testing Strategies](#testing-strategies)
7. [Data Management](#data-management)
8. [Code Organization](#code-organization)

---

## Flow Design Principles

### 1. Single Responsibility Principle

**❌ BAD - Flow does too much:**
```python
@flow
def massive_flow():
    # Handles opt-in, scoring, nurture, retargeting, analytics all in one
    create_lead()
    score_lead()
    send_nurture_emails()
    sync_to_facebook()
    generate_analytics()
```

**✅ GOOD - Separate concerns:**
```python
@flow
def handle_lead_optin(email: str, first_name: str):
    """Single purpose: Process lead opt-in"""
    create_lead_in_notion(email, first_name)
    send_immediate_cta_email(email, first_name)
    add_to_retargeting_audience(email)

@flow
def calculate_lead_score(notion_id: str):
    """Single purpose: Calculate and update lead score"""
    activities = fetch_lead_activities(notion_id)
    score = calculate_score(activities)
    update_notion_score(notion_id, score)

@flow
def send_nurture_sequence(email: str, sequence_day: int):
    """Single purpose: Send specific nurture email"""
    send_email_for_day(email, sequence_day)
```

### 2. Idempotency - Safe to Retry

Design tasks to produce the same result when run multiple times:

**❌ BAD - Not idempotent:**
```python
@task
def add_to_email_list(email: str):
    # Creates duplicate entries on retry
    email_list.append(email)
```

**✅ GOOD - Idempotent:**
```python
@task
def add_to_email_list(email: str):
    # Check if already exists before adding
    if email not in email_list:
        email_list.append(email)
    return {"added": email not in email_list, "email": email}
```

### 3. Atomic Operations

Keep tasks small and atomic - either fully succeed or fully fail:

**❌ BAD - Partial failure possible:**
```python
@task
def process_100_leads(leads: list):
    for lead in leads:
        send_email(lead["email"])  # If fails at lead 50, first 49 sent, rest not
```

**✅ GOOD - Individual atomic operations:**
```python
@task(retries=3, retry_delay_seconds=60)
def send_email_to_lead(lead: dict):
    """Process one lead atomically"""
    send_email(lead["email"])

@flow
def process_leads(leads: list):
    results = []
    for lead in leads:
        try:
            result = send_email_to_lead(lead)
            results.append({"success": True, "lead": lead})
        except Exception as e:
            results.append({"success": False, "lead": lead, "error": str(e)})
    return results
```

### 4. Clear Input/Output Contracts

**✅ GOOD - Type hints and documentation:**
```python
from typing import Dict, List, Optional
from pydantic import BaseModel

class LeadData(BaseModel):
    email: str
    first_name: str
    phone: Optional[str] = None
    segment: str = "general"

@task
def create_lead_in_notion(lead: LeadData) -> Dict[str, str]:
    """
    Create a new lead in Notion CRM.

    Args:
        lead: Lead data with email, name, and optional phone

    Returns:
        Dict with notion_id and status

    Raises:
        NotionAPIError: If Notion API call fails
    """
    # Implementation
    return {"notion_id": "abc123", "status": "created"}
```

---

## Error Handling & Resilience

### 1. Retry with Exponential Backoff

**✅ GOOD - Retry transient failures:**
```python
@task(
    retries=3,
    retry_delay_seconds=60,
    retry_jitter_factor=0.5  # Add randomness to avoid thundering herd
)
def call_external_api():
    """Retries with delays: ~60s, ~120s, ~240s"""
    response = httpx.post("https://api.example.com/endpoint")
    response.raise_for_status()
    return response.json()
```

### 2. Conditional Retry Logic

**✅ GOOD - Only retry on specific errors:**
```python
from prefect import task
import httpx

def should_retry(task, task_run, state) -> bool:
    """Custom retry logic - only retry on network/rate limit errors"""
    if isinstance(state.data, httpx.HTTPStatusError):
        status_code = state.data.response.status_code
        # Retry on 429 (rate limit) and 5xx (server errors)
        return status_code == 429 or status_code >= 500
    # Retry on network errors
    if isinstance(state.data, httpx.NetworkError):
        return True
    return False

@task(retries=3, retry_condition_fn=should_retry)
def api_call():
    response = httpx.post(...)
    response.raise_for_status()
```

### 3. Circuit Breaker Pattern

**✅ GOOD - Fail fast after repeated failures:**
```python
from datetime import datetime, timedelta

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half_open

    def call(self, func, *args, **kwargs):
        if self.state == "open":
            if datetime.now() - self.last_failure_time > timedelta(seconds=self.timeout):
                self.state = "half_open"
            else:
                raise Exception("Circuit breaker is OPEN - service unavailable")

        try:
            result = func(*args, **kwargs)
            self.failure_count = 0
            self.state = "closed"
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
            raise

loops_breaker = CircuitBreaker(failure_threshold=5, timeout=300)

@task
def send_email_with_breaker(email: str):
    return loops_breaker.call(send_email, email)
```

### 4. Graceful Degradation

**✅ GOOD - Continue with reduced functionality:**
```python
@flow
def campaign_with_fallback():
    try:
        # Primary: Send via Loops.so
        send_via_loops()
    except Exception as e:
        logger.warning(f"Loops.so failed: {e}. Falling back to SendGrid")
        try:
            # Fallback: Send via SendGrid
            send_via_sendgrid()
        except Exception as e2:
            logger.error(f"Both providers failed: {e2}")
            # Last resort: Queue for manual processing
            queue_for_manual_send()
```

---

## Performance Optimization

### 1. Parallel Execution for Independent Tasks

**❌ BAD - Sequential execution:**
```python
@flow
def process_leads_sequential(leads: list):
    for lead in leads:
        send_email(lead)  # Takes 2s each = 200s for 100 leads
```

**✅ GOOD - Parallel execution:**
```python
import asyncio

@task
async def send_email_async(lead: dict):
    async with httpx.AsyncClient() as client:
        await client.post(...)

@flow
async def process_leads_parallel(leads: list):
    # Process 10 leads concurrently
    batch_size = 10
    for i in range(0, len(leads), batch_size):
        batch = leads[i:i+batch_size]
        await asyncio.gather(*[send_email_async(lead) for lead in batch])
    # 100 leads in ~20s (10 batches × 2s)
```

### 2. Rate Limiting - Respect API Limits

**✅ GOOD - Token bucket rate limiting:**
```python
from prefect.concurrency import rate_limit

@task
async def send_email_rate_limited(email: str):
    # Loops.so: 5 emails per second
    async with rate_limit("loops_email", 5, per="second"):
        send_email(email)

@task
async def update_notion_rate_limited(notion_id: str, data: dict):
    # Notion: 3 requests per second
    async with rate_limit("notion_api", 3, per="second"):
        update_notion(notion_id, data)
```

### 3. Batch Operations

**❌ BAD - Individual API calls:**
```python
@flow
def add_100_leads_to_audience(leads: list):
    for lead in leads:
        facebook_ads.add_to_custom_audience(lead)  # 100 API calls
```

**✅ GOOD - Batch API calls:**
```python
@flow
def add_100_leads_to_audience(leads: list):
    # Facebook allows up to 10,000 users per batch
    batch_size = 1000
    for i in range(0, len(leads), batch_size):
        batch = leads[i:i+batch_size]
        facebook_ads.add_users_to_custom_audience(batch)  # 1 API call for 1000 leads
```

### 4. Caching Expensive Operations

**✅ GOOD - Cache API responses:**
```python
from prefect import task
from prefect.cache_policies import INPUTS

@task(cache_policy=INPUTS, cache_expiration=timedelta(hours=1))
def fetch_notion_database():
    """Cache database query for 1 hour"""
    notion = Client(auth=os.getenv("NOTION_API_KEY"))
    return notion.databases.query(database_id=os.getenv("NOTION_DATABASE_ID"))
```

---

## Security & Secrets Management

### 1. Never Hardcode Secrets

**❌ BAD - Hardcoded secrets:**
```python
LOOPS_API_KEY = "loops_sk_abc123..."
NOTION_API_KEY = "secret_xyz789..."
```

**✅ GOOD - Environment variables:**
```python
import os
from dotenv import load_dotenv

load_dotenv()

LOOPS_API_KEY = os.getenv("LOOPS_API_KEY")
NOTION_API_KEY = os.getenv("NOTION_API_KEY")

# Validate secrets are present
assert LOOPS_API_KEY, "LOOPS_API_KEY not set"
assert NOTION_API_KEY, "NOTION_API_KEY not set"
```

### 2. Use Prefect Blocks for Secrets (Advanced)

```python
from prefect.blocks.system import Secret

# Store secret
secret_block = Secret(value="my_secret_value")
secret_block.save("loops-api-key")

# Retrieve in flow
@task
def send_email():
    api_key = Secret.load("loops-api-key").get()
    # Use api_key
```

### 3. Webhook Signature Verification

**✅ GOOD - Verify webhook authenticity:**
```python
import hmac
import hashlib

def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify webhook came from trusted source"""
    expected_signature = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected_signature)

@flow
def handle_webhook(payload: dict, signature: str):
    if not verify_webhook_signature(json.dumps(payload).encode(), signature, WEBHOOK_SECRET):
        raise ValueError("Invalid webhook signature")
    # Process webhook
```

### 4. Hash PII for Facebook Custom Audiences

**✅ GOOD - Hash emails and phone numbers:**
```python
import hashlib

def hash_for_facebook(value: str) -> str:
    """Hash email/phone for Facebook Custom Audiences"""
    normalized = value.lower().strip()
    return hashlib.sha256(normalized.encode()).hexdigest()

@task
def add_to_custom_audience(email: str, phone: str):
    hashed_data = {
        "email": hash_for_facebook(email),
        "phone": hash_for_facebook(phone)
    }
    # Send hashed data to Facebook
```

---

## Monitoring & Observability

### 1. Structured Logging

**✅ GOOD - Structured logs with context:**
```python
from prefect import get_run_logger

@task
def send_email(email: str, template_id: str):
    logger = get_run_logger()

    logger.info(
        "Sending email",
        extra={
            "email": email,
            "template_id": template_id,
            "timestamp": datetime.now().isoformat()
        }
    )

    try:
        result = loops_api.send(email, template_id)
        logger.info("Email sent successfully", extra={"email": email, "message_id": result["id"]})
    except Exception as e:
        logger.error("Email send failed", extra={"email": email, "error": str(e)})
        raise
```

### 2. Real-Time Alerts

**✅ GOOD - Alert on failures:**
```python
@task
def send_discord_alert(title: str, message: str, color: int = 0xff0000):
    """Send alert to Discord channel"""
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

@flow
def campaign_with_monitoring():
    try:
        send_discord_alert("🚀 Campaign Started", "Nurture sequence beginning", color=0x0099ff)
        results = execute_campaign()
        send_discord_alert("✅ Campaign Complete", f"Processed {len(results)} leads", color=0x00ff00)
    except Exception as e:
        send_discord_alert("❌ Campaign Failed", f"Error: {str(e)}", color=0xff0000)
        raise
```

### 3. Performance Metrics

**✅ GOOD - Track execution time:**
```python
import time

@task
def send_email_with_metrics(email: str):
    start_time = time.time()
    logger = get_run_logger()

    try:
        send_email(email)
        duration = time.time() - start_time
        logger.info(f"Email sent in {duration:.2f}s", extra={"duration": duration, "email": email})
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Email failed after {duration:.2f}s", extra={"duration": duration, "error": str(e)})
        raise
```

### 4. Success/Failure Tracking

**✅ GOOD - Aggregate results:**
```python
@flow
def campaign_with_results_tracking():
    results = {"success": 0, "failed": 0, "errors": []}

    for lead in leads:
        try:
            send_email(lead["email"])
            results["success"] += 1
        except Exception as e:
            results["failed"] += 1
            results["errors"].append({"lead": lead, "error": str(e)})

    logger.info(f"Campaign complete: {results['success']} sent, {results['failed']} failed")

    if results["failed"] > 0:
        send_discord_alert(
            "⚠️ Campaign Partial Failure",
            f"{results['failed']} emails failed. Check logs for details.",
            color=0xffa500
        )

    return results
```

---

## Testing Strategies

### 1. Unit Test Individual Tasks

```python
import pytest
from unittest.mock import Mock, patch
from my_flow import send_email

def test_send_email_success():
    with patch("httpx.post") as mock_post:
        mock_post.return_value.json.return_value = {"id": "msg_123"}
        result = send_email("test@example.com")
        assert result["id"] == "msg_123"

def test_send_email_failure():
    with patch("httpx.post") as mock_post:
        mock_post.side_effect = httpx.HTTPStatusError("429 Too Many Requests")
        with pytest.raises(httpx.HTTPStatusError):
            send_email("test@example.com")
```

### 2. Integration Tests with Test Environment

```python
@pytest.fixture
def test_env():
    """Set up test environment"""
    os.environ["LOOPS_API_KEY"] = "test_key"
    os.environ["NOTION_DATABASE_ID"] = "test_db_id"
    yield
    # Cleanup

def test_full_campaign_flow(test_env):
    """Test complete flow with test data"""
    test_lead = {"email": "test@example.com", "first_name": "Test"}
    result = handle_lead_optin.fn(test_lead["email"], test_lead["first_name"])
    assert result["status"] == "success"
```

### 3. Dry-Run Mode

```python
@flow
def campaign_flow(dry_run: bool = False):
    """Execute campaign with optional dry-run mode"""
    leads = fetch_leads()

    if dry_run:
        logger.info(f"DRY RUN: Would process {len(leads)} leads")
        return {"dry_run": True, "leads": len(leads)}

    # Actual execution
    for lead in leads:
        send_email(lead)
```

---

## Data Management

### 1. Deduplication

**✅ GOOD - Check before creating:**
```python
@task
def create_lead_with_dedup(email: str, first_name: str):
    notion = Client(auth=os.getenv("NOTION_API_KEY"))

    # Check if lead exists
    existing = notion.databases.query(
        database_id=os.getenv("NOTION_DATABASE_ID"),
        filter={"property": "Email", "email": {"equals": email}}
    )

    if existing["results"]:
        logger.info(f"Lead {email} already exists, updating instead")
        return notion.pages.update(
            page_id=existing["results"][0]["id"],
            properties={"First Name": {"title": [{"text": {"content": first_name}}]}}
        )

    # Create new lead
    return notion.pages.create(...)
```

### 2. Data Validation

```python
from pydantic import BaseModel, EmailStr, validator

class LeadData(BaseModel):
    email: EmailStr  # Validates email format
    first_name: str
    phone: Optional[str] = None

    @validator("first_name")
    def name_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("First name cannot be empty")
        return v.strip()

    @validator("phone")
    def phone_format(cls, v):
        if v and not v.replace("+", "").replace("-", "").isdigit():
            raise ValueError("Invalid phone format")
        return v

@task
def create_lead(lead_data: dict):
    validated = LeadData(**lead_data)  # Validates data
    # Create lead with validated data
```

### 3. Audit Trail

```python
@task
def update_lead_with_audit(notion_id: str, updates: dict):
    """Update lead and log change history"""
    notion = Client(auth=os.getenv("NOTION_API_KEY"))

    # Add audit metadata
    audit_entry = {
        "updated_at": datetime.now().isoformat(),
        "updated_by": "prefect_flow",
        "changes": json.dumps(updates)
    }

    # Update with audit trail
    notion.pages.update(
        page_id=notion_id,
        properties={
            **updates,
            "Last Updated": {"date": {"start": audit_entry["updated_at"]}},
            "Audit Log": {"rich_text": [{"text": {"content": audit_entry["changes"]}}]}
        }
    )
```

---

## Code Organization

### 1. Separate Configuration

```python
# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys
    LOOPS_API_KEY = os.getenv("LOOPS_API_KEY")
    NOTION_API_KEY = os.getenv("NOTION_API_KEY")
    NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

    # Timeouts
    HTTP_TIMEOUT = 30
    RETRY_DELAY = 60

    # Rate Limits
    LOOPS_RATE_LIMIT = 5  # per second
    NOTION_RATE_LIMIT = 3  # per second

# my_flow.py
from config import Config

@task
def send_email():
    api_key = Config.LOOPS_API_KEY
```

### 2. Reusable Task Library

```python
# tasks/email.py
@task(retries=3, retry_delay_seconds=60)
def send_loops_email(email: str, template_id: str, variables: dict):
    """Reusable email sending task"""
    # Implementation

# tasks/notion.py
@task(retries=2, retry_delay_seconds=10)
def create_notion_page(database_id: str, properties: dict):
    """Reusable Notion page creation"""
    # Implementation

# flows/campaign.py
from tasks.email import send_loops_email
from tasks.notion import create_notion_page

@flow
def my_campaign():
    create_notion_page(...)
    send_loops_email(...)
```

### 3. Type Hints and Documentation

```python
from typing import Dict, List, Optional

@task
def calculate_score(activities: List[Dict[str, any]]) -> int:
    """
    Calculate lead score based on activities.

    Args:
        activities: List of activity dicts with 'type' and 'timestamp'

    Returns:
        Score from 0-100

    Example:
        >>> activities = [{"type": "email_open", "timestamp": "2025-01-01"}]
        >>> calculate_score(activities)
        25
    """
    score = 0
    for activity in activities:
        if activity["type"] == "email_open":
            score += 5
        elif activity["type"] == "link_click":
            score += 10
    return min(score, 100)
```

---

## Production Deployment Checklist

Before deploying to production, ensure:

- [ ] **Error Handling**: All tasks have retry logic
- [ ] **Rate Limiting**: API calls respect rate limits
- [ ] **Monitoring**: Discord/Slack alerts configured
- [ ] **Logging**: Structured logging with context
- [ ] **Security**: Secrets in environment variables, not code
- [ ] **Testing**: Unit tests for critical tasks
- [ ] **Idempotency**: Tasks can be safely retried
- [ ] **Documentation**: Code documented with type hints
- [ ] **Performance**: Parallel execution where possible
- [ ] **Fallbacks**: Graceful degradation on failures
- [ ] **Audit Trail**: Changes logged in CRM
- [ ] **Deduplication**: Prevent duplicate records
- [ ] **Validation**: Input data validated before processing

---

## Next Steps

- Review [Deployment Guide](./deployment-guide.md) for production setup
- Consult [Troubleshooting Guide](./troubleshooting.md) for common issues
- Study [Complete Examples](../examples/) for production patterns
- Explore [Pattern Guides](../patterns/) for specific use cases
