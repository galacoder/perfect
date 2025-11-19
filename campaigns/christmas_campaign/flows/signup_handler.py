"""
Christmas Campaign Signup Handler Flow.

This flow handles new customer signups from the Christmas campaign:
1. Receives signup data from webhook
2. Creates/updates contact in BusinessX Canada Database
3. Creates email sequence tracking record in Email Sequence Database
4. Schedules 7-email nurture sequence via Prefect Deployment

The flow ensures idempotency - if the customer already exists in the email
sequence, it will not create duplicate records or schedule duplicate emails.

Author: Christmas Campaign Team
Created: 2025-11-19
"""

from prefect import flow, get_run_logger
from typing import Optional
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Import Notion operations
from campaigns.christmas_campaign.tasks.notion_operations import (
    search_contact_by_email,
    search_email_sequence_by_email,
    create_email_sequence,
    update_assessment_data
)

# Load environment variables
load_dotenv()

# Configuration
TESTING_MODE = os.getenv("TESTING_MODE", "false").lower() == "true"


@flow(
    name="christmas-signup-handler",
    description="Handle Christmas campaign signup and start email sequence",
    log_prints=True
)
def signup_handler_flow(
    email: str,
    first_name: str,
    business_name: str,
    assessment_score: int,
    red_systems: int = 0,
    orange_systems: int = 0,
    yellow_systems: int = 0,
    green_systems: int = 0,
    gps_score: Optional[int] = None,
    money_score: Optional[int] = None,
    weakest_system_1: Optional[str] = None,
    weakest_system_2: Optional[str] = None,
    revenue_leak_total: Optional[int] = None
) -> dict:
    """
    Handle Christmas campaign signup and start nurture sequence.

    Args:
        email: Customer email address
        first_name: Customer first name
        business_name: Business name
        assessment_score: Overall BusOS score (0-100)
        red_systems: Number of red (broken) systems
        orange_systems: Number of orange (struggling) systems
        yellow_systems: Number of yellow (functional) systems
        green_systems: Number of green (optimized) systems
        gps_score: GPS system score (optional)
        money_score: Money system score (optional)
        weakest_system_1: Weakest system name (optional)
        weakest_system_2: Second weakest system (optional)
        revenue_leak_total: Total revenue leak estimate (optional)

    Returns:
        Flow result with status and sequence_id

    Example:
        result = signup_handler_flow(
            email="sarah@example.com",
            first_name="Sarah",
            business_name="Sarah's Salon",
            assessment_score=52,
            red_systems=2,
            orange_systems=1,
            yellow_systems=2,
            green_systems=3
        )
    """
    logger = get_run_logger()
    logger.info(f"🎄 Christmas Signup Handler started for {email}")
    logger.info(f"   Business: {business_name}, Score: {assessment_score}")

    # ==============================================================================
    # Step 1: Check for existing email sequence (Idempotency)
    # ==============================================================================

    logger.info(f"🔍 Checking if {email} is already in email sequence...")

    existing_sequence = search_email_sequence_by_email(email)

    if existing_sequence:
        sequence_id = existing_sequence["id"]
        campaign = existing_sequence["properties"]["Campaign"]["select"]["name"]

        logger.warning(f"⚠️ Email sequence already exists for {email}")
        logger.warning(f"   Sequence ID: {sequence_id}, Campaign: {campaign}")

        # Check if any emails have been sent
        props = existing_sequence["properties"]
        emails_sent = []
        for i in range(1, 8):
            if props.get(f"Email {i} Sent", {}).get("date"):
                emails_sent.append(i)

        if emails_sent:
            logger.warning(f"   Emails already sent: {emails_sent}")
            logger.warning(f"   Skipping duplicate signup - sequence already in progress")
            return {
                "status": "skipped",
                "reason": "already_in_sequence",
                "sequence_id": sequence_id,
                "emails_sent": emails_sent
            }
        else:
            logger.info(f"   Sequence exists but no emails sent yet - will continue")

    # ==============================================================================
    # Step 2: Determine segment classification
    # ==============================================================================

    logger.info(f"📊 Classifying segment based on assessment data...")

    # Segment classification logic (aligned with BusinessX Canada campaign)
    if red_systems >= 2:
        segment = "CRITICAL"
    elif red_systems == 1 or orange_systems >= 2:
        segment = "URGENT"
    else:
        segment = "OPTIMIZE"

    logger.info(f"   Segment: {segment}")
    logger.info(f"   Systems: {red_systems}R, {orange_systems}O, {yellow_systems}Y, {green_systems}G")

    # ==============================================================================
    # Step 3: Find or create contact in BusinessX Canada Database
    # ==============================================================================

    logger.info(f"🔍 Searching for contact in BusinessX Canada Database...")

    contact = search_contact_by_email(email)

    if contact:
        contact_id = contact["id"]
        logger.info(f"✅ Found existing contact: {contact_id}")

        # Update assessment data
        logger.info(f"📝 Updating assessment data for contact {contact_id}...")
        update_assessment_data(
            page_id=contact_id,
            assessment_score=assessment_score,
            red_systems=red_systems,
            orange_systems=orange_systems,
            yellow_systems=yellow_systems,
            green_systems=green_systems,
            segment=segment
        )
        logger.info(f"✅ Contact updated with assessment data")

    else:
        logger.warning(f"⚠️ Contact not found in BusinessX Canada Database")
        logger.warning(f"   This is unusual - typically contacts exist before assessment")
        logger.warning(f"   Continuing with email sequence creation only")
        contact_id = None

    # ==============================================================================
    # Step 4: Create email sequence tracking record
    # ==============================================================================

    if not existing_sequence:
        logger.info(f"📝 Creating email sequence record in Email Sequence Database...")

        sequence = create_email_sequence(
            email=email,
            first_name=first_name,
            business_name=business_name,
            assessment_score=assessment_score,
            red_systems=red_systems,
            orange_systems=orange_systems,
            yellow_systems=yellow_systems,
            green_systems=green_systems,
            segment=segment
        )

        sequence_id = sequence["id"]
        logger.info(f"✅ Email sequence record created: {sequence_id}")

    else:
        sequence_id = existing_sequence["id"]
        logger.info(f"✅ Using existing email sequence record: {sequence_id}")

    # ==============================================================================
    # Step 5: Schedule 7-email nurture sequence via Prefect Deployment
    # ==============================================================================

    logger.info(f"🚀 Email sequence scheduling will be implemented in Wave 2")
    logger.info(f"   For now, signup handler completes successfully")
    logger.info(f"   Sequence ID: {sequence_id}, Segment: {segment}")

    # TODO: Wave 2 - Implement Prefect Deployment scheduling
    # This will be implemented in Wave 2 when we create the deployment-based
    # email scheduler that schedules all 7 emails with correct timing.
    #
    # Expected implementation:
    # orchestrator_result = schedule_email_sequence(
    #     email=email,
    #     sequence_id=sequence_id,
    #     segment=segment,
    #     assessment_score=assessment_score,
    #     ...
    # )

    # Placeholder result for Wave 1
    orchestrator_result = {
        "status": "pending_wave_2_implementation",
        "scheduled_count": 0,
        "note": "Email scheduling will be implemented in Wave 2"
    }

    # ==============================================================================
    # Return result
    # ==============================================================================

    result = {
        "status": "success",
        "email": email,
        "sequence_id": sequence_id,
        "contact_id": contact_id,
        "segment": segment,
        "campaign": "Christmas 2025",
        "timestamp": datetime.now().isoformat(),
        "orchestrator_result": orchestrator_result
    }

    logger.info(f"🎉 Christmas signup handler completed for {email}")
    logger.info(f"   Sequence ID: {sequence_id}, Segment: {segment}")

    return result


if __name__ == "__main__":
    """
    Test the signup handler flow locally.

    Usage:
        python campaigns/christmas_campaign/flows/signup_handler.py
    """
    print("🧪 Testing Christmas Signup Handler Flow...")

    test_result = signup_handler_flow(
        email="sarah.test@example.com",
        first_name="Sarah",
        business_name="Sarah's Test Salon",
        assessment_score=52,
        red_systems=2,
        orange_systems=1,
        yellow_systems=2,
        green_systems=3,
        gps_score=45,
        money_score=38,
        weakest_system_1="GPS",
        weakest_system_2="Money",
        revenue_leak_total=14700
    )

    print("\n✅ Test completed!")
    print(f"Status: {test_result['status']}")
    print(f"Sequence ID: {test_result.get('sequence_id')}")
    print(f"Segment: {test_result.get('segment')}")
