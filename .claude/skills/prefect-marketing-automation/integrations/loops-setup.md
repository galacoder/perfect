# Loops.so Integration Guide

## Overview

Loops.so is a transactional email and email automation platform designed for modern SaaS businesses. This guide shows how to integrate Loops.so with Prefect for marketing automation.

**Use Cases:**
- Transactional emails (assessment results, booking confirmations)
- Nurture sequence automation (7-email Soap Opera sequence)
- Event-triggered emails (lead scored, assessment completed)
- Email engagement tracking

## Prerequisites

1. **Loops.so Account**: Sign up at [https://loops.so/](https://loops.so/)
2. **API Key**: Get from Settings → API Keys
3. **Email Templates**: Create in Loops.so dashboard

## Setup Steps

### 1. Get Your API Key

```bash
# Login to Loops.so
# Navigate to: Settings → API Keys
# Click "Create API Key"
# Copy the key (starts with "sk_...")

# Set as environment variable
export LOOPS_API_KEY="sk_your_api_key_here"
```

### 2. Create Email Templates

In the Loops.so dashboard:

1. Go to **Templates**
2. Click **Create Template**
3. Design your email using their visual editor
4. Add **Data Variables** for personalization:
   - `{{first_name}}` - Lead's first name
   - `{{segment}}` - Lead segment (e.g., "beauty-salon")
   - `{{score}}` - Assessment score
   - `{{from_email}}` - Sender email

**Example Template:**

```
Subject: Your Assessment Results, {{first_name}}!

Hi {{first_name}},

Thanks for completing the 8-System Assessment!

Your business scored {{score}}/100, which puts you in the {{segment}} category.

Here's what we discovered...

[Content continues]
```

4. Save template and copy the **Template ID** (e.g., `email-1-immediate-cta`)

### 3. Install Python Dependencies

```bash
pip install httpx prefect
```

### 4. Test API Connection

```python
import httpx
import os

LOOPS_API_KEY = os.getenv("LOOPS_API_KEY")

# Test API connection
response = httpx.get(
    "https://app.loops.so/api/v1/api-key",
    headers={"Authorization": f"Bearer {LOOPS_API_KEY}"},
    timeout=10
)

if response.status_code == 200:
    print("✅ Loops.so API connection successful!")
    print(f"   Account: {response.json()}")
else:
    print(f"❌ API connection failed: {response.status_code}")
```

## Prefect Integration

### Basic Email Sending Task

```python
from prefect import task
import httpx
import os

LOOPS_API_KEY = os.getenv("LOOPS_API_KEY")

@task(retries=3, retry_delay_seconds=60, retry_jitter_factor=0.5)
def send_loops_email(to_email: str, template_id: str, variables: dict):
    """
    Send email via Loops.so API with retry logic.

    Args:
        to_email: Recipient email address
        template_id: Loops.so template ID
        variables: Template variables (personalization data)

    Returns:
        Response from Loops.so API

    Raises:
        httpx.HTTPStatusError: If API request fails after retries
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

### Usage in Flow

```python
from prefect import flow

@flow(name="send-welcome-email")
def send_welcome_email(email: str, first_name: str, segment: str):
    """Send welcome email to new lead."""

    result = send_loops_email(
        to_email=email,
        template_id="email-1-immediate-cta",
        variables={
            "first_name": first_name,
            "segment": segment,
            "from_email": "hello@yourdomain.com"
        }
    )

    print(f"✅ Email sent to {email}: {result}")
    return result
```

## Advanced Features

### 1. Add Contact to List

```python
@task(retries=2, retry_delay_seconds=30)
def add_contact_to_loops(email: str, first_name: str, segment: str):
    """Add contact to Loops.so list for ongoing automation."""

    response = httpx.post(
        "https://app.loops.so/api/v1/contacts/create",
        headers={"Authorization": f"Bearer {LOOPS_API_KEY}"},
        json={
            "email": email,
            "firstName": first_name,
            "userGroup": segment,  # Custom property
            "subscribed": True
        },
        timeout=30
    )

    response.raise_for_status()
    return response.json()
```

### 2. Track Email Events (Webhooks)

Configure webhooks in Loops.so to track:
- Email delivered
- Email opened
- Link clicked
- Email bounced

**Webhook URL:** `https://your-prefect-server.com/webhooks/loops`

**Webhook Handler Flow:**

```python
@flow(name="loops-webhook-handler")
def handle_loops_webhook(event_type: str, email: str, template_id: str):
    """Handle Loops.so webhook events."""

    print(f"📧 Loops.so Event: {event_type} - {email}")

    if event_type == "email.opened":
        # Increment engagement score
        update_lead_engagement(email, points=5)

    elif event_type == "email.clicked":
        # Higher engagement for clicks
        update_lead_engagement(email, points=10)

    elif event_type == "email.bounced":
        # Mark email as invalid
        mark_email_invalid(email)
```

### 3. Batch Email Sending

```python
@flow(name="batch-email-sender")
def send_batch_emails(leads: list, template_id: str):
    """Send same email to multiple leads."""

    results = []

    for lead in leads:
        result = send_loops_email(
            to_email=lead["email"],
            template_id=template_id,
            variables={
                "first_name": lead["first_name"],
                "segment": lead["segment"]
            }
        )
        results.append(result)

    print(f"✅ Sent {len(results)} emails via Loops.so")
    return results
```

## Rate Limits

Loops.so API limits:
- **100 requests/second** per API key
- **No daily limit** on transactional emails

**Best Practices:**
- Use Prefect's `@task(retries=3)` for automatic retry
- Add `retry_delay_seconds=60` to handle temporary rate limits
- Use `retry_jitter_factor=0.5` to avoid thundering herd

## Error Handling

```python
@task(retries=3, retry_delay_seconds=60)
def send_loops_email_with_fallback(to_email: str, template_id: str, variables: dict):
    """Send email with comprehensive error handling."""

    try:
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

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 400:
            # Invalid email or template
            print(f"❌ Invalid request: {e.response.json()}")
            raise  # Don't retry

        elif e.response.status_code == 429:
            # Rate limit - will retry
            print(f"⚠️ Rate limit hit, retrying...")
            raise

        else:
            # Server error - will retry
            print(f"❌ Server error: {e}")
            raise

    except httpx.TimeoutException:
        print(f"⚠️ Request timeout, retrying...")
        raise
```

## Testing

### Test Template Rendering

```python
# Test email locally without sending
variables = {
    "first_name": "Min-Ji",
    "segment": "beauty-salon",
    "score": 75,
    "from_email": "hello@yourdomain.com"
}

print(f"Template variables: {variables}")
print(f"Template ID: email-1-immediate-cta")

# Send test email to yourself
send_loops_email(
    to_email="your-email@example.com",
    template_id="email-1-immediate-cta",
    variables=variables
)
```

## Common Issues

### Issue 1: "Invalid API Key"

**Solution:**
```bash
# Check API key format
echo $LOOPS_API_KEY  # Should start with "sk_"

# Verify key is active in Loops.so dashboard
# Settings → API Keys → Check status
```

### Issue 2: "Template not found"

**Solution:**
```bash
# Verify template ID in Loops.so dashboard
# Templates → Click template → Copy ID from URL or settings
```

### Issue 3: Rate Limit Errors

**Solution:**
```python
# Add exponential backoff with jitter
@task(
    retries=5,
    retry_delay_seconds=60,
    retry_jitter_factor=0.5
)
def send_loops_email(...):
    # Task implementation
```

## Best Practices

1. **Template Variables**: Always provide all required variables
2. **Error Handling**: Use `@task(retries=3)` for resilience
3. **Rate Limiting**: Batch emails with delays between groups
4. **Testing**: Test templates in Loops.so dashboard first
5. **Monitoring**: Track email delivery rates and engagement
6. **Security**: Never log API keys or email addresses

## Resources

- [Loops.so Documentation](https://loops.so/docs)
- [API Reference](https://loops.so/docs/api-reference)
- [Template Variables Guide](https://loops.so/docs/templates)
- [Webhook Events](https://loops.so/docs/webhooks)

## Next Steps

1. ✅ Set up Loops.so account and get API key
2. ✅ Create email templates for your campaigns
3. ✅ Test API connection with Python script
4. ✅ Integrate with Prefect flows
5. ✅ Configure webhooks for engagement tracking
6. ✅ Monitor email delivery and engagement metrics
