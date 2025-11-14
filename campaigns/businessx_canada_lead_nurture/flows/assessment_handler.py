"""
Assessment Handler Flow - Process completed BusOS assessments and trigger email sequence.

This flow:
1. Updates contact with assessment results (red/orange/yellow/green systems)
2. Determines customer segment (CRITICAL/URGENT/OPTIMIZE)
3. Triggers the 5-email nurture sequence

Webhook payload expected:
{
    "email": "john@example.com",
    "red_systems": 2,
    "orange_systems": 1,
    "yellow_systems": 2,
    "green_systems": 3,
    "assessment_score": 65,
    "assessment_date": "2025-11-12T10:30:00Z"
}
"""

from prefect import flow
from datetime import datetime
from typing import Dict, Any, Optional

# Import our task modules
from campaigns.businessx_canada_lead_nurture.tasks.notion_operations import search_contact_by_email, update_contact, get_contact
from campaigns.businessx_canada_lead_nurture.tasks.routing import determine_segment

# Import email sequence flow
from campaigns.businessx_canada_lead_nurture.flows.email_sequence import email_sequence_flow


@flow(name="assessment-handler", log_prints=True)
def assessment_handler_flow(
    email: str,
    red_systems: int,
    orange_systems: int,
    yellow_systems: int = 0,
    green_systems: int = 0,
    assessment_score: Optional[int] = None,
    assessment_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Handle completed BusOS assessment and trigger email sequence.

    Args:
        email: Contact's email address
        red_systems: Number of red (broken) systems
        orange_systems: Number of orange (warning) systems
        yellow_systems: Number of yellow systems
        green_systems: Number of green (healthy) systems
        assessment_score: Overall assessment score (0-100)
        assessment_date: ISO timestamp of assessment completion

    Returns:
        Dictionary with assessment results and email sequence status

    Example:
        result = assessment_handler_flow(
            email="john@example.com",
            red_systems=2,
            orange_systems=1,
            yellow_systems=2,
            green_systems=3,
            assessment_score=65
        )
    """
    print(f"📊 Processing assessment for: {email}")
    print(f"   Systems: {red_systems} red, {orange_systems} orange, {yellow_systems} yellow, {green_systems} green")

    # Find contact in Notion
    contact = search_contact_by_email(email)

    if not contact:
        print(f"   ❌ Contact not found for {email}")
        return {
            "status": "error",
            "message": f"Contact not found for {email}. Please ensure signup was completed first."
        }

    page_id = contact["id"]
    print(f"   ✅ Found contact (page_id: {page_id})")

    # Determine segment
    segment = determine_segment(
        red_systems=red_systems,
        orange_systems=orange_systems,
        yellow_systems=yellow_systems,
        green_systems=green_systems
    )
    print(f"   📍 Classified as: {segment}")

    # Prepare Notion properties update
    assessment_properties = {
        "Assessment Completed": {"checkbox": True},
        "Assessment Date": {
            "date": {"start": assessment_date or datetime.now().isoformat()}
        },
        "Red Systems": {"number": red_systems},
        "Orange Systems": {"number": orange_systems},
        "Yellow Systems": {"number": yellow_systems},
        "Green Systems": {"number": green_systems},
        "Segment": {"select": {"name": segment}}
    }

    if assessment_score is not None:
        assessment_properties["Assessment Score"] = {"number": assessment_score}

    # Update contact with assessment results
    print(f"   Updating contact with assessment results...")
    update_contact(page_id=page_id, properties=assessment_properties)
    print(f"   ✅ Assessment results saved to Notion")

    # Get complete contact info for email personalization
    contact_full = get_contact(page_id)
    properties = contact_full["properties"]

    # Extract contact details
    first_name_prop = properties.get("First Name", {}).get("rich_text", [])
    first_name = first_name_prop[0]["plain_text"] if first_name_prop else "there"

    business_name_prop = properties.get("Business Name", {}).get("rich_text", [])
    business_name = business_name_prop[0]["plain_text"] if business_name_prop else "your business"

    print(f"   Starting email sequence for {first_name} ({segment})...")

    # Trigger email sequence flow
    try:
        email_result = email_sequence_flow(
            contact_page_id=page_id,
            email=email,
            first_name=first_name,
            business_name=business_name,
            red_systems=red_systems,
            orange_systems=orange_systems,
            yellow_systems=yellow_systems,
            green_systems=green_systems
        )

        print(f"   🎉 Email sequence triggered successfully")

        return {
            "status": "success",
            "page_id": page_id,
            "email": email,
            "segment": segment,
            "email_sequence_status": email_result["status"],
            "message": f"Assessment processed and email sequence started for {segment} segment"
        }

    except Exception as e:
        print(f"   ❌ Error triggering email sequence: {e}")

        # Update Notion with error
        update_contact(
            page_id=page_id,
            properties={
                "Email Sequence Error": {
                    "rich_text": [{"text": {"content": str(e)}}]
                }
            }
        )

        return {
            "status": "error",
            "page_id": page_id,
            "email": email,
            "segment": segment,
            "message": f"Assessment processed but email sequence failed: {e}"
        }


if __name__ == "__main__":
    # Example usage for testing
    print("Testing assessment handler flow...")

    result = assessment_handler_flow(
        email="test@example.com",
        red_systems=2,
        orange_systems=1,
        yellow_systems=2,
        green_systems=3,
        assessment_score=65
    )

    print(f"\n✅ Test complete: {result}")
