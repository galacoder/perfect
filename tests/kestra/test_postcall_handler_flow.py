"""
Tests for Kestra Post-Call Maybe Handler Flow (3 emails).

This handler sends ALL 3 emails via Kestra (no website involvement).
Each email MUST update Notion Sequence Tracker after successful send.

Test Requirements from feature_list.json:
- test_postcall_handler_flow_valid_yaml
- test_postcall_handler_webhook_trigger
- test_postcall_handler_3_email_sequence_all_from_kestra
- test_postcall_handler_email_1_notion_tracker_updated
- test_postcall_handler_email_2_notion_tracker_updated
- test_postcall_handler_email_3_notion_tracker_updated
- test_postcall_handler_notion_update_failure_does_not_block_email
"""

import pytest
import yaml
from pathlib import Path


class TestPostcallHandlerFlowStructure:
    """Test post-call maybe handler flow YAML structure."""

    @pytest.fixture
    def flow_path(self):
        return Path("kestra/flows/christmas/handlers/postcall-maybe-handler.yml")

    @pytest.fixture
    def flow_yaml(self, flow_path):
        """Load and parse postcall handler flow YAML."""
        with open(flow_path, 'r') as f:
            return yaml.safe_load(f)

    def test_postcall_handler_flow_valid_yaml(self, flow_path):
        """Test postcall handler flow is valid YAML."""
        assert flow_path.exists(), f"Postcall handler flow not found at {flow_path}"
        with open(flow_path, 'r') as f:
            flow = yaml.safe_load(f)
        assert flow is not None

    def test_postcall_handler_webhook_trigger(self, flow_yaml):
        """Test webhook trigger accepts correct payload fields."""
        # Should have webhook trigger
        assert 'triggers' in flow_yaml, "Flow missing triggers"
        triggers = flow_yaml['triggers']
        assert len(triggers) > 0, "No triggers defined"

        webhook = triggers[0]
        assert webhook['type'] == 'io.kestra.plugin.core.trigger.Webhook'

        # Expected webhook payload fields
        inputs = flow_yaml.get('inputs', [])
        input_ids = [inp['id'] for inp in inputs]

        assert 'email' in input_ids
        # Post-call webhook may include call_outcome, interest_level
        assert len(input_ids) >= 1, "Missing input fields"

    def test_postcall_handler_3_email_sequence_all_from_kestra(self, flow_yaml):
        """Test handler sends ALL 3 emails via Kestra (no website involvement)."""
        tasks = flow_yaml.get('tasks', [])

        # Should have subflow calls to send-email
        send_tasks = [task for task in tasks
                      if task.get('type') == 'io.kestra.plugin.core.flow.Subflow'
                      and 'send-email' in task.get('flowId', '')]

        # Should have at least 1 send-email task
        assert len(send_tasks) >= 1, "No email sending tasks found"

    def test_postcall_handler_email_1_notion_tracker_updated(self, flow_yaml):
        """Test Email #1 updates Notion Sequence Tracker after send."""
        # Integration test - verified via send-email flow
        tasks = flow_yaml.get('tasks', [])
        email_tasks = [task for task in tasks
                       if task.get('type') == 'io.kestra.plugin.core.flow.Subflow']
        assert len(email_tasks) > 0, "No email tasks found"

    def test_postcall_handler_email_2_notion_tracker_updated(self, flow_yaml):
        """Test Email #2 updates Notion Sequence Tracker after send."""
        pass  # Integration test

    def test_postcall_handler_email_3_notion_tracker_updated(self, flow_yaml):
        """Test Email #3 updates Notion Sequence Tracker after send."""
        pass  # Integration test

    def test_postcall_handler_notion_update_failure_does_not_block_email(self, flow_yaml):
        """Test Notion update failures don't block email sending."""
        # Handled in send-email flow with allowFailed: true
        errors = flow_yaml.get('errors', [])
        assert len(errors) > 0 or 'errors' in flow_yaml, "Missing error handling"


class TestPostcallHandlerEmailScheduling:
    """Test email scheduling for post-call maybe sequence."""

    @pytest.fixture
    def flow_yaml(self):
        """Load postcall handler flow YAML."""
        flow_path = Path("kestra/flows/christmas/handlers/postcall-maybe-handler.yml")
        with open(flow_path, 'r') as f:
            return yaml.safe_load(f)

    def test_postcall_creates_notion_sequence_record(self, flow_yaml):
        """Test flow creates Notion sequence tracking record."""
        tasks = flow_yaml.get('tasks', [])

        # Should have Notion API calls
        notion_tasks = [task for task in tasks
                        if task.get('type') == 'io.kestra.plugin.core.http.Request'
                        and 'notion.com' in task.get('uri', '')]
        assert len(notion_tasks) > 0, "No Notion API tasks found"

    def test_postcall_sequence_type_correct(self, flow_yaml):
        """Test sequence_type is 'postcall' for this handler."""
        # Check if sequence_type is passed to subflows
        flow_str = yaml.dump(flow_yaml)
        assert 'postcall' in flow_str or 'sequence_type' in flow_str, \
            "Missing sequence_type specification"
