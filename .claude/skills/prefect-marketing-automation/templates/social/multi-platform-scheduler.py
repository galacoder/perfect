"""
Multi-Platform Social Media Scheduler

Schedule and publish content across:
- Twitter/X (API v2)
- LinkedIn (Share API)
- Facebook Pages (Graph API)

Features:
- Scheduled posting with optimal timing
- Cross-platform content adaptation
- Engagement tracking and reporting
- Retry logic for API failures
- Discord notifications for published posts

Integrations:
- Twitter API v2 for tweets
- LinkedIn Share API for posts
- Facebook Graph API for page posts
- Notion for content calendar and tracking
- Discord for publishing notifications

Usage:
    python multi-platform-scheduler.py
    # Or deploy: prefect deploy -n social-scheduler-daily
"""

from datetime import datetime, timedelta
from prefect import flow, task
import httpx
import os
from typing import Dict, List, Optional

# Configuration
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")

LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
LINKEDIN_PERSON_URN = os.getenv("LINKEDIN_PERSON_URN")

FB_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN")
FB_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")


@task(retries=3, retry_delay_seconds=60)
def fetch_scheduled_posts():
    """
    Fetch posts scheduled for today from Notion content calendar.

    Returns:
        List of post records ready to publish
    """
    from notion_client import Client

    notion = Client(auth=NOTION_API_KEY)

    # Query content calendar for today's posts
    today = datetime.now().date()

    results = notion.databases.query(
        database_id=os.getenv("NOTION_CONTENT_CALENDAR_DB_ID"),
        filter={
            "and": [
                {
                    "property": "Scheduled Date",
                    "date": {"equals": today.isoformat()}
                },
                {
                    "property": "Status",
                    "select": {"equals": "scheduled"}
                }
            ]
        }
    )

    posts = []
    for page in results["results"]:
        props = page["properties"]

        # Get platforms (multi-select)
        platforms = [p["name"] for p in props.get("Platforms", {}).get("multi_select", [])]

        posts.append({
            "notion_id": page["id"],
            "content": props.get("Content", {}).get("rich_text", [{}])[0].get("plain_text", ""),
            "platforms": platforms,
            "scheduled_time": props.get("Scheduled Time", {}).get("rich_text", [{}])[0].get("plain_text", "09:00"),
            "image_url": props.get("Image URL", {}).get("url", None),
            "link_url": props.get("Link URL", {}).get("url", None),
            "hashtags": props.get("Hashtags", {}).get("rich_text", [{}])[0].get("plain_text", "")
        })

    print(f"📅 Found {len(posts)} posts scheduled for {today}")
    return posts


@task
def adapt_content_for_platform(content: str, platform: str, hashtags: str = ""):
    """
    Adapt content for platform-specific requirements and best practices.

    Args:
        content: Original post content
        platform: Target platform (twitter, linkedin, facebook)
        hashtags: Space-separated hashtags

    Returns:
        Adapted content string
    """
    # Platform-specific adaptations
    if platform == "twitter":
        # Twitter: 280 character limit, hashtags at end
        max_length = 280 - len(hashtags) - 2  # Account for space and hashtags
        adapted = content[:max_length]

        if hashtags:
            adapted += f"\n\n{hashtags}"

        return adapted

    elif platform == "linkedin":
        # LinkedIn: Professional tone, hashtags inline
        # LinkedIn allows 3000 chars but optimal is 150-300
        adapted = content

        if hashtags:
            # Convert hashtags to LinkedIn format
            linkedin_tags = " ".join([f"#{tag.strip('#')}" for tag in hashtags.split()])
            adapted += f"\n\n{linkedin_tags}"

        return adapted

    elif platform == "facebook":
        # Facebook: More casual, emoji-friendly
        adapted = content

        if hashtags:
            adapted += f"\n\n{hashtags}"

        return adapted

    return content


@task(retries=3, retry_delay_seconds=60, retry_jitter_factor=0.5)
def publish_to_twitter(content: str, image_url: Optional[str] = None):
    """
    Publish post to Twitter using API v2.

    Args:
        content: Tweet text (max 280 chars)
        image_url: Optional image URL to attach

    Returns:
        Tweet ID and URL
    """
    if not TWITTER_BEARER_TOKEN:
        print("⚠️ Twitter credentials not configured")
        return None

    # Note: Twitter API v2 requires OAuth 1.0a for posting
    # This is a simplified example - production would use tweepy or similar
    from requests_oauthlib import OAuth1Session

    twitter = OAuth1Session(
        TWITTER_API_KEY,
        client_secret=TWITTER_API_SECRET,
        resource_owner_key=TWITTER_ACCESS_TOKEN,
        resource_owner_secret=TWITTER_ACCESS_SECRET
    )

    # Create tweet
    payload = {"text": content}

    # Upload media if provided
    if image_url:
        # Download image
        img_response = httpx.get(image_url, timeout=30)
        img_response.raise_for_status()

        # Upload to Twitter
        media_response = twitter.post(
            "https://upload.twitter.com/1.1/media/upload.json",
            files={"media": img_response.content}
        )
        media_id = media_response.json()["media_id_string"]

        payload["media"] = {"media_ids": [media_id]}

    # Post tweet
    response = twitter.post(
        "https://api.twitter.com/2/tweets",
        json=payload
    )

    response.raise_for_status()
    tweet_data = response.json()["data"]

    tweet_id = tweet_data["id"]
    tweet_url = f"https://twitter.com/user/status/{tweet_id}"

    print(f"✅ Published to Twitter: {tweet_url}")

    return {
        "platform": "twitter",
        "post_id": tweet_id,
        "post_url": tweet_url,
        "published_at": datetime.now().isoformat()
    }


@task(retries=3, retry_delay_seconds=60, retry_jitter_factor=0.5)
def publish_to_linkedin(content: str, link_url: Optional[str] = None):
    """
    Publish post to LinkedIn using Share API.

    Args:
        content: Post text
        link_url: Optional link to share

    Returns:
        Post ID and URL
    """
    if not LINKEDIN_ACCESS_TOKEN or not LINKEDIN_PERSON_URN:
        print("⚠️ LinkedIn credentials not configured")
        return None

    # Build post payload
    payload = {
        "author": LINKEDIN_PERSON_URN,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": content
                },
                "shareMediaCategory": "ARTICLE" if link_url else "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    # Add link if provided
    if link_url:
        payload["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [{
            "status": "READY",
            "originalUrl": link_url
        }]

    # Post to LinkedIn
    response = httpx.post(
        "https://api.linkedin.com/v2/ugcPosts",
        headers={
            "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        },
        json=payload,
        timeout=30
    )

    response.raise_for_status()
    post_id = response.json()["id"]
    post_url = f"https://www.linkedin.com/feed/update/{post_id}"

    print(f"✅ Published to LinkedIn: {post_url}")

    return {
        "platform": "linkedin",
        "post_id": post_id,
        "post_url": post_url,
        "published_at": datetime.now().isoformat()
    }


@task(retries=3, retry_delay_seconds=60, retry_jitter_factor=0.5)
def publish_to_facebook(content: str, link_url: Optional[str] = None,
                       image_url: Optional[str] = None):
    """
    Publish post to Facebook Page using Graph API.

    Args:
        content: Post text
        link_url: Optional link to share
        image_url: Optional image URL to attach

    Returns:
        Post ID and URL
    """
    if not FB_ACCESS_TOKEN or not FB_PAGE_ID:
        print("⚠️ Facebook credentials not configured")
        return None

    # Build post payload
    payload = {
        "message": content,
        "access_token": FB_ACCESS_TOKEN
    }

    if link_url:
        payload["link"] = link_url

    # Determine endpoint based on media
    if image_url:
        # Post with photo
        endpoint = f"https://graph.facebook.com/v18.0/{FB_PAGE_ID}/photos"
        payload["url"] = image_url
    else:
        # Text or link post
        endpoint = f"https://graph.facebook.com/v18.0/{FB_PAGE_ID}/feed"

    # Post to Facebook
    response = httpx.post(endpoint, data=payload, timeout=30)
    response.raise_for_status()

    post_id = response.json()["id"]
    post_url = f"https://www.facebook.com/{post_id}"

    print(f"✅ Published to Facebook: {post_url}")

    return {
        "platform": "facebook",
        "post_id": post_id,
        "post_url": post_url,
        "published_at": datetime.now().isoformat()
    }


@task
def update_notion_post_status(notion_id: str, results: List[Dict]):
    """
    Update Notion content calendar with publishing results.

    Args:
        notion_id: Notion page ID for post
        results: List of publishing results per platform
    """
    from notion_client import Client

    notion = Client(auth=NOTION_API_KEY)

    # Build status text
    status_lines = []
    for result in results:
        if result:
            status_lines.append(f"{result['platform'].title()}: {result['post_url']}")

    status_text = "\n".join(status_lines) if status_lines else "Failed to publish"

    # Update Notion
    notion.pages.update(
        page_id=notion_id,
        properties={
            "Status": {"select": {"name": "published"}},
            "Published At": {"date": {"start": datetime.now().isoformat()}},
            "Post URLs": {"rich_text": [{"text": {"content": status_text}}]}
        }
    )


@task
def send_publish_notification(post_content: str, results: List[Dict]):
    """
    Send Discord notification with publishing results.

    Args:
        post_content: Original post content
        results: List of publishing results per platform
    """
    if not DISCORD_WEBHOOK_URL:
        return

    # Count successful publications
    successful = [r for r in results if r is not None]
    failed = len(results) - len(successful)

    fields = []
    for result in successful:
        fields.append({
            "name": result["platform"].title(),
            "value": f"[View Post]({result['post_url']})",
            "inline": True
        })

    payload = {
        "content": "📱 **Social Media Post Published**",
        "embeds": [{
            "title": "Multi-Platform Publishing Complete",
            "description": post_content[:200] + ("..." if len(post_content) > 200 else ""),
            "color": 0x00ff00 if failed == 0 else 0xffa500,
            "fields": fields,
            "footer": {
                "text": f"Published: {len(successful)} | Failed: {failed}"
            },
            "timestamp": datetime.now().isoformat()
        }]
    }

    httpx.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)


@flow(name="publish-scheduled-post", log_prints=True)
def publish_scheduled_post(post_data: Dict):
    """
    Publish single post to configured platforms.

    Args:
        post_data: Post data from Notion (content, platforms, images, etc.)

    Returns:
        dict: Publishing results per platform
    """
    print(f"📤 Publishing post to {len(post_data['platforms'])} platform(s)")

    results = []

    for platform in post_data["platforms"]:
        print(f"\n📱 Publishing to {platform.upper()}")

        # Adapt content for platform
        adapted_content = adapt_content_for_platform(
            content=post_data["content"],
            platform=platform,
            hashtags=post_data.get("hashtags", "")
        )

        try:
            if platform == "twitter":
                result = publish_to_twitter(
                    content=adapted_content,
                    image_url=post_data.get("image_url")
                )
            elif platform == "linkedin":
                result = publish_to_linkedin(
                    content=adapted_content,
                    link_url=post_data.get("link_url")
                )
            elif platform == "facebook":
                result = publish_to_facebook(
                    content=adapted_content,
                    link_url=post_data.get("link_url"),
                    image_url=post_data.get("image_url")
                )
            else:
                print(f"   ⚠️ Unknown platform: {platform}")
                result = None

            results.append(result)

        except Exception as e:
            print(f"   ❌ Failed to publish to {platform}: {e}")
            results.append(None)

    # Update Notion status
    update_notion_post_status(post_data["notion_id"], results)

    # Send notification
    send_publish_notification(post_data["content"], results)

    return {
        "notion_id": post_data["notion_id"],
        "platforms_attempted": len(post_data["platforms"]),
        "platforms_successful": len([r for r in results if r is not None]),
        "results": results
    }


@flow(name="social-scheduler-daily", log_prints=True)
def social_scheduler_daily():
    """
    Daily batch publishing of scheduled social media posts.

    Runs daily to publish all posts scheduled for today.

    Returns:
        dict: Publishing summary
    """
    print(f"🚀 Starting daily social media publishing")
    print(f"   Date: {datetime.now().date()}")

    # Fetch scheduled posts
    scheduled_posts = fetch_scheduled_posts()

    if not scheduled_posts:
        print("📭 No posts scheduled for today")
        return {
            "total_posts": 0,
            "successful": 0,
            "failed": 0,
            "published_at": datetime.now().isoformat()
        }

    # Publish each post
    total_successful = 0
    total_failed = 0

    for post in scheduled_posts:
        print(f"\n{'='*60}")

        try:
            result = publish_scheduled_post(post)

            if result["platforms_successful"] > 0:
                total_successful += 1
            else:
                total_failed += 1

        except Exception as e:
            print(f"❌ Failed to process post: {e}")
            total_failed += 1

    # Summary
    print(f"\n{'='*60}")
    print(f"📊 DAILY PUBLISHING SUMMARY")
    print(f"   Total Posts: {len(scheduled_posts)}")
    print(f"   ✅ Successful: {total_successful}")
    print(f"   ❌ Failed: {total_failed}")
    print(f"{'='*60}\n")

    return {
        "total_posts": len(scheduled_posts),
        "successful": total_successful,
        "failed": total_failed,
        "published_at": datetime.now().isoformat()
    }


# Deployment configuration
if __name__ == "__main__":
    # Deployment: Daily publishing at 9 AM
    social_scheduler_daily.serve(
        name="social-scheduler-daily-v1",
        cron="0 9 * * *",  # Daily at 9 AM
        description="Daily batch publishing of scheduled social media posts"
    )

    # Manual trigger for testing:
    # social_scheduler_daily()
