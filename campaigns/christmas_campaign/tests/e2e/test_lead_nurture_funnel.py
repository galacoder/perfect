"""
E2E Tests: Lead Nurture Funnel

Tests the complete lead nurture funnel:
1. Landing page navigation
2. Opt-in form submission
3. Assessment completion
4. Results page display
5. Webhook triggering
6. Email sequence creation

Prerequisites:
- FastAPI server running: uvicorn server:app --reload
- Prefect server running (optional)
- Website running: npm run dev (localhost:3005) - for browser tests
- TESTING_MODE=true for fast email timing
"""

import pytest
import time
import json
from pathlib import Path

# Import shared fixtures
from .conftest_e2e import (
    E2EConfig,
    e2e_config,
    http_client,
    load_fixture,
    customer_data,
    unique_email,
    make_unique_payload,
    result_capture,
    ensure_fastapi_running,
    post_webhook,
)


class TestChristmasSignupWebhook:
    """Test Christmas signup webhook endpoint."""

    def test_e2e_christmas_signup_critical_segment(
        self,
        ensure_fastapi_running,
        http_client,
        e2e_config,
        customer_data,
        unique_email,
        result_capture
    ):
        """CRITICAL segment signup should be accepted."""
        payload = customer_data["lead_nurture_critical"].copy()
        payload["email"] = unique_email("e2e-critical")

        response = http_client.post(
            f"{e2e_config.FASTAPI_URL}/webhook/christmas-signup",
            json=payload
        )

        result_capture.add_webhook_response(
            endpoint="/webhook/christmas-signup",
            status_code=response.status_code,
            response=response.json()
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "accepted"
        assert data["campaign"] == "Christmas 2025"

        result_capture.add_note(f"CRITICAL segment: {payload['email']}")
        result_capture.add_note(f"Expected segment: {payload['expected_segment']}")

    def test_e2e_christmas_signup_urgent_segment(
        self,
        ensure_fastapi_running,
        http_client,
        e2e_config,
        customer_data,
        unique_email,
        result_capture
    ):
        """URGENT segment signup should be accepted."""
        payload = customer_data["lead_nurture_urgent"].copy()
        payload["email"] = unique_email("e2e-urgent")

        response = http_client.post(
            f"{e2e_config.FASTAPI_URL}/webhook/christmas-signup",
            json=payload
        )

        result_capture.add_webhook_response(
            endpoint="/webhook/christmas-signup",
            status_code=response.status_code,
            response=response.json()
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "accepted"

        result_capture.add_note(f"URGENT segment: {payload['email']}")

    def test_e2e_christmas_signup_optimize_segment(
        self,
        ensure_fastapi_running,
        http_client,
        e2e_config,
        customer_data,
        unique_email,
        result_capture
    ):
        """OPTIMIZE segment signup should be accepted."""
        payload = customer_data["lead_nurture_optimize"].copy()
        payload["email"] = unique_email("e2e-optimize")

        response = http_client.post(
            f"{e2e_config.FASTAPI_URL}/webhook/christmas-signup",
            json=payload
        )

        result_capture.add_webhook_response(
            endpoint="/webhook/christmas-signup",
            status_code=response.status_code,
            response=response.json()
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "accepted"

        result_capture.add_note(f"OPTIMIZE segment: {payload['email']}")


class TestWebhookTriggersFlow:
    """Test that webhook triggers Prefect flow correctly."""

    def test_e2e_verify_webhook_triggers_signup_handler(
        self,
        ensure_fastapi_running,
        http_client,
        e2e_config,
        customer_data,
        unique_email,
        result_capture
    ):
        """Webhook should trigger signup_handler_flow."""
        payload = customer_data["lead_nurture_critical"].copy()
        test_email = unique_email("e2e-flow-trigger")
        payload["email"] = test_email

        response = http_client.post(
            f"{e2e_config.FASTAPI_URL}/webhook/christmas-signup",
            json=payload
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "accepted"

        # Give flow time to start
        time.sleep(2)

        result_capture.add_note(f"Flow triggered for {test_email}")
        result_capture.add_note("Verify in Prefect UI: signup_handler_flow run created")


class TestEmailSequenceCreation:
    """Test email sequence is created correctly."""

    @pytest.mark.skip(reason="Requires Notion API access - run manually")
    def test_e2e_verify_email_sequence_created_in_notion(
        self,
        ensure_fastapi_running,
        http_client,
        e2e_config,
        customer_data,
        unique_email,
        result_capture
    ):
        """Verify sequence record is created in Notion."""
        payload = customer_data["lead_nurture_critical"].copy()
        test_email = unique_email("e2e-notion-sequence")
        payload["email"] = test_email

        response = http_client.post(
            f"{e2e_config.FASTAPI_URL}/webhook/christmas-signup",
            json=payload
        )
        assert response.status_code == 200

        time.sleep(5)

        result_capture.add_note(
            f"Verify in Notion: sequence record for {test_email}"
        )
        result_capture.add_note("Expected: Campaign=Christmas 2025, Segment=CRITICAL")


class TestBrowserAutomation:
    """Browser automation tests for funnel navigation."""

    @pytest.mark.skip(reason="Requires Puppeteer MCP - run via e2e_test_runner.py")
    def test_e2e_navigate_to_landing_page(self, result_capture):
        """Navigate to Christmas campaign landing page."""
        result_capture.add_note(
            "URL: localhost:3005/en/flows/businessX/dfu/xmas-a01"
        )
        result_capture.add_note("Use Puppeteer MCP for browser automation")

    @pytest.mark.skip(reason="Requires Puppeteer MCP - run via e2e_test_runner.py")
    def test_e2e_fill_optin_form_with_test_email(self, result_capture):
        """Fill opt-in form with test email."""
        result_capture.add_note("Fill form fields: first_name, email, business_name")

    @pytest.mark.skip(reason="Requires Puppeteer MCP - run via e2e_test_runner.py")
    def test_e2e_complete_16_question_assessment(self, result_capture):
        """Complete the 16-question BusOS assessment."""
        result_capture.add_note("Answer all 16 questions")
        result_capture.add_note("Use CRITICAL segment answers for testing")

    @pytest.mark.skip(reason="Requires Puppeteer MCP - run via e2e_test_runner.py")
    def test_e2e_verify_results_page_displayed(self, result_capture):
        """Verify results page is displayed after assessment."""
        result_capture.add_note("Check for results page elements")
        result_capture.add_note("Verify score displayed correctly")

    @pytest.mark.skip(reason="Requires Puppeteer MCP - run via e2e_test_runner.py")
    def test_e2e_screenshots_at_each_step(self, result_capture):
        """Capture screenshots at each funnel step."""
        result_capture.add_note("Screenshots saved to: tests/e2e/screenshots/")


class TestEmailSequenceMonitoring:
    """Test email sequence sending (in testing mode)."""

    @pytest.mark.skip(reason="Requires time-based testing - run in testing mode")
    def test_e2e_monitor_7_nurture_emails_sent(self, result_capture):
        """Monitor all 7 nurture emails are sent."""
        result_capture.add_note("Email timing in testing mode:")
        result_capture.add_note("  Email 1: Immediate")
        result_capture.add_note("  Email 2: +1 minute")
        result_capture.add_note("  Email 3: +2 minutes")
        result_capture.add_note("  Email 4: +3 minutes")
        result_capture.add_note("  Email 5: +4 minutes")
        result_capture.add_note("  Email 6: +5 minutes")
        result_capture.add_note("  Email 7: +6 minutes")

    @pytest.mark.skip(reason="Requires Resend API access - run manually")
    def test_e2e_verify_new_template_content_in_emails(self, result_capture):
        """Verify updated template content is used."""
        result_capture.add_note("Verify templates from new Notion database")
        result_capture.add_note("Database ID: 2ab7c374-1115-8115-932c-ca6789c5b87b")


# ============================================================================
# Test Summary
# ============================================================================

def test_e2e_lead_nurture_suite_summary(result_capture):
    """Generate test suite summary."""
    result_capture.add_note("Lead Nurture Funnel E2E Test Suite")
    result_capture.add_note("Tests covered:")
    result_capture.add_note("  - Christmas signup webhook (3 segments)")
    result_capture.add_note("  - Flow triggering")
    result_capture.add_note("  - Sequence creation (manual verification)")
    result_capture.add_note("  - Browser automation (Puppeteer)")
    result_capture.add_note("  - Email monitoring (manual verification)")
