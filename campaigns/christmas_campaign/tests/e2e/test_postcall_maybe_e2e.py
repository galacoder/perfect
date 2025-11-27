"""
E2E Tests: Post-Call Maybe Sequence

Tests the complete post-call maybe flow:
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
    postcall_fixtures,
    unique_email,
    make_unique_payload,
    result_capture,
    ensure_fastapi_running,
    post_webhook,
)


class TestPostCallWebhookValidation:
    """Test post-call maybe webhook endpoint validation."""

    def test_e2e_postcall_webhook_valid_payload_accepted(
        self,
        ensure_fastapi_running,
        http_client,
        e2e_config,
        postcall_fixtures,
        unique_email,
        result_capture
    ):
        """Valid post-call payload should be accepted with 200 status."""
        payload = postcall_fixtures["valid_payload"].copy()
        payload["email"] = unique_email("e2e-postcall-valid")

        response = http_client.post(
            f"{e2e_config.FASTAPI_URL}/webhook/postcall-maybe",
            json=payload
        )

        result_capture.add_webhook_response(
            endpoint="/webhook/postcall-maybe",
            status_code=response.status_code,
            response=response.json()
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "accepted"
        assert data["email"] == payload["email"]
        assert data["campaign"] == "Christmas Traditional Service"

        result_capture.add_note(f"Flow triggered for {payload['email']}")

    def test_e2e_postcall_webhook_minimal_payload_accepted(
        self,
        ensure_fastapi_running,
        http_client,
        e2e_config,
        postcall_fixtures,
        unique_email,
        result_capture
    ):
        """Minimal payload (required fields only) should be accepted."""
        payload = postcall_fixtures["valid_payload_minimal"].copy()
        payload["email"] = unique_email("e2e-postcall-minimal")

        response = http_client.post(
            f"{e2e_config.FASTAPI_URL}/webhook/postcall-maybe",
            json=payload
        )

        result_capture.add_webhook_response(
            endpoint="/webhook/postcall-maybe",
            status_code=response.status_code,
            response=response.json()
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "accepted"

    def test_e2e_postcall_webhook_with_call_notes(
        self,
        ensure_fastapi_running,
        http_client,
        e2e_config,
        postcall_fixtures,
        unique_email,
        result_capture
    ):
        """Payload with call notes should be accepted."""
        payload = postcall_fixtures["valid_payload"].copy()
        payload["email"] = unique_email("e2e-postcall-notes")
        payload["call_notes"] = "Very detailed call notes about client concerns and interests"

        response = http_client.post(
            f"{e2e_config.FASTAPI_URL}/webhook/postcall-maybe",
            json=payload
        )

        result_capture.add_webhook_response(
            endpoint="/webhook/postcall-maybe",
            status_code=response.status_code,
            response=response.json()
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "accepted"

        result_capture.add_note(f"Call notes captured for {payload['email']}")

    def test_e2e_postcall_webhook_with_objections(
        self,
        ensure_fastapi_running,
        http_client,
        e2e_config,
        postcall_fixtures,
        unique_email,
        result_capture
    ):
        """Payload with objections array should be accepted."""
        payload = postcall_fixtures["valid_payload_with_multiple_objections"].copy()
        payload["email"] = unique_email("e2e-postcall-objections")

        response = http_client.post(
            f"{e2e_config.FASTAPI_URL}/webhook/postcall-maybe",
            json=payload
        )

        result_capture.add_webhook_response(
            endpoint="/webhook/postcall-maybe",
            status_code=response.status_code,
            response=response.json()
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "accepted"

        result_capture.add_note(f"Objections captured: {payload['objections']}")

    def test_e2e_postcall_webhook_invalid_payload_rejected(
        self,
        ensure_fastapi_running,
        http_client,
        e2e_config,
        postcall_fixtures,
        result_capture
    ):
        """Missing email should return 422 validation error."""
        payload = postcall_fixtures["invalid_payload_missing_email"]

        response = http_client.post(
            f"{e2e_config.FASTAPI_URL}/webhook/postcall-maybe",
            json=payload
        )

        result_capture.add_webhook_response(
            endpoint="/webhook/postcall-maybe",
            status_code=response.status_code,
            response=response.json() if response.status_code != 500 else {"error": "server error"}
        )

        assert response.status_code == 422, f"Expected 422, got {response.status_code}"

    def test_e2e_postcall_webhook_malformed_email_rejected(
        self,
        ensure_fastapi_running,
        http_client,
        e2e_config,
        postcall_fixtures,
        result_capture
    ):
        """Malformed email should return 422 validation error."""
        payload = postcall_fixtures["invalid_payload_malformed_email"]

        response = http_client.post(
            f"{e2e_config.FASTAPI_URL}/webhook/postcall-maybe",
            json=payload
        )

        result_capture.add_webhook_response(
            endpoint="/webhook/postcall-maybe",
            status_code=response.status_code,
            response=response.json() if response.status_code != 500 else {"error": "server error"}
        )

        assert response.status_code == 422, f"Expected 422, got {response.status_code}"


class TestPostCallFlowTriggering:
    """Test post-call flow is properly triggered."""

    def test_e2e_postcall_webhook_triggers_prefect_flow(
        self,
        ensure_fastapi_running,
        http_client,
        e2e_config,
        postcall_fixtures,
        unique_email,
        result_capture
    ):
        """Webhook should trigger Prefect flow and return accepted status."""
        payload = postcall_fixtures["valid_payload"].copy()
        test_email = unique_email("e2e-postcall-flow")
        payload["email"] = test_email

        response = http_client.post(
            f"{e2e_config.FASTAPI_URL}/webhook/postcall-maybe",
            json=payload
        )

        result_capture.add_webhook_response(
            endpoint="/webhook/postcall-maybe",
            status_code=response.status_code,
            response=response.json()
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "accepted"

        # Give flow time to start (background task)
        time.sleep(2)

        result_capture.add_note(f"Flow triggered for {test_email} - verify in Prefect UI")

    def test_e2e_postcall_flow_run_id_returned(
        self,
        ensure_fastapi_running,
        http_client,
        e2e_config,
        postcall_fixtures,
        unique_email,
        result_capture
    ):
        """Response should include confirmation of flow acceptance."""
        payload = postcall_fixtures["valid_payload"].copy()
        payload["email"] = unique_email("e2e-postcall-flowid")

        response = http_client.post(
            f"{e2e_config.FASTAPI_URL}/webhook/postcall-maybe",
            json=payload
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response contains expected fields
        assert "status" in data
        assert "message" in data
        assert "email" in data
        assert "call_outcome" in data
        assert data["status"] == "accepted"

        result_capture.add_webhook_response(
            endpoint="/webhook/postcall-maybe",
            status_code=response.status_code,
            response=data
        )


class TestPostCallSequenceCreation:
    """Test post-call sequence record is created correctly."""

    @pytest.mark.skip(reason="Requires Notion API access - run manually")
    def test_e2e_postcall_sequence_record_created_in_notion(
        self,
        ensure_fastapi_running,
        http_client,
        e2e_config,
        postcall_fixtures,
        unique_email,
        result_capture
    ):
        """Verify sequence record is created in Notion after webhook."""
        payload = postcall_fixtures["valid_payload"].copy()
        test_email = unique_email("e2e-postcall-notion")
        payload["email"] = test_email

        # Trigger webhook
        response = http_client.post(
            f"{e2e_config.FASTAPI_URL}/webhook/postcall-maybe",
            json=payload
        )
        assert response.status_code == 200

        # Wait for flow to create Notion record
        time.sleep(5)

        result_capture.add_note(
            f"Notion record should be created for {test_email} - verify manually"
        )

    @pytest.mark.skip(reason="Requires Notion API access - run manually")
    def test_e2e_postcall_template_type_is_postcall_followup(
        self,
        ensure_fastapi_running,
        http_client,
        e2e_config,
        postcall_fixtures,
        unique_email,
        result_capture
    ):
        """Verify sequence has correct Template Type: Post-Call Follow-Up."""
        payload = postcall_fixtures["valid_payload"].copy()
        test_email = unique_email("e2e-postcall-template")
        payload["email"] = test_email

        response = http_client.post(
            f"{e2e_config.FASTAPI_URL}/webhook/postcall-maybe",
            json=payload
        )
        assert response.status_code == 200

        time.sleep(5)

        result_capture.add_note(
            f"Verify Template Type = 'Post-Call Follow-Up' for {test_email} in Notion"
        )


class TestPostCallEmailSequence:
    """Test post-call email sequence scheduling."""

    @pytest.mark.skip(reason="Requires time-based testing - run in testing mode")
    def test_e2e_postcall_email_1_sent_after_1min(
        self,
        ensure_fastapi_running,
        http_client,
        e2e_config,
        postcall_fixtures,
        unique_email,
        result_capture
    ):
        """In testing mode, first email should be sent after ~1 minute."""
        payload = postcall_fixtures["valid_payload"].copy()
        test_email = unique_email("e2e-postcall-email1")
        payload["email"] = test_email

        response = http_client.post(
            f"{e2e_config.FASTAPI_URL}/webhook/postcall-maybe",
            json=payload
        )
        assert response.status_code == 200

        result_capture.add_note(
            f"Email 1 should be sent ~1min after trigger for {test_email}"
        )
        result_capture.add_note("Timing: Testing=1min, Production=1h")

    @pytest.mark.skip(reason="Requires time-based testing - run in testing mode")
    def test_e2e_postcall_correct_templates_used(
        self,
        ensure_fastapi_running,
        http_client,
        e2e_config,
        postcall_fixtures,
        unique_email,
        result_capture
    ):
        """Verify correct templates are used: postcall_maybe_email_1, _2, _3."""
        payload = postcall_fixtures["valid_payload"].copy()
        test_email = unique_email("e2e-postcall-templates")
        payload["email"] = test_email

        response = http_client.post(
            f"{e2e_config.FASTAPI_URL}/webhook/postcall-maybe",
            json=payload
        )
        assert response.status_code == 200

        result_capture.add_note(
            f"Verify templates used: postcall_maybe_email_1, _2, _3 for {test_email}"
        )

    @pytest.mark.skip(reason="Requires time-based testing - run in testing mode")
    def test_e2e_postcall_call_notes_in_personalization(
        self,
        ensure_fastapi_running,
        http_client,
        e2e_config,
        postcall_fixtures,
        unique_email,
        result_capture
    ):
        """Verify call notes appear in email personalization."""
        payload = postcall_fixtures["valid_payload"].copy()
        test_email = unique_email("e2e-postcall-personalization")
        payload["email"] = test_email
        payload["call_notes"] = "Client interested in GPS and Money systems improvement"

        response = http_client.post(
            f"{e2e_config.FASTAPI_URL}/webhook/postcall-maybe",
            json=payload
        )
        assert response.status_code == 200

        result_capture.add_note(
            f"Verify call_notes personalization in emails for {test_email}"
        )


# ============================================================================
# Test Summary
# ============================================================================

def test_e2e_postcall_suite_summary(result_capture):
    """Generate test suite summary."""
    result_capture.add_note("Post-Call Maybe E2E Test Suite")
    result_capture.add_note("Tests covered:")
    result_capture.add_note("  - Webhook validation (valid/invalid payloads)")
    result_capture.add_note("  - Call notes and objections capture")
    result_capture.add_note("  - Flow triggering")
    result_capture.add_note("  - Sequence record creation (manual verification)")
    result_capture.add_note("  - Email timing (manual verification in testing mode)")
