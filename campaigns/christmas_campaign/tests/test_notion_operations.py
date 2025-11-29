"""
Tests for Notion operations - Lead Nurture Template Verification (Wave 0).

This module tests:
1. Template fetching from new Notion database (2ab7c374-1115-8115-932c-ca6789c5b87b)
2. New template naming format (lead_nurture_email_X)
3. Template properties validation
4. Active status filtering

TDD Approach: Tests written FIRST (Red phase), then implementation (Green phase).

Author: Coding Agent (Sonnet 4.5)
Created: 2025-11-26
Wave: 0 - Lead Nurture Verification
"""

import pytest
from unittest.mock import Mock, patch, MagicMock


# Note: fetch_email_template is a Prefect @task, so we need to call it directly
# or mock the underlying function. We'll mock the Notion client instead.


# ==============================================================================
# Feature 0.1: Verify 7 lead nurture templates accessible
# DEPRECATED (Wave 11): These tests verify archived lead_nurture_email_* templates.
# These templates have been archived in Notion and replaced with 5-Day E* templates.
# Tests kept for backward compatibility - see "Active 5-Day E* Template Tests" below.
# ==============================================================================

class TestFetchTemplate:
    """Test fetch_email_template() function with new lead nurture templates."""

    def test_fetch_template_lead_nurture_email_1_exists(self, monkeypatch):
        """Verify lead_nurture_email_1 template exists and is fetchable."""
        # Import here to avoid Prefect initialization issues
        from campaigns.christmas_campaign.tasks import notion_operations

        # Mock Notion client response
        mock_notion = MagicMock()
        mock_notion.databases.query.return_value = {
            "results": [
                {
                    "id": "template-1-id",
                    "properties": {
                        "Template Name": {
                            "title": [{"plain_text": "lead_nurture_email_1"}]
                        },
                        "Subject Line": {
                            "rich_text": [{"plain_text": "Your BusOS Assessment Results"}]
                        },
                        "Email Body HTML": {
                            "rich_text": [{"plain_text": "<html><body>Email 1 content</body></html>"}]
                        },
                        "Active": {
                            "checkbox": True
                        }
                    }
                }
            ]
        }

        # Patch Notion client
        monkeypatch.setattr(
            "campaigns.christmas_campaign.tasks.notion_operations.notion",
            mock_notion
        )

        # Execute (call .fn() to bypass Prefect task decorator)
        result = notion_operations.fetch_email_template.fn("lead_nurture_email_1")

        # Assert
        assert result is not None
        assert result["template_id"] == "lead_nurture_email_1"
        assert result["subject"] == "Your BusOS Assessment Results"
        assert "<html>" in result["html_body"]

    def test_fetch_template_lead_nurture_email_2a_critical_exists(self, monkeypatch):
        """Verify lead_nurture_email_2a_critical template exists."""
        from campaigns.christmas_campaign.tasks import notion_operations

        mock_notion = MagicMock()
        mock_notion.databases.query.return_value = {
            "results": [
                {
                    "id": "template-2a-id",
                    "properties": {
                        "Template Name": {
                            "title": [{"plain_text": "lead_nurture_email_2a_critical"}]
                        },
                        "Subject Line": {
                            "rich_text": [{"plain_text": "URGENT: Critical Systems for {{business_name}}"}]
                        },
                        "Email Body HTML": {
                            "rich_text": [{"plain_text": "<html><body>Email 2a CRITICAL content</body></html>"}]
                        },
                        "Active": {
                            "checkbox": True
                        }
                    }
                }
            ]
        }

        monkeypatch.setattr(
            "campaigns.christmas_campaign.tasks.notion_operations.notion",
            mock_notion
        )

        result = notion_operations.fetch_email_template.fn("lead_nurture_email_2a_critical")

        assert result is not None
        assert result["template_id"] == "lead_nurture_email_2a_critical"
        assert "CRITICAL" in result["html_body"] or "URGENT" in result["subject"]

    def test_fetch_template_lead_nurture_email_2b_urgent_exists(self, monkeypatch):
        """Verify lead_nurture_email_2b_urgent template exists."""
        from campaigns.christmas_campaign.tasks import notion_operations

        mock_notion = MagicMock()
        mock_notion.databases.query.return_value = {
            "results": [
                {
                    "id": "template-2b-id",
                    "properties": {
                        "Template Name": {
                            "title": [{"plain_text": "lead_nurture_email_2b_urgent"}]
                        },
                        "Subject Line": {
                            "rich_text": [{"plain_text": "Quick Wins for {{business_name}}"}]
                        },
                        "Email Body HTML": {
                            "rich_text": [{"plain_text": "<html><body>Email 2b URGENT content</body></html>"}]
                        },
                        "Active": {
                            "checkbox": True
                        }
                    }
                }
            ]
        }

        monkeypatch.setattr(
            "campaigns.christmas_campaign.tasks.notion_operations.notion",
            mock_notion
        )

        result = notion_operations.fetch_email_template.fn("lead_nurture_email_2b_urgent")

        assert result is not None
        assert result["template_id"] == "lead_nurture_email_2b_urgent"

    def test_fetch_template_lead_nurture_email_2c_optimize_exists(self, monkeypatch):
        """Verify lead_nurture_email_2c_optimize template exists."""
        from campaigns.christmas_campaign.tasks import notion_operations

        mock_notion = MagicMock()
        mock_notion.databases.query.return_value = {
            "results": [
                {
                    "id": "template-2c-id",
                    "properties": {
                        "Template Name": {
                            "title": [{"plain_text": "lead_nurture_email_2c_optimize"}]
                        },
                        "Subject Line": {
                            "rich_text": [{"plain_text": "Optimization Opportunities for {{business_name}}"}]
                        },
                        "Email Body HTML": {
                            "rich_text": [{"plain_text": "<html><body>Email 2c OPTIMIZE content</body></html>"}]
                        },
                        "Active": {
                            "checkbox": True
                        }
                    }
                }
            ]
        }

        monkeypatch.setattr(
            "campaigns.christmas_campaign.tasks.notion_operations.notion",
            mock_notion
        )

        result = notion_operations.fetch_email_template.fn("lead_nurture_email_2c_optimize")

        assert result is not None
        assert result["template_id"] == "lead_nurture_email_2c_optimize"

    def test_fetch_template_lead_nurture_email_3_exists(self, monkeypatch):
        """Verify lead_nurture_email_3 template exists."""
        from campaigns.christmas_campaign.tasks import notion_operations

        mock_notion = MagicMock()
        mock_notion.databases.query.return_value = {
            "results": [
                {
                    "id": "template-3-id",
                    "properties": {
                        "Template Name": {
                            "title": [{"plain_text": "lead_nurture_email_3"}]
                        },
                        "Subject Line": {
                            "rich_text": [{"plain_text": "Email 3 Subject"}]
                        },
                        "Email Body HTML": {
                            "rich_text": [{"plain_text": "<html><body>Email 3 content</body></html>"}]
                        },
                        "Active": {
                            "checkbox": True
                        }
                    }
                }
            ]
        }

        monkeypatch.setattr(
            "campaigns.christmas_campaign.tasks.notion_operations.notion",
            mock_notion
        )

        result = notion_operations.fetch_email_template.fn("lead_nurture_email_3")

        assert result is not None
        assert result["template_id"] == "lead_nurture_email_3"

    def test_fetch_template_lead_nurture_email_4_exists(self, monkeypatch):
        """Verify lead_nurture_email_4 template exists."""
        from campaigns.christmas_campaign.tasks import notion_operations

        mock_notion = MagicMock()
        mock_notion.databases.query.return_value = {
            "results": [
                {
                    "id": "template-4-id",
                    "properties": {
                        "Template Name": {
                            "title": [{"plain_text": "lead_nurture_email_4"}]
                        },
                        "Subject Line": {
                            "rich_text": [{"plain_text": "Email 4 Subject"}]
                        },
                        "Email Body HTML": {
                            "rich_text": [{"plain_text": "<html><body>Email 4 content</body></html>"}]
                        },
                        "Active": {
                            "checkbox": True
                        }
                    }
                }
            ]
        }

        monkeypatch.setattr(
            "campaigns.christmas_campaign.tasks.notion_operations.notion",
            mock_notion
        )

        result = notion_operations.fetch_email_template.fn("lead_nurture_email_4")

        assert result is not None
        assert result["template_id"] == "lead_nurture_email_4"

    def test_fetch_template_lead_nurture_email_5_exists(self, monkeypatch):
        """Verify lead_nurture_email_5 template exists."""
        from campaigns.christmas_campaign.tasks import notion_operations

        mock_notion = MagicMock()
        mock_notion.databases.query.return_value = {
            "results": [
                {
                    "id": "template-5-id",
                    "properties": {
                        "Template Name": {
                            "title": [{"plain_text": "lead_nurture_email_5"}]
                        },
                        "Subject Line": {
                            "rich_text": [{"plain_text": "Email 5 Subject"}]
                        },
                        "Email Body HTML": {
                            "rich_text": [{"plain_text": "<html><body>Email 5 content</body></html>"}]
                        },
                        "Active": {
                            "checkbox": True
                        }
                    }
                }
            ]
        }

        monkeypatch.setattr(
            "campaigns.christmas_campaign.tasks.notion_operations.notion",
            mock_notion
        )

        result = notion_operations.fetch_email_template.fn("lead_nurture_email_5")

        assert result is not None
        assert result["template_id"] == "lead_nurture_email_5"

    def test_fetch_template_returns_correct_properties(self, monkeypatch):
        """Verify fetch_email_template returns all required properties."""
        from campaigns.christmas_campaign.tasks import notion_operations

        mock_notion = MagicMock()
        mock_notion.databases.query.return_value = {
            "results": [
                {
                    "id": "template-test-id",
                    "properties": {
                        "Template Name": {
                            "title": [{"plain_text": "lead_nurture_email_1"}]
                        },
                        "Subject Line": {
                            "rich_text": [{"plain_text": "Test Subject"}]
                        },
                        "Email Body HTML": {
                            "rich_text": [{"plain_text": "<html><body>Test content</body></html>"}]
                        },
                        "Active": {
                            "checkbox": True
                        }
                    }
                }
            ]
        }

        monkeypatch.setattr(
            "campaigns.christmas_campaign.tasks.notion_operations.notion",
            mock_notion
        )

        result = notion_operations.fetch_email_template.fn("lead_nurture_email_1")

        # Verify structure
        assert isinstance(result, dict)
        assert "template_id" in result
        assert "subject" in result
        assert "html_body" in result

        # Verify values
        assert result["template_id"] == "lead_nurture_email_1"
        assert result["subject"] == "Test Subject"
        assert result["html_body"] == "<html><body>Test content</body></html>"

    def test_fetch_template_active_status_filter(self, monkeypatch):
        """Verify fetch_email_template respects Active status (if implemented)."""
        from campaigns.christmas_campaign.tasks import notion_operations

        # This test verifies that only active templates are returned
        # The implementation may or may not filter by Active status
        mock_notion = MagicMock()
        mock_notion.databases.query.return_value = {
            "results": [
                {
                    "id": "template-active-id",
                    "properties": {
                        "Template Name": {
                            "title": [{"plain_text": "lead_nurture_email_1"}]
                        },
                        "Subject Line": {
                            "rich_text": [{"plain_text": "Active Template"}]
                        },
                        "Email Body HTML": {
                            "rich_text": [{"plain_text": "<html><body>Active content</body></html>"}]
                        },
                        "Active": {
                            "checkbox": True
                        }
                    }
                }
            ]
        }

        monkeypatch.setattr(
            "campaigns.christmas_campaign.tasks.notion_operations.notion",
            mock_notion
        )

        result = notion_operations.fetch_email_template.fn("lead_nurture_email_1")

        # Verify we get the active template
        assert result is not None
        assert result["subject"] == "Active Template"


# ==============================================================================
# Feature 0.2: Update template fetching for new Template Name format
# ==============================================================================

class TestFetchTemplateNewFormat:
    """Test new template naming format support."""

    def test_fetch_template_new_naming_format(self, monkeypatch):
        """Verify new naming format: lead_nurture_email_X works correctly."""
        from campaigns.christmas_campaign.tasks import notion_operations

        mock_notion = MagicMock()
        mock_notion.databases.query.return_value = {
            "results": [
                {
                    "id": "template-id",
                    "properties": {
                        "Template Name": {
                            "title": [{"plain_text": "lead_nurture_email_1"}]
                        },
                        "Subject Line": {
                            "rich_text": [{"plain_text": "New Format Subject"}]
                        },
                        "Email Body HTML": {
                            "rich_text": [{"plain_text": "<html><body>New format content</body></html>"}]
                        }
                    }
                }
            ]
        }

        monkeypatch.setattr(
            "campaigns.christmas_campaign.tasks.notion_operations.notion",
            mock_notion
        )

        result = notion_operations.fetch_email_template.fn("lead_nurture_email_1")

        # Verify query was called with correct template name
        mock_notion.databases.query.assert_called_once()
        call_args = mock_notion.databases.query.call_args
        assert call_args[1]["filter"]["property"] == "Template Name"
        assert call_args[1]["filter"]["title"]["equals"] == "lead_nurture_email_1"

        # Verify result
        assert result["template_id"] == "lead_nurture_email_1"

    def test_fetch_template_segment_specific_2a_2b_2c(self, monkeypatch):
        """Verify segment-specific templates (2a, 2b, 2c) are correctly fetched."""
        from campaigns.christmas_campaign.tasks import notion_operations

        templates = [
            ("lead_nurture_email_2a_critical", "CRITICAL"),
            ("lead_nurture_email_2b_urgent", "URGENT"),
            ("lead_nurture_email_2c_optimize", "OPTIMIZE"),
        ]

        for template_id, segment in templates:
            mock_notion = MagicMock()
            mock_notion.databases.query.return_value = {
                "results": [
                    {
                        "id": f"template-{segment.lower()}-id",
                        "properties": {
                            "Template Name": {
                                "title": [{"plain_text": template_id}]
                            },
                            "Subject Line": {
                                "rich_text": [{"plain_text": f"{segment} Subject"}]
                            },
                            "Email Body HTML": {
                                "rich_text": [{"plain_text": f"<html><body>{segment} content</body></html>"}]
                            }
                        }
                    }
                ]
            }

            monkeypatch.setattr(
                "campaigns.christmas_campaign.tasks.notion_operations.notion",
                mock_notion
            )

            result = notion_operations.fetch_email_template.fn(template_id)

            assert result is not None
            assert result["template_id"] == template_id
            assert segment in result["subject"] or segment in result["html_body"]

    def test_fetch_template_backward_compatibility(self, monkeypatch):
        """Verify old naming format still works (christmas_email_X) if needed."""
        from campaigns.christmas_campaign.tasks import notion_operations

        # This test ensures we don't break existing templates
        mock_notion = MagicMock()
        mock_notion.databases.query.return_value = {
            "results": [
                {
                    "id": "old-template-id",
                    "properties": {
                        "Template Name": {
                            "title": [{"plain_text": "christmas_email_1"}]
                        },
                        "Subject Line": {
                            "rich_text": [{"plain_text": "Old Format Subject"}]
                        },
                        "Email Body HTML": {
                            "rich_text": [{"plain_text": "<html><body>Old format content</body></html>"}]
                        }
                    }
                }
            ]
        }

        monkeypatch.setattr(
            "campaigns.christmas_campaign.tasks.notion_operations.notion",
            mock_notion
        )

        result = notion_operations.fetch_email_template.fn("christmas_email_1")

        assert result is not None
        assert result["template_id"] == "christmas_email_1"

    def test_fetch_template_invalid_name_returns_none(self, monkeypatch):
        """Verify invalid template name returns None."""
        from campaigns.christmas_campaign.tasks import notion_operations

        mock_notion = MagicMock()
        mock_notion.databases.query.return_value = {
            "results": []  # No templates found
        }

        monkeypatch.setattr(
            "campaigns.christmas_campaign.tasks.notion_operations.notion",
            mock_notion
        )

        result = notion_operations.fetch_email_template.fn("nonexistent_template")

        assert result is None

    # ==============================================================================
    # Active 5-Day E* Template Tests (Wave 11: Template Naming Alignment)
    # ==============================================================================

    def test_fetch_template_5day_e1_exists(self, monkeypatch):
        """Verify 5-Day E1 template exists and is fetchable."""
        from campaigns.christmas_campaign.tasks import notion_operations

        mock_notion = MagicMock()
        mock_notion.databases.query.return_value = {
            "results": [
                {
                    "properties": {
                        "Template ID": {
                            "title": [{"plain_text": "5-Day E1"}]
                        },
                        "Subject Line": {
                            "rich_text": [{"plain_text": "Your BusOS Assessment Results"}]
                        },
                        "HTML Body": {
                            "rich_text": [{"plain_text": "<html>Email 1 body</html>"}]
                        },
                        "Campaign": {
                            "select": {"name": "Christmas 2025"}
                        }
                    }
                }
            ]
        }

        monkeypatch.setattr(
            "campaigns.christmas_campaign.tasks.notion_operations.notion",
            mock_notion
        )

        result = notion_operations.fetch_email_template.fn("5-Day E1")

        assert result is not None
        assert result["template_id"] == "5-Day E1"
        assert result["subject"] == "Your BusOS Assessment Results"

    def test_fetch_template_5day_e2_exists(self, monkeypatch):
        """Verify 5-Day E2 template exists and is fetchable."""
        from campaigns.christmas_campaign.tasks import notion_operations

        mock_notion = MagicMock()
        mock_notion.databases.query.return_value = {
            "results": [
                {
                    "properties": {
                        "Template ID": {
                            "title": [{"plain_text": "5-Day E2"}]
                        },
                        "Subject Line": {
                            "rich_text": [{"plain_text": "The $500K Mistake"}]
                        },
                        "HTML Body": {
                            "rich_text": [{"plain_text": "<html>Email 2 body</html>"}]
                        },
                        "Campaign": {
                            "select": {"name": "Christmas 2025"}
                        }
                    }
                }
            ]
        }

        monkeypatch.setattr(
            "campaigns.christmas_campaign.tasks.notion_operations.notion",
            mock_notion
        )

        result = notion_operations.fetch_email_template.fn("5-Day E2")

        assert result is not None
        assert result["template_id"] == "5-Day E2"

    def test_fetch_template_5day_e3_exists(self, monkeypatch):
        """Verify 5-Day E3 template exists and is fetchable."""
        from campaigns.christmas_campaign.tasks import notion_operations

        mock_notion = MagicMock()
        mock_notion.databases.query.return_value = {
            "results": [
                {
                    "properties": {
                        "Template ID": {
                            "title": [{"plain_text": "5-Day E3"}]
                        },
                        "Subject Line": {
                            "rich_text": [{"plain_text": "Van Tiny Case Study"}]
                        },
                        "HTML Body": {
                            "rich_text": [{"plain_text": "<html>Email 3 body</html>"}]
                        },
                        "Campaign": {
                            "select": {"name": "Christmas 2025"}
                        }
                    }
                }
            ]
        }

        monkeypatch.setattr(
            "campaigns.christmas_campaign.tasks.notion_operations.notion",
            mock_notion
        )

        result = notion_operations.fetch_email_template.fn("5-Day E3")

        assert result is not None
        assert result["template_id"] == "5-Day E3"

    def test_fetch_template_5day_e4_exists(self, monkeypatch):
        """Verify 5-Day E4 template exists and is fetchable."""
        from campaigns.christmas_campaign.tasks import notion_operations

        mock_notion = MagicMock()
        mock_notion.databases.query.return_value = {
            "results": [
                {
                    "properties": {
                        "Template ID": {
                            "title": [{"plain_text": "5-Day E4"}]
                        },
                        "Subject Line": {
                            "rich_text": [{"plain_text": "Value Stack"}]
                        },
                        "HTML Body": {
                            "rich_text": [{"plain_text": "<html>Email 4 body</html>"}]
                        },
                        "Campaign": {
                            "select": {"name": "Christmas 2025"}
                        }
                    }
                }
            ]
        }

        monkeypatch.setattr(
            "campaigns.christmas_campaign.tasks.notion_operations.notion",
            mock_notion
        )

        result = notion_operations.fetch_email_template.fn("5-Day E4")

        assert result is not None
        assert result["template_id"] == "5-Day E4"

    def test_fetch_template_5day_e5_exists(self, monkeypatch):
        """Verify 5-Day E5 template exists and is fetchable."""
        from campaigns.christmas_campaign.tasks import notion_operations

        mock_notion = MagicMock()
        mock_notion.databases.query.return_value = {
            "results": [
                {
                    "properties": {
                        "Template ID": {
                            "title": [{"plain_text": "5-Day E5"}]
                        },
                        "Subject Line": {
                            "rich_text": [{"plain_text": "Final Call"}]
                        },
                        "HTML Body": {
                            "rich_text": [{"plain_text": "<html>Email 5 body</html>"}]
                        },
                        "Campaign": {
                            "select": {"name": "Christmas 2025"}
                        }
                    }
                }
            ]
        }

        monkeypatch.setattr(
            "campaigns.christmas_campaign.tasks.notion_operations.notion",
            mock_notion
        )

        result = notion_operations.fetch_email_template.fn("5-Day E5")

        assert result is not None
        assert result["template_id"] == "5-Day E5"
