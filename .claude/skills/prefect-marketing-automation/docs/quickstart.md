# Quickstart Guide - Prefect Marketing Automation

Get your first marketing automation flow running in 5 minutes.

---

## Prerequisites

Before you begin, ensure you have:

- **Python 3.9+** installed
- **Prefect 3.4+** installed (`pip install prefect>=3.4.1`)
- **Self-hosted Prefect server** running (or use Prefect Cloud)
- **API keys** for your marketing tools (Loops.so, Notion, Discord, etc.)

---

## Step 1: Install Dependencies (1 min)

```bash
# Install Prefect and required libraries
pip install prefect>=3.4.1 httpx notion-client python-dotenv

# Verify installation
prefect version
# Should output: Version: 3.4.1 or higher
```

---

## Step 2: Set Up Environment Variables (1 min)

Create a `.env` file in your project directory:

```bash
# .env file
PREFECT_API_URL=http://localhost:4200/api  # Your self-hosted Prefect server

# Marketing Tools
LOOPS_API_KEY=your_loops_api_key_here
NOTION_API_KEY=your_notion_integration_key_here
NOTION_DATABASE_ID=your_notion_database_id_here
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your_webhook_url

# Social Media (optional for quickstart)
FACEBOOK_ACCESS_TOKEN=your_facebook_token
TWITTER_API_KEY=your_twitter_api_key
LINKEDIN_ACCESS_TOKEN=your_linkedin_token
```

**Quick Setup Tips:**
- **Loops.so**: Get API key from [Loops.so Settings](https://loops.so/settings/api)
- **Notion**: Create integration at [Notion Integrations](https://www.notion.so/my-integrations)
- **Discord**: Create webhook in Discord channel settings → Integrations → Webhooks

---

## Step 3: Copy a Template Flow (1 min)

Copy one of the example flows from this skill to your project:

```bash
# Create your project directory
mkdir my-marketing-automation
cd my-marketing-automation

# Copy the simple lead magnet flow
cp ~/.claude/skills/prefect-marketing-automation/examples/lead-magnet-funnel.py ./my_first_flow.py
```

Or create a minimal flow from scratch:

```python
# my_first_flow.py
from prefect import flow, task
import httpx
import os

@task
def send_welcome_email(email: str, first_name: str):
    """Send welcome email via Loops.so"""
    response = httpx.post(
        "https://app.loops.so/api/v1/transactional",
        headers={"Authorization": f"Bearer {os.getenv('LOOPS_API_KEY')}"},
        json={
            "email": email,
            "transactionalId": "welcome-email-template-id",
            "dataVariables": {"first_name": first_name}
        }
    )
    response.raise_for_status()
    return {"status": "sent", "email": email}

@flow(name="welcome-flow", log_prints=True)
def welcome_new_lead(email: str, first_name: str):
    """Simple flow to welcome a new lead"""
    print(f"Processing new lead: {first_name} ({email})")
    result = send_welcome_email(email, first_name)
    print(f"Welcome email sent to {email}")
    return result

if __name__ == "__main__":
    # Test the flow locally
    welcome_new_lead.serve(name="welcome-deployment")
```

---

## Step 4: Deploy Your Flow (1 min)

Deploy your flow to your Prefect server:

```bash
# Start your Prefect server (if not already running)
prefect server start

# In another terminal, deploy the flow
python my_first_flow.py
```

You should see:

```
Your flow 'welcome-flow' is being served and polling for scheduled runs!

To trigger a run for this flow, use the following command:

    $ prefect deployment run 'welcome-flow/welcome-deployment'

You can also run your flow via the Prefect UI: http://localhost:4200/deployments
```

---

## Step 5: Trigger Your First Run (1 min)

### Option A: Via Command Line

```bash
prefect deployment run 'welcome-flow/welcome-deployment' \
  --params '{"email": "test@example.com", "first_name": "John"}'
```

### Option B: Via Prefect UI

1. Open http://localhost:4200 in your browser
2. Navigate to **Deployments** → **welcome-flow/welcome-deployment**
3. Click **Quick Run**
4. Enter parameters:
   - `email`: test@example.com
   - `first_name`: John
5. Click **Run**

### Option C: Via Python API

```python
from prefect.deployments import run_deployment

run_deployment(
    name="welcome-flow/welcome-deployment",
    parameters={"email": "test@example.com", "first_name": "John"}
)
```

---

## Step 6: View Results (30 seconds)

Watch your flow execute in real-time:

1. **Prefect UI**: Navigate to **Flow Runs** → Select your run
2. **Check logs**: See task execution and print statements
3. **Verify email**: Check if test email was sent via Loops.so
4. **Monitor status**: ✅ Completed, ⏳ Running, ❌ Failed

---

## 🎉 Congratulations!

You've successfully:
- ✅ Installed Prefect
- ✅ Deployed your first marketing automation flow
- ✅ Triggered a test run
- ✅ Sent an automated email via Loops.so

---

## Next Steps

### 1. **Explore Templates** (5-10 min)

Try more advanced templates from this skill:

```bash
# Email nurture sequence (7-email Soap Opera)
python ~/.claude/skills/prefect-marketing-automation/templates/email-nurture-sequence.py

# Lead scoring pipeline
python ~/.claude/skills/prefect-marketing-automation/templates/lead-scoring-pipeline.py

# Retargeting orchestrator
python ~/.claude/skills/prefect-marketing-automation/templates/retargeting-orchestrator.py
```

### 2. **Set Up Event-Driven Triggers** (10 min)

Convert your flow to event-driven automation:

```python
from prefect.events import DeploymentEventTrigger

# Add to your flow deployment:
welcome_new_lead.serve(
    name="welcome-deployment",
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

Now your flow triggers automatically when leads opt in via webhook.

### 3. **Integrate with Notion CRM** (10 min)

Add Notion integration to store lead data:

```python
from notion_client import Client

@task
def create_lead_in_notion(email: str, first_name: str):
    notion = Client(auth=os.getenv("NOTION_API_KEY"))
    notion.pages.create(
        parent={"database_id": os.getenv("NOTION_DATABASE_ID")},
        properties={
            "Email": {"email": email},
            "First Name": {"title": [{"text": {"content": first_name}}]},
            "Status": {"select": {"name": "New Lead"}},
            "Lead Score": {"number": 0}
        }
    )
```

See full guide: [Integration: Notion CRM Setup](../integrations/notion-connector.md)

### 4. **Add Scheduling** (5 min)

Schedule your flows to run automatically:

```python
# Run daily at 9 AM
welcome_new_lead.serve(name="welcome-deployment", cron="0 9 * * *")

# Run every 2 hours
welcome_new_lead.serve(name="welcome-deployment", interval=7200)  # seconds
```

See full guide: [Pattern: Scheduling Patterns](../patterns/scheduling-patterns.md)

### 5. **Set Up Monitoring** (10 min)

Add Discord notifications for flow status:

```python
@task
def send_discord_notification(message: str):
    httpx.post(
        os.getenv("DISCORD_WEBHOOK_URL"),
        json={"content": f"🚀 {message}"}
    )

@flow
def welcome_new_lead(email: str, first_name: str):
    try:
        result = send_welcome_email(email, first_name)
        send_discord_notification(f"✅ Welcome email sent to {first_name}")
        return result
    except Exception as e:
        send_discord_notification(f"❌ Failed to send email: {str(e)}")
        raise
```

See full guide: [Pattern: Monitoring & Alerts](../patterns/monitoring-alerts.md)

---

## Complete Examples

For production-ready flows, check out these complete examples:

1. **Christmas Campaign Flow** - Full campaign automation with event-driven triggers, nurture sequences, retargeting, and analytics
   - File: `examples/christmas-campaign-flow.py`
   - Features: 5 coordinated flows, lead scoring, Facebook retargeting

2. **8-System Assessment Flow** - Lead magnet delivery with personalized scoring
   - File: `examples/8-system-assessment-flow.py`
   - Features: Weighted scoring, hot lead alerts, personalized insights

3. **Multi-Channel Launch Blast** - Coordinated Twitter, LinkedIn, Facebook + email
   - File: `examples/multi-channel-blast.py`
   - Features: Parallel social posting, email blast, Notion calendar integration

---

## Resources

- **Integration Guides**: `integrations/` directory
- **Pattern Guides**: `patterns/` directory
- **Templates**: `templates/` directory
- **Troubleshooting**: [docs/troubleshooting.md](./troubleshooting.md)
- **Best Practices**: [docs/best-practices.md](./best-practices.md)
- **Deployment Guide**: [docs/deployment-guide.md](./deployment-guide.md)

---

## Getting Help

**Common Issues:**
- Flow not triggering? Check deployment status in Prefect UI
- Email not sending? Verify Loops.so API key and template ID
- Webhook not working? Verify event trigger configuration

See [Troubleshooting Guide](./troubleshooting.md) for solutions.

**Need More Help?**
- Check Prefect docs: https://docs.prefect.io
- Review example flows in `examples/` directory
- Consult integration guides in `integrations/` directory
