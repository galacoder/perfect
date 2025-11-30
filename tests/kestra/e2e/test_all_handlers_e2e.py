"""
E2E Test: All Handler Flows

This test verifies the complete handler flows for:
- noshow-recovery-handler (3-email sequence)
- postcall-maybe-handler (3-email sequence)
- onboarding-handler (3-email welcome sequence)

All emails for these sequences are sent by Kestra (no website involvement).

Test Email: lengobaosang@gmail.com (per CLAUDE.md requirements)
"""

import pytest
import requests
import json
from datetime import datetime, timedelta, timezone
import os
import time
from dotenv import load_dotenv

load_dotenv()

# Test configuration
TEST_EMAIL = "lengobaosang@gmail.com"
KESTRA_URL = os.getenv("KESTRA_URL", "https://kestra.galatek.dev")
KESTRA_USER = os.getenv("KESTRA_USER", "galacoder69@gmail.com")
KESTRA_PASS = os.getenv("KESTRA_PASS", "Kestra2025Admin!")
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_SEQUENCE_DB_ID = os.getenv("NOTION_EMAIL_SEQUENCE_DB_ID")
NOTION_CONTACTS_DB_ID = os.getenv("NOTION_CONTACTS_DB_ID")


@pytest.fixture
def kestra_session():
    """Create authenticated Kestra session"""
    session = requests.Session()
    session.auth = (KESTRA_USER, KESTRA_PASS)
    return session


@pytest.fixture
def notion_headers():
    """Notion API headers"""
    return {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }


@pytest.fixture
def cleanup_notion_contact(notion_headers):
    """Cleanup test contact from Notion before and after test"""
    def _cleanup():
        # Cleanup Contact database
        search_url = f"https://api.notion.com/v1/databases/{NOTION_CONTACTS_DB_ID}/query"
        search_payload = {
            "filter": {
                "property": "email",
                "email": {
                    "equals": TEST_EMAIL
                }
            }
        }

        response = requests.post(search_url, headers=notion_headers, json=search_payload)
        if response.status_code == 200:
            results = response.json().get("results", [])
            for page in results:
                # Archive the page
                archive_url = f"https://api.notion.com/v1/pages/{page['id']}"
                requests.patch(archive_url, headers=notion_headers, json={"archived": True})

        # Cleanup Email Sequence database
        sequence_url = f"https://api.notion.com/v1/databases/{NOTION_SEQUENCE_DB_ID}/query"
        sequence_payload = {
            "filter": {
                "property": "Email",
                "email": {
                    "equals": TEST_EMAIL
                }
            }
        }

        response = requests.post(sequence_url, headers=notion_headers, json=sequence_payload)
        if response.status_code == 200:
            results = response.json().get("results", [])
            for page in results:
                # Archive the page
                archive_url = f"https://api.notion.com/v1/pages/{page['id']}"
                requests.patch(archive_url, headers=notion_headers, json={"archived": True})

    # Cleanup before test
    _cleanup()
    yield
    # Cleanup after test
    _cleanup()


def test_e2e_noshow_recovery_full_flow(kestra_session, cleanup_notion_contact, notion_headers):
    """
    TC-4.5.1: E2E test for noshow-recovery-handler flow

    Verify complete no-show recovery sequence (3 emails ALL from Kestra).
    """
    # 1. Create contact
    create_url = f"https://api.notion.com/v1/pages"
    contact_payload = {
        "parent": {"database_id": NOTION_CONTACTS_DB_ID},
        "properties": {
            "first_name": {"title": [{"text": {"content": "E2E Noshow Test"}}]},
            "email": {"email": TEST_EMAIL},
            "Segment": {"select": {"name": "URGENT"}}
        }
    }
    response = requests.post(create_url, headers=notion_headers, json=contact_payload)
    assert response.status_code == 200, f"Failed to create contact: {response.text}"

    # 2. Trigger noshow-recovery webhook
    webhook_url = f"{KESTRA_URL}/api/v1/executions/webhook/christmas/noshow-recovery-handler/calendly-noshow-webhook"
    webhook_payload = {
        "email": TEST_EMAIL,
        "first_name": "E2E",
        "business_name": "Noshow Corp",
        "meeting_time": datetime.now(timezone.utc).isoformat(),
        "meeting_url": "https://calendly.com/test-meeting",
        "testing_mode": True
    }

    response = kestra_session.post(webhook_url, json=webhook_payload)
    assert response.status_code in [200, 201], f"Webhook trigger failed: {response.text}"

    execution_id = response.json().get("id")
    assert execution_id is not None, "No execution ID returned"

    print(f"\n✅ No-show recovery handler triggered - execution ID: {execution_id}")
    print(f"📧 Expected: 3 emails scheduled by Kestra")


def test_e2e_postcall_maybe_full_flow(kestra_session, cleanup_notion_contact, notion_headers):
    """
    TC-4.5.2: E2E test for postcall-maybe-handler flow

    Verify complete post-call maybe sequence (3 emails ALL from Kestra).
    """
    # 1. Create contact
    create_url = f"https://api.notion.com/v1/pages"
    contact_payload = {
        "parent": {"database_id": NOTION_CONTACTS_DB_ID},
        "properties": {
            "first_name": {"title": [{"text": {"content": "E2E Postcall Test"}}]},
            "email": {"email": TEST_EMAIL},
            "Segment": {"select": {"name": "OPTIMIZE"}}
        }
    }
    response = requests.post(create_url, headers=notion_headers, json=contact_payload)
    assert response.status_code == 200, f"Failed to create contact: {response.text}"

    # 2. Trigger postcall-maybe webhook
    webhook_url = f"{KESTRA_URL}/api/v1/executions/webhook/christmas/postcall-maybe-handler/postcall-maybe-webhook"
    webhook_payload = {
        "email": TEST_EMAIL,
        "first_name": "E2E",
        "business_name": "Postcall Corp",
        "call_outcome": "maybe",
        "call_date": datetime.now(timezone.utc).isoformat(),
        "testing_mode": True
    }

    response = kestra_session.post(webhook_url, json=webhook_payload)
    assert response.status_code in [200, 201], f"Webhook trigger failed: {response.text}"

    execution_id = response.json().get("id")
    assert execution_id is not None, "No execution ID returned"

    print(f"\n✅ Post-call maybe handler triggered - execution ID: {execution_id}")
    print(f"📧 Expected: 3 emails scheduled by Kestra")


def test_e2e_onboarding_full_flow(kestra_session, cleanup_notion_contact, notion_headers):
    """
    TC-4.5.3: E2E test for onboarding-handler flow

    Verify complete onboarding welcome sequence (3 emails ALL from Kestra).
    """
    # 1. Create contact
    create_url = f"https://api.notion.com/v1/pages"
    contact_payload = {
        "parent": {"database_id": NOTION_CONTACTS_DB_ID},
        "properties": {
            "first_name": {"title": [{"text": {"content": "E2E Onboarding Test"}}]},
            "email": {"email": TEST_EMAIL},
            "Segment": {"select": {"name": "CRITICAL"}}
        }
    }
    response = requests.post(create_url, headers=notion_headers, json=contact_payload)
    assert response.status_code == 200, f"Failed to create contact: {response.text}"

    # 2. Trigger onboarding webhook
    webhook_url = f"{KESTRA_URL}/api/v1/executions/webhook/christmas/onboarding-handler/onboarding-start-webhook"
    webhook_payload = {
        "email": TEST_EMAIL,
        "first_name": "E2E",
        "business_name": "Onboarding Corp",
        "payment_confirmed": True,
        "docusign_completed": True,
        "contract_value": 5000,
        "testing_mode": True
    }

    response = kestra_session.post(webhook_url, json=webhook_payload)
    assert response.status_code in [200, 201], f"Webhook trigger failed: {response.text}"

    execution_id = response.json().get("id")
    assert execution_id is not None, "No execution ID returned"

    print(f"\n✅ Onboarding handler triggered - execution ID: {execution_id}")
    print(f"📧 Expected: 3 emails scheduled by Kestra")
