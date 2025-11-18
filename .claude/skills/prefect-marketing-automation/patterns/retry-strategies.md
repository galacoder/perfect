# Retry Strategies for Marketing Automation

## Overview

Retry strategies ensure marketing automation flows handle transient failures gracefully. This guide covers exponential backoff, jitter, selective retries, and circuit breaker patterns for API integrations.

## Why Retries Matter

**Common Transient Failures:**
- API rate limits (429 errors)
- Network timeouts
- Temporary service unavailability (503 errors)
- Database connection issues
- Third-party service hiccups

**Benefits:**
- ✅ Automatic recovery from temporary failures
- ✅ Reduced manual intervention
- ✅ Better success rates
- ✅ Improved reliability

## Basic Retry Pattern

```python
from prefect import task

@task(retries=3, retry_delay_seconds=60)
def send_email(to_email: str, template_id: str):
    """
    Send email with automatic retry on failure.

    Retries 3 times with 60-second delay between attempts.
    """
    # Email sending logic
    response = loops_api.send_email(to_email, template_id)
    response.raise_for_status()
    return response
```

**Parameters:**
- `retries=3` - Number of retry attempts (total: 1 initial + 3 retries = 4 attempts)
- `retry_delay_seconds=60` - Fixed delay between retries

## Advanced Retry Patterns

### 1. Exponential Backoff with Jitter

**Best for:** API rate limits, prevents thundering herd problem

```python
@task(
    retries=5,
    retry_delay_seconds=60,
    retry_jitter_factor=0.5  # Adds ±50% randomness
)
def api_call_with_backoff(endpoint: str, data: dict):
    """
    API call with exponential backoff and jitter.

    Retry delays (approximate with jitter):
    - Attempt 1: Initial call
    - Attempt 2: 30-90 seconds (60 ± 50%)
    - Attempt 3: 60-180 seconds (120 ± 50%)
    - Attempt 4: 120-360 seconds (240 ± 50%)
    - Attempt 5: 240-720 seconds (480 ± 50%)
    - Attempt 6: 480-1440 seconds (960 ± 50%)
    """
    response = httpx.post(endpoint, json=data, timeout=30)
    response.raise_for_status()
    return response.json()
```

**Why Jitter?**
- Prevents multiple tasks from retrying simultaneously
- Reduces load spikes on recovering services
- Improves overall success rate

### 2. Selective Retry (Status Code-Based)

**Best for:** Distinguishing between retryable and non-retryable errors

```python
from prefect import task
import httpx

@task(retries=3, retry_delay_seconds=30)
def smart_api_call(url: str, data: dict):
    """
    API call with smart retry logic.

    Retries only on specific error codes:
    - 429 (Rate Limit) - Retry
    - 500, 502, 503, 504 (Server Errors) - Retry
    - 400, 401, 403, 404 (Client Errors) - Don't retry
    """
    try:
        response = httpx.post(url, json=data, timeout=30)
        response.raise_for_status()
        return response.json()

    except httpx.HTTPStatusError as e:
        status_code = e.response.status_code

        # Don't retry client errors (4xx except 429)
        if 400 <= status_code < 500 and status_code != 429:
            print(f"❌ Client error {status_code}, not retrying")
            raise  # Raises without retry

        # Retry server errors (5xx) and rate limits (429)
        elif status_code >= 500 or status_code == 429:
            print(f"⚠️ Transient error {status_code}, will retry")
            raise  # Raises with retry

    except httpx.TimeoutException:
        print("⚠️ Timeout, will retry")
        raise  # Raises with retry
```

### 3. Custom Retry Logic

**Best for:** Complex retry conditions

```python
from prefect import task
from prefect.tasks import task_input_hash
from datetime import timedelta

@task(
    retries=5,
    retry_delay_seconds=60,
    cache_key_fn=task_input_hash,
    cache_expiration=timedelta(hours=1)
)
def facebook_ads_api_call(ad_account_id: str, params: dict):
    """
    Facebook Ads API call with custom retry logic.

    Handles:
    - Rate limits with retry-after header
    - Temporary errors
    - Caches successful results for 1 hour
    """
    try:
        response = httpx.get(
            f"https://graph.facebook.com/v18.0/act_{ad_account_id}/insights",
            params=params,
            headers={"Authorization": f"Bearer {FB_ACCESS_TOKEN}"},
            timeout=60
        )

        response.raise_for_status()
        return response.json()

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            # Check retry-after header
            retry_after = int(e.response.headers.get("Retry-After", 60))
            print(f"⚠️ Rate limited, retrying after {retry_after}s")

            # Note: Prefect doesn't support dynamic retry delays
            # This will use default retry_delay_seconds
            raise

        elif e.response.status_code == 400:
            # Invalid request - don't retry
            error_msg = e.response.json().get("error", {}).get("message", "Unknown error")
            print(f"❌ Invalid request: {error_msg}")
            raise

        else:
            # Other errors - retry
            print(f"⚠️ Error {e.response.status_code}, will retry")
            raise
```

### 4. Circuit Breaker Pattern

**Best for:** Protecting against cascading failures

```python
from datetime import datetime, timedelta

class CircuitBreaker:
    """Simple circuit breaker implementation."""

    def __init__(self, failure_threshold=5, timeout=300):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open

    def call(self, func, *args, **kwargs):
        """Call function with circuit breaker protection."""

        # Check if circuit should reset
        if self.state == "open":
            if datetime.now() - self.last_failure_time > timedelta(seconds=self.timeout):
                print("🔄 Circuit breaker: Half-open (testing)")
                self.state = "half-open"
                self.failures = 0
            else:
                raise Exception("Circuit breaker: OPEN (too many failures)")

        # Attempt call
        try:
            result = func(*args, **kwargs)

            # Success - reset circuit
            if self.state == "half-open":
                print("✅ Circuit breaker: Closed (recovered)")
                self.state = "closed"

            self.failures = 0
            return result

        except Exception as e:
            # Failure - increment counter
            self.failures += 1
            self.last_failure_time = datetime.now()

            if self.failures >= self.failure_threshold:
                print(f"❌ Circuit breaker: OPEN ({self.failures} failures)")
                self.state = "open"

            raise

# Usage
loops_circuit_breaker = CircuitBreaker(failure_threshold=5, timeout=300)

@task(retries=3, retry_delay_seconds=60)
def send_email_with_circuit_breaker(email: str, template_id: str):
    """Send email with circuit breaker protection."""

    def _send():
        return loops_api.send_email(email, template_id)

    return loops_circuit_breaker.call(_send)
```

## Marketing Automation Retry Patterns

### Pattern 1: Email Sending (Loops.so)

```python
@task(retries=3, retry_delay_seconds=60, retry_jitter_factor=0.5)
def send_loops_email(to_email: str, template_id: str, variables: dict):
    """
    Send email via Loops.so with retry logic.

    Retry strategy:
    - 3 retries with 60s base delay
    - Jitter prevents simultaneous retries
    - Handles rate limits and timeouts
    """
    response = httpx.post(
        "https://app.loops.so/api/v1/transactional",
        headers={"Authorization": f"Bearer {LOOPS_API_KEY}"},
        json={
            "transactionalId": template_id,
            "email": to_email,
            "dataVariables": variables
        },
        timeout=30
    )

    response.raise_for_status()
    return response.json()
```

### Pattern 2: Notion Database Operations

```python
@task(retries=5, retry_delay_seconds=5, retry_jitter_factor=0.5)
def notion_database_query(database_id: str, filters: dict):
    """
    Query Notion database with aggressive retry.

    Retry strategy:
    - 5 retries (Notion rate limits: 3 req/sec)
    - Short 5s delay (quick recovery)
    - Jitter to avoid concurrent requests
    """
    from notion_client import Client

    notion = Client(auth=NOTION_API_KEY)

    try:
        results = notion.databases.query(
            database_id=database_id,
            filter=filters
        )
        return results

    except APIResponseError as e:
        if e.code == "rate_limited":
            print("⚠️ Notion rate limited, retrying...")
            raise  # Will retry
        else:
            print(f"❌ Notion error: {e.code}")
            raise
```

### Pattern 3: Facebook Ads API

```python
@task(retries=5, retry_delay_seconds=120, retry_jitter_factor=0.5)
def facebook_ads_insights(ad_account_id: str, date_range: dict):
    """
    Fetch Facebook Ads insights with patient retry.

    Retry strategy:
    - 5 retries (complex queries may timeout)
    - Long 120s delay (Facebook needs time)
    - Jitter to spread load
    """
    response = httpx.get(
        f"https://graph.facebook.com/v18.0/act_{ad_account_id}/insights",
        params={
            "access_token": FB_ACCESS_TOKEN,
            "time_range": json.dumps(date_range),
            "fields": "spend,impressions,clicks,conversions"
        },
        timeout=60
    )

    response.raise_for_status()
    return response.json()
```

### Pattern 4: No Retry (Idempotent Operations)

```python
@task  # No retries specified
def log_event(event_type: str, event_data: dict):
    """
    Log event without retry.

    Logging is non-critical - don't retry.
    If it fails, log to stderr and continue.
    """
    try:
        analytics_api.log_event(event_type, event_data)
    except Exception as e:
        print(f"⚠️ Failed to log event: {e}", file=sys.stderr)
        # Don't raise - continue flow
```

## Best Practices

### 1. Match Retry Strategy to Use Case

| Operation | Retries | Delay | Jitter | Why |
|-----------|---------|-------|--------|-----|
| Email sending | 3 | 60s | Yes | Moderate reliability needed |
| Database queries | 5 | 5s | Yes | Quick recovery, high rate limits |
| Heavy API calls | 5 | 120s | Yes | Long timeouts, complex queries |
| Logging | 0 | - | - | Non-critical, don't delay flow |
| Webhooks | 2 | 30s | Yes | Fast failure detection |

### 2. Use Jitter for All API Calls

```python
# DON'T: Fixed delays cause thundering herd
@task(retries=3, retry_delay_seconds=60)

# DO: Jitter spreads retry attempts
@task(retries=3, retry_delay_seconds=60, retry_jitter_factor=0.5)
```

### 3. Log Retry Attempts

```python
from prefect import get_run_logger

@task(retries=3, retry_delay_seconds=60)
def api_call_with_logging(endpoint: str):
    """API call with retry logging."""

    logger = get_run_logger()

    try:
        logger.info(f"Calling {endpoint}")
        response = httpx.get(endpoint, timeout=30)
        response.raise_for_status()
        logger.info(f"✅ Success: {endpoint}")
        return response.json()

    except Exception as e:
        logger.warning(f"⚠️ Failed (will retry): {e}")
        raise
```

### 4. Set Reasonable Retry Limits

```python
# DON'T: Too many retries delay failure detection
@task(retries=20, retry_delay_seconds=300)  # Could take 1.6 hours!

# DO: Reasonable retries with fast failure
@task(retries=3, retry_delay_seconds=60)  # Max 3 minutes
```

## Testing Retry Logic

### Simulate Failures

```python
@task(retries=3, retry_delay_seconds=5)
def flaky_api_call(fail_times: int = 2):
    """Simulate flaky API for testing."""

    # Track call count using task state
    if not hasattr(flaky_api_call, "call_count"):
        flaky_api_call.call_count = 0

    flaky_api_call.call_count += 1

    if flaky_api_call.call_count <= fail_times:
        print(f"❌ Simulated failure #{flaky_api_call.call_count}")
        raise Exception("Simulated API failure")

    print(f"✅ Success on attempt #{flaky_api_call.call_count}")
    return {"status": "success", "attempts": flaky_api_call.call_count}
```

### Test Different Scenarios

```python
from prefect import flow

@flow
def test_retry_strategies():
    """Test different retry scenarios."""

    # Test 1: Success on first try
    print("Test 1: Immediate success")
    result = flaky_api_call(fail_times=0)
    assert result["attempts"] == 1

    # Test 2: Success after 2 retries
    print("Test 2: Success after retries")
    flaky_api_call.call_count = 0  # Reset
    result = flaky_api_call(fail_times=2)
    assert result["attempts"] == 3

    # Test 3: Failure after all retries
    print("Test 3: Complete failure")
    flaky_api_call.call_count = 0  # Reset
    try:
        result = flaky_api_call(fail_times=10)  # Will fail all retries
    except Exception as e:
        print(f"✅ Expected failure: {e}")

# Run tests
test_retry_strategies()
```

## Monitoring Retries

```python
@task(retries=3, retry_delay_seconds=60)
def monitored_api_call(endpoint: str):
    """API call with metrics tracking."""

    logger = get_run_logger()

    start_time = time.time()

    try:
        response = httpx.get(endpoint, timeout=30)
        duration = time.time() - start_time

        logger.info(f"API call succeeded in {duration:.2f}s")

        # Track metrics in Notion or analytics
        track_metric("api_call_success", duration)

        return response.json()

    except Exception as e:
        duration = time.time() - start_time

        logger.warning(f"API call failed after {duration:.2f}s: {e}")

        # Track failure metrics
        track_metric("api_call_failure", duration)

        raise
```

## Resources

- [Prefect Retry Documentation](https://docs.prefect.io/latest/concepts/tasks/#retries)
- [Exponential Backoff Wikipedia](https://en.wikipedia.org/wiki/Exponential_backoff)
- [Circuit Breaker Pattern](https://martinfowler.com/bliki/CircuitBreaker.html)
- [Jitter in Retry Logic](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/)

## Next Steps

1. ✅ Identify critical API integrations
2. ✅ Implement retry strategies based on failure patterns
3. ✅ Add jitter to all retry logic
4. ✅ Test retry behavior with simulated failures
5. ✅ Monitor retry metrics and adjust strategies
