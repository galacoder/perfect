"""
Tests for Resend email operations - Lead Nurture Email Sending (Wave 0).

This module tests:
1. Sending all 7 lead nurture emails via Resend API
2. Correct subject lines and body content
3. Template variable substitution
4. Error handling for failed sends

TDD Approach: Tests written FIRST (Red phase), then implementation (Green phase).

Author: Coding Agent (Sonnet 4.5)
Created: 2025-11-26
Wave: 0 - Lead Nurture Verification
"""

import pytest
from unittest.mock import Mock, patch, MagicMock


# ==============================================================================
# Feature 0.3: Test all 7 nurture emails send correctly
# ==============================================================================

class TestSendLeadNurtureEmails:
    """Test sending lead nurture emails via Resend API."""

    def test_send_lead_nurture_email_1_success(self, monkeypatch):
        """Verify lead_nurture_email_1 can be sent successfully."""
        from campaigns.christmas_campaign.tasks import resend_operations

        # Mock Resend API
        mock_resend_emails = MagicMock()
        mock_resend_emails.send.return_value = {"id": "email-1-id-123"}

        monkeypatch.setattr(
            "campaigns.christmas_campaign.tasks.resend_operations.resend.Emails",
            mock_resend_emails
        )

        # Execute
        result = resend_operations.send_email.fn(
            to_email="test@example.com",
            subject="Your BusOS Assessment Results",
            html_body="<html><body>Email 1 content</body></html>"
        )

        # Assert
        assert result == "email-1-id-123"
        mock_resend_emails.send.assert_called_once()

    def test_send_lead_nurture_email_2a_critical_success(self, monkeypatch):
        """Verify lead_nurture_email_2a_critical can be sent successfully."""
        from campaigns.christmas_campaign.tasks import resend_operations

        mock_resend_emails = MagicMock()
        mock_resend_emails.send.return_value = {"id": "email-2a-id-123"}

        monkeypatch.setattr(
            "campaigns.christmas_campaign.tasks.resend_operations.resend.Emails",
            mock_resend_emails
        )

        result = resend_operations.send_email.fn(
            to_email="critical@example.com",
            subject="URGENT: Critical Systems",
            html_body="<html><body>Email 2a CRITICAL content</body></html>"
        )

        assert result == "email-2a-id-123"

    def test_send_lead_nurture_email_2b_urgent_success(self, monkeypatch):
        """Verify lead_nurture_email_2b_urgent can be sent successfully."""
        from campaigns.christmas_campaign.tasks import resend_operations

        mock_resend_emails = MagicMock()
        mock_resend_emails.send.return_value = {"id": "email-2b-id-123"}

        monkeypatch.setattr(
            "campaigns.christmas_campaign.tasks.resend_operations.resend.Emails",
            mock_resend_emails
        )

        result = resend_operations.send_email.fn(
            to_email="urgent@example.com",
            subject="Quick Wins for Your Business",
            html_body="<html><body>Email 2b URGENT content</body></html>"
        )

        assert result == "email-2b-id-123"

    def test_send_lead_nurture_email_2c_optimize_success(self, monkeypatch):
        """Verify lead_nurture_email_2c_optimize can be sent successfully."""
        from campaigns.christmas_campaign.tasks import resend_operations

        mock_resend_emails = MagicMock()
        mock_resend_emails.send.return_value = {"id": "email-2c-id-123"}

        monkeypatch.setattr(
            "campaigns.christmas_campaign.tasks.resend_operations.resend.Emails",
            mock_resend_emails
        )

        result = resend_operations.send_email.fn(
            to_email="optimize@example.com",
            subject="Optimization Opportunities",
            html_body="<html><body>Email 2c OPTIMIZE content</body></html>"
        )

        assert result == "email-2c-id-123"

    def test_send_lead_nurture_email_3_success(self, monkeypatch):
        """Verify lead_nurture_email_3 can be sent successfully."""
        from campaigns.christmas_campaign.tasks import resend_operations

        mock_resend_emails = MagicMock()
        mock_resend_emails.send.return_value = {"id": "email-3-id-123"}

        monkeypatch.setattr(
            "campaigns.christmas_campaign.tasks.resend_operations.resend.Emails",
            mock_resend_emails
        )

        result = resend_operations.send_email.fn(
            to_email="test@example.com",
            subject="Email 3 Subject",
            html_body="<html><body>Email 3 content</body></html>"
        )

        assert result == "email-3-id-123"

    def test_send_lead_nurture_email_4_success(self, monkeypatch):
        """Verify lead_nurture_email_4 can be sent successfully."""
        from campaigns.christmas_campaign.tasks import resend_operations

        mock_resend_emails = MagicMock()
        mock_resend_emails.send.return_value = {"id": "email-4-id-123"}

        monkeypatch.setattr(
            "campaigns.christmas_campaign.tasks.resend_operations.resend.Emails",
            mock_resend_emails
        )

        result = resend_operations.send_email.fn(
            to_email="test@example.com",
            subject="Email 4 Subject",
            html_body="<html><body>Email 4 content</body></html>"
        )

        assert result == "email-4-id-123"

    def test_send_lead_nurture_email_5_success(self, monkeypatch):
        """Verify lead_nurture_email_5 can be sent successfully."""
        from campaigns.christmas_campaign.tasks import resend_operations

        mock_resend_emails = MagicMock()
        mock_resend_emails.send.return_value = {"id": "email-5-id-123"}

        monkeypatch.setattr(
            "campaigns.christmas_campaign.tasks.resend_operations.resend.Emails",
            mock_resend_emails
        )

        result = resend_operations.send_email.fn(
            to_email="test@example.com",
            subject="Email 5 Subject",
            html_body="<html><body>Email 5 content</body></html>"
        )

        assert result == "email-5-id-123"

    def test_send_email_correct_subject_line(self, monkeypatch):
        """Verify subject line is passed correctly to Resend API."""
        from campaigns.christmas_campaign.tasks import resend_operations

        mock_resend_emails = MagicMock()
        mock_resend_emails.send.return_value = {"id": "email-id-123"}

        monkeypatch.setattr(
            "campaigns.christmas_campaign.tasks.resend_operations.resend.Emails",
            mock_resend_emails
        )

        test_subject = "Custom Subject Line with {{variable}}"
        resend_operations.send_email.fn(
            to_email="test@example.com",
            subject=test_subject,
            html_body="<html><body>Content</body></html>"
        )

        # Verify subject is in the call
        call_args = mock_resend_emails.send.call_args
        params = call_args[0][0]
        assert params["subject"] == test_subject

    def test_send_email_correct_body_content(self, monkeypatch):
        """Verify HTML body content is passed correctly to Resend API."""
        from campaigns.christmas_campaign.tasks import resend_operations

        mock_resend_emails = MagicMock()
        mock_resend_emails.send.return_value = {"id": "email-id-123"}

        monkeypatch.setattr(
            "campaigns.christmas_campaign.tasks.resend_operations.resend.Emails",
            mock_resend_emails
        )

        test_body = "<html><body><h1>Test</h1><p>Content with {{first_name}}</p></body></html>"
        resend_operations.send_email.fn(
            to_email="test@example.com",
            subject="Test Subject",
            html_body=test_body
        )

        # Verify body is in the call
        call_args = mock_resend_emails.send.call_args
        params = call_args[0][0]
        assert params["html"] == test_body

    def test_send_email_uses_correct_sender(self, monkeypatch):
        """Verify emails are sent from value@galatek.dev."""
        from campaigns.christmas_campaign.tasks import resend_operations

        mock_resend_emails = MagicMock()
        mock_resend_emails.send.return_value = {"id": "email-id-123"}

        monkeypatch.setattr(
            "campaigns.christmas_campaign.tasks.resend_operations.resend.Emails",
            mock_resend_emails
        )

        resend_operations.send_email.fn(
            to_email="test@example.com",
            subject="Test Subject",
            html_body="<html><body>Test</body></html>"
        )

        # Verify sender email
        call_args = mock_resend_emails.send.call_args
        params = call_args[0][0]
        assert "value@galatek.dev" in params["from"]

    def test_send_email_handles_api_error(self, monkeypatch):
        """Verify error handling when Resend API fails."""
        from campaigns.christmas_campaign.tasks import resend_operations

        mock_resend_emails = MagicMock()
        mock_resend_emails.send.side_effect = Exception("API Error: Rate limit exceeded")

        monkeypatch.setattr(
            "campaigns.christmas_campaign.tasks.resend_operations.resend.Emails",
            mock_resend_emails
        )

        # Should raise exception
        with pytest.raises(Exception) as exc_info:
            resend_operations.send_email.fn(
                to_email="test@example.com",
                subject="Test Subject",
                html_body="<html><body>Test</body></html>"
            )

        assert "API Error" in str(exc_info.value)


# ==============================================================================
# Feature 0.4: Variable substitution tests will go in test_template_rendering.py
# ==============================================================================
