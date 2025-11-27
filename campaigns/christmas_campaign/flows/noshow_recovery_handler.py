"""
Christmas Campaign No-Show Recovery Handler Flow.

This flow handles Calendly no-show events:
1. Receives no-show webhook data from Calendly
2. Searches for contact in BusinessX Canada Database
3. Creates no-show sequence tracking record
4. Schedules 3-email recovery sequence

The flow ensures idempotency - if a no-show recovery sequence already exists
for this contact, it will not create duplicate records.

Author: Christmas Campaign Team
Created: 2025-11-27
"""

from prefect import flow, get_run_logger
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import os

# Import Notion operations
from campaigns.christmas_campaign.tasks.notion_operations import (
    search_contact_by_email,
    create_noshow_sequence,
    search_email_sequence_by_email
)


# ==============================================================================
# No-Show Email Scheduling Function (Wave 2, Feature 2.3)
# ==============================================================================

def schedule_noshow_emails(
    email: str,
    first_name: str,
    business_name: str,
    calendly_event_uri: str,
    scheduled_time: str,
    reschedule_url: Optional[str] = None,
    sequence_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Schedule 3 no-show recovery emails using Prefect Deployment.

    This function creates 3 separate flow runs of the send_email_flow, each scheduled
    at the appropriate delay from now. The delay timing depends on TESTING_MODE:
    - Production: [5min, 24h, 48h] (2 days total)
    - Testing: [1min, 2min, 3min] (~3 minutes total)

    Args:
        email: Contact email address
        first_name: Contact first name
        business_name: Business name
        calendly_event_uri: Calendly event URI
        scheduled_time: Original scheduled time
        reschedule_url: Calendly reschedule URL (optional)
        sequence_id: Email sequence tracking ID (optional)

    Returns:
        List of scheduled flow run details (email_number, flow_run_id, scheduled_time)

    Example:
        scheduled = schedule_noshow_emails(
            email="sarah@example.com",
            first_name="Sarah",
            business_name="Sarah's Salon",
            calendly_event_uri="https://calendly.com/events/ABC123",
            scheduled_time="2025-12-01T14:00:00Z"
        )
    """
    logger = get_run_logger()

    scheduled_flows = []

    # Use async context to interact with Prefect API
    async def schedule_all_emails():
        from prefect.client.orchestration import get_client
        from prefect.blocks.system import Secret

        # Load TESTING_MODE from Secret block
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

        # No-show recovery email timing
        # Production: 5min, 24h (Day 1), 48h (Day 2)
        # Testing: 1min, 2min, 3min
        if testing_mode:
            delays_hours = [1/60, 2/60, 3/60]  # Minutes converted to hours
            logger.info("⚡ TESTING MODE: Using fast delays (1min, 2min, 3min)")
        else:
            delays_hours = [5/60, 24, 48]  # 5 minutes, 1 day, 2 days
            logger.info("🚀 PRODUCTION MODE: Using standard delays (5min, 24h, 48h)")

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

            # Schedule each of the 3 no-show recovery emails
            for email_number in range(1, 4):
                delay_hours = delays_hours[email_number - 1]
                scheduled_dt = datetime.now() + timedelta(hours=delay_hours)

                template_id = f"noshow_recovery_email_{email_number}"

                logger.info(
                    f"📧 Scheduling No-Show Email #{email_number} ({template_id}) "
                    f"for {scheduled_dt.strftime('%Y-%m-%d %H:%M:%S')} "
                    f"({delay_hours:.2f} hours from now)"
                )

                # Create flow run with scheduled time
                from prefect.states import Scheduled

                flow_run = await client.create_flow_run_from_deployment(
                    deployment_id=deployment.id,
                    parameters={
                        "email": email,
                        "first_name": first_name,
                        "business_name": business_name,
                        "template_id": template_id,
                        "email_number": email_number,
                        "sequence_id": sequence_id,
                        "calendly_event_uri": calendly_event_uri,
                        "scheduled_time": scheduled_time,
                        "reschedule_url": reschedule_url,
                        "campaign": "Christmas 2025",
                        "template_type": "No-Show Recovery"
                    },
                    state=Scheduled(scheduled_time=scheduled_dt)
                )

                scheduled_flows.append({
                    "email_number": email_number,
                    "template_id": template_id,
                    "flow_run_id": str(flow_run.id),
                    "scheduled_time": scheduled_dt.isoformat(),
                    "delay_hours": delay_hours
                })

                logger.info(f"✅ Scheduled Email {email_number}: Flow Run ID = {flow_run.id}")

        return scheduled_flows

    # Run the async scheduling function
    import asyncio
    try:
        if asyncio.get_event_loop().is_running():
            # If we're already in an async context (e.g., during testing),
            # create a new event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            scheduled = loop.run_until_complete(schedule_all_emails())
            loop.close()
        else:
            scheduled = asyncio.run(schedule_all_emails())

        scheduled_flows.extend(scheduled)
        logger.info(f"✅ Successfully scheduled {len(scheduled_flows)} no-show recovery emails")
        return scheduled_flows

    except Exception as e:
        logger.error(f"❌ Error scheduling no-show emails: {e}")
        raise


@flow(
    name="christmas-noshow-recovery-handler",
    description="Handle Calendly no-show event and start recovery sequence",
    log_prints=True
)
def noshow_recovery_handler_flow(
    email: str,
    first_name: str,
    business_name: str,
    calendly_event_uri: str,
    scheduled_time: str,
    event_type: str = "Discovery Call - $2997 Diagnostic",
    reschedule_url: Optional[str] = None
) -> dict:
    """
    Handle Calendly no-show event and trigger 3-email recovery sequence.

    Args:
        email: Contact email address
        first_name: Contact first name
        business_name: Business name
        calendly_event_uri: Calendly event URI (unique identifier)
        scheduled_time: Original scheduled time (ISO format)
        event_type: Type of event (default: Discovery Call)
        reschedule_url: Calendly reschedule URL (optional)

    Returns:
        Flow result with status and sequence_id

    Example:
        result = noshow_recovery_handler_flow(
            email="sarah@example.com",
            first_name="Sarah",
            business_name="Sarah's Salon",
            calendly_event_uri="https://calendly.com/events/ABC123",
            scheduled_time="2025-12-01T14:00:00Z",
            reschedule_url="https://calendly.com/reschedule/ABC123"
        )
    """
    logger = get_run_logger()
    logger.info(f"🚫 No-Show Recovery Handler started for {email}")
    logger.info(f"   Business: {business_name}")
    logger.info(f"   Event: {event_type}, Scheduled: {scheduled_time}")

    # ==============================================================================
    # Step 1: Search for contact
    # ==============================================================================

    logger.info(f"🔍 Searching for contact {email} in BusinessX Canada Database...")

    contact = search_contact_by_email(email)

    if not contact:
        logger.error(f"❌ Contact not found: {email}")
        return {
            "status": "error",
            "message": f"Contact not found: {email}",
            "email": email
        }

    contact_id = contact["id"]
    logger.info(f"✅ Contact found: {contact_id}")

    # ==============================================================================
    # Step 2: Check for existing no-show recovery sequence (Idempotency)
    # ==============================================================================

    logger.info(f"🔍 Checking for existing no-show recovery sequence for {email}...")

    existing_sequence = search_email_sequence_by_email(email)

    if existing_sequence:
        # Check if it's a no-show recovery sequence
        template_type = existing_sequence.get("properties", {}).get("Template Type", {}).get("select", {}).get("name")

        if template_type == "No-Show Recovery":
            logger.info(f"⚠️  No-show recovery sequence already exists for {email}")
            return {
                "status": "skipped",
                "reason": "duplicate_noshow_sequence",
                "email": email,
                "existing_sequence_id": existing_sequence["id"]
            }
        else:
            logger.info(f"✅ Existing sequence is {template_type}, will create no-show recovery")

    # ==============================================================================
    # Step 3: Create no-show sequence tracking record
    # ==============================================================================

    logger.info(f"📝 Creating no-show recovery sequence for {email}...")

    sequence = create_noshow_sequence(
        email=email,
        first_name=first_name,
        business_name=business_name,
        calendly_event_uri=calendly_event_uri,
        scheduled_time=scheduled_time,
        event_type=event_type
    )

    sequence_id = sequence["id"]
    logger.info(f"✅ Created no-show sequence: {sequence_id}")

    # ==============================================================================
    # Step 4: Schedule 3-email recovery sequence
    # ==============================================================================

    logger.info(f"📅 Scheduling 3 no-show recovery emails for {email}...")

    scheduled_emails = schedule_noshow_emails(
        email=email,
        first_name=first_name,
        business_name=business_name,
        calendly_event_uri=calendly_event_uri,
        scheduled_time=scheduled_time,
        reschedule_url=reschedule_url,
        sequence_id=sequence_id
    )

    logger.info(f"✅ Scheduled {len(scheduled_emails)} emails")

    # ==============================================================================
    # Return result
    # ==============================================================================

    logger.info(f"✅ No-Show Recovery Handler execution complete for {email}")

    return {
        "status": "success",
        "message": f"No-show recovery sequence created and {len(scheduled_emails)} emails scheduled",
        "email": email,
        "business_name": business_name,
        "calendly_event_uri": calendly_event_uri,
        "contact_id": contact_id,
        "sequence_id": sequence_id,
        "scheduled_emails": scheduled_emails
    }


# ==============================================================================
# Main execution (for testing)
# ==============================================================================

if __name__ == "__main__":
    # Test the flow with sample data
    result = noshow_recovery_handler_flow(
        email="test@example.com",
        first_name="Test",
        business_name="Test Business",
        calendly_event_uri="https://calendly.com/events/TEST123",
        scheduled_time="2025-12-01T14:00:00Z",
        reschedule_url="https://calendly.com/reschedule/TEST123"
    )
    print(f"\nFlow Result: {result}")
