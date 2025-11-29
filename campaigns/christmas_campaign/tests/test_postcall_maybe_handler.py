"""
Unit tests for Post-Call Maybe Handler Flow.

Tests cover:
- Flow structure validation
- Contact search (success and failure)
- Idempotency checks
- Sequence creation
- Email scheduling
- Error handling

Author: Christmas Campaign Team
Created: 2025-11-27
Updated: 2025-11-28 (Wave 6: Comprehensive test coverage)
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from campaigns.christmas_campaign.flows.postcall_maybe_handler import (
    postcall_maybe_handler_flow,
    schedule_postcall_emails
)


# ==============================================================================
# Test Fixtures
# ==============================================================================

@pytest.fixture
def mock_contact():
    """Mock contact from Notion."""
    return {
        "id": "contact-123",
        "properties": {
            "email": {"email": "test@example.com"},
            "First Name": {"title": [{"plain_text": "John"}]},
            "Business Name": {"rich_text": [{"plain_text": "Test Corp"}]}
        }
    }


@pytest.fixture
def mock_postcall_sequence():
    """Mock post-call sequence from Notion."""
    return {
        "id": "sequence-456",
        "properties": {
            "Email": {"email": "test@example.com"},
            "Template Type": {"select": {"name": "Post-Call Follow-Up"}},
            "Campaign": {"select": {"name": "Christmas 2025"}}
        }
    }


@pytest.fixture
def mock_lead_nurture_sequence():
    """Mock lead nurture sequence (different type)."""
    return {
        "id": "sequence-789",
        "properties": {
            "Email": {"email": "test@example.com"},
            "Template Type": {"select": {"name": "Lead Nurture"}},
            "Campaign": {"select": {"name": "Christmas 2025"}}
        }
    }


# ==============================================================================
# Flow Structure Tests
# ==============================================================================

class TestPostCallMaybeHandlerFlowStructure:
    """Test post-call maybe handler flow structure."""

    def test_flow_exists(self):
        """Test that postcall_maybe_handler_flow exists and is callable."""
        assert callable(postcall_maybe_handler_flow)
        assert postcall_maybe_handler_flow.__name__ == "postcall_maybe_handler_flow"

    def test_flow_has_correct_parameters(self):
        """Test flow accepts required parameters."""
        import inspect
        sig = inspect.signature(postcall_maybe_handler_flow)
        params = list(sig.parameters.keys())

        # Required parameters
        assert "email" in params
        assert "first_name" in params
        assert "business_name" in params
        assert "call_date" in params

        # Optional parameters
        assert "call_outcome" in params
        assert "call_notes" in params
        assert "objections" in params
        assert "follow_up_priority" in params


# ==============================================================================
# Contact Search Tests
# ==============================================================================

class TestContactSearch:
    """Test contact search behavior."""

    @patch('campaigns.christmas_campaign.flows.postcall_maybe_handler.search_contact_by_email')
    def test_flow_fails_when_contact_not_found(self, mock_search):
        """Test flow returns error when contact not found."""
        mock_search.return_value = None

        result = postcall_maybe_handler_flow(
            email="unknown@example.com",
            first_name="Unknown",
            business_name="Unknown Corp",
            call_date="2025-12-01T14:30:00Z"
        )

        assert result["status"] == "error"
        assert "not found" in result["message"].lower()
        assert result["email"] == "unknown@example.com"

    @patch('campaigns.christmas_campaign.flows.postcall_maybe_handler.search_contact_by_email')
    @patch('campaigns.christmas_campaign.flows.postcall_maybe_handler.search_email_sequence_by_email')
    @patch('campaigns.christmas_campaign.flows.postcall_maybe_handler.create_postcall_sequence')
    @patch('campaigns.christmas_campaign.flows.postcall_maybe_handler.schedule_postcall_emails')
    def test_flow_succeeds_when_contact_found(
        self, mock_schedule, mock_create, mock_search_sequence, mock_search_contact,
        mock_contact, mock_postcall_sequence
    ):
        """Test flow succeeds when contact found."""
        mock_search_contact.return_value = mock_contact
        mock_search_sequence.return_value = None
        mock_create.return_value = mock_postcall_sequence
        mock_schedule.return_value = []

        result = postcall_maybe_handler_flow(
            email="test@example.com",
            first_name="John",
            business_name="Test Corp",
            call_date="2025-12-01T14:30:00Z"
        )

        assert result["status"] == "success"
        assert result["contact_id"] == "contact-123"
        mock_search_contact.assert_called_once_with("test@example.com")


# ==============================================================================
# Idempotency Tests
# ==============================================================================

class TestIdempotency:
    """Test idempotency checks for duplicate prevention."""

    @patch('campaigns.christmas_campaign.flows.postcall_maybe_handler.search_contact_by_email')
    @patch('campaigns.christmas_campaign.flows.postcall_maybe_handler.search_email_sequence_by_email')
    def test_flow_skips_duplicate_postcall_sequence(
        self, mock_search_sequence, mock_search_contact,
        mock_contact, mock_postcall_sequence
    ):
        """Test flow skips when post-call sequence already exists."""
        mock_search_contact.return_value = mock_contact
        mock_search_sequence.return_value = mock_postcall_sequence

        result = postcall_maybe_handler_flow(
            email="test@example.com",
            first_name="John",
            business_name="Test Corp",
            call_date="2025-12-01T14:30:00Z"
        )

        assert result["status"] == "skipped"
        assert result["reason"] == "duplicate_postcall_sequence"
        assert result["existing_sequence_id"] == "sequence-456"

    @patch('campaigns.christmas_campaign.flows.postcall_maybe_handler.search_contact_by_email')
    @patch('campaigns.christmas_campaign.flows.postcall_maybe_handler.search_email_sequence_by_email')
    @patch('campaigns.christmas_campaign.flows.postcall_maybe_handler.create_postcall_sequence')
    @patch('campaigns.christmas_campaign.flows.postcall_maybe_handler.schedule_postcall_emails')
    def test_flow_continues_when_different_sequence_type_exists(
        self, mock_schedule, mock_create, mock_search_sequence, mock_search_contact,
        mock_contact, mock_lead_nurture_sequence, mock_postcall_sequence
    ):
        """Test flow continues when existing sequence is different type (e.g., Lead Nurture)."""
        mock_search_contact.return_value = mock_contact
        mock_search_sequence.return_value = mock_lead_nurture_sequence  # Different type
        mock_create.return_value = mock_postcall_sequence
        mock_schedule.return_value = []

        result = postcall_maybe_handler_flow(
            email="test@example.com",
            first_name="John",
            business_name="Test Corp",
            call_date="2025-12-01T14:30:00Z"
        )

        # Should create new post-call sequence despite existing lead nurture sequence
        assert result["status"] == "success"
        mock_create.assert_called_once()


# ==============================================================================
# Sequence Creation Tests
# ==============================================================================

class TestSequenceCreation:
    """Test post-call sequence creation."""

    @patch('campaigns.christmas_campaign.flows.postcall_maybe_handler.search_contact_by_email')
    @patch('campaigns.christmas_campaign.flows.postcall_maybe_handler.search_email_sequence_by_email')
    @patch('campaigns.christmas_campaign.flows.postcall_maybe_handler.create_postcall_sequence')
    @patch('campaigns.christmas_campaign.flows.postcall_maybe_handler.schedule_postcall_emails')
    def test_sequence_created_with_all_params(
        self, mock_schedule, mock_create, mock_search_sequence, mock_search_contact,
        mock_contact, mock_postcall_sequence
    ):
        """Test sequence creation with all parameters."""
        mock_search_contact.return_value = mock_contact
        mock_search_sequence.return_value = None
        mock_create.return_value = mock_postcall_sequence
        mock_schedule.return_value = []

        result = postcall_maybe_handler_flow(
            email="test@example.com",
            first_name="John",
            business_name="Test Corp",
            call_date="2025-12-01T14:30:00Z",
            call_outcome="Maybe",
            call_notes="Interested but needs budget approval",
            objections=["Price", "Timing"],
            follow_up_priority="High"
        )

        # Verify create_postcall_sequence called with correct params
        mock_create.assert_called_once_with(
            email="test@example.com",
            first_name="John",
            business_name="Test Corp",
            call_date="2025-12-01T14:30:00Z",
            call_outcome="Maybe",
            call_notes="Interested but needs budget approval",
            objections=["Price", "Timing"],
            follow_up_priority="High"
        )

        assert result["status"] == "success"
        assert result["sequence_id"] == "sequence-456"

    @patch('campaigns.christmas_campaign.flows.postcall_maybe_handler.search_contact_by_email')
    @patch('campaigns.christmas_campaign.flows.postcall_maybe_handler.search_email_sequence_by_email')
    @patch('campaigns.christmas_campaign.flows.postcall_maybe_handler.create_postcall_sequence')
    @patch('campaigns.christmas_campaign.flows.postcall_maybe_handler.schedule_postcall_emails')
    def test_sequence_created_with_minimal_params(
        self, mock_schedule, mock_create, mock_search_sequence, mock_search_contact,
        mock_contact, mock_postcall_sequence
    ):
        """Test sequence creation with only required parameters."""
        mock_search_contact.return_value = mock_contact
        mock_search_sequence.return_value = None
        mock_create.return_value = mock_postcall_sequence
        mock_schedule.return_value = []

        result = postcall_maybe_handler_flow(
            email="test@example.com",
            first_name="John",
            business_name="Test Corp",
            call_date="2025-12-01T14:30:00Z"
        )

        # Verify defaults are used
        call_args = mock_create.call_args
        assert call_args.kwargs["call_outcome"] == "Maybe"  # Default
        assert call_args.kwargs["call_notes"] is None
        assert call_args.kwargs["objections"] is None
        assert call_args.kwargs["follow_up_priority"] == "Medium"  # Default

        assert result["status"] == "success"


# ==============================================================================
# Email Scheduling Tests
# ==============================================================================

class TestEmailScheduling:
    """Test post-call email scheduling."""

    @patch('campaigns.christmas_campaign.flows.postcall_maybe_handler.search_contact_by_email')
    @patch('campaigns.christmas_campaign.flows.postcall_maybe_handler.search_email_sequence_by_email')
    @patch('campaigns.christmas_campaign.flows.postcall_maybe_handler.create_postcall_sequence')
    @patch('campaigns.christmas_campaign.flows.postcall_maybe_handler.schedule_postcall_emails')
    def test_schedule_postcall_emails_called_correctly(
        self, mock_schedule, mock_create, mock_search_sequence, mock_search_contact,
        mock_contact, mock_postcall_sequence
    ):
        """Test that schedule_postcall_emails is called with correct parameters."""
        mock_search_contact.return_value = mock_contact
        mock_search_sequence.return_value = None
        mock_create.return_value = mock_postcall_sequence
        mock_schedule.return_value = [
            {"email_number": 1, "flow_run_id": "run-1"},
            {"email_number": 2, "flow_run_id": "run-2"},
            {"email_number": 3, "flow_run_id": "run-3"}
        ]

        result = postcall_maybe_handler_flow(
            email="test@example.com",
            first_name="John",
            business_name="Test Corp",
            call_date="2025-12-01T14:30:00Z",
            call_notes="Test notes",
            objections=["Price"]
        )

        # Verify scheduling was called
        mock_schedule.assert_called_once()
        call_kwargs = mock_schedule.call_args.kwargs

        assert call_kwargs["email"] == "test@example.com"
        assert call_kwargs["first_name"] == "John"
        assert call_kwargs["business_name"] == "Test Corp"
        assert call_kwargs["call_date"] == "2025-12-01T14:30:00Z"
        assert call_kwargs["call_notes"] == "Test notes"
        assert call_kwargs["objections"] == ["Price"]
        assert call_kwargs["sequence_id"] == "sequence-456"

        # Verify result includes scheduled emails
        assert len(result["scheduled_emails"]) == 3


# ==============================================================================
# Result Structure Tests
# ==============================================================================

class TestResultStructure:
    """Test result dictionary structure."""

    @patch('campaigns.christmas_campaign.flows.postcall_maybe_handler.search_contact_by_email')
    @patch('campaigns.christmas_campaign.flows.postcall_maybe_handler.search_email_sequence_by_email')
    @patch('campaigns.christmas_campaign.flows.postcall_maybe_handler.create_postcall_sequence')
    @patch('campaigns.christmas_campaign.flows.postcall_maybe_handler.schedule_postcall_emails')
    def test_success_result_contains_all_fields(
        self, mock_schedule, mock_create, mock_search_sequence, mock_search_contact,
        mock_contact, mock_postcall_sequence
    ):
        """Test successful result contains all expected fields."""
        mock_search_contact.return_value = mock_contact
        mock_search_sequence.return_value = None
        mock_create.return_value = mock_postcall_sequence
        mock_schedule.return_value = []

        result = postcall_maybe_handler_flow(
            email="test@example.com",
            first_name="John",
            business_name="Test Corp",
            call_date="2025-12-01T14:30:00Z",
            call_outcome="Maybe"
        )

        # Verify all required fields present
        assert "status" in result
        assert "message" in result
        assert "email" in result
        assert "business_name" in result
        assert "call_date" in result
        assert "call_outcome" in result
        assert "contact_id" in result
        assert "sequence_id" in result
        assert "scheduled_emails" in result

        # Verify field values
        assert result["status"] == "success"
        assert result["email"] == "test@example.com"
        assert result["business_name"] == "Test Corp"
        assert result["call_outcome"] == "Maybe"
        assert result["contact_id"] == "contact-123"
        assert result["sequence_id"] == "sequence-456"


# ==============================================================================
# Error Handling Tests
# ==============================================================================

class TestErrorHandling:
    """Test error handling scenarios."""

    @patch('campaigns.christmas_campaign.flows.postcall_maybe_handler.search_contact_by_email')
    def test_handles_contact_search_exception(self, mock_search):
        """Test flow handles Notion API exception during contact search."""
        mock_search.side_effect = Exception("Notion API error")

        with pytest.raises(Exception, match="Notion API error"):
            postcall_maybe_handler_flow(
                email="test@example.com",
                first_name="John",
                business_name="Test Corp",
                call_date="2025-12-01T14:30:00Z"
            )

    @patch('campaigns.christmas_campaign.flows.postcall_maybe_handler.search_contact_by_email')
    @patch('campaigns.christmas_campaign.flows.postcall_maybe_handler.search_email_sequence_by_email')
    @patch('campaigns.christmas_campaign.flows.postcall_maybe_handler.create_postcall_sequence')
    def test_handles_sequence_creation_exception(
        self, mock_create, mock_search_sequence, mock_search_contact, mock_contact
    ):
        """Test flow handles exception during sequence creation."""
        mock_search_contact.return_value = mock_contact
        mock_search_sequence.return_value = None
        mock_create.side_effect = Exception("Failed to create sequence")

        with pytest.raises(Exception, match="Failed to create sequence"):
            postcall_maybe_handler_flow(
                email="test@example.com",
                first_name="John",
                business_name="Test Corp",
                call_date="2025-12-01T14:30:00Z"
            )

    @patch('campaigns.christmas_campaign.flows.postcall_maybe_handler.search_contact_by_email')
    @patch('campaigns.christmas_campaign.flows.postcall_maybe_handler.search_email_sequence_by_email')
    @patch('campaigns.christmas_campaign.flows.postcall_maybe_handler.create_postcall_sequence')
    @patch('campaigns.christmas_campaign.flows.postcall_maybe_handler.schedule_postcall_emails')
    def test_handles_scheduling_exception(
        self, mock_schedule, mock_create, mock_search_sequence, mock_search_contact,
        mock_contact, mock_postcall_sequence
    ):
        """Test flow handles exception during email scheduling."""
        mock_search_contact.return_value = mock_contact
        mock_search_sequence.return_value = None
        mock_create.return_value = mock_postcall_sequence
        mock_schedule.side_effect = Exception("Deployment not found")

        with pytest.raises(Exception, match="Deployment not found"):
            postcall_maybe_handler_flow(
                email="test@example.com",
                first_name="John",
                business_name="Test Corp",
                call_date="2025-12-01T14:30:00Z"
            )
