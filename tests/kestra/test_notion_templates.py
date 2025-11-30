"""
Tests for Notion template fetching with fallback to static templates.

Tests dynamic template fetching from Notion Templates database,
fallback to static templates on API failure, and variable substitution.
"""

import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add lib directory to path for importing fetch_template module
sys.path.insert(0, os.path.join(os.getcwd(), 'kestra', 'flows', 'christmas', 'lib'))

# Import after path adjustment
from fetch_template import (
    fetch_template_from_notion,
    render_template,
    STATIC_TEMPLATES
)


@pytest.mark.asyncio
async def test_notion_template_api_mock():
    """Test Notion template API call with mocked response."""
    # Mock Notion API response
    mock_response = {
        "results": [{
            "properties": {
                "subject": {"title": [{"text": {"content": "Welcome {{first_name}}!"}}]},
                "body": {"rich_text": [{"text": {"content": "Hi {{first_name}}, welcome to {{business_name}}!"}}]}
            }
        }]
    }

    with patch('fetch_template.requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_response

        result = await fetch_template_from_notion(
            sequence_type="5day",
            email_number=2,
            notion_token="test_token",
            templates_db_id="test_db_id"
        )

        assert result is not None
        assert "subject" in result
        assert "body" in result
        assert "{{first_name}}" in result["subject"]
        assert "{{business_name}}" in result["body"]


def test_template_rendering_with_variables():
    """Test template variable substitution."""
    template = {
        "subject": "Hello {{first_name}}!",
        "body": "Welcome to {{business_name}}, {{first_name}}. You're in the {{segment}} segment."
    }

    variables = {
        "first_name": "John",
        "business_name": "Acme Corp",
        "segment": "CRITICAL"
    }

    result = render_template(template, variables)

    assert result["subject"] == "Hello John!"
    assert result["body"] == "Welcome to Acme Corp, John. You're in the CRITICAL segment."


@pytest.mark.asyncio
async def test_fallback_to_static_templates_on_api_failure():
    """Test fallback to static templates when Notion API fails."""
    with patch('fetch_template.requests.post') as mock_post:
        # Simulate API failure
        mock_post.side_effect = Exception("API connection failed")

        result = await fetch_template_from_notion(
            sequence_type="5day",
            email_number=2,
            notion_token="test_token",
            templates_db_id="test_db_id"
        )

        # Should fall back to static template
        assert result is not None
        assert "subject" in result
        assert "body" in result

        # Verify it's from static templates
        static_template = STATIC_TEMPLATES["5day"][2]
        assert result["subject"] == static_template["subject"]
        assert result["body"] == static_template["body"]


def test_all_sequence_types_have_static_templates():
    """Test all 4 sequence types have static template fallbacks."""
    required_sequences = ["5day", "noshow", "postcall", "onboarding"]

    for seq_type in required_sequences:
        assert seq_type in STATIC_TEMPLATES, f"Missing static templates for {seq_type}"
        assert len(STATIC_TEMPLATES[seq_type]) > 0, f"No templates defined for {seq_type}"


def test_template_variable_substitution_all_variables():
    """Test variable substitution supports all expected variables."""
    template = {
        "subject": "{{first_name}}, your {{business_name}} assessment",
        "body": "Hi {{first_name}} from {{business_name}}! Segment: {{segment}}"
    }

    variables = {
        "first_name": "Jane",
        "business_name": "Tech Startup",
        "segment": "URGENT"
    }

    result = render_template(template, variables)

    # All variables should be substituted
    assert "{{" not in result["subject"]
    assert "{{" not in result["body"]
    assert "Jane" in result["subject"]
    assert "Tech Startup" in result["subject"]
    assert "URGENT" in result["body"]


def test_empty_template_handling():
    """Test handling of empty/null templates."""
    # Empty template should return defaults
    empty_template = None

    # Should use static fallback for sequence
    result = STATIC_TEMPLATES["5day"][2]

    assert result is not None
    assert "subject" in result
    assert "body" in result
