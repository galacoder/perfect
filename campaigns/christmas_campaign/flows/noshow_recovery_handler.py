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
from typing import Optional, Dict, Any
from datetime import datetime

# Import Notion operations
from campaigns.christmas_campaign.tasks.notion_operations import (
    search_contact_by_email,
    create_noshow_sequence,
    search_email_sequence_by_email
)


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

    # TODO: Implement email scheduling in Wave 2, Feature 2.3
    logger.info("⏭️  Email scheduling not yet implemented (Wave 2, Feature 2.3)")

    # ==============================================================================
    # Return result
    # ==============================================================================

    logger.info(f"✅ No-Show Recovery Handler execution complete for {email}")

    return {
        "status": "success",
        "message": "No-show recovery sequence created (emails will be scheduled in Feature 2.3)",
        "email": email,
        "business_name": business_name,
        "calendly_event_uri": calendly_event_uri,
        "contact_id": contact_id,
        "sequence_id": sequence_id
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
