"""
Christmas Campaign Onboarding Handler Flow.

This flow handles new client onboarding after DocuSign + payment:
1. Receives onboarding trigger from DocuSign/payment system
2. Searches for contact in BusinessX Canada Database
3. Creates onboarding sequence tracking record
4. Schedules 3-email onboarding welcome sequence

The flow ensures idempotency - if an onboarding sequence already exists
for this contact, it will not create duplicate records.

Author: Christmas Campaign Team
Created: 2025-11-27
"""

from prefect import flow, get_run_logger
from typing import Optional, List, Dict, Any
from datetime import datetime

# Import Notion operations
from campaigns.christmas_campaign.tasks.notion_operations import (
    search_contact_by_email
)


@flow(
    name="christmas-onboarding-handler",
    description="Handle new client onboarding and start welcome sequence",
    log_prints=True
)
def onboarding_handler_flow(
    email: str,
    first_name: str,
    business_name: str,
    payment_confirmed: bool,
    payment_amount: float,
    payment_date: str,
    docusign_completed: bool = True,
    salon_address: Optional[str] = None,
    observation_dates: Optional[List[str]] = None,
    start_date: Optional[str] = None,
    package_type: str = "Phase 1 - Traditional Service Diagnostic"
) -> dict:
    """
    Handle new client onboarding and trigger 3-email welcome sequence.

    Args:
        email: Client email address
        first_name: Client first name
        business_name: Salon/business name
        payment_confirmed: Whether payment was confirmed
        payment_amount: Payment amount (e.g., 2997.00)
        payment_date: Payment date (ISO format)
        docusign_completed: Whether DocuSign contract was completed
        salon_address: Physical address of salon (optional)
        observation_dates: List of scheduled observation dates (optional)
        start_date: Phase 1 start date (ISO format, optional)
        package_type: Package purchased (default: Phase 1)

    Returns:
        Flow result with status and sequence_id

    Example:
        result = onboarding_handler_flow(
            email="sarah@example.com",
            first_name="Sarah",
            business_name="Sarah's Salon",
            payment_confirmed=True,
            payment_amount=2997.00,
            payment_date="2025-12-01T15:00:00Z",
            docusign_completed=True,
            salon_address="123 Main St, Toronto, ON",
            observation_dates=["2025-12-10", "2025-12-17"],
            start_date="2025-12-10"
        )
    """
    logger = get_run_logger()
    logger.info(f"🎉 Onboarding Handler started for {email}")
    logger.info(f"   Business: {business_name}")
    logger.info(f"   Package: {package_type}")
    logger.info(f"   Payment: ${payment_amount:.2f} on {payment_date}")

    # ==============================================================================
    # Step 1: Validate payment and DocuSign
    # ==============================================================================

    if not payment_confirmed:
        logger.error(f"❌ Payment not confirmed for {email}")
        return {
            "status": "error",
            "message": f"Payment not confirmed for {email}",
            "email": email
        }

    if not docusign_completed:
        logger.warning(f"⚠️ DocuSign not completed for {email}")
        # Continue anyway, but log the warning

    # ==============================================================================
    # Step 2: Search for contact
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
    # Step 3: Check for existing onboarding sequence (Idempotency)
    # ==============================================================================

    # TODO: Implement idempotency check in Wave 4
    logger.info("⏭️  Idempotency check not yet implemented (Wave 4)")

    # ==============================================================================
    # Step 4: Create onboarding sequence tracking record
    # ==============================================================================

    # TODO: Implement sequence creation in Wave 4
    logger.info("⏭️  Sequence creation not yet implemented (Wave 4)")

    # Log onboarding details for future use
    if salon_address:
        logger.info(f"🏢 Salon Address: {salon_address}")

    if observation_dates:
        logger.info(f"📅 Observation Dates: {', '.join(observation_dates)}")

    if start_date:
        logger.info(f"🚀 Start Date: {start_date}")

    # ==============================================================================
    # Step 5: Schedule 3-email onboarding sequence
    # ==============================================================================

    # TODO: Implement email scheduling in Wave 4
    logger.info("⏭️  Email scheduling not yet implemented (Wave 4)")

    # ==============================================================================
    # Return result
    # ==============================================================================

    logger.info(f"✅ Onboarding Handler skeleton execution complete for {email}")

    return {
        "status": "skeleton_complete",
        "message": "Flow skeleton created successfully (Wave 1)",
        "email": email,
        "business_name": business_name,
        "payment_confirmed": payment_confirmed,
        "payment_amount": payment_amount,
        "package_type": package_type,
        "contact_id": contact_id
    }


# ==============================================================================
# Main execution (for testing)
# ==============================================================================

if __name__ == "__main__":
    # Test the flow with sample data
    result = onboarding_handler_flow(
        email="test@example.com",
        first_name="Test",
        business_name="Test Salon",
        payment_confirmed=True,
        payment_amount=2997.00,
        payment_date="2025-12-01T15:00:00Z",
        docusign_completed=True,
        salon_address="123 Main St, Toronto, ON",
        observation_dates=["2025-12-10", "2025-12-17"],
        start_date="2025-12-10"
    )
    print(f"\nFlow Result: {result}")
