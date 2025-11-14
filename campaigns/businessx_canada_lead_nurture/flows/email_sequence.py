"""
BusOS Email Nurture Sequence - 5-email campaign with segment-based routing.

This flow orchestrates the complete email sequence:
1. Email #1: Assessment invitation (universal) - Wait 24h
2. Email #2: Results (CRITICAL/URGENT/OPTIMIZE) - Wait 48h
3. Email #3: BusOS Framework (universal) - Wait 48h
4. Email #4: Christmas Special (universal) - Wait 48h
5. Email #5: Final push (CRITICAL/URGENT/OPTIMIZE)

Wait times controlled by TESTING_MODE env var:
- Production: 24h, 48h, 48h, 48h between emails
- Testing: 1min, 2min, 3min, 4min between emails
"""

from prefect import flow, task
from prefect.tasks import task_input_hash
from datetime import timedelta
import os
from typing import Dict, Any, Optional

# Import our task modules
from campaigns.businessx_canada_lead_nurture.tasks.notion_operations import get_contact, update_contact
from campaigns.businessx_canada_lead_nurture.tasks.resend_operations import send_template_email
from campaigns.businessx_canada_lead_nurture.tasks.routing import determine_segment, select_email_template, get_wait_duration
from campaigns.businessx_canada_lead_nurture.tasks.template_operations import get_template

# Environment configuration
TESTING_MODE = os.getenv("TESTING_MODE", "false").lower() == "true"


@flow(name="email-sequence-5-emails", log_prints=True)
def email_sequence_flow(
    contact_page_id: str,
    email: str,
    first_name: str,
    business_name: str,
    red_systems: int,
    orange_systems: int,
    yellow_systems: int = 0,
    green_systems: int = 0
) -> Dict[str, Any]:
    """
    Execute complete 5-email nurture sequence with segment-based routing.

    Args:
        contact_page_id: Notion contact page ID (for context restoration after waits)
        email: Recipient email address
        first_name: Contact's first name
        business_name: Contact's business name
        red_systems: Number of red (broken) systems
        orange_systems: Number of orange (warning) systems
        yellow_systems: Number of yellow systems
        green_systems: Number of green (healthy) systems

    Returns:
        Dictionary with execution summary and email IDs

    Example:
        result = email_sequence_flow(
            contact_page_id="page-123",
            email="john@example.com",
            first_name="John",
            business_name="John's Salon",
            red_systems=2,
            orange_systems=1
        )
    """
    print(f"🚀 Starting email sequence for {first_name} ({email})")
    print(f"   Segment: {red_systems} red, {orange_systems} orange, {yellow_systems} yellow, {green_systems} green")
    print(f"   Testing mode: {TESTING_MODE}")

    # Determine customer segment
    segment = determine_segment(
        red_systems=red_systems,
        orange_systems=orange_systems,
        yellow_systems=yellow_systems,
        green_systems=green_systems
    )
    print(f"   Classified as: {segment}")

    # Track sent emails
    sent_emails = {}

    # Template variables for substitution
    template_vars = {
        "first_name": first_name,
        "business_name": business_name,
        "email": email
    }

    # ===== EMAIL #1: Assessment Invitation (Universal) =====
    print("\n📧 Sending Email #1: Assessment Invitation")
    template_name_1 = select_email_template(email_number=1, segment=segment)
    template_1 = get_template(template_name_1, use_notion=True)

    email_result_1 = send_template_email(
        to_email=email,
        template=template_1,
        variables=template_vars
    )
    sent_emails["email_1"] = email_result_1
    print(f"   ✅ Sent email_1 (ID: {email_result_1.get('id', 'N/A')})")

    # Update Notion: Mark Email #1 sent
    update_contact(
        page_id=contact_page_id,
        properties={
            "Email 1 Sent": {"checkbox": True},
            "Email 1 Sent Date": {"date": {"start": email_result_1.get("created_at", "")}}
        }
    )

    # Wait after Email #1
    wait_duration_1 = get_wait_duration(email_number=1, testing_mode=TESTING_MODE)
    print(f"⏳ Waiting {wait_duration_1} seconds before Email #2...")
    from time import sleep
    sleep(wait_duration_1)

    # ===== EMAIL #2: Results (Segment-Specific) =====
    print("\n📧 Sending Email #2: Results")
    template_name_2 = select_email_template(email_number=2, segment=segment)
    template_2 = get_template(template_name_2, use_notion=True)
    print(f"   Using template: {template_name_2} for segment {segment}")

    email_result_2 = send_template_email(
        to_email=email,
        template=template_2,
        variables=template_vars
    )
    sent_emails["email_2"] = email_result_2
    print(f"   ✅ Sent {template_name_2} (ID: {email_result_2.get('id', 'N/A')})")

    # Update Notion: Mark Email #2 sent
    update_contact(
        page_id=contact_page_id,
        properties={
            "Email 2 Sent": {"checkbox": True},
            "Email 2 Sent Date": {"date": {"start": email_result_2.get("created_at", "")}}
        }
    )

    # Wait after Email #2
    wait_duration_2 = get_wait_duration(email_number=2, testing_mode=TESTING_MODE)
    print(f"⏳ Waiting {wait_duration_2} seconds before Email #3...")
    sleep(wait_duration_2)

    # ===== EMAIL #3: BusOS Framework (Universal) =====
    print("\n📧 Sending Email #3: BusOS Framework")
    template_name_3 = select_email_template(email_number=3, segment=segment)
    template_3 = get_template(template_name_3, use_notion=True)

    email_result_3 = send_template_email(
        to_email=email,
        template=template_3,
        variables=template_vars
    )
    sent_emails["email_3"] = email_result_3
    print(f"   ✅ Sent email_3 (ID: {email_result_3.get('id', 'N/A')})")

    # Update Notion: Mark Email #3 sent
    update_contact(
        page_id=contact_page_id,
        properties={
            "Email 3 Sent": {"checkbox": True},
            "Email 3 Sent Date": {"date": {"start": email_result_3.get("created_at", "")}}
        }
    )

    # Wait after Email #3
    wait_duration_3 = get_wait_duration(email_number=3, testing_mode=TESTING_MODE)
    print(f"⏳ Waiting {wait_duration_3} seconds before Email #4...")
    sleep(wait_duration_3)

    # ===== EMAIL #4: Christmas Special (Universal) =====
    print("\n📧 Sending Email #4: Christmas Special")
    template_name_4 = select_email_template(email_number=4, segment=segment)
    template_4 = get_template(template_name_4, use_notion=True)

    email_result_4 = send_template_email(
        to_email=email,
        template=template_4,
        variables=template_vars
    )
    sent_emails["email_4"] = email_result_4
    print(f"   ✅ Sent email_4 (ID: {email_result_4.get('id', 'N/A')})")

    # Update Notion: Mark Email #4 sent
    update_contact(
        page_id=contact_page_id,
        properties={
            "Email 4 Sent": {"checkbox": True},
            "Email 4 Sent Date": {"date": {"start": email_result_4.get("created_at", "")}}
        }
    )

    # Wait after Email #4
    wait_duration_4 = get_wait_duration(email_number=4, testing_mode=TESTING_MODE)
    print(f"⏳ Waiting {wait_duration_4} seconds before Email #5...")
    sleep(wait_duration_4)

    # ===== EMAIL #5: Final Push (Segment-Specific) =====
    print("\n📧 Sending Email #5: Final Push")
    template_name_5 = select_email_template(email_number=5, segment=segment)
    template_5 = get_template(template_name_5, use_notion=True)
    print(f"   Using template: {template_name_5} for segment {segment}")

    email_result_5 = send_template_email(
        to_email=email,
        template=template_5,
        variables=template_vars
    )
    sent_emails["email_5"] = email_result_5
    print(f"   ✅ Sent {template_name_5} (ID: {email_result_5.get('id', 'N/A')})")

    # Update Notion: Mark Email #5 sent and sequence complete
    update_contact(
        page_id=contact_page_id,
        properties={
            "Email 5 Sent": {"checkbox": True},
            "Email 5 Sent Date": {"date": {"start": email_result_5.get("created_at", "")}},
            "Sequence Complete": {"checkbox": True}
        }
    )

    print(f"\n🎉 Email sequence complete for {first_name} ({segment})")

    return {
        "status": "complete",
        "segment": segment,
        "emails_sent": sent_emails,
        "contact_page_id": contact_page_id
    }


if __name__ == "__main__":
    # Example usage for testing
    print("Testing email sequence flow...")

    # Test with CRITICAL segment
    result = email_sequence_flow(
        contact_page_id="test-page-123",
        email="test@example.com",
        first_name="John",
        business_name="John's Salon",
        red_systems=2,
        orange_systems=1,
        yellow_systems=0,
        green_systems=5
    )

    print(f"\n✅ Test complete: {result}")
