"""
Email sequence orchestrator flow for Christmas Campaign.

This flow schedules all 7 emails in the nurture sequence with calculated delays.

Flow responsibilities:
1. Receive assessment completion trigger
2. Classify contact into segment
3. Update Notion with assessment data
4. Schedule all 7 email flows with correct timing
5. Send Discord alert for CRITICAL segments

This flow does NOT send emails directly - it schedules 7 child flows
that will execute at the correct times using Prefect deployments.

Author: Christmas Campaign Team
Created: 2025-11-16
"""

from prefect import flow, get_run_logger
from datetime import datetime
import os
from typing import Optional

# Import tasks
from campaigns.christmas_campaign.tasks.notion_operations import (
    search_contact_by_email,
    update_assessment_data,
    update_contact_phase
)
from campaigns.christmas_campaign.tasks.routing import (
    classify_segment,
    should_send_discord_alert
)
from campaigns.christmas_campaign.deployments.deploy_utils import (
    schedule_email_flow,
    calculate_delay_hours
)

# Import models
from campaigns.christmas_campaign.tasks.models import AssessmentData


@flow(
    name="christmas-email-sequence-orchestrator",
    description="Orchestrate 7-email Christmas campaign nurture sequence",
    retries=1,
    retry_delay_seconds=300
)
async def email_sequence_orchestrator(
    email: str,
    red_systems: int = 0,
    orange_systems: int = 0,
    yellow_systems: int = 0,
    green_systems: int = 0,
    assessment_score: int = 50,
    first_name: str = "there",
    business_name: str = "your business"
) -> dict:
    """
    Orchestrate the complete 7-email Christmas campaign nurture sequence.

    This flow is triggered when a contact completes the BusOS assessment.
    It schedules all 7 emails with calculated delays based on the email timing:
    - Email 1: Immediate (0 hours)
    - Email 2: Day 2 (+48 hours)
    - Email 3: Day 3 (+24 hours = 72 hours total)
    - Email 4: Day 4 (+24 hours = 96 hours total)
    - Email 5: Day 6 (+48 hours = 144 hours total)
    - Email 6: Day 8 (+48 hours = 192 hours total)
    - Email 7: Day 10 (+48 hours = 240 hours total)

    In testing mode (TESTING_MODE=true), delays are in minutes instead of hours:
    - Email 1: Immediate (0 min)
    - Email 2: +2 min
    - Email 3: +3 min (5 min total)
    - Email 4: +4 min (9 min total)
    - Email 5: +5 min (14 min total)
    - Email 6: +6 min (20 min total)
    - Email 7: +7 min (27 min total)

    Args:
        email: Contact email address
        red_systems: Number of red (broken) systems
        orange_systems: Number of orange (struggling) systems
        yellow_systems: Number of yellow (functional) systems
        green_systems: Number of green (optimized) systems
        assessment_score: Overall BusOS score (0-100)
        first_name: Contact first name
        business_name: Business name

    Returns:
        Dict with status, segment, scheduled_flow_ids

    Example:
        result = await email_sequence_orchestrator(
            email="john@testcorp.com",
            red_systems=2,
            orange_systems=3,
            yellow_systems=2,
            green_systems=1,
            assessment_score=35,
            first_name="John",
            business_name="Test Corp"
        )
    """
    logger = get_run_logger()
    logger.info(f"🚀 Starting email sequence orchestration for {email}")

    # Get testing mode from environment
    testing_mode = os.getenv("TESTING_MODE", "false").lower() == "true"
    logger.info(f"📋 Testing mode: {testing_mode}")

    try:
        # Step 1: Validate assessment data
        logger.info("✅ Validating assessment data")
        assessment = AssessmentData(
            email=email,
            red_systems=red_systems,
            orange_systems=orange_systems,
            yellow_systems=yellow_systems,
            green_systems=green_systems,
            assessment_score=assessment_score,
            first_name=first_name,
            business_name=business_name
        )

        # Step 2: Classify segment
        logger.info("🎯 Classifying contact segment")
        segment = classify_segment(
            red_systems=red_systems,
            orange_systems=orange_systems,
            yellow_systems=yellow_systems,
            green_systems=green_systems
        )
        logger.info(f"✅ Segment: {segment}")

        # Step 3: Find contact in Notion
        logger.info(f"📋 Searching for contact: {email}")
        contact = search_contact_by_email(email)

        if not contact:
            logger.error(f"❌ Contact not found: {email}")
            return {
                "status": "failed",
                "error": "Contact not found",
                "email": email
            }

        page_id = contact["id"]
        logger.info(f"✅ Contact found: {page_id}")

        # Step 4: Update Notion with assessment data
        logger.info("📝 Updating Notion with assessment data")
        update_assessment_data(
            page_id=page_id,
            assessment_score=assessment_score,
            red_systems=red_systems,
            orange_systems=orange_systems,
            yellow_systems=yellow_systems,
            green_systems=green_systems,
            segment=segment
        )

        # Step 5: Update contact phase
        logger.info("📝 Updating contact phase to 'Phase 1 Assessment'")
        update_contact_phase(page_id, "Phase 1 Assessment")

        # Step 6: Send Discord alert for CRITICAL segments
        if should_send_discord_alert(segment):
            logger.info("🚨 CRITICAL segment detected - sending Discord alert")
            # TODO: Implement Discord webhook in Wave 3
            # send_discord_alert(email, first_name, business_name, assessment_score, segment)

        # Step 7: Schedule all 7 email flows with calculated delays
        logger.info("📅 Scheduling all 7 email flows with calculated delays")

        contact_data = {
            "email": email,
            "first_name": first_name,
            "business_name": business_name,
            "segment": segment,
            "assessment_score": assessment_score
        }

        scheduled_flows = []

        for email_number in range(1, 8):  # Emails 1-7
            delay = calculate_delay_hours(email_number, testing_mode)

            logger.info(
                f"📧 Scheduling Email #{email_number} "
                f"({delay} {'minutes' if testing_mode else 'hours'} from now)"
            )

            flow_run_id = await schedule_email_flow(
                flow_name=f"christmas-email-{email_number}",
                email_number=email_number,
                contact_data=contact_data,
                delay_hours=delay,
                testing_mode=testing_mode
            )

            scheduled_flows.append({
                "email_number": email_number,
                "flow_run_id": flow_run_id,
                "delay": delay,
                "delay_unit": "minutes" if testing_mode else "hours"
            })

            logger.info(f"✅ Email #{email_number} scheduled: {flow_run_id}")

        # Step 8: Return success
        logger.info(f"🎉 Successfully scheduled all 7 emails for {email}")

        return {
            "status": "success",
            "email": email,
            "segment": segment,
            "assessment_score": assessment_score,
            "testing_mode": testing_mode,
            "scheduled_flows": scheduled_flows,
            "total_duration_hours": calculate_delay_hours(7, testing_mode),
            "orchestrated_at": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ Error orchestrating email sequence for {email}: {e}")
        return {
            "status": "failed",
            "email": email,
            "error": str(e),
            "failed_at": datetime.now().isoformat()
        }


# ==============================================================================
# Synchronous Wrapper for FastAPI
# ==============================================================================

def email_sequence_orchestrator_sync(
    email: str,
    red_systems: int = 0,
    orange_systems: int = 0,
    yellow_systems: int = 0,
    green_systems: int = 0,
    assessment_score: int = 50,
    first_name: str = "there",
    business_name: str = "your business"
) -> dict:
    """
    Synchronous wrapper for email_sequence_orchestrator.

    Use this when calling from FastAPI webhook handlers or other sync code.

    Example:
        # In FastAPI webhook handler
        result = email_sequence_orchestrator_sync(
            email="john@testcorp.com",
            red_systems=2,
            orange_systems=3,
            assessment_score=35,
            first_name="John",
            business_name="Test Corp"
        )
    """
    import asyncio
    return asyncio.run(email_sequence_orchestrator(
        email=email,
        red_systems=red_systems,
        orange_systems=orange_systems,
        yellow_systems=yellow_systems,
        green_systems=green_systems,
        assessment_score=assessment_score,
        first_name=first_name,
        business_name=business_name
    ))


# ==============================================================================
# Testing Entry Point
# ==============================================================================

if __name__ == "__main__":
    import asyncio

    # Test orchestrator locally
    result = asyncio.run(email_sequence_orchestrator(
        email="test@example.com",
        red_systems=2,
        orange_systems=3,
        yellow_systems=2,
        green_systems=1,
        assessment_score=35,
        first_name="Test",
        business_name="Test Corp"
    ))
    print(f"\n✅ Test result: {result}")
