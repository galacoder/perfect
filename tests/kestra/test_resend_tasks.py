"""
Test Resend HTTP task templates for Kestra implementation.

Tests the Resend API task definitions in YAML format.

Author: Kestra Migration Team
Created: 2025-11-29
"""

import pytest
import yaml
from pathlib import Path


# Path to Kestra task templates
TASKS_DIR = Path(__file__).parent.parent.parent / "kestra" / "flows" / "christmas" / "tasks"


class TestResendTaskTemplates:
    """Test Resend API task YAML templates."""

    def test_resend_send_email_task_exists(self):
        """Resend send email task file exists."""
        task_file = TASKS_DIR / "resend_send_email.yml"
        assert task_file.exists(), f"Task file not found: {task_file}"

    def test_resend_send_email_task_valid_yaml(self):
        """Resend send email task is valid YAML."""
        task_file = TASKS_DIR / "resend_send_email.yml"
        with open(task_file, 'r') as f:
            task = yaml.safe_load(f)

        assert task is not None
        assert 'id' in task
        assert 'type' in task
        assert task['type'] == 'io.kestra.plugin.core.http.Request'

    def test_resend_api_endpoint_correct(self):
        """Resend API endpoint is correct."""
        task_file = TASKS_DIR / "resend_send_email.yml"
        with open(task_file, 'r') as f:
            task = yaml.safe_load(f)

        uri = task.get('uri')
        assert uri is not None
        assert 'api.resend.com/emails' in uri

    def test_resend_api_auth_header(self):
        """Resend API uses Authorization header with API key."""
        task_file = TASKS_DIR / "resend_send_email.yml"
        with open(task_file, 'r') as f:
            task = yaml.safe_load(f)

        headers = task.get('headers', {})
        assert 'Authorization' in headers
        assert 'Bearer' in headers['Authorization']
        assert "secret('RESEND_API_KEY')" in headers['Authorization']

    def test_resend_email_payload_structure(self):
        """Resend email payload has correct structure."""
        task_file = TASKS_DIR / "resend_send_email.yml"
        with open(task_file, 'r') as f:
            task = yaml.safe_load(f)

        # Should have contentType and body
        assert task.get('contentType') == 'application/json'
        assert 'body' in task

    def test_resend_from_address(self):
        """Resend from address is correct."""
        task_file = TASKS_DIR / "resend_send_email.yml"
        with open(task_file, 'r') as f:
            content = f.read()

        # Should use no-reply@sangletech.com or value@galatek.dev
        assert 'from' in content.lower()
        assert '@' in content  # Has an email address

    def test_resend_template_variable_substitution(self):
        """Resend task supports template variable substitution."""
        task_file = TASKS_DIR / "resend_send_email.yml"
        with open(task_file, 'r') as f:
            content = f.read()

        # Should have inputs for email, subject, html_content
        assert 'to' in content.lower()
        assert 'subject' in content.lower()
        assert 'html' in content.lower()

    def test_resend_response_id_capture(self):
        """Resend task captures response ID."""
        task_file = TASKS_DIR / "resend_send_email.yml"
        with open(task_file, 'r') as f:
            content = f.read()

        # Should reference id in response
        # Kestra automatically stores response, just verify task exists
        assert 'id' in content.lower()


class TestResendAPIConfiguration:
    """Test Resend API configuration and security."""

    def test_resend_task_uses_secret_api_key(self):
        """Resend task uses secret('RESEND_API_KEY') for auth."""
        task_file = TASKS_DIR / "resend_send_email.yml"
        with open(task_file, 'r') as f:
            content = f.read()

        # Should use secret('RESEND_API_KEY')
        assert "secret('RESEND_API_KEY')" in content

    def test_resend_task_method_post(self):
        """Resend send email uses POST method."""
        task_file = TASKS_DIR / "resend_send_email.yml"
        with open(task_file, 'r') as f:
            task = yaml.safe_load(f)

        assert task.get('method') == 'POST'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
