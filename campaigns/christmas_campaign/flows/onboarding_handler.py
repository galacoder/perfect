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
from datetime import datetime, timedelta
import os
import asyncio

# Import Notion operations
from campaigns.christmas_campaign.tasks.notion_operations import (
    search_contact_by_email,
    create_onboarding_sequence,
    search_email_sequence_by_email
)


# ==============================================================================
# Onboarding Email Scheduling Function (Wave 4, Feature 4.3)
# ==============================================================================

def schedule_onboarding_emails(
    email: str,
    first_name: str,
    business_name: str,
    payment_date: str,
    salon_address: Optional[str] = None,
    observation_dates: Optional[List[str]] = None,
    start_date: Optional[str] = None,
    sequence_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Schedule 3 onboarding emails using Prefect Deployment.

    Timing depends on TESTING_MODE:
    - Production: [1h, 24h (Day 1), 72h (Day 3)] (3 days total)
    - Testing: [1min, 2min, 3min] (~3 minutes total)

    Args:
        email: Client email address
        first_name: Client first name
        business_name: Business name
        payment_date: Payment date
        salon_address: Salon physical address (optional)
        observation_dates: List of observation dates (optional)
        start_date: Phase 1 start date (optional)
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

        # Onboarding email timing
        # Production: 1h, Day 1 (24h), Day 3 (72h)
        # Testing: 1min, 2min, 3min
        if testing_mode:
            delays_hours = [1/60, 2/60, 3/60]
            logger.info("⚡ TESTING MODE: Using fast delays (1min, 2min, 3min)")
        else:
            delays_hours = [1, 24, 72]  # 1 hour, 1 day, 3 days
            logger.info("🚀 PRODUCTION MODE: Using standard delays (1h, 24h, 72h)")

        async with get_client() as client:
            try:
                deployment = await client.read_deployment_by_name(
                    "christmas-send-email/christmas-send-email"
                )
                logger.info(f"✅ Found deployment: {deployment.id}")
            except Exception as e:
                logger.error(f"❌ Failed to find deployment: {e}")
                raise

            # Schedule each of the 3 onboarding emails
            for email_number in range(1, 4):
                delay_hours = delays_hours[email_number - 1]
                scheduled_dt = datetime.now() + timedelta(hours=delay_hours)
                template_id = f"onboarding_phase1_email_{email_number}"

                logger.info(
                    f"📧 Scheduling Onboarding Email #{email_number} ({template_id}) "
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
                        "payment_date": payment_date,
                        "salon_address": salon_address,
                        "observation_dates": observation_dates,
                        "start_date": start_date,
                        "campaign": "Christmas 2025",
                        "template_type": "Onboarding"
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
    try:
        if asyncio.get_event_loop().is_running():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            scheduled = loop.run_until_complete(schedule_all_emails())
            loop.close()
        else:
            scheduled = asyncio.run(schedule_all_emails())

        scheduled_flows.extend(scheduled)
        logger.info(f"✅ Successfully scheduled {len(scheduled_flows)} onboarding emails")
        return scheduled_flows

    except Exception as e:
        logger.error(f"❌ Error scheduling onboarding emails: {e}")
        raise


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

    logger.info(f"🔍 Checking for existing onboarding sequence for {email}...")

    existing_sequence = search_email_sequence_by_email(email)

    if existing_sequence:
        template_type = existing_sequence.get("properties", {}).get("Template Type", {}).get("select", {}).get("name")

        if template_type == "Onboarding":
            logger.info(f"⚠️  Onboarding sequence already exists for {email}")
            return {
                "status": "skipped",
                "reason": "duplicate_onboarding_sequence",
                "email": email,
                "existing_sequence_id": existing_sequence["id"]
            }
        else:
            logger.info(f"✅ Existing sequence is {template_type}, will create onboarding sequence")

    # ==============================================================================
    # Step 4: Create onboarding sequence tracking record
    # ==============================================================================

    logger.info(f"📝 Creating onboarding sequence for {email}...")

    # Log onboarding details
    if salon_address:
        logger.info(f"🏢 Salon Address: {salon_address}")

    if observation_dates:
        logger.info(f"📅 Observation Dates: {', '.join(observation_dates)}")

    if start_date:
        logger.info(f"🚀 Start Date: {start_date}")

    sequence = create_onboarding_sequence(
        email=email,
        first_name=first_name,
        business_name=business_name,
        payment_confirmed=payment_confirmed,
        payment_amount=payment_amount,
        payment_date=payment_date,
        package_type=package_type,
        salon_address=salon_address,
        observation_dates=observation_dates,
        start_date=start_date
    )

    sequence_id = sequence["id"]
    logger.info(f"✅ Created onboarding sequence: {sequence_id}")

    # ==============================================================================
    # Step 5: Schedule 3-email onboarding sequence
    # ==============================================================================

    logger.info(f"📅 Scheduling 3 onboarding welcome emails for {email}...")

    scheduled_emails = schedule_onboarding_emails(
        email=email,
        first_name=first_name,
        business_name=business_name,
        payment_date=payment_date,
        salon_address=salon_address,
        observation_dates=observation_dates,
        start_date=start_date,
        sequence_id=sequence_id
    )

    logger.info(f"✅ Scheduled {len(scheduled_emails)} emails")

    # ==============================================================================
    # Return result
    # ==============================================================================

    logger.info(f"✅ Onboarding Handler execution complete for {email}")

    return {
        "status": "success",
        "message": f"Onboarding sequence created and {len(scheduled_emails)} emails scheduled",
        "email": email,
        "business_name": business_name,
        "payment_confirmed": payment_confirmed,
        "payment_amount": payment_amount,
        "payment_date": payment_date,
        "package_type": package_type,
        "contact_id": contact_id,
        "sequence_id": sequence_id,
        "scheduled_emails": scheduled_emails
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
