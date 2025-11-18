"""
Tests for Christmas Campaign email template seeding script.

This module tests the upload of email templates from config to Notion database.
Uses mocking for unit tests and provides integration test support.

Author: Automation Developer
Created: 2025-11-18
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from campaigns.christmas_campaign.config.email_templates_christmas import TEMPLATES


class TestTemplateConfig:
    """Test template configuration file."""

    def test_template_config_loads_7_templates(self):
        """Verify 7 templates defined in config."""
        assert len(TEMPLATES) == 7, f"Expected 7 templates, found {len(TEMPLATES)}"

    def test_template_has_required_fields(self):
        """Verify each template has required fields."""
        required_fields = ["subject", "html_body", "campaign", "email_number", "segment", "active"]

        for template_id, template_data in TEMPLATES.items():
            for field in required_fields:
                assert field in template_data, f"Template {template_id} missing field: {field}"

    def test_template_preserves_variables(self):
        """Verify {{variable}} placeholders not escaped."""
        # Check Email 1 for variable preservation
        email_1 = TEMPLATES["christmas_email_1"]

        # These variables must be in the template
        required_variables = [
            "{{first_name}}",
            "{{GPSScore}}",
            "{{WeakestSystem1}}",
            "{{TotalRevenueLeak}}"
        ]

        for var in required_variables:
            assert var in email_1["html_body"], f"Variable {var} not found in Email 1"

    def test_all_templates_have_unique_email_numbers(self):
        """Verify each template has unique email number."""
        email_numbers = [template["email_number"] for template in TEMPLATES.values()]
        assert len(email_numbers) == len(set(email_numbers)), "Duplicate email numbers found"

    def test_template_ids_match_naming_convention(self):
        """Verify template_ids follow christmas_email_N pattern."""
        valid_ids = [
            "christmas_email_1",
            "christmas_email_2",
            "christmas_email_3",
            "christmas_email_4",
            "christmas_email_5",
            "christmas_email_6",
            "christmas_email_7"
        ]

        for template_id in TEMPLATES.keys():
            assert template_id in valid_ids, f"Invalid template_id: {template_id}"


class TestUploadFunctions:
    """Test upload functions for Notion integration."""

    @patch('campaigns.christmas_campaign.scripts.seed_email_templates.notion')
    def test_upload_template_creates_new_page(self, mock_notion):
        """Test creating new template in Notion when it doesn't exist."""
        from campaigns.christmas_campaign.scripts.seed_email_templates import upload_template_to_notion

        # Mock: Template doesn't exist
        mock_notion.databases.query.return_value = {"results": []}
        mock_notion.pages.create.return_value = {"id": "new-page-123"}

        template_data = TEMPLATES["christmas_email_1"]
        result = upload_template_to_notion("christmas_email_1", template_data)

        # Verify create was called
        assert mock_notion.pages.create.called
        assert result == "new-page-123"

    @patch('campaigns.christmas_campaign.scripts.seed_email_templates.notion')
    def test_upload_template_updates_existing_page(self, mock_notion):
        """Test updating existing template in Notion."""
        from campaigns.christmas_campaign.scripts.seed_email_templates import upload_template_to_notion

        # Mock: Template exists
        mock_notion.databases.query.return_value = {"results": [{"id": "existing-page-456"}]}
        mock_notion.pages.update.return_value = {"id": "existing-page-456"}

        template_data = TEMPLATES["christmas_email_1"]
        result = upload_template_to_notion("christmas_email_1", template_data)

        # Verify update was called, not create
        assert mock_notion.pages.update.called
        assert not mock_notion.pages.create.called
        assert result == "existing-page-456"

    @patch('campaigns.christmas_campaign.scripts.seed_email_templates.notion')
    def test_find_existing_template_returns_none_when_not_found(self, mock_notion):
        """Test finding template that doesn't exist."""
        from campaigns.christmas_campaign.scripts.seed_email_templates import find_existing_template

        mock_notion.databases.query.return_value = {"results": []}

        result = find_existing_template("christmas_email_1")

        assert result is None

    @patch('campaigns.christmas_campaign.scripts.seed_email_templates.notion')
    def test_find_existing_template_returns_page_when_found(self, mock_notion):
        """Test finding template that exists."""
        from campaigns.christmas_campaign.scripts.seed_email_templates import find_existing_template

        expected_page = {"id": "page-789", "properties": {}}
        mock_notion.databases.query.return_value = {"results": [expected_page]}

        result = find_existing_template("christmas_email_1")

        assert result == expected_page

    @patch('campaigns.christmas_campaign.scripts.seed_email_templates.upload_template_to_notion')
    def test_seed_all_templates_uploads_7_templates(self, mock_upload):
        """Test uploading all 7 templates."""
        from campaigns.christmas_campaign.scripts.seed_email_templates import seed_all_templates

        # Mock upload to return page IDs
        mock_upload.side_effect = [f"page-{i}" for i in range(1, 8)]

        result = seed_all_templates()

        assert len(result) == 7
        assert mock_upload.call_count == 7


@pytest.mark.integration
class TestIntegration:
    """Integration tests with real Notion API (requires NOTION_TOKEN in .env)."""

    def test_full_upload_flow_integration(self):
        """
        Integration test: upload all templates to real Notion database.

        NOTE: This test requires valid NOTION_TOKEN and NOTION_EMAIL_TEMPLATES_DB_ID
        in .env file. Run with: pytest -m integration
        """
        from campaigns.christmas_campaign.scripts.seed_email_templates import seed_all_templates
        from campaigns.christmas_campaign.tasks.notion_operations import fetch_email_template

        # Upload all templates
        results = seed_all_templates()
        assert len(results) == 7

        # Verify each template can be fetched
        for template_id in results.keys():
            template = fetch_email_template(template_id)
            assert template is not None, f"Failed to fetch {template_id}"
            assert "subject" in template
            assert "html_body" in template

            # Verify variables preserved
            assert "{{" in template["html_body"], f"Variables missing in {template_id}"
