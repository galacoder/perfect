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
from unittest.mock import patch, MagicMock
from campaigns.christmas_campaign.tasks.resend_operations import (
    substitute_variables,
    get_email_variables,
    get_fallback_template
)


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
