"""
Single email sender flow for Christmas Campaign.

This is an atomic operation that sends ONE email and tracks its delivery.
Each email in the 7-email sequence has its own deployment of this flow.

Flow responsibilities:
1. Fetch contact data from Notion
2. Determine template ID based on email number and segment
3. Fetch template from Notion (with fallback)
4. Substitute variables
5. Send email via Resend
6. Track delivery in Notion
7. Log analytics

Author: Christmas Campaign Team
Created: 2025-11-16
"""

from prefect import flow, get_run_logger
from datetime import datetime
from typing import Optional

# Import tasks
from campaigns.christmas_campaign.tasks.notion_operations import (
    search_contact_by_email,
    fetch_email_template,
    track_email_sent,
    log_email_analytics
)
from campaigns.christmas_campaign.tasks.resend_operations import (
    send_template_email,
    get_email_variables,
    get_fallback_template
)
from campaigns.christmas_campaign.tasks.routing import get_email_template_id


@flow(
    name="christmas-send-email",
    description="Send single email in Christmas campaign nurture sequence",
    retries=1,
    retry_delay_seconds=300
)
def send_email_flow(
    email: str,
    email_number: int,
    first_name: str = "there",
    business_name: str = "your business",
    segment: str = "OPTIMIZE",
    assessment_score: Optional[int] = None
) -> dict:
    """
    Send single email in the Christmas campaign nurture sequence.

    This flow is deployed 7 times (one per email) and scheduled by the
    orchestrator flow with calculated delays.

    Args:
        email: Contact email address
        email_number: Email number in sequence (1-7)
        first_name: Contact first name (for personalization)
        business_name: Business name (for personalization)
        segment: Contact segment (CRITICAL/URGENT/OPTIMIZE)
        assessment_score: BusOS score (optional)

    Returns:
        Dict with status, resend_email_id, and metadata

    Example:
        # Deployed as "christmas-email-1"
        result = send_email_flow(
            email="john@testcorp.com",
            email_number=1,
            first_name="John",
            business_name="Test Corp",
            segment="URGENT",
            assessment_score=45
        )
    """
    logger = get_run_logger()
    logger.info(f"🚀 Starting email #{email_number} send for {email}")

    try:
        # Step 1: Fetch contact from Notion (to get page_id and verify contact exists)
        logger.info(f"📋 Fetching contact: {email}")
        contact = search_contact_by_email(email)

        if not contact:
            logger.error(f"❌ Contact not found: {email}")
            return {
                "status": "failed",
                "error": "Contact not found",
                "email_number": email_number
            }

        page_id = contact["id"]
        logger.info(f"✅ Contact found: {page_id}")

        # Step 2: Get template ID based on email number and segment
        logger.info(f"🎯 Determining template for email #{email_number}, segment: {segment}")
        template_id = get_email_template_id(email_number, segment)
        logger.info(f"📧 Using template: {template_id}")

        # Step 3: Fetch template from Notion
        logger.info(f"📥 Fetching template from Notion: {template_id}")
        template_data = fetch_email_template(template_id)

        # Step 3b: Use fallback if Notion fetch fails
        if not template_data:
            logger.warning(f"⚠️ Template {template_id} not found in Notion, using fallback")
            template_data = get_fallback_template(template_id)

        subject = template_data.get("subject", "Update from BusOS")
        html_body = template_data.get("html_body", "")

        # Step 4: Build variables for template substitution
        logger.info("🔧 Building email variables")
        variables = get_email_variables(
            first_name=first_name,
            business_name=business_name,
            assessment_score=assessment_score,
            segment=segment
        )

        # Step 5: Send email via Resend
        logger.info(f"📤 Sending email to {email}")
        resend_email_id = send_template_email(
            to_email=email,
            subject=subject,
            template=html_body,
            variables=variables
        )
        logger.info(f"✅ Email sent: {resend_email_id}")

        # Step 6: Track email sent in Notion contact record
        logger.info(f"📝 Tracking email #{email_number} sent in Notion")
        track_email_sent(page_id, email_number)

        # Step 7: Log email analytics
        logger.info("📊 Logging email analytics")
        log_email_analytics(
            email=email,
            template_id=template_id,
            email_number=email_number,
            status="sent",
            resend_email_id=resend_email_id
        )

        # Return success
        return {
            "status": "success",
            "email_number": email_number,
            "resend_email_id": resend_email_id,
            "template_id": template_id,
            "sent_at": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ Error sending email #{email_number} to {email}: {e}")

        # Log failure analytics
        try:
            log_email_analytics(
                email=email,
                template_id=template_id if 'template_id' in locals() else "unknown",
                email_number=email_number,
                status="failed",
                error_message=str(e)
            )
        except:
            pass  # Don't fail if analytics logging fails

        return {
            "status": "failed",
            "email_number": email_number,
            "error": str(e),
            "failed_at": datetime.now().isoformat()
        }


# ==============================================================================
# Testing Entry Point
# ==============================================================================

if __name__ == "__main__":
    # Test email flow locally
    result = send_email_flow(
        email="test@example.com",
        email_number=1,
        first_name="Test",
        business_name="Test Corp",
        segment="OPTIMIZE",
        assessment_score=50
    )
    print(f"\n✅ Test result: {result}")
