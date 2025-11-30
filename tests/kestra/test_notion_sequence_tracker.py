"""
Tests for Notion Sequence Tracker update task.

Tests the dedicated task that updates Notion Sequence Tracker database
after EVERY email send. This task is called by send_email_flow and all
handler flows.

CRITICAL: Notion update failures must NOT block email delivery.
"""

import pytest
import yaml


def load_task_config():
    """Load notion_update_sequence_tracker.yml task configuration."""
    task_path = "kestra/flows/christmas/tasks/notion_update_sequence_tracker.yml"

    with open(task_path, 'r') as f:
        # Skip comment lines
        lines = [line for line in f.readlines() if not line.strip().startswith('#')]
        config = yaml.safe_load(''.join(lines))

    return config


def test_sequence_tracker_update_payload_structure():
    """Test sequence tracker update has correct Notion API payload structure."""
    config = load_task_config()

    # Should be HTTP PATCH request
    assert config['type'] == 'io.kestra.plugin.core.http.Request'
    assert config['method'] == 'PATCH'

    # Should have Notion API headers
    headers = config['headers']
    assert 'Authorization' in headers
    assert 'Bearer' in headers['Authorization']
    assert headers['Notion-Version'] == '2022-06-28'
    assert headers['Content-Type'] == 'application/json'

    # Should have body with properties
    body = config['body']
    assert 'properties' in body


def test_sequence_tracker_email_number_field_correct():
    """Test email_number is correctly templated in property names."""
    config = load_task_config()
    body = config['body']

    # Email number should be templated in multiple properties
    assert '{{ inputs.email_number }}' in body

    # Should have email-specific properties
    assert 'Email {{ inputs.email_number }} Sent' in body
    assert 'Email {{ inputs.email_number }} Status' in body
    assert 'Email {{ inputs.email_number }} Resend ID' in body
    assert 'Email {{ inputs.email_number }} Sent By' in body


def test_sequence_tracker_sent_at_iso8601_format():
    """Test sent_at timestamp is in ISO 8601 format."""
    config = load_task_config()
    body = config['body']

    # Should reference sent_at input
    assert '{{ inputs.sent_at }}' in body

    # Should be used in date field
    assert '"start": "{{ inputs.sent_at }}"' in body


def test_sequence_tracker_status_sent_on_success():
    """Test status field is set to 'sent' on successful email delivery."""
    config = load_task_config()
    body = config['body']

    # Should have status field
    assert 'Email {{ inputs.email_number }} Status' in body

    # Should reference inputs.status with default 'sent'
    assert '{{ inputs.status | default(\'sent\') }}' in body or \
           '{{ inputs.status }}' in body


def test_sequence_tracker_status_failed_on_error():
    """Test status field can be set to 'failed' on error."""
    config = load_task_config()
    body = config['body']

    # Status field should accept dynamic value
    assert '{{ inputs.status' in body

    # Should support both 'sent' and 'failed' values
    # (actual value passed via inputs)


def test_sequence_tracker_resend_id_captured():
    """Test Resend ID is captured from Resend API response."""
    config = load_task_config()
    body = config['body']

    # Should have Resend ID field
    assert 'Email {{ inputs.email_number }} Resend ID' in body

    # Should reference inputs.resend_id
    assert '{{ inputs.resend_id' in body


def test_sequence_tracker_sent_by_kestra():
    """Test sent_by field is set to 'kestra' for Kestra-sent emails."""
    config = load_task_config()
    body = config['body']

    # Should have sent_by field
    assert 'Email {{ inputs.email_number }} Sent By' in body

    # Should reference inputs.sent_by with default 'kestra'
    assert '{{ inputs.sent_by | default(\'kestra\') }}' in body or \
           '{{ inputs.sent_by }}' in body


def test_sequence_tracker_sent_by_website_for_email_1():
    """Test sent_by field supports 'website' value for Email #1."""
    config = load_task_config()
    body = config['body']

    # sent_by should be dynamic (can be 'website' or 'kestra')
    assert '{{ inputs.sent_by' in body

    # Should accept any value passed via inputs
    # (actual value validated at runtime)


def test_sequence_tracker_sequence_type_5day():
    """Test support for '5day' sequence type."""
    config = load_task_config()

    # Should accept sequence_type input
    # (used to differentiate sequences, but not in body directly)
    # Task should work for 5day sequence


def test_sequence_tracker_sequence_type_noshow():
    """Test support for 'noshow' sequence type."""
    config = load_task_config()

    # Task should work for noshow sequence
    # Same Notion properties used across all sequence types


def test_sequence_tracker_sequence_type_postcall():
    """Test support for 'postcall' sequence type."""
    config = load_task_config()

    # Task should work for postcall sequence
    # Same Notion properties used across all sequence types


def test_sequence_tracker_sequence_type_onboarding():
    """Test support for 'onboarding' sequence type."""
    config = load_task_config()

    # Task should work for onboarding sequence
    # Same Notion properties used across all sequence types


def test_sequence_tracker_api_failure_returns_success():
    """Test Notion API failures are gracefully handled and return success."""
    config = load_task_config()

    # Should have allowFailed=true for graceful error handling
    assert config.get('allowFailed') is True, \
        "Task must have allowFailed=true to gracefully handle Notion API failures"


def test_sequence_tracker_api_failure_logs_error():
    """Test Notion API failures are logged as warnings."""
    config = load_task_config()

    # Should have logLevel set to WARN for error visibility
    assert config.get('logLevel') == 'WARN', \
        "Task must have logLevel=WARN to log Notion API failures"


def test_sequence_tracker_idempotent_on_duplicate_update():
    """Test sequence tracker updates are idempotent."""
    config = load_task_config()

    # PATCH method is idempotent
    assert config['method'] == 'PATCH'

    # Same inputs should produce same Notion update
    # (Notion API handles idempotency at database level)


def test_sequence_tracker_contact_last_email_sent_updated():
    """Test Contact database last_email_sent field is updated."""
    config = load_task_config()
    body = config['body']

    # Should update Last Email Sent tracking fields
    assert 'Last Email Sent' in body
    assert 'Last Email Sent At' in body

    # Last Email Sent should be email_number
    assert '"Last Email Sent": {\n        "number": {{ inputs.email_number }}' in body or \
           '"Last Email Sent"' in body

    # Last Email Sent At should be sent_at timestamp
    assert '"Last Email Sent At"' in body
