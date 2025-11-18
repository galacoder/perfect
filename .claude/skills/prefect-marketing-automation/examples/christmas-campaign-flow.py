#!/usr/bin/env python3
"""
Complete Christmas Campaign Automation
=====================================

Production-ready example demonstrating:
- Full campaign orchestration from opt-in to conversion
- Integration with Loops.so, Notion, Discord, Facebook Ads
- Event-driven triggers and scheduled flows
- 7-email Soap Opera nurture sequence
- 4-audience retargeting strategy
- Lead scoring and routing
- Multi-platform social media posting
- Analytics consolidation and reporting

Aligned with Christmas campaign framework and Hormozi/Brunson methodologies.

Prerequisites:
--------------
1. Environment variables set:
   - LOOPS_API_KEY
   - NOTION_API_KEY
   - DISCORD_WEBHOOK_URL
   - FB_ACCESS_TOKEN
   - FB_AD_ACCOUNT_ID
   - TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET
   - LINKEDIN_ACCESS_TOKEN
   - FB_PAGE_ACCESS_TOKEN

2. Notion databases created:
   - Leads database
   - Visitors database
   - Content Calendar database
   - Analytics Dashboard database

3. Loops.so email templates created:
   - email-1-immediate-cta
   - email-2-high-drama
   - email-3-epiphany-bridge
   - email-4-hidden-benefits
   - email-5-urgency-scarcity
   - email-6-social-proof
   - email-7-last-chance

4. Prefect server running:
   prefect server start

Usage:
------
1. Deploy all flows:
   python christmas-campaign-flow.py

2. Test lead opt-in trigger:
   from prefect.events import emit_event
   emit_event(
       event="lead.opted_in",
       resource={"prefect.resource.id": "lead.test@example.com"},
       payload={
           "email": "test@example.com",
           "first_name": "Test",
           "phone": "+1234567890",
           "visitor_id": "visitor-123",
           "segment": "beauty-salon"
       }
   )

3. Monitor in Prefect UI:
   http://localhost:4200

Author: Marketing Automation Team
Date: 2025-01-10
Version: 1.0.0
"""

import os
import httpx
import hashlib
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from prefect import flow, task, get_run_logger
from prefect.deployments import DeploymentEventTrigger
from notion_client import Client
from notion_client.errors import APIResponseError

# ============================================================================
# Configuration
# ============================================================================

# API Keys (from environment)
LOOPS_API_KEY = os.getenv("LOOPS_API_KEY")
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
FB_AD_ACCOUNT_ID = os.getenv("FB_AD_ACCOUNT_ID")

# Notion Database IDs
NOTION_LEADS_DB_ID = os.getenv("NOTION_LEADS_DB_ID")
NOTION_VISITORS_DB_ID = os.getenv("NOTION_VISITORS_DB_ID")
NOTION_CONTENT_DB_ID = os.getenv("NOTION_CONTENT_DB_ID")
NOTION_ANALYTICS_DB_ID = os.getenv("NOTION_ANALYTICS_DB_ID")

# Email Sequence Configuration (Soap Opera Sequence - Brunson/Hormozi timing)
EMAIL_SEQUENCE = [
    {"day": 0, "template_id": "email-1-immediate-cta", "subject": "Your Free Assessment is Ready"},
    {"day": 3, "template_id": "email-2-high-drama", "subject": "The #1 Mistake Businesses Make"},
    {"day": 7, "template_id": "email-3-epiphany-bridge", "subject": "The Day Everything Changed for Me"},
    {"day": 14, "template_id": "email-4-hidden-benefits", "subject": "What Nobody Tells You About Growth"},
    {"day": 21, "template_id": "email-5-urgency-scarcity", "subject": "Only 3 Spots Left This Month"},
    {"day": 21, "template_id": "email-6-social-proof", "subject": "How [Client] Went from $50K to $500K"},
    {"day": 28, "template_id": "email-7-last-chance", "subject": "Last Call - Decision Time"}
]

# ============================================================================
# Core Integration Tasks
# ============================================================================

@task(retries=3, retry_delay_seconds=60, retry_jitter_factor=0.5)
def send_loops_email(to_email: str, template_id: str, variables: dict):
    """Send email via Loops.so API with retry logic."""
    logger = get_run_logger()

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
    logger.info(f"✅ Sent email '{template_id}' to {to_email}")
    return response.json()

@task(retries=3, retry_delay_seconds=30)
def create_lead_in_notion(email: str, first_name: str, visitor_id: str, phone: Optional[str] = None, segment: str = "general"):
    """Create new lead record in Notion CRM."""
    logger = get_run_logger()
    notion = Client(auth=NOTION_API_KEY)

    lead_record = notion.pages.create(
        parent={"database_id": NOTION_LEADS_DB_ID},
        properties={
            "Email": {"title": [{"text": {"content": email}}]},
            "Name": {"rich_text": [{"text": {"content": first_name}}]},
            "Phone": {"phone_number": phone} if phone else {"phone_number": None},
            "Visitor ID": {"rich_text": [{"text": {"content": visitor_id}}]},
            "Created": {"date": {"start": datetime.now().isoformat()}},
            "Stage": {"select": {"name": "opted_in"}},
            "Score": {"number": 0},
            "Status": {"select": {"name": "new"}},
            "Priority": {"select": {"name": "medium"}},
            "Email Stage": {"number": 0},
            "Engagement Score": {"number": 0},
            "Segment": {"select": {"name": segment}}
        }
    )

    logger.info(f"✅ Created lead in Notion: {email}")
    return {"notion_id": lead_record["id"], "email": email, "first_name": first_name}

@task(retries=2, retry_delay_seconds=30)
def update_lead_in_notion(notion_id: str, properties: dict):
    """Update existing lead record in Notion."""
    logger = get_run_logger()
    notion = Client(auth=NOTION_API_KEY)

    # Build Notion property format
    notion_props = {}

    if "score" in properties:
        notion_props["Score"] = {"number": properties["score"]}
    if "status" in properties:
        notion_props["Status"] = {"select": {"name": properties["status"]}}
    if "priority" in properties:
        notion_props["Priority"] = {"select": {"name": properties["priority"]}}
    if "stage" in properties:
        notion_props["Stage"] = {"select": {"name": properties["stage"]}}
    if "email_stage" in properties:
        notion_props["Email Stage"] = {"number": properties["email_stage"]}
    if "last_email_sent" in properties:
        notion_props["Last Email"] = {"date": {"start": properties["last_email_sent"]}}

    notion.pages.update(page_id=notion_id, properties=notion_props)
    logger.info(f"✅ Updated lead in Notion: {notion_id}")

@task(retries=2, retry_delay_seconds=10)
def send_discord_notification(content: str, title: str, description: str, color: int = 0x0099ff, fields: list = None):
    """Send notification to Discord channel."""
    logger = get_run_logger()

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
    logger.info(f"✅ Sent Discord notification: {title}")

@task(retries=3, retry_delay_seconds=60)
def add_to_facebook_custom_audience(audience_name: str, user_data: List[Dict]):
    """Add users to Facebook Custom Audience for retargeting."""
    logger = get_run_logger()

    # Hash user data for privacy
    hashed_users = []
    for user in user_data:
        hashed = {}
        if "email" in user:
            hashed["em"] = hashlib.sha256(user["email"].lower().encode()).hexdigest()
        if "phone" in user:
            hashed["ph"] = hashlib.sha256(user["phone"].encode()).hexdigest()
        hashed_users.append(hashed)

    # Find or create custom audience
    response = httpx.post(
        f"https://graph.facebook.com/v18.0/act_{FB_AD_ACCOUNT_ID}/customaudiences",
        params={
            "access_token": FB_ACCESS_TOKEN,
            "name": audience_name,
            "subtype": "CUSTOM",
            "customer_file_source": "USER_PROVIDED_ONLY"
        },
        timeout=30
    )

    audience_id = response.json().get("id")

    # Add users to audience
    httpx.post(
        f"https://graph.facebook.com/v18.0/{audience_id}/users",
        json={
            "payload": {"data": hashed_users},
            "access_token": FB_ACCESS_TOKEN
        },
        timeout=30
    )

    logger.info(f"✅ Added {len(hashed_users)} users to Facebook audience '{audience_name}'")
    return {"audience_id": audience_id, "users_added": len(hashed_users)}

# ============================================================================
# Flow 1: Lead Opt-In Handler (Event-Driven)
# ============================================================================

@flow(name="christmas-lead-optin-handler", log_prints=True)
def handle_lead_optin(email: str, first_name: str, phone: str, visitor_id: str, segment: str = "general"):
    """
    Event-driven flow triggered when lead opts in.

    Actions:
    1. Create lead in Notion CRM
    2. Send immediate CTA email (Day 0)
    3. Add to Facebook retargeting audience
    4. Send Discord notification
    5. Update visitor stage
    """
    logger = get_run_logger()
    logger.info(f"🎄 Processing opt-in for {email} ({segment})")

    # 1. Create lead in Notion
    lead_data = create_lead_in_notion(email, first_name, visitor_id, phone, segment)

    # 2. Send immediate CTA email (Day 0)
    send_loops_email(
        to_email=email,
        template_id="email-1-immediate-cta",
        variables={"first_name": first_name, "assessment_url": "https://yourdomain.com/assessment"}
    )

    # Update email stage
    update_lead_in_notion(lead_data["notion_id"], {
        "email_stage": 1,
        "last_email_sent": datetime.now().isoformat()
    })

    # 3. Add to Facebook retargeting audience
    add_to_facebook_custom_audience("opted_in_leads", [{"email": email, "phone": phone}])

    # 4. Send Discord notification
    send_discord_notification(
        content="🎁 **New Lead Opt-In**",
        title=f"{first_name} - {segment}",
        description=f"New lead from {segment} segment",
        color=0x00ff00,
        fields=[
            {"name": "Email", "value": email, "inline": True},
            {"name": "Segment", "value": segment, "inline": True},
            {"name": "Phone", "value": phone or "Not provided", "inline": True}
        ]
    )

    logger.info(f"✅ Opt-in processing complete for {email}")
    return {"status": "success", "notion_id": lead_data["notion_id"]}

# ============================================================================
# Flow 2: Assessment Completion Handler (Event-Driven)
# ============================================================================

@task
def calculate_assessment_score(assessment_data: dict) -> int:
    """
    Calculate lead score based on 8-System assessment responses.

    Each system scored 0-12 points, total 0-100.
    """
    scores = {
        "strategy": assessment_data.get("strategy", 0),
        "team": assessment_data.get("team", 0),
        "revenue": assessment_data.get("revenue", 0),
        "marketing": assessment_data.get("marketing", 0),
        "operations": assessment_data.get("operations", 0),
        "finance": assessment_data.get("finance", 0),
        "technology": assessment_data.get("technology", 0),
        "leadership": assessment_data.get("leadership", 0)
    }

    # Weight each system (total 100 points)
    total_score = sum(scores.values())

    # Normalize to 0-100
    normalized_score = min(100, max(0, total_score))

    return normalized_score

@flow(name="christmas-assessment-completion", log_prints=True)
def handle_assessment_completion(notion_id: str, email: str, first_name: str, assessment_data: dict):
    """
    Event-driven flow triggered when lead completes assessment.

    Actions:
    1. Calculate lead score (0-100)
    2. Update lead in Notion with score and status
    3. Send hot lead alert if score ≥ 80
    4. Add to appropriate retargeting audience
    5. Trigger nurture sequence
    """
    logger = get_run_logger()
    logger.info(f"🎯 Processing assessment completion for {email}")

    # 1. Calculate score
    score = calculate_assessment_score(assessment_data)

    # 2. Update lead in Notion
    status = "hot" if score >= 80 else "warm" if score >= 50 else "cold"
    priority = "high" if score >= 80 else "medium" if score >= 50 else "low"

    update_lead_in_notion(notion_id, {
        "stage": "assessment_complete",
        "score": score,
        "status": status,
        "priority": priority
    })

    # 3. Hot lead alert if score ≥ 80
    if score >= 80:
        send_discord_notification(
            content="🔥 **HOT LEAD ALERT**",
            title=f"{first_name} - Score: {score}/100",
            description="Immediate follow-up recommended within 24 hours",
            color=0xff0000,
            fields=[
                {"name": "Email", "value": email, "inline": True},
                {"name": "Score", "value": str(score), "inline": True},
                {"name": "Priority", "value": "HIGH", "inline": True},
                {"name": "Notion Link", "value": f"[Open Lead](https://notion.so/{notion_id})", "inline": False}
            ]
        )

    # 4. Add to retargeting audience
    add_to_facebook_custom_audience("assessment_completers", [{"email": email}])

    # 5. Trigger next email in nurture sequence
    # (Email 2 will be sent automatically by scheduled nurture flow)

    logger.info(f"✅ Assessment processing complete: {email} (Score: {score})")
    return {"status": "success", "score": score, "priority": priority}

# ============================================================================
# Flow 3: Nurture Sequence Scheduler (Scheduled Daily)
# ============================================================================

@task(retries=5, retry_delay_seconds=5, retry_jitter_factor=0.5)
def fetch_leads_due_for_email(email_stage: int):
    """Fetch leads from Notion who are due for specific email stage."""
    logger = get_run_logger()
    notion = Client(auth=NOTION_API_KEY)

    # Calculate date threshold based on email stage
    days_ago = EMAIL_SEQUENCE[email_stage - 1]["day"]
    threshold_date = (datetime.now() - timedelta(days=days_ago)).date().isoformat()

    # Query Notion for leads at this stage
    results = notion.databases.query(
        database_id=NOTION_LEADS_DB_ID,
        filter={
            "and": [
                {"property": "Email Stage", "number": {"equals": email_stage - 1}},
                {"property": "Created", "date": {"on_or_before": threshold_date}},
                {"property": "Stage", "select": {"does_not_equal": "unsubscribed"}}
            ]
        }
    )

    # Parse results
    leads = []
    for page in results["results"]:
        props = page["properties"]
        leads.append({
            "notion_id": page["id"],
            "email": props.get("Email", {}).get("title", [{}])[0].get("plain_text", ""),
            "first_name": props.get("Name", {}).get("rich_text", [{}])[0].get("plain_text", ""),
            "email_stage": props.get("Email Stage", {}).get("number", 0)
        })

    logger.info(f"📧 Found {len(leads)} leads due for email stage {email_stage}")
    return leads

@flow(name="christmas-nurture-scheduler", log_prints=True)
def nurture_sequence_scheduler():
    """
    Scheduled flow that runs daily to send nurture emails.

    Checks all 7 email stages and sends emails to leads who are due.
    """
    logger = get_run_logger()
    logger.info("🎄 Starting daily nurture sequence check")

    total_sent = 0

    # Check each email stage
    for i, email_config in enumerate(EMAIL_SEQUENCE[1:], start=2):  # Skip stage 1 (immediate)
        leads = fetch_leads_due_for_email(i)

        for lead in leads:
            # Send email
            send_loops_email(
                to_email=lead["email"],
                template_id=email_config["template_id"],
                variables={"first_name": lead["first_name"]}
            )

            # Update email stage
            update_lead_in_notion(lead["notion_id"], {
                "email_stage": i,
                "last_email_sent": datetime.now().isoformat()
            })

            total_sent += 1

    logger.info(f"✅ Nurture sequence complete: {total_sent} emails sent")

    # Send summary to Discord
    if total_sent > 0:
        send_discord_notification(
            content="📧 **Daily Nurture Complete**",
            title=f"Sent {total_sent} emails",
            description="Email nurture sequence executed successfully",
            color=0x0099ff
        )

    return {"status": "success", "emails_sent": total_sent}

# ============================================================================
# Flow 4: Retargeting Sync (Scheduled Daily)
# ============================================================================

@task
def fetch_visitors_by_stage(stage: str, lookback_days: int = 7):
    """Fetch visitors from Notion by stage for retargeting."""
    logger = get_run_logger()
    notion = Client(auth=NOTION_API_KEY)

    cutoff_date = (datetime.now() - timedelta(days=lookback_days)).date().isoformat()

    results = notion.databases.query(
        database_id=NOTION_VISITORS_DB_ID,
        filter={
            "and": [
                {"property": "Stage", "select": {"equals": stage}},
                {"property": "Visit Date", "date": {"on_or_after": cutoff_date}},
                {"property": "Status", "select": {"does_not_equal": "converted"}}
            ]
        }
    )

    visitors = []
    for page in results["results"]:
        props = page["properties"]
        email = props.get("Email", {}).get("email")
        if email:
            visitors.append({"email": email})

    logger.info(f"🎯 Found {len(visitors)} visitors in stage '{stage}'")
    return visitors

@flow(name="christmas-retargeting-sync", log_prints=True)
def retargeting_sync_daily(lookback_days: int = 7):
    """
    4-Audience Retargeting Strategy (Daily Sync)

    Audiences:
    1. Landing Page Bouncers ($1/day)
    2. Assessment Abandoners ($2/day)
    3. Assessment Completers ($3/day)
    4. Sales Page Abandoners ($5/day)

    Expected lift: +50-110% more bookings
    """
    logger = get_run_logger()
    logger.info("🎯 Starting daily retargeting sync")

    audiences = [
        {"stage": "landing_page", "name": "Landing Page Bouncers", "budget": 1.00},
        {"stage": "assessment_started", "name": "Assessment Abandoners", "budget": 2.00},
        {"stage": "assessment_complete", "name": "Assessment Completers", "budget": 3.00},
        {"stage": "sales_page", "name": "Sales Page Abandoners", "budget": 5.00}
    ]

    total_visitors = 0
    results = []

    for config in audiences:
        visitors = fetch_visitors_by_stage(config["stage"], lookback_days)

        if visitors:
            audience_result = add_to_facebook_custom_audience(config["name"], visitors)
            results.append({
                "audience": config["name"],
                "users": len(visitors),
                "budget": config["budget"]
            })
            total_visitors += len(visitors)

    # Send summary to Discord
    fields = [
        {"name": f"{r['audience']}", "value": f"Users: {r['users']} | Budget: ${r['budget']}/day", "inline": False}
        for r in results
    ]

    send_discord_notification(
        content="🎯 **Daily Retargeting Sync Complete**",
        title="4-Audience Strategy",
        description=f"Total visitors: {total_visitors}",
        color=0x0099ff,
        fields=fields
    )

    logger.info(f"✅ Retargeting sync complete: {total_visitors} visitors")
    return {"status": "success", "total_visitors": total_visitors, "audiences": results}

# ============================================================================
# Flow 5: Daily Analytics Report (Scheduled Daily)
# ============================================================================

@task
def gather_daily_metrics():
    """Gather metrics from Notion for daily report."""
    notion = Client(auth=NOTION_API_KEY)

    # Get lead counts
    all_leads = notion.databases.query(database_id=NOTION_LEADS_DB_ID)
    hot_leads = notion.databases.query(
        database_id=NOTION_LEADS_DB_ID,
        filter={"property": "Status", "select": {"equals": "hot"}}
    )

    # Calculate metrics (simplified for example)
    metrics = {
        "total_leads": len(all_leads["results"]),
        "hot_leads": len(hot_leads["results"]),
        "total_spend": 250.00,  # Example: would come from Facebook/Google APIs
        "total_conversions": 12,
        "cost_per_lead": 20.83,
        "ctr": 2.5,
        "optin_rate": 18.5,
        "close_rate": 8.0
    }

    return metrics

@flow(name="christmas-daily-analytics", log_prints=True)
def daily_analytics_report():
    """
    Daily analytics report sent to Discord.

    Consolidates metrics from all channels.
    """
    logger = get_run_logger()
    logger.info("📊 Generating daily analytics report")

    metrics = gather_daily_metrics()

    # Send to Discord
    send_discord_notification(
        content="📊 **Daily Marketing Report**",
        title=f"Performance - {datetime.now().strftime('%Y-%m-%d')}",
        description="Consolidated metrics from all marketing channels",
        color=0x0099ff,
        fields=[
            {"name": "💰 Total Ad Spend", "value": f"${metrics['total_spend']:.2f}", "inline": True},
            {"name": "👥 Total Leads", "value": str(metrics['total_leads']), "inline": True},
            {"name": "🔥 Hot Leads", "value": str(metrics['hot_leads']), "inline": True},
            {"name": "📊 Cost Per Lead", "value": f"${metrics['cost_per_lead']:.2f}", "inline": True},
            {"name": "🎯 CTR", "value": f"{metrics['ctr']:.2f}%", "inline": True},
            {"name": "📥 Opt-in Rate", "value": f"{metrics['optin_rate']:.1f}%", "inline": True}
        ]
    )

    logger.info("✅ Daily analytics report sent")
    return {"status": "success", "metrics": metrics}

# ============================================================================
# Deployment Configuration
# ============================================================================

if __name__ == "__main__":
    """
    Deploy all flows with appropriate triggers and schedules.
    """
    print("🎄 Deploying Christmas Campaign Flows...")

    # Flow 1: Lead Opt-In (Event-Driven)
    handle_lead_optin.serve(
        name="christmas-lead-optin",
        triggers=[
            DeploymentEventTrigger(
                match={"prefect.resource.id": "lead.*"},
                expect=["lead.opted_in"],
                parameters={
                    "email": "{{ event.payload.email }}",
                    "first_name": "{{ event.payload.first_name }}",
                    "phone": "{{ event.payload.phone }}",
                    "visitor_id": "{{ event.payload.visitor_id }}",
                    "segment": "{{ event.payload.segment }}"
                }
            )
        ]
    )

    # Flow 2: Assessment Completion (Event-Driven)
    handle_assessment_completion.serve(
        name="christmas-assessment",
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

    # Flow 3: Nurture Sequence (Scheduled Daily at 9 AM)
    nurture_sequence_scheduler.serve(
        name="christmas-nurture",
        cron="0 9 * * *"
    )

    # Flow 4: Retargeting Sync (Scheduled Daily at 10 AM)
    retargeting_sync_daily.serve(
        name="christmas-retargeting",
        cron="0 10 * * *"
    )

    # Flow 5: Daily Analytics (Scheduled Daily at 5 PM)
    daily_analytics_report.serve(
        name="christmas-analytics",
        cron="0 17 * * *"
    )

    print("✅ All flows deployed successfully!")
    print("📊 Monitor at: http://localhost:4200")
