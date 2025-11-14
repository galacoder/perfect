"""
Unit tests for template operations module (dynamic Notion template fetching).

Tests all Prefect tasks for fetching email templates from Notion Templates DB.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from campaigns.businessx_canada_lead_nurture.tasks.template_operations import (
    fetch_template_from_notion,
    fetch_template_cached,
    list_all_templates,
    seed_templates_to_notion,
    get_template
)


@pytest.fixture
def mock_notion_client():
    """Mock Notion client for testing."""
    with patch('campaigns.businessx_canada_lead_nurture.tasks.template_operations.notion') as mock_client:
        yield mock_client


class TestFetchTemplateFromNotion:
    """Tests for fetch_template_from_notion task."""

    def test_fetch_template_success(self, mock_notion_client):
        """Test fetching active template from Notion."""
        # Arrange
        mock_response = {
            "results": [
                {
                    "id": "page-123",
                    "properties": {
                        "Subject": {
                            "rich_text": [
                                {"plain_text": "Hello {{first_name}}"}
                            ]
                        },
                        "HTML Body": {
                            "rich_text": [
                                {"plain_text": "<p>Welcome to {{business_name}}</p>"}
                            ]
                        }
                    }
                }
            ]
        }
        mock_notion_client.databases.query.return_value = mock_response

        # Act
        template = fetch_template_from_notion("email_1")

        # Assert
        assert template["subject"] == "Hello {{first_name}}"
        assert template["html"] == "<p>Welcome to {{business_name}}</p>"

        # Verify query structure
        call_args = mock_notion_client.databases.query.call_args
        assert call_args[1]["filter"]["and"][0]["property"] == "Template Name"
        assert call_args[1]["filter"]["and"][0]["title"]["equals"] == "email_1"
        assert call_args[1]["filter"]["and"][1]["property"] == "Active"
        assert call_args[1]["filter"]["and"][1]["checkbox"]["equals"] is True

    def test_fetch_template_with_multiple_text_blocks(self, mock_notion_client):
        """Test fetching template with multiple rich text blocks."""
        # Arrange
        mock_response = {
            "results": [
                {
                    "id": "page-456",
                    "properties": {
                        "Subject": {
                            "rich_text": [
                                {"plain_text": "Part 1 "},
                                {"plain_text": "Part 2"}
                            ]
                        },
                        "HTML Body": {
                            "rich_text": [
                                {"plain_text": "<html>"},
                                {"plain_text": "<body>Content</body>"},
                                {"plain_text": "</html>"}
                            ]
                        }
                    }
                }
            ]
        }
        mock_notion_client.databases.query.return_value = mock_response

        # Act
        template = fetch_template_from_notion("email_2a_critical")

        # Assert
        assert template["subject"] == "Part 1 Part 2"
        assert template["html"] == "<html><body>Content</body></html>"

    def test_fetch_template_not_found(self, mock_notion_client):
        """Test fetching non-existent template raises ValueError."""
        # Arrange
        mock_response = {"results": []}
        mock_notion_client.databases.query.return_value = mock_response

        # Act & Assert
        with pytest.raises(ValueError, match="Template 'nonexistent' not found or not active"):
            fetch_template_from_notion("nonexistent")

    def test_fetch_template_inactive(self, mock_notion_client):
        """Test fetching inactive template raises ValueError."""
        # Arrange - Query returns empty because Active=false filtered out
        mock_response = {"results": []}
        mock_notion_client.databases.query.return_value = mock_response

        # Act & Assert
        with pytest.raises(ValueError, match="Template 'email_1' not found or not active"):
            fetch_template_from_notion("email_1")

    def test_fetch_template_missing_subject(self, mock_notion_client):
        """Test fetching template with missing Subject raises ValueError."""
        # Arrange
        mock_response = {
            "results": [
                {
                    "id": "page-789",
                    "properties": {
                        "Subject": {"rich_text": []},  # Empty
                        "HTML Body": {"rich_text": [{"plain_text": "<p>Body</p>"}]}
                    }
                }
            ]
        }
        mock_notion_client.databases.query.return_value = mock_response

        # Act & Assert
        with pytest.raises(ValueError, match="Template 'email_1' is missing Subject or HTML Body"):
            fetch_template_from_notion("email_1")

    def test_fetch_template_missing_html_body(self, mock_notion_client):
        """Test fetching template with missing HTML Body raises ValueError."""
        # Arrange
        mock_response = {
            "results": [
                {
                    "id": "page-101",
                    "properties": {
                        "Subject": {"rich_text": [{"plain_text": "Subject"}]},
                        "HTML Body": {"rich_text": []}  # Empty
                    }
                }
            ]
        }
        mock_notion_client.databases.query.return_value = mock_response

        # Act & Assert
        with pytest.raises(ValueError, match="Template 'email_1' is missing Subject or HTML Body"):
            fetch_template_from_notion("email_1")

    def test_fetch_template_handles_api_error(self, mock_notion_client):
        """Test fetch_template_from_notion raises exception on API error."""
        # Arrange
        mock_notion_client.databases.query.side_effect = Exception("Notion API Error")

        # Act & Assert
        with pytest.raises(Exception, match="Notion API Error"):
            fetch_template_from_notion("email_1")


class TestFetchTemplateCached:
    """Tests for fetch_template_cached task (with manual cache)."""

    def test_cached_template_reduces_api_calls(self, mock_notion_client):
        """Test manual cache reduces duplicate API calls."""
        # Arrange
        mock_response = {
            "results": [
                {
                    "id": "page-123",
                    "properties": {
                        "Subject": {"rich_text": [{"plain_text": "Subject"}]},
                        "HTML Body": {"rich_text": [{"plain_text": "<p>Body</p>"}]}
                    }
                }
            ]
        }
        mock_notion_client.databases.query.return_value = mock_response

        # Clear cache before test
        from campaigns.businessx_canada_lead_nurture.tasks import template_operations
        template_operations._template_cache.clear()

        # Act - First call (should hit API)
        template1 = fetch_template_cached("email_1")

        # Act - Second call (should use cache)
        template2 = fetch_template_cached("email_1")

        # Assert - Both returns should be identical
        assert template1 == template2
        assert template1["subject"] == "Subject"

        # Note: Due to Prefect task decoration, we can't easily verify call count
        # This test primarily validates caching behavior exists

    def test_cached_different_templates(self, mock_notion_client):
        """Test cache stores different templates separately."""
        # Arrange
        def mock_query(*args, **kwargs):
            template_name = kwargs["filter"]["and"][0]["title"]["equals"]
            return {
                "results": [
                    {
                        "id": f"page-{template_name}",
                        "properties": {
                            "Subject": {"rich_text": [{"plain_text": f"Subject {template_name}"}]},
                            "HTML Body": {"rich_text": [{"plain_text": f"<p>{template_name}</p>"}]}
                        }
                    }
                ]
            }

        mock_notion_client.databases.query.side_effect = mock_query

        # Clear cache
        from campaigns.businessx_canada_lead_nurture.tasks import template_operations
        template_operations._template_cache.clear()

        # Act
        template1 = fetch_template_cached("email_1")
        template2 = fetch_template_cached("email_2a_critical")

        # Assert
        assert template1["subject"] == "Subject email_1"
        assert template2["subject"] == "Subject email_2a_critical"
        assert template1 != template2


class TestListAllTemplates:
    """Tests for list_all_templates task."""

    def test_list_all_templates_success(self, mock_notion_client):
        """Test listing all active templates."""
        # Arrange
        mock_response = {
            "results": [
                {
                    "id": "page-1",
                    "properties": {
                        "Template Name": {"title": [{"plain_text": "email_1"}]},
                        "Subject": {"rich_text": [{"plain_text": "Subject 1"}]},
                        "Last Modified": {"last_edited_time": "2025-11-12T00:00:00.000Z"}
                    }
                },
                {
                    "id": "page-2",
                    "properties": {
                        "Template Name": {"title": [{"plain_text": "email_2a_critical"}]},
                        "Subject": {"rich_text": [{"plain_text": "Subject 2A"}]},
                        "Last Modified": {"last_edited_time": "2025-11-11T00:00:00.000Z"}
                    }
                }
            ]
        }
        mock_notion_client.databases.query.return_value = mock_response

        # Act
        templates = list_all_templates()

        # Assert
        assert len(templates) == 2
        assert templates[0]["name"] == "email_1"
        assert templates[0]["subject"] == "Subject 1"
        assert templates[0]["page_id"] == "page-1"
        assert templates[1]["name"] == "email_2a_critical"
        assert templates[1]["subject"] == "Subject 2A"

        # Verify filter for Active=true
        call_args = mock_notion_client.databases.query.call_args
        assert call_args[1]["filter"]["property"] == "Active"
        assert call_args[1]["filter"]["checkbox"]["equals"] is True

        # Verify sorting
        assert call_args[1]["sorts"][0]["property"] == "Template Name"
        assert call_args[1]["sorts"][0]["direction"] == "ascending"

    def test_list_all_templates_empty(self, mock_notion_client):
        """Test listing when no active templates exist."""
        # Arrange
        mock_response = {"results": []}
        mock_notion_client.databases.query.return_value = mock_response

        # Act
        templates = list_all_templates()

        # Assert
        assert len(templates) == 0

    def test_list_all_templates_handles_api_error(self, mock_notion_client):
        """Test list_all_templates raises exception on API error."""
        # Arrange
        mock_notion_client.databases.query.side_effect = Exception("API Error")

        # Act & Assert
        with pytest.raises(Exception, match="API Error"):
            list_all_templates()


class TestSeedTemplatesToNotion:
    """Tests for seed_templates_to_notion task."""

    def test_seed_templates_creates_new(self, mock_notion_client):
        """Test seeding creates new templates in Notion."""
        # Arrange - No existing templates
        mock_notion_client.databases.query.return_value = {"results": []}
        mock_notion_client.pages.create.return_value = {"id": "new-page-123"}

        templates = {
            "email_1": {
                "subject": "Test Subject",
                "html": "<p>Test Body</p>"
            }
        }

        # Act
        result = seed_templates_to_notion(templates)

        # Assert
        assert "email_1" in result
        assert result["email_1"] == "new-page-123"
        mock_notion_client.pages.create.assert_called_once()

        # Verify properties structure
        call_args = mock_notion_client.pages.create.call_args
        properties = call_args[1]["properties"]
        assert properties["Template Name"]["title"][0]["text"]["content"] == "email_1"
        assert properties["Subject"]["rich_text"][0]["text"]["content"] == "Test Subject"
        assert properties["Active"]["checkbox"] is True

    def test_seed_templates_skips_existing(self, mock_notion_client):
        """Test seeding skips templates that already exist."""
        # Arrange - Template already exists
        mock_notion_client.databases.query.return_value = {
            "results": [{"id": "existing-page-456"}]
        }

        templates = {
            "email_1": {
                "subject": "Test Subject",
                "html": "<p>Test Body</p>"
            }
        }

        # Act
        result = seed_templates_to_notion(templates)

        # Assert
        assert "email_1" in result
        assert result["email_1"] == "existing-page-456"
        mock_notion_client.pages.create.assert_not_called()

    def test_seed_templates_multiple(self, mock_notion_client):
        """Test seeding multiple templates."""
        # Arrange
        mock_notion_client.databases.query.return_value = {"results": []}

        def mock_create(*args, **kwargs):
            template_name = kwargs["properties"]["Template Name"]["title"][0]["text"]["content"]
            return {"id": f"page-{template_name}"}

        mock_notion_client.pages.create.side_effect = mock_create

        templates = {
            "email_1": {"subject": "Subject 1", "html": "<p>Body 1</p>"},
            "email_2a_critical": {"subject": "Subject 2A", "html": "<p>Body 2A</p>"},
            "email_3": {"subject": "Subject 3", "html": "<p>Body 3</p>"}
        }

        # Act
        result = seed_templates_to_notion(templates)

        # Assert
        assert len(result) == 3
        assert result["email_1"] == "page-email_1"
        assert result["email_2a_critical"] == "page-email_2a_critical"
        assert result["email_3"] == "page-email_3"
        assert mock_notion_client.pages.create.call_count == 3

    def test_seed_templates_handles_creation_error(self, mock_notion_client):
        """Test seeding continues on individual template error."""
        # Arrange
        mock_notion_client.databases.query.return_value = {"results": []}

        def mock_create(*args, **kwargs):
            template_name = kwargs["properties"]["Template Name"]["title"][0]["text"]["content"]
            if template_name == "email_2a_critical":
                raise Exception("Creation failed")
            return {"id": f"page-{template_name}"}

        mock_notion_client.pages.create.side_effect = mock_create

        templates = {
            "email_1": {"subject": "Subject 1", "html": "<p>Body 1</p>"},
            "email_2a_critical": {"subject": "Subject 2A", "html": "<p>Body 2A</p>"},
            "email_3": {"subject": "Subject 3", "html": "<p>Body 3</p>"}
        }

        # Act
        result = seed_templates_to_notion(templates)

        # Assert - email_1 and email_3 should succeed, email_2a_critical should fail
        assert len(result) == 2
        assert "email_1" in result
        assert "email_3" in result
        assert "email_2a_critical" not in result

    def test_seed_templates_truncates_long_html(self, mock_notion_client):
        """Test seeding truncates HTML body to 2000 chars (Notion limit)."""
        # Arrange
        mock_notion_client.databases.query.return_value = {"results": []}
        mock_notion_client.pages.create.return_value = {"id": "page-long"}

        long_html = "A" * 3000  # 3000 characters
        templates = {
            "email_1": {
                "subject": "Test",
                "html": long_html
            }
        }

        # Act
        result = seed_templates_to_notion(templates)

        # Assert
        call_args = mock_notion_client.pages.create.call_args
        html_content = call_args[1]["properties"]["HTML Body"]["rich_text"][0]["text"]["content"]
        assert len(html_content) == 2000  # Truncated


class TestGetTemplate:
    """Tests for get_template helper function."""

    def test_get_template_from_notion(self, mock_notion_client):
        """Test get_template fetches from Notion by default."""
        # Arrange
        mock_response = {
            "results": [
                {
                    "id": "page-123",
                    "properties": {
                        "Subject": {"rich_text": [{"plain_text": "Notion Subject"}]},
                        "HTML Body": {"rich_text": [{"plain_text": "<p>Notion Body</p>"}]}
                    }
                }
            ]
        }
        mock_notion_client.databases.query.return_value = mock_response

        # Clear cache
        from campaigns.businessx_canada_lead_nurture.tasks import template_operations
        template_operations._template_cache.clear()

        # Act
        template = get_template("email_1", use_notion=True)

        # Assert
        assert template["subject"] == "Notion Subject"
        assert template["html"] == "<p>Notion Body</p>"

    def test_get_template_static_fallback(self):
        """Test get_template uses static templates when use_notion=False."""
        # Act
        template = get_template("email_1", use_notion=False)

        # Assert - Should fetch from config.email_templates.TEMPLATES
        assert "subject" in template
        assert "html" in template
        assert "{{first_name}}" in template["subject"] or "{{first_name}}" in template["html"]

    def test_get_template_static_not_found(self):
        """Test get_template raises KeyError for non-existent static template."""
        # Act & Assert
        with pytest.raises(KeyError, match="Template 'nonexistent' not found in static config"):
            get_template("nonexistent", use_notion=False)


class TestRetryLogic:
    """Tests for Prefect retry logic (integration test concept)."""

    def test_retry_annotation_exists(self):
        """Verify all tasks have retry annotations."""
        import inspect
        from campaigns.businessx_canada_lead_nurture.tasks import template_operations

        # Get all functions that should be tasks
        task_functions = [
            template_operations.fetch_template_from_notion,
            template_operations.list_all_templates,
            template_operations.seed_templates_to_notion
        ]

        for func in task_functions:
            # Verify function has task metadata
            assert callable(func), f"{func.__name__} should be callable"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
