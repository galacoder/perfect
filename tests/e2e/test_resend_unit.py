"""
Unit tests for Christmas Campaign Resend operations.

This module tests email sending and template functions:
- substitute_variables() - Template variable substitution
- get_email_variables() - Build email variables dictionary
- get_fallback_template() - Fallback template retrieval
- send_email() - Email sending (mocked)
- send_template_email() - Template email sending (mocked)

Coverage target: 100% of resend_operations.py (with mocking for API calls)
"""

import pytest
from unittest.mock import patch, MagicMock, call
from campaigns.christmas_campaign.tasks.resend_operations import (
    substitute_variables,
    get_email_variables,
    get_fallback_template
)

# Import for mocking tests
import campaigns.christmas_campaign.tasks.resend_operations as resend_ops


# ===== substitute_variables() tests =====

class TestSubstituteVariables:
    """Test template variable substitution logic."""

    def test_simple_variable_substitution(self):
        """Simple {{variable}} replacement works."""
        template = "Hi {{first_name}}!"
        variables = {"first_name": "John"}
        result = substitute_variables(template, variables)
        assert result == "Hi John!"

    def test_multiple_variables(self):
        """Multiple variables substituted correctly."""
        template = "Hi {{first_name}} from {{business_name}}!"
        variables = {
            "first_name": "John",
            "business_name": "Test Corp"
        }
        result = substitute_variables(template, variables)
        assert result == "Hi John from Test Corp!"

    def test_numeric_variable(self):
        """Numeric values converted to strings."""
        template = "Your score is {{assessment_score}}/100"
        variables = {"assessment_score": 45}
        result = substitute_variables(template, variables)
        assert result == "Your score is 45/100"

    def test_html_template(self):
        """HTML templates with variables work."""
        template = "<html><body><p>Hi {{first_name}}</p></body></html>"
        variables = {"first_name": "John"}
        result = substitute_variables(template, variables)
        assert "<p>Hi John</p>" in result

    def test_variable_not_in_template(self):
        """Extra variables in dict are ignored."""
        template = "Hi {{first_name}}!"
        variables = {
            "first_name": "John",
            "extra_var": "ignored"
        }
        result = substitute_variables(template, variables)
        assert result == "Hi John!"
        assert "ignored" not in result

    def test_missing_variable_unchanged(self):
        """Missing variables remain as {{variable}}."""
        template = "Hi {{first_name}}, your score is {{assessment_score}}!"
        variables = {"first_name": "John"}
        result = substitute_variables(template, variables)
        assert "Hi John" in result
        assert "{{assessment_score}}" in result  # Unchanged

    def test_empty_variables(self):
        """Empty variables dict returns template unchanged."""
        template = "Hi {{first_name}}!"
        variables = {}
        result = substitute_variables(template, variables)
        assert result == template

    def test_special_characters_in_value(self):
        """Special characters in values handled correctly."""
        template = "Name: {{name}}"
        variables = {"name": "O'Brien & Sons"}
        result = substitute_variables(template, variables)
        assert result == "Name: O'Brien & Sons"

    def test_repeated_variable(self):
        """Same variable used multiple times."""
        template = "Hi {{name}}! Welcome {{name}}!"
        variables = {"name": "John"}
        result = substitute_variables(template, variables)
        assert result == "Hi John! Welcome John!"

    def test_variable_in_subject_line(self):
        """Variables in subject lines work."""
        subject = "Welcome to BusOS, {{first_name}}!"
        variables = {"first_name": "Jane"}
        result = substitute_variables(subject, variables)
        assert result == "Welcome to BusOS, Jane!"

    def test_none_value(self):
        """None values converted to 'None' string."""
        template = "Value: {{value}}"
        variables = {"value": None}
        result = substitute_variables(template, variables)
        assert result == "Value: None"

    def test_boolean_value(self):
        """Boolean values converted to strings."""
        template = "Status: {{status}}"
        variables = {"status": True}
        result = substitute_variables(template, variables)
        assert result == "Status: True"


# ===== get_email_variables() tests =====

class TestGetEmailVariables:
    """Test email variables dictionary builder."""

    def test_minimal_variables(self):
        """Default first_name and business_name."""
        variables = get_email_variables()
        assert variables["first_name"] == "there"
        assert variables["business_name"] == "your business"
        assert len(variables) == 2  # Only defaults

    def test_custom_names(self):
        """Custom names override defaults."""
        variables = get_email_variables(
            first_name="John",
            business_name="Test Corp"
        )
        assert variables["first_name"] == "John"
        assert variables["business_name"] == "Test Corp"

    def test_assessment_score_included(self):
        """Assessment score included when provided."""
        variables = get_email_variables(
            first_name="John",
            assessment_score=45
        )
        assert variables["assessment_score"] == "45"  # Converted to string

    def test_assessment_score_zero(self):
        """Assessment score of 0 is included."""
        variables = get_email_variables(assessment_score=0)
        assert variables["assessment_score"] == "0"

    def test_assessment_score_none_excluded(self):
        """Assessment score of None is excluded."""
        variables = get_email_variables(assessment_score=None)
        assert "assessment_score" not in variables

    def test_segment_included(self):
        """Segment included when provided."""
        variables = get_email_variables(
            first_name="John",
            segment="CRITICAL"
        )
        assert variables["segment"] == "CRITICAL"

    def test_segment_empty_string_excluded(self):
        """Empty segment string is excluded."""
        variables = get_email_variables(segment="")
        assert "segment" not in variables

    def test_diagnostic_call_date_included(self):
        """Diagnostic call date included when provided."""
        variables = get_email_variables(
            diagnostic_call_date="2025-11-25"
        )
        assert variables["diagnostic_call_date"] == "2025-11-25"

    def test_portal_url_included(self):
        """Portal URL included when provided."""
        variables = get_email_variables(
            portal_url="https://notion.so/portal-123"
        )
        assert variables["portal_url"] == "https://notion.so/portal-123"

    def test_all_variables_included(self):
        """All variables included when provided."""
        variables = get_email_variables(
            first_name="John",
            business_name="Test Corp",
            assessment_score=45,
            segment="URGENT",
            diagnostic_call_date="2025-11-25",
            portal_url="https://notion.so/portal-123"
        )
        assert len(variables) == 6
        assert variables["first_name"] == "John"
        assert variables["assessment_score"] == "45"
        assert variables["segment"] == "URGENT"
        assert variables["diagnostic_call_date"] == "2025-11-25"
        assert variables["portal_url"] == "https://notion.so/portal-123"

    def test_optional_variables_excluded_by_default(self):
        """Optional variables excluded when not provided."""
        variables = get_email_variables(
            first_name="John",
            business_name="Test Corp"
        )
        assert "assessment_score" not in variables
        assert "segment" not in variables
        assert "diagnostic_call_date" not in variables
        assert "portal_url" not in variables


# ===== get_fallback_template() tests =====

class TestGetFallbackTemplate:
    """Test fallback template retrieval."""

    def test_christmas_email_1_fallback(self):
        """christmas_email_1 fallback template exists."""
        template = get_fallback_template("christmas_email_1")
        assert "subject" in template
        assert "html_body" in template
        assert "BusOS Assessment Results" in template["subject"]
        assert "{{first_name}}" in template["html_body"]
        assert "{{business_name}}" in template["html_body"]
        assert "{{assessment_score}}" in template["html_body"]

    def test_christmas_email_2_fallback(self):
        """christmas_email_2 fallback template exists."""
        template = get_fallback_template("christmas_email_2")
        assert "subject" in template
        assert "html_body" in template
        assert "Quick Wins" in template["subject"]
        assert "{{business_name}}" in template["subject"]

    def test_unknown_template_returns_default(self):
        """Unknown template ID returns generic fallback."""
        template = get_fallback_template("unknown_template_123")
        assert "subject" in template
        assert "html_body" in template
        assert "Update from BusOS" in template["subject"]
        assert "{{first_name}}" in template["html_body"]

    def test_fallback_template_structure(self):
        """All fallback templates have required keys."""
        template_ids = ["christmas_email_1", "christmas_email_2", "unknown"]
        for template_id in template_ids:
            template = get_fallback_template(template_id)
            assert isinstance(template, dict)
            assert "subject" in template
            assert "html_body" in template
            assert isinstance(template["subject"], str)
            assert isinstance(template["html_body"], str)

    def test_fallback_templates_have_placeholders(self):
        """Fallback templates contain variable placeholders."""
        template = get_fallback_template("christmas_email_1")
        # Should have at least first_name placeholder
        assert "{{first_name}}" in template["html_body"]


# ===== Integration tests =====

class TestResendIntegration:
    """Test resend functions work together."""

    def test_full_email_workflow(self):
        """Test complete workflow: get variables → substitute → ready to send."""
        # Step 1: Get email variables
        variables = get_email_variables(
            first_name="John",
            business_name="Test Corp",
            assessment_score=45,
            segment="URGENT"
        )

        # Step 2: Get fallback template
        template = get_fallback_template("christmas_email_1")

        # Step 3: Substitute variables in subject
        final_subject = substitute_variables(template["subject"], variables)
        assert "John" not in final_subject  # first_name not in this subject

        # Step 4: Substitute variables in body
        final_body = substitute_variables(template["html_body"], variables)
        assert "John" in final_body
        assert "Test Corp" in final_body
        assert "45" in final_body

    def test_subject_line_with_variables(self):
        """Test subject line variable substitution."""
        template = get_fallback_template("christmas_email_2")
        variables = get_email_variables(
            first_name="Jane",
            business_name="Acme Inc"
        )

        final_subject = substitute_variables(template["subject"], variables)
        assert "Acme Inc" in final_subject
        assert "{{business_name}}" not in final_subject

    def test_missing_optional_variables_graceful(self):
        """Missing optional variables don't break template."""
        template = get_fallback_template("christmas_email_1")
        variables = get_email_variables(
            first_name="John"
            # Missing assessment_score
        )

        final_body = substitute_variables(template["html_body"], variables)
        assert "John" in final_body
        # assessment_score placeholder remains
        assert "{{assessment_score}}" in final_body

    def test_all_segment_types(self):
        """Test variable building for all segment types."""
        segments = ["CRITICAL", "URGENT", "OPTIMIZE"]
        for segment in segments:
            variables = get_email_variables(
                first_name="Test",
                segment=segment
            )
            assert variables["segment"] == segment

    def test_email_template_ready_for_sending(self):
        """Final email body is valid HTML."""
        variables = get_email_variables(
            first_name="John",
            business_name="Test Corp",
            assessment_score=45
        )
        template = get_fallback_template("christmas_email_1")
        final_body = substitute_variables(template["html_body"], variables)

        # Basic HTML validation
        assert "<html>" in final_body or "<HTML>" in final_body.upper()
        assert "</html>" in final_body or "</HTML>" in final_body.upper()
        assert "John" in final_body
        assert "Test Corp" in final_body


# ===== Mocked API tests =====

class TestSendEmailMocked:
    """Test send_email() with mocked Resend API."""

    @patch('campaigns.christmas_campaign.tasks.resend_operations.resend.Emails.send')
    def test_send_email_success(self, mock_send):
        """Successful email send returns email ID."""
        # Mock successful API response
        mock_send.return_value = {"id": "email-id-123"}

        from campaigns.christmas_campaign.tasks.resend_operations import send_email

        # Call function
        email_id = send_email.fn(
            to_email="test@example.com",
            subject="Test Subject",
            html_body="<html><body>Test</body></html>"
        )

        # Verify result
        assert email_id == "email-id-123"

        # Verify API called correctly
        mock_send.assert_called_once()
        call_args = mock_send.call_args[0][0]
        assert call_args["to"] == ["test@example.com"]
        assert call_args["subject"] == "Test Subject"
        assert call_args["html"] == "<html><body>Test</body></html>"
        assert "Sang Le - BusOS" in call_args["from"]

    @patch('campaigns.christmas_campaign.tasks.resend_operations.resend.Emails.send')
    def test_send_email_failure_raises_exception(self, mock_send):
        """Email send failure raises exception."""
        # Mock API failure
        mock_send.side_effect = Exception("API Error")

        from campaigns.christmas_campaign.tasks.resend_operations import send_email

        # Call should raise exception
        with pytest.raises(Exception) as exc_info:
            send_email.fn(
                to_email="test@example.com",
                subject="Test",
                html_body="Test"
            )

        assert "API Error" in str(exc_info.value)

    @patch('campaigns.christmas_campaign.tasks.resend_operations.resend.Emails.send')
    def test_send_email_with_html_content(self, mock_send):
        """HTML content passed through correctly."""
        mock_send.return_value = {"id": "email-123"}

        from campaigns.christmas_campaign.tasks.resend_operations import send_email

        html = "<html><head><title>Test</title></head><body><h1>Hello</h1></body></html>"
        send_email.fn(
            to_email="test@example.com",
            subject="HTML Test",
            html_body=html
        )

        call_args = mock_send.call_args[0][0]
        assert call_args["html"] == html


class TestSendTemplateEmailMocked:
    """Test send_template_email() with mocked send_email."""

    @patch('campaigns.christmas_campaign.tasks.resend_operations.send_email')
    def test_send_template_email_substitutes_variables(self, mock_send_email):
        """Template variables substituted before sending."""
        # Mock send_email task
        mock_send_email.return_value = "email-id-123"

        from campaigns.christmas_campaign.tasks.resend_operations import send_template_email

        # Call with template and variables
        result = send_template_email.fn(
            to_email="john@testcorp.com",
            subject="Hi {{first_name}}!",
            template="<html><body>Hi {{first_name}} from {{business_name}}</body></html>",
            variables={"first_name": "John", "business_name": "Test Corp"}
        )

        # Verify result
        assert result == "email-id-123"

        # Verify send_email called with substituted content
        mock_send_email.assert_called_once_with(
            "john@testcorp.com",
            "Hi John!",  # Subject substituted
            "<html><body>Hi John from Test Corp</body></html>"  # Body substituted
        )

    @patch('campaigns.christmas_campaign.tasks.resend_operations.send_email')
    def test_send_template_email_with_missing_variables(self, mock_send_email):
        """Missing variables remain as placeholders."""
        mock_send_email.return_value = "email-id-456"

        from campaigns.christmas_campaign.tasks.resend_operations import send_template_email

        send_template_email.fn(
            to_email="test@example.com",
            subject="Test {{first_name}}",
            template="Hi {{first_name}}, score: {{assessment_score}}",
            variables={"first_name": "Jane"}  # Missing assessment_score
        )

        # Verify substituted content
        call_args = mock_send_email.call_args[0]
        assert call_args[1] == "Test Jane"  # Subject
        assert "Jane" in call_args[2]  # Body has Jane
        assert "{{assessment_score}}" in call_args[2]  # Placeholder remains

    @patch('campaigns.christmas_campaign.tasks.resend_operations.send_email')
    def test_send_template_email_with_numeric_variables(self, mock_send_email):
        """Numeric variables converted to strings."""
        mock_send_email.return_value = "email-id-789"

        from campaigns.christmas_campaign.tasks.resend_operations import send_template_email

        send_template_email.fn(
            to_email="test@example.com",
            subject="Score: {{score}}",
            template="Your score is {{score}}/100",
            variables={"score": 85}
        )

        call_args = mock_send_email.call_args[0]
        assert call_args[1] == "Score: 85"
        assert "85/100" in call_args[2]
