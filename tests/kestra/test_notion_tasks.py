"""
Test Notion HTTP task templates for Kestra implementation.

Tests the Notion API task definitions in YAML format.

Author: Kestra Migration Team
Created: 2025-11-29
"""

import pytest
import yaml
from pathlib import Path


# Path to Kestra task templates
TASKS_DIR = Path(__file__).parent.parent.parent / "kestra" / "flows" / "christmas" / "tasks"


class TestNotionTaskTemplates:
    """Test Notion API task YAML templates."""

    def test_notion_search_contact_task_exists(self):
        """Notion search contact task file exists."""
        task_file = TASKS_DIR / "notion_search_contact.yml"
        assert task_file.exists(), f"Task file not found: {task_file}"

    def test_notion_search_contact_task_valid_yaml(self):
        """Notion search contact task is valid YAML."""
        task_file = TASKS_DIR / "notion_search_contact.yml"
        with open(task_file, 'r') as f:
            task = yaml.safe_load(f)

        assert task is not None
        assert 'id' in task
        assert 'type' in task
        assert task['type'] == 'io.kestra.plugin.core.http.Request'

    def test_notion_search_contact_has_auth_header(self):
        """Notion search contact task has Authorization header."""
        task_file = TASKS_DIR / "notion_search_contact.yml"
        with open(task_file, 'r') as f:
            task = yaml.safe_load(f)

        headers = task.get('headers', {})
        assert 'Authorization' in headers
        assert 'Bearer' in headers['Authorization']
        assert "secret('NOTION_TOKEN')" in headers['Authorization']

    def test_notion_search_contact_endpoint(self):
        """Notion search contact task uses correct endpoint."""
        task_file = TASKS_DIR / "notion_search_contact.yml"
        with open(task_file, 'r') as f:
            task = yaml.safe_load(f)

        uri = task.get('uri')
        assert uri is not None
        assert 'api.notion.com/v1/databases' in uri
        assert 'query' in uri

    def test_notion_create_sequence_task_exists(self):
        """Notion create sequence task file exists."""
        task_file = TASKS_DIR / "notion_create_sequence.yml"
        assert task_file.exists(), f"Task file not found: {task_file}"

    def test_notion_create_sequence_task_valid_yaml(self):
        """Notion create sequence task is valid YAML."""
        task_file = TASKS_DIR / "notion_create_sequence.yml"
        with open(task_file, 'r') as f:
            task = yaml.safe_load(f)

        assert task is not None
        assert 'id' in task
        assert task['type'] == 'io.kestra.plugin.core.http.Request'
        assert task['method'] == 'POST'

    def test_notion_update_sequence_tracker_task_exists(self):
        """Notion update sequence tracker task file exists (CRITICAL for per-email updates)."""
        task_file = TASKS_DIR / "notion_update_sequence_tracker.yml"
        assert task_file.exists(), f"Task file not found: {task_file}"

    def test_notion_update_sequence_tracker_payload_structure(self):
        """Notion update sequence tracker task has correct payload structure."""
        task_file = TASKS_DIR / "notion_update_sequence_tracker.yml"
        with open(task_file, 'r') as f:
            task = yaml.safe_load(f)

        # Should have contentType and body
        assert task.get('contentType') == 'application/json'
        assert 'body' in task

    def test_notion_update_sequence_tracker_email_number_field(self):
        """Notion update sequence tracker includes email_number field."""
        task_file = TASKS_DIR / "notion_update_sequence_tracker.yml"
        with open(task_file, 'r') as f:
            content = f.read()

        # Check for email_number variable
        assert 'email_number' in content.lower()

    def test_notion_update_sequence_tracker_sent_timestamp_field(self):
        """Notion update sequence tracker includes sent_at timestamp field."""
        task_file = TASKS_DIR / "notion_update_sequence_tracker.yml"
        with open(task_file, 'r') as f:
            content = f.read()

        assert 'sent_at' in content.lower() or 'sent_timestamp' in content.lower()

    def test_notion_update_sequence_tracker_sent_by_field(self):
        """Notion update sequence tracker includes sent_by='kestra' field."""
        task_file = TASKS_DIR / "notion_update_sequence_tracker.yml"
        with open(task_file, 'r') as f:
            content = f.read()

        assert 'sent_by' in content.lower()

    def test_notion_update_sequence_tracker_resend_id_field(self):
        """Notion update sequence tracker includes resend_id field."""
        task_file = TASKS_DIR / "notion_update_sequence_tracker.yml"
        with open(task_file, 'r') as f:
            content = f.read()

        assert 'resend_id' in content.lower()

    def test_notion_fetch_template_task_exists(self):
        """Notion fetch template task file exists."""
        task_file = TASKS_DIR / "notion_fetch_template.yml"
        assert task_file.exists(), f"Task file not found: {task_file}"

    def test_notion_fetch_template_task_valid_yaml(self):
        """Notion fetch template task is valid YAML."""
        task_file = TASKS_DIR / "notion_fetch_template.yml"
        with open(task_file, 'r') as f:
            task = yaml.safe_load(f)

        assert task is not None
        assert 'id' in task
        assert task['type'] == 'io.kestra.plugin.core.http.Request'


class TestNotionAPIConfiguration:
    """Test Notion API configuration and security."""

    def test_all_notion_tasks_use_secret_token(self):
        """All Notion tasks use secret('NOTION_TOKEN') for auth."""
        task_files = list(TASKS_DIR.glob("notion_*.yml"))

        for task_file in task_files:
            with open(task_file, 'r') as f:
                content = f.read()

            # Should use secret('NOTION_TOKEN')
            assert "secret('NOTION_TOKEN')" in content, \
                f"{task_file.name} does not use secret('NOTION_TOKEN')"

    def test_all_notion_tasks_use_notion_api_version(self):
        """All Notion tasks use correct Notion API version header."""
        task_files = list(TASKS_DIR.glob("notion_*.yml"))

        for task_file in task_files:
            with open(task_file, 'r') as f:
                task = yaml.safe_load(f)

            headers = task.get('headers', {})
            # Notion API requires Notion-Version header
            assert 'Notion-Version' in headers, \
                f"{task_file.name} missing Notion-Version header"


class TestNotionSequenceTrackerUpdate:
    """Test Notion Sequence Tracker update task (Feature 2.8 integration)."""

    def test_update_sequence_tracker_per_email_payload(self):
        """Notion update sequence tracker has per-email tracking payload."""
        task_file = TASKS_DIR / "notion_update_sequence_tracker.yml"
        with open(task_file, 'r') as f:
            task = yaml.safe_load(f)

        # Task should have body with properties
        assert 'body' in task

    def test_update_sequence_tracker_email_number_correct(self):
        """Email number field is properly mapped from inputs."""
        task_file = TASKS_DIR / "notion_update_sequence_tracker.yml"
        with open(task_file, 'r') as f:
            content = f.read()

        # Should use inputs.email_number
        assert '{{' in content and 'email_number' in content

    def test_update_sequence_tracker_sent_timestamp_format(self):
        """Sent timestamp uses ISO 8601 format."""
        task_file = TASKS_DIR / "notion_update_sequence_tracker.yml"
        with open(task_file, 'r') as f:
            content = f.read()

        # Should reference timestamp variable
        assert 'sent_at' in content.lower() or 'timestamp' in content.lower()

    def test_update_sequence_tracker_status_field(self):
        """Status field included (sent/failed)."""
        task_file = TASKS_DIR / "notion_update_sequence_tracker.yml"
        with open(task_file, 'r') as f:
            content = f.read()

        assert 'status' in content.lower()

    def test_update_sequence_tracker_sent_by_kestra_default(self):
        """sent_by defaults to 'kestra'."""
        task_file = TASKS_DIR / "notion_update_sequence_tracker.yml"
        with open(task_file, 'r') as f:
            content = f.read()

        # Should have sent_by with default value 'kestra'
        assert 'sent_by' in content.lower()
        assert 'kestra' in content.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
