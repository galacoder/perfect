# Monitoring & Alerting for Marketing Automation

## Overview

Monitoring and alerting ensure marketing automation runs reliably and delivers results. This guide covers flow monitoring, performance metrics, error detection, and proactive alerting patterns for Prefect workflows.

**Use Cases:**
- Flow failure alerts → Immediate notification
- Performance degradation → Identify bottlenecks
- Cost tracking → Monitor API usage and spend
- Success metrics → Track campaign performance
- Anomaly detection → Catch unusual patterns

## Prefect Monitoring Features

### Built-in Observability

**Prefect UI Dashboard** (http://localhost:4200):
- Flow run history and status
- Task execution timeline
- Logs and artifacts
- Event timeline
- Resource usage

**What Prefect Tracks Automatically:**
- Flow run status (pending, running, completed, failed)
- Task execution time and retries
- Event emissions and triggers
- Logs (stdout/stderr)
- Artifacts (outputs, files, metrics)

## Alerting Patterns

### Pattern 1: Discord Notifications

**Best for**: Real-time team alerts

```python
from prefect import flow, task, get_run_logger
import httpx
import os
from datetime import datetime

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

@task(retries=2, retry_delay_seconds=10)
def send_discord_alert(
    content: str,
    title: str,
    description: str,
    color: int = 0xff0000,
    fields: list = None
):
    """
    Send alert to Discord channel.

    Colors:
    - Red (0xff0000): Errors, failures
    - Yellow (0xffff00): Warnings
    - Green (0x00ff00): Success
    - Blue (0x0099ff): Info
    """
    payload = {
        "content": content,
        "embeds": [{
            "title": title,
            "description": description,
            "color": color,
            "timestamp": datetime.now().isoformat(),
            "fields": fields or []
        }]
    }

    response = httpx.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
    response.raise_for_status()

@flow(name="campaign-with-alerts")
def campaign_with_alerts():
    """Campaign flow with Discord alerts."""

    logger = get_run_logger()

    try:
        # Start alert
        send_discord_alert(
            content="🚀 **Campaign Started**",
            title="Email Nurture Campaign",
            description="Starting daily campaign execution...",
            color=0x0099ff
        )

        # Execute campaign
        results = execute_campaign_logic()

        # Success alert
        send_discord_alert(
            content="✅ **Campaign Complete**",
            title="Execution Successful",
            description=f"Processed {results['total']} leads",
            color=0x00ff00,
            fields=[
                {"name": "Success", "value": str(results['success']), "inline": True},
                {"name": "Failed", "value": str(results['failed']), "inline": True},
                {"name": "Duration", "value": f"{results['duration']}s", "inline": True}
            ]
        )

    except Exception as e:
        # Error alert
        send_discord_alert(
            content="❌ **Campaign Failed**",
            title="Execution Error",
            description=str(e),
            color=0xff0000,
            fields=[
                {"name": "Flow Name", "value": "campaign-with-alerts", "inline": True},
                {"name": "Error Type", "value": type(e).__name__, "inline": True}
            ]
        )
        raise
```

### Pattern 2: Email Notifications

**Best for**: Executive summaries and reports

```python
@task(retries=3, retry_delay_seconds=60)
def send_email_alert(
    to_email: str,
    subject: str,
    body_html: str
):
    """
    Send email alert via Loops.so.
    """
    response = httpx.post(
        "https://app.loops.so/api/v1/transactional",
        headers={"Authorization": f"Bearer {LOOPS_API_KEY}"},
        json={
            "transactionalId": "alert-template",
            "email": to_email,
            "dataVariables": {
                "subject": subject,
                "body": body_html
            }
        },
        timeout=30
    )
    response.raise_for_status()

@flow(name="daily-report-with-email")
def daily_report_with_email():
    """Daily marketing report sent via email."""

    # Gather metrics
    metrics = gather_daily_metrics()

    # Generate HTML report
    report_html = f"""
    <h2>Daily Marketing Report - {datetime.now().strftime('%Y-%m-%d')}</h2>
    <table>
        <tr><td>Total Spend:</td><td>${metrics['total_spend']:.2f}</td></tr>
        <tr><td>Total Conversions:</td><td>{metrics['total_conversions']}</td></tr>
        <tr><td>Cost Per Lead:</td><td>${metrics['cost_per_lead']:.2f}</td></tr>
        <tr><td>CTR:</td><td>{metrics['ctr']:.2f}%</td></tr>
    </table>
    """

    # Send email
    send_email_alert(
        to_email="team@yourdomain.com",
        subject=f"Marketing Report - {datetime.now().strftime('%Y-%m-%d')}",
        body_html=report_html
    )
```

### Pattern 3: Slack Integration

**Best for**: Team collaboration and threading

```python
@task(retries=2, retry_delay_seconds=10)
def send_slack_alert(channel: str, text: str, blocks: list = None):
    """
    Send alert to Slack channel.

    Requires Slack webhook or bot token.
    """
    payload = {
        "channel": channel,
        "text": text,
        "blocks": blocks
    }

    response = httpx.post(
        SLACK_WEBHOOK_URL,
        json=payload,
        timeout=10
    )
    response.raise_for_status()

@flow(name="hot-lead-slack-alert")
def hot_lead_slack_alert(lead_email: str, score: int, notion_id: str):
    """
    Alert sales team on Slack when hot lead appears.
    """
    send_slack_alert(
        channel="#sales-alerts",
        text=f"🔥 Hot Lead: {lead_email} (Score: {score})",
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Hot Lead Alert*\n🔥 Score: *{score}/100*"
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Email:*\n{lead_email}"},
                    {"type": "mrkdwn", "text": f"*Action:*\nImmediate follow-up"}
                ]
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "View in Notion"},
                        "url": f"https://notion.so/{notion_id}"
                    }
                ]
            }
        ]
    )
```

## Performance Monitoring

### Pattern 1: Execution Time Tracking

```python
import time
from prefect import flow, task

@task
def track_task_duration(task_name: str):
    """
    Context manager for tracking task duration.
    """
    class DurationTracker:
        def __enter__(self):
            self.start = time.time()
            return self

        def __exit__(self, *args):
            duration = time.time() - self.start
            print(f"⏱️ {task_name} took {duration:.2f}s")

            # Alert if too slow
            if duration > 60:  # 1 minute threshold
                send_discord_alert(
                    content="⚠️ **Performance Warning**",
                    title=f"Slow Task: {task_name}",
                    description=f"Took {duration:.2f}s (threshold: 60s)",
                    color=0xffff00
                )

    return DurationTracker()

@flow(name="monitored-campaign")
def monitored_campaign():
    """Campaign with performance monitoring."""

    # Track email sending
    with track_task_duration("send_batch_emails"):
        send_batch_emails(leads)

    # Track database queries
    with track_task_duration("query_notion_leads"):
        leads = query_notion_leads()

    # Track API calls
    with track_task_duration("facebook_ads_sync"):
        sync_facebook_ads()
```

### Pattern 2: Resource Usage Monitoring

```python
import psutil
from prefect import flow, task

@task
def check_resource_usage():
    """
    Monitor CPU, memory, and disk usage.

    Alert if resources are constrained.
    """
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    # Check thresholds
    alerts = []

    if cpu_percent > 80:
        alerts.append(f"High CPU usage: {cpu_percent}%")

    if memory.percent > 85:
        alerts.append(f"High memory usage: {memory.percent}%")

    if disk.percent > 90:
        alerts.append(f"High disk usage: {disk.percent}%")

    # Send alerts
    if alerts:
        send_discord_alert(
            content="⚠️ **Resource Warning**",
            title="High Resource Usage",
            description="\n".join(alerts),
            color=0xffff00
        )

    return {
        "cpu_percent": cpu_percent,
        "memory_percent": memory.percent,
        "disk_percent": disk.percent
    }

@flow(name="campaign-with-resource-monitoring")
def campaign_with_resource_monitoring():
    """Campaign with resource monitoring."""

    # Check resources before execution
    pre_resources = check_resource_usage()

    # Execute campaign
    execute_campaign_logic()

    # Check resources after execution
    post_resources = check_resource_usage()
```

### Pattern 3: API Rate Limit Monitoring

```python
from collections import defaultdict
from datetime import datetime, timedelta

api_calls = defaultdict(list)

@task
def track_api_call(api_name: str, limit_per_minute: int):
    """
    Track API calls and alert when approaching rate limit.
    """
    now = datetime.now()

    # Clean old entries
    api_calls[api_name] = [
        ts for ts in api_calls[api_name]
        if now - ts < timedelta(minutes=1)
    ]

    # Record call
    api_calls[api_name].append(now)

    # Check threshold (80% of limit)
    if len(api_calls[api_name]) >= limit_per_minute * 0.8:
        send_discord_alert(
            content="⚠️ **Rate Limit Warning**",
            title=f"{api_name} API",
            description=f"Approaching rate limit: {len(api_calls[api_name])}/{limit_per_minute} calls/min",
            color=0xffff00
        )

@flow(name="campaign-with-rate-monitoring")
def campaign_with_rate_monitoring():
    """Campaign with API rate monitoring."""

    for lead in leads:
        # Track Loops.so API call (100 req/min limit)
        track_api_call("loops.so", 100)
        send_loops_email(lead["email"], template_id, variables)

        # Track Notion API call (3 req/sec = 180 req/min)
        track_api_call("notion", 180)
        update_lead(lead["notion_id"], properties)
```

## Error Detection & Recovery

### Pattern 1: Automatic Retry with Alerts

```python
@task(retries=3, retry_delay_seconds=60, retry_jitter_factor=0.5)
def api_call_with_alerts(endpoint: str, data: dict):
    """
    API call with automatic retry and failure alerts.
    """
    logger = get_run_logger()

    try:
        response = httpx.post(endpoint, json=data, timeout=30)
        response.raise_for_status()
        return response.json()

    except Exception as e:
        logger.error(f"API call failed: {e}")

        # Alert on failure (will retry)
        send_discord_alert(
            content="⚠️ **API Call Failed (Retrying)**",
            title=f"Error calling {endpoint}",
            description=str(e),
            color=0xffff00
        )

        raise  # Re-raise to trigger retry

@flow(name="campaign-with-retry-alerts")
def campaign_with_retry_alerts():
    """Campaign with retry alerts."""

    for lead in leads:
        try:
            api_call_with_alerts("https://api.example.com/lead", lead)
        except Exception as e:
            # Final failure after all retries
            send_discord_alert(
                content="❌ **API Call Failed (All Retries Exhausted)**",
                title="Critical Error",
                description=f"Failed to process lead {lead['email']}: {str(e)}",
                color=0xff0000
            )
```

### Pattern 2: Circuit Breaker with Alerts

```python
from datetime import datetime, timedelta

class CircuitBreaker:
    """Circuit breaker with alert integration."""

    def __init__(self, failure_threshold=5, timeout=300):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = "closed"

    def call(self, func, *args, **kwargs):
        """Call function with circuit breaker protection."""

        # Check if circuit should reset
        if self.state == "open":
            if datetime.now() - self.last_failure_time > timedelta(seconds=self.timeout):
                self.state = "half-open"
                self.failures = 0

                # Alert: Circuit testing
                send_discord_alert(
                    content="🔄 **Circuit Breaker: Testing**",
                    title="Half-Open State",
                    description="Testing if service recovered",
                    color=0xffff00
                )
            else:
                raise Exception("Circuit breaker: OPEN (too many failures)")

        # Attempt call
        try:
            result = func(*args, **kwargs)

            # Success - reset circuit
            if self.state == "half-open":
                self.state = "closed"

                # Alert: Circuit recovered
                send_discord_alert(
                    content="✅ **Circuit Breaker: Recovered**",
                    title="Closed State",
                    description="Service is healthy again",
                    color=0x00ff00
                )

            self.failures = 0
            return result

        except Exception as e:
            # Failure - increment counter
            self.failures += 1
            self.last_failure_time = datetime.now()

            if self.failures >= self.failure_threshold:
                self.state = "open"

                # Alert: Circuit opened
                send_discord_alert(
                    content="❌ **Circuit Breaker: OPEN**",
                    title="Too Many Failures",
                    description=f"{self.failures} consecutive failures detected",
                    color=0xff0000
                )

            raise
```

## Cost Tracking

### Pattern 1: API Usage Tracking

```python
from datetime import date

api_costs = {
    "loops.so": 0.001,  # $0.001 per email
    "notion": 0.0001,   # $0.0001 per API call
    "openai": 0.002,    # $0.002 per request (GPT-4 Turbo)
}

daily_usage = defaultdict(int)

@task
def track_api_cost(api_name: str):
    """
    Track API usage and cost.

    Alert if daily spend exceeds threshold.
    """
    today = date.today().isoformat()
    key = f"{today}:{api_name}"

    daily_usage[key] += 1

    # Calculate cost
    total_calls = daily_usage[key]
    total_cost = total_calls * api_costs[api_name]

    # Alert if threshold exceeded ($10/day per API)
    if total_cost > 10.00:
        send_discord_alert(
            content="💰 **Cost Alert**",
            title=f"{api_name} Daily Spend",
            description=f"Spent ${total_cost:.2f} today ({total_calls} calls)",
            color=0xff0000
        )

@flow(name="campaign-with-cost-tracking")
def campaign_with_cost_tracking():
    """Campaign with cost tracking."""

    for lead in leads:
        track_api_cost("loops.so")
        send_loops_email(lead["email"], template_id, variables)

        track_api_cost("notion")
        update_lead(lead["notion_id"], properties)
```

### Pattern 2: Budget Monitoring

```python
MONTHLY_BUDGET = 500.00  # $500/month

@task
def check_monthly_budget():
    """
    Check if monthly budget is approaching or exceeded.
    """
    # Calculate total spend this month
    total_spend = sum(
        daily_usage[key] * api_costs[api]
        for key in daily_usage
        if key.startswith(date.today().strftime("%Y-%m"))
        for api in api_costs
        if key.endswith(api)
    )

    # Check thresholds
    if total_spend >= MONTHLY_BUDGET:
        send_discord_alert(
            content="🚨 **BUDGET EXCEEDED**",
            title="Monthly Budget Alert",
            description=f"Spent ${total_spend:.2f} / ${MONTHLY_BUDGET:.2f}",
            color=0xff0000
        )
    elif total_spend >= MONTHLY_BUDGET * 0.8:
        send_discord_alert(
            content="⚠️ **Budget Warning**",
            title="80% Budget Used",
            description=f"Spent ${total_spend:.2f} / ${MONTHLY_BUDGET:.2f}",
            color=0xffff00
        )

@flow(name="daily-budget-check")
def daily_budget_check():
    """Daily budget monitoring."""
    check_monthly_budget()

# Schedule daily
daily_budget_check.serve(
    name="budget-monitor",
    cron="0 9 * * *"  # 9 AM daily
)
```

## Success Metrics

### Pattern 1: Campaign Performance Tracking

```python
@task
def track_campaign_metrics():
    """
    Track and report campaign performance metrics.
    """
    # Gather metrics from Notion
    metrics = {
        "total_leads": query_total_leads(),
        "hot_leads": query_hot_leads(),
        "conversions": query_conversions(),
        "email_open_rate": calculate_email_open_rate(),
        "click_through_rate": calculate_ctr(),
        "cost_per_lead": calculate_cost_per_lead()
    }

    # Send daily report
    send_discord_alert(
        content="📊 **Daily Campaign Metrics**",
        title=f"Performance - {date.today().isoformat()}",
        description="Consolidated metrics from all channels",
        color=0x0099ff,
        fields=[
            {"name": "Total Leads", "value": str(metrics["total_leads"]), "inline": True},
            {"name": "Hot Leads", "value": str(metrics["hot_leads"]), "inline": True},
            {"name": "Conversions", "value": str(metrics["conversions"]), "inline": True},
            {"name": "Open Rate", "value": f"{metrics['email_open_rate']:.1f}%", "inline": True},
            {"name": "CTR", "value": f"{metrics['click_through_rate']:.2f}%", "inline": True},
            {"name": "CPL", "value": f"${metrics['cost_per_lead']:.2f}", "inline": True}
        ]
    )

@flow(name="daily-metrics-report")
def daily_metrics_report():
    """Daily metrics tracking and reporting."""
    track_campaign_metrics()

# Schedule daily
daily_metrics_report.serve(
    name="metrics-report",
    cron="0 17 * * *"  # 5 PM daily
)
```

### Pattern 2: Anomaly Detection

```python
@task
def detect_anomalies():
    """
    Detect anomalies in campaign performance.

    Alert if metrics deviate significantly from baseline.
    """
    # Calculate baseline (last 7 days average)
    baseline = calculate_baseline_metrics(days=7)

    # Get today's metrics
    today = get_today_metrics()

    # Detect anomalies (>30% deviation)
    anomalies = []

    for metric, value in today.items():
        baseline_value = baseline.get(metric, 0)

        if baseline_value == 0:
            continue

        deviation = abs(value - baseline_value) / baseline_value

        if deviation > 0.30:  # 30% threshold
            anomalies.append({
                "metric": metric,
                "today": value,
                "baseline": baseline_value,
                "deviation": f"{deviation * 100:.1f}%"
            })

    # Alert if anomalies detected
    if anomalies:
        fields = [
            {
                "name": a["metric"],
                "value": f"Today: {a['today']} | Baseline: {a['baseline']} | Deviation: {a['deviation']}",
                "inline": False
            }
            for a in anomalies
        ]

        send_discord_alert(
            content="🔔 **Anomaly Detected**",
            title="Campaign Performance Anomaly",
            description="Significant deviation from baseline detected",
            color=0xffff00,
            fields=fields
        )

@flow(name="anomaly-detection-daily")
def anomaly_detection_daily():
    """Daily anomaly detection."""
    detect_anomalies()

# Schedule daily
anomaly_detection_daily.serve(
    name="anomaly-detector",
    cron="0 18 * * *"  # 6 PM daily
)
```

## Best Practices

### 1. Alert Fatigue Prevention

```python
# DON'T: Alert on every minor issue
@task
def bad_alerting():
    for lead in leads:
        send_discord_alert("Processing lead...")  # Too many alerts

# DO: Batch alerts and use appropriate severity
@task
def good_alerting():
    # Process all leads
    results = process_all_leads()

    # Single summary alert
    if results["failed"] > 0:
        send_discord_alert(
            content="⚠️ Some leads failed",
            title=f"{results['failed']}/{results['total']} leads failed",
            color=0xffff00
        )
```

### 2. Alert Routing by Severity

```python
def send_alert_by_severity(severity: str, title: str, description: str):
    """
    Route alerts based on severity.

    - critical → Slack + Email + Discord
    - warning → Discord only
    - info → Log only
    """
    if severity == "critical":
        send_slack_alert("#critical-alerts", title)
        send_email_alert("team@example.com", title, description)
        send_discord_alert(title, description, color=0xff0000)

    elif severity == "warning":
        send_discord_alert(title, description, color=0xffff00)

    elif severity == "info":
        print(f"INFO: {title} - {description}")
```

### 3. Monitoring Dashboard

```python
@flow(name="monitoring-dashboard")
def monitoring_dashboard():
    """
    Centralized monitoring dashboard.

    Runs every 5 minutes, checks all systems.
    """
    # Check flow health
    flow_health = check_all_flows_status()

    # Check API health
    api_health = check_api_endpoints()

    # Check resource usage
    resource_health = check_resource_usage()

    # Check cost
    cost_status = check_monthly_budget()

    # Generate dashboard
    dashboard = {
        "flows": flow_health,
        "apis": api_health,
        "resources": resource_health,
        "cost": cost_status
    }

    # Alert if any issues
    if any(
        dashboard["flows"]["failed"] > 0,
        not dashboard["apis"]["all_healthy"],
        dashboard["resources"]["cpu_percent"] > 80
    ):
        send_discord_alert(
            content="⚠️ **System Health Warning**",
            title="Monitoring Dashboard Alert",
            description="One or more systems need attention",
            color=0xffff00
        )

# Run every 5 minutes
monitoring_dashboard.serve(
    name="dashboard-monitor",
    cron="*/5 * * * *"
)
```

## Resources

- [Prefect Logging Documentation](https://docs.prefect.io/latest/concepts/logs/)
- [Discord Webhook Guide](https://discord.com/developers/docs/resources/webhook)
- [Slack Webhook Documentation](https://api.slack.com/messaging/webhooks)
- [Observability Best Practices](https://sre.google/workbook/monitoring/)

## Next Steps

1. ✅ Set up Discord webhook for team alerts
2. ✅ Implement performance tracking for critical flows
3. ✅ Configure budget monitoring and thresholds
4. ✅ Create daily/weekly reporting flows
5. ✅ Set up anomaly detection baselines
6. ✅ Test alert routing and severity levels
