"""
Notion database operations for Christmas Campaign.

This module provides Prefect tasks for interacting with Notion databases:
- Search for contacts by email (BusinessX Canada database)
- Update contact assessment and segment data
- Track email sends and flow runs
- Fetch email templates
- Create customer portal pages

All tasks include retry logic for API failures.

Author: Christmas Campaign Team
Created: 2025-11-16
"""

from prefect import task
from prefect.blocks.system import Secret
from notion_client import Client
from datetime import datetime
import os
from typing import Optional, Dict, Any, Literal
from dotenv import load_dotenv

# Load environment variables (fallback for local development)
load_dotenv()

# Notion credentials and database IDs
# Load ALL from Prefect Secret blocks (fallback to environment variables for local dev)
try:
    NOTION_TOKEN = Secret.load("notion-token").get()
    NOTION_EMAIL_TEMPLATES_DB_ID = Secret.load("notion-email-templates-db-id").get()
    NOTION_EMAIL_SEQUENCE_DB_ID = Secret.load("notion-email-sequence-db-id").get()
    NOTION_BUSINESSX_DB_ID = Secret.load("notion-businessx-db-id").get()
    NOTION_CUSTOMER_PROJECTS_DB_ID = Secret.load("notion-customer-projects-db-id").get()
    NOTION_EMAIL_ANALYTICS_DB_ID = Secret.load("notion-email-analytics-db-id").get()
    print("✅ Loaded all Notion configuration from Prefect Secret blocks")
except Exception as e:
    print(f"⚠️  Failed to load from Secret blocks, using environment variables: {e}")
    NOTION_TOKEN = os.getenv("NOTION_TOKEN")
    NOTION_EMAIL_TEMPLATES_DB_ID = os.getenv("NOTION_EMAIL_TEMPLATES_DB_ID")
    NOTION_EMAIL_SEQUENCE_DB_ID = os.getenv("NOTION_EMAIL_SEQUENCE_DB_ID")
    NOTION_BUSINESSX_DB_ID = os.getenv("NOTION_BUSINESSX_DB_ID")
    NOTION_CUSTOMER_PROJECTS_DB_ID = os.getenv("NOTION_CUSTOMER_PROJECTS_DB_ID")
    NOTION_EMAIL_ANALYTICS_DB_ID = os.getenv("NOTION_EMAIL_ANALYTICS_DB_ID")

# Initialize Notion client
notion = Client(auth=NOTION_TOKEN)


# ==============================================================================
# Contact Operations
# ==============================================================================

@task(retries=3, retry_delay_seconds=60, name="christmas-search-contact")
def search_contact_by_email(email: str) -> Optional[Dict[str, Any]]:
    """
    Search for existing contact in BusinessX Canada database by email.

    Args:
        email: Contact email address to search for

    Returns:
        Contact page object if found, None if not found

    Example:
        contact = search_contact_by_email("john@testcorp.com")
        if contact:
            page_id = contact["id"]
            segment = contact["properties"]["Segment"]["select"]["name"]
    """
    try:
        response = notion.databases.query(
            database_id=NOTION_BUSINESSX_DB_ID,
            filter={
                "property": "email",
                "email": {
                    "equals": email
                }
            }
        )

        if response["results"]:
            return response["results"][0]
        return None

    except Exception as e:
        print(f"❌ Error searching for contact {email}: {e}")
        raise


@task(retries=3, retry_delay_seconds=60, name="christmas-update-assessment")
def update_assessment_data(
    page_id: str,
    assessment_score: int,
    red_systems: int = 0,
    orange_systems: int = 0,
    yellow_systems: int = 0,
    green_systems: int = 0,
    segment: Literal["CRITICAL", "URGENT", "OPTIMIZE"] = "OPTIMIZE"
) -> Dict[str, Any]:
    """
    Update contact with assessment results and segment classification.

    Args:
        page_id: Notion page ID of contact
        assessment_score: Overall BusOS score (0-100)
        red_systems: Number of red (broken) systems
        orange_systems: Number of orange (struggling) systems
        yellow_systems: Number of yellow (functional) systems
        green_systems: Number of green (optimized) systems
        segment: Classified segment (CRITICAL/URGENT/OPTIMIZE)

    Returns:
        Updated page object

    Example:
        update_assessment_data(
            page_id="abc123",
            assessment_score=35,
            red_systems=2,
            orange_systems=3,
            yellow_systems=2,
            green_systems=1,
            segment="URGENT"
        )
    """
    try:
        properties = {
            "Assessment Score": {"number": assessment_score},
            "Segment": {"select": {"name": segment}},
            "Christmas Campaign Status": {"select": {"name": "Nurture Sequence"}},
            # Store system breakdown (if we have these fields - optional)
            # "Red Systems": {"number": red_systems},
            # "Orange Systems": {"number": orange_systems},
            # "Yellow Systems": {"number": yellow_systems},
            # "Green Systems": {"number": green_systems}
        }

        response = notion.pages.update(
            page_id=page_id,
            properties=properties
        )

        print(f"✅ Updated assessment for contact {page_id}: {segment} segment, score {assessment_score}")
        return response

    except Exception as e:
        print(f"❌ Error updating assessment for {page_id}: {e}")
        raise


@task(retries=3, retry_delay_seconds=60, name="christmas-track-email-sent")
def track_email_sent(
    page_id: str,
    email_number: int,
    flow_run_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Mark email as sent and record timestamp in contact record.

    Args:
        page_id: Notion page ID of contact
        email_number: Email number in sequence (1-7)
        flow_run_id: Prefect flow run ID (optional, for debugging)

    Returns:
        Updated page object

    Example:
        track_email_sent(page_id="abc123", email_number=1)
        track_email_sent(page_id="abc123", email_number=2, flow_run_id="flow-123")
    """
    try:
        properties = {
            f"Christmas Email {email_number} Sent": {"checkbox": True},
            f"Christmas Email {email_number} Date": {"date": {"start": datetime.now().isoformat()}}
        }

        response = notion.pages.update(
            page_id=page_id,
            properties=properties
        )

        print(f"✅ Tracked email #{email_number} sent for contact {page_id}")
        return response

    except Exception as e:
        print(f"❌ Error tracking email #{email_number} for {page_id}: {e}")
        raise


@task(retries=3, retry_delay_seconds=60, name="christmas-update-phase")
def update_contact_phase(
    page_id: str,
    phase: Literal[
        "Phase 1 Assessment",
        "Phase 1 Diagnostic",
        "Phase 2A Done-For-You",
        "Phase 2B Coaching",
        "Phase 2C DIY"
    ]
) -> Dict[str, Any]:
    """
    Update contact's current phase in the customer journey.

    Args:
        page_id: Notion page ID of contact
        phase: New phase value

    Returns:
        Updated page object

    Example:
        # After assessment completion
        update_contact_phase(page_id, "Phase 1 Assessment")

        # After booking diagnostic call
        update_contact_phase(page_id, "Phase 1 Diagnostic")

        # After choosing Phase 2 option
        update_contact_phase(page_id, "Phase 2A Done-For-You")
    """
    try:
        properties = {
            "Phase": {"select": {"name": phase}}
        }

        response = notion.pages.update(
            page_id=page_id,
            properties=properties
        )

        print(f"✅ Updated phase for contact {page_id}: {phase}")
        return response

    except Exception as e:
        print(f"❌ Error updating phase for {page_id}: {e}")
        raise


@task(retries=3, retry_delay_seconds=60, name="christmas-update-booking-status")
def update_booking_status(
    page_id: str,
    status: Literal["Not Booked", "Booked", "Completed", "No-Show"],
    call_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update contact's diagnostic call booking status.

    Args:
        page_id: Notion page ID of contact
        status: Booking status
        call_date: Diagnostic call date (YYYY-MM-DD format, optional)

    Returns:
        Updated page object

    Example:
        # After booking
        update_booking_status(page_id, "Booked", call_date="2025-11-20")

        # After call completion
        update_booking_status(page_id, "Completed")
    """
    try:
        properties = {
            "Booking Status": {"select": {"name": status}},
            "Christmas Campaign Status": {"select": {"name": "Pre-Call Prep"}}
        }

        if call_date:
            properties["Diagnostic Call Date"] = {"date": {"start": call_date}}

        response = notion.pages.update(
            page_id=page_id,
            properties=properties
        )

        print(f"✅ Updated booking status for contact {page_id}: {status}")
        return response

    except Exception as e:
        print(f"❌ Error updating booking status for {page_id}: {e}")
        raise


# ==============================================================================
# Email Sequence Tracking Operations
# ==============================================================================

@task(retries=3, retry_delay_seconds=60, name="christmas-search-email-sequence")
def search_email_sequence_by_email(email: str) -> Optional[Dict[str, Any]]:
    """
    Search for existing email sequence record in Email Sequence database by email.

    This function checks if the contact is already in the email nurture sequence,
    which is critical for:
    - Idempotency: Prevent duplicate sequence starts
    - State portability: Track which emails have been sent across server switches
    - Resume capability: Continue sequence after interruptions

    Args:
        email: Contact email address to search for

    Returns:
        Email sequence record if found, None if not found

    Example:
        sequence = search_email_sequence_by_email("sarah@example.com")
        if sequence:
            sequence_id = sequence["id"]
            email_1_sent = sequence["properties"]["Email 1 Sent"]["date"]
            campaign = sequence["properties"]["Campaign"]["select"]["name"]
    """
    try:
        response = notion.databases.query(
            database_id=NOTION_EMAIL_SEQUENCE_DB_ID,
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
        print(f"❌ Error searching email sequence for {email}: {e}")
        raise


@task(retries=3, retry_delay_seconds=60, name="christmas-create-email-sequence")
def create_email_sequence(
    email: str,
    first_name: str,
    business_name: str,
    assessment_score: int,
    red_systems: int = 0,
    orange_systems: int = 0,
    yellow_systems: int = 0,
    green_systems: int = 0,
    segment: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create new email sequence tracking record in Email Sequence database.

    This function creates the master record for tracking all email sends
    for this contact in the Christmas campaign.

    Args:
        email: Contact email address
        first_name: Contact first name
        business_name: Business name
        assessment_score: Overall BusOS score (0-100)
        red_systems: Number of red (broken) systems
        orange_systems: Number of orange (struggling) systems
        yellow_systems: Number of yellow (functional) systems
        green_systems: Number of green (optimized) systems
        segment: Classified segment (CRITICAL/URGENT/OPTIMIZE)

    Returns:
        Created email sequence record

    Example:
        sequence = create_email_sequence(
            email="sarah@example.com",
            first_name="Sarah",
            business_name="Sarah's Salon",
            assessment_score=52,
            red_systems=2,
            orange_systems=1,
            yellow_systems=2,
            green_systems=3,
            segment="URGENT"
        )
        sequence_id = sequence["id"]
    """
    try:
        properties = {
            "Email": {"email": email},
            "First Name": {"rich_text": [{"text": {"content": first_name}}]},
            "Business Name": {"rich_text": [{"text": {"content": business_name}}]},
            "Assessment Score": {"number": assessment_score},
            "Red Systems": {"number": red_systems},
            "Orange Systems": {"number": orange_systems},
            "Yellow Systems": {"number": yellow_systems},
            "Green Systems": {"number": green_systems},
            "Campaign": {"select": {"name": "Christmas 2025"}},
            "Signup Date": {"date": {"start": datetime.now().isoformat()}},
            "Sequence Completed": {"checkbox": False},
            "Assessment Completed": {"checkbox": True}
        }

        if segment:
            properties["Segment"] = {"select": {"name": segment}}

        response = notion.pages.create(
            parent={"database_id": NOTION_EMAIL_SEQUENCE_DB_ID},
            properties=properties
        )

        print(f"✅ Created email sequence record for {email} (Campaign: Christmas 2025)")
        return response

    except Exception as e:
        print(f"❌ Error creating email sequence for {email}: {e}")
        raise


@task(retries=3, retry_delay_seconds=60, name="christmas-update-email-sequence")
def update_email_sequence(
    sequence_id: str,
    email_number: Optional[int] = None,
    sequence_completed: Optional[bool] = None,
    **additional_properties
) -> Dict[str, Any]:
    """
    Update email sequence tracking record after sending an email.

    This function is called AFTER each email is successfully sent to update
    the "Email X Sent" timestamp field. This ensures state portability - if
    we switch servers, we know exactly which emails have been sent.

    Args:
        sequence_id: Notion page ID of email sequence record
        email_number: Email number just sent (1-7, optional)
        sequence_completed: Mark sequence as complete (optional)
        **additional_properties: Additional Notion properties to update

    Returns:
        Updated email sequence record

    Example:
        # After sending Email 1
        update_email_sequence(
            sequence_id="abc123",
            email_number=1
        )

        # After sending final email
        update_email_sequence(
            sequence_id="abc123",
            email_number=7,
            sequence_completed=True
        )

        # Custom update
        update_email_sequence(
            sequence_id="abc123",
            **{"Custom Field": {"rich_text": [{"text": {"content": "value"}}]}}
        )
    """
    try:
        properties = {}

        # Update email sent timestamp
        if email_number:
            properties[f"Email {email_number} Sent"] = {
                "date": {"start": datetime.now().isoformat()}
            }

        # Mark sequence completion
        if sequence_completed is not None:
            properties["Sequence Completed"] = {"checkbox": sequence_completed}

        # Add any additional properties
        properties.update(additional_properties)

        response = notion.pages.update(
            page_id=sequence_id,
            properties=properties
        )

        if email_number:
            print(f"✅ Updated email sequence {sequence_id}: Email {email_number} sent")
        else:
            print(f"✅ Updated email sequence {sequence_id}")

        return response

    except Exception as e:
        print(f"❌ Error updating email sequence {sequence_id}: {e}")
        raise


# ==============================================================================
# Email Template Operations
# ==============================================================================

@task(retries=3, retry_delay_seconds=60, name="christmas-fetch-template")
def fetch_email_template(template_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch email template from Notion Email Templates database.

    Args:
        template_id: Template identifier (e.g., "christmas_email_1", "christmas_email_2")

    Returns:
        Template data dict with 'subject' and 'html_body' keys, or None if not found

    Example:
        template = fetch_email_template("christmas_email_1")
        if template:
            subject = template["subject"]
            html_body = template["html_body"]
    """
    try:
        response = notion.databases.query(
            database_id=NOTION_EMAIL_TEMPLATES_DB_ID,
            filter={
                "property": "Template Name",
                "title": {
                    "equals": template_id
                }
            }
        )

        if not response["results"]:
            print(f"⚠️ Template {template_id} not found in Notion")
            return None

        page = response["results"][0]
        props = page["properties"]

        # Extract subject from "Subject Line" rich_text property
        subject_prop = props.get("Subject Line", {}).get("rich_text", [])
        subject = "".join([text["plain_text"] for text in subject_prop]) if subject_prop else ""

        # Extract HTML body from "Email Body HTML" rich_text property
        html_prop = props.get("Email Body HTML", {}).get("rich_text", [])
        html_body = "".join([text["plain_text"] for text in html_prop]) if html_prop else ""

        # Extract template data
        template_data = {
            "template_id": template_id,
            "subject": subject,
            "html_body": html_body
        }

        print(f"✅ Fetched template: {template_id}")
        return template_data

    except Exception as e:
        print(f"❌ Error fetching template {template_id}: {e}")
        raise


# ==============================================================================
# Customer Portal Operations
# ==============================================================================

@task(retries=3, retry_delay_seconds=60, name="christmas-create-portal")
def create_customer_portal(
    email: str,
    first_name: str,
    business_name: str,
    call_date: str,
    next_steps: str
) -> str:
    """
    Create customer portal page in Customer Projects database.

    This must complete in <60 seconds (Hormozi friction reduction standard).

    Args:
        email: Contact email
        first_name: Contact first name
        business_name: Business name
        call_date: Diagnostic call date (YYYY-MM-DD)
        next_steps: Recommended next phase

    Returns:
        Notion portal page URL

    Example:
        portal_url = create_customer_portal(
            email="john@testcorp.com",
            first_name="John",
            business_name="Test Corp",
            call_date="2025-11-20",
            next_steps="Phase 2A Done-For-You"
        )
    """
    try:
        start_time = datetime.now()

        properties = {
            "Name": {"title": [{"text": {"content": f"{business_name} - Customer Portal"}}]},
            "Email": {"email": email},
            "Business Name": {"rich_text": [{"text": {"content": business_name}}]},
            "Diagnostic Call Date": {"date": {"start": call_date}},
            "Next Steps": {"rich_text": [{"text": {"content": next_steps}}]},
            "Status": {"select": {"name": "Portal Delivered"}},
            "Created Date": {"date": {"start": datetime.now().isoformat()}}
        }

        response = notion.pages.create(
            parent={"database_id": NOTION_CUSTOMER_PROJECTS_DB_ID},
            properties=properties
        )

        portal_url = response["url"]
        elapsed = (datetime.now() - start_time).total_seconds()

        print(f"✅ Created customer portal in {elapsed:.2f}s: {portal_url}")

        if elapsed > 60:
            print(f"⚠️ WARNING: Portal creation took {elapsed:.2f}s (>60s threshold)")

        return portal_url

    except Exception as e:
        print(f"❌ Error creating customer portal for {email}: {e}")
        raise


# ==============================================================================
# Email Analytics Operations
# ==============================================================================

@task(retries=2, retry_delay_seconds=30, name="christmas-log-email-analytics")
def log_email_analytics(
    email: str,
    template_id: str,
    email_number: int,
    status: Literal["sent", "failed"],
    resend_email_id: Optional[str] = None,
    error_message: Optional[str] = None
) -> str:
    """
    Log email send event to Email Analytics database.

    Args:
        email: Recipient email
        template_id: Template used
        email_number: Email number in sequence (1-7)
        status: Send status (sent/failed)
        resend_email_id: Resend API email ID (optional)
        error_message: Error message if failed (optional)

    Returns:
        Analytics page ID

    Example:
        log_email_analytics(
            email="john@testcorp.com",
            template_id="christmas_email_1",
            email_number=1,
            status="sent",
            resend_email_id="resend-123"
        )
    """
    try:
        properties = {
            "Email": {"email": email},
            "Template ID": {"rich_text": [{"text": {"content": template_id}}]},
            "Email Number": {"number": email_number},
            "Status": {"select": {"name": status}},
            "Sent Date": {"date": {"start": datetime.now().isoformat()}},
            "Campaign": {"select": {"name": "Christmas Campaign"}}
        }

        if resend_email_id:
            properties["Resend Email ID"] = {"rich_text": [{"text": {"content": resend_email_id}}]}

        if error_message:
            properties["Error Message"] = {"rich_text": [{"text": {"content": error_message}}]}

        response = notion.pages.create(
            parent={"database_id": NOTION_EMAIL_ANALYTICS_DB_ID},
            properties=properties
        )

        print(f"✅ Logged email analytics for {email}: {template_id} ({status})")
        return response["id"]

    except Exception as e:
        print(f"❌ Error logging email analytics for {email}: {e}")
        # Don't raise - analytics logging should not block email sending
        return None
