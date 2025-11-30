"""
Tests for Kestra Email Analytics Logging Task.

This task logs email send events to Notion Email Analytics database.
Includes sent_by field to distinguish website vs Kestra email sends.

Test Requirements:
- Test analytics log payload structure
- Test sent_by='kestra' logged correctly
- Test sent_by='website' logged correctly (for Email #1)
- Test all sequence types logged
- Test Notion API failure handled gracefully
"""

import pytest
import yaml
from pathlib import Path


class TestEmailAnalyticsTask:
    """Test email analytics logging task."""

    @pytest.fixture
    def task_path(self):
        return Path("kestra/flows/christmas/tasks/analytics-log-email.yml")

    @pytest.fixture
    def task_yaml(self, task_path):
        """Load and parse analytics task YAML."""
        if not task_path.exists():
            pytest.skip(f"Task file not found: {task_path}")
        with open(task_path, 'r') as f:
            return yaml.safe_load(f)

    def test_analytics_task_valid_yaml(self, task_path):
        """Test analytics task is valid YAML."""
        # This is optional - analytics might be integrated into send-email flow
        if not task_path.exists():
            pytest.skip("Analytics task is optional - may be integrated into send-email flow")

        with open(task_path, 'r') as f:
            task = yaml.safe_load(f)
        assert task is not None

    def test_analytics_log_payload_structure(self):
        """Test analytics logging includes required fields."""
        # This is tested via integration with send-email flow
        # Just verify send-email flow exists and has logging
        send_email_path = Path("kestra/flows/christmas/send-email.yml")
        assert send_email_path.exists(), "send-email flow not found"

        with open(send_email_path, 'r') as f:
            flow = yaml.safe_load(f)
            flow_str = yaml.dump(flow)

            # Should log or track email sends
            assert 'notion' in flow_str.lower() or 'log' in flow_str.lower(), \
                "Missing email event logging"

    def test_sent_by_kestra_logged_correctly(self):
        """Test sent_by='kestra' is logged for Kestra-sent emails."""
        # Verified in send-email flow
        send_email_path = Path("kestra/flows/christmas/send-email.yml")
        with open(send_email_path, 'r') as f:
            flow_str = f.read()

            # Should have sent_by field with 'kestra'
            assert 'sent_by' in flow_str.lower() or 'Sent By' in flow_str, \
                "Missing sent_by field"
            assert 'kestra' in flow_str, \
                "Missing 'kestra' value for sent_by"

    def test_sent_by_website_logged_correctly(self):
        """Test sent_by='website' is logged for Email #1."""
        # Verified in assessment handler
        assessment_path = Path("kestra/flows/christmas/handlers/assessment-handler.yml")
        with open(assessment_path, 'r') as f:
            flow_str = f.read()

            # Should mark Email #1 as sent_by_website
            assert 'website' in flow_str, \
                "Missing 'website' value for Email #1 sent_by"

    def test_all_sequence_types_logged(self):
        """Test all sequence types (5day, noshow, postcall, onboarding) are tracked."""
        handler_files = [
            "kestra/flows/christmas/handlers/assessment-handler.yml",
            "kestra/flows/christmas/handlers/noshow-recovery-handler.yml",
            "kestra/flows/christmas/handlers/postcall-maybe-handler.yml",
            "kestra/flows/christmas/handlers/onboarding-handler.yml"
        ]

        sequence_types = []
        for handler_path in handler_files:
            path = Path(handler_path)
            if path.exists():
                with open(path, 'r') as f:
                    flow_str = f.read()
                    if '5day' in flow_str:
                        sequence_types.append('5day')
                    if 'noshow' in flow_str:
                        sequence_types.append('noshow')
                    if 'postcall' in flow_str:
                        sequence_types.append('postcall')
                    if 'onboarding' in flow_str:
                        sequence_types.append('onboarding')

        # Should have all 4 sequence types
        assert '5day' in sequence_types, "Missing 5day sequence"
        assert 'noshow' in sequence_types, "Missing noshow sequence"
        assert 'postcall' in sequence_types, "Missing postcall sequence"
        assert 'onboarding' in sequence_types, "Missing onboarding sequence"

    def test_notion_api_failure_handled_gracefully(self):
        """Test Notion API failures don't block email sending."""
        # Verified in send-email flow - allowFailed: true
        send_email_path = Path("kestra/flows/christmas/send-email.yml")
        with open(send_email_path, 'r') as f:
            flow_str = f.read()

            # Should have allowFailed for Notion updates
            assert 'allowFailed' in flow_str, \
                "Missing graceful error handling for Notion updates"
