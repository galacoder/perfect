# Discord Webhooks Integration Guide

## Overview

Discord webhooks provide real-time notifications for marketing automation events. This guide shows how to send rich notifications to Discord channels from Prefect flows.

**Use Cases:**
- Hot lead alerts (score ≥ 80)
- Campaign performance reports (daily/weekly)
- System health notifications
- Publishing confirmations
- Error alerts

## Prerequisites

1. **Discord Server**: Create or use existing server
2. **Channel**: Create dedicated channel for notifications (e.g., `#marketing-alerts`)
3. **Webhook URL**: Create webhook for the channel

## Setup Steps

### 1. Create Discord Webhook

```bash
# 1. Open Discord and navigate to your server
# 2. Right-click the channel (e.g., #marketing-alerts)
# 3. Click "Edit Channel"
# 4. Go to "Integrations" tab
# 5. Click "Create Webhook"
# 6. Name: "Prefect Marketing Automation"
# 7. Copy webhook URL (looks like: https://discord.com/api/webhooks/...)

# Set as environment variable
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/your_webhook_url_here"
```

### 2. Test Webhook

```python
import httpx
import os
from datetime import datetime

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# Send test message
response = httpx.post(
    DISCORD_WEBHOOK_URL,
    json={
        "content": "✅ **Prefect Marketing Automation Connected!**",
        "embeds": [{
            "title": "System Test",
            "description": "Discord webhook is working correctly",
            "color": 0x00ff00,
            "timestamp": datetime.now().isoformat()
        }]
    },
    timeout=10
)

if response.status_code == 204:
    print("✅ Discord webhook test successful!")
else:
    print(f"❌ Test failed: {response.status_code}")
```

## Prefect Integration

### Basic Notification Task

```python
from prefect import task
import httpx
import os
from datetime import datetime

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

@task(retries=2, retry_delay_seconds=10)
def send_discord_notification(
    content: str,
    title: str = None,
    description: str = None,
    color: int = 0x0099ff,
    fields: list = None
):
    """
    Send notification to Discord channel.

    Args:
        content: Main message text (supports **bold**, *italic*, etc.)
        title: Embed title
        description: Embed description
        color: Embed color (hex int, e.g., 0xff0000 for red)
        fields: List of field dicts with name, value, inline keys

    Example:
        send_discord_notification(
            content="🔥 **Hot Lead Alert**",
            title="Min-Ji Park - 85/100",
            description="Immediate follow-up recommended",
            color=0xff0000,
            fields=[
                {"name": "Email", "value": "minjipark@salon.com", "inline": True},
                {"name": "Score", "value": "85", "inline": True}
            ]
        )
    """
    if not DISCORD_WEBHOOK_URL:
        print("⚠️ Discord webhook URL not configured")
        return

    payload = {"content": content}

    # Add embed if title or description provided
    if title or description or fields:
        embed = {}

        if title:
            embed["title"] = title

        if description:
            embed["description"] = description

        if color:
            embed["color"] = color

        if fields:
            embed["fields"] = fields

        embed["timestamp"] = datetime.now().isoformat()

        payload["embeds"] = [embed]

    response = httpx.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
    response.raise_for_status()
```

### Common Notification Patterns

#### 1. Hot Lead Alert

```python
@task
def notify_hot_lead(lead_data: dict, score: int):
    """Send alert for hot leads (score ≥ 80)."""

    if score < 80:
        return  # Only notify for hot leads

    send_discord_notification(
        content="🔥 **HOT LEAD ALERT**",
        title=f"{lead_data.get('first_name', 'Unknown')} - Score: {score}",
        description="Immediate follow-up recommended within 24 hours",
        color=0xff0000,  # Red
        fields=[
            {"name": "Email", "value": lead_data["email"], "inline": True},
            {"name": "Score", "value": str(score), "inline": True},
            {"name": "Stage", "value": "Assessment Complete", "inline": True},
            {"name": "Notion Link", "value": f"[Open in Notion](https://notion.so/{lead_data['notion_id']})", "inline": False}
        ]
    )
```

#### 2. Daily Performance Report

```python
@task
def send_daily_performance_report(metrics: dict):
    """Send daily marketing performance summary."""

    send_discord_notification(
        content="📊 **Daily Marketing Report**",
        title=f"Performance - {datetime.now().strftime('%Y-%m-%d')}",
        description="Consolidated metrics from all marketing channels",
        color=0x0099ff,  # Blue
        fields=[
            {"name": "💰 Total Ad Spend", "value": f"${metrics['total_spend']}", "inline": True},
            {"name": "👥 Conversions", "value": str(metrics['total_conversions']), "inline": True},
            {"name": "📊 Cost Per Lead", "value": f"${metrics['cost_per_lead']}", "inline": True},
            {"name": "🎯 CTR", "value": f"{metrics['ctr']:.2f}%", "inline": True},
            {"name": "📥 Opt-in Rate", "value": f"{metrics['optin_rate']:.1f}%", "inline": True},
            {"name": "✅ Close Rate", "value": f"{metrics['close_rate']:.1f}%", "inline": True}
        ]
    )
```

#### 3. Campaign Publishing Confirmation

```python
@task
def notify_campaign_published(post_content: str, platforms: list, urls: list):
    """Notify when social media post is published."""

    platform_fields = []
    for platform, url in zip(platforms, urls):
        if url:
            platform_fields.append({
                "name": platform.title(),
                "value": f"[View Post]({url})",
                "inline": True
            })

    send_discord_notification(
        content="📱 **Social Media Post Published**",
        title="Multi-Platform Publishing Complete",
        description=post_content[:200] + ("..." if len(post_content) > 200 else ""),
        color=0x00ff00,  # Green
        fields=platform_fields
    )
```

#### 4. Error Alert

```python
@task
def notify_error(error_message: str, flow_name: str, details: str = None):
    """Send error notification to Discord."""

    send_discord_notification(
        content="❌ **Flow Error Alert**",
        title=f"Error in {flow_name}",
        description=error_message,
        color=0xff0000,  # Red
        fields=[
            {"name": "Details", "value": details or "No additional details", "inline": False},
            {"name": "Time", "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "inline": True}
        ]
    )
```

#### 5. Retargeting Report

```python
@task
def send_retargeting_report(audiences: list, total_visitors: int):
    """Send daily retargeting performance report."""

    total_budget = sum(a["recommended_budget"] for a in audiences)

    fields = []
    for audience in audiences:
        fields.append({
            "name": f"{audience['audience_name']}",
            "value": f"Users: {audience['users_count']} | Budget: ${audience['recommended_budget']}/day",
            "inline": False
        })

    send_discord_notification(
        content="📊 **Daily Retargeting Report**",
        title="4-Audience Retargeting Status",
        description=f"Total visitors processed: {total_visitors}\nTotal daily budget: ${total_budget}",
        color=0x0099ff,
        fields=fields
    )
```

### Usage in Flows

```python
from prefect import flow

@flow(name="marketing-campaign-with-notifications")
def run_campaign_with_notifications():
    """Example flow with Discord notifications."""

    # Start notification
    send_discord_notification(
        content="🚀 **Campaign Started**",
        title="Marketing Campaign Execution",
        description="Starting daily marketing automation...",
        color=0x0099ff
    )

    try:
        # Run campaign logic
        results = execute_campaign()

        # Success notification
        send_discord_notification(
            content="✅ **Campaign Complete**",
            title="Execution Successful",
            description=f"Processed {results['total']} items",
            color=0x00ff00,
            fields=[
                {"name": "Success", "value": str(results['success']), "inline": True},
                {"name": "Failed", "value": str(results['failed']), "inline": True}
            ]
        )

    except Exception as e:
        # Error notification
        notify_error(
            error_message=str(e),
            flow_name="marketing-campaign",
            details=f"Failed at step: {results.get('current_step', 'unknown')}"
        )
        raise
```

## Advanced Features

### 1. Mentions and Role Pings

```python
# Mention user
content = "<@USER_ID> New hot lead!"

# Mention role (e.g., @marketing-team)
content = "<@&ROLE_ID> Daily report ready!"

# Mention everyone (use sparingly)
content = "@everyone Critical system alert!"
```

### 2. Buttons and Links

```python
# Add clickable button
payload = {
    "content": "🔥 Hot lead alert!",
    "embeds": [{
        "title": "Min-Ji Park - Score: 85",
        "description": "View in Notion",
        "url": "https://notion.so/page-id-here"  # Makes title clickable
    }]
}
```

### 3. Progress Updates

```python
@flow(name="campaign-with-progress")
def campaign_with_progress_updates():
    """Send progress updates during long-running campaign."""

    send_discord_notification(
        content="🚀 Starting campaign...",
        title="Progress: 0%",
        color=0x0099ff
    )

    # Step 1
    execute_step_1()
    send_discord_notification(
        content="📊 Step 1 complete",
        title="Progress: 33%",
        color=0x0099ff
    )

    # Step 2
    execute_step_2()
    send_discord_notification(
        content="📊 Step 2 complete",
        title="Progress: 67%",
        color=0x0099ff
    )

    # Step 3
    execute_step_3()
    send_discord_notification(
        content="✅ All steps complete!",
        title="Progress: 100%",
        color=0x00ff00
    )
```

## Rate Limits

Discord webhook limits:
- **30 requests/minute** per webhook
- **5 requests/second** burst
- Message length: **2000 characters** for content, **6000** for embeds

**Best Practices:**
```python
@task(retries=3, retry_delay_seconds=10)
def rate_limited_discord_notification(...):
    """Notification with retry logic for rate limits."""

    try:
        send_discord_notification(...)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            # Rate limited - will retry
            retry_after = e.response.json().get("retry_after", 10)
            print(f"⚠️ Rate limited, retrying after {retry_after}s")
            raise
        else:
            raise
```

## Color Reference

Common notification colors:

```python
COLORS = {
    "red": 0xff0000,      # Errors, critical alerts
    "orange": 0xffa500,   # Warnings
    "yellow": 0xffff00,   # Cautions
    "green": 0x00ff00,    # Success
    "blue": 0x0099ff,     # Info, reports
    "purple": 0x9b59b6,   # Special events
    "gray": 0x95a5a6      # Neutral
}
```

## Formatting Guide

Discord supports Markdown formatting:

```markdown
**bold text**
*italic text*
__underline text__
~~strikethrough text~~
`inline code`
```code block```
[link text](https://example.com)
> quote
```

## Error Handling

```python
@task
def safe_discord_notification(content: str, **kwargs):
    """Wrapper for safe Discord notifications."""

    try:
        send_discord_notification(content, **kwargs)
    except httpx.TimeoutException:
        print("⚠️ Discord notification timeout (not critical)")
        # Don't raise - notifications are not critical
    except Exception as e:
        print(f"⚠️ Discord notification failed: {e}")
        # Don't raise - don't fail flow for notifications
```

## Best Practices

1. **Channels**: Use separate channels for different alert types
2. **Rate Limiting**: Batch notifications, add delays
3. **Content Length**: Keep messages concise (< 2000 chars)
4. **Error Handling**: Don't fail flows for notification failures
5. **Testing**: Test formatting in Discord before deploying
6. **Mentions**: Use sparingly to avoid alert fatigue

## Common Issues

### Issue 1: Webhook URL Invalid

**Solution:**
```bash
# Verify URL format: https://discord.com/api/webhooks/...
# Regenerate webhook if needed in Discord channel settings
```

### Issue 2: Rate Limit Errors

**Solution:**
```python
# Add retry logic with exponential backoff
@task(retries=3, retry_delay_seconds=10, retry_jitter_factor=0.5)
def send_discord_notification(...):
    # Implementation
```

### Issue 3: Embeds Not Showing

**Solution:**
```python
# Verify embed structure matches Discord format
# Check color is int (0x format), not string
# Ensure timestamp is ISO 8601 format
```

## Resources

- [Discord Webhook Documentation](https://discord.com/developers/docs/resources/webhook)
- [Embed Object Reference](https://discord.com/developers/docs/resources/channel#embed-object)
- [Rate Limits](https://discord.com/developers/docs/topics/rate-limits)
- [Markdown Reference](https://support.discord.com/hc/en-us/articles/210298617)

## Next Steps

1. ✅ Create Discord channel for notifications
2. ✅ Set up webhook and get URL
3. ✅ Test webhook with Python script
4. ✅ Integrate with Prefect flows
5. ✅ Configure notification preferences per channel
6. ✅ Monitor notification delivery and adjust as needed
