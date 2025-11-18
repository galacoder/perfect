# Concurrency Limits for Marketing Automation

## Overview

Concurrency limits prevent overwhelming external APIs and services. This guide covers task concurrency, rate limiting patterns, and API quota management for marketing automation.

## Why Concurrency Limits Matter

**Problems Without Limits:**
- ❌ API bans from excessive requests
- ❌ Rate limit errors (429)
- ❌ Service degradation
- ❌ Cost overruns

**Benefits With Limits:**
- ✅ Stay within API quotas
- ✅ Avoid rate limit errors
- ✅ Predictable performance
- ✅ Better reliability

## Task Concurrency

### Limit Concurrent Tasks

```python
from prefect import task, flow

@task(retries=3, retry_delay_seconds=60)
async def send_email(email: str, template_id: str):
    """Send single email."""
    # Email sending logic

@flow
async def send_batch_emails(leads: list):
    """
    Send emails with concurrency limit.

    Process 10 emails at a time to avoid overwhelming Loops.so API.
    """
    from prefect.task_runners import ConcurrentTaskRunner

    # Limit to 10 concurrent email sends
    async with ConcurrentTaskRunner(max_workers=10):
        tasks = [send_email(lead["email"], "template-id") for lead in leads]
        results = await asyncio.gather(*tasks)

    return results
```

### Sequential Execution (No Concurrency)

```python
@flow
def send_emails_sequentially(leads: list):
    """
    Send emails one at a time (safest for strict rate limits).
    """
    results = []

    for lead in leads:
        result = send_email(lead["email"], "template-id")
        results.append(result)

        # Optional delay between calls
        time.sleep(1)  # 1 second between emails

    return results
```

## Rate Limiting Patterns

### Pattern 1: Token Bucket (Simple)

```python
import time
from threading import Lock

class RateLimiter:
    """Simple token bucket rate limiter."""

    def __init__(self, requests_per_second: int):
        self.requests_per_second = requests_per_second
        self.min_interval = 1.0 / requests_per_second
        self.last_call = 0
        self.lock = Lock()

    def wait(self):
        """Wait until next request is allowed."""
        with self.lock:
            now = time.time()
            time_since_last = now - self.last_call

            if time_since_last < self.min_interval:
                sleep_time = self.min_interval - time_since_last
                time.sleep(sleep_time)

            self.last_call = time.time()

# Usage
loops_limiter = RateLimiter(requests_per_second=100)  # Loops.so limit

@task
def rate_limited_email(email: str, template_id: str):
    """Send email with rate limiting."""
    loops_limiter.wait()
    return send_loops_email(email, template_id)
```

### Pattern 2: Batching

```python
@flow
def send_batch_with_delays(leads: list, batch_size: int = 50):
    """
    Send emails in batches with delays.

    Processes 50 emails, then waits 60 seconds before next batch.
    """
    results = []

    for i in range(0, len(leads), batch_size):
        batch = leads[i:i + batch_size]

        print(f"Processing batch {i // batch_size + 1}")

        # Send batch
        batch_results = [send_email(lead["email"], "template-id") for lead in batch]
        results.extend(batch_results)

        # Wait before next batch (except last batch)
        if i + batch_size < len(leads):
            print(f"Waiting 60 seconds before next batch...")
            time.sleep(60)

    return results
```

## API-Specific Limits

### Loops.so (100 req/sec)

```python
@task(retries=3, retry_delay_seconds=60, retry_jitter_factor=0.5)
def loops_api_call(endpoint: str, data: dict):
    """
    Loops.so API call respecting 100 req/sec limit.

    Safe concurrency: 10 parallel tasks max.
    """
    response = httpx.post(
        f"https://app.loops.so/api/v1/{endpoint}",
        headers={"Authorization": f"Bearer {LOOPS_API_KEY}"},
        json=data,
        timeout=30
    )
    response.raise_for_status()
    return response.json()
```

**Recommended Concurrency:** 10 parallel tasks

### Notion (3 req/sec)

```python
@task(retries=5, retry_delay_seconds=5, retry_jitter_factor=0.5)
def notion_api_call(operation: str, data: dict):
    """
    Notion API call respecting 3 req/sec limit.

    Safe concurrency: 2 parallel tasks max.
    """
    from notion_client import Client

    notion = Client(auth=NOTION_API_KEY)

    # Notion operations
    if operation == "create":
        return notion.pages.create(**data)
    elif operation == "update":
        return notion.pages.update(**data)
    elif operation == "query":
        return notion.databases.query(**data)
```

**Recommended Concurrency:** 2 parallel tasks

### Facebook Ads (200 req/hour)

```python
# Facebook has hourly limits - use careful batching
@flow
def facebook_ads_batch_query(accounts: list):
    """
    Query Facebook Ads data respecting 200 req/hour limit.

    Process 180 requests max per hour (safety margin).
    """
    results = []
    request_count = 0
    start_time = time.time()

    for account in accounts:
        # Check if approaching hourly limit
        if request_count >= 180:
            elapsed = time.time() - start_time

            if elapsed < 3600:  # Less than 1 hour
                wait_time = 3600 - elapsed
                print(f"Approaching rate limit, waiting {wait_time:.0f}s...")
                time.sleep(wait_time)
                request_count = 0
                start_time = time.time()

        # Make request
        result = facebook_ads_api_call(account["id"])
        results.append(result)
        request_count += 1

    return results
```

**Recommended Concurrency:** Sequential (1 at a time)

## Best Practices

### 1. Know Your Limits

| API | Rate Limit | Recommended Concurrency |
|-----|-----------|------------------------|
| Loops.so | 100 req/sec | 10 parallel tasks |
| Notion | 3 req/sec | 2 parallel tasks |
| Facebook Ads | 200 req/hour | Sequential |
| Google Ads | 15K req/day | 10 parallel tasks |
| Discord Webhooks | 30 req/min | 5 parallel tasks |

### 2. Add Safety Margins

```python
# DON'T: Use exact limit
max_concurrent = 100  # Loops.so limit

# DO: Use 80% of limit for safety
max_concurrent = 80  # 80% of Loops.so limit
```

### 3. Monitor and Adjust

```python
@task
def monitored_api_call(endpoint: str):
    """API call with rate limit monitoring."""

    logger = get_run_logger()

    try:
        response = api_call(endpoint)
        return response

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            logger.warning("⚠️ Rate limit hit - reduce concurrency!")
            raise
        else:
            raise
```

## Resources

- [Prefect Concurrency Documentation](https://docs.prefect.io/latest/concepts/task-runners/)
- [Rate Limiting Patterns](https://cloud.google.com/architecture/rate-limiting-strategies-techniques)
- [Token Bucket Algorithm](https://en.wikipedia.org/wiki/Token_bucket)

## Next Steps

1. ✅ Document API rate limits for all integrations
2. ✅ Implement appropriate concurrency limits
3. ✅ Add rate limit monitoring
4. ✅ Test with production-like loads
5. ✅ Adjust limits based on observed behavior
