"""
Email Nurture Sequence - Soap Opera Framework

7-email sequence implementing Russell Brunson's Soap Opera Sequence:
- Email #1: Immediate CTA (ask when hot - Hormozi timing)
- Email #2: High drama (common problems)
- Email #3: Epiphany (framework introduction)
- Email #4: Offer + guarantee (hidden benefits)
- Email #5: Case study (social proof)
- Email #6: Objection handling
- Email #7: Deadline urgency

Integrations:
- Loops.so for email delivery
- Notion for lead tracking
- Discord for engagement alerts

Usage:
    python email-nurture-sequence.py
    # Or deploy: prefect deploy -n nurture-campaign
"""

from datetime import timedelta
from prefect import flow, task
from prefect.deployments import DeploymentEventTrigger
import httpx
import os

# Configuration
LOOPS_API_KEY = os.getenv("LOOPS_API_KEY")
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")


@task(retries=3, retry_delay_seconds=60, retry_jitter_factor=0.5)
def send_loops_email(to_email: str, template_id: str, variables: dict):
    """
    Send email via Loops.so API with retry logic.

    Args:
        to_email: Recipient email address
        template_id: Loops.so template ID (e.g., "email-1-immediate-cta")
        variables: Template variables (personalization data)

    Returns:
        Response from Loops.so API

    Raises:
        httpx.HTTPStatusError: If API request fails after retries
    """
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
    return response.json()


@task
def update_notion_lead(lead_id: str, properties: dict):
    """
    Update lead properties in Notion database.

    Args:
        lead_id: Notion page ID
        properties: Dictionary of properties to update
            - email_stage: Current email in sequence (1-7)
            - last_email_sent: Date of last email
            - engagement_score: Click/open tracking score
            - status: Lead status (nurturing, engaged, cold)
    """
    from notion_client import Client

    notion = Client(auth=NOTION_API_KEY)
    notion.pages.update(
        page_id=lead_id,
        properties={
            "Email Stage": {"number": properties.get("email_stage", 0)},
            "Last Email": {"date": {"start": properties.get("last_email_sent")}},
            "Engagement Score": {"number": properties.get("engagement_score", 0)},
            "Status": {"select": {"name": properties.get("status", "nurturing")}}
        }
    )


@task
def notify_discord_engagement(lead_data: dict, email_number: int, action: str):
    """
    Send Discord notification for high-engagement actions.

    Args:
        lead_data: Lead information (name, email, score)
        email_number: Which email triggered engagement (1-7)
        action: Action taken (opened, clicked, booked, purchased)
    """
    if action in ["clicked", "booked", "purchased"]:
        emoji = {"clicked": "👆", "booked": "📅", "purchased": "💰"}[action]

        payload = {
            "content": f"{emoji} Email #{email_number} Engagement!",
            "embeds": [{
                "title": lead_data.get("name", "Unknown Lead"),
                "description": f"Action: {action.upper()}",
                "color": 0x00ff00,
                "fields": [
                    {"name": "Email", "value": lead_data["email"], "inline": True},
                    {"name": "Email #", "value": str(email_number), "inline": True},
                    {"name": "Score", "value": str(lead_data.get("score", 0)), "inline": True}
                ]
            }]
        }

        httpx.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)


@flow(name="email-nurture-soap-opera", log_prints=True)
def email_nurture_campaign(
    lead_email: str,
    lead_name: str,
    lead_id: str,
    segment: str = "general",
    from_email: str = "hello@yourdomain.com",
    notify_discord: bool = True
):
    """
    7-email Soap Opera nurture sequence.

    Args:
        lead_email: Lead's email address
        lead_name: Lead's first name (for personalization)
        lead_id: Notion page ID for tracking
        segment: Lead segment (e.g., "beauty-salon", "auto-repair")
        from_email: Sender email address
        notify_discord: Send Discord alerts for high engagement

    Returns:
        dict: Summary of emails sent and engagement

    Example:
        email_nurture_campaign(
            lead_email="minjipark@salon.com",
            lead_name="Min-Ji",
            lead_id="notion-page-id-here",
            segment="beauty-salon"
        )
    """

    # Email sequence configuration
    # Day 0, 3, 7, 14, 21 timing (standard Soap Opera)
    email_sequence = [
        {
            "day": 0,
            "template_id": "email-1-immediate-cta",
            "subject": "Your {segment} Assessment Results",
            "stage": "immediate_cta",
            "description": "Ask when hot - 2X conversion"
        },
        {
            "day": 3,
            "template_id": "email-2-high-drama",
            "subject": "The 3 systems that break EVERY {season}",
            "stage": "high_drama",
            "description": "Common problems revealed"
        },
        {
            "day": 7,
            "template_id": "email-3-epiphany",
            "subject": "Why your business is like a bus",
            "stage": "epiphany",
            "description": "BusOS framework introduction"
        },
        {
            "day": 14,
            "template_id": "email-4-offer-guarantee",
            "subject": "How the diagnostic works",
            "stage": "offer",
            "description": "The Stack + guarantee"
        },
        {
            "day": 21,
            "template_id": "email-5-case-study",
            "subject": "How Min-Ji went from 70-hour weeks to 45",
            "stage": "social_proof",
            "description": "Customer transformation story"
        },
        {
            "day": 21,  # Same day as email 5
            "template_id": "email-6-objections",
            "subject": "Can I just DIY this? (and 3 other questions)",
            "stage": "objection_handling",
            "description": "Address common concerns"
        },
        {
            "day": 28,
            "template_id": "email-7-urgency",
            "subject": "{days_left} days until {deadline}",
            "stage": "deadline",
            "description": "Create urgency"
        }
    ]

    print(f"Starting nurture sequence for {lead_name} ({lead_email})")
    print(f"Segment: {segment}")

    results = []

    for email_config in email_sequence:
        # Personalization variables
        variables = {
            "first_name": lead_name,
            "segment": segment,
            "from_email": from_email,
            "season": "Christmas",  # Make dynamic based on campaign
            "days_left": 30,  # Calculate from deadline
            "deadline": "December 20"
        }

        # Send email via Loops.so
        print(f"Sending Email #{email_sequence.index(email_config) + 1}: {email_config['stage']}")

        try:
            response = send_loops_email(
                to_email=lead_email,
                template_id=email_config["template_id"],
                variables=variables
            )

            # Update Notion with email stage
            update_notion_lead(
                lead_id=lead_id,
                properties={
                    "email_stage": email_sequence.index(email_config) + 1,
                    "last_email_sent": email_config.get("day", 0),
                    "status": "nurturing"
                }
            )

            # Track success
            results.append({
                "email": email_sequence.index(email_config) + 1,
                "stage": email_config["stage"],
                "sent": True,
                "day": email_config["day"]
            })

            print(f"  ✅ Email #{email_sequence.index(email_config) + 1} sent successfully")

        except Exception as e:
            print(f"  ❌ Email #{email_sequence.index(email_config) + 1} failed: {e}")
            results.append({
                "email": email_sequence.index(email_config) + 1,
                "stage": email_config["stage"],
                "sent": False,
                "error": str(e)
            })

    # Final summary
    sent_count = sum(1 for r in results if r.get("sent"))
    print(f"\n📊 Summary: {sent_count}/7 emails sent successfully")

    return {
        "lead_email": lead_email,
        "segment": segment,
        "emails_sent": sent_count,
        "results": results
    }


# Deployment configuration
if __name__ == "__main__":
    # Option 1: Deploy with webhook trigger (recommended)
    # Triggers when lead completes assessment or opts in

    email_nurture_campaign.serve(
        name="nurture-soap-opera-v1",
        triggers=[
            DeploymentEventTrigger(
                match={"prefect.resource.id": "lead.*"},
                expect=["lead.created", "lead.assessment_complete"],
                parameters={
                    "lead_email": "{{ event.payload.email }}",
                    "lead_name": "{{ event.payload.first_name }}",
                    "lead_id": "{{ event.payload.notion_id }}",
                    "segment": "{{ event.payload.segment }}"
                }
            )
        ],
        description="7-email Soap Opera nurture sequence triggered by lead creation"
    )

    # Option 2: Deploy with daily batch processing
    # Processes new leads from Notion database

    # email_nurture_campaign.serve(
    #     name="nurture-daily-batch",
    #     cron="0 9 * * *",  # Daily at 9 AM
    #     description="Process new leads daily at 9 AM"
    # )

    # Option 3: Manual trigger for testing
    # Uncomment to test locally:

    # email_nurture_campaign(
    #     lead_email="test@example.com",
    #     lead_name="Test",
    #     lead_id="test-notion-id",
    #     segment="test",
    #     from_email="hello@yourdomain.com"
    # )
