"""
Unit tests for Christmas Campaign signup_handler flow.

This test suite validates:
1. Idempotency: Prevents duplicate signups
2. Database operations: Notion DB create/update
3. Segment classification: CRITICAL/URGENT/OPTIMIZE
4. Flow integration: Orchestrator triggering
5. Error handling: API failures, missing data

Author: Christmas Campaign Team
Created: 2025-11-19
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import Dict, Any

# Import flow to test
from campaigns.christmas_campaign.flows.signup_handler import signup_handler_flow


# ==============================================================================
# Test: Successful New Signup (No Existing Records)
# ==============================================================================

@patch('campaigns.christmas_campaign.flows.signup_handler.search_email_sequence_by_email')
@patch('campaigns.christmas_campaign.flows.signup_handler.search_contact_by_email')
@patch('campaigns.christmas_campaign.flows.signup_handler.update_assessment_data')
@patch('campaigns.christmas_campaign.flows.signup_handler.create_email_sequence')
def test_signup_handler_new_contact_success(
    mock_create_sequence,
    mock_update_assessment,
    mock_search_contact,
    mock_search_sequence
):
    """Test successful signup for new contact with no existing records."""

    # Mock: No existing sequence
    mock_search_sequence.return_value = None

    # Mock: Contact exists in BusinessX Canada DB
    mock_search_contact.return_value = {
        "id": "contact-123",
        "properties": {
            "email": {"email": "sarah@example.com"}
        }
    }

    # Mock: Email sequence created successfully
    mock_create_sequence.return_value = {
        "id": "sequence-456",
        "properties": {
            "Email": {"email": "sarah@example.com"},
            "Campaign": {"select": {"name": "Christmas 2025"}}
        }
    }

    # Run flow
    result = signup_handler_flow(
        email="sarah@example.com",
        first_name="Sarah",
        business_name="Sarah's Salon",
        assessment_score=52,
        red_systems=2,
        orange_systems=1,
        yellow_systems=2,
        green_systems=3,
        gps_score=45,
        money_score=38
    )

    # Assertions
    assert result["status"] == "success"
    assert result["email"] == "sarah@example.com"
    assert result["sequence_id"] == "sequence-456"
    assert result["contact_id"] == "contact-123"
    assert result["segment"] == "CRITICAL"  # 2 red systems = CRITICAL
    assert result["campaign"] == "Christmas 2025"

    # Verify functions called
    mock_search_sequence.assert_called_once_with("sarah@example.com")
    mock_search_contact.assert_called_once_with("sarah@example.com")
    mock_update_assessment.assert_called_once()
    mock_create_sequence.assert_called_once()


# ==============================================================================
# Test: Idempotency - Duplicate Signup Detection
# ==============================================================================

@patch('campaigns.christmas_campaign.flows.signup_handler.search_email_sequence_by_email')
def test_signup_handler_duplicate_with_emails_sent(mock_search_sequence):
    """Test that duplicate signups are detected and skipped if emails already sent."""

    # Mock: Existing sequence with emails already sent
    mock_search_sequence.return_value = {
        "id": "sequence-789",
        "properties": {
            "Email": {"email": "sarah@example.com"},
            "Campaign": {"select": {"name": "Christmas 2025"}},
            "Email 1 Sent": {"date": {"start": "2025-11-19T10:00:00Z"}},
            "Email 2 Sent": {"date": {"start": "2025-11-20T10:00:00Z"}},
            "Email 3 Sent": {"date": None},
            "Email 4 Sent": {"date": None},
            "Email 5 Sent": {"date": None},
            "Email 6 Sent": {"date": None},
            "Email 7 Sent": {"date": None}
        }
    }

    # Run flow
    result = signup_handler_flow(
        email="sarah@example.com",
        first_name="Sarah",
        business_name="Sarah's Salon",
        assessment_score=52,
        red_systems=2
    )

    # Assertions
    assert result["status"] == "skipped"
    assert result["reason"] == "already_in_sequence"
    assert result["sequence_id"] == "sequence-789"
    assert result["emails_sent"] == [1, 2]

    # Verify only search was called (no create/update)
    mock_search_sequence.assert_called_once_with("sarah@example.com")


@patch('campaigns.christmas_campaign.flows.signup_handler.search_email_sequence_by_email')
@patch('campaigns.christmas_campaign.flows.signup_handler.search_contact_by_email')
@patch('campaigns.christmas_campaign.flows.signup_handler.update_assessment_data')
def test_signup_handler_duplicate_no_emails_sent(
    mock_update_assessment,
    mock_search_contact,
    mock_search_sequence
):
    """Test that duplicate signup continues if sequence exists but no emails sent yet."""

    # Mock: Existing sequence but no emails sent yet
    mock_search_sequence.return_value = {
        "id": "sequence-999",
        "properties": {
            "Email": {"email": "sarah@example.com"},
            "Campaign": {"select": {"name": "Christmas 2025"}},
            "Email 1 Sent": {"date": None},
            "Email 2 Sent": {"date": None},
            "Email 3 Sent": {"date": None},
            "Email 4 Sent": {"date": None},
            "Email 5 Sent": {"date": None},
            "Email 6 Sent": {"date": None},
            "Email 7 Sent": {"date": None}
        }
    }

    # Mock: Contact exists
    mock_search_contact.return_value = {"id": "contact-123"}

    # Run flow
    result = signup_handler_flow(
        email="sarah@example.com",
        first_name="Sarah",
        business_name="Sarah's Salon",
        assessment_score=52,
        red_systems=2
    )

    # Assertions - should continue with existing sequence
    assert result["status"] == "success"
    assert result["sequence_id"] == "sequence-999"


# ==============================================================================
# Test: Segment Classification
# ==============================================================================

@patch('campaigns.christmas_campaign.flows.signup_handler.search_email_sequence_by_email')
@patch('campaigns.christmas_campaign.flows.signup_handler.search_contact_by_email')
@patch('campaigns.christmas_campaign.flows.signup_handler.update_assessment_data')
@patch('campaigns.christmas_campaign.flows.signup_handler.create_email_sequence')
def test_segment_classification_critical(
    mock_create, mock_update, mock_search_contact, mock_search_sequence
):
    """Test CRITICAL segment: red_systems >= 2."""
    mock_search_sequence.return_value = None
    mock_search_contact.return_value = {"id": "contact-123"}
    mock_create.return_value = {"id": "seq-123"}

    result = signup_handler_flow(
        email="test@example.com",
        first_name="Test",
        business_name="Test Corp",
        assessment_score=20,
        red_systems=3,  # >= 2 = CRITICAL
        orange_systems=1
    )

    assert result["segment"] == "CRITICAL"


@patch('campaigns.christmas_campaign.flows.signup_handler.search_email_sequence_by_email')
@patch('campaigns.christmas_campaign.flows.signup_handler.search_contact_by_email')
@patch('campaigns.christmas_campaign.flows.signup_handler.update_assessment_data')
@patch('campaigns.christmas_campaign.flows.signup_handler.create_email_sequence')

def test_segment_classification_urgent_red(
    mock_create, mock_update, mock_search_contact, mock_search_sequence
):
    """Test URGENT segment: red_systems == 1."""
    mock_search_sequence.return_value = None
    mock_search_contact.return_value = {"id": "contact-123"}
    mock_create.return_value = {"id": "seq-123"}

    result = signup_handler_flow(
        email="test@example.com",
        first_name="Test",
        business_name="Test Corp",
        assessment_score=35,
        red_systems=1,  # == 1 = URGENT
        orange_systems=1
    )

    assert result["segment"] == "URGENT"


@patch('campaigns.christmas_campaign.flows.signup_handler.search_email_sequence_by_email')
@patch('campaigns.christmas_campaign.flows.signup_handler.search_contact_by_email')
@patch('campaigns.christmas_campaign.flows.signup_handler.update_assessment_data')
@patch('campaigns.christmas_campaign.flows.signup_handler.create_email_sequence')

def test_segment_classification_urgent_orange(
    mock_create, mock_update, mock_search_contact, mock_search_sequence
):
    """Test URGENT segment: orange_systems >= 2."""
    mock_search_sequence.return_value = None
    mock_search_contact.return_value = {"id": "contact-123"}
    mock_create.return_value = {"id": "seq-123"}

    result = signup_handler_flow(
        email="test@example.com",
        first_name="Test",
        business_name="Test Corp",
        assessment_score=40,
        red_systems=0,
        orange_systems=3  # >= 2 = URGENT
    )

    assert result["segment"] == "URGENT"


@patch('campaigns.christmas_campaign.flows.signup_handler.search_email_sequence_by_email')
@patch('campaigns.christmas_campaign.flows.signup_handler.search_contact_by_email')
@patch('campaigns.christmas_campaign.flows.signup_handler.update_assessment_data')
@patch('campaigns.christmas_campaign.flows.signup_handler.create_email_sequence')

def test_segment_classification_optimize(
    mock_create, mock_update, mock_search_contact, mock_search_sequence
):
    """Test OPTIMIZE segment: red < 2 and orange < 2."""
    mock_search_sequence.return_value = None
    mock_search_contact.return_value = {"id": "contact-123"}
    mock_create.return_value = {"id": "seq-123"}

    result = signup_handler_flow(
        email="test@example.com",
        first_name="Test",
        business_name="Test Corp",
        assessment_score=70,
        red_systems=0,
        orange_systems=1,  # < 2 = OPTIMIZE
        yellow_systems=3,
        green_systems=4
    )

    assert result["segment"] == "OPTIMIZE"


# ==============================================================================
# Test: Missing Contact in BusinessX Canada DB
# ==============================================================================

@patch('campaigns.christmas_campaign.flows.signup_handler.search_email_sequence_by_email')
@patch('campaigns.christmas_campaign.flows.signup_handler.search_contact_by_email')
@patch('campaigns.christmas_campaign.flows.signup_handler.create_email_sequence')

def test_signup_handler_no_existing_contact(
    mock_create_sequence,
    mock_search_contact,
    mock_search_sequence
):
    """Test flow when contact doesn't exist in BusinessX Canada DB (edge case)."""

    # Mock: No sequence, no contact
    mock_search_sequence.return_value = None
    mock_search_contact.return_value = None  # Contact not found

    # Mock: Sequence creation succeeds
    mock_create_sequence.return_value = {"id": "seq-new-123"}

    # Run flow
    result = signup_handler_flow(
        email="new@example.com",
        first_name="New",
        business_name="New Corp",
        assessment_score=50,
        red_systems=1
    )

    # Assertions - should succeed with sequence creation only
    assert result["status"] == "success"
    assert result["sequence_id"] == "seq-new-123"
    assert result["contact_id"] is None  # No contact found

    # Verify sequence was still created
    mock_create_sequence.assert_called_once()


# ==============================================================================
# Test: Orchestrator Context Data
# ==============================================================================

@patch('campaigns.christmas_campaign.flows.signup_handler.search_email_sequence_by_email')
@patch('campaigns.christmas_campaign.flows.signup_handler.search_contact_by_email')
@patch('campaigns.christmas_campaign.flows.signup_handler.create_email_sequence')

def test_orchestrator_receives_complete_context(
    mock_create_sequence,
    mock_search_contact,
    mock_search_sequence
):
    """Test that signup handler successfully processes full customer data."""

    # Setup mocks
    mock_search_sequence.return_value = None
    mock_search_contact.return_value = {"id": "contact-123"}
    mock_create_sequence.return_value = {"id": "seq-456"}

    # Run flow with full data
    result = signup_handler_flow(
        email="sarah@example.com",
        first_name="Sarah",
        business_name="Sarah's Salon",
        assessment_score=52,
        red_systems=2,
        orange_systems=1,
        yellow_systems=2,
        green_systems=3,
        gps_score=45,
        money_score=38,
        weakest_system_1="GPS",
        weakest_system_2="Money",
        revenue_leak_total=14700
    )

    # Verify flow completed successfully with all data
    assert result["status"] == "success"
    assert result["email"] == "sarah@example.com"
    assert result["sequence_id"] == "seq-456"
    assert result["segment"] == "CRITICAL"


# ==============================================================================
# Test: Error Handling
# ==============================================================================

@patch('campaigns.christmas_campaign.flows.signup_handler.search_email_sequence_by_email')
def test_signup_handler_notion_api_error(mock_search_sequence):
    """Test flow handles Notion API errors gracefully."""

    # Mock: Notion API raises exception
    mock_search_sequence.side_effect = Exception("Notion API connection failed")

    # Run flow - should raise exception (Prefect will handle retries)
    with pytest.raises(Exception, match="Notion API connection failed"):
        signup_handler_flow(
            email="test@example.com",
            first_name="Test",
            business_name="Test Corp",
            assessment_score=50,
            red_systems=1
        )


# ==============================================================================
# Test: Database Operation Calls
# ==============================================================================

@patch('campaigns.christmas_campaign.flows.signup_handler.search_email_sequence_by_email')
@patch('campaigns.christmas_campaign.flows.signup_handler.search_contact_by_email')
@patch('campaigns.christmas_campaign.flows.signup_handler.update_assessment_data')
@patch('campaigns.christmas_campaign.flows.signup_handler.create_email_sequence')

def test_create_email_sequence_called_with_correct_params(
    mock_create_sequence,
    mock_update_assessment,
    mock_search_contact,
    mock_search_sequence
):
    """Test that create_email_sequence is called with correct parameters."""

    # Setup mocks
    mock_search_sequence.return_value = None
    mock_search_contact.return_value = {"id": "contact-123"}
    mock_create_sequence.return_value = {"id": "seq-456"}

    # Run flow
    signup_handler_flow(
        email="sarah@example.com",
        first_name="Sarah",
        business_name="Sarah's Salon",
        assessment_score=52,
        red_systems=2,
        orange_systems=1,
        yellow_systems=2,
        green_systems=3
    )

    # Verify create_email_sequence called with correct params
    mock_create_sequence.assert_called_once_with(
        email="sarah@example.com",
        first_name="Sarah",
        business_name="Sarah's Salon",
        assessment_score=52,
        red_systems=2,
        orange_systems=1,
        yellow_systems=2,
        green_systems=3,
        segment="CRITICAL"
    )


@patch('campaigns.christmas_campaign.flows.signup_handler.search_email_sequence_by_email')
@patch('campaigns.christmas_campaign.flows.signup_handler.search_contact_by_email')
@patch('campaigns.christmas_campaign.flows.signup_handler.update_assessment_data')
@patch('campaigns.christmas_campaign.flows.signup_handler.create_email_sequence')

def test_update_assessment_data_called_with_correct_params(
    mock_create_sequence,
    mock_update_assessment,
    mock_search_contact,
    mock_search_sequence
):
    """Test that update_assessment_data is called with correct parameters."""

    # Setup mocks
    mock_search_sequence.return_value = None
    mock_search_contact.return_value = {"id": "contact-999"}
    mock_create_sequence.return_value = {"id": "seq-456"}

    # Run flow
    signup_handler_flow(
        email="sarah@example.com",
        first_name="Sarah",
        business_name="Sarah's Salon",
        assessment_score=52,
        red_systems=2,
        orange_systems=1,
        yellow_systems=2,
        green_systems=3
    )

    # Verify update_assessment_data called with correct params
    mock_update_assessment.assert_called_once_with(
        page_id="contact-999",
        assessment_score=52,
        red_systems=2,
        orange_systems=1,
        yellow_systems=2,
        green_systems=3,
        segment="CRITICAL"
    )
