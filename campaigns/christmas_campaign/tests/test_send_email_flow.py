"""
Unit tests for send_email_flow.py.

Tests the individual email sending flow including:
- Sequence lookup
- Idempotency checks
- Template fetching from Notion
- Email sending via Resend
- Sequence update tracking

Author: Christmas Campaign Team
Created: 2025-11-28 (Wave 6)
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime


# ==============================================================================
# Test Fixtures
# ==============================================================================

@pytest.fixture
def mock_email_sequence_record():
    """Mock Email Sequence DB record from Notion."""
    return {
        "id": "sequence-page-id-123",
        "object": "page",
        "properties": {
            "Email": {"email": "test@example.com"},
            "Contact": {"relation": [{"id": "contact-page-id-456"}]},
            "Segment": {"select": {"name": "URGENT"}},
            "Email 1 Sent": {"date": None},
            "Email 2 Sent": {"date": None},
            "Email 3 Sent": {"date": None},
            "Email 4 Sent": {"date": None},
            "Email 5 Sent": {"date": None},
            "Email 6 Sent": {"date": None},
            "Email 7 Sent": {"date": None},
            "Sequence Type": {"select": {"name": "lead_nurture"}}
        }
    }


@pytest.fixture
def mock_email_sequence_with_sent_email():
    """Mock Email Sequence DB record with Email 1 already sent."""
    return {
        "id": "sequence-page-id-123",
        "object": "page",
        "properties": {
            "Email": {"email": "test@example.com"},
            "Contact": {"relation": [{"id": "contact-page-id-456"}]},
            "Segment": {"select": {"name": "URGENT"}},
            "Email 1 Sent": {"date": {"start": "2025-11-27T10:00:00.000Z"}},
            "Email 2 Sent": {"date": None},
            "Email 3 Sent": {"date": None},
        }
    }


@pytest.fixture
def mock_email_template():
    """Mock email template from Notion."""
    return {
        "template_id": "christmas_email_1",
        "subject": "Your BusOS Assessment Results - {{first_name}}",
        "html_body": """
        <html>
        <body>
            <h1>Hi {{first_name}}!</h1>
            <p>Thank you for completing your assessment for {{business_name}}.</p>
            <p>Your score: {{assessment_score}}</p>
        </body>
        </html>
        """
    }


# ==============================================================================
# Flow Structure Tests
# ==============================================================================

class TestSendEmailFlowStructure:
    """Test send_email_flow structure and parameters."""

    def test_flow_exists(self):
        """Test that send_email_flow exists and is importable."""
        from campaigns.christmas_campaign.flows.send_email_flow import send_email_flow
        assert send_email_flow is not None

    def test_flow_has_correct_name(self):
        """Test flow has correct Prefect name."""
        from campaigns.christmas_campaign.flows.send_email_flow import send_email_flow
        assert send_email_flow.name == "christmas-send-email"

    def test_flow_accepts_required_parameters(self):
        """Test flow accepts email and email_number parameters."""
        from campaigns.christmas_campaign.flows.send_email_flow import send_email_flow
        import inspect
        sig = inspect.signature(send_email_flow.fn)
        params = list(sig.parameters.keys())

        assert "email" in params
        assert "email_number" in params

    def test_flow_has_optional_parameters(self):
        """Test flow accepts optional personalization parameters."""
        from campaigns.christmas_campaign.flows.send_email_flow import send_email_flow
        import inspect
        sig = inspect.signature(send_email_flow.fn)
        params = list(sig.parameters.keys())

        assert "first_name" in params
        assert "business_name" in params
        assert "segment" in params
        assert "assessment_score" in params


# ==============================================================================
# Sequence Lookup Tests
# ==============================================================================

class TestSequenceLookup:
    """Test Email Sequence DB lookup behavior."""

    @patch('campaigns.christmas_campaign.flows.send_email_flow.search_email_sequence_by_email')
    @patch('campaigns.christmas_campaign.flows.send_email_flow.fetch_email_template')
    @patch('campaigns.christmas_campaign.flows.send_email_flow.send_template_email')
    @patch('campaigns.christmas_campaign.flows.send_email_flow.update_email_sequence')
    @patch('campaigns.christmas_campaign.flows.send_email_flow.log_email_analytics')
    def test_flow_returns_error_when_sequence_not_found(
        self, mock_analytics, mock_update, mock_send, mock_fetch, mock_search
    ):
        """Test flow returns error when email sequence not found."""
        from campaigns.christmas_campaign.flows.send_email_flow import send_email_flow

        # Mock sequence not found
        mock_search.return_value = None

        result = send_email_flow(
            email="unknown@example.com",
            email_number=1
        )

        assert result["status"] == "failed"
        assert "sequence not found" in result["error"].lower()
        assert result["email_number"] == 1

    @patch('campaigns.christmas_campaign.flows.send_email_flow.search_email_sequence_by_email')
    @patch('campaigns.christmas_campaign.flows.send_email_flow.fetch_email_template')
    @patch('campaigns.christmas_campaign.flows.send_email_flow.send_template_email')
    @patch('campaigns.christmas_campaign.flows.send_email_flow.update_email_sequence')
    @patch('campaigns.christmas_campaign.flows.send_email_flow.log_email_analytics')
    def test_flow_finds_sequence_successfully(
        self, mock_analytics, mock_update, mock_send, mock_fetch, mock_search,
        mock_email_sequence_record, mock_email_template
    ):
        """Test flow finds email sequence record."""
        from campaigns.christmas_campaign.flows.send_email_flow import send_email_flow

        mock_search.return_value = mock_email_sequence_record
        mock_fetch.return_value = mock_email_template
        mock_send.return_value = "resend-id-123"

        result = send_email_flow(
            email="test@example.com",
            email_number=1
        )

        mock_search.assert_called_once_with("test@example.com")
        assert result["status"] == "success"
        assert result["sequence_id"] == "sequence-page-id-123"


# ==============================================================================
# Idempotency Tests
# ==============================================================================

class TestIdempotency:
    """Test idempotency checks for duplicate prevention."""

    @patch('campaigns.christmas_campaign.flows.send_email_flow.search_email_sequence_by_email')
    @patch('campaigns.christmas_campaign.flows.send_email_flow.fetch_email_template')
    @patch('campaigns.christmas_campaign.flows.send_email_flow.send_template_email')
    def test_flow_skips_when_email_already_sent(
        self, mock_send, mock_fetch, mock_search, mock_email_sequence_with_sent_email
    ):
        """Test flow skips sending when email already marked as sent."""
        from campaigns.christmas_campaign.flows.send_email_flow import send_email_flow

        mock_search.return_value = mock_email_sequence_with_sent_email

        result = send_email_flow(
            email="test@example.com",
            email_number=1  # Already sent
        )

        assert result["status"] == "skipped"
        assert result["reason"] == "already_sent"
        assert "sent_at" in result

        # Verify email was NOT sent
        mock_send.assert_not_called()
        mock_fetch.assert_not_called()

    @patch('campaigns.christmas_campaign.flows.send_email_flow.search_email_sequence_by_email')
    @patch('campaigns.christmas_campaign.flows.send_email_flow.fetch_email_template')
    @patch('campaigns.christmas_campaign.flows.send_email_flow.send_template_email')
    @patch('campaigns.christmas_campaign.flows.send_email_flow.update_email_sequence')
    @patch('campaigns.christmas_campaign.flows.send_email_flow.log_email_analytics')
    def test_flow_proceeds_when_email_not_sent(
        self, mock_analytics, mock_update, mock_send, mock_fetch, mock_search,
        mock_email_sequence_record, mock_email_template
    ):
        """Test flow proceeds when email not yet sent."""
        from campaigns.christmas_campaign.flows.send_email_flow import send_email_flow

        mock_search.return_value = mock_email_sequence_record
        mock_fetch.return_value = mock_email_template
        mock_send.return_value = "resend-id-456"

        result = send_email_flow(
            email="test@example.com",
            email_number=2  # Not sent yet
        )

        assert result["status"] == "success"
        mock_send.assert_called_once()


# ==============================================================================
# Template Fetching Tests
# ==============================================================================

class TestTemplateFetching:
    """Test Notion template fetching behavior."""

    @patch('campaigns.christmas_campaign.flows.send_email_flow.search_email_sequence_by_email')
    @patch('campaigns.christmas_campaign.flows.send_email_flow.fetch_email_template')
    @patch('campaigns.christmas_campaign.flows.send_email_flow.log_email_analytics')
    def test_flow_fails_when_template_not_found(
        self, mock_analytics, mock_fetch, mock_search, mock_email_sequence_record
    ):
        """Test flow fails when template not found in Notion (no fallback)."""
        from campaigns.christmas_campaign.flows.send_email_flow import send_email_flow

        mock_search.return_value = mock_email_sequence_record
        mock_fetch.return_value = None  # Template not found

        result = send_email_flow(
            email="test@example.com",
            email_number=1
        )

        assert result["status"] == "failed"
        assert "not found" in result["error"].lower() or "template" in result["error"].lower()

    @patch('campaigns.christmas_campaign.flows.send_email_flow.search_email_sequence_by_email')
    @patch('campaigns.christmas_campaign.flows.send_email_flow.fetch_email_template')
    @patch('campaigns.christmas_campaign.flows.send_email_flow.log_email_analytics')
    def test_flow_fails_when_template_missing_subject(
        self, mock_analytics, mock_fetch, mock_search, mock_email_sequence_record
    ):
        """Test flow fails when template missing subject."""
        from campaigns.christmas_campaign.flows.send_email_flow import send_email_flow

        mock_search.return_value = mock_email_sequence_record
        mock_fetch.return_value = {"html_body": "<p>Test</p>"}  # Missing subject

        result = send_email_flow(
            email="test@example.com",
            email_number=1
        )

        assert result["status"] == "failed"
        assert "subject" in result["error"].lower() or "missing" in result["error"].lower()

    @patch('campaigns.christmas_campaign.flows.send_email_flow.search_email_sequence_by_email')
    @patch('campaigns.christmas_campaign.flows.send_email_flow.fetch_email_template')
    @patch('campaigns.christmas_campaign.flows.send_email_flow.log_email_analytics')
    def test_flow_fails_when_template_missing_body(
        self, mock_analytics, mock_fetch, mock_search, mock_email_sequence_record
    ):
        """Test flow fails when template missing html_body."""
        from campaigns.christmas_campaign.flows.send_email_flow import send_email_flow

        mock_search.return_value = mock_email_sequence_record
        mock_fetch.return_value = {"subject": "Test Subject"}  # Missing body

        result = send_email_flow(
            email="test@example.com",
            email_number=1
        )

        assert result["status"] == "failed"
        assert "body" in result["error"].lower() or "missing" in result["error"].lower()

    @patch('campaigns.christmas_campaign.flows.send_email_flow.search_email_sequence_by_email')
    @patch('campaigns.christmas_campaign.flows.send_email_flow.fetch_email_template')
    @patch('campaigns.christmas_campaign.flows.send_email_flow.send_template_email')
    @patch('campaigns.christmas_campaign.flows.send_email_flow.update_email_sequence')
    @patch('campaigns.christmas_campaign.flows.send_email_flow.log_email_analytics')
    def test_flow_uses_correct_template_for_segment(
        self, mock_analytics, mock_update, mock_send, mock_fetch, mock_search,
        mock_email_sequence_record, mock_email_template
    ):
        """Test flow fetches correct segment-specific template."""
        from campaigns.christmas_campaign.flows.send_email_flow import send_email_flow

        mock_search.return_value = mock_email_sequence_record
        mock_fetch.return_value = mock_email_template
        mock_send.return_value = "resend-id-789"

        # Test CRITICAL segment
        result = send_email_flow(
            email="test@example.com",
            email_number=2,  # Email 2 is segment-specific
            segment="CRITICAL"
        )

        # Verify template was fetched
        mock_fetch.assert_called()
        assert result["status"] == "success"


# ==============================================================================
# Email Sending Tests
# ==============================================================================

class TestEmailSending:
    """Test email sending via Resend."""

    @patch('campaigns.christmas_campaign.flows.send_email_flow.search_email_sequence_by_email')
    @patch('campaigns.christmas_campaign.flows.send_email_flow.fetch_email_template')
    @patch('campaigns.christmas_campaign.flows.send_email_flow.send_template_email')
    @patch('campaigns.christmas_campaign.flows.send_email_flow.update_email_sequence')
    @patch('campaigns.christmas_campaign.flows.send_email_flow.log_email_analytics')
    def test_flow_sends_email_with_variables(
        self, mock_analytics, mock_update, mock_send, mock_fetch, mock_search,
        mock_email_sequence_record, mock_email_template
    ):
        """Test flow sends email with substituted variables."""
        from campaigns.christmas_campaign.flows.send_email_flow import send_email_flow

        mock_search.return_value = mock_email_sequence_record
        mock_fetch.return_value = mock_email_template
        mock_send.return_value = "resend-success-id"

        result = send_email_flow(
            email="test@example.com",
            email_number=1,
            first_name="John",
            business_name="Test Corp",
            assessment_score=75
        )

        # Verify send_template_email was called
        mock_send.assert_called_once()
        call_args = mock_send.call_args

        assert call_args[1]["to_email"] == "test@example.com"
        assert result["resend_email_id"] == "resend-success-id"

    @patch('campaigns.christmas_campaign.flows.send_email_flow.search_email_sequence_by_email')
    @patch('campaigns.christmas_campaign.flows.send_email_flow.fetch_email_template')
    @patch('campaigns.christmas_campaign.flows.send_email_flow.send_template_email')
    @patch('campaigns.christmas_campaign.flows.send_email_flow.log_email_analytics')
    def test_flow_handles_send_failure(
        self, mock_analytics, mock_send, mock_fetch, mock_search,
        mock_email_sequence_record, mock_email_template
    ):
        """Test flow handles Resend API failure."""
        from campaigns.christmas_campaign.flows.send_email_flow import send_email_flow

        mock_search.return_value = mock_email_sequence_record
        mock_fetch.return_value = mock_email_template
        mock_send.side_effect = Exception("Resend API error")

        result = send_email_flow(
            email="test@example.com",
            email_number=1
        )

        assert result["status"] == "failed"
        assert "error" in result


# ==============================================================================
# Sequence Update Tests
# ==============================================================================

class TestSequenceUpdate:
    """Test Email Sequence DB update after sending."""

    @patch('campaigns.christmas_campaign.flows.send_email_flow.search_email_sequence_by_email')
    @patch('campaigns.christmas_campaign.flows.send_email_flow.fetch_email_template')
    @patch('campaigns.christmas_campaign.flows.send_email_flow.send_template_email')
    @patch('campaigns.christmas_campaign.flows.send_email_flow.update_email_sequence')
    @patch('campaigns.christmas_campaign.flows.send_email_flow.log_email_analytics')
    def test_flow_updates_sequence_after_send(
        self, mock_analytics, mock_update, mock_send, mock_fetch, mock_search,
        mock_email_sequence_record, mock_email_template
    ):
        """Test flow updates Email Sequence DB after successful send."""
        from campaigns.christmas_campaign.flows.send_email_flow import send_email_flow

        mock_search.return_value = mock_email_sequence_record
        mock_fetch.return_value = mock_email_template
        mock_send.return_value = "resend-id-update"

        result = send_email_flow(
            email="test@example.com",
            email_number=3
        )

        # Verify update_email_sequence was called with correct params
        mock_update.assert_called_once_with(
            sequence_id="sequence-page-id-123",
            email_number=3
        )
        assert result["status"] == "success"


# ==============================================================================
# Analytics Logging Tests
# ==============================================================================

class TestAnalyticsLogging:
    """Test email analytics logging."""

    @patch('campaigns.christmas_campaign.flows.send_email_flow.search_email_sequence_by_email')
    @patch('campaigns.christmas_campaign.flows.send_email_flow.fetch_email_template')
    @patch('campaigns.christmas_campaign.flows.send_email_flow.send_template_email')
    @patch('campaigns.christmas_campaign.flows.send_email_flow.update_email_sequence')
    @patch('campaigns.christmas_campaign.flows.send_email_flow.log_email_analytics')
    def test_flow_logs_successful_send_analytics(
        self, mock_analytics, mock_update, mock_send, mock_fetch, mock_search,
        mock_email_sequence_record, mock_email_template
    ):
        """Test flow logs analytics on successful send."""
        from campaigns.christmas_campaign.flows.send_email_flow import send_email_flow

        mock_search.return_value = mock_email_sequence_record
        mock_fetch.return_value = mock_email_template
        mock_send.return_value = "resend-analytics-id"

        result = send_email_flow(
            email="test@example.com",
            email_number=1
        )

        # Verify analytics was logged
        mock_analytics.assert_called_once()
        call_kwargs = mock_analytics.call_args[1]

        assert call_kwargs["email"] == "test@example.com"
        assert call_kwargs["email_number"] == 1
        assert call_kwargs["status"] == "sent"


# ==============================================================================
# End-to-End Flow Tests
# ==============================================================================

class TestSendEmailFlowE2E:
    """End-to-end tests for send_email_flow."""

    @patch('campaigns.christmas_campaign.flows.send_email_flow.search_email_sequence_by_email')
    @patch('campaigns.christmas_campaign.flows.send_email_flow.fetch_email_template')
    @patch('campaigns.christmas_campaign.flows.send_email_flow.send_template_email')
    @patch('campaigns.christmas_campaign.flows.send_email_flow.update_email_sequence')
    @patch('campaigns.christmas_campaign.flows.send_email_flow.log_email_analytics')
    def test_complete_successful_flow(
        self, mock_analytics, mock_update, mock_send, mock_fetch, mock_search,
        mock_email_sequence_record, mock_email_template
    ):
        """Test complete successful email send flow."""
        from campaigns.christmas_campaign.flows.send_email_flow import send_email_flow

        mock_search.return_value = mock_email_sequence_record
        mock_fetch.return_value = mock_email_template
        mock_send.return_value = "resend-e2e-id"

        result = send_email_flow(
            email="test@example.com",
            email_number=1,
            first_name="John",
            business_name="Test Corp",
            segment="URGENT",
            assessment_score=55
        )

        # Verify all steps completed
        assert result["status"] == "success"
        assert result["email_number"] == 1
        assert result["resend_email_id"] == "resend-e2e-id"
        assert "sent_at" in result
        assert "sequence_id" in result
        assert "template_id" in result

        # Verify call sequence
        mock_search.assert_called_once()
        mock_fetch.assert_called_once()
        mock_send.assert_called_once()
        mock_update.assert_called_once()
        mock_analytics.assert_called_once()

    @patch('campaigns.christmas_campaign.flows.send_email_flow.search_email_sequence_by_email')
    @patch('campaigns.christmas_campaign.flows.send_email_flow.fetch_email_template')
    @patch('campaigns.christmas_campaign.flows.send_email_flow.send_template_email')
    @patch('campaigns.christmas_campaign.flows.send_email_flow.update_email_sequence')
    @patch('campaigns.christmas_campaign.flows.send_email_flow.log_email_analytics')
    def test_all_seven_emails(
        self, mock_analytics, mock_update, mock_send, mock_fetch, mock_search,
        mock_email_sequence_record, mock_email_template
    ):
        """Test all 7 emails can be sent successfully."""
        from campaigns.christmas_campaign.flows.send_email_flow import send_email_flow

        mock_search.return_value = mock_email_sequence_record
        mock_fetch.return_value = mock_email_template
        mock_send.return_value = "resend-id"

        for email_num in range(1, 8):
            result = send_email_flow(
                email="test@example.com",
                email_number=email_num
            )

            assert result["status"] == "success"
            assert result["email_number"] == email_num
