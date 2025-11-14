"""
Signup Handler Flow - Process new user signups from webhook.

This flow handles new contact creation and triggers the email sequence
once the user completes their BusOS assessment.

Webhook payload expected:
{
    "email": "john@example.com",
    "name": "John Doe",
    "first_name": "John",
    "business_name": "John's Salon",
    "signup_source": "web_form"
}
"""

from prefect import flow
from datetime import datetime
from typing import Dict, Any, Optional

# Import our task modules
from campaigns.businessx_canada_lead_nurture.tasks.notion_operations import search_contact_by_email, create_contact, update_contact


@flow(name="signup-handler", log_prints=True)
def signup_handler_flow(
    email: str,
    name: str,
    first_name: str,
    business_name: str = "your business",
    signup_source: str = "web_form"
) -> Dict[str, Any]:
    """
    Handle new user signup and create contact in Notion.

    Args:
        email: Contact's email address (unique identifier)
        name: Full name
        first_name: First name for personalization
        business_name: Business name for email personalization
        signup_source: Where the signup came from (web_form, landing_page, etc.)

    Returns:
        Dictionary with contact page_id and status

    Example:
        result = signup_handler_flow(
            email="john@example.com",
            name="John Doe",
            first_name="John",
            business_name="John's Salon",
            signup_source="web_form"
        )
    """
    print(f"🆕 Processing signup for: {email}")
    print(f"   Name: {name}, Business: {business_name}")

    # Check if contact already exists
    existing_contact = search_contact_by_email(email)

    if existing_contact:
        page_id = existing_contact["id"]
        print(f"   ⚠️  Contact already exists (page_id: {page_id})")

        # Update existing contact with new signup info
        update_contact(
            page_id=page_id,
            properties={
                "Last Signup Date": {
                    "date": {"start": datetime.now().isoformat()}
                },
                "Signup Source": {
                    "select": {"name": signup_source}
                }
            }
        )
        print(f"   ✅ Updated existing contact")

        return {
            "status": "existing",
            "page_id": page_id,
            "email": email,
            "message": "Contact already exists, updated signup info"
        }

    # Create new contact
    print(f"   Creating new contact in Notion...")
    page_id = create_contact(
        email=email,
        name=name,
        first_name=first_name,
        business_name=business_name,
        signup_source=signup_source
    )

    print(f"   ✅ Created new contact (page_id: {page_id})")
    print(f"   ℹ️  Waiting for assessment completion to trigger email sequence...")

    return {
        "status": "created",
        "page_id": page_id,
        "email": email,
        "message": "New contact created, awaiting assessment completion"
    }


if __name__ == "__main__":
    # Example usage for testing
    print("Testing signup handler flow...")

    result = signup_handler_flow(
        email="test@example.com",
        name="Test User",
        first_name="Test",
        business_name="Test Business",
        signup_source="web_form"
    )

    print(f"\n✅ Test complete: {result}")
