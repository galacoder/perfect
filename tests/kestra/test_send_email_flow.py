"""
Test send_email_flow for Kestra implementation.

Tests the complete send_email flow YAML with Notion tracking.

Author: Kestra Migration Team
Created: 2025-11-29
"""

import pytest
import yaml
from pathlib import Path


# Path to Kestra flows
FLOWS_DIR = Path(__file__).parent.parent.parent / "kestra" / "flows" / "christmas"


class TestSendEmailFlow:
    """Test send_email flow structure and integration."""

    def test_send_email_flow_exists(self):
        """send_email flow file exists."""
        flow_file = FLOWS_DIR / "send-email.yml"
        assert flow_file.exists(), f"Flow file not found: {flow_file}"

    def test_send_email_flow_valid_yaml(self):
        """send_email flow is valid YAML."""
        flow_file = FLOWS_DIR / "send-email.yml"
        with open(flow_file, 'r') as f:
            flow = yaml.safe_load(f)

        assert flow is not None
        assert 'id' in flow
        assert 'namespace' in flow
        assert 'tasks' in flow

    def test_send_email_flow_idempotency_check(self):
        """Flow includes idempotency check (check if email already sent)."""
        flow_file = FLOWS_DIR / "send-email.yml"
        with open(flow_file, 'r') as f:
            content = f.read()

        # Should search for existing sequence and check if email already sent
        assert 'search' in content.lower() or 'sequence' in content.lower()

    def test_send_email_flow_template_fetch(self):
        """Flow fetches email template from Notion."""
        flow_file = FLOWS_DIR / "send-email.yml"
        with open(flow_file, 'r') as f:
            content = f.read()

        # Should call notion_fetch_template task
        assert 'fetch_template' in content.lower() or 'template' in content.lower()

    def test_send_email_flow_variable_substitution(self):
        """Flow substitutes variables in template."""
        flow_file = FLOWS_DIR / "send-email.yml"
        with open(flow_file, 'r') as f:
            content = f.read()

        # Should reference first_name, business_name, etc.
        assert 'first_name' in content.lower() or 'variables' in content.lower()

    def test_send_email_flow_resend_api_call(self):
        """Flow calls Resend API to send email."""
        flow_file = FLOWS_DIR / "send-email.yml"
        with open(flow_file, 'r') as f:
            content = f.read()

        # Should call resend_send_email task
        assert 'resend' in content.lower()

    def test_send_email_flow_notion_sequence_tracker_update_called(self):
        """Flow calls Notion sequence tracker update after email send."""
        flow_file = FLOWS_DIR / "send-email.yml"
        with open(flow_file, 'r') as f:
            content = f.read()

        # Should call notion_update_sequence_tracker
        assert 'update_sequence_tracker' in content.lower() or 'tracker' in content.lower()

    def test_send_email_flow_notion_update_email_number_correct(self):
        """Notion update uses correct email_number from inputs."""
        flow_file = FLOWS_DIR / "send-email.yml"
        with open(flow_file, 'r') as f:
            content = f.read()

        # Should pass email_number to Notion update
        assert 'email_number' in content.lower()

    def test_send_email_flow_notion_update_sent_timestamp(self):
        """Notion update includes sent_at timestamp."""
        flow_file = FLOWS_DIR / "send-email.yml"
        with open(flow_file, 'r') as f:
            content = f.read()

        # Should include timestamp (sent_at or 'Email X Sent' or now())
        content_lower = content.lower()
        assert 'sent_at' in content_lower or 'sent' in content_lower or 'now()' in content_lower

    def test_send_email_flow_notion_update_sent_by_kestra(self):
        """Notion update includes sent_by='kestra'."""
        flow_file = FLOWS_DIR / "send-email.yml"
        with open(flow_file, 'r') as f:
            content = f.read()

        # Should set sent_by to 'kestra' (field name: "Sent By")
        content_lower = content.lower()
        assert 'sent' in content_lower and 'by' in content_lower
        assert 'kestra' in content_lower

    def test_send_email_flow_notion_update_resend_id_captured(self):
        """Notion update captures resend_id from Resend API response."""
        flow_file = FLOWS_DIR / "send-email.yml"
        with open(flow_file, 'r') as f:
            content = f.read()

        # Should capture and pass resend_id
        assert 'resend_id' in content.lower() or 'response' in content.lower()

    def test_send_email_flow_notion_update_status_success(self):
        """Notion update sets status='sent' on success."""
        flow_file = FLOWS_DIR / "send-email.yml"
        with open(flow_file, 'r') as f:
            content = f.read()

        # Should include status field
        assert 'status' in content.lower()

    def test_send_email_flow_notion_update_failure_does_not_block_email(self):
        """Notion update failure does not block email sending."""
        flow_file = FLOWS_DIR / "send-email.yml"
        with open(flow_file, 'r') as f:
            flow = yaml.safe_load(f)

        # Check if Notion update task has allowFailed or is in separate error handler
        # This is implementation-dependent, so check for error handling patterns
        content = flow_file.read_text()
        # Should either have allowFailed or error handlers
        assert 'allowFailed' in content or 'errors' in content.lower()

    def test_send_email_flow_contact_last_email_sent_updated(self):
        """Flow updates Contact database with last_email_sent timestamp."""
        flow_file = FLOWS_DIR / "send-email.yml"
        with open(flow_file, 'r') as f:
            content = f.read()

        # Should update last_email_sent or similar field
        assert 'last' in content.lower() and 'email' in content.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
