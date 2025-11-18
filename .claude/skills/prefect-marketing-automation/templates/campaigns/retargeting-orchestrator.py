"""
Retargeting Orchestrator - 4-Audience Recovery System

Implements the 4-audience retargeting strategy with daily budget allocation:
- Audience #1: Landing Page Bouncers ($1/day) - 5-10% recovery
- Audience #2: Assessment Abandoners ($2/day) - 10-15% recovery
- Audience #3: Assessment Completers/Non-Bookers ($3/day) ⭐ - 15-25% recovery
- Audience #4: Sales Page Abandoners ($5/day) ⭐⭐ - 30-50% recovery

Total daily budget: $11/day ($330/month)
Expected lift: +50-110% more bookings

Integrations:
- Facebook Ads API for audience creation and management
- Notion for visitor tracking and segmentation
- Discord for performance monitoring

Usage:
    python retargeting-orchestrator.py
    # Or deploy: prefect deploy -n retargeting-daily
"""

from datetime import datetime, timedelta
from prefect import flow, task
import httpx
import os
from typing import List, Dict, Optional
import hashlib

# Configuration
FB_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN")
FB_AD_ACCOUNT_ID = os.getenv("FACEBOOK_AD_ACCOUNT_ID")
FB_PIXEL_ID = os.getenv("FACEBOOK_PIXEL_ID")
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")


@task(retries=3, retry_delay_seconds=60)
def fetch_visitors_by_stage(stage: str, lookback_days: int = 7):
    """
    Fetch visitors who abandoned at specific funnel stage.

    Args:
        stage: Funnel stage (landing_page, assessment_started,
               assessment_complete, sales_page)
        lookback_days: How many days back to look for visitors

    Returns:
        List of visitor records with hashed identifiers
    """
    from notion_client import Client

    notion = Client(auth=NOTION_API_KEY)

    # Query Notion database for visitors at this stage
    cutoff_date = (datetime.now() - timedelta(days=lookback_days)).isoformat()

    results = notion.databases.query(
        database_id=os.getenv("NOTION_VISITORS_DB_ID"),
        filter={
            "and": [
                {
                    "property": "Stage",
                    "select": {"equals": stage}
                },
                {
                    "property": "Visit Date",
                    "date": {"on_or_after": cutoff_date}
                },
                {
                    "property": "Status",
                    "select": {"equals": "abandoned"}
                }
            ]
        }
    )

    visitors = []
    for page in results["results"]:
        props = page["properties"]

        visitors.append({
            "notion_id": page["id"],
            "visitor_id": props.get("Visitor ID", {}).get("rich_text", [{}])[0].get("plain_text", ""),
            "email": props.get("Email", {}).get("email", ""),
            "phone": props.get("Phone", {}).get("phone_number", ""),
            "visit_date": props.get("Visit Date", {}).get("date", {}).get("start", ""),
            "source": props.get("Source", {}).get("select", {}).get("name", "")
        })

    print(f"📊 Found {len(visitors)} visitors at stage '{stage}'")
    return visitors


@task
def hash_user_data(email: str = None, phone: str = None):
    """
    Hash user identifiers for Facebook Custom Audience upload.

    Facebook requires SHA-256 hashed emails and phones for privacy.

    Args:
        email: Email address (will be lowercased and hashed)
        phone: Phone number (will be normalized and hashed)

    Returns:
        dict with hashed identifiers
    """
    hashed = {}

    if email:
        # Lowercase and trim, then hash
        normalized_email = email.strip().lower()
        hashed["email"] = hashlib.sha256(normalized_email.encode()).hexdigest()

    if phone:
        # Remove non-numeric characters, then hash
        normalized_phone = ''.join(filter(str.isdigit, phone))
        hashed["phone"] = hashlib.sha256(normalized_phone.encode()).hexdigest()

    return hashed


@task(retries=3, retry_delay_seconds=120)
def create_or_update_custom_audience(
    stage: str,
    audience_name: str,
    visitor_data: List[Dict],
    budget: float
):
    """
    Create or update Facebook Custom Audience with visitor data.

    Args:
        stage: Funnel stage (for identification)
        audience_name: Display name for audience
        visitor_data: List of visitor records to add
        budget: Recommended daily budget

    Returns:
        Audience ID and stats
    """
    if not FB_ACCESS_TOKEN or not FB_AD_ACCOUNT_ID:
        print("⚠️ Facebook credentials not configured")
        return None

    # Check if audience already exists
    existing_audiences = httpx.get(
        f"https://graph.facebook.com/v18.0/act_{FB_AD_ACCOUNT_ID}/customaudiences",
        headers={"Authorization": f"Bearer {FB_ACCESS_TOKEN}"},
        params={"fields": "id,name", "limit": 500},
        timeout=30
    )
    existing_audiences.raise_for_status()

    audience_id = None
    for audience in existing_audiences.json().get("data", []):
        if stage in audience["name"]:
            audience_id = audience["id"]
            print(f"✅ Found existing audience: {audience['name']} (ID: {audience_id})")
            break

    # Create new audience if doesn't exist
    if not audience_id:
        create_response = httpx.post(
            f"https://graph.facebook.com/v18.0/act_{FB_AD_ACCOUNT_ID}/customaudiences",
            headers={"Authorization": f"Bearer {FB_ACCESS_TOKEN}"},
            json={
                "name": f"{audience_name} - {datetime.now().strftime('%Y-%m')}",
                "description": f"Retargeting audience for {stage} abandoners",
                "subtype": "CUSTOM",
                "customer_file_source": "USER_PROVIDED_ONLY"
            },
            timeout=30
        )
        create_response.raise_for_status()
        audience_id = create_response.json()["id"]
        print(f"✅ Created new audience: {audience_name} (ID: {audience_id})")

    # Prepare user data with hashing
    users_payload = []
    for visitor in visitor_data[:10000]:  # Facebook limit: 10k users per request
        hashed = hash_user_data(
            email=visitor.get("email"),
            phone=visitor.get("phone")
        )
        if hashed:
            users_payload.append(hashed)

    # Upload users to audience
    if users_payload:
        upload_response = httpx.post(
            f"https://graph.facebook.com/v18.0/{audience_id}/users",
            headers={"Authorization": f"Bearer {FB_ACCESS_TOKEN}"},
            json={
                "payload": {
                    "schema": ["EMAIL_SHA256", "PHONE_SHA256"],
                    "data": [[u.get("email", ""), u.get("phone", "")] for u in users_payload]
                }
            },
            timeout=60
        )
        upload_response.raise_for_status()

        print(f"✅ Uploaded {len(users_payload)} users to audience {audience_id}")
    else:
        print("⚠️ No user data to upload (missing emails/phones)")

    return {
        "audience_id": audience_id,
        "stage": stage,
        "audience_name": audience_name,
        "users_count": len(users_payload),
        "recommended_budget": budget,
        "created_at": datetime.now().isoformat()
    }


@task
def send_performance_report(audiences: List[Dict], total_visitors: int):
    """
    Send daily performance report to Discord.

    Args:
        audiences: List of audience stats
        total_visitors: Total visitors processed
    """
    if not DISCORD_WEBHOOK_URL:
        return

    total_budget = sum(a["recommended_budget"] for a in audiences)

    fields = []
    for audience in audiences:
        fields.append({
            "name": f"{audience['audience_name']}",
            "value": f"Users: {audience['users_count']} | Budget: ${audience['recommended_budget']}/day",
            "inline": False
        })

    payload = {
        "content": "📊 **Daily Retargeting Report**",
        "embeds": [{
            "title": "4-Audience Retargeting Status",
            "description": f"Total visitors processed: {total_visitors}\nTotal daily budget: ${total_budget}",
            "color": 0x0099ff,
            "fields": fields,
            "footer": {
                "text": f"Expected lift: +50-110% more bookings | {datetime.now().strftime('%Y-%m-%d')}"
            },
            "timestamp": datetime.now().isoformat()
        }]
    }

    httpx.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)


@flow(name="retargeting-orchestrator-daily", log_prints=True)
def daily_retargeting_sync(lookback_days: int = 7):
    """
    Daily orchestration of 4-audience retargeting strategy.

    Runs daily to:
    1. Fetch visitors who abandoned at each stage
    2. Create/update Facebook Custom Audiences
    3. Send performance report to Discord

    Args:
        lookback_days: How many days back to include visitors

    Returns:
        dict: Summary of audiences created and performance

    Example:
        # Deploy to run daily at 9 AM:
        daily_retargeting_sync.serve(
            name="retargeting-daily",
            cron="0 9 * * *"
        )
    """

    print(f"🚀 Starting daily retargeting sync")
    print(f"   Lookback period: {lookback_days} days")

    # Define 4 audiences
    audience_configs = [
        {
            "stage": "landing_page",
            "name": "Landing Page Bouncers",
            "budget": 1.00,
            "description": "Visited landing page but didn't opt in",
            "recovery_rate": "5-10%"
        },
        {
            "stage": "assessment_started",
            "name": "Assessment Abandoners",
            "budget": 2.00,
            "description": "Started assessment but didn't complete",
            "recovery_rate": "10-15%"
        },
        {
            "stage": "assessment_complete",
            "name": "Assessment Completers (Non-Bookers)",
            "budget": 3.00,
            "description": "Completed assessment but didn't book sales call",
            "recovery_rate": "15-25%",
            "priority": "high"
        },
        {
            "stage": "sales_page",
            "name": "Sales Page Abandoners",
            "budget": 5.00,
            "description": "Visited sales page but didn't book",
            "recovery_rate": "30-50%",
            "priority": "critical"
        }
    ]

    audiences_created = []
    total_visitors = 0

    for config in audience_configs:
        print(f"\n{'='*60}")
        print(f"📊 Processing: {config['name']}")
        print(f"   Stage: {config['stage']}")
        print(f"   Budget: ${config['budget']}/day")
        print(f"   Expected Recovery: {config['recovery_rate']}")

        # Fetch visitors at this stage
        visitors = fetch_visitors_by_stage(
            stage=config["stage"],
            lookback_days=lookback_days
        )

        if not visitors:
            print(f"   ⚠️ No visitors found at this stage")
            continue

        total_visitors += len(visitors)

        # Create or update audience
        audience_result = create_or_update_custom_audience(
            stage=config["stage"],
            audience_name=config["name"],
            visitor_data=visitors,
            budget=config["budget"]
        )

        if audience_result:
            audiences_created.append(audience_result)
            print(f"   ✅ Audience synced: {audience_result['users_count']} users")

    # Send performance report
    print(f"\n{'='*60}")
    print(f"📧 Sending performance report to Discord")
    send_performance_report(
        audiences=audiences_created,
        total_visitors=total_visitors
    )

    # Summary
    total_budget = sum(a["recommended_budget"] for a in audiences_created)

    print(f"\n{'='*60}")
    print(f"📊 DAILY RETARGETING SUMMARY")
    print(f"   Audiences Created: {len(audiences_created)}")
    print(f"   Total Visitors Processed: {total_visitors}")
    print(f"   Total Daily Budget: ${total_budget}")
    print(f"   Expected Monthly Cost: ${total_budget * 30}")
    print(f"   Expected Lift: +50-110% more bookings")
    print(f"{'='*60}\n")

    return {
        "audiences_created": len(audiences_created),
        "total_visitors": total_visitors,
        "total_budget": total_budget,
        "audience_details": audiences_created,
        "synced_at": datetime.now().isoformat()
    }


@flow(name="retargeting-ad-creator", log_prints=True)
def create_retargeting_ads(
    audience_id: str,
    stage: str,
    ad_creative: Dict,
    budget: float
):
    """
    Create retargeting ad campaigns for specific audience.

    Note: This is a simplified example. Production would need full ad creation
    with multiple ad sets, A/B testing, and performance monitoring.

    Args:
        audience_id: Facebook Custom Audience ID
        stage: Funnel stage (for ad messaging)
        ad_creative: Ad creative data (image, headline, copy)
        budget: Daily budget for this audience

    Returns:
        Campaign ID and status
    """
    if not FB_ACCESS_TOKEN or not FB_AD_ACCOUNT_ID:
        print("⚠️ Facebook credentials not configured")
        return None

    # Stage-specific ad messaging
    ad_messages = {
        "landing_page": {
            "headline": "Still thinking about it?",
            "copy": "Take our free 8-System Assessment and discover what's holding your business back this Christmas season."
        },
        "assessment_started": {
            "headline": "Complete your assessment",
            "copy": "You're almost done! Finish your 8-System Assessment to see your personalized business scorecard."
        },
        "assessment_complete": {
            "headline": "Ready to fix those broken systems?",
            "copy": "You scored {score}/100. Book a diagnostic call to create your 45-90 day action plan."
        },
        "sales_page": {
            "headline": "Last chance for Christmas capacity boost",
            "copy": "Book your $2,997 diagnostic before December 20th. 100% money-back guarantee."
        }
    }

    message = ad_messages.get(stage, ad_messages["landing_page"])

    print(f"📢 Creating retargeting ad for {stage}")
    print(f"   Audience ID: {audience_id}")
    print(f"   Budget: ${budget}/day")
    print(f"   Headline: {message['headline']}")

    # In production, you would:
    # 1. Create campaign
    # 2. Create ad set with audience targeting
    # 3. Create ad with creative
    # 4. Set budget and schedule

    # This is a placeholder for the full implementation
    print(f"   ✅ Ad campaign created (production implementation needed)")

    return {
        "audience_id": audience_id,
        "stage": stage,
        "budget": budget,
        "ad_message": message,
        "created_at": datetime.now().isoformat()
    }


# Deployment configuration
if __name__ == "__main__":
    # Deployment 1: Daily retargeting sync (9 AM daily)
    daily_retargeting_sync.serve(
        name="retargeting-daily-sync-v1",
        cron="0 9 * * *",  # Daily at 9 AM
        parameters={"lookback_days": 7},
        description="Daily sync of 4-audience retargeting strategy - $11/day total budget"
    )

    # Manual trigger for testing:
    # daily_retargeting_sync(lookback_days=7)
