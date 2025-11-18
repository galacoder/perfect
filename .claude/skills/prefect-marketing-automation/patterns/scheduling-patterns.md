# Scheduling Patterns for Prefect Marketing Automation

## Overview

Prefect v3 supports multiple scheduling patterns for marketing automation flows. This guide covers cron expressions, interval-based scheduling, RRule (recurrence rules), and event-driven triggers.

## Scheduling Methods

### 1. Cron Expressions

**Best for:** Fixed time schedules (daily, weekly, monthly)

```python
from prefect import flow

@flow
def daily_report():
    """Generate daily marketing report."""
    # Flow implementation

# Deploy with cron schedule
daily_report.serve(
    name="daily-report-v1",
    cron="0 8 * * *",  # Daily at 8:00 AM
    description="Daily marketing performance report"
)
```

**Common Cron Patterns:**

```python
# Every hour
cron="0 * * * *"

# Every day at 9 AM
cron="0 9 * * *"

# Every Monday at 9 AM
cron="0 9 * * 1"

# First day of month at midnight
cron="0 0 1 * *"

# Every 15 minutes
cron="*/15 * * * *"

# Weekdays at 8 AM (Mon-Fri)
cron="0 8 * * 1-5"

# Every 6 hours
cron="0 */6 * * *"
```

**Cron Format Reference:**
```
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day of month (1 - 31)
│ │ │ ┌───────────── month (1 - 12)
│ │ │ │ ┌───────────── day of week (0 - 6) (Sunday=0)
│ │ │ │ │
* * * * *
```

### 2. Interval Scheduling

**Best for:** Regular intervals independent of clock time

```python
from datetime import timedelta

@flow
def hourly_lead_scoring():
    """Score leads every hour."""
    # Flow implementation

# Deploy with interval schedule
hourly_lead_scoring.serve(
    name="lead-scoring-hourly",
    interval=timedelta(hours=1),  # Every hour
    description="Hourly lead scoring update"
)
```

**Common Interval Patterns:**

```python
# Every 30 seconds (testing)
interval=timedelta(seconds=30)

# Every 5 minutes
interval=timedelta(minutes=5)

# Every hour
interval=timedelta(hours=1)

# Every 6 hours
interval=timedelta(hours=6)

# Every day
interval=timedelta(days=1)

# Every week
interval=timedelta(weeks=1)
```

### 3. RRule (Recurrence Rules)

**Best for:** Complex recurring patterns

```python
from dateutil.rrule import rrule, DAILY, WEEKLY, MONTHLY

@flow
def complex_campaign():
    """Campaign with complex schedule."""
    # Flow implementation

# Deploy with RRule schedule
complex_campaign.serve(
    name="complex-campaign-v1",
    rrule="FREQ=WEEKLY;BYDAY=MO,WE,FR;BYHOUR=9",  # Mon, Wed, Fri at 9 AM
    description="Runs Monday, Wednesday, Friday at 9 AM"
)
```

**Common RRule Patterns:**

```python
# Every weekday (Mon-Fri)
rrule="FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR"

# First Monday of every month
rrule="FREQ=MONTHLY;BYDAY=1MO"

# Last day of every month
rrule="FREQ=MONTHLY;BYMONTHDAY=-1"

# Every other week on Tuesday
rrule="FREQ=WEEKLY;INTERVAL=2;BYDAY=TU"

# Quarterly (every 3 months)
rrule="FREQ=MONTHLY;INTERVAL=3"

# Business hours (9 AM - 5 PM, Mon-Fri)
rrule="FREQ=HOURLY;BYHOUR=9,10,11,12,13,14,15,16,17;BYDAY=MO,TU,WE,TH,FR"
```

### 4. Event-Driven Triggers

**Best for:** Webhooks, lead events, campaign triggers

```python
from prefect.deployments import DeploymentEventTrigger

@flow
def handle_new_lead(email: str, first_name: str, notion_id: str):
    """Triggered when new lead opts in."""
    # Flow implementation

# Deploy with event trigger
handle_new_lead.serve(
    name="new-lead-handler",
    triggers=[
        DeploymentEventTrigger(
            match={"prefect.resource.id": "lead.*"},
            expect=["lead.opted_in"],
            parameters={
                "email": "{{ event.payload.email }}",
                "first_name": "{{ event.payload.first_name }}",
                "notion_id": "{{ event.payload.notion_id }}"
            }
        )
    ],
    description="Triggered when lead opts in"
)
```

**Event Trigger Patterns:**

```python
# Trigger on multiple events
triggers=[
    DeploymentEventTrigger(
        match={"prefect.resource.id": "lead.*"},
        expect=["lead.opted_in", "lead.assessment_complete"],
        parameters={
            "email": "{{ event.payload.email }}",
            "stage": "{{ event.payload.stage }}"
        }
    )
]

# Trigger on resource pattern
triggers=[
    DeploymentEventTrigger(
        match={"prefect.resource.id": "campaign.*"},
        expect=["campaign.published"],
        parameters={
            "campaign_id": "{{ event.payload.campaign_id }}"
        }
    )
]
```

## Marketing Automation Scheduling Patterns

### Pattern 1: Daily Morning Report (Cron)

```python
@flow
def daily_marketing_report():
    """Daily report at 8 AM."""
    # Generate report logic

daily_marketing_report.serve(
    name="daily-report-8am",
    cron="0 8 * * *",  # 8:00 AM every day
    description="Daily marketing metrics report"
)
```

**Use Cases:**
- Daily performance summaries
- Overnight lead processing
- Morning analytics reports

### Pattern 2: Hourly Lead Scoring (Interval)

```python
@flow
def score_active_leads():
    """Score leads every hour."""
    # Scoring logic

score_active_leads.serve(
    name="lead-scoring-hourly",
    interval=timedelta(hours=1),
    description="Hourly lead scoring update"
)
```

**Use Cases:**
- Real-time lead scoring
- Activity monitoring
- Engagement tracking

### Pattern 3: Weekly Campaign Review (RRule)

```python
@flow
def weekly_campaign_review():
    """Review campaigns every Monday."""
    # Review logic

weekly_campaign_review.serve(
    name="weekly-review-monday",
    rrule="FREQ=WEEKLY;BYDAY=MO;BYHOUR=9",
    description="Weekly campaign review every Monday at 9 AM"
)
```

**Use Cases:**
- Weekly performance analysis
- Campaign optimization
- ROI reporting

### Pattern 4: Business Hours Only (RRule)

```python
@flow
def business_hours_check():
    """Run every hour during business hours."""
    # Check logic

business_hours_check.serve(
    name="business-hours-monitor",
    rrule="FREQ=HOURLY;BYHOUR=9,10,11,12,13,14,15,16,17;BYDAY=MO,TU,WE,TH,FR",
    description="Runs every hour, 9 AM - 5 PM, Mon-Fri"
)
```

**Use Cases:**
- Sales team alerts
- Hot lead notifications
- Support hours monitoring

### Pattern 5: Event-Driven Nurture (Event Trigger)

```python
@flow
def trigger_nurture_sequence(email: str, first_name: str, notion_id: str):
    """Triggered when lead completes assessment."""
    # Nurture sequence logic

trigger_nurture_sequence.serve(
    name="nurture-on-assessment",
    triggers=[
        DeploymentEventTrigger(
            match={"prefect.resource.id": "lead.*"},
            expect=["lead.assessment_complete"],
            parameters={
                "email": "{{ event.payload.email }}",
                "first_name": "{{ event.payload.first_name }}",
                "notion_id": "{{ event.payload.notion_id }}"
            }
        )
    ]
)
```

**Use Cases:**
- Immediate follow-up actions
- Triggered email sequences
- Real-time routing

## Advanced Patterns

### Multiple Schedules (Hybrid)

```python
@flow
def flexible_campaign():
    """Campaign with multiple triggers."""
    # Campaign logic

# Option 1: Scheduled daily
flexible_campaign.serve(
    name="campaign-scheduled",
    cron="0 9 * * *"
)

# Option 2: Manual trigger via event
flexible_campaign.serve(
    name="campaign-manual",
    triggers=[
        DeploymentEventTrigger(
            match={"prefect.resource.id": "campaign.manual"},
            expect=["trigger.now"]
        )
    ]
)
```

### Conditional Scheduling (Time-Based Logic)

```python
from datetime import datetime

@flow
def smart_campaign():
    """Campaign with conditional logic."""

    now = datetime.now()

    # Weekend behavior
    if now.weekday() >= 5:  # Saturday=5, Sunday=6
        print("Weekend mode: reduced activity")
        run_light_campaign()
    # Weekday behavior
    else:
        print("Weekday mode: full campaign")
        run_full_campaign()

smart_campaign.serve(
    name="smart-campaign-daily",
    cron="0 9 * * *"  # Runs daily, decides behavior internally
)
```

### Staggered Execution (Avoid Overlap)

```python
# Campaign 1: Runs at 8:00 AM
campaign_1.serve(name="campaign-1", cron="0 8 * * *")

# Campaign 2: Runs at 8:30 AM (30 min after)
campaign_2.serve(name="campaign-2", cron="30 8 * * *")

# Campaign 3: Runs at 9:00 AM (1 hour after first)
campaign_3.serve(name="campaign-3", cron="0 9 * * *")
```

## Best Practices

### 1. Choose the Right Scheduling Method

| Use Case | Best Method | Example |
|----------|-------------|---------|
| Fixed daily time | Cron | Daily report at 8 AM |
| Regular intervals | Interval | Every hour lead scoring |
| Complex patterns | RRule | First Monday of month |
| Real-time actions | Event Trigger | New lead handler |

### 2. Consider Timezone

```python
# Prefect uses UTC by default
# Convert local time to UTC

# If local time is 9 AM PST (UTC-8):
# UTC equivalent is 5 PM (17:00)
cron="0 17 * * *"  # 9 AM PST = 5 PM UTC
```

### 3. Avoid Resource Contention

```python
# DON'T: Multiple flows at same time
flow1.serve(cron="0 9 * * *")
flow2.serve(cron="0 9 * * *")
flow3.serve(cron="0 9 * * *")

# DO: Stagger execution
flow1.serve(cron="0 9 * * *")
flow2.serve(cron="15 9 * * *")
flow3.serve(cron="30 9 * * *")
```

### 4. Handle Missed Runs

```python
# Prefect automatically handles missed runs
# No special configuration needed

@flow
def resilient_campaign():
    """Campaign handles missed runs gracefully."""

    # Check last run time
    last_run = get_last_run_time()

    if last_run:
        catchup_period = datetime.now() - last_run
        if catchup_period > timedelta(hours=2):
            print(f"Catching up from {catchup_period} ago")
            # Handle backlog

    # Normal execution
    run_campaign()
```

## Testing Schedules

### Test with Manual Triggers

```python
# Deploy without schedule first
test_flow.serve(name="test-flow-manual")

# Test manually via Prefect UI or API
# Then add schedule once verified

test_flow.serve(
    name="test-flow-scheduled",
    cron="0 9 * * *"
)
```

### Test with Shorter Intervals

```python
# Development: Run every minute
dev_flow.serve(
    name="dev-flow",
    interval=timedelta(minutes=1)
)

# Production: Run every hour
prod_flow.serve(
    name="prod-flow",
    interval=timedelta(hours=1)
)
```

## Monitoring Schedules

```python
from prefect import get_run_logger

@flow
def monitored_campaign():
    """Campaign with logging."""

    logger = get_run_logger()

    logger.info(f"Campaign started at {datetime.now()}")
    logger.info(f"Next run scheduled at: {get_next_run_time()}")

    # Campaign logic

    logger.info(f"Campaign completed at {datetime.now()}")
```

## Resources

- [Prefect Scheduling Documentation](https://docs.prefect.io/latest/concepts/schedules/)
- [Cron Expression Generator](https://crontab.guru/)
- [RRule Specification](https://icalendar.org/iCalendar-RFC-5545/3-8-5-3-recurrence-rule.html)
- [Python dateutil.rrule](https://dateutil.readthedocs.io/en/stable/rrule.html)

## Next Steps

1. ✅ Choose scheduling method for your use case
2. ✅ Test schedule with manual triggers first
3. ✅ Deploy with appropriate schedule
4. ✅ Monitor execution and adjust as needed
5. ✅ Add conditional logic for special cases
