#!/usr/bin/env python3
"""
Multi-Channel Coordinated Launch Blast
=====================================

Production-ready example demonstrating:
- Coordinated multi-platform publishing (Twitter, LinkedIn, Facebook)
- Email blast to segmented list
- Discord launch notifications
- Analytics tracking
- Scheduled execution for maximum reach

Use Case:
---------
Product launch, webinar announcement, limited-time offer, or event promotion
across all marketing channels simultaneously for maximum impact.

Prerequisites:
--------------
1. Environment variables:
   - LOOPS_API_KEY
   - NOTION_API_KEY
   - DISCORD_WEBHOOK_URL
   - TWITTER_API_KEY, TWITTER_API_SECRET
   - TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET
   - LINKEDIN_ACCESS_TOKEN
   - FB_PAGE_ACCESS_TOKEN, FB_PAGE_ID

2. Notion databases:
   - Leads database with Email, Segment, Status fields
   - Content Calendar database

3. Social media accounts:
   - Twitter Business account
   - LinkedIn Company page
   - Facebook Business page

4. Loops.so template:
   - launch-blast (configured for your offer)

Usage:
------
1. Create content in Notion Content Calendar with:
   - Title: "Black Friday 50% Off - Launch"
   - Content: Post text (Twitter: 280 chars, LinkedIn/FB: longer)
   - Image URL: Featured image
   - Link URL: Landing page
   - Scheduled Date: Launch date
   - Scheduled Time: Launch time (e.g., "09:00")

2. Deploy flow:
   python multi-channel-blast.py

3. Manual trigger (for immediate launch):
   from prefect.events import emit_event
   emit_event(
       event="launch.trigger",
       resource={"prefect.resource.id": "launch.black-friday"},
       payload={
           "campaign_name": "Black Friday 50% Off",
           "offer_description": "50% off all services",
           "landing_url": "https://yourdomain.com/black-friday",
           "expiry_date": "2025-11-30",
           "segment_filter": "all"  # or specific segment
       }
   )

4. Or schedule via cron (daily check for scheduled launches):
   Deployment runs daily at 9 AM, checks Notion for scheduled content

Author: Marketing Automation Team
Date: 2025-01-10
Version: 1.0.0
"""

import os
import httpx
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from prefect import flow, task, get_run_logger
from prefect.deployments import DeploymentEventTrigger
from notion_client import Client
from requests_oauthlib import OAuth1Session

# ============================================================================
# Configuration
# ============================================================================

# API Keys
LOOPS_API_KEY = os.getenv("LOOPS_API_KEY")
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# Twitter OAuth 1.0a
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")

# LinkedIn OAuth 2.0
LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
LINKEDIN_ORG_ID = os.getenv("LINKEDIN_ORG_ID")

# Facebook Graph API
FB_PAGE_ACCESS_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN")
FB_PAGE_ID = os.getenv("FB_PAGE_ID")

# Notion Database IDs
NOTION_LEADS_DB_ID = os.getenv("NOTION_LEADS_DB_ID")
NOTION_CONTENT_DB_ID = os.getenv("NOTION_CONTENT_DB_ID")

# ============================================================================
# Social Media Publishing Tasks
# ============================================================================

@task(retries=3, retry_delay_seconds=60, retry_jitter_factor=0.5)
def publish_to_twitter(content: str, image_url: Optional[str] = None, link_url: Optional[str] = None):
    """
    Publish post to Twitter using API v2.

    Twitter character limit: 280 characters
    """
    logger = get_run_logger()

    # Initialize OAuth session
    twitter = OAuth1Session(
        TWITTER_API_KEY,
        client_secret=TWITTER_API_SECRET,
        resource_owner_key=TWITTER_ACCESS_TOKEN,
        resource_owner_secret=TWITTER_ACCESS_SECRET
    )

    # Prepare tweet text
    tweet_text = content
    if link_url and len(tweet_text) + len(link_url) + 1 <= 280:
        tweet_text += f"\n{link_url}"

    # Upload media if provided
    media_ids = []
    if image_url:
        # Download image
        img_response = httpx.get(image_url, timeout=30)
        img_response.raise_for_status()

        # Upload to Twitter
        media_response = twitter.post(
            "https://upload.twitter.com/1.1/media/upload.json",
            files={"media": img_response.content}
        )
        media_ids.append(media_response.json()["media_id_string"])

    # Create tweet
    payload = {"text": tweet_text}
    if media_ids:
        payload["media"] = {"media_ids": media_ids}

    response = twitter.post("https://api.twitter.com/2/tweets", json=payload)
    response.raise_for_status()

    tweet_data = response.json()
    tweet_id = tweet_data["data"]["id"]
    tweet_url = f"https://twitter.com/user/status/{tweet_id}"

    logger.info(f"✅ Published to Twitter: {tweet_url}")
    return {"platform": "twitter", "post_id": tweet_id, "post_url": tweet_url}

@task(retries=3, retry_delay_seconds=60, retry_jitter_factor=0.5)
def publish_to_linkedin(content: str, image_url: Optional[str] = None, link_url: Optional[str] = None):
    """
    Publish post to LinkedIn Company Page.

    LinkedIn character limit: 3000 characters
    """
    logger = get_run_logger()

    # Prepare post content
    post_text = content
    if link_url:
        post_text += f"\n\n{link_url}"

    # Upload media if provided
    media_urn = None
    if image_url:
        # Download image
        img_response = httpx.get(image_url, timeout=30)
        img_response.raise_for_status()

        # Register upload
        register_response = httpx.post(
            "https://api.linkedin.com/v2/assets?action=registerUpload",
            headers={
                "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
                "Content-Type": "application/json"
            },
            json={
                "registerUploadRequest": {
                    "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                    "owner": f"urn:li:organization:{LINKEDIN_ORG_ID}",
                    "serviceRelationships": [{
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent"
                    }]
                }
            },
            timeout=30
        )
        register_data = register_response.json()
        upload_url = register_data["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
        asset_urn = register_data["value"]["asset"]

        # Upload image
        httpx.put(
            upload_url,
            headers={"Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}"},
            content=img_response.content,
            timeout=60
        )

        media_urn = asset_urn

    # Create post
    post_payload = {
        "author": f"urn:li:organization:{LINKEDIN_ORG_ID}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": post_text},
                "shareMediaCategory": "IMAGE" if media_urn else "NONE"
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
    }

    if media_urn:
        post_payload["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [{
            "status": "READY",
            "media": media_urn
        }]

    response = httpx.post(
        "https://api.linkedin.com/v2/ugcPosts",
        headers={
            "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        },
        json=post_payload,
        timeout=30
    )

    response.raise_for_status()
    post_id = response.headers.get("X-RestLi-Id")
    post_url = f"https://www.linkedin.com/feed/update/{post_id}"

    logger.info(f"✅ Published to LinkedIn: {post_url}")
    return {"platform": "linkedin", "post_id": post_id, "post_url": post_url}

@task(retries=3, retry_delay_seconds=60, retry_jitter_factor=0.5)
def publish_to_facebook(content: str, image_url: Optional[str] = None, link_url: Optional[str] = None):
    """
    Publish post to Facebook Business Page.

    Facebook character limit: 63,206 characters (practically unlimited)
    """
    logger = get_run_logger()

    # Prepare post
    post_payload = {
        "message": content,
        "access_token": FB_PAGE_ACCESS_TOKEN
    }

    if link_url:
        post_payload["link"] = link_url

    # If image provided, use photo post endpoint
    if image_url:
        # Download image
        img_response = httpx.get(image_url, timeout=30)
        img_response.raise_for_status()

        # Upload photo
        response = httpx.post(
            f"https://graph.facebook.com/v18.0/{FB_PAGE_ID}/photos",
            data={
                "message": content,
                "url": image_url,
                "access_token": FB_PAGE_ACCESS_TOKEN
            },
            timeout=30
        )
    else:
        # Regular post
        response = httpx.post(
            f"https://graph.facebook.com/v18.0/{FB_PAGE_ID}/feed",
            data=post_payload,
            timeout=30
        )

    response.raise_for_status()
    post_data = response.json()
    post_id = post_data["id"]
    post_url = f"https://www.facebook.com/{post_id}"

    logger.info(f"✅ Published to Facebook: {post_url}")
    return {"platform": "facebook", "post_id": post_id, "post_url": post_url}

# ============================================================================
# Email Blast Tasks
# ============================================================================

@task(retries=5, retry_delay_seconds=5, retry_jitter_factor=0.5)
def fetch_leads_for_blast(segment_filter: str = "all"):
    """
    Fetch leads from Notion for email blast.

    Args:
        segment_filter: "all" or specific segment (e.g., "beauty-salon")
    """
    logger = get_run_logger()
    notion = Client(auth=NOTION_API_KEY)

    # Build filter
    query_filter = {
        "and": [
            {"property": "Stage", "select": {"does_not_equal": "unsubscribed"}},
            {"property": "Status", "select": {"is_not_empty": True}}
        ]
    }

    if segment_filter != "all":
        query_filter["and"].append({"property": "Segment", "select": {"equals": segment_filter}})

    # Query Notion
    results = notion.databases.query(
        database_id=NOTION_LEADS_DB_ID,
        filter=query_filter
    )

    # Parse leads
    leads = []
    for page in results["results"]:
        props = page["properties"]
        email = props.get("Email", {}).get("title", [{}])[0].get("plain_text")
        first_name = props.get("Name", {}).get("rich_text", [{}])[0].get("plain_text")

        if email:
            leads.append({"email": email, "first_name": first_name})

    logger.info(f"📧 Found {len(leads)} leads for blast (segment: {segment_filter})")
    return leads

@task(retries=3, retry_delay_seconds=60, retry_jitter_factor=0.5)
def send_blast_email(
    email: str,
    first_name: str,
    campaign_name: str,
    offer_description: str,
    landing_url: str,
    expiry_date: str
):
    """
    Send launch blast email via Loops.so.
    """
    logger = get_run_logger()

    response = httpx.post(
        "https://app.loops.so/api/v1/transactional",
        headers={"Authorization": f"Bearer {LOOPS_API_KEY}"},
        json={
            "transactionalId": "launch-blast",
            "email": email,
            "dataVariables": {
                "first_name": first_name,
                "campaign_name": campaign_name,
                "offer_description": offer_description,
                "landing_url": landing_url,
                "expiry_date": expiry_date
            }
        },
        timeout=30
    )

    response.raise_for_status()
    return {"email": email, "status": "sent"}

# ============================================================================
# Notification Tasks
# ============================================================================

@task(retries=2, retry_delay_seconds=10)
def send_launch_start_notification(campaign_name: str, channels: List[str], recipient_count: int):
    """Send Discord notification when launch starts."""
    logger = get_run_logger()

    payload = {
        "content": "🚀 **LAUNCH IN PROGRESS**",
        "embeds": [{
            "title": campaign_name,
            "description": f"Multi-channel blast initiated across {len(channels)} platforms",
            "color": 0x0099ff,
            "timestamp": datetime.now().isoformat(),
            "fields": [
                {"name": "Channels", "value": ", ".join(channels), "inline": False},
                {"name": "Email Recipients", "value": str(recipient_count), "inline": True},
                {"name": "Status", "value": "⏳ Publishing...", "inline": True}
            ]
        }]
    }

    response = httpx.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
    response.raise_for_status()
    logger.info("🚀 Sent launch start notification")

@task(retries=2, retry_delay_seconds=10)
def send_launch_complete_notification(
    campaign_name: str,
    social_results: List[Dict],
    email_results: Dict
):
    """Send Discord notification when launch completes."""
    logger = get_run_logger()

    # Build fields
    fields = []
    for result in social_results:
        fields.append({
            "name": f"{result['platform'].capitalize()} Post",
            "value": f"[View Post]({result['post_url']})",
            "inline": True
        })

    fields.append({
        "name": "Email Blast",
        "value": f"✅ {email_results['sent']} sent | ❌ {email_results['failed']} failed",
        "inline": False
    })

    payload = {
        "content": "✅ **LAUNCH COMPLETE**",
        "embeds": [{
            "title": campaign_name,
            "description": "Multi-channel blast completed successfully",
            "color": 0x00ff00,
            "timestamp": datetime.now().isoformat(),
            "fields": fields
        }]
    }

    response = httpx.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
    response.raise_for_status()
    logger.info("✅ Sent launch complete notification")

# ============================================================================
# Main Launch Flow
# ============================================================================

@flow(name="multi-channel-launch-blast", log_prints=True)
def execute_launch_blast(
    campaign_name: str,
    offer_description: str,
    landing_url: str,
    expiry_date: str,
    segment_filter: str = "all",
    social_content: str = None,
    image_url: str = None,
    platforms: List[str] = ["twitter", "linkedin", "facebook"]
):
    """
    Execute coordinated multi-channel launch blast.

    Publishes to social media platforms and sends email blast simultaneously
    for maximum reach and impact.

    Args:
        campaign_name: Campaign title (e.g., "Black Friday 50% Off")
        offer_description: Short offer summary for emails
        landing_url: Landing page URL
        expiry_date: Offer expiry date (e.g., "2025-11-30")
        segment_filter: "all" or specific segment
        social_content: Post content (auto-generated if not provided)
        image_url: Featured image URL (optional)
        platforms: List of platforms to publish to

    Returns:
        Summary with post URLs and email results
    """
    logger = get_run_logger()
    logger.info(f"🚀 Starting multi-channel launch: {campaign_name}")

    # Generate social content if not provided
    if not social_content:
        social_content = f"🎉 {campaign_name}\n\n{offer_description}\n\n👉 {landing_url}\n\n⏰ Offer ends {expiry_date}"

    # 1. Fetch leads for email blast
    leads = fetch_leads_for_blast(segment_filter)

    # 2. Send launch start notification
    send_launch_start_notification(campaign_name, platforms, len(leads))

    # 3. Publish to social media platforms (parallel)
    social_results = []

    if "twitter" in platforms:
        twitter_result = publish_to_twitter(
            content=social_content[:280],  # Twitter limit
            image_url=image_url,
            link_url=landing_url
        )
        social_results.append(twitter_result)

    if "linkedin" in platforms:
        linkedin_result = publish_to_linkedin(
            content=social_content,
            image_url=image_url,
            link_url=landing_url
        )
        social_results.append(linkedin_result)

    if "facebook" in platforms:
        facebook_result = publish_to_facebook(
            content=social_content,
            image_url=image_url,
            link_url=landing_url
        )
        social_results.append(facebook_result)

    # 4. Send email blast
    email_sent = 0
    email_failed = 0

    for lead in leads:
        try:
            send_blast_email(
                email=lead["email"],
                first_name=lead["first_name"],
                campaign_name=campaign_name,
                offer_description=offer_description,
                landing_url=landing_url,
                expiry_date=expiry_date
            )
            email_sent += 1
        except Exception as e:
            logger.error(f"❌ Failed to send to {lead['email']}: {e}")
            email_failed += 1

    email_results = {"sent": email_sent, "failed": email_failed}

    # 5. Send launch complete notification
    send_launch_complete_notification(campaign_name, social_results, email_results)

    logger.info(f"✅ Launch complete: {campaign_name}")
    logger.info(f"   Social posts: {len(social_results)}")
    logger.info(f"   Emails sent: {email_sent}")
    logger.info(f"   Emails failed: {email_failed}")

    return {
        "status": "success",
        "campaign_name": campaign_name,
        "social_posts": social_results,
        "email_results": email_results
    }

# ============================================================================
# Scheduled Launch Checker
# ============================================================================

@task
def fetch_scheduled_launches():
    """
    Fetch scheduled launches from Notion Content Calendar.

    Returns launches scheduled for today at current hour.
    """
    logger = get_run_logger()
    notion = Client(auth=NOTION_API_KEY)

    # Get current date and hour
    now = datetime.now()
    today = now.date().isoformat()
    current_hour = now.strftime("%H:00")

    # Query Notion for scheduled content
    results = notion.databases.query(
        database_id=NOTION_CONTENT_DB_ID,
        filter={
            "and": [
                {"property": "Scheduled Date", "date": {"equals": today}},
                {"property": "Scheduled Time", "rich_text": {"equals": current_hour}},
                {"property": "Status", "select": {"equals": "scheduled"}}
            ]
        }
    )

    # Parse launches
    launches = []
    for page in results["results"]:
        props = page["properties"]
        launches.append({
            "notion_id": page["id"],
            "campaign_name": props.get("Content", {}).get("title", [{}])[0].get("plain_text", ""),
            "social_content": props.get("Content", {}).get("title", [{}])[0].get("plain_text", ""),
            "image_url": props.get("Image URL", {}).get("url"),
            "landing_url": props.get("Link URL", {}).get("url"),
            "platforms": [p["name"] for p in props.get("Platforms", {}).get("multi_select", [])]
        })

    logger.info(f"📅 Found {len(launches)} scheduled launches")
    return launches

@flow(name="scheduled-launch-checker", log_prints=True)
def check_and_execute_scheduled_launches():
    """
    Check Notion Content Calendar for scheduled launches and execute them.

    Runs hourly via cron schedule.
    """
    logger = get_run_logger()
    logger.info("📅 Checking for scheduled launches...")

    launches = fetch_scheduled_launches()

    for launch in launches:
        logger.info(f"🚀 Executing scheduled launch: {launch['campaign_name']}")

        execute_launch_blast(
            campaign_name=launch["campaign_name"],
            offer_description=launch["campaign_name"],  # Simplified
            landing_url=launch["landing_url"],
            expiry_date=(datetime.now() + timedelta(days=7)).date().isoformat(),
            social_content=launch["social_content"],
            image_url=launch["image_url"],
            platforms=launch["platforms"] or ["twitter", "linkedin", "facebook"]
        )

    logger.info(f"✅ Scheduled launch check complete ({len(launches)} executed)")
    return {"status": "success", "launches_executed": len(launches)}

# ============================================================================
# Deployment Configuration
# ============================================================================

if __name__ == "__main__":
    """
    Deploy multi-channel launch flows.

    1. Manual trigger via event
    2. Scheduled checker (hourly)
    """
    print("🚀 Deploying Multi-Channel Launch Flows...")

    # Flow 1: Manual trigger
    execute_launch_blast.serve(
        name="launch-blast-manual",
        triggers=[
            DeploymentEventTrigger(
                match={"prefect.resource.id": "launch.*"},
                expect=["launch.trigger"],
                parameters={
                    "campaign_name": "{{ event.payload.campaign_name }}",
                    "offer_description": "{{ event.payload.offer_description }}",
                    "landing_url": "{{ event.payload.landing_url }}",
                    "expiry_date": "{{ event.payload.expiry_date }}",
                    "segment_filter": "{{ event.payload.segment_filter }}"
                }
            )
        ]
    )

    # Flow 2: Scheduled checker (every hour)
    check_and_execute_scheduled_launches.serve(
        name="launch-checker",
        cron="0 * * * *"  # Every hour
    )

    print("✅ Multi-Channel Launch Flows deployed!")
    print("📊 Monitor at: http://localhost:4200")
