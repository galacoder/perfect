# Webhook Triggers for Event-Driven Marketing Automation

## Overview

Webhook triggers enable real-time marketing automation by responding to external events. This guide covers event-driven patterns for Prefect flows triggered by lead actions, form submissions, and third-party integrations.

**Use Cases:**
- Lead opt-in → Start nurture sequence
- Assessment completion → Score lead and route
- Sales page visit → Trigger retargeting
- Email click → Update engagement score
- Form submission → Create CRM record

## Prerequisites

1. **Prefect v3.0+**: Event-driven triggers via `DeploymentEventTrigger`
2. **Webhook Endpoint**: Public URL to receive events
3. **Event Source**: Service sending webhook events (forms, landing pages, etc.)

## Event-Driven Architecture

### Pattern 1: Direct Webhook → Flow Trigger

**Best for**: Simple event-to-flow mapping

```python
from prefect import flow
from prefect.deployments import DeploymentEventTrigger

@flow(name="handle-lead-optin")
def handle_lead_optin(email: str, first_name: str, phone: str = None):
    """
    Triggered when lead opts in via landing page.

    Event payload: {"email": "...", "first_name": "...", "phone": "..."}
    """
    # Create lead in Notion
    lead_data = create_lead_from_optin(email, first_name, phone)

    # Send immediate CTA email
    send_loops_email(email, "email-1-immediate-cta", {"first_name": first_name})

    # Start nurture sequence
    trigger_nurture_sequence(email, first_name, lead_data["notion_id"])

# Deploy with event trigger
handle_lead_optin.serve(
    name="lead-optin-handler",
    triggers=[
        DeploymentEventTrigger(
            match={"prefect.resource.id": "lead.*"},
            expect=["lead.opted_in"],
            parameters={
                "email": "{{ event.payload.email }}",
                "first_name": "{{ event.payload.first_name }}",
                "phone": "{{ event.payload.phone }}"
            }
        )
    ]
)
```

### Pattern 2: Webhook Proxy → Event Emission

**Best for**: Multiple flows listening to same event

```python
from prefect import flow
from prefect.events import emit_event

@flow(name="webhook-proxy")
def webhook_proxy(event_type: str, payload: dict):
    """
    Generic webhook proxy that emits Prefect events.

    Allows multiple flows to listen to same webhook event.
    """
    emit_event(
        event=f"lead.{event_type}",
        resource={"prefect.resource.id": f"lead.{payload.get('email')}"},
        payload=payload
    )

# Multiple flows listen to same event
@flow(name="start-nurture-on-optin")
def start_nurture_on_optin(email: str, first_name: str):
    """Flow 1: Start nurture sequence."""
    trigger_nurture_sequence(email, first_name)

@flow(name="notify-slack-on-optin")
def notify_slack_on_optin(email: str, first_name: str):
    """Flow 2: Notify sales team."""
    send_slack_notification(f"New lead: {first_name} ({email})")

# Both flows listen to same event
start_nurture_on_optin.serve(
    name="nurture-listener",
    triggers=[
        DeploymentEventTrigger(
            match={"prefect.resource.id": "lead.*"},
            expect=["lead.opted_in"],
            parameters={"email": "{{ event.payload.email }}", "first_name": "{{ event.payload.first_name }}"}
        )
    ]
)

notify_slack_on_optin.serve(
    name="slack-listener",
    triggers=[
        DeploymentEventTrigger(
            match={"prefect.resource.id": "lead.*"},
            expect=["lead.opted_in"],
            parameters={"email": "{{ event.payload.email }}", "first_name": "{{ event.payload.first_name }}"}
        )
    ]
)
```

### Pattern 3: Conditional Event Routing

**Best for**: Different flows for different event properties

```python
@flow(name="route-by-segment")
def route_by_segment(email: str, first_name: str, segment: str):
    """
    Route to different nurture sequences based on segment.
    """
    if segment == "beauty-salon":
        trigger_beauty_salon_nurture(email, first_name)
    elif segment == "auto-repair":
        trigger_auto_repair_nurture(email, first_name)
    elif segment == "fitness":
        trigger_fitness_nurture(email, first_name)
    else:
        trigger_general_nurture(email, first_name)

route_by_segment.serve(
    name="segment-router",
    triggers=[
        DeploymentEventTrigger(
            match={"prefect.resource.id": "lead.*"},
            expect=["lead.opted_in"],
            parameters={
                "email": "{{ event.payload.email }}",
                "first_name": "{{ event.payload.first_name }}",
                "segment": "{{ event.payload.segment }}"
            }
        )
    ]
)
```

## Common Marketing Automation Events

### Event 1: Lead Opt-In

**Trigger**: Landing page form submission

```python
@flow(name="lead-optin-automation")
def lead_optin_automation(email: str, first_name: str, phone: str, visitor_id: str):
    """
    Complete opt-in automation:
    1. Create lead in Notion
    2. Send immediate CTA email
    3. Add to retargeting audience
    4. Notify Discord if high-value segment
    """
    # Create lead
    lead_data = create_lead_from_optin(email, first_name, visitor_id, phone)

    # Send email
    send_loops_email(email, "email-1-immediate-cta", {"first_name": first_name})

    # Update visitor record
    update_visitor_stage(visitor_id, "opted_in")

    # Add to Facebook Custom Audience
    add_to_custom_audience("opted_in_leads", [{"email": email}])

lead_optin_automation.serve(
    name="lead-optin-v1",
    triggers=[
        DeploymentEventTrigger(
            match={"prefect.resource.id": "lead.*"},
            expect=["lead.opted_in"],
            parameters={
                "email": "{{ event.payload.email }}",
                "first_name": "{{ event.payload.first_name }}",
                "phone": "{{ event.payload.phone }}",
                "visitor_id": "{{ event.payload.visitor_id }}"
            }
        )
    ]
)
```

### Event 2: Assessment Completion

**Trigger**: 8-System assessment form submitted

```python
@flow(name="assessment-completion-handler")
def assessment_completion_handler(
    notion_id: str,
    email: str,
    first_name: str,
    assessment_data: dict
):
    """
    Handle assessment completion:
    1. Score assessment (0-100)
    2. Update lead record
    3. Notify if hot lead (≥80)
    4. Trigger appropriate nurture
    5. Add to retargeting audience
    """
    # Calculate score
    score = calculate_assessment_score(assessment_data)

    # Update Notion
    update_lead(notion_id, {
        "stage": "assessment_complete",
        "score": score,
        "status": "hot" if score >= 80 else "warm" if score >= 50 else "cold",
        "priority": "high" if score >= 80 else "medium"
    })

    # Hot lead notification
    if score >= 80:
        send_discord_notification(
            content="🔥 **HOT LEAD ALERT**",
            title=f"{first_name} - Score: {score}",
            description="Immediate follow-up recommended",
            color=0xff0000,
            fields=[
                {"name": "Email", "value": email, "inline": True},
                {"name": "Score", "value": str(score), "inline": True},
                {"name": "Notion", "value": f"[Open](https://notion.so/{notion_id})", "inline": False}
            ]
        )

    # Trigger nurture based on score
    if score >= 80:
        trigger_hot_lead_nurture(email, first_name, notion_id)
    else:
        trigger_standard_nurture(email, first_name, notion_id)

    # Add to retargeting
    add_to_custom_audience("assessment_completers", [{"email": email}])

assessment_completion_handler.serve(
    name="assessment-handler-v1",
    triggers=[
        DeploymentEventTrigger(
            match={"prefect.resource.id": "lead.*"},
            expect=["lead.assessment_complete"],
            parameters={
                "notion_id": "{{ event.payload.notion_id }}",
                "email": "{{ event.payload.email }}",
                "first_name": "{{ event.payload.first_name }}",
                "assessment_data": "{{ event.payload.assessment_data }}"
            }
        )
    ]
)
```

### Event 3: Sales Page Visit

**Trigger**: Visitor lands on sales/pricing page

```python
@flow(name="sales-page-visit-handler")
def sales_page_visit_handler(visitor_id: str, page_url: str, duration: int):
    """
    Handle sales page visit:
    1. Update visitor stage
    2. Calculate engagement score
    3. Add to sales page retargeting audience
    4. Send follow-up email if engaged (>30s)
    """
    # Update visitor
    update_visitor_stage(visitor_id, "sales_page", page_url, duration)

    # Check if lead exists
    visitor = get_visitor_by_id(visitor_id)

    if visitor.get("lead_id"):
        # Existing lead - update score
        update_lead_score(visitor["lead_id"], points=20)  # Sales page visit = 20 points

        # Send follow-up if engaged
        if duration > 30:
            lead_data = get_lead_by_notion_id(visitor["lead_id"])
            send_loops_email(
                lead_data["email"],
                "email-sales-page-follow-up",
                {"first_name": lead_data["first_name"], "page_url": page_url}
            )

    # Add to retargeting audience
    add_to_custom_audience("sales_page_visitors", [{"visitor_id": visitor_id}])

sales_page_visit_handler.serve(
    name="sales-page-handler",
    triggers=[
        DeploymentEventTrigger(
            match={"prefect.resource.id": "visitor.*"},
            expect=["visitor.sales_page_visit"],
            parameters={
                "visitor_id": "{{ event.payload.visitor_id }}",
                "page_url": "{{ event.payload.page_url }}",
                "duration": "{{ event.payload.duration }}"
            }
        )
    ]
)
```

### Event 4: Email Engagement

**Trigger**: Lead opens email or clicks link

```python
@flow(name="email-engagement-handler")
def email_engagement_handler(
    email: str,
    event_type: str,  # "open" or "click"
    email_id: str,
    link_url: str = None
):
    """
    Handle email engagement:
    1. Update lead engagement score
    2. Track email stage completion
    3. Send next email if appropriate
    4. Notify if high engagement
    """
    # Find lead by email
    lead = get_lead_by_email(email)

    if not lead:
        return  # Skip if lead not found

    # Calculate points
    points = 5 if event_type == "open" else 10  # Click worth 2× open

    # Update engagement score
    update_lead(lead["notion_id"], {
        "engagement_score": lead.get("engagement_score", 0) + points
    })

    # Track click if present
    if event_type == "click" and link_url:
        track_email_click(lead["notion_id"], email_id, link_url)

        # High engagement notification
        if lead.get("engagement_score", 0) + points >= 50:
            send_discord_notification(
                content="📈 **High Email Engagement**",
                title=f"{lead['first_name']} - {points} points",
                description=f"Clicked: {link_url}",
                color=0x0099ff
            )

email_engagement_handler.serve(
    name="email-engagement-v1",
    triggers=[
        DeploymentEventTrigger(
            match={"prefect.resource.id": "email.*"},
            expect=["email.opened", "email.clicked"],
            parameters={
                "email": "{{ event.payload.email }}",
                "event_type": "{{ event.payload.event_type }}",
                "email_id": "{{ event.payload.email_id }}",
                "link_url": "{{ event.payload.link_url }}"
            }
        )
    ]
)
```

## Webhook Security

### Pattern 1: Signature Verification

```python
import hmac
import hashlib

@flow(name="webhook-receiver-secure")
def webhook_receiver_secure(payload: dict, signature: str):
    """
    Verify webhook signature before processing.

    Prevents unauthorized webhook calls.
    """
    # Calculate expected signature
    secret = os.getenv("WEBHOOK_SECRET")
    expected = hmac.new(
        secret.encode(),
        json.dumps(payload).encode(),
        hashlib.sha256
    ).hexdigest()

    # Verify signature
    if not hmac.compare_digest(signature, expected):
        print("❌ Invalid webhook signature")
        return {"status": "error", "message": "Invalid signature"}

    # Process webhook
    emit_event(
        event=f"lead.{payload['event_type']}",
        resource={"prefect.resource.id": f"lead.{payload.get('email')}"},
        payload=payload
    )

    return {"status": "success"}
```

### Pattern 2: IP Whitelisting

```python
ALLOWED_IPS = ["192.168.1.100", "10.0.0.50"]

@flow(name="webhook-receiver-ip-restricted")
def webhook_receiver_ip_restricted(payload: dict, source_ip: str):
    """
    Only accept webhooks from trusted IPs.
    """
    if source_ip not in ALLOWED_IPS:
        print(f"❌ Unauthorized IP: {source_ip}")
        return {"status": "error", "message": "Unauthorized"}

    # Process webhook
    emit_event(
        event=f"lead.{payload['event_type']}",
        resource={"prefect.resource.id": f"lead.{payload.get('email')}"},
        payload=payload
    )

    return {"status": "success"}
```

### Pattern 3: Rate Limiting

```python
from datetime import datetime, timedelta
from collections import defaultdict

webhook_calls = defaultdict(list)
MAX_CALLS_PER_MINUTE = 100

@flow(name="webhook-receiver-rate-limited")
def webhook_receiver_rate_limited(payload: dict, source_ip: str):
    """
    Rate limit webhook calls to prevent abuse.
    """
    now = datetime.now()

    # Clean old entries
    webhook_calls[source_ip] = [
        ts for ts in webhook_calls[source_ip]
        if now - ts < timedelta(minutes=1)
    ]

    # Check rate limit
    if len(webhook_calls[source_ip]) >= MAX_CALLS_PER_MINUTE:
        print(f"⚠️ Rate limit exceeded for {source_ip}")
        return {"status": "error", "message": "Rate limit exceeded"}

    # Record call
    webhook_calls[source_ip].append(now)

    # Process webhook
    emit_event(
        event=f"lead.{payload['event_type']}",
        resource={"prefect.resource.id": f"lead.{payload.get('email')}"},
        payload=payload
    )

    return {"status": "success"}
```

## Testing Webhook Triggers

### Local Testing with ngrok

```bash
# 1. Start Prefect server locally
prefect server start

# 2. Deploy flow with webhook trigger
python deploy_webhook_flow.py

# 3. Expose local server with ngrok
ngrok http 4200

# 4. Configure webhook URL in external service
# URL: https://abc123.ngrok.io/api/webhooks/lead-optin

# 5. Test webhook with curl
curl -X POST https://abc123.ngrok.io/api/webhooks/lead-optin \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "first_name": "Test",
    "phone": "+1234567890",
    "visitor_id": "visitor-123"
  }'
```

### Testing Event Emission

```python
from prefect.events import emit_event

def test_event_trigger():
    """Test event emission locally."""

    # Emit test event
    emit_event(
        event="lead.opted_in",
        resource={"prefect.resource.id": "lead.test@example.com"},
        payload={
            "email": "test@example.com",
            "first_name": "Test",
            "phone": "+1234567890",
            "visitor_id": "visitor-123"
        }
    )

    print("✅ Test event emitted")

# Run test
test_event_trigger()

# Check Prefect UI for flow run triggered by event
```

### Mock Webhook Payload

```python
def test_webhook_handler():
    """Test webhook handler with mock payload."""

    mock_payload = {
        "event_type": "opted_in",
        "email": "test@example.com",
        "first_name": "Test User",
        "phone": "+1234567890",
        "visitor_id": "visitor-123",
        "segment": "beauty-salon"
    }

    # Test handler
    result = webhook_proxy("opted_in", mock_payload)

    assert result["status"] == "success"
    print("✅ Webhook handler test passed")

test_webhook_handler()
```

## Best Practices

### 1. Event Naming Conventions

```python
# Good: Hierarchical, descriptive
"lead.opted_in"
"lead.assessment_started"
"lead.assessment_complete"
"visitor.sales_page_visit"
"email.opened"
"email.clicked"

# Bad: Flat, ambiguous
"optin"
"test_done"
"page_view"
```

### 2. Payload Structure

```python
# Good: Consistent, typed
{
    "event_type": "opted_in",
    "timestamp": "2025-01-10T14:30:00Z",
    "email": "user@example.com",
    "first_name": "John",
    "phone": "+1234567890",
    "metadata": {
        "visitor_id": "visitor-123",
        "segment": "beauty-salon",
        "source": "facebook-ad"
    }
}

# Bad: Inconsistent, unstructured
{
    "type": "opt-in",
    "data": "user@example.com|John|+1234567890",
    "extra": "some string"
}
```

### 3. Idempotency

```python
@flow(name="idempotent-webhook-handler")
def idempotent_webhook_handler(event_id: str, email: str, first_name: str):
    """
    Ensure webhook is only processed once.

    Use event_id to prevent duplicate processing.
    """
    # Check if already processed
    if is_event_processed(event_id):
        print(f"⚠️ Event {event_id} already processed, skipping")
        return {"status": "duplicate"}

    # Process event
    result = process_lead_optin(email, first_name)

    # Mark as processed
    mark_event_processed(event_id)

    return {"status": "success", "result": result}
```

### 4. Error Handling

```python
@flow(name="webhook-handler-resilient")
def webhook_handler_resilient(payload: dict):
    """
    Handle webhook errors gracefully.

    Don't fail entire flow if one operation fails.
    """
    results = {"status": "success", "operations": []}

    # Operation 1: Create lead
    try:
        lead_data = create_lead_from_optin(
            payload["email"],
            payload["first_name"],
            payload.get("phone")
        )
        results["operations"].append({"operation": "create_lead", "status": "success"})
    except Exception as e:
        print(f"❌ Failed to create lead: {e}")
        results["operations"].append({"operation": "create_lead", "status": "failed", "error": str(e)})

    # Operation 2: Send email
    try:
        send_loops_email(payload["email"], "email-1-immediate-cta", {"first_name": payload["first_name"]})
        results["operations"].append({"operation": "send_email", "status": "success"})
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        results["operations"].append({"operation": "send_email", "status": "failed", "error": str(e)})

    # Operation 3: Update retargeting
    try:
        add_to_custom_audience("opted_in_leads", [{"email": payload["email"]}])
        results["operations"].append({"operation": "add_to_audience", "status": "success"})
    except Exception as e:
        print(f"❌ Failed to update audience: {e}")
        results["operations"].append({"operation": "add_to_audience", "status": "failed", "error": str(e)})

    return results
```

## Integration with Landing Pages

### Pattern 1: Direct Form Submission

```html
<!-- Landing page form -->
<form id="optin-form">
  <input type="email" name="email" required>
  <input type="text" name="first_name" required>
  <input type="tel" name="phone">
  <button type="submit">Get Free Assessment</button>
</form>

<script>
document.getElementById('optin-form').addEventListener('submit', async (e) => {
  e.preventDefault();

  const formData = new FormData(e.target);

  // Send webhook to Prefect
  const response = await fetch('https://your-prefect-server.com/api/webhooks/lead-optin', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      email: formData.get('email'),
      first_name: formData.get('first_name'),
      phone: formData.get('phone'),
      visitor_id: localStorage.getItem('visitor_id'),
      segment: 'beauty-salon'
    })
  });

  if (response.ok) {
    window.location.href = '/thank-you';
  }
});
</script>
```

### Pattern 2: Via Zapier/Make.com

```yaml
# Zapier Flow:
# 1. Trigger: New form submission (Typeform, Google Forms, etc.)
# 2. Action: Webhook POST to Prefect
#    URL: https://your-prefect-server.com/api/webhooks/lead-optin
#    Payload:
#      email: {{Email}}
#      first_name: {{First Name}}
#      phone: {{Phone}}
#      visitor_id: {{Visitor ID}}
```

## Resources

- [Prefect Events Documentation](https://docs.prefect.io/latest/concepts/events/)
- [Webhook Security Best Practices](https://webhooks.fyi/security/best-practices)
- [ngrok Documentation](https://ngrok.com/docs)
- [HMAC Signature Verification](https://en.wikipedia.org/wiki/HMAC)

## Next Steps

1. ✅ Choose event-driven pattern (direct trigger vs proxy)
2. ✅ Implement signature verification for security
3. ✅ Set up local testing with ngrok
4. ✅ Deploy webhook-triggered flows
5. ✅ Configure external services to send webhooks
6. ✅ Monitor event logs and flow runs
