"""
Helper utilities for E2E sales funnel tests.

This module provides:
- Test email generation
- Prefect flow polling
- Notion record verification
- Test data cleanup
- Assessment data generation
"""

import time
import uuid
import httpx
import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from notion_client import Client


# ===== Test Email Generation =====

def generate_test_email() -> str:
    """
    Generate unique test email for this test run.

    Returns:
        str: Unique test email (e.g., test+1732073456+abc123@example.com)

    Example:
        >>> email = generate_test_email()
        >>> assert email.startswith("test+")
        >>> assert "@example.com" in email
    """
    timestamp = int(time.time())
    unique_id = str(uuid.uuid4())[:8]
    return f"test+{timestamp}+{unique_id}@example.com"


# ===== Prefect Flow Polling =====

def wait_for_prefect_flow(
    deployment_name: str,
    email: str,
    prefect_api_url: str = "https://prefect.galatek.dev/api",
    timeout: int = 300,
    poll_interval: int = 5
) -> Optional[str]:
    """
    Poll Prefect API for flow run completion.

    Args:
        deployment_name: Deployment name (e.g., "christmas-signup/production")
        email: Test email to filter flow runs
        prefect_api_url: Prefect API base URL
        timeout: Maximum wait time in seconds (default: 300 = 5 minutes)
        poll_interval: Seconds between polls (default: 5)

    Returns:
        str: Flow run ID if found and completed
        None: If timeout or flow run not found

    Raises:
        ValueError: If deployment_name or email is empty

    Example:
        >>> flow_run_id = wait_for_prefect_flow(
        ...     deployment_name="christmas-signup/production",
        ...     email="test@example.com",
        ...     timeout=60
        ... )
        >>> assert flow_run_id is not None
    """
    if not deployment_name or not email:
        raise ValueError("deployment_name and email are required")

    start_time = time.time()

    with httpx.Client(timeout=10.0) as client:
        while (time.time() - start_time) < timeout:
            try:
                # Query flow runs (Prefect API doesn't support filtering by parameters directly)
                # So we fetch recent flow runs and filter locally
                response = client.get(
                    f"{prefect_api_url}/flow_runs",
                    params={
                        "limit": 50,
                        "sort": "CREATED_DESC"
                    }
                )

                if response.status_code == 200:
                    flow_runs = response.json()

                    # Find flow run matching our criteria
                    for run in flow_runs:
                        # Check if parameters include our test email
                        params = run.get("parameters", {})
                        if params.get("email") == email:
                            # Check state
                            state = run.get("state", {}).get("type")
                            if state == "COMPLETED":
                                return run["id"]
                            elif state in ["FAILED", "CRASHED", "CANCELLED"]:
                                print(f"❌ Flow run {run['id']} failed with state: {state}")
                                return None

                # Wait before next poll
                time.sleep(poll_interval)

            except httpx.RequestError as e:
                print(f"⚠️  Prefect API request error: {e}")
                time.sleep(poll_interval)

    print(f"❌ Timeout waiting for flow run (deployment: {deployment_name}, email: {email})")
    return None


def get_child_flow_runs(
    parent_flow_run_id: str,
    prefect_api_url: str = "https://prefect.galatek.dev/api"
) -> List[Dict[str, Any]]:
    """
    Get child flow runs for a parent flow run.

    Args:
        parent_flow_run_id: Parent flow run ID
        prefect_api_url: Prefect API base URL

    Returns:
        list: List of child flow run objects

    Example:
        >>> child_runs = get_child_flow_runs("flow-run-id-123")
        >>> assert len(child_runs) == 7  # Christmas campaign has 7 emails
    """
    with httpx.Client(timeout=10.0) as client:
        try:
            response = client.get(
                f"{prefect_api_url}/flow_runs",
                params={
                    "parent_flow_run_id": parent_flow_run_id,
                    "limit": 100
                }
            )

            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Failed to get child flow runs: {response.status_code}")
                return []

        except httpx.RequestError as e:
            print(f"❌ Error fetching child flow runs: {e}")
            return []


def cancel_scheduled_flows(
    email: str,
    prefect_api_url: str = "https://prefect.galatek.dev/api"
):
    """
    Cancel all scheduled flow runs for a test email.

    Args:
        email: Test email to filter flow runs
        prefect_api_url: Prefect API base URL

    Example:
        >>> cancel_scheduled_flows("test@example.com")
    """
    with httpx.Client(timeout=10.0) as client:
        try:
            # Get all flow runs with this email
            response = client.get(
                f"{prefect_api_url}/flow_runs",
                params={"limit": 100, "sort": "CREATED_DESC"}
            )

            if response.status_code != 200:
                print(f"⚠️  Failed to fetch flow runs: {response.status_code}")
                return

            flow_runs = response.json()
            cancelled_count = 0

            for run in flow_runs:
                params = run.get("parameters", {})
                if params.get("email") == email:
                    state = run.get("state", {}).get("type")
                    if state == "SCHEDULED":
                        # Cancel this flow run
                        cancel_response = client.post(
                            f"{prefect_api_url}/flow_runs/{run['id']}/set_state",
                            json={"type": "CANCELLED", "name": "Cancelled"}
                        )
                        if cancel_response.status_code == 201:
                            cancelled_count += 1

            if cancelled_count > 0:
                print(f"✅ Cancelled {cancelled_count} scheduled flow runs for {email}")

        except httpx.RequestError as e:
            print(f"⚠️  Error cancelling flow runs: {e}")


# ===== Notion Record Verification =====

def verify_notion_contact(
    notion_client: Client,
    email: str,
    expected_data: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Verify contact exists in BusinessX Canada database with correct data.

    Args:
        notion_client: Notion API client
        email: Contact email to search for
        expected_data: Expected field values

    Returns:
        dict: Contact record if found and verified
        None: If not found or data doesn't match

    Raises:
        AssertionError: If required fields don't match expected values

    Example:
        >>> contact = verify_notion_contact(
        ...     notion_client,
        ...     "test@example.com",
        ...     {"first_name": "Test", "assessment_score": 52}
        ... )
        >>> assert contact is not None
    """
    db_id = os.getenv("NOTION_BUSINESSX_DB_ID")
    if not db_id:
        raise ValueError("NOTION_BUSINESSX_DB_ID not set in environment")

    # Query database
    response = notion_client.databases.query(
        database_id=db_id,
        filter={"property": "Email", "email": {"equals": email}}
    )

    results = response.get("results", [])
    if not results:
        return None

    record = results[0]
    props = record["properties"]

    # Verify expected fields
    if "first_name" in expected_data:
        actual_first_name = props.get("First Name", {}).get("title", [{}])[0].get("text", {}).get("content", "")
        assert actual_first_name == expected_data["first_name"], \
            f"First name mismatch: {actual_first_name} != {expected_data['first_name']}"

    if "business_name" in expected_data:
        actual_business = props.get("Business Name", {}).get("rich_text", [{}])[0].get("text", {}).get("content", "")
        assert actual_business == expected_data["business_name"], \
            f"Business name mismatch: {actual_business} != {expected_data['business_name']}"

    if "assessment_score" in expected_data:
        actual_score = props.get("Assessment Score", {}).get("number")
        assert actual_score == expected_data["assessment_score"], \
            f"Assessment score mismatch: {actual_score} != {expected_data['assessment_score']}"

    return record


def verify_notion_sequence(
    notion_client: Client,
    email: str,
    expected_emails_count: int = 7
) -> Optional[Dict[str, Any]]:
    """
    Verify sequence entry exists in Email Sequence database.

    Args:
        notion_client: Notion API client
        email: Contact email to search for
        expected_emails_count: Expected number of emails (default: 7 for Christmas)

    Returns:
        dict: Sequence record if found
        None: If not found

    Example:
        >>> sequence = verify_notion_sequence(notion_client, "test@example.com")
        >>> assert sequence is not None
    """
    db_id = os.getenv("NOTION_EMAIL_SEQUENCE_DB_ID")
    if not db_id:
        raise ValueError("NOTION_EMAIL_SEQUENCE_DB_ID not set in environment")

    # Query database
    response = notion_client.databases.query(
        database_id=db_id,
        filter={"property": "Email", "email": {"equals": email}}
    )

    results = response.get("results", [])
    if not results:
        return None

    record = results[0]
    props = record["properties"]

    # Verify emails scheduled
    emails_scheduled = props.get("Emails Scheduled", {}).get("number")
    assert emails_scheduled == expected_emails_count, \
        f"Emails scheduled mismatch: {emails_scheduled} != {expected_emails_count}"

    # Verify campaign
    campaign = props.get("Campaign", {}).get("select", {}).get("name")
    assert campaign == "Christmas 2025", \
        f"Campaign mismatch: {campaign} != Christmas 2025"

    # Verify status
    status = props.get("Status", {}).get("select", {}).get("name")
    assert status == "Active", \
        f"Status mismatch: {status} != Active"

    return record


# ===== Test Data Cleanup =====

def cleanup_test_data(
    notion_client: Client,
    email: str,
    prefect_api_url: str = "https://prefect.galatek.dev/api"
):
    """
    Clean up all test data for a test email.

    This removes:
    - Contact from BusinessX Canada database
    - Sequence from Email Sequence database
    - Scheduled flow runs from Prefect

    Args:
        notion_client: Notion API client
        email: Test email to clean up
        prefect_api_url: Prefect API base URL

    Example:
        >>> cleanup_test_data(notion_client, "test@example.com")
    """
    print(f"🧹 Cleaning up test data for {email}...")

    # Delete Notion contact
    try:
        delete_notion_contact(notion_client, email)
        print(f"✅ Deleted Notion contact")
    except Exception as e:
        print(f"⚠️  Failed to delete contact: {e}")

    # Delete Notion sequence
    try:
        delete_notion_sequence(notion_client, email)
        print(f"✅ Deleted Notion sequence")
    except Exception as e:
        print(f"⚠️  Failed to delete sequence: {e}")

    # Cancel Prefect flows
    try:
        cancel_scheduled_flows(email, prefect_api_url)
        print(f"✅ Cancelled Prefect flows")
    except Exception as e:
        print(f"⚠️  Failed to cancel flows: {e}")

    print(f"✅ Cleanup complete for {email}")


def delete_notion_contact(notion_client: Client, email: str):
    """Delete contact from BusinessX Canada database (internal)."""
    db_id = os.getenv("NOTION_BUSINESSX_DB_ID")
    if not db_id:
        return

    response = notion_client.databases.query(
        database_id=db_id,
        filter={"property": "Email", "email": {"equals": email}}
    )

    for page in response.get("results", []):
        notion_client.pages.update(page_id=page["id"], archived=True)


def delete_notion_sequence(notion_client: Client, email: str):
    """Delete sequence from Email Sequence database (internal)."""
    db_id = os.getenv("NOTION_EMAIL_SEQUENCE_DB_ID")
    if not db_id:
        return

    response = notion_client.databases.query(
        database_id=db_id,
        filter={"property": "Email", "email": {"equals": email}}
    )

    for page in response.get("results", []):
        notion_client.pages.update(page_id=page["id"], archived=True)


# ===== Assessment Data Generation =====

def get_assessment_test_data(email: str, first_name: str = "TestUser", business_name: str = "Test Business") -> Dict[str, Any]:
    """
    Generate realistic assessment test data.

    Args:
        email: Test email address
        first_name: Test first name (default: "TestUser")
        business_name: Test business name (default: "Test Business")

    Returns:
        dict: Complete assessment data

    Example:
        >>> data = get_assessment_test_data("test@example.com")
        >>> assert data["red_systems"] == 2  # CRITICAL segment
        >>> assert data["assessment_score"] == 52
    """
    return {
        # Contact info
        "email": email,
        "first_name": first_name,
        "last_name": "User",
        "business_name": business_name,

        # Assessment results (CRITICAL segment: 2 red systems)
        "assessment_score": 52,
        "red_systems": 2,
        "orange_systems": 1,
        "yellow_systems": 2,
        "green_systems": 3,

        # System-specific scores
        "gps_score": 45,
        "money_score": 38,
        "marketing_score": 62,

        # Revenue leak (calculated: 2*$5000 + 1*$3000 = $13000/month)
        "revenue_leak_total": 13000,

        # Weakest systems
        "weakest_system_1": "Money",
        "weakest_system_2": "GPS",

        # Metadata
        "timestamp": datetime.now().isoformat()
    }
