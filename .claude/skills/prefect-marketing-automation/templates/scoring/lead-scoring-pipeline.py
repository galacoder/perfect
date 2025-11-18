"""
Lead Scoring Pipeline - Activity-Based Scoring & Routing

Calculates lead scores based on:
- Email engagement (opens, clicks)
- Website activity (page views, time on site)
- Assessment completion and results
- Sales page visits
- Form submissions
- Response time to communications

Scoring Logic:
- Score 0-100 (higher = hotter lead)
- Hot leads (≥80): Immediate sales follow-up
- Warm leads (50-79): Standard nurture sequence
- Cold leads (<50): Educational content only

Routes leads to appropriate workflows based on score.

Integrations:
- Loops.so for email engagement tracking
- Notion for lead database and score updates
- Discord for hot lead notifications

Usage:
    python lead-scoring-pipeline.py
    # Or deploy: prefect deploy -n lead-scoring-hourly
"""

from datetime import datetime, timedelta
from prefect import flow, task
import httpx
import os
from typing import Dict, List, Optional

# Configuration
LOOPS_API_KEY = os.getenv("LOOPS_API_KEY")
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")


@task(retries=3, retry_delay_seconds=60)
def fetch_lead_activity(notion_id: str, lookback_hours: int = 24):
    """
    Fetch recent lead activity from Notion and external sources.

    Args:
        notion_id: Notion page ID for lead
        lookback_hours: How many hours back to check for activity

    Returns:
        dict: Activity summary with engagement metrics
    """
    from notion_client import Client

    notion = Client(auth=NOTION_API_KEY)

    # Get lead record
    lead = notion.pages.retrieve(page_id=notion_id)
    props = lead["properties"]

    email = props.get("Email", {}).get("title", [{}])[0].get("plain_text", "")

    # Fetch email engagement from Loops.so
    email_activity = fetch_loops_engagement(email, lookback_hours)

    # Fetch website activity from Notion tracking
    website_activity = fetch_website_activity(notion_id, lookback_hours)

    return {
        "notion_id": notion_id,
        "email": email,
        "email_activity": email_activity,
        "website_activity": website_activity,
        "current_score": props.get("Score", {}).get("number", 0),
        "current_status": props.get("Status", {}).get("select", {}).get("name", "new")
    }


@task(retries=2, retry_delay_seconds=30)
def fetch_loops_engagement(email: str, lookback_hours: int):
    """
    Fetch email engagement metrics from Loops.so.

    Args:
        email: Lead email address
        lookback_hours: Time window for engagement

    Returns:
        dict: Email engagement metrics (opens, clicks, responses)
    """
    if not LOOPS_API_KEY:
        return {"opens": 0, "clicks": 0, "responses": 0}

    # Note: Loops.so API doesn't have a direct engagement endpoint
    # In production, you'd use webhooks to track this in Notion
    # This is a placeholder showing the data structure

    cutoff_time = datetime.now() - timedelta(hours=lookback_hours)

    # Placeholder: fetch from your tracking system
    return {
        "opens": 0,  # Email opens in lookback period
        "clicks": 0,  # Link clicks in lookback period
        "responses": 0,  # Direct email responses
        "last_open": None,
        "last_click": None
    }


@task
def fetch_website_activity(notion_id: str, lookback_hours: int):
    """
    Fetch website activity from Notion visitor tracking.

    Args:
        notion_id: Notion page ID for lead
        lookback_hours: Time window for activity

    Returns:
        dict: Website activity metrics
    """
    from notion_client import Client

    notion = Client(auth=NOTION_API_KEY)

    cutoff_time = datetime.now() - timedelta(hours=lookback_hours)

    # Query visitor database for this lead's activity
    results = notion.databases.query(
        database_id=os.getenv("NOTION_VISITORS_DB_ID"),
        filter={
            "and": [
                {
                    "property": "Lead ID",
                    "rich_text": {"equals": notion_id}
                },
                {
                    "property": "Visit Date",
                    "date": {"on_or_after": cutoff_time.isoformat()}
                }
            ]
        }
    )

    page_views = len(results["results"])
    pages_visited = set()
    time_on_site = 0

    for page in results["results"]:
        props = page["properties"]
        page_url = props.get("Page URL", {}).get("url", "")
        duration = props.get("Duration", {}).get("number", 0)

        pages_visited.add(page_url)
        time_on_site += duration

    return {
        "page_views": page_views,
        "unique_pages": len(pages_visited),
        "time_on_site": time_on_site,
        "visited_sales_page": any("diagnostic" in url or "booking" in url for url in pages_visited)
    }


@task
def calculate_lead_score(activity_data: Dict):
    """
    Calculate lead score based on activity metrics.

    Scoring rubric:
    - Email opens: +5 per open (max 20)
    - Email clicks: +10 per click (max 30)
    - Email responses: +15 per response (max 30)
    - Page views: +3 per view (max 15)
    - Time on site: +1 per minute (max 10)
    - Sales page visit: +20
    - Assessment completion: +30 (from assessment data)

    Args:
        activity_data: Activity metrics from fetch_lead_activity

    Returns:
        dict: New score and score change
    """
    email = activity_data["email_activity"]
    website = activity_data["website_activity"]
    current_score = activity_data["current_score"]

    # Calculate points from different activities
    points = 0

    # Email engagement
    points += min(email["opens"] * 5, 20)
    points += min(email["clicks"] * 10, 30)
    points += min(email["responses"] * 15, 30)

    # Website activity
    points += min(website["page_views"] * 3, 15)
    points += min(website["time_on_site"] // 60, 10)  # Minutes on site

    # High-value actions
    if website["visited_sales_page"]:
        points += 20

    # Calculate new score (weighted average with previous score)
    # 70% previous score + 30% new activity
    new_score = int((current_score * 0.7) + (points * 0.3))
    new_score = min(max(new_score, 0), 100)  # Clamp 0-100

    score_change = new_score - current_score

    # Determine status
    if new_score >= 80:
        status = "hot"
        priority = "high"
    elif new_score >= 50:
        status = "warm"
        priority = "medium"
    else:
        status = "cold"
        priority = "low"

    return {
        "new_score": new_score,
        "previous_score": current_score,
        "score_change": score_change,
        "status": status,
        "priority": priority,
        "points_breakdown": {
            "email_opens": min(email["opens"] * 5, 20),
            "email_clicks": min(email["clicks"] * 10, 30),
            "email_responses": min(email["responses"] * 15, 30),
            "page_views": min(website["page_views"] * 3, 15),
            "time_on_site": min(website["time_on_site"] // 60, 10),
            "sales_page_visit": 20 if website["visited_sales_page"] else 0
        }
    }


@task(retries=2, retry_delay_seconds=30)
def update_lead_score(notion_id: str, score_data: Dict):
    """
    Update lead score and status in Notion.

    Args:
        notion_id: Notion page ID for lead
        score_data: Score calculation results

    Returns:
        bool: Update success status
    """
    from notion_client import Client

    notion = Client(auth=NOTION_API_KEY)

    notion.pages.update(
        page_id=notion_id,
        properties={
            "Score": {"number": score_data["new_score"]},
            "Status": {"select": {"name": score_data["status"]}},
            "Priority": {"select": {"name": score_data["priority"]}},
            "Last Scored": {"date": {"start": datetime.now().isoformat()}}
        }
    )

    return True


@task
def route_lead_by_score(notion_id: str, email: str, first_name: str, score_data: Dict):
    """
    Route lead to appropriate workflow based on score.

    Routes:
    - Hot leads (≥80): Trigger immediate sales follow-up
    - Warm leads (50-79): Continue nurture sequence
    - Cold leads (<50): Send educational content

    Args:
        notion_id: Notion page ID for lead
        email: Lead email address
        first_name: Lead first name
        score_data: Score calculation results
    """
    from prefect.events import emit_event

    status = score_data["status"]
    score = score_data["new_score"]

    print(f"📊 Routing lead: {first_name} ({email})")
    print(f"   Score: {score}/100 ({status.upper()})")

    if status == "hot":
        # Trigger immediate sales follow-up
        print(f"   🔥 HOT LEAD - Triggering sales team alert")

        emit_event(
            event="lead.became_hot",
            resource={
                "prefect.resource.id": f"lead.{notion_id}",
                "prefect.resource.name": email
            },
            payload={
                "notion_id": notion_id,
                "email": email,
                "first_name": first_name,
                "score": score,
                "status": status
            }
        )

        # Send Discord notification
        if DISCORD_WEBHOOK_URL:
            httpx.post(
                DISCORD_WEBHOOK_URL,
                json={
                    "content": f"🔥 **HOT LEAD ALERT** - {first_name} scored {score}/100",
                    "embeds": [{
                        "title": f"{first_name} - {email}",
                        "description": "Immediate follow-up recommended",
                        "color": 0xff0000,
                        "fields": [
                            {"name": "Score", "value": f"{score}/100", "inline": True},
                            {"name": "Status", "value": status.upper(), "inline": True}
                        ]
                    }]
                },
                timeout=10
            )

    elif status == "warm":
        print(f"   📧 WARM LEAD - Continue nurture sequence")
        # Warm leads continue standard nurture (no action needed)

    else:  # cold
        print(f"   ❄️ COLD LEAD - Educational content only")

        emit_event(
            event="lead.became_cold",
            resource={
                "prefect.resource.id": f"lead.{notion_id}",
                "prefect.resource.name": email
            },
            payload={
                "notion_id": notion_id,
                "email": email,
                "first_name": first_name,
                "score": score
            }
        )


@flow(name="score-single-lead", log_prints=True)
def score_single_lead(notion_id: str, email: str, first_name: str):
    """
    Score a single lead based on recent activity.

    Args:
        notion_id: Notion page ID for lead
        email: Lead email address
        first_name: Lead first name

    Returns:
        dict: Scoring results and routing decision
    """
    print(f"🔢 Scoring lead: {first_name} ({email})")

    # Step 1: Fetch activity
    activity_data = fetch_lead_activity(notion_id, lookback_hours=24)

    # Step 2: Calculate score
    score_data = calculate_lead_score(activity_data)

    print(f"   Score: {score_data['previous_score']} → {score_data['new_score']} ({score_data['score_change']:+d})")
    print(f"   Status: {score_data['status'].upper()}")

    # Step 3: Update Notion
    update_lead_score(notion_id, score_data)

    # Step 4: Route by score
    route_lead_by_score(notion_id, email, first_name, score_data)

    return {
        "notion_id": notion_id,
        "email": email,
        "score": score_data["new_score"],
        "status": score_data["status"],
        "score_change": score_data["score_change"]
    }


@flow(name="score-all-leads-batch", log_prints=True)
def score_all_leads_batch():
    """
    Batch scoring of all active leads.

    Runs hourly to update scores for all leads in the system.

    Returns:
        dict: Batch scoring summary
    """
    from notion_client import Client

    print(f"🚀 Starting batch lead scoring")

    notion = Client(auth=NOTION_API_KEY)

    # Fetch all active leads
    results = notion.databases.query(
        database_id=os.getenv("NOTION_LEADS_DB_ID"),
        filter={
            "property": "Status",
            "select": {
                "does_not_equal": "converted"
            }
        }
    )

    leads = []
    for page in results["results"]:
        props = page["properties"]

        leads.append({
            "notion_id": page["id"],
            "email": props.get("Email", {}).get("title", [{}])[0].get("plain_text", ""),
            "first_name": props.get("Name", {}).get("rich_text", [{}])[0].get("plain_text", "Unknown")
        })

    print(f"📊 Found {len(leads)} active leads to score")

    # Score each lead
    results = []
    hot_leads = 0
    warm_leads = 0
    cold_leads = 0

    for lead in leads:
        try:
            result = score_single_lead(
                notion_id=lead["notion_id"],
                email=lead["email"],
                first_name=lead["first_name"]
            )
            results.append(result)

            if result["status"] == "hot":
                hot_leads += 1
            elif result["status"] == "warm":
                warm_leads += 1
            else:
                cold_leads += 1

        except Exception as e:
            print(f"   ❌ Error scoring {lead['email']}: {e}")

    # Summary
    print(f"\n{'='*60}")
    print(f"📊 BATCH SCORING SUMMARY")
    print(f"   Total Leads Scored: {len(results)}")
    print(f"   🔥 Hot Leads (≥80): {hot_leads}")
    print(f"   📧 Warm Leads (50-79): {warm_leads}")
    print(f"   ❄️ Cold Leads (<50): {cold_leads}")
    print(f"{'='*60}\n")

    return {
        "total_scored": len(results),
        "hot_leads": hot_leads,
        "warm_leads": warm_leads,
        "cold_leads": cold_leads,
        "scored_at": datetime.now().isoformat()
    }


# Deployment configuration
if __name__ == "__main__":
    # Deployment 1: Batch scoring (hourly)
    score_all_leads_batch.serve(
        name="lead-scoring-hourly-v1",
        cron="0 * * * *",  # Every hour
        description="Hourly batch scoring of all active leads"
    )

    # Deployment 2: Single lead scoring (webhook triggered)
    score_single_lead.serve(
        name="score-single-lead-v1",
        description="Score individual lead on activity webhook"
    )

    # Manual trigger for testing:
    # score_all_leads_batch()
