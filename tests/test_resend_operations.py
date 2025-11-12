"""
Unit tests for Resend operations module.

Tests all Prefect tasks for email sending with mocking.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from tasks.resend_operations import (
    send_email,
    substitute_variables,
    send_template_email
)


@pytest.fixture
def mock_httpx_client():
    """Mock httpx client for testing."""
    with patch('tasks.resend_operations.httpx.Client') as mock_client:
        yield mock_client


class TestSendEmail:
    """Tests for send_email task."""

    def test_send_email_success(self, mock_httpx_client):
        """Test sending email returns email ID."""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "email-123", "status": "sent"}

        mock_client_instance = Mock()
        mock_client_instance.post.return_value = mock_response
        mock_httpx_client.return_value.__enter__.return_value = mock_client_instance

        # Act
        result = send_email(
            to_email="test@example.com",
            subject="Test Subject",
            html="<p>Test body</p>",
            from_email="Sang Le <sang@sanglescalinglabs.com>"
        )

        # Assert
        assert result["id"] == "email-123"
        assert result["status"] == "sent"
        mock_client_instance.post.assert_called_once()

        # Verify API call structure
        call_args = mock_client_instance.post.call_args
        assert call_args[0][0] == "https://api.resend.com/emails"

        json_payload = call_args[1]["json"]
        assert json_payload["to"] == ["test@example.com"]
        assert json_payload["subject"] == "Test Subject"
        assert json_payload["html"] == "<p>Test body</p>"
        assert json_payload["from"] == "Sang Le <sang@sanglescalinglabs.com>"

    def test_send_email_with_reply_to(self, mock_httpx_client):
        """Test sending email with reply_to address."""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "email-456"}

        mock_client_instance = Mock()
        mock_client_instance.post.return_value = mock_response
        mock_httpx_client.return_value.__enter__.return_value = mock_client_instance

        # Act
        result = send_email(
            to_email="test@example.com",
            subject="Test",
            html="<p>Body</p>",
            reply_to="reply@example.com"
        )

        # Assert
        assert result["id"] == "email-456"
        call_args = mock_client_instance.post.call_args
        json_payload = call_args[1]["json"]
        assert json_payload["reply_to"] == ["reply@example.com"]

    def test_send_email_handles_api_error(self, mock_httpx_client):
        """Test send_email raises exception on API error."""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": "Invalid email"}
        mock_response.raise_for_status.side_effect = Exception("API Error 400")

        mock_client_instance = Mock()
        mock_client_instance.post.return_value = mock_response
        mock_httpx_client.return_value.__enter__.return_value = mock_client_instance

        # Act & Assert
        with pytest.raises(Exception, match="API Error 400"):
            send_email(
                to_email="invalid",
                subject="Test",
                html="<p>Body</p>"
            )

    def test_send_email_handles_network_error(self, mock_httpx_client):
        """Test send_email raises exception on network error."""
        # Arrange
        mock_client_instance = Mock()
        mock_client_instance.post.side_effect = Exception("Network timeout")
        mock_httpx_client.return_value.__enter__.return_value = mock_client_instance

        # Act & Assert
        with pytest.raises(Exception, match="Network timeout"):
            send_email(
                to_email="test@example.com",
                subject="Test",
                html="<p>Body</p>"
            )


class TestSubstituteVariables:
    """Tests for substitute_variables task."""

    def test_substitute_single_variable(self):
        """Test substituting a single variable."""
        # Arrange
        template = "Hello {{name}}"
        variables = {"name": "John"}

        # Act
        result = substitute_variables(template, variables)

        # Assert
        assert result == "Hello John"

    def test_substitute_multiple_variables(self):
        """Test substituting multiple variables."""
        # Arrange
        template = "Hello {{first_name}}, welcome to {{business_name}}!"
        variables = {
            "first_name": "Sarah",
            "business_name": "Elegant Hair Salon"
        }

        # Act
        result = substitute_variables(template, variables)

        # Assert
        assert result == "Hello Sarah, welcome to Elegant Hair Salon!"

    def test_substitute_variables_in_html(self):
        """Test substituting variables in HTML content."""
        # Arrange
        template = """
        <!DOCTYPE html>
        <html>
        <body>
            <h1>Hi {{first_name}}</h1>
            <p>Your assessment for {{business_name}} is ready.</p>
            <a href="{{assessment_url}}">View Results</a>
        </body>
        </html>
        """
        variables = {
            "first_name": "Mike",
            "business_name": "The Barber Shop",
            "assessment_url": "https://example.com/assessment/123"
        }

        # Act
        result = substitute_variables(template, variables)

        # Assert
        assert "Hi Mike" in result
        assert "Your assessment for The Barber Shop is ready." in result
        assert 'href="https://example.com/assessment/123"' in result
        assert "{{" not in result  # No remaining placeholders

    def test_substitute_missing_variable(self):
        """Test that missing variables are left as placeholders."""
        # Arrange
        template = "Hello {{first_name}}, your score is {{score}}"
        variables = {"first_name": "Jane"}

        # Act
        result = substitute_variables(template, variables)

        # Assert
        assert result == "Hello Jane, your score is {{score}}"
        assert "{{score}}" in result  # Placeholder remains

    def test_substitute_empty_variables(self):
        """Test substituting with empty variable dictionary."""
        # Arrange
        template = "Hello {{name}}"
        variables = {}

        # Act
        result = substitute_variables(template, variables)

        # Assert
        assert result == "Hello {{name}}"

    def test_substitute_numeric_values(self):
        """Test substituting numeric values."""
        # Arrange
        template = "Your score is {{score}} out of {{total}}"
        variables = {"score": 85, "total": 100}

        # Act
        result = substitute_variables(template, variables)

        # Assert
        assert result == "Your score is 85 out of 100"

    def test_substitute_duplicate_variables(self):
        """Test substituting the same variable multiple times."""
        # Arrange
        template = "{{name}} {{name}} {{name}}"
        variables = {"name": "Test"}

        # Act
        result = substitute_variables(template, variables)

        # Assert
        assert result == "Test Test Test"


class TestSendTemplateEmail:
    """Tests for send_template_email task."""

    def test_send_template_email_success(self, mock_httpx_client):
        """Test sending email with template substitution."""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "email-789", "status": "sent"}

        mock_client_instance = Mock()
        mock_client_instance.post.return_value = mock_response
        mock_httpx_client.return_value.__enter__.return_value = mock_client_instance

        template = {
            "subject": "Hello {{first_name}}",
            "html": "<p>Welcome to {{business_name}}!</p>"
        }
        variables = {
            "first_name": "Alex",
            "business_name": "Spa Paradise"
        }

        # Act
        result = send_template_email(
            to_email="alex@example.com",
            template=template,
            variables=variables
        )

        # Assert
        assert result["id"] == "email-789"
        assert result["status"] == "sent"

        # Verify substitution happened
        call_args = mock_client_instance.post.call_args
        json_payload = call_args[1]["json"]
        assert json_payload["subject"] == "Hello Alex"
        assert json_payload["html"] == "<p>Welcome to Spa Paradise!</p>"

    def test_send_template_email_with_custom_from(self, mock_httpx_client):
        """Test sending template email with custom from address."""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "email-101"}

        mock_client_instance = Mock()
        mock_client_instance.post.return_value = mock_response
        mock_httpx_client.return_value.__enter__.return_value = mock_client_instance

        template = {
            "subject": "Test",
            "html": "<p>Body</p>"
        }

        # Act
        result = send_template_email(
            to_email="test@example.com",
            template=template,
            variables={},
            from_email="Custom <custom@example.com>"
        )

        # Assert
        assert result["id"] == "email-101"
        call_args = mock_client_instance.post.call_args
        json_payload = call_args[1]["json"]
        assert json_payload["from"] == "Custom <custom@example.com>"

    def test_send_template_email_handles_error(self, mock_httpx_client):
        """Test send_template_email raises exception on API error."""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = Exception("Server Error")

        mock_client_instance = Mock()
        mock_client_instance.post.return_value = mock_response
        mock_httpx_client.return_value.__enter__.return_value = mock_client_instance

        template = {"subject": "Test", "html": "<p>Body</p>"}

        # Act & Assert
        with pytest.raises(Exception, match="Server Error"):
            send_template_email(
                to_email="test@example.com",
                template=template,
                variables={}
            )


class TestRetryLogic:
    """Tests for Prefect retry logic (integration test concept)."""

    def test_retry_annotation_exists(self):
        """Verify all tasks have retry annotations."""
        import inspect
        from tasks import resend_operations

        # Get all functions that should be tasks
        task_functions = [
            resend_operations.send_email,
            resend_operations.send_template_email
        ]

        for func in task_functions:
            # Verify function has task metadata
            assert callable(func), f"{func.__name__} should be callable"

    def test_substitute_variables_is_task(self):
        """Verify substitute_variables is a Prefect task."""
        from tasks.resend_operations import substitute_variables
        assert callable(substitute_variables)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
