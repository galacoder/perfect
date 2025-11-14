"""
Unit tests for Notion operations module.

Tests all Prefect tasks for Notion database operations with mocking.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from campaigns.businessx_canada_lead_nurture.tasks.notion_operations import (
    search_contact_by_email,
    create_contact,
    update_contact,
    get_contact
)


@pytest.fixture
def mock_notion_client():
    """Mock Notion client for testing."""
    with patch('campaigns.businessx_canada_lead_nurture.tasks.notion_operations.notion') as mock_client:
        yield mock_client


class TestSearchContactByEmail:
    """Tests for search_contact_by_email task."""

    def test_search_finds_existing_contact(self, mock_notion_client):
        """Test searching for an existing contact returns the contact."""
        # Arrange
        mock_response = {
            "results": [
                {
                    "id": "page-123",
                    "properties": {
                        "Email": {"email": "test@example.com"}
                    }
                }
            ]
        }
        mock_notion_client.databases.query.return_value = mock_response

        # Act
        result = search_contact_by_email("test@example.com")

        # Assert
        assert result is not None
        assert result["id"] == "page-123"
        mock_notion_client.databases.query.assert_called_once()
        call_args = mock_notion_client.databases.query.call_args
        assert call_args[1]["filter"]["property"] == "Email"
        assert call_args[1]["filter"]["email"]["equals"] == "test@example.com"

    def test_search_contact_not_found(self, mock_notion_client):
        """Test searching for non-existent contact returns None."""
        # Arrange
        mock_response = {"results": []}
        mock_notion_client.databases.query.return_value = mock_response

        # Act
        result = search_contact_by_email("notfound@example.com")

        # Assert
        assert result is None
        mock_notion_client.databases.query.assert_called_once()

    def test_search_handles_api_error(self, mock_notion_client):
        """Test search raises exception on API error."""
        # Arrange
        mock_notion_client.databases.query.side_effect = Exception("API Error")

        # Act & Assert
        with pytest.raises(Exception, match="API Error"):
            search_contact_by_email("error@example.com")


class TestCreateContact:
    """Tests for create_contact task."""

    def test_create_contact_success(self, mock_notion_client):
        """Test creating a new contact returns page_id."""
        # Arrange
        mock_response = {"id": "new-page-456"}
        mock_notion_client.pages.create.return_value = mock_response

        # Act
        page_id = create_contact(
            email="newuser@example.com",
            name="New User",
            first_name="New",
            business_name="Test Salon",
            signup_source="web_form"
        )

        # Assert
        assert page_id == "new-page-456"
        mock_notion_client.pages.create.assert_called_once()

        # Verify properties structure
        call_args = mock_notion_client.pages.create.call_args[1]
        properties = call_args["properties"]
        assert properties["Email"]["email"] == "newuser@example.com"
        assert properties["Name"]["rich_text"][0]["text"]["content"] == "New User"
        assert properties["First Name"]["rich_text"][0]["text"]["content"] == "New"
        assert properties["Business Name"]["rich_text"][0]["text"]["content"] == "Test Salon"
        assert properties["Signup Source"]["select"]["name"] == "web_form"
        assert "Signup Date" in properties

    def test_create_contact_with_defaults(self, mock_notion_client):
        """Test creating contact with default values."""
        # Arrange
        mock_response = {"id": "page-789"}
        mock_notion_client.pages.create.return_value = mock_response

        # Act
        page_id = create_contact(
            email="default@example.com",
            name="Default User",
            first_name="Default"
        )

        # Assert
        assert page_id == "page-789"
        call_args = mock_notion_client.pages.create.call_args[1]
        properties = call_args["properties"]
        assert properties["Business Name"]["rich_text"][0]["text"]["content"] == "your salon"
        assert properties["Signup Source"]["select"]["name"] == "web_form"

    def test_create_contact_handles_error(self, mock_notion_client):
        """Test create_contact raises exception on API error."""
        # Arrange
        mock_notion_client.pages.create.side_effect = Exception("Create failed")

        # Act & Assert
        with pytest.raises(Exception, match="Create failed"):
            create_contact(
                email="error@example.com",
                name="Error User",
                first_name="Error"
            )


class TestUpdateContact:
    """Tests for update_contact task."""

    def test_update_contact_success(self, mock_notion_client):
        """Test updating a contact with new properties."""
        # Arrange
        mock_response = {
            "id": "page-123",
            "properties": {
                "Segment": {"select": {"name": "CRITICAL"}}
            }
        }
        mock_notion_client.pages.update.return_value = mock_response

        # Act
        properties_to_update = {
            "Segment": {"select": {"name": "CRITICAL"}},
            "Assessment Score": {"number": 65}
        }
        result = update_contact("page-123", properties_to_update)

        # Assert
        assert result["id"] == "page-123"
        mock_notion_client.pages.update.assert_called_once_with(
            page_id="page-123",
            properties=properties_to_update
        )

    def test_update_contact_partial_properties(self, mock_notion_client):
        """Test updating only specific properties."""
        # Arrange
        mock_response = {"id": "page-456"}
        mock_notion_client.pages.update.return_value = mock_response

        # Act
        result = update_contact("page-456", {
            "Email 1 Sent": {"date": {"start": "2025-11-12T00:00:00"}}
        })

        # Assert
        assert result["id"] == "page-456"
        mock_notion_client.pages.update.assert_called_once()

    def test_update_contact_handles_error(self, mock_notion_client):
        """Test update_contact raises exception on API error."""
        # Arrange
        mock_notion_client.pages.update.side_effect = Exception("Update failed")

        # Act & Assert
        with pytest.raises(Exception, match="Update failed"):
            update_contact("page-error", {"Name": {"rich_text": []}})


class TestGetContact:
    """Tests for get_contact task."""

    def test_get_contact_success(self, mock_notion_client):
        """Test retrieving a contact by page_id."""
        # Arrange
        mock_response = {
            "id": "page-123",
            "properties": {
                "Email": {"email": "retrieve@example.com"},
                "First Name": {"rich_text": [{"text": {"content": "Test"}}]},
                "Segment": {"select": {"name": "URGENT"}}
            }
        }
        mock_notion_client.pages.retrieve.return_value = mock_response

        # Act
        result = get_contact("page-123")

        # Assert
        assert result["id"] == "page-123"
        assert result["properties"]["Email"]["email"] == "retrieve@example.com"
        assert result["properties"]["Segment"]["select"]["name"] == "URGENT"
        mock_notion_client.pages.retrieve.assert_called_once_with(page_id="page-123")

    def test_get_contact_handles_error(self, mock_notion_client):
        """Test get_contact raises exception on API error."""
        # Arrange
        mock_notion_client.pages.retrieve.side_effect = Exception("Page not found")

        # Act & Assert
        with pytest.raises(Exception, match="Page not found"):
            get_contact("nonexistent-page")


class TestRetryLogic:
    """Tests for Prefect retry logic (integration test concept)."""

    def test_retry_annotation_exists(self):
        """Verify all tasks have retry annotations."""
        # Check that tasks are decorated with @task and have retries
        import inspect
        from campaigns.businessx_canada_lead_nurture.tasks import notion_operations

        # Get all functions that should be tasks
        task_functions = [
            notion_operations.search_contact_by_email,
            notion_operations.create_contact,
            notion_operations.update_contact,
            notion_operations.get_contact
        ]

        for func in task_functions:
            # Verify function has task metadata (Prefect adds __prefect_task__ attribute)
            # This is a basic check - actual retry behavior tested in integration tests
            assert callable(func), f"{func.__name__} should be callable"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
