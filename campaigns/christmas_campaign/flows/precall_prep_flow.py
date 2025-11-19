"""
Pre-Call Prep Flow for Christmas Campaign.

This flow handles meeting bookings from Cal.com:
1. Receives booking data (email, name, meeting time)
2. Validates meeting is far enough in future
3. Schedules 3 reminder emails before the meeting
4. Updates Notion with meeting booking status

The flow schedules reminder emails at:
- Email 1: 72 hours before meeting (meeting prep guide)
- Email 2: 24 hours before meeting (reminder + what to prepare)
- Email 3: 2 hours before meeting (final reminder + meeting link)

Author: Christmas Campaign Team
Created: 2025-11-19
"""

from prefect import flow, get_run_logger
from prefect.client.orchestration import PrefectClient
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dateutil.parser import parse as parse_datetime
import asyncio
import os
from dotenv import load_dotenv

# Import Notion operations
from campaigns.christmas_campaign.tasks.notion_operations import (
    search_email_sequence_by_email,
    search_contact_by_email,
    update_booking_status
)

# Load environment variables
load_dotenv()

# Configuration
TESTING_MODE = os.getenv("TESTING_MODE", "false").lower() == "true"


# ==============================================================================
# Helper Function: Schedule Pre-Call Reminder Emails
# ==============================================================================

def schedule_precall_reminders(
    email: str,
    name: str,
    meeting_time: str
) -> List[Dict[str, Any]]:
    """
    Schedule 3 reminder emails before the meeting.

    This function creates 3 separate flow runs of the send_email_flow, each scheduled
    at the appropriate time before the meeting. The timing depends on TESTING_MODE:
    - Production: [-72h, -24h, -2h] (3 days before, 1 day before, 2 hours before)
    - Testing: [-6min, -3min, -1min] (~6 minutes total for testing)

    Args:
        email: Customer email address
        name: Customer name
        meeting_time: ISO 8601 timestamp from Cal.com

    Returns:
        List of scheduled flow run details (email_number, flow_run_id, scheduled_time)

    Example:
        scheduled = schedule_precall_reminders(
            email="customer@example.com",
            name="Customer Name",
            meeting_time="2025-11-25T14:00:00Z"
        )
        # Returns: [
        #   {"reminder_number": 1, "flow_run_id": "...", "scheduled_time": "2025-11-22T14:00:00"},
        #   {"reminder_number": 2, "flow_run_id": "...", "scheduled_time": "2025-11-24T14:00:00"},
        #   {"reminder_number": 3, "flow_run_id": "...", "scheduled_time": "2025-11-25T12:00:00"}
        # ]
    """
    logger = get_run_logger()

    # Parse meeting time
    try:
        meeting_dt = parse_datetime(meeting_time)
    except Exception as e:
        logger.error(f"❌ Failed to parse meeting time '{meeting_time}': {e}")
        raise ValueError(f"Invalid meeting time format: {meeting_time}")

    # Calculate current time with same timezone
    now = datetime.now(meeting_dt.tzinfo) if meeting_dt.tzinfo else datetime.now()

    # Calculate hours until meeting
    hours_until_meeting = (meeting_dt - now).total_seconds() / 3600

    logger.info(f"📅 Meeting scheduled for {meeting_dt.isoformat()}")
    logger.info(f"⏰ Time until meeting: {hours_until_meeting:.2f} hours")

    # Check if meeting is too soon
    if hours_until_meeting < 2:
        logger.warning(f"⚠️ Meeting in <2 hours ({hours_until_meeting:.2f}h), skipping reminders")
        return []

    # Reminder timing (hours before meeting)
    # Production: 72h before, 24h before, 2h before
    # Testing: 6min before, 3min before, 1min before
    if TESTING_MODE:
        delays_hours_before = [6/60, 3/60, 1/60]  # Minutes converted to hours
        logger.info("⚡ TESTING MODE: Using fast delays (minutes before meeting)")
    else:
        delays_hours_before = [72, 24, 2]  # Production delays (hours before)
        logger.info("🚀 PRODUCTION MODE: Using standard delays (hours before meeting)")

    # Check if we have enough time for all reminders
    max_delay = max(delays_hours_before)
    if hours_until_meeting < max_delay:
        logger.warning(f"⚠️ Meeting in {hours_until_meeting:.2f}h, less than max delay {max_delay}h")
        logger.warning(f"   Will only schedule reminders that fit before meeting")
        # Filter delays to only those that fit
        delays_hours_before = [d for d in delays_hours_before if d < hours_until_meeting]

    if not delays_hours_before:
        logger.warning(f"⚠️ No reminders fit before meeting, skipping")
        return []

    scheduled_flows = []

    # Use async context to interact with Prefect API
    async def schedule_all_reminders():
        async with PrefectClient() as client:
            # Find the deployment
            # TODO: Update this when pre-call reminder deployment is created
            deployment_name = "christmas-precall-reminder/christmas-precall-reminder"

            try:
                deployment = await client.read_deployment_by_name(deployment_name)
                logger.info(f"✅ Found deployment: {deployment.id}")
            except Exception as e:
                logger.error(f"❌ Failed to find deployment '{deployment_name}': {e}")
                logger.error(f"   Make sure pre-call reminder deployment is created")
                raise

            # Schedule each of the 3 reminder emails
            for idx, hours_before in enumerate(delays_hours_before, start=1):
                # Calculate scheduled time (meeting_time - hours_before)
                scheduled_time = meeting_dt - timedelta(hours=hours_before)

                logger.info(
                    f"📧 Scheduling Reminder #{idx} for {scheduled_time.strftime('%Y-%m-%d %H:%M:%S')} "
                    f"({hours_before:.2f} hours before meeting)"
                )

                # Create flow run with scheduled time
                flow_run = await client.create_flow_run_from_deployment(
                    deployment_id=deployment.id,
                    parameters={
                        "reminder_number": idx,
                        "email": email,
                        "name": name,
                        "meeting_time": meeting_time
                    },
                    state={
                        "type": "SCHEDULED",
                        "timestamp": scheduled_time.isoformat()
                    }
                )

                scheduled_flows.append({
                    "reminder_number": idx,
                    "flow_run_id": str(flow_run.id),
                    "scheduled_time": scheduled_time.isoformat(),
                    "hours_before_meeting": hours_before
                })

                logger.info(f"   ✅ Reminder #{idx} scheduled: {flow_run.id}")

        return scheduled_flows

    # Run the async function
    try:
        result = asyncio.run(schedule_all_reminders())
        return result
    except Exception as e:
        logger.error(f"❌ Error scheduling reminder sequence: {e}")
        raise


# ==============================================================================
# Main Flow: Pre-Call Prep
# ==============================================================================

@flow(
    name="christmas-precall-prep",
    description="Schedule pre-call prep emails after Cal.com booking",
    log_prints=True
)
def precall_prep_flow(
    email: str,
    name: str,
    meeting_time: str
) -> dict:
    """
    Schedule pre-call prep email sequence.

    This flow:
    1. Validates meeting is far enough in future (>2 hours)
    2. Schedules 3 reminder emails via Prefect Deployment
    3. Updates Notion Email Sequence DB with meeting info
    4. Returns scheduling status

    Args:
        email: Customer email address
        name: Customer name
        meeting_time: ISO 8601 timestamp from Cal.com (e.g., "2025-11-25T14:00:00Z")

    Returns:
        Flow result with status and scheduled_flows

    Example:
        result = precall_prep_flow(
            email="customer@example.com",
            name="Customer Name",
            meeting_time="2025-11-25T14:00:00Z"
        )
    """
    logger = get_run_logger()
    logger.info(f"📞 Pre-call prep flow started for {email}")
    logger.info(f"   Name: {name}, Meeting: {meeting_time}")

    # ==============================================================================
    # Step 1: Validate meeting is far enough in future
    # ==============================================================================

    try:
        meeting_dt = parse_datetime(meeting_time)
        now = datetime.now(meeting_dt.tzinfo) if meeting_dt.tzinfo else datetime.now()
        hours_until_meeting = (meeting_dt - now).total_seconds() / 3600

        if hours_until_meeting < 2:
            logger.warning(f"⚠️ Meeting in <2 hours ({hours_until_meeting:.2f}h), skipping prep sequence")
            return {
                "status": "skipped",
                "reason": "meeting_too_soon",
                "email": email,
                "meeting_time": meeting_time,
                "hours_until_meeting": hours_until_meeting
            }

    except Exception as e:
        logger.error(f"❌ Failed to parse meeting time: {e}")
        return {
            "status": "failed",
            "error": f"Invalid meeting time: {str(e)}",
            "email": email
        }

    # ==============================================================================
    # Step 2: Check if customer is in Christmas campaign
    # ==============================================================================

    logger.info(f"🔍 Checking if {email} is in Christmas campaign...")

    try:
        sequence = search_email_sequence_by_email(email)

        if sequence:
            sequence_id = sequence["id"]
            campaign = sequence["properties"]["Campaign"]["select"]["name"]
            logger.info(f"✅ Found sequence: {sequence_id}, Campaign: {campaign}")
        else:
            logger.warning(f"⚠️ No email sequence found for {email}")
            logger.warning(f"   Customer may not be in Christmas campaign yet")
            sequence_id = None

    except Exception as e:
        logger.error(f"❌ Error searching for email sequence: {e}")
        sequence_id = None

    # ==============================================================================
    # Step 3: Schedule 3 reminder emails via Prefect Deployment
    # ==============================================================================

    logger.info(f"🚀 Scheduling 3 reminder emails before meeting")

    try:
        scheduled_flows = schedule_precall_reminders(
            email=email,
            name=name,
            meeting_time=meeting_time
        )

        logger.info(f"✅ Scheduled {len(scheduled_flows)} reminder emails")
        for flow_info in scheduled_flows:
            logger.info(
                f"   Reminder #{flow_info['reminder_number']}: "
                f"{flow_info['flow_run_id']} @ {flow_info['scheduled_time']}"
            )

        scheduler_result = {
            "status": "success",
            "scheduled_count": len(scheduled_flows),
            "scheduled_flows": scheduled_flows
        }

    except Exception as e:
        logger.error(f"❌ Failed to schedule reminder sequence: {e}")
        logger.error(f"   Continuing with booking - reminders will need to be scheduled manually")
        scheduler_result = {
            "status": "failed",
            "scheduled_count": 0,
            "error": str(e),
            "note": "Booking accepted but reminder scheduling failed - check deployment"
        }

    # ==============================================================================
    # Step 4: Update Notion with meeting info
    # ==============================================================================

    logger.info(f"📝 Updating Notion with meeting booking info...")

    notion_update_result = {
        "contact_updated": False,
        "contact_id": None
    }

    try:
        # Search for contact in BusinessX Canada database
        contact = search_contact_by_email(email)

        if contact:
            contact_id = contact["id"]
            logger.info(f"✅ Found contact: {contact_id}")

            # Extract call date from meeting time (YYYY-MM-DD)
            try:
                meeting_dt = parse_datetime(meeting_time)
                call_date = meeting_dt.strftime("%Y-%m-%d")

                # Update booking status
                update_booking_status(
                    page_id=contact_id,
                    status="Booked",
                    call_date=call_date
                )

                logger.info(f"✅ Updated Notion: Booking Status = Booked, Call Date = {call_date}")

                notion_update_result = {
                    "contact_updated": True,
                    "contact_id": contact_id,
                    "booking_status": "Booked",
                    "call_date": call_date
                }

            except Exception as e:
                logger.error(f"❌ Error parsing call date or updating Notion: {e}")
                notion_update_result["error"] = str(e)

        else:
            logger.warning(f"⚠️ Contact not found in BusinessX Canada database")
            logger.warning(f"   Customer may need to be added manually")

    except Exception as e:
        logger.error(f"❌ Error updating Notion with booking info: {e}")
        notion_update_result["error"] = str(e)

    # ==============================================================================
    # Return result
    # ==============================================================================

    result = {
        "status": "success",
        "email": email,
        "name": name,
        "meeting_time": meeting_time,
        "sequence_id": sequence_id,
        "timestamp": datetime.now().isoformat(),
        "scheduler_result": scheduler_result,
        "notion_update_result": notion_update_result
    }

    logger.info(f"🎉 Pre-call prep flow completed for {email}")
    logger.info(f"   Meeting: {meeting_time}, Reminders scheduled: {scheduler_result['scheduled_count']}")
    logger.info(f"   Notion updated: {notion_update_result.get('contact_updated', False)}")

    return result


def precall_prep_flow_sync(**kwargs):
    """
    Synchronous wrapper for FastAPI BackgroundTasks.

    FastAPI BackgroundTasks expects synchronous functions, but our flow
    uses async Prefect operations internally. This wrapper handles the conversion.

    Args:
        **kwargs: All arguments to pass to precall_prep_flow

    Returns:
        Flow result dict
    """
    return precall_prep_flow(**kwargs)


if __name__ == "__main__":
    """
    Test the pre-call prep flow locally.

    Usage:
        python campaigns/christmas_campaign/flows/precall_prep_flow.py
    """
    print("🧪 Testing Pre-Call Prep Flow...")

    # Test with meeting 3 days in future
    future_meeting = (datetime.now() + timedelta(days=3)).isoformat()

    test_result = precall_prep_flow(
        email="customer.test@example.com",
        name="Test Customer",
        meeting_time=future_meeting
    )

    print("\n✅ Test completed!")
    print(f"Status: {test_result['status']}")
    print(f"Meeting Time: {test_result.get('meeting_time')}")
    print(f"Reminders Scheduled: {test_result.get('scheduler_result', {}).get('scheduled_count', 0)}")
