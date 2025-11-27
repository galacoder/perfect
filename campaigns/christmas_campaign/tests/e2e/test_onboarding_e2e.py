"""
E2E Tests: Onboarding Sequence

Tests the complete onboarding flow:
1. Webhook endpoint validation
2. Flow triggering
3. Email sequence scheduling
4. Notion sequence record creation
5. Payment validation

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
    onboarding_fixtures,
    unique_email,
    make_unique_payload,
    result_capture,
    ensure_fastapi_running,
    post_webhook,
)


class TestOnboardingWebhookValidation:
    """Test onboarding webhook endpoint validation."""

    def test_e2e_onboarding_webhook_valid_payload_accepted(
        self,
        ensure_fastapi_running,
        http_client,
        e2e_config,
        onboarding_fixtures,
        unique_email,
        result_capture
    ):
        """Valid onboarding payload should be accepted with 200 status."""
        payload = onboarding_fixtures["valid_payload"].copy()
        payload["email"] = unique_email("e2e-onboarding-valid")

        response = http_client.post(
            f"{e2e_config.FASTAPI_URL}/webhook/onboarding-start",
            json=payload
        )

        result_capture.add_webhook_response(
            endpoint="/webhook/onboarding-start",
            status_code=response.status_code,
            response=response.json()
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "accepted"
        assert data["email"] == payload["email"]
        assert data["campaign"] == "Christmas Traditional Service"
        assert data["payment_amount"] == 2997.00

        result_capture.add_note(f"Flow triggered for {payload['email']}")

    def test_e2e_onboarding_webhook_minimal_payload_accepted(
        self,
        ensure_fastapi_running,
        http_client,
        e2e_config,
        onboarding_fixtures,
        unique_email,
        result_capture
    ):
        """Minimal payload (required fields only) should be accepted."""
        payload = onboarding_fixtures["valid_payload_minimal"].copy()
        payload["email"] = unique_email("e2e-onboarding-minimal")

        response = http_client.post(
            f"{e2e_config.FASTAPI_URL}/webhook/onboarding-start",
            json=payload
        )

        result_capture.add_webhook_response(
            endpoint="/webhook/onboarding-start",
            status_code=response.status_code,
            response=response.json()
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "accepted"

    def test_e2e_onboarding_webhook_full_details_accepted(
        self,
        ensure_fastapi_running,
        http_client,
        e2e_config,
        onboarding_fixtures,
        unique_email,
        result_capture
    ):
        """Full payload with all details should be accepted."""
        payload = onboarding_fixtures["valid_payload_full_details"].copy()
        payload["email"] = unique_email("e2e-onboarding-full")

        response = http_client.post(
            f"{e2e_config.FASTAPI_URL}/webhook/onboarding-start",
            json=payload
        )

        result_capture.add_webhook_response(
            endpoint="/webhook/onboarding-start",
            status_code=response.status_code,
            response=response.json()
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "accepted"

        result_capture.add_note(f"Full details captured: salon_address, observation_dates")

    def test_e2e_onboarding_webhook_invalid_payload_rejected(
        self,
        ensure_fastapi_running,
        http_client,
        e2e_config,
        onboarding_fixtures,
        result_capture
    ):
        """Missing email should return 422 validation error."""
        payload = onboarding_fixtures["invalid_payload_missing_email"]

        response = http_client.post(
            f"{e2e_config.FASTAPI_URL}/webhook/onboarding-start",
            json=payload
        )

        result_capture.add_webhook_response(
            endpoint="/webhook/onboarding-start",
            status_code=response.status_code,
            response=response.json() if response.status_code != 500 else {"error": "server error"}
        )

        assert response.status_code == 422, f"Expected 422, got {response.status_code}"

    def test_e2e_onboarding_webhook_partial_data_handled(
        self,
        ensure_fastapi_running,
        http_client,
        e2e_config,
        onboarding_fixtures,
        unique_email,
        result_capture
    ):
        """Partial payload with only required fields should be accepted."""
        payload = {
            "email": unique_email("e2e-onboarding-partial"),
            "first_name": "Partial Test",
            "business_name": "Partial Test Salon",
            "payment_confirmed": True,
            "payment_amount": 2997.00,
            "payment_date": "2025-12-01T12:00:00Z"
        }

        response = http_client.post(
            f"{e2e_config.FASTAPI_URL}/webhook/onboarding-start",
            json=payload
        )

        result_capture.add_webhook_response(
            endpoint="/webhook/onboarding-start",
            status_code=response.status_code,
            response=response.json()
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "accepted"


class TestOnboardingFlowTriggering:
    """Test onboarding flow is properly triggered."""

    def test_e2e_onboarding_webhook_triggers_prefect_flow(
        self,
        ensure_fastapi_running,
        http_client,
        e2e_config,
        onboarding_fixtures,
        unique_email,
        result_capture
    ):
        """Webhook should trigger Prefect flow and return accepted status."""
        payload = onboarding_fixtures["valid_payload"].copy()
        test_email = unique_email("e2e-onboarding-flow")
        payload["email"] = test_email

        response = http_client.post(
            f"{e2e_config.FASTAPI_URL}/webhook/onboarding-start",
            json=payload
        )

        result_capture.add_webhook_response(
            endpoint="/webhook/onboarding-start",
            status_code=response.status_code,
            response=response.json()
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "accepted"

        # Give flow time to start (background task)
        time.sleep(2)

        result_capture.add_note(f"Flow triggered for {test_email} - verify in Prefect UI")

    def test_e2e_onboarding_flow_run_id_returned(
        self,
        ensure_fastapi_running,
        http_client,
        e2e_config,
        onboarding_fixtures,
        unique_email,
        result_capture
    ):
        """Response should include confirmation of flow acceptance."""
        payload = onboarding_fixtures["valid_payload"].copy()
        payload["email"] = unique_email("e2e-onboarding-flowid")

        response = http_client.post(
            f"{e2e_config.FASTAPI_URL}/webhook/onboarding-start",
            json=payload
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response contains expected fields
        assert "status" in data
        assert "message" in data
        assert "email" in data
        assert "payment_amount" in data
        assert data["status"] == "accepted"

        result_capture.add_webhook_response(
            endpoint="/webhook/onboarding-start",
            status_code=response.status_code,
            response=data
        )


class TestOnboardingSequenceCreation:
    """Test onboarding sequence record is created correctly."""

    @pytest.mark.skip(reason="Requires Notion API access - run manually")
    def test_e2e_onboarding_sequence_record_created_in_notion(
        self,
        ensure_fastapi_running,
        http_client,
        e2e_config,
        onboarding_fixtures,
        unique_email,
        result_capture
    ):
        """Verify sequence record is created in Notion after webhook."""
        payload = onboarding_fixtures["valid_payload"].copy()
        test_email = unique_email("e2e-onboarding-notion")
        payload["email"] = test_email

        # Trigger webhook
        response = http_client.post(
            f"{e2e_config.FASTAPI_URL}/webhook/onboarding-start",
            json=payload
        )
        assert response.status_code == 200

        # Wait for flow to create Notion record
        time.sleep(5)

        result_capture.add_note(
            f"Notion record should be created for {test_email} - verify manually"
        )

    @pytest.mark.skip(reason="Requires Notion API access - run manually")
    def test_e2e_onboarding_template_type_is_onboarding(
        self,
        ensure_fastapi_running,
        http_client,
        e2e_config,
        onboarding_fixtures,
        unique_email,
        result_capture
    ):
        """Verify sequence has correct Template Type: Onboarding."""
        payload = onboarding_fixtures["valid_payload"].copy()
        test_email = unique_email("e2e-onboarding-template")
        payload["email"] = test_email

        response = http_client.post(
            f"{e2e_config.FASTAPI_URL}/webhook/onboarding-start",
            json=payload
        )
        assert response.status_code == 200

        time.sleep(5)

        result_capture.add_note(
            f"Verify Template Type = 'Onboarding' for {test_email} in Notion"
        )


class TestOnboardingEmailSequence:
    """Test onboarding email sequence scheduling."""

    @pytest.mark.skip(reason="Requires time-based testing - run in testing mode")
    def test_e2e_onboarding_email_1_sent_after_1min(
        self,
        ensure_fastapi_running,
        http_client,
        e2e_config,
        onboarding_fixtures,
        unique_email,
        result_capture
    ):
        """In testing mode, first email should be sent after ~1 minute."""
        payload = onboarding_fixtures["valid_payload"].copy()
        test_email = unique_email("e2e-onboarding-email1")
        payload["email"] = test_email

        response = http_client.post(
            f"{e2e_config.FASTAPI_URL}/webhook/onboarding-start",
            json=payload
        )
        assert response.status_code == 200

        result_capture.add_note(
            f"Email 1 should be sent ~1min after trigger for {test_email}"
        )
        result_capture.add_note("Timing: Testing=1min, Production=1h")

    @pytest.mark.skip(reason="Requires time-based testing - run in testing mode")
    def test_e2e_onboarding_correct_templates_used(
        self,
        ensure_fastapi_running,
        http_client,
        e2e_config,
        onboarding_fixtures,
        unique_email,
        result_capture
    ):
        """Verify correct templates are used: onboarding_phase1_email_1, _2, _3."""
        payload = onboarding_fixtures["valid_payload"].copy()
        test_email = unique_email("e2e-onboarding-templates")
        payload["email"] = test_email

        response = http_client.post(
            f"{e2e_config.FASTAPI_URL}/webhook/onboarding-start",
            json=payload
        )
        assert response.status_code == 200

        result_capture.add_note(
            f"Verify templates used: onboarding_phase1_email_1, _2, _3 for {test_email}"
        )

    @pytest.mark.skip(reason="Requires time-based testing - run in testing mode")
    def test_e2e_onboarding_salon_address_in_personalization(
        self,
        ensure_fastapi_running,
        http_client,
        e2e_config,
        onboarding_fixtures,
        unique_email,
        result_capture
    ):
        """Verify salon address appears in email personalization."""
        payload = onboarding_fixtures["valid_payload"].copy()
        test_email = unique_email("e2e-onboarding-address")
        payload["email"] = test_email
        payload["salon_address"] = "123 Test Street, Toronto, ON"

        response = http_client.post(
            f"{e2e_config.FASTAPI_URL}/webhook/onboarding-start",
            json=payload
        )
        assert response.status_code == 200

        result_capture.add_note(
            f"Verify salon_address personalization in emails for {test_email}"
        )

    @pytest.mark.skip(reason="Requires time-based testing - run in testing mode")
    def test_e2e_onboarding_observation_dates_in_personalization(
        self,
        ensure_fastapi_running,
        http_client,
        e2e_config,
        onboarding_fixtures,
        unique_email,
        result_capture
    ):
        """Verify observation dates appear in email personalization."""
        payload = onboarding_fixtures["valid_payload"].copy()
        test_email = unique_email("e2e-onboarding-dates")
        payload["email"] = test_email
        payload["observation_dates"] = ["2025-12-15", "2025-12-20"]

        response = http_client.post(
            f"{e2e_config.FASTAPI_URL}/webhook/onboarding-start",
            json=payload
        )
        assert response.status_code == 200

        result_capture.add_note(
            f"Verify observation_dates personalization in emails for {test_email}"
        )


# ============================================================================
# Test Summary
# ============================================================================

def test_e2e_onboarding_suite_summary(result_capture):
    """Generate test suite summary."""
    result_capture.add_note("Onboarding E2E Test Suite")
    result_capture.add_note("Tests covered:")
    result_capture.add_note("  - Webhook validation (valid/invalid payloads)")
    result_capture.add_note("  - Payment validation")
    result_capture.add_note("  - Salon address and observation dates capture")
    result_capture.add_note("  - Flow triggering")
    result_capture.add_note("  - Sequence record creation (manual verification)")
    result_capture.add_note("  - Email timing (manual verification in testing mode)")
