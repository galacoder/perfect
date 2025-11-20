"""
Shared test fixtures and configuration for E2E sales funnel tests.

This module provides:
- Test email generation (unique per run)
- Notion database cleanup fixtures
- FastAPI server health check
- Test data factories
- Setup/teardown hooks
"""

import pytest
import os
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
import httpx
from notion_client import Client


# ===== Test Configuration =====

@pytest.fixture(scope="session")
def api_base_url():
    """FastAPI server base URL (should be running locally)."""
    return "http://localhost:8000"


@pytest.fixture(scope="session")
def prefect_api_url():
    """Prefect API URL (production instance)."""
    return "https://prefect.galatek.dev/api"


@pytest.fixture(scope="session")
def notion_client():
    """Notion API client for database verification."""
    token = os.getenv("NOTION_TOKEN")
    if not token:
        pytest.fail("NOTION_TOKEN not found in environment variables")
    return Client(auth=token)


# ===== Test Email Generation =====

@pytest.fixture(scope="function")
def test_email():
    """
    Generate unique test email for this test run.

    Format: test+{timestamp}+{uuid}@example.com

    Example: test+1732073456+abc123@example.com
    """
    timestamp = int(time.time())
    unique_id = str(uuid.uuid4())[:8]
    return f"test+{timestamp}+{unique_id}@example.com"


@pytest.fixture(scope="function")
def test_first_name():
    """Generate test first name."""
    return "TestUser"


@pytest.fixture(scope="function")
def test_business_name():
    """Generate test business name."""
    return "Test Business"


# ===== Test Data Factory =====

@pytest.fixture(scope="function")
def assessment_test_data(test_email, test_first_name, test_business_name):
    """
    Generate realistic assessment test data.

    Returns:
        dict: Complete assessment data with:
            - Contact info (email, name, business)
            - Assessment scores (red, orange, yellow, green systems)
            - System-specific scores (GPS, Money, etc.)
            - Revenue leak estimates
            - Weakest systems
    """
    return {
        # Contact info
        "email": test_email,
        "first_name": test_first_name,
        "last_name": "User",
        "business_name": test_business_name,

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
        "timestamp": datetime.now().isoformat(),

        # Assessment answers (16 questions - realistic pattern)
        "answers": {
            "q1": False,  # GPS Generate
            "q2": True,   # GPS Generate
            "q3": False,  # GPS Persuade
            "q4": True,   # GPS Persuade
            "q5": False,  # GPS Serve
            "q6": True,   # GPS Serve
            "q7": True,   # GPS Serve
            "q8": False,  # Money
            "q9": False,  # Money
            "q10": True,  # Money
            "q11": False, # Money
            "q12": True,  # Marketing
            "q13": True,  # Marketing
            "q14": True,  # Marketing
            "q15": False, # Marketing
            "q16": True   # Marketing
        }
    }


# ===== FastAPI Server Health Check =====

@pytest.fixture(scope="session", autouse=True)
def verify_server_running(api_base_url):
    """
    Verify FastAPI server is running before any tests execute.

    Raises:
        pytest.fail: If server is not accessible
    """
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(f"{api_base_url}/health")
            if response.status_code != 200:
                pytest.fail(
                    f"FastAPI server health check failed: {response.status_code}\n"
                    f"Start server with: uvicorn server:app --reload"
                )

            health_data = response.json()
            print(f"\n✅ FastAPI server healthy: {health_data}")

            # Verify TESTING_MODE is enabled
            if health_data.get("environment", {}).get("testing_mode") != "true":
                pytest.fail(
                    "TESTING_MODE is not enabled!\n"
                    "Set TESTING_MODE=true in .env for fast test execution"
                )

    except httpx.ConnectError:
        pytest.fail(
            "FastAPI server not running!\n"
            "Start server with: uvicorn server:app --reload"
        )


# ===== Notion Database Cleanup =====

@pytest.fixture(scope="function")
def cleanup_notion_contact(notion_client, request):
    """
    Cleanup fixture that deletes test contact from Notion after test completes.

    Usage:
        def test_something(assessment_test_data, cleanup_notion_contact):
            # Test creates contact with assessment_test_data['email']
            # Contact will be deleted automatically after test
            pass
    """
    test_email = None

    # Capture email from test
    def _set_test_email(email: str):
        nonlocal test_email
        test_email = email

    # Provide setter to test
    yield _set_test_email

    # Cleanup after test
    if test_email:
        try:
            _delete_notion_contact(notion_client, test_email)
            print(f"✅ Cleaned up Notion contact: {test_email}")
        except Exception as e:
            print(f"⚠️  Failed to cleanup Notion contact {test_email}: {e}")


def _delete_notion_contact(notion_client: Client, email: str):
    """Delete contact from BusinessX Canada database."""
    db_id = os.getenv("NOTION_BUSINESSX_DB_ID")
    if not db_id:
        print("⚠️  NOTION_BUSINESSX_DB_ID not set, skipping cleanup")
        return

    # Query for contact
    response = notion_client.databases.query(
        database_id=db_id,
        filter={"property": "Email", "email": {"equals": email}}
    )

    # Archive (delete) all matching pages
    for page in response.get("results", []):
        notion_client.pages.update(
            page_id=page["id"],
            archived=True
        )


@pytest.fixture(scope="function")
def cleanup_notion_sequence(notion_client, request):
    """
    Cleanup fixture that deletes test sequence from Notion after test completes.

    Usage:
        def test_something(assessment_test_data, cleanup_notion_sequence):
            # Test creates sequence with assessment_test_data['email']
            # Sequence will be deleted automatically after test
            pass
    """
    test_email = None

    # Capture email from test
    def _set_test_email(email: str):
        nonlocal test_email
        test_email = email

    # Provide setter to test
    yield _set_test_email

    # Cleanup after test
    if test_email:
        try:
            _delete_notion_sequence(notion_client, test_email)
            print(f"✅ Cleaned up Notion sequence: {test_email}")
        except Exception as e:
            print(f"⚠️  Failed to cleanup Notion sequence {test_email}: {e}")


def _delete_notion_sequence(notion_client: Client, email: str):
    """Delete sequence from Email Sequence database."""
    db_id = os.getenv("NOTION_EMAIL_SEQUENCE_DB_ID")
    if not db_id:
        print("⚠️  NOTION_EMAIL_SEQUENCE_DB_ID not set, skipping cleanup")
        return

    # Query for sequence
    response = notion_client.databases.query(
        database_id=db_id,
        filter={"property": "Email", "email": {"equals": email}}
    )

    # Archive (delete) all matching pages
    for page in response.get("results", []):
        notion_client.pages.update(
            page_id=page["id"],
            archived=True
        )


# ===== Test Session Hooks =====

@pytest.fixture(scope="session", autouse=True)
def test_session_info():
    """Print test session information."""
    print("\n" + "="*80)
    print("🎯 E2E Sales Funnel Test Suite")
    print("="*80)
    print(f"Campaign: Christmas Campaign (dfu/xmas-a01)")
    print(f"Server: Local dev server")
    print(f"Testing Mode: ENABLED (fast execution)")
    print(f"Started: {datetime.now().isoformat()}")
    print("="*80 + "\n")

    yield

    print("\n" + "="*80)
    print(f"Test session completed: {datetime.now().isoformat()}")
    print("="*80 + "\n")
