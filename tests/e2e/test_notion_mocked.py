"""
Mocked tests for Christmas Campaign Notion operations.

This module tests Notion API functions with mocked API responses:
- search_contact_by_email() - Search for contact
- update_assessment_data() - Update assessment results
- track_email_sent() - Track email delivery
- update_contact_phase() - Update customer journey phase
- search_email_sequence_by_email() - Search for email sequence
- create_email_sequence() - Create new sequence
- fetch_email_template() - Fetch email template from Notion

Coverage target: 85%+ of notion_operations.py
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from campaigns.christmas_campaign.tasks.notion_operations import (
    search_contact_by_email,
    update_assessment_data,
    track_email_sent,
    update_contact_phase,
    search_email_sequence_by_email,
    create_email_sequence,
    fetch_email_template
)


# ===== search_contact_by_email() tests =====

class TestSearchContactByEmail:
    """Test search_contact_by_email() with mocked Notion API."""

    @patch('campaigns.christmas_campaign.tasks.notion_operations.notion')
    def test_search_contact_found(self, mock_client):
        """Contact found returns contact data."""
        # Mock Notion API response
        mock_client.databases.query.return_value = {
            "results": [{
                "id": "page-123",
                "properties": {
                    "email": {"email": "john@testcorp.com"},
                    "first_name": {"title": [{"plain_text": "John"}]},
                    "Assessment Score": {"number": 45}
                }
            }]
        }

        # Call function
        result = search_contact_by_email.fn("john@testcorp.com")

        # Verify result
        assert result is not None
        assert result["id"] == "page-123"
        assert "properties" in result

        # Verify API called correctly
        mock_client.databases.query.assert_called_once()
        call_kwargs = mock_client.databases.query.call_args.kwargs
        assert call_kwargs["filter"]["property"] == "email"

    @patch('campaigns.christmas_campaign.tasks.notion_operations.notion')
    def test_search_contact_not_found(self, mock_client):
        """Contact not found returns None."""
        # Mock empty results
        mock_client.databases.query.return_value = {"results": []}

        result = search_contact_by_email.fn("notfound@example.com")

        assert result is None

    @patch('campaigns.christmas_campaign.tasks.notion_operations.notion')
    def test_search_contact_api_error(self, mock_client):
        """API error raises exception."""
        mock_client.databases.query.side_effect = Exception("Notion API Error")

        with pytest.raises(Exception) as exc_info:
            search_contact_by_email.fn("test@example.com")

        assert "Notion API Error" in str(exc_info.value)


# ===== update_assessment_data() tests =====

class TestUpdateAssessmentData:
    """Test update_assessment_data() with mocked Notion API."""

    @patch('campaigns.christmas_campaign.tasks.notion_operations.notion')
    def test_update_assessment_data_success(self, mock_client):
        """Assessment data updated successfully."""
        mock_client.pages.update.return_value = {"id": "page-123"}

        result = update_assessment_data.fn(
            page_id="page-123",
            assessment_score=45,
            red_systems=2,
            orange_systems=2,
            yellow_systems=2,
            green_systems=2,
            segment="CRITICAL"
        )

        assert result["id"] == "page-123"

        # Verify update called
        mock_client.pages.update.assert_called_once()
        call_kwargs = mock_client.pages.update.call_args.kwargs
        assert call_kwargs["page_id"] == "page-123"
        assert "properties" in call_kwargs

    @patch('campaigns.christmas_campaign.tasks.notion_operations.notion')
    def test_update_assessment_data_with_defaults(self, mock_client):
        """Update with default values works."""
        mock_client.pages.update.return_value = {"id": "page-456"}

        result = update_assessment_data.fn(
            page_id="page-456",
            assessment_score=50,
            segment="OPTIMIZE"
        )

        assert result["id"] == "page-456"


# ===== track_email_sent() tests =====

class TestTrackEmailSent:
    """Test track_email_sent() with mocked Notion API."""

    @patch('campaigns.christmas_campaign.tasks.notion_operations.notion')
    def test_track_email_sent_success(self, mock_client):
        """Email tracking updated successfully."""
        mock_client.pages.update.return_value = {"id": "page-123"}

        result = track_email_sent.fn(
            page_id="page-123",
            email_number=1
        )

        assert result["id"] == "page-123"

        # Verify checkbox set to true
        call_kwargs = mock_client.pages.update.call_args.kwargs
        props = call_kwargs["properties"]
        assert "Christmas Email 1 Sent" in props
        assert props["Christmas Email 1 Sent"]["checkbox"] is True

    @patch('campaigns.christmas_campaign.tasks.notion_operations.notion')
    def test_track_all_emails(self, mock_client):
        """All email numbers (1-7) can be tracked."""
        mock_client.pages.update.return_value = {"id": "page-123"}

        for email_num in range(1, 8):
            track_email_sent.fn(page_id="page-123", email_number=email_num)

        # Verify 7 calls made
        assert mock_client.pages.update.call_count == 7


# ===== update_contact_phase() tests =====

class TestUpdateContactPhase:
    """Test update_contact_phase() with mocked Notion API."""

    @patch('campaigns.christmas_campaign.tasks.notion_operations.notion')
    def test_update_contact_phase_success(self, mock_client):
        """Contact phase updated successfully."""
        mock_client.pages.update.return_value = {"id": "page-123"}

        result = update_contact_phase.fn(
            page_id="page-123",
            phase="Phase 2A Done-For-You"
        )

        assert result["id"] == "page-123"

        # Verify phase property updated
        call_kwargs = mock_client.pages.update.call_args.kwargs
        props = call_kwargs["properties"]
        assert "Phase" in props
        assert props["Phase"]["select"]["name"] == "Phase 2A Done-For-You"

    @patch('campaigns.christmas_campaign.tasks.notion_operations.notion')
    def test_update_all_phases(self, mock_client):
        """All valid phases can be set."""
        mock_client.pages.update.return_value = {"id": "page-123"}

        phases = [
            "Phase 1 Assessment",
            "Phase 1 Diagnostic",
            "Phase 2A Done-For-You",
            "Phase 2B Coaching",
            "Phase 2C DIY"
        ]

        for phase in phases:
            update_contact_phase.fn(page_id="page-123", phase=phase)

        assert mock_client.pages.update.call_count == len(phases)


# ===== search_email_sequence_by_email() tests =====

class TestSearchEmailSequenceByEmail:
    """Test search_email_sequence_by_email() with mocked Notion API."""

    @patch('campaigns.christmas_campaign.tasks.notion_operations.notion')
    def test_search_sequence_found(self, mock_client):
        """Email sequence found returns sequence data."""
        mock_client.databases.query.return_value = {
            "results": [{
                "id": "sequence-123",
                "properties": {
                    "Email": {"email": "john@testcorp.com"},
                    "Campaign": {"select": {"name": "Christmas 2025"}},
                    "Segment": {"select": {"name": "CRITICAL"}}
                }
            }]
        }

        result = search_email_sequence_by_email.fn("john@testcorp.com")

        assert result is not None
        assert result["id"] == "sequence-123"

    @patch('campaigns.christmas_campaign.tasks.notion_operations.notion')
    def test_search_sequence_not_found(self, mock_client):
        """Sequence not found returns None."""
        mock_client.databases.query.return_value = {"results": []}

        result = search_email_sequence_by_email.fn("notfound@example.com")

        assert result is None


# ===== create_email_sequence() tests =====

class TestCreateEmailSequence:
    """Test create_email_sequence() with mocked Notion API."""

    @patch('campaigns.christmas_campaign.tasks.notion_operations.notion')
    def test_create_sequence_success(self, mock_client):
        """Email sequence created successfully."""
        mock_client.pages.create.return_value = {"id": "sequence-new-123"}

        result = create_email_sequence.fn(
            email="john@testcorp.com",
            first_name="John",
            business_name="Test Corp",
            assessment_score=45,
            red_systems=2,
            segment="CRITICAL"
        )

        assert result["id"] == "sequence-new-123"

        # Verify create called with correct properties
        mock_client.pages.create.assert_called_once()
        call_kwargs = mock_client.pages.create.call_args.kwargs
        assert "properties" in call_kwargs
        props = call_kwargs["properties"]
        assert "Email" in props
        assert "Campaign" in props
        assert "Segment" in props

    @patch('campaigns.christmas_campaign.tasks.notion_operations.notion')
    def test_create_sequence_all_segments(self, mock_client):
        """All segment types can be created."""
        mock_client.pages.create.return_value = {"id": "sequence-123"}

        segments = ["CRITICAL", "URGENT", "OPTIMIZE"]
        for segment in segments:
            create_email_sequence.fn(
                email="test@example.com",
                first_name="Test",
                business_name="Test Corp",
                assessment_score=50,
                segment=segment
            )

        assert mock_client.pages.create.call_count == len(segments)


# ===== fetch_email_template() tests =====

class TestFetchEmailTemplate:
    """Test fetch_email_template() with mocked Notion API."""

    @patch('campaigns.christmas_campaign.tasks.notion_operations.notion')
    def test_fetch_template_found(self, mock_client):
        """Template found returns template data."""
        mock_client.databases.query.return_value = {
            "results": [{
                "id": "template-123",
                "properties": {
                    "Template ID": {"title": [{"plain_text": "christmas_email_1"}]},
                    "Subject": {"rich_text": [{"plain_text": "Your BusOS Results"}]},
                    "HTML Body": {"rich_text": [{"plain_text": "<html>Hi {{first_name}}</html>"}]},
                    "Segment": {"select": {"name": "ALL"}}
                }
            }]
        }

        result = fetch_email_template.fn("christmas_email_1")

        assert result is not None
        assert "template_id" in result
        assert "subject" in result
        assert "html_body" in result

    @patch('campaigns.christmas_campaign.tasks.notion_operations.notion')
    def test_fetch_template_not_found(self, mock_client):
        """Template not found returns None."""
        mock_client.databases.query.return_value = {"results": []}

        result = fetch_email_template.fn("nonexistent_template")

        assert result is None

    @patch('campaigns.christmas_campaign.tasks.notion_operations.notion')
    def test_fetch_template_segment_specific(self, mock_client):
        """Segment-specific templates can be fetched."""
        mock_client.databases.query.return_value = {
            "results": [{
                "id": "template-2a",
                "properties": {
                    "Template ID": {"title": [{"plain_text": "christmas_email_2a_critical"}]},
                    "Subject": {"rich_text": [{"plain_text": "CRITICAL: Urgent Action"}]},
                    "HTML Body": {"rich_text": [{"plain_text": "<html>Critical segment</html>"}]},
                    "Segment": {"select": {"name": "CRITICAL"}}
                }
            }]
        }

        result = fetch_email_template.fn("christmas_email_2a_critical")

        assert result is not None
        assert "template_id" in result


# ===== update_booking_status() tests =====

class TestUpdateBookingStatus:
    """Test update_booking_status() with mocked Notion API."""

    @patch('campaigns.christmas_campaign.tasks.notion_operations.notion')
    def test_update_booking_booked_with_date(self, mock_client):
        """Booking status updated with call date."""
        mock_client.pages.update.return_value = {"id": "page-123"}

        from campaigns.christmas_campaign.tasks.notion_operations import update_booking_status

        result = update_booking_status.fn(
            page_id="page-123",
            status="Booked",
            call_date="2025-11-25"
        )

        assert result["id"] == "page-123"

        call_kwargs = mock_client.pages.update.call_args.kwargs
        props = call_kwargs["properties"]
        assert props["Booking Status"]["select"]["name"] == "Booked"
        assert "Diagnostic Call Date" in props
        assert props["Diagnostic Call Date"]["date"]["start"] == "2025-11-25"

    @patch('campaigns.christmas_campaign.tasks.notion_operations.notion')
    def test_update_booking_completed_no_date(self, mock_client):
        """Booking status updated without call date."""
        mock_client.pages.update.return_value = {"id": "page-456"}

        from campaigns.christmas_campaign.tasks.notion_operations import update_booking_status

        result = update_booking_status.fn(
            page_id="page-456",
            status="Completed"
        )

        assert result["id"] == "page-456"

        call_kwargs = mock_client.pages.update.call_args.kwargs
        props = call_kwargs["properties"]
        assert props["Booking Status"]["select"]["name"] == "Completed"
        assert "Diagnostic Call Date" not in props


# ===== update_email_sequence() tests =====

class TestUpdateEmailSequence:
    """Test update_email_sequence() with mocked Notion API."""

    @patch('campaigns.christmas_campaign.tasks.notion_operations.notion')
    def test_update_email_number(self, mock_client):
        """Update email sequence with email number."""
        mock_client.pages.update.return_value = {"id": "seq-123"}

        from campaigns.christmas_campaign.tasks.notion_operations import update_email_sequence

        result = update_email_sequence.fn(
            sequence_id="seq-123",
            email_number=3
        )

        assert result["id"] == "seq-123"

        call_kwargs = mock_client.pages.update.call_args.kwargs
        props = call_kwargs["properties"]
        assert "Email 3 Sent" in props
        assert "date" in props["Email 3 Sent"]

    @patch('campaigns.christmas_campaign.tasks.notion_operations.notion')
    def test_update_sequence_completed(self, mock_client):
        """Mark sequence as completed."""
        mock_client.pages.update.return_value = {"id": "seq-456"}

        from campaigns.christmas_campaign.tasks.notion_operations import update_email_sequence

        result = update_email_sequence.fn(
            sequence_id="seq-456",
            email_number=7,
            sequence_completed=True
        )

        assert result["id"] == "seq-456"

        call_kwargs = mock_client.pages.update.call_args.kwargs
        props = call_kwargs["properties"]
        assert "Email 7 Sent" in props
        assert props["Sequence Completed"]["checkbox"] is True


# ===== create_customer_portal() tests =====

class TestCreateCustomerPortal:
    """Test create_customer_portal() with mocked Notion API."""

    @patch('campaigns.christmas_campaign.tasks.notion_operations.notion')
    def test_create_portal_success(self, mock_client):
        """Customer portal created successfully."""
        mock_client.pages.create.return_value = {
            "id": "portal-123",
            "url": "https://notion.so/portal-123"
        }

        from campaigns.christmas_campaign.tasks.notion_operations import create_customer_portal

        result = create_customer_portal.fn(
            email="john@testcorp.com",
            first_name="John",
            business_name="Test Corp",
            call_date="2025-11-25",
            next_steps="Phase 2A Done-For-You"
        )

        assert result == "https://notion.so/portal-123"

        call_kwargs = mock_client.pages.create.call_args.kwargs
        props = call_kwargs["properties"]
        assert "Email" in props
        assert props["Email"]["email"] == "john@testcorp.com"
        assert props["Diagnostic Call Date"]["date"]["start"] == "2025-11-25"


# ===== log_email_analytics() tests =====

class TestLogEmailAnalytics:
    """Test log_email_analytics() with mocked Notion API."""

    @patch('campaigns.christmas_campaign.tasks.notion_operations.notion')
    def test_log_analytics_sent_success(self, mock_client):
        """Email analytics logged for successful send."""
        mock_client.pages.create.return_value = {"id": "analytics-123"}

        from campaigns.christmas_campaign.tasks.notion_operations import log_email_analytics

        result = log_email_analytics.fn(
            email="test@example.com",
            template_id="christmas_email_1",
            email_number=1,
            status="sent",
            resend_email_id="resend-abc123"
        )

        assert result == "analytics-123"

        call_kwargs = mock_client.pages.create.call_args.kwargs
        props = call_kwargs["properties"]
        assert props["Email"]["email"] == "test@example.com"
        assert props["Status"]["select"]["name"] == "sent"
        assert "Resend Email ID" in props

    @patch('campaigns.christmas_campaign.tasks.notion_operations.notion')
    def test_log_analytics_failed_with_error(self, mock_client):
        """Email analytics logged for failed send."""
        mock_client.pages.create.return_value = {"id": "analytics-456"}

        from campaigns.christmas_campaign.tasks.notion_operations import log_email_analytics

        result = log_email_analytics.fn(
            email="test@example.com",
            template_id="christmas_email_2",
            email_number=2,
            status="failed",
            error_message="API timeout"
        )

        assert result == "analytics-456"

        call_kwargs = mock_client.pages.create.call_args.kwargs
        props = call_kwargs["properties"]
        assert props["Status"]["select"]["name"] == "failed"
        assert "Error Message" in props


# ===== Error handling tests =====

class TestNotionErrorHandling:
    """Test error handling paths in Notion operations."""

    @patch('campaigns.christmas_campaign.tasks.notion_operations.notion')
    def test_update_assessment_error_handling(self, mock_client):
        """Test exception handling in update_assessment_data."""
        mock_client.pages.update.side_effect = Exception("Notion API error")

        from campaigns.christmas_campaign.tasks.notion_operations import update_assessment_data

        with pytest.raises(Exception) as exc_info:
            update_assessment_data.fn(
                page_id="page-123",
                assessment_score=45,
                segment="CRITICAL"
            )

        assert "Notion API error" in str(exc_info.value)

    @patch('campaigns.christmas_campaign.tasks.notion_operations.notion')
    def test_track_email_sent_error_handling(self, mock_client):
        """Test exception handling in track_email_sent."""
        mock_client.pages.update.side_effect = Exception("Update failed")

        from campaigns.christmas_campaign.tasks.notion_operations import track_email_sent

        with pytest.raises(Exception) as exc_info:
            track_email_sent.fn(page_id="page-123", email_number=1)

        assert "Update failed" in str(exc_info.value)

    @patch('campaigns.christmas_campaign.tasks.notion_operations.notion')
    def test_update_contact_phase_error_handling(self, mock_client):
        """Test exception handling in update_contact_phase."""
        mock_client.pages.update.side_effect = Exception("Phase update failed")

        from campaigns.christmas_campaign.tasks.notion_operations import update_contact_phase

        with pytest.raises(Exception) as exc_info:
            update_contact_phase.fn(page_id="page-123", phase="Phase 2A Done-For-You")

        assert "Phase update failed" in str(exc_info.value)

    @patch('campaigns.christmas_campaign.tasks.notion_operations.notion')
    def test_update_booking_status_error_handling(self, mock_client):
        """Test exception handling in update_booking_status."""
        mock_client.pages.update.side_effect = Exception("Booking update failed")

        from campaigns.christmas_campaign.tasks.notion_operations import update_booking_status

        with pytest.raises(Exception) as exc_info:
            update_booking_status.fn(page_id="page-123", status="Booked")

        assert "Booking update failed" in str(exc_info.value)

    @patch('campaigns.christmas_campaign.tasks.notion_operations.notion')
    def test_search_email_sequence_error_handling(self, mock_client):
        """Test exception handling in search_email_sequence_by_email."""
        mock_client.databases.query.side_effect = Exception("Search failed")

        from campaigns.christmas_campaign.tasks.notion_operations import search_email_sequence_by_email

        with pytest.raises(Exception) as exc_info:
            search_email_sequence_by_email.fn("test@example.com")

        assert "Search failed" in str(exc_info.value)

    @patch('campaigns.christmas_campaign.tasks.notion_operations.notion')
    def test_create_email_sequence_error_handling(self, mock_client):
        """Test exception handling in create_email_sequence."""
        mock_client.pages.create.side_effect = Exception("Create failed")

        from campaigns.christmas_campaign.tasks.notion_operations import create_email_sequence

        with pytest.raises(Exception) as exc_info:
            create_email_sequence.fn(
                email="test@example.com",
                first_name="Test",
                business_name="Test Corp",
                assessment_score=50
            )

        assert "Create failed" in str(exc_info.value)

    @patch('campaigns.christmas_campaign.tasks.notion_operations.notion')
    def test_update_email_sequence_error_handling(self, mock_client):
        """Test exception handling in update_email_sequence."""
        mock_client.pages.update.side_effect = Exception("Update failed")

        from campaigns.christmas_campaign.tasks.notion_operations import update_email_sequence

        with pytest.raises(Exception) as exc_info:
            update_email_sequence.fn(sequence_id="seq-123", email_number=1)

        assert "Update failed" in str(exc_info.value)

    @patch('campaigns.christmas_campaign.tasks.notion_operations.notion')
    def test_fetch_email_template_error_handling(self, mock_client):
        """Test exception handling in fetch_email_template."""
        mock_client.databases.query.side_effect = Exception("Template fetch failed")

        from campaigns.christmas_campaign.tasks.notion_operations import fetch_email_template

        with pytest.raises(Exception) as exc_info:
            fetch_email_template.fn("christmas_email_1")

        assert "Template fetch failed" in str(exc_info.value)

    @patch('campaigns.christmas_campaign.tasks.notion_operations.notion')
    def test_create_customer_portal_error_handling(self, mock_client):
        """Test exception handling in create_customer_portal."""
        mock_client.pages.create.side_effect = Exception("Portal creation failed")

        from campaigns.christmas_campaign.tasks.notion_operations import create_customer_portal

        with pytest.raises(Exception) as exc_info:
            create_customer_portal.fn(
                email="test@example.com",
                first_name="Test",
                business_name="Test Corp",
                call_date="2025-11-25",
                next_steps="Phase 2A Done-For-You"
            )

        assert "Portal creation failed" in str(exc_info.value)

    @patch('campaigns.christmas_campaign.tasks.notion_operations.notion')
    def test_log_email_analytics_error_handling(self, mock_client):
        """Test exception handling in log_email_analytics (should not raise)."""
        mock_client.pages.create.side_effect = Exception("Analytics failed")

        from campaigns.christmas_campaign.tasks.notion_operations import log_email_analytics

        # Should NOT raise - analytics errors should be caught
        result = log_email_analytics.fn(
            email="test@example.com",
            template_id="christmas_email_1",
            email_number=1,
            status="sent"
        )

        assert result is None  # Returns None on error

    @patch('campaigns.christmas_campaign.tasks.notion_operations.notion')
    def test_update_email_sequence_without_email_number(self, mock_client):
        """Test update_email_sequence with only sequence_completed flag."""
        mock_client.pages.update.return_value = {"id": "seq-123"}

        from campaigns.christmas_campaign.tasks.notion_operations import update_email_sequence

        result = update_email_sequence.fn(
            sequence_id="seq-123",
            sequence_completed=True
        )

        assert result["id"] == "seq-123"

        call_kwargs = mock_client.pages.update.call_args.kwargs
        props = call_kwargs["properties"]
        assert props["Sequence Completed"]["checkbox"] is True


# ===== Integration tests =====

class TestNotionIntegration:
    """Test Notion functions work together."""

    @patch('campaigns.christmas_campaign.tasks.notion_operations.notion')
    def test_complete_contact_workflow(self, mock_client):
        """Test complete contact creation and update workflow."""
        # Step 1: Search returns None (contact doesn't exist)
        mock_client.databases.query.return_value = {"results": []}

        contact = search_contact_by_email.fn("new@example.com")
        assert contact is None

        # Step 2: Create contact (simulated)
        mock_client.pages.create.return_value = {"id": "new-page-123"}

        # Step 3: Update assessment data
        mock_client.pages.update.return_value = {"id": "new-page-123"}

        result = update_assessment_data.fn(
            page_id="new-page-123",
            assessment_score=65,
            segment="URGENT"
        )

        assert result["id"] == "new-page-123"

    @patch('campaigns.christmas_campaign.tasks.notion_operations.notion')
    def test_email_sequence_workflow(self, mock_client):
        """Test email sequence creation and tracking."""
        # Step 1: Create sequence
        mock_client.pages.create.return_value = {"id": "seq-123"}

        sequence = create_email_sequence.fn(
            email="test@example.com",
            first_name="Test",
            business_name="Test Corp",
            assessment_score=45,
            segment="CRITICAL"
        )

        assert sequence["id"] == "seq-123"

        # Step 2: Track emails sent
        mock_client.pages.update.return_value = {"id": "seq-123"}

        for email_num in [1, 2, 3]:
            track_email_sent.fn(page_id="seq-123", email_number=email_num)

        # Verify 3 tracking updates
        assert mock_client.pages.update.call_count == 3

    @patch('campaigns.christmas_campaign.tasks.notion_operations.notion')
    def test_phase_progression_workflow(self, mock_client):
        """Test contact phase progression."""
        mock_client.pages.update.return_value = {"id": "page-123"}

        # Simulate phase progression
        phases = [
            "Phase 1 Assessment",
            "Phase 1 Diagnostic",
            "Phase 2A Done-For-You"
        ]

        for phase in phases:
            update_contact_phase.fn(page_id="page-123", phase=phase)

        assert mock_client.pages.update.call_count == len(phases)
