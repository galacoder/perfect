"""
Christmas Campaign Signup Handler Flow.

This flow handles new customer signups from the Christmas campaign:
1. Receives signup data from webhook
2. Creates/updates contact in BusinessX Canada Database
3. Creates email sequence tracking record in Email Sequence Database
4. Schedules 5-email nurture sequence via Prefect Deployment (Emails 2-5)

Architecture (Website-First):
- Website sends Email 1 immediately after signup
- Website marks "Email 1 Sent" in Notion Email Sequence DB
- Prefect schedules and sends Emails 2-5

The flow ensures idempotency - if the customer already exists in the email
sequence, it will not create duplicate records or schedule duplicate emails.

Author: Christmas Campaign Team
Created: 2025-11-19
Updated: 2025-11-28 (Changed to 5-day sequence, website-first architecture)
"""

from prefect import flow, get_run_logger
from prefect.client.schemas.schedules import IntervalSchedule
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import asyncio

# Import Notion operations
from campaigns.christmas_campaign.tasks.notion_operations import (
    search_contact_by_email,
    search_email_sequence_by_email,
    create_email_sequence,
    update_assessment_data
)

# Load environment variables
load_dotenv()

# Note: TESTING_MODE is loaded inside schedule_email_sequence async context
# to properly access Prefect Secret blocks within the flow runtime


# ==============================================================================
# Helper Function: Schedule Email Sequence via Prefect Deployment
# ==============================================================================

def schedule_email_sequence(
    email: str,
    first_name: str,
    business_name: str,
    segment: str,
    assessment_score: int,
    red_systems: int = 0,
    orange_systems: int = 0,
    yellow_systems: int = 0,
    green_systems: int = 0,
    gps_score: Optional[int] = None,
    money_score: Optional[int] = None,
    weakest_system_1: Optional[str] = None,
    weakest_system_2: Optional[str] = None,
    strongest_system: Optional[str] = None,
    revenue_leak_total: Optional[int] = None,
    start_from_email: int = 2
) -> List[Dict[str, Any]]:
    """
    Schedule emails 2-5 using Prefect Deployment (5-day sequence).

    Architecture:
    - Website sends Email 1 immediately after signup
    - This function schedules Emails 2-5 via Prefect
    - By default, starts from Email 2 (website-first architecture)

    This function creates flow runs for each scheduled email. Timing depends on TESTING_MODE:
    - Production: Email 2 at +24h, Email 3 at +72h, Email 4 at +96h, Email 5 at +120h
    - Testing: Email 2 at +1min, Email 3 at +2min, Email 4 at +3min, Email 5 at +4min

    Args:
        email: Customer email address
        first_name: Customer first name
        business_name: Business name
        segment: CRITICAL/URGENT/OPTIMIZE
        assessment_score: Overall BusOS score
        red_systems: Number of red systems
        orange_systems: Number of orange systems
        yellow_systems: Number of yellow systems
        green_systems: Number of green systems
        gps_score: GPS system score (optional)
        money_score: Money system score (optional)
        weakest_system_1: Weakest system name (optional)
        weakest_system_2: Second weakest system (optional)
        strongest_system: Strongest system name (optional)
        revenue_leak_total: Revenue leak estimate (optional)
        start_from_email: Email number to start from (default: 2, since website sends Email 1)

    Returns:
        List of scheduled flow run details (email_number, flow_run_id, scheduled_time)

    Example:
        scheduled = schedule_email_sequence(
            email="sarah@example.com",
            first_name="Sarah",
            business_name="Sarah's Salon",
            segment="CRITICAL",
            assessment_score=52,
            red_systems=2
        )
        # Returns: [
        #   {"email_number": 2, "flow_run_id": "...", "scheduled_time": "2025-11-20T10:00:00"},
        #   {"email_number": 3, "flow_run_id": "...", "scheduled_time": "2025-11-22T10:00:00"},
        #   ...
        # ]
    """
    logger = get_run_logger()

    scheduled_flows = []

    # Use async context to interact with Prefect API
    async def schedule_all_emails():
        from prefect.client.orchestration import get_client
        from prefect.blocks.system import Secret

        # Load TESTING_MODE from Secret block (sync call within async context)
        testing_mode = False
        try:
            secret = Secret.load("testing-mode")
            value = secret.get()
            logger.info(f"✅ Loaded TESTING_MODE from Secret block: {value}")
            # Handle both boolean and string values
            if isinstance(value, bool):
                testing_mode = value
            else:
                testing_mode = str(value).lower() == "true"
        except Exception as e:
            logger.warning(f"⚠️ Failed to load testing-mode Secret: {e}")
            testing_mode = os.getenv("TESTING_MODE", "false").lower() == "true"

        # 5-Day Email Sequence Timing (hours from now)
        # Email 1 is sent by website immediately, so we skip it
        # Production: Email 2 at +24h, Email 3 at +72h, Email 4 at +96h, Email 5 at +120h
        # Testing: Email 2 at +1min, Email 3 at +2min, Email 4 at +3min, Email 5 at +4min
        if testing_mode:
            # Testing mode: 1 minute between emails
            delays_hours = {
                1: 0,       # Email 1: sent by website
                2: 1/60,    # Email 2: 1 minute
                3: 2/60,    # Email 3: 2 minutes
                4: 3/60,    # Email 4: 3 minutes
                5: 4/60     # Email 5: 4 minutes
            }
            logger.info("⚡ TESTING MODE: Using fast delays (minutes)")
        else:
            # Production mode: 5-day sequence
            delays_hours = {
                1: 0,       # Email 1: sent by website (Day 0)
                2: 24,      # Email 2: Day 1 (24 hours)
                3: 72,      # Email 3: Day 3 (72 hours)
                4: 96,      # Email 4: Day 4 (96 hours)
                5: 120      # Email 5: Day 5 (120 hours)
            }
            logger.info("🚀 PRODUCTION MODE: Using 5-day delays")

        async with get_client() as client:
            # Find the deployment
            try:
                deployment = await client.read_deployment_by_name(
                    "christmas-send-email/christmas-send-email"
                )
                logger.info(f"✅ Found deployment: {deployment.id}")
            except Exception as e:
                logger.error(f"❌ Failed to find deployment: {e}")
                logger.error(f"   Make sure to run: python campaigns/christmas_campaign/deployments/deploy_christmas.py")
                raise

            # Schedule emails from start_from_email to 5 (5-day sequence)
            # Default: start_from_email=2 (website sends Email 1)
            for email_number in range(start_from_email, 6):  # 2, 3, 4, 5
                delay_hours = delays_hours.get(email_number, 0)
                scheduled_time = datetime.now() + timedelta(hours=delay_hours)

                logger.info(
                    f"📧 Scheduling Email #{email_number} for {scheduled_time.strftime('%Y-%m-%d %H:%M:%S')} "
                    f"({delay_hours:.2f} hours from now)"
                )

                # Create flow run with scheduled time
                from prefect.states import Scheduled

                flow_run = await client.create_flow_run_from_deployment(
                    deployment_id=deployment.id,
                    parameters={
                        "email_number": email_number,
                        "email": email,
                        "first_name": first_name,
                        "business_name": business_name,
                        "segment": segment,
                        "assessment_score": assessment_score,
                        "red_systems": red_systems,
                        "orange_systems": orange_systems,
                        "yellow_systems": yellow_systems,
                        "green_systems": green_systems,
                        "gps_score": gps_score,
                        "money_score": money_score,
                        "weakest_system_1": weakest_system_1,
                        "weakest_system_2": weakest_system_2,
                        "strongest_system": strongest_system,
                        "revenue_leak_total": revenue_leak_total
                    },
                    state=Scheduled(scheduled_time=scheduled_time)
                )

                scheduled_flows.append({
                    "email_number": email_number,
                    "flow_run_id": str(flow_run.id),
                    "scheduled_time": scheduled_time.isoformat(),
                    "delay_hours": delay_hours
                })

                logger.info(f"   ✅ Email #{email_number} scheduled: {flow_run.id}")

        return scheduled_flows

    # Run the async function
    try:
        result = asyncio.run(schedule_all_emails())
        return result
    except Exception as e:
        logger.error(f"❌ Error scheduling email sequence: {e}")
        raise


@flow(
    name="christmas-signup-handler",
    description="Handle Christmas campaign signup and start 5-day email sequence (Emails 2-5)",
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
    strongest_system: Optional[str] = None,
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

        # Check if any emails have been sent (5-day sequence)
        props = existing_sequence["properties"]
        emails_sent = []
        for i in range(1, 6):  # 5-day sequence: Emails 1-5
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
    # Step 5: Schedule 5-day nurture sequence via Prefect Deployment (Emails 2-5)
    # ==============================================================================

    # Determine start email: Check if Email 1 was already sent by website
    start_email = 2  # Default: website sends Email 1
    if existing_sequence:
        email_1_sent = existing_sequence["properties"].get("Email 1 Sent", {}).get("date")
        if email_1_sent:
            logger.info(f"✅ Email 1 already sent at {email_1_sent['start']} (website)")
            start_email = 2
        else:
            # Website hasn't sent Email 1 yet - Prefect will send all 5
            logger.warning(f"⚠️ Email 1 not yet sent - Prefect will schedule from Email 1")
            start_email = 1

    logger.info(f"🚀 Scheduling 5-day email sequence via Prefect Deployment")
    logger.info(f"   Starting from Email #{start_email}, Sequence ID: {sequence_id}, Segment: {segment}")

    try:
        scheduled_flows = schedule_email_sequence(
            email=email,
            first_name=first_name,
            business_name=business_name,
            segment=segment,
            assessment_score=assessment_score,
            red_systems=red_systems,
            orange_systems=orange_systems,
            yellow_systems=yellow_systems,
            green_systems=green_systems,
            gps_score=gps_score,
            money_score=money_score,
            weakest_system_1=weakest_system_1,
            weakest_system_2=weakest_system_2,
            strongest_system=strongest_system,
            revenue_leak_total=revenue_leak_total,
            start_from_email=start_email
        )

        logger.info(f"✅ Scheduled {len(scheduled_flows)} email flows")
        for flow_info in scheduled_flows:
            logger.info(
                f"   Email #{flow_info['email_number']}: "
                f"{flow_info['flow_run_id']} @ {flow_info['scheduled_time']}"
            )

        orchestrator_result = {
            "status": "success",
            "scheduled_count": len(scheduled_flows),
            "scheduled_flows": scheduled_flows
        }

    except Exception as e:
        logger.error(f"❌ Failed to schedule email sequence: {e}")
        logger.error(f"   Continuing with signup - emails will need to be scheduled manually")
        orchestrator_result = {
            "status": "failed",
            "scheduled_count": 0,
            "error": str(e),
            "note": "Signup succeeded but email scheduling failed - check deployment"
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
