"""
Notion database operations for BusOS Email Sequence.

This module provides Prefect tasks for interacting with Notion databases:
- Search for contacts by email
- Create new contacts
- Update existing contacts

All tasks include retry logic for API failures.
"""

from prefect import task
from notion_client import Client
from datetime import datetime
import os
from typing import Optional, Dict, Any

# Load environment variables
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_CONTACTS_DB_ID = os.getenv("NOTION_CONTACTS_DB_ID")

# Initialize Notion client
notion = Client(auth=NOTION_TOKEN)


@task(retries=3, retry_delay_seconds=60, name="notion-search-contact")
def search_contact_by_email(email: str) -> Optional[Dict[str, Any]]:
    """
    Search for existing contact in Notion database by email.

    Uses Notion query endpoint (not search) for better performance.

    Args:
        email: Contact email address to search for

    Returns:
        Contact page object if found, None if not found

    Example:
        contact = search_contact_by_email("test@example.com")
        if contact:
            page_id = contact["id"]
    """
    try:
        response = notion.databases.query(
            database_id=NOTION_CONTACTS_DB_ID,
            filter={
                "property": "Email",
                "email": {
                    "equals": email
                }
            }
        )

        if response["results"]:
            return response["results"][0]
        return None

    except Exception as e:
        print(f"Error searching for contact {email}: {e}")
        raise


@task(retries=3, retry_delay_seconds=60, name="notion-create-contact")
def create_contact(
    email: str,
    name: str,
    first_name: str,
    business_name: str = "your salon",
    signup_source: str = "web_form"
) -> str:
    """
    Create new contact in Notion database.

    Args:
        email: Contact email address (primary key)
        name: Full name
        first_name: First name for email personalization
        business_name: Business name (default: "your salon")
        signup_source: Source of signup (default: "web_form")

    Returns:
        Notion page ID of created contact

    Example:
        page_id = create_contact(
            email="test@example.com",
            name="Test User",
            first_name="Test",
            business_name="Test Salon"
        )
    """
    try:
        properties = {
            "Email": {"email": email},
            "Name": {"rich_text": [{"text": {"content": name}}]},
            "First Name": {"rich_text": [{"text": {"content": first_name}}]},
            "Business Name": {"rich_text": [{"text": {"content": business_name}}]},
            "Signup Date": {"date": {"start": datetime.now().isoformat()}},
            "Signup Source": {"select": {"name": signup_source}}
        }

        response = notion.pages.create(
            parent={"database_id": NOTION_CONTACTS_DB_ID},
            properties=properties
        )

        print(f"✅ Created contact: {email} (page_id: {response['id']})")
        return response["id"]

    except Exception as e:
        print(f"Error creating contact {email}: {e}")
        raise


@task(retries=3, retry_delay_seconds=60, name="notion-update-contact")
def update_contact(page_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update existing contact in Notion database.

    Args:
        page_id: Notion page ID of contact to update
        properties: Dictionary of properties to update (Notion API format)

    Returns:
        Updated page object

    Example:
        # Mark Email #1 sent
        update_contact(page_id, {
            "Email 1 Sent": {"date": {"start": datetime.now().isoformat()}}
        })

        # Update assessment results
        update_contact(page_id, {
            "Assessment Completed": {"checkbox": True},
            "Segment": {"select": {"name": "CRITICAL"}},
            "Assessment Score": {"number": 65}
        })
    """
    try:
        response = notion.pages.update(
            page_id=page_id,
            properties=properties
        )

        print(f"✅ Updated contact: {page_id}")
        return response

    except Exception as e:
        print(f"Error updating contact {page_id}: {e}")
        raise


@task(retries=3, retry_delay_seconds=60, name="notion-get-contact")
def get_contact(page_id: str) -> Dict[str, Any]:
    """
    Retrieve contact by page ID (for context restoration after waits).

    Args:
        page_id: Notion page ID of contact

    Returns:
        Contact page object with all properties

    Example:
        contact = get_contact(page_id)
        first_name = contact["properties"]["First Name"]["rich_text"][0]["text"]["content"]
    """
    try:
        response = notion.pages.retrieve(page_id=page_id)
        return response

    except Exception as e:
        print(f"Error retrieving contact {page_id}: {e}")
        raise
