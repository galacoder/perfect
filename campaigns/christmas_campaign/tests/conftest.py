"""
Pytest fixtures for Christmas Campaign tests.

This module provides shared test fixtures for:
1. Mock contact data
2. Mock assessment data
3. Mock email templates
4. Mock Notion responses
5. Mock Resend responses

Author: Christmas Campaign Team
Created: 2025-11-16
"""

import pytest
from datetime import datetime
from typing import Dict, Any


# ==============================================================================
# Contact Data Fixtures
# ==============================================================================

@pytest.fixture
def sample_contact_data() -> Dict[str, Any]:
    """Sample contact data for testing."""
    return {
        "email": "test@example.com",
        "first_name": "John",
        "business_name": "Test Corp",
        "segment": "OPTIMIZE",
        "phase": "Phase 1 Assessment",
        "assessment_score": 42
    }


@pytest.fixture
def sample_contact_critical() -> Dict[str, Any]:
    """Sample contact with CRITICAL segment."""
    return {
        "email": "critical@example.com",
        "first_name": "Jane",
        "business_name": "Critical Corp",
        "segment": "CRITICAL",
        "phase": "Phase 1 Assessment",
        "assessment_score": 15,
        "red_systems": 3
    }


@pytest.fixture
def sample_contact_urgent() -> Dict[str, Any]:
    """Sample contact with URGENT segment."""
    return {
        "email": "urgent@example.com",
        "first_name": "Bob",
        "business_name": "Urgent Inc",
        "segment": "URGENT",
        "phase": "Phase 1 Assessment",
        "assessment_score": 28,
        "red_systems": 1,
        "orange_systems": 2
    }


# ==============================================================================
# Assessment Data Fixtures
# ==============================================================================

@pytest.fixture
def sample_assessment_optimize() -> Dict[str, Any]:
    """Sample assessment data resulting in OPTIMIZE segment."""
    return {
        "email": "test@example.com",
        "red_systems": 0,
        "orange_systems": 1,
        "yellow_systems": 3,
        "green_systems": 4,
        "assessment_score": 65
    }


@pytest.fixture
def sample_assessment_urgent() -> Dict[str, Any]:
    """Sample assessment data resulting in URGENT segment."""
    return {
        "email": "test@example.com",
        "red_systems": 1,
        "orange_systems": 2,
        "yellow_systems": 2,
        "green_systems": 3,
        "assessment_score": 45
    }


@pytest.fixture
def sample_assessment_critical() -> Dict[str, Any]:
    """Sample assessment data resulting in CRITICAL segment."""
    return {
        "email": "test@example.com",
        "red_systems": 3,
        "orange_systems": 2,
        "yellow_systems": 2,
        "green_systems": 1,
        "assessment_score": 20
    }


# ==============================================================================
# Email Template Fixtures
# ==============================================================================

@pytest.fixture
def sample_email_template() -> str:
    """Sample email template with variables."""
    return """
    <html>
    <body>
        <h1>Hi {{first_name}}!</h1>
        <p>Thanks for completing the assessment for {{business_name}}.</p>
        <p>Your score: {{assessment_score}}</p>
    </body>
    </html>
    """


@pytest.fixture
def email_template_results() -> str:
    """Email 1: Results delivery template."""
    return """
    <html>
    <body>
        <h1>Your BusOS Assessment Results</h1>
        <p>Hi {{first_name}},</p>
        <p>Your assessment for {{business_name}} is complete!</p>
        <p>Your BusOS Score: {{assessment_score}}/100</p>
    </body>
    </html>
    """


@pytest.fixture
def email_template_quick_wins() -> str:
    """Email 2: Quick wins template."""
    return """
    <html>
    <body>
        <h1>3 Quick Wins for {{business_name}}</h1>
        <p>Hi {{first_name}},</p>
        <p>Based on your assessment, here are 3 immediate actions...</p>
    </body>
    </html>
    """


# ==============================================================================
# Notion Response Fixtures
# ==============================================================================

@pytest.fixture
def mock_notion_contact_response() -> Dict[str, Any]:
    """Mock Notion contact database response."""
    return {
        "object": "page",
        "id": "test-page-id-123",
        "created_time": "2025-11-16T00:00:00.000Z",
        "last_edited_time": "2025-11-16T00:00:00.000Z",
        "properties": {
            "email": {
                "email": "test@example.com"
            },
            "first_name": {
                "rich_text": [{"text": {"content": "John"}}]
            },
            "business_name": {
                "title": [{"text": {"content": "Test Corp"}}]
            },
            "Segment": {
                "select": {"name": "OPTIMIZE"}
            },
            "Assessment Score": {
                "number": 42
            }
        }
    }


@pytest.fixture
def mock_notion_template_response() -> Dict[str, Any]:
    """Mock Notion template database response."""
    return {
        "object": "page",
        "id": "template-page-id-123",
        "properties": {
            "template_id": {
                "title": [{"text": {"content": "christmas_email_1"}}]
            },
            "subject": {
                "rich_text": [{"text": {"content": "Your BusOS Results"}}]
            },
            "html_body": {
                "rich_text": [{"text": {"content": "<html>...</html>"}}]
            }
        }
    }


@pytest.fixture
def mock_notion_search_results() -> Dict[str, Any]:
    """Mock Notion database search results."""
    return {
        "object": "list",
        "results": [
            {
                "object": "page",
                "id": "test-page-id-123",
                "properties": {
                    "email": {"email": "test@example.com"}
                }
            }
        ],
        "has_more": False
    }


# ==============================================================================
# Resend Response Fixtures
# ==============================================================================

@pytest.fixture
def mock_resend_success_response() -> Dict[str, Any]:
    """Mock successful Resend API response."""
    return {
        "id": "resend-email-id-123",
        "from": "noreply@sangletech.com",
        "to": ["test@example.com"],
        "subject": "Your BusOS Results",
        "created_at": datetime.now().isoformat()
    }


@pytest.fixture
def mock_resend_error_response() -> Dict[str, Any]:
    """Mock error Resend API response."""
    return {
        "statusCode": 400,
        "message": "Invalid email address",
        "name": "validation_error"
    }


# ==============================================================================
# Date/Time Fixtures
# ==============================================================================

@pytest.fixture
def mock_current_time():
    """Mock current time for testing."""
    return datetime(2025, 11, 16, 12, 0, 0)


@pytest.fixture
def mock_future_time():
    """Mock future time for testing scheduled flows."""
    return datetime(2025, 11, 18, 12, 0, 0)


# ==============================================================================
# Environment Fixtures
# ==============================================================================

@pytest.fixture(autouse=True)
def prefect_test_mode(monkeypatch):
    """Disable Prefect tracking for unit tests."""
    # Use ephemeral API (in-memory, no server needed)
    monkeypatch.setenv("PREFECT_API_URL", "http://ephemeral/api")
    monkeypatch.setenv("PREFECT_API_ENABLE_HTTP2", "false")


@pytest.fixture(autouse=True)
def mock_schedule_email_sequence(monkeypatch):
    """
    Mock schedule_email_sequence for all tests.

    This prevents tests from trying to connect to Prefect API when testing
    signup_handler flow. Returns a successful scheduling result by default.
    """
    from unittest.mock import Mock

    mock_return = [
        {
            "email_number": i,
            "flow_run_id": f"test-flow-run-{i}",
            "scheduled_time": "2025-11-19T10:00:00",
            "delay_hours": i * 24
        }
        for i in range(1, 8)
    ]

    mock_func = Mock(return_value=mock_return)
    monkeypatch.setattr(
        "campaigns.christmas_campaign.flows.signup_handler.schedule_email_sequence",
        mock_func
    )

    return mock_func


@pytest.fixture
def testing_mode_enabled(monkeypatch):
    """Enable testing mode for fast email sequences."""
    monkeypatch.setenv("TESTING_MODE", "true")


@pytest.fixture
def testing_mode_disabled(monkeypatch):
    """Disable testing mode for production-like tests."""
    monkeypatch.setenv("TESTING_MODE", "false")


# ==============================================================================
# Deployment Fixtures
# ==============================================================================

@pytest.fixture
def sample_deployment_ids(monkeypatch):
    """Mock deployment IDs in environment."""
    deployment_ids = {
        "DEPLOYMENT_ID_CHRISTMAS_EMAIL_1": "deploy-1-id-123",
        "DEPLOYMENT_ID_CHRISTMAS_EMAIL_2": "deploy-2-id-123",
        "DEPLOYMENT_ID_CHRISTMAS_EMAIL_3": "deploy-3-id-123",
        "DEPLOYMENT_ID_CHRISTMAS_EMAIL_4": "deploy-4-id-123",
        "DEPLOYMENT_ID_CHRISTMAS_EMAIL_5": "deploy-5-id-123",
        "DEPLOYMENT_ID_CHRISTMAS_EMAIL_6": "deploy-6-id-123",
        "DEPLOYMENT_ID_CHRISTMAS_EMAIL_7": "deploy-7-id-123",
    }
    for key, value in deployment_ids.items():
        monkeypatch.setenv(key, value)


# ==============================================================================
# Cal.com Webhook Fixtures
# ==============================================================================

@pytest.fixture
def sample_booking_payload() -> Dict[str, Any]:
    """Sample Cal.com booking webhook payload."""
    return {
        "triggerEvent": "BOOKING_CREATED",
        "payload": {
            "id": 12345,
            "uid": "booking-uid-123",
            "title": "BusOS Diagnostic Call",
            "startTime": "2025-11-20T10:00:00.000Z",
            "endTime": "2025-11-20T11:00:00.000Z",
            "attendees": [
                {
                    "email": "test@example.com",
                    "name": "John Doe",
                    "timeZone": "America/Toronto"
                }
            ],
            "metadata": {
                "business_name": "Test Corp"
            }
        }
    }


@pytest.fixture
def sample_call_complete_payload() -> Dict[str, Any]:
    """Sample webhook payload for completed diagnostic call."""
    return {
        "email": "test@example.com",
        "call_date": "2025-11-20",
        "call_notes": "Great call, ready for portal delivery",
        "next_steps": "Phase 2A Done-For-You"
    }
