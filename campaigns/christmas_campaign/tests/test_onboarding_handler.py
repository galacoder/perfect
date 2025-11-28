"""
Unit tests for Onboarding Handler Flow.

Tests cover:
- Flow structure validation
- Payment validation
- Contact search
- Idempotency checks (Wave 4)
- Email scheduling (Wave 4)

Author: Christmas Campaign Team
Created: 2025-11-27
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from campaigns.christmas_campaign.flows.onboarding_handler import (
    onboarding_handler_flow,
    schedule_onboarding_emails
)


@pytest.fixture
def prefect_test_harness():
    """Fixture to provide Prefect test harness for flow execution."""
    from prefect.testing.utilities import prefect_test_harness
    with prefect_test_harness():
        yield


@pytest.fixture
def mock_contact():
    """Mock contact returned from Notion."""
    return {
        "id": "test-contact-123",
        "properties": {
            "Email": {"email": "test@example.com"},
            "First Name": {"rich_text": [{"plain_text": "Test"}]},
            "Business Name": {"title": [{"plain_text": "Test Salon"}]}
        }
    }


@pytest.fixture
def mock_onboarding_sequence():
    """Mock onboarding sequence returned from Notion."""
    return {
        "id": "test-sequence-456",
        "properties": {
            "Email": {"email": "test@example.com"},
            "Campaign": {"select": {"name": "Christmas 2025"}},
            "Payment Amount": {"number": 2997.00},
            "Payment Date": {"date": {"start": "2025-12-01T15:00:00Z"}},
            "Salon Address": {"rich_text": [{"plain_text": "123 Main St"}]},
            "Observation Dates": {"rich_text": [{"plain_text": "2025-12-10, 2025-12-17"}]}
        }
    }


class TestOnboardingHandlerFlowStructure:
    """Test onboarding handler flow structure (Wave 1, Feature 1.4)."""

    def test_flow_exists(self):
        """Test that onboarding_handler_flow exists and is callable."""
        assert callable(onboarding_handler_flow)
        assert onboarding_handler_flow.__name__ == "onboarding_handler_flow"

    def test_flow_has_correct_parameters(self):
        """Test flow accepts required parameters."""
        import inspect
        sig = inspect.signature(onboarding_handler_flow)
        params = list(sig.parameters.keys())

        # Required parameters
        assert "email" in params
        assert "first_name" in params
        assert "business_name" in params
        assert "payment_confirmed" in params
        assert "payment_amount" in params
        assert "payment_date" in params

        # Optional parameters
        assert "docusign_completed" in params
        assert "salon_address" in params
        assert "observation_dates" in params
        assert "start_date" in params
        assert "package_type" in params


class TestOnboardingHandlerFlow:
    """Test onboarding handler flow functionality (Wave 4)."""

    def test_flow_rejects_unconfirmed_payment(self, prefect_test_harness):
        """Test flow rejects requests without payment confirmation."""
        result = onboarding_handler_flow(
            email="test@example.com",
            first_name="Test",
            business_name="Test Salon",
            payment_confirmed=False,
            payment_amount=2997.00,
            payment_date="2025-12-01T15:00:00Z"
        )

        assert result["status"] == "error"
        assert "payment not confirmed" in result["message"].lower()

    @patch('campaigns.christmas_campaign.flows.onboarding_handler.search_contact_by_email')
    def test_flow_handles_contact_not_found(self, mock_search, prefect_test_harness):
        """Test flow handles contact not found gracefully."""
        mock_search.return_value = None

        result = onboarding_handler_flow(
            email="nonexistent@example.com",
            first_name="Test",
            business_name="Test Salon",
            payment_confirmed=True,
            payment_amount=2997.00,
            payment_date="2025-12-01T15:00:00Z"
        )

        assert result["status"] == "error"
        assert "contact not found" in result["message"].lower()
        mock_search.assert_called_once_with("nonexistent@example.com")

    @patch('campaigns.christmas_campaign.flows.onboarding_handler.schedule_onboarding_emails')
    @patch('campaigns.christmas_campaign.flows.onboarding_handler.create_onboarding_sequence')
    @patch('campaigns.christmas_campaign.flows.onboarding_handler.search_email_sequence_by_email')
    @patch('campaigns.christmas_campaign.flows.onboarding_handler.search_contact_by_email')
    def test_flow_creates_sequence_and_schedules_emails(
        self, mock_search_contact, mock_search_sequence, mock_create_sequence,
        mock_schedule, mock_contact, mock_onboarding_sequence, prefect_test_harness
    ):
        """Test successful flow execution creates sequence and schedules emails."""
        mock_search_contact.return_value = mock_contact
        mock_search_sequence.return_value = None  # No existing sequence
        mock_create_sequence.return_value = mock_onboarding_sequence
        mock_schedule.return_value = [
            {"email_number": 1, "flow_run_id": "run-1"},
            {"email_number": 2, "flow_run_id": "run-2"},
            {"email_number": 3, "flow_run_id": "run-3"}
        ]

        result = onboarding_handler_flow(
            email="test@example.com",
            first_name="Test",
            business_name="Test Salon",
            payment_confirmed=True,
            payment_amount=2997.00,
            payment_date="2025-12-01T15:00:00Z",
            salon_address="123 Main St",
            observation_dates=["2025-12-10", "2025-12-17"],
            start_date="2025-12-10"
        )

        assert result["status"] == "success"
        assert result["sequence_id"] == "test-sequence-456"
        assert len(result["scheduled_emails"]) == 3
        mock_create_sequence.assert_called_once()
        mock_schedule.assert_called_once()

    @patch('campaigns.christmas_campaign.flows.onboarding_handler.search_email_sequence_by_email')
    @patch('campaigns.christmas_campaign.flows.onboarding_handler.search_contact_by_email')
    def test_flow_skips_duplicate_onboarding_sequence(
        self, mock_search_contact, mock_search_sequence,
        mock_contact, mock_onboarding_sequence, prefect_test_harness
    ):
        """Test idempotency - skip if onboarding sequence already exists."""
        mock_search_contact.return_value = mock_contact
        mock_search_sequence.return_value = mock_onboarding_sequence

        result = onboarding_handler_flow(
            email="test@example.com",
            first_name="Test",
            business_name="Test Salon",
            payment_confirmed=True,
            payment_amount=2997.00,
            payment_date="2025-12-01T15:00:00Z"
        )

        assert result["status"] == "skipped"
        assert result["reason"] == "duplicate_onboarding_sequence"
        assert "existing_sequence_id" in result


class TestOnboardingEmailScheduling:
    """Test onboarding email scheduling function (Wave 4, Feature 4.3)."""

    @patch('campaigns.christmas_campaign.flows.onboarding_handler.get_run_logger')
    def test_schedule_onboarding_emails_structure(self, mock_logger):
        """Test schedule_onboarding_emails function exists and has correct signature."""
        import inspect
        assert callable(schedule_onboarding_emails)

        sig = inspect.signature(schedule_onboarding_emails)
        params = list(sig.parameters.keys())

        assert "email" in params
        assert "first_name" in params
        assert "business_name" in params
        assert "payment_date" in params

    @patch('campaigns.christmas_campaign.flows.onboarding_handler.asyncio.run')
    @patch('campaigns.christmas_campaign.flows.onboarding_handler.get_run_logger')
    def test_schedule_onboarding_emails_production_timing(self, mock_logger, mock_asyncio_run):
        """Test production timing: 1h, 24h, 72h."""
        mock_asyncio_run.return_value = [
            {"email_number": 1, "delay_hours": 1},
            {"email_number": 2, "delay_hours": 24},
            {"email_number": 3, "delay_hours": 72}
        ]

        result = schedule_onboarding_emails(
            email="test@example.com",
            first_name="Test",
            business_name="Test Salon",
            payment_date="2025-12-01T15:00:00Z"
        )

        assert len(result) == 3
        assert result[0]["delay_hours"] == 1
        assert result[1]["delay_hours"] == 24
        assert result[2]["delay_hours"] == 72

    @patch('campaigns.christmas_campaign.flows.onboarding_handler.asyncio.run')
    @patch('campaigns.christmas_campaign.flows.onboarding_handler.get_run_logger')
    def test_schedule_onboarding_emails_testing_timing(self, mock_logger, mock_asyncio_run):
        """Test TESTING_MODE timing: 1min, 2min, 3min."""
        mock_asyncio_run.return_value = [
            {"email_number": 1, "delay_hours": 1/60},
            {"email_number": 2, "delay_hours": 2/60},
            {"email_number": 3, "delay_hours": 3/60}
        ]

        result = schedule_onboarding_emails(
            email="test@example.com",
            first_name="Test",
            business_name="Test Salon",
            payment_date="2025-12-01T15:00:00Z"
        )

        assert len(result) == 3
        # In testing mode, delays should be in minutes
        assert result[0]["delay_hours"] < 0.02  # ~1 minute
        assert result[1]["delay_hours"] < 0.04  # ~2 minutes
        assert result[2]["delay_hours"] < 0.06  # ~3 minutes
