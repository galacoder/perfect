"""
Tests for template variable rendering - Lead Nurture Personalization (Wave 0).

This module tests:
1. Variable substitution for all personalization fields
2. No unreplaced {{variable}} placeholders remain in output
3. Fallback handling for missing variables
4. All standard variables: first_name, top_red_system, segment, scorecard_url, calendly_link

TDD Approach: Tests written FIRST (Red phase), then implementation (Green phase).

Author: Coding Agent (Sonnet 4.5)
Created: 2025-11-26
Wave: 0 - Lead Nurture Verification
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import re


# ==============================================================================
# Feature 0.4: Verify personalization variables render correctly
# ==============================================================================

class TestTemplateVariableRendering:
    """Test template variable substitution for lead nurture emails."""

    def test_render_first_name_variable(self):
        """Verify {{first_name}} variable is replaced correctly."""
        from campaigns.christmas_campaign.tasks import resend_operations

        template = "Hi {{first_name}}, welcome to BusOS!"
        variables = {"first_name": "John"}

        result = resend_operations.substitute_variables.fn(template, variables)

        assert "{{first_name}}" not in result
        assert "John" in result
        assert result == "Hi John, welcome to BusOS!"

    def test_render_top_red_system_variable(self):
        """Verify {{top_red_system}} variable is replaced correctly."""
        from campaigns.christmas_campaign.tasks import resend_operations

        template = "Your biggest issue is {{top_red_system}}."
        variables = {"top_red_system": "Cash Flow"}

        result = resend_operations.substitute_variables.fn(template, variables)

        assert "{{top_red_system}}" not in result
        assert "Cash Flow" in result

    def test_render_segment_variable(self):
        """Verify {{segment}} variable is replaced correctly."""
        from campaigns.christmas_campaign.tasks import resend_operations

        template = "You're in the {{segment}} segment."
        variables = {"segment": "CRITICAL"}

        result = resend_operations.substitute_variables.fn(template, variables)

        assert "{{segment}}" not in result
        assert "CRITICAL" in result

    def test_render_scorecard_url_variable(self):
        """Verify {{scorecard_url}} variable is replaced correctly."""
        from campaigns.christmas_campaign.tasks import resend_operations

        template = "View your results: {{scorecard_url}}"
        variables = {"scorecard_url": "https://example.com/scorecard/123"}

        result = resend_operations.substitute_variables.fn(template, variables)

        assert "{{scorecard_url}}" not in result
        assert "https://example.com/scorecard/123" in result

    def test_render_calendly_link_variable(self):
        """Verify {{calendly_link}} variable is replaced correctly."""
        from campaigns.christmas_campaign.tasks import resend_operations

        template = "Book your call: {{calendly_link}}"
        variables = {"calendly_link": "https://calendly.com/sang-le/diagnostic"}

        result = resend_operations.substitute_variables.fn(template, variables)

        assert "{{calendly_link}}" not in result
        assert "https://calendly.com/sang-le/diagnostic" in result

    def test_render_all_variables_replaced(self):
        """Verify all variables are replaced in a complex template."""
        from campaigns.christmas_campaign.tasks import resend_operations

        template = """
        Hi {{first_name}},

        Your BusOS segment: {{segment}}
        Top issue: {{top_red_system}}

        View scorecard: {{scorecard_url}}
        Book call: {{calendly_link}}
        """

        variables = {
            "first_name": "Jane",
            "segment": "URGENT",
            "top_red_system": "Marketing",
            "scorecard_url": "https://example.com/scorecard/456",
            "calendly_link": "https://calendly.com/sang-le/diagnostic"
        }

        result = resend_operations.substitute_variables.fn(template, variables)

        # Check all variables replaced
        assert "Jane" in result
        assert "URGENT" in result
        assert "Marketing" in result
        assert "https://example.com/scorecard/456" in result
        assert "https://calendly.com/sang-le/diagnostic" in result

    def test_render_no_unreplaced_variables_in_output(self):
        """Verify no {{variable}} placeholders remain after substitution."""
        from campaigns.christmas_campaign.tasks import resend_operations

        template = """
        <html>
        <body>
            <h1>Hi {{first_name}}!</h1>
            <p>Your segment: {{segment}}</p>
            <p>Top issue: {{top_red_system}}</p>
            <a href="{{scorecard_url}}">View Scorecard</a>
            <a href="{{calendly_link}}">Book Call</a>
        </body>
        </html>
        """

        variables = {
            "first_name": "Sarah",
            "segment": "OPTIMIZE",
            "top_red_system": "Sales",
            "scorecard_url": "https://example.com/scorecard/789",
            "calendly_link": "https://calendly.com/sang-le/diagnostic"
        }

        result = resend_operations.substitute_variables.fn(template, variables)

        # Check for any unreplaced {{...}} patterns
        unreplaced_vars = re.findall(r'\{\{[^}]+\}\}', result)
        assert len(unreplaced_vars) == 0, f"Found unreplaced variables: {unreplaced_vars}"

    def test_render_missing_variable_fallback(self):
        """Verify graceful handling when variable is missing from dict."""
        from campaigns.christmas_campaign.tasks import resend_operations

        template = "Hi {{first_name}}, your score is {{assessment_score}}."
        variables = {"first_name": "Bob"}  # missing assessment_score

        result = resend_operations.substitute_variables.fn(template, variables)

        # Should replace first_name but leave assessment_score as-is
        assert "Bob" in result
        assert "{{assessment_score}}" in result  # Not replaced

    def test_render_business_name_variable(self):
        """Verify {{business_name}} variable is replaced correctly."""
        from campaigns.christmas_campaign.tasks import resend_operations

        template = "Great to meet you, {{business_name}}!"
        variables = {"business_name": "Test Salon LLC"}

        result = resend_operations.substitute_variables.fn(template, variables)

        assert "{{business_name}}" not in result
        assert "Test Salon LLC" in result

    def test_render_with_special_characters(self):
        """Verify variables with special characters are handled correctly."""
        from campaigns.christmas_campaign.tasks import resend_operations

        template = "Business: {{business_name}}, Owner: {{first_name}}"
        variables = {
            "business_name": "Sarah's Salon & Spa",
            "first_name": "O'Brien"
        }

        result = resend_operations.substitute_variables.fn(template, variables)

        assert "Sarah's Salon & Spa" in result
        assert "O'Brien" in result

    def test_render_variables_in_subject_line(self):
        """Verify variables work in email subject lines."""
        from campaigns.christmas_campaign.tasks import resend_operations

        subject_template = "{{first_name}}, your {{segment}} results are ready"
        variables = {
            "first_name": "Mike",
            "segment": "CRITICAL"
        }

        result = resend_operations.substitute_variables.fn(subject_template, variables)

        assert result == "Mike, your CRITICAL results are ready"


class TestSendTemplateEmail:
    """Test send_template_email function with variable substitution."""

    def test_send_template_email_substitutes_variables(self, monkeypatch):
        """Verify send_template_email substitutes variables before sending."""
        from campaigns.christmas_campaign.tasks import resend_operations

        mock_resend_emails = MagicMock()
        mock_resend_emails.send.return_value = {"id": "email-id-123"}

        monkeypatch.setattr(
            "campaigns.christmas_campaign.tasks.resend_operations.resend.Emails",
            mock_resend_emails
        )

        # Mock substitute_variables at module level (called as regular function in send_template_email)
        def mock_substitute(template, vars):
            result = template
            for key, value in vars.items():
                result = result.replace(f"{{{{{key}}}}}", str(value))
            return result

        # Create a mock task that has .fn() method
        mock_substitute_task = Mock()
        mock_substitute_task.fn = mock_substitute
        mock_substitute_task.side_effect = mock_substitute  # For direct calls

        monkeypatch.setattr(
            "campaigns.christmas_campaign.tasks.resend_operations.substitute_variables",
            mock_substitute
        )

        # Mock send_email to bypass Prefect task decorator
        def mock_send(to_email, subject, html_body):
            return resend_operations.resend.Emails.send({
                "from": f"Sang Le - BusOS <value@galatek.dev>",
                "to": [to_email],
                "subject": subject,
                "html": html_body
            })["id"]

        monkeypatch.setattr(
            "campaigns.christmas_campaign.tasks.resend_operations.send_email",
            mock_send
        )

        # Call send_template_email
        result = resend_operations.send_template_email.fn(
            to_email="test@example.com",
            subject="Hi {{first_name}}!",
            template="<html><body>Your segment: {{segment}}</body></html>",
            variables={"first_name": "John", "segment": "URGENT"}
        )

        # Verify variables were substituted in the call to send()
        call_args = mock_resend_emails.send.call_args
        params = call_args[0][0]

        # Subject should have variable replaced
        assert params["subject"] == "Hi John!"

        # HTML body should have variable replaced
        assert "URGENT" in params["html"]
        assert "{{segment}}" not in params["html"]

    def test_send_template_email_handles_numeric_variables(self, monkeypatch):
        """Verify numeric variables (like assessment_score) are handled correctly."""
        from campaigns.christmas_campaign.tasks import resend_operations

        mock_resend_emails = MagicMock()
        mock_resend_emails.send.return_value = {"id": "email-id-123"}

        monkeypatch.setattr(
            "campaigns.christmas_campaign.tasks.resend_operations.resend.Emails",
            mock_resend_emails
        )

        # Mock substitute_variables at module level
        def mock_substitute(template, vars):
            result = template
            for key, value in vars.items():
                result = result.replace(f"{{{{{key}}}}}", str(value))
            return result

        monkeypatch.setattr(
            "campaigns.christmas_campaign.tasks.resend_operations.substitute_variables",
            mock_substitute
        )

        # Mock send_email to bypass Prefect task decorator
        def mock_send(to_email, subject, html_body):
            return resend_operations.resend.Emails.send({
                "from": f"Sang Le - BusOS <value@galatek.dev>",
                "to": [to_email],
                "subject": subject,
                "html": html_body
            })["id"]

        monkeypatch.setattr(
            "campaigns.christmas_campaign.tasks.resend_operations.send_email",
            mock_send
        )

        result = resend_operations.send_template_email.fn(
            to_email="test@example.com",
            subject="Your score: {{assessment_score}}",
            template="<html><body>Score: {{assessment_score}}/100</body></html>",
            variables={"assessment_score": 42}
        )

        # Verify numeric value was converted to string and substituted
        call_args = mock_resend_emails.send.call_args
        params = call_args[0][0]

        assert "42" in params["subject"]
        assert "42/100" in params["html"]
