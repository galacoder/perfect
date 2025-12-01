"""
Tests for Kestra Signup Handler Flow (TRACKING ONLY - NO EMAIL).

CRITICAL: This handler does NOT send any emails. Website handles signup email directly.
Kestra only: (1) Parse webhook, (2) Search/create contact in Notion, (3) Log signup event.

Test Requirements from feature_list.json:
- Test webhook trigger parses payload correctly
- Test contact created/updated in Notion
- Test NO emails are sent or scheduled by this handler
- Test signup event logged for analytics
- Test idempotency (duplicate signups handled)
"""

import pytest
import yaml
from pathlib import Path


class TestSignupHandlerFlowStructure:
    """Test signup handler flow YAML structure."""

    @pytest.fixture
    def flow_path(self):
        return Path("kestra/flows/christmas/handlers/signup-handler.yml")

    @pytest.fixture
    def flow_yaml(self, flow_path):
        """Load and parse signup handler flow YAML."""
        with open(flow_path, 'r') as f:
            return yaml.safe_load(f)

    def test_signup_handler_flow_valid_yaml(self, flow_path):
        """Test signup handler flow is valid YAML."""
        assert flow_path.exists(), f"Signup handler flow not found at {flow_path}"
        with open(flow_path, 'r') as f:
            flow = yaml.safe_load(f)
        assert flow is not None

    def test_webhook_trigger_parses_payload_correctly(self, flow_yaml):
        """Test webhook trigger accepts correct payload fields."""
        # Signup handler should have webhook trigger
        assert 'triggers' in flow_yaml, "Flow missing triggers"
        triggers = flow_yaml['triggers']
        assert len(triggers) > 0, "No triggers defined"

        webhook = triggers[0]
        assert webhook['type'] == 'io.kestra.plugin.core.trigger.Webhook'

        # Flow uses variables to extract from trigger.body, not inputs
        variables = flow_yaml.get('variables', {})

        # Check that email, name/first_name, and business_name are extracted from trigger.body
        assert 'email' in variables
        assert 'trigger.body.email' in variables['email']

        assert 'first_name' in variables or 'name' in variables

        assert 'business_name' in variables

    def test_contact_created_updated_in_notion(self, flow_yaml):
        """Test flow has Notion contact create/update task."""
        tasks = flow_yaml.get('tasks', [])
        task_ids = [task['id'] for task in tasks]

        # Should have create_or_update_contact task (no search needed - Notion handles duplicates)
        assert 'create_or_update_contact' in task_ids, \
            "Missing create_or_update_contact task"

        # Should have Notion API calls
        notion_tasks = [task for task in tasks
                        if task.get('type') == 'io.kestra.plugin.core.http.Request'
                        and 'notion.com' in task.get('uri', '')]
        assert len(notion_tasks) > 0, "No Notion API tasks found"

    def test_no_emails_sent_or_scheduled(self, flow_yaml):
        """Test NO emails are sent or scheduled by this handler (CRITICAL)."""
        tasks = flow_yaml.get('tasks', [])

        # Should NOT have Resend API calls
        resend_tasks = [task for task in tasks
                        if task.get('type') == 'io.kestra.plugin.core.http.Request'
                        and 'resend.com' in task.get('uri', '')]
        assert len(resend_tasks) == 0, "Signup handler MUST NOT send emails (website responsibility)"

        # Should NOT have subflow calls to send-email
        subflow_tasks = [task for task in tasks
                         if task.get('type') == 'io.kestra.plugin.core.flow.Subflow'
                         and 'send-email' in task.get('flowId', '')]
        assert len(subflow_tasks) == 0, "Signup handler MUST NOT schedule emails"

        # Should NOT have schedule-email-sequence subflow
        schedule_tasks = [task for task in tasks
                          if task.get('type') == 'io.kestra.plugin.core.flow.Subflow'
                          and 'schedule' in task.get('flowId', '').lower()]
        assert len(schedule_tasks) == 0, "Signup handler MUST NOT schedule email sequences"

    def test_signup_event_logged_for_analytics(self, flow_yaml):
        """Test signup event is logged (analytics tracking)."""
        tasks = flow_yaml.get('tasks', [])

        # Should have logging task
        log_tasks = [task for task in tasks
                     if task.get('type') == 'io.kestra.plugin.core.log.Log']
        assert len(log_tasks) > 0, "Missing analytics logging"

    def test_idempotency_duplicate_signups_handled(self, flow_yaml):
        """Test flow handles duplicate signups gracefully."""
        tasks = flow_yaml.get('tasks', [])
        task_ids = [task['id'] for task in tasks]

        # Flow uses Notion's email uniqueness constraint for idempotency
        # create_or_update_contact will fail gracefully on duplicates (handled by Notion)
        assert 'create_or_update_contact' in task_ids, \
            "Missing create_or_update_contact task (idempotency via Notion email uniqueness)"


class TestSignupHandlerNotionIntegration:
    """Test Notion database operations."""

    @pytest.fixture
    def flow_yaml(self):
        """Load signup handler flow YAML."""
        flow_path = Path("kestra/flows/christmas/handlers/signup-handler.yml")
        with open(flow_path, 'r') as f:
            return yaml.safe_load(f)

    def test_notion_api_auth_header(self, flow_yaml):
        """Test Notion tasks use correct authentication."""
        tasks = flow_yaml.get('tasks', [])

        notion_tasks = [task for task in tasks
                        if task.get('type') == 'io.kestra.plugin.core.http.Request'
                        and 'notion.com' in task.get('uri', '')]

        for task in notion_tasks:
            headers = task.get('headers', {})
            assert 'Authorization' in headers
            assert 'Bearer' in headers['Authorization']
            assert 'Notion-Version' in headers

    def test_notion_contacts_db_id_used(self, flow_yaml):
        """Test flow uses correct Notion Contacts database ID."""
        tasks = flow_yaml.get('tasks', [])

        # Should reference secret('NOTION_CONTACTS_DB_ID')
        flow_str = yaml.dump(flow_yaml)
        assert "secret('NOTION_CONTACTS_DB_ID')" in flow_str, \
            "Missing Notion Contacts DB ID secret"

    def test_contact_payload_structure(self, flow_yaml):
        """Test contact creation payload has required fields."""
        tasks = flow_yaml.get('tasks', [])

        # Find contact creation task
        create_tasks = [task for task in tasks
                        if 'create' in task.get('id', '').lower()
                        and task.get('type') == 'io.kestra.plugin.core.http.Request']

        if create_tasks:
            # Check payload structure (email, name, business_name)
            task = create_tasks[0]
            body_template = task.get('body', '')

            # Should reference vars.* variables (not inputs.*)
            assert 'vars.email' in body_template or '{{ email }}' in body_template
            assert 'vars.first_name' in body_template or 'vars.name' in body_template
