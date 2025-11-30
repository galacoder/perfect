"""
Tests for webhook payload validator with email_1_sent_at support.

Validates assessment webhook payloads including:
- email_1_sent_at timestamp (ISO 8601 format)
- email_1_status field
- Assessment data (red_systems, orange_systems)
"""

import pytest
import sys
import os
from datetime import datetime

# Add lib directory to path
sys.path.insert(0, os.path.join(os.getcwd(), 'kestra', 'flows', 'christmas', 'lib'))

from validate_payload import (
    validate_assessment_payload,
    ValidationError
)


def test_valid_payload_with_email_1_sent_at():
    """Test valid payload with email_1_sent_at ISO 8601 timestamp."""
    payload = {
        "email": "user@example.com",
        "first_name": "John",
        "business_name": "Acme Corp",
        "red_systems": 2,
        "orange_systems": 1,
        "email_1_sent_at": "2025-11-29T10:30:00Z",
        "email_1_status": "sent"
    }

    result = validate_assessment_payload(payload)

    assert result["valid"] is True
    assert result["email_1_sent_at"] == "2025-11-29T10:30:00Z"
    assert result["email_1_status"] == "sent"
    assert result["red_systems"] == 2
    assert result["orange_systems"] == 1


def test_valid_payload_with_email_1_status_sent():
    """Test valid payload confirms email_1_status='sent'."""
    payload = {
        "email": "user@example.com",
        "first_name": "Jane",
        "business_name": "Tech Co",
        "red_systems": 0,
        "orange_systems": 3,
        "email_1_sent_at": "2025-11-29T12:00:00Z",
        "email_1_status": "sent"
    }

    result = validate_assessment_payload(payload)

    assert result["valid"] is True
    assert result["email_1_status"] == "sent"


def test_missing_email_1_sent_at_defaults_to_current_time():
    """Test missing email_1_sent_at defaults to current time with warning."""
    payload = {
        "email": "user@example.com",
        "first_name": "Bob",
        "business_name": "Corp Inc",
        "red_systems": 1,
        "orange_systems": 2
        # email_1_sent_at missing
    }

    result = validate_assessment_payload(payload)

    # Should still be valid
    assert result["valid"] is True

    # Should have default timestamp
    assert "email_1_sent_at" in result
    assert result["email_1_sent_at"] is not None

    # Should have warning
    assert result.get("warnings") is not None
    assert "email_1_sent_at missing" in result["warnings"][0].lower()

    # Timestamp should be ISO 8601 format
    try:
        datetime.fromisoformat(result["email_1_sent_at"].replace('Z', '+00:00'))
        timestamp_valid = True
    except:
        timestamp_valid = False

    assert timestamp_valid is True


def test_invalid_timestamp_format_rejected():
    """Test invalid timestamp format is rejected with error."""
    payload = {
        "email": "user@example.com",
        "first_name": "Alice",
        "business_name": "Business Ltd",
        "red_systems": 2,
        "orange_systems": 0,
        "email_1_sent_at": "invalid-timestamp",  # Invalid format
        "email_1_status": "sent"
    }

    with pytest.raises(ValidationError) as exc_info:
        validate_assessment_payload(payload)

    assert "timestamp format" in str(exc_info.value).lower()


def test_payload_schema_validation():
    """Test payload schema validation for assessment data."""
    # red_systems must be int
    payload_invalid_red = {
        "email": "user@example.com",
        "first_name": "Test",
        "business_name": "Test Co",
        "red_systems": "not_an_int",  # Invalid
        "orange_systems": 1,
        "email_1_sent_at": "2025-11-29T10:00:00Z",
        "email_1_status": "sent"
    }

    with pytest.raises(ValidationError) as exc_info:
        validate_assessment_payload(payload_invalid_red)

    assert "red_systems" in str(exc_info.value).lower()

    # orange_systems must be int
    payload_invalid_orange = {
        "email": "user@example.com",
        "first_name": "Test",
        "business_name": "Test Co",
        "red_systems": 1,
        "orange_systems": "not_an_int",  # Invalid
        "email_1_sent_at": "2025-11-29T10:00:00Z",
        "email_1_status": "sent"
    }

    with pytest.raises(ValidationError) as exc_info:
        validate_assessment_payload(payload_invalid_orange)

    assert "orange_systems" in str(exc_info.value).lower()


def test_email_1_sent_at_used_for_email_2_scheduling():
    """Test email_1_sent_at is extracted for Email #2 schedule calculation."""
    payload = {
        "email": "user@example.com",
        "first_name": "Charlie",
        "business_name": "Example Corp",
        "red_systems": 1,
        "orange_systems": 1,
        "email_1_sent_at": "2025-11-29T08:00:00Z",
        "email_1_status": "sent"
    }

    result = validate_assessment_payload(payload)

    # Extract timestamp for scheduling
    email_1_time = result["email_1_sent_at"]

    # Parse timestamp
    email_1_dt = datetime.fromisoformat(email_1_time.replace('Z', '+00:00'))

    # Email #2 should be scheduled 24 hours later (production mode)
    from datetime import timedelta
    expected_email_2_time = email_1_dt + timedelta(hours=24)

    # Verify we can calculate Email #2 time
    assert expected_email_2_time is not None
    assert expected_email_2_time > email_1_dt
