"""
Christmas Campaign Post-Call Maybe Handler Flow.

This flow handles post-call "maybe" prospects:
1. Receives post-call data from CRM
2. Searches for contact in BusinessX Canada Database
3. Creates post-call sequence tracking record
4. Schedules 3-email follow-up sequence

The flow ensures idempotency - if a post-call sequence already exists
for this contact, it will not create duplicate records.

Author: Christmas Campaign Team
Created: 2025-11-27
"""

from prefect import flow, get_run_logger
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import os

# Import Notion operations
from campaigns.christmas_campaign.tasks.notion_operations import (
    search_contact_by_email,
    create_postcall_sequence,
    search_email_sequence_by_email
)


# ==============================================================================
# Post-Call Email Scheduling Function (Wave 3, Feature 3.3)
# ==============================================================================

def schedule_postcall_emails(
    email: str,
    first_name: str,
    business_name: str,
    call_date: str,
    call_notes: Optional[str] = None,
    objections: Optional[List[str]] = None,
    sequence_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Schedule 3 post-call maybe emails using Prefect Deployment.

    Timing depends on TESTING_MODE:
    - Production: [1h, 72h (Day 3), 168h (Day 7)] (7 days total)
    - Testing: [1min, 2min, 3min] (~3 minutes total)

    Args:
        email: Contact email address
        first_name: Contact first name
        business_name: Business name
        call_date: Call date
        call_notes: Notes from call (optional)
        objections: List of objections (optional)
        sequence_id: Email sequence tracking ID (optional)

    Returns:
        List of scheduled flow run details
    """
    logger = get_run_logger()
    scheduled_flows = []

    async def schedule_all_emails():
        from prefect.client.orchestration import get_client
        from prefect.blocks.system import Secret

        # Load TESTING_MODE
        testing_mode = False
        try:
            secret = Secret.load("testing-mode")
            value = secret.get()
            logger.info(f"✅ Loaded TESTING_MODE from Secret block: {value}")
            testing_mode = value if isinstance(value, bool) else str(value).lower() == "true"
        except Exception as e:
            logger.warning(f"⚠️ Failed to load testing-mode Secret: {e}")
            testing_mode = os.getenv("TESTING_MODE", "false").lower() == "true"

        # Post-call email timing
        # Production: 1h, Day 3 (72h), Day 7 (168h)
        # Testing: 1min, 2min, 3min
        if testing_mode:
            delays_hours = [1/60, 2/60, 3/60]
            logger.info("⚡ TESTING MODE: Using fast delays (1min, 2min, 3min)")
        else:
            delays_hours = [1, 72, 168]  # 1 hour, 3 days, 7 days
            logger.info("🚀 PRODUCTION MODE: Using standard delays (1h, 72h, 168h)")

        async with get_client() as client:
            try:
                deployment = await client.read_deployment_by_name(
                    "christmas-send-email/christmas-send-email"
                )
                logger.info(f"✅ Found deployment: {deployment.id}")
            except Exception as e:
                logger.error(f"❌ Failed to find deployment: {e}")
                raise

            # Schedule each of the 3 post-call emails
            for email_number in range(1, 4):
                delay_hours = delays_hours[email_number - 1]
                scheduled_dt = datetime.now() + timedelta(hours=delay_hours)
                template_id = f"postcall_maybe_email_{email_number}"

                logger.info(
                    f"📧 Scheduling Post-Call Email #{email_number} ({template_id}) "
                    f"for {scheduled_dt.strftime('%Y-%m-%d %H:%M:%S')} "
                    f"({delay_hours:.2f} hours from now)"
                )

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
                        "call_date": call_date,
                        "call_notes": call_notes,
                        "objections": objections,
                        "campaign": "Christmas 2025",
                        "template_type": "Post-Call Follow-Up"
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
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            scheduled = loop.run_until_complete(schedule_all_emails())
            loop.close()
        else:
            scheduled = asyncio.run(schedule_all_emails())

        scheduled_flows.extend(scheduled)
        logger.info(f"✅ Successfully scheduled {len(scheduled_flows)} post-call emails")
        return scheduled_flows

    except Exception as e:
        logger.error(f"❌ Error scheduling post-call emails: {e}")
        raise


@flow(
    name="christmas-postcall-maybe-handler",
    description="Handle post-call maybe prospect and start follow-up sequence",
    log_prints=True
)
def postcall_maybe_handler_flow(
    email: str,
    first_name: str,
    business_name: str,
    call_date: str,
    call_outcome: str = "Maybe",
    call_notes: Optional[str] = None,
    objections: Optional[List[str]] = None,
    follow_up_priority: str = "Medium"
) -> dict:
    """
    Handle post-call maybe prospect and trigger 3-email follow-up sequence.

    Args:
        email: Contact email address
        first_name: Contact first name
        business_name: Business name
        call_date: Call date (ISO format)
        call_outcome: Call outcome (default: Maybe)
        call_notes: Notes from the call (optional)
        objections: List of objections raised (optional)
        follow_up_priority: Follow-up priority (High/Medium/Low, default: Medium)

    Returns:
        Flow result with status and sequence_id
    """
    logger = get_run_logger()
    logger.info(f"📞 Post-Call Maybe Handler started for {email}")
    logger.info(f"   Business: {business_name}")
    logger.info(f"   Call Date: {call_date}, Outcome: {call_outcome}")
    logger.info(f"   Priority: {follow_up_priority}")

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
    # Step 2: Check for existing post-call sequence (Idempotency)
    # ==============================================================================

    logger.info(f"🔍 Checking for existing post-call sequence for {email}...")

    existing_sequence = search_email_sequence_by_email(email)

    if existing_sequence:
        template_type = existing_sequence.get("properties", {}).get("Template Type", {}).get("select", {}).get("name")

        if template_type == "Post-Call Follow-Up":
            logger.info(f"⚠️  Post-call follow-up sequence already exists for {email}")
            return {
                "status": "skipped",
                "reason": "duplicate_postcall_sequence",
                "email": email,
                "existing_sequence_id": existing_sequence["id"]
            }
        else:
            logger.info(f"✅ Existing sequence is {template_type}, will create post-call follow-up")

    # ==============================================================================
    # Step 3: Create post-call sequence tracking record
    # ==============================================================================

    logger.info(f"📝 Creating post-call follow-up sequence for {email}...")

    if call_notes:
        logger.info(f"📝 Call notes: {call_notes[:100]}...")

    if objections:
        logger.info(f"🚧 Objections: {', '.join(objections)}")

    sequence = create_postcall_sequence(
        email=email,
        first_name=first_name,
        business_name=business_name,
        call_date=call_date,
        call_outcome=call_outcome,
        call_notes=call_notes,
        objections=objections,
        follow_up_priority=follow_up_priority
    )

    sequence_id = sequence["id"]
    logger.info(f"✅ Created post-call sequence: {sequence_id}")

    # ==============================================================================
    # Step 4: Schedule 3-email follow-up sequence
    # ==============================================================================

    logger.info(f"📅 Scheduling 3 post-call follow-up emails for {email}...")

    scheduled_emails = schedule_postcall_emails(
        email=email,
        first_name=first_name,
        business_name=business_name,
        call_date=call_date,
        call_notes=call_notes,
        objections=objections,
        sequence_id=sequence_id
    )

    logger.info(f"✅ Scheduled {len(scheduled_emails)} emails")

    # ==============================================================================
    # Return result
    # ==============================================================================

    logger.info(f"✅ Post-Call Maybe Handler execution complete for {email}")

    return {
        "status": "success",
        "message": f"Post-call follow-up sequence created and {len(scheduled_emails)} emails scheduled",
        "email": email,
        "business_name": business_name,
        "call_date": call_date,
        "call_outcome": call_outcome,
        "contact_id": contact_id,
        "sequence_id": sequence_id,
        "scheduled_emails": scheduled_emails
    }


# ==============================================================================
# Main execution (for testing)
# ==============================================================================

if __name__ == "__main__":
    # Test the flow with sample data
    result = postcall_maybe_handler_flow(
        email="test@example.com",
        first_name="Test",
        business_name="Test Business",
        call_date="2025-12-01T14:30:00Z",
        call_notes="Interested but needs to check budget",
        objections=["Price", "Timing"],
        follow_up_priority="High"
    )
    print(f"\nFlow Result: {result}")
