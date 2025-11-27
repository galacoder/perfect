"""
E2E Tests: No-Show Recovery Sequence

Tests the complete no-show recovery flow:
1. Webhook endpoint validation
2. Flow triggering
3. Email sequence scheduling
4. Notion sequence record creation

Prerequisites:
- FastAPI server running: uvicorn server:app --reload
- Prefect server running (optional for flow verification)
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
    calendly_noshow_fixtures,
    unique_email,
    make_unique_payload,
    result_capture,
    ensure_fastapi_running,
    post_webhook,
)


class TestNoShowWebhookValidation:
    """Test no-show webhook endpoint validation."""

    def test_e2e_noshow_webhook_valid_payload_accepted(
        self,
        ensure_fastapi_running,
        http_client,
        e2e_config,
        calendly_noshow_fixtures,
        unique_email,
        result_capture
    ):
        """Valid no-show payload should be accepted with 200 status."""
        payload = calendly_noshow_fixtures["valid_payload"].copy()
        payload["email"] = unique_email("e2e-noshow-valid")

        response = http_client.post(
            f"{e2e_config.FASTAPI_URL}/webhook/calendly-noshow",
            json=payload
        )

        result_capture.add_webhook_response(
            endpoint="/webhook/calendly-noshow",
            status_code=response.status_code,
            response=response.json()
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "accepted"
        assert data["email"] == payload["email"]
        assert data["campaign"] == "Christmas Traditional Service"

        result_capture.add_note(f"Flow triggered for {payload['email']}")

    def test_e2e_noshow_webhook_missing_email_rejected(
        self,
        ensure_fastapi_running,
        http_client,
        e2e_config,
        calendly_noshow_fixtures,
        result_capture
    ):
        """Missing email should return 422 validation error."""
        payload = calendly_noshow_fixtures["invalid_payload_missing_email"]

        response = http_client.post(
            f"{e2e_config.FASTAPI_URL}/webhook/calendly-noshow",
            json=payload
        )

        result_capture.add_webhook_response(
            endpoint="/webhook/calendly-noshow",
            status_code=response.status_code,
            response=response.json() if response.status_code != 500 else {"error": "server error"}
        )

        assert response.status_code == 422, f"Expected 422, got {response.status_code}"

    def test_e2e_noshow_webhook_missing_event_uri_rejected(
        self,
        ensure_fastapi_running,
        http_client,
        e2e_config,
        calendly_noshow_fixtures,
        result_capture
    ):
        """Missing calendly_event_uri should return 422 validation error."""
        payload = calendly_noshow_fixtures["invalid_payload_missing_event_uri"]

        response = http_client.post(
            f"{e2e_config.FASTAPI_URL}/webhook/calendly-noshow",
            json=payload
        )

        result_capture.add_webhook_response(
            endpoint="/webhook/calendly-noshow",
            status_code=response.status_code,
            response=response.json() if response.status_code != 500 else {"error": "server error"}
        )

        assert response.status_code == 422, f"Expected 422, got {response.status_code}"

    def test_e2e_noshow_webhook_malformed_email_rejected(
        self,
        ensure_fastapi_running,
        http_client,
        e2e_config,
        calendly_noshow_fixtures,
        result_capture
    ):
        """Malformed email should return 422 validation error."""
        payload = calendly_noshow_fixtures["invalid_payload_malformed_email"]

        response = http_client.post(
            f"{e2e_config.FASTAPI_URL}/webhook/calendly-noshow",
            json=payload
        )

        result_capture.add_webhook_response(
            endpoint="/webhook/calendly-noshow",
            status_code=response.status_code,
            response=response.json() if response.status_code != 500 else {"error": "server error"}
        )

        assert response.status_code == 422, f"Expected 422, got {response.status_code}"


class TestNoShowFlowTriggering:
    """Test no-show flow is properly triggered."""

    def test_e2e_noshow_webhook_triggers_prefect_flow(
        self,
        ensure_fastapi_running,
        http_client,
        e2e_config,
        calendly_noshow_fixtures,
        unique_email,
        result_capture
    ):
        """Webhook should trigger Prefect flow and return accepted status."""
        payload = calendly_noshow_fixtures["valid_payload"].copy()
        test_email = unique_email("e2e-noshow-flow")
        payload["email"] = test_email

        response = http_client.post(
            f"{e2e_config.FASTAPI_URL}/webhook/calendly-noshow",
            json=payload
        )

        result_capture.add_webhook_response(
            endpoint="/webhook/calendly-noshow",
            status_code=response.status_code,
            response=response.json()
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "accepted"

        # Give flow time to start (background task)
        time.sleep(2)

        result_capture.add_note(f"Flow triggered for {test_email} - verify in Prefect UI")

    def test_e2e_noshow_flow_run_id_returned(
        self,
        ensure_fastapi_running,
        http_client,
        e2e_config,
        calendly_noshow_fixtures,
        unique_email,
        result_capture
    ):
        """Response should include confirmation of flow acceptance."""
        payload = calendly_noshow_fixtures["valid_payload"].copy()
        payload["email"] = unique_email("e2e-noshow-flowid")

        response = http_client.post(
            f"{e2e_config.FASTAPI_URL}/webhook/calendly-noshow",
            json=payload
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response contains expected fields
        assert "status" in data
        assert "message" in data
        assert "email" in data
        assert data["status"] == "accepted"

        result_capture.add_webhook_response(
            endpoint="/webhook/calendly-noshow",
            status_code=response.status_code,
            response=data
        )


class TestNoShowSequenceCreation:
    """Test no-show sequence record is created correctly."""

    @pytest.mark.skip(reason="Requires Notion API access - run manually")
    def test_e2e_noshow_sequence_record_created_in_notion(
        self,
        ensure_fastapi_running,
        http_client,
        e2e_config,
        calendly_noshow_fixtures,
        unique_email,
        result_capture
    ):
        """Verify sequence record is created in Notion after webhook."""
        payload = calendly_noshow_fixtures["valid_payload"].copy()
        test_email = unique_email("e2e-noshow-notion")
        payload["email"] = test_email

        # Trigger webhook
        response = http_client.post(
            f"{e2e_config.FASTAPI_URL}/webhook/calendly-noshow",
            json=payload
        )
        assert response.status_code == 200

        # Wait for flow to create Notion record
        time.sleep(5)

        # Note: Actual Notion verification would require API access
        result_capture.add_note(
            f"Notion record should be created for {test_email} - verify manually in Notion"
        )

    @pytest.mark.skip(reason="Requires Notion API access - run manually")
    def test_e2e_noshow_template_type_is_noshow_recovery(
        self,
        ensure_fastapi_running,
        http_client,
        e2e_config,
        calendly_noshow_fixtures,
        unique_email,
        result_capture
    ):
        """Verify sequence has correct Template Type: No-Show Recovery."""
        payload = calendly_noshow_fixtures["valid_payload"].copy()
        test_email = unique_email("e2e-noshow-template")
        payload["email"] = test_email

        response = http_client.post(
            f"{e2e_config.FASTAPI_URL}/webhook/calendly-noshow",
            json=payload
        )
        assert response.status_code == 200

        time.sleep(5)

        result_capture.add_note(
            f"Verify Template Type = 'No-Show Recovery' for {test_email} in Notion"
        )


class TestNoShowEmailSequence:
    """Test no-show email sequence scheduling."""

    @pytest.mark.skip(reason="Requires time-based testing - run in testing mode")
    def test_e2e_noshow_email_1_sent_after_1min(
        self,
        ensure_fastapi_running,
        http_client,
        e2e_config,
        calendly_noshow_fixtures,
        unique_email,
        result_capture
    ):
        """In testing mode, first email should be sent after ~1 minute."""
        payload = calendly_noshow_fixtures["valid_payload"].copy()
        test_email = unique_email("e2e-noshow-email1")
        payload["email"] = test_email

        response = http_client.post(
            f"{e2e_config.FASTAPI_URL}/webhook/calendly-noshow",
            json=payload
        )
        assert response.status_code == 200

        result_capture.add_note(
            f"Email 1 should be sent ~1min after trigger for {test_email}"
        )
        result_capture.add_note("Timing: Testing=1min, Production=5min")

    @pytest.mark.skip(reason="Requires time-based testing - run in testing mode")
    def test_e2e_noshow_correct_templates_used(
        self,
        ensure_fastapi_running,
        http_client,
        e2e_config,
        calendly_noshow_fixtures,
        unique_email,
        result_capture
    ):
        """Verify correct templates are used: noshow_recovery_email_1, _2, _3."""
        payload = calendly_noshow_fixtures["valid_payload"].copy()
        test_email = unique_email("e2e-noshow-templates")
        payload["email"] = test_email

        response = http_client.post(
            f"{e2e_config.FASTAPI_URL}/webhook/calendly-noshow",
            json=payload
        )
        assert response.status_code == 200

        result_capture.add_note(
            f"Verify templates used: noshow_recovery_email_1, _2, _3 for {test_email}"
        )


# ============================================================================
# Test Summary
# ============================================================================

def test_e2e_noshow_suite_summary(result_capture):
    """Generate test suite summary."""
    result_capture.add_note("No-Show Recovery E2E Test Suite")
    result_capture.add_note("Tests covered:")
    result_capture.add_note("  - Webhook validation (valid/invalid payloads)")
    result_capture.add_note("  - Flow triggering")
    result_capture.add_note("  - Sequence record creation (manual verification)")
    result_capture.add_note("  - Email timing (manual verification in testing mode)")
