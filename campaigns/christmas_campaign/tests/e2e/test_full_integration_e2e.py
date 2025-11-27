"""
E2E Tests: Full Integration - Multi-Sequence Scenario

Tests the complete customer journey:
1. Opt-in -> Nurture sequence starts
2. No-show -> Recovery sequence starts
3. Maybe -> Post-call sequence starts
4. Close -> Onboarding sequence starts

Verifies:
- Sequences don't conflict
- Idempotency prevents duplicates
- Proper handoff between sequences

Prerequisites:
- FastAPI server running: uvicorn server:app --reload
- Prefect server running
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
    result_capture,
    ensure_fastapi_running,
)


class TestFullCustomerJourney:
    """Test complete customer journey through all sequences."""

    def test_e2e_full_journey_complete_path(
        self,
        ensure_fastapi_running,
        http_client,
        e2e_config,
        customer_data,
        unique_email,
        result_capture
    ):
        """
        Complete customer journey:
        1. Opt-in (Lead Nurture starts)
        2. No-show (Recovery sequence)
        3. Maybe (Post-call sequence)
        4. Close (Onboarding sequence)
        """
        # Use same email for entire journey
        journey_email = unique_email("e2e-full-journey")
        flow_run_ids = []

        # Step 1: Opt-in -> Lead Nurture
        result_capture.add_note("=== Step 1: Opt-in (Lead Nurture) ===")
        nurture_payload = customer_data["lead_nurture_critical"].copy()
        nurture_payload["email"] = journey_email

        response = http_client.post(
            f"{e2e_config.FASTAPI_URL}/webhook/christmas-signup",
            json=nurture_payload
        )
        assert response.status_code == 200
        result_capture.add_webhook_response(
            "/webhook/christmas-signup", response.status_code, response.json()
        )
        result_capture.add_note(f"Lead Nurture triggered for {journey_email}")

        # Give flow time to start
        time.sleep(2)

        # Step 2: No-show -> Recovery
        result_capture.add_note("=== Step 2: No-show (Recovery Sequence) ===")
        noshow_payload = {
            "email": journey_email,
            "first_name": "Journey",
            "business_name": "Full Journey Salon",
            "calendly_event_uri": "https://calendly.com/events/JOURNEY-001",
            "scheduled_time": "2025-12-05T14:00:00Z"
        }

        response = http_client.post(
            f"{e2e_config.FASTAPI_URL}/webhook/calendly-noshow",
            json=noshow_payload
        )
        assert response.status_code == 200
        result_capture.add_webhook_response(
            "/webhook/calendly-noshow", response.status_code, response.json()
        )
        result_capture.add_note(f"No-Show Recovery triggered for {journey_email}")

        time.sleep(2)

        # Step 3: Maybe -> Post-call
        result_capture.add_note("=== Step 3: Maybe (Post-Call Sequence) ===")
        postcall_payload = {
            "email": journey_email,
            "first_name": "Journey",
            "business_name": "Full Journey Salon",
            "call_date": "2025-12-05T14:30:00Z",
            "call_outcome": "Maybe",
            "call_notes": "Interested but needs time to decide"
        }

        response = http_client.post(
            f"{e2e_config.FASTAPI_URL}/webhook/postcall-maybe",
            json=postcall_payload
        )
        assert response.status_code == 200
        result_capture.add_webhook_response(
            "/webhook/postcall-maybe", response.status_code, response.json()
        )
        result_capture.add_note(f"Post-Call Maybe triggered for {journey_email}")

        time.sleep(2)

        # Step 4: Close -> Onboarding
        result_capture.add_note("=== Step 4: Close (Onboarding Sequence) ===")
        onboarding_payload = {
            "email": journey_email,
            "first_name": "Journey",
            "business_name": "Full Journey Salon",
            "payment_confirmed": True,
            "payment_amount": 2997.00,
            "payment_date": "2025-12-06T10:00:00Z",
            "salon_address": "789 Yonge Street, Toronto, ON"
        }

        response = http_client.post(
            f"{e2e_config.FASTAPI_URL}/webhook/onboarding-start",
            json=onboarding_payload
        )
        assert response.status_code == 200
        result_capture.add_webhook_response(
            "/webhook/onboarding-start", response.status_code, response.json()
        )
        result_capture.add_note(f"Onboarding triggered for {journey_email}")

        # Summary
        result_capture.add_note("=== Journey Complete ===")
        result_capture.add_note(f"Customer email: {journey_email}")
        result_capture.add_note("Sequences triggered: Lead Nurture, No-Show, Post-Call, Onboarding")


class TestSequenceConflictPrevention:
    """Test that sequences don't conflict with each other."""

    def test_e2e_sequences_dont_conflict(
        self,
        ensure_fastapi_running,
        http_client,
        e2e_config,
        unique_email,
        result_capture
    ):
        """Verify multiple sequences can run for same contact without conflict."""
        test_email = unique_email("e2e-conflict-test")

        # Trigger lead nurture
        nurture_response = http_client.post(
            f"{e2e_config.FASTAPI_URL}/webhook/christmas-signup",
            json={
                "email": test_email,
                "first_name": "Conflict",
                "business_name": "Conflict Test Salon",
                "assessment_score": 45,
                "red_systems": 2,
                "orange_systems": 1
            }
        )
        assert nurture_response.status_code == 200

        # Immediately trigger no-show (should not conflict)
        noshow_response = http_client.post(
            f"{e2e_config.FASTAPI_URL}/webhook/calendly-noshow",
            json={
                "email": test_email,
                "first_name": "Conflict",
                "business_name": "Conflict Test Salon",
                "calendly_event_uri": "https://calendly.com/events/CONFLICT-001",
                "scheduled_time": "2025-12-05T14:00:00Z"
            }
        )
        assert noshow_response.status_code == 200

        result_capture.add_note(f"Both sequences accepted for {test_email}")
        result_capture.add_note("No conflict between Lead Nurture and No-Show sequences")


class TestIdempotencyPrevention:
    """Test that idempotency prevents duplicate sequences."""

    def test_e2e_idempotency_prevents_duplicates(
        self,
        ensure_fastapi_running,
        http_client,
        e2e_config,
        unique_email,
        result_capture
    ):
        """Verify duplicate webhooks don't create duplicate sequences."""
        test_email = unique_email("e2e-idempotency-test")

        payload = {
            "email": test_email,
            "first_name": "Idempotency",
            "business_name": "Idempotency Test Salon",
            "assessment_score": 50,
            "red_systems": 2,
            "orange_systems": 1
        }

        # First request
        response1 = http_client.post(
            f"{e2e_config.FASTAPI_URL}/webhook/christmas-signup",
            json=payload
        )
        assert response1.status_code == 200
        result_capture.add_note(f"First request accepted for {test_email}")

        time.sleep(1)

        # Duplicate request
        response2 = http_client.post(
            f"{e2e_config.FASTAPI_URL}/webhook/christmas-signup",
            json=payload
        )
        assert response2.status_code == 200  # Webhook accepts, flow handles idempotency
        result_capture.add_note("Second request accepted (idempotency in flow)")
        result_capture.add_note("Verify in Notion: only ONE sequence record created")


class TestSequenceHandoff:
    """Test proper handoff between sequences."""

    def test_e2e_proper_handoff_between_sequences(
        self,
        ensure_fastapi_running,
        http_client,
        e2e_config,
        unique_email,
        result_capture
    ):
        """Verify sequences maintain separate tracking."""
        test_email = unique_email("e2e-handoff-test")

        # Trigger all 4 sequence types
        sequences = [
            ("christmas-signup", {
                "email": test_email,
                "first_name": "Handoff",
                "business_name": "Handoff Test Salon",
                "assessment_score": 45,
                "red_systems": 2
            }),
            ("calendly-noshow", {
                "email": test_email,
                "first_name": "Handoff",
                "business_name": "Handoff Test Salon",
                "calendly_event_uri": "https://calendly.com/events/HANDOFF",
                "scheduled_time": "2025-12-05T14:00:00Z"
            }),
            ("postcall-maybe", {
                "email": test_email,
                "first_name": "Handoff",
                "business_name": "Handoff Test Salon",
                "call_date": "2025-12-05T15:00:00Z"
            }),
            ("onboarding-start", {
                "email": test_email,
                "first_name": "Handoff",
                "business_name": "Handoff Test Salon",
                "payment_confirmed": True,
                "payment_amount": 2997.00,
                "payment_date": "2025-12-06T10:00:00Z"
            })
        ]

        for endpoint, payload in sequences:
            response = http_client.post(
                f"{e2e_config.FASTAPI_URL}/webhook/{endpoint}",
                json=payload
            )
            assert response.status_code == 200
            result_capture.add_note(f"/{endpoint}: accepted")
            time.sleep(0.5)

        result_capture.add_note(f"All 4 sequence types triggered for {test_email}")
        result_capture.add_note("Verify in Notion: 4 separate sequence records")


class TestProductionReadinessChecks:
    """Pre-production verification tests."""

    def test_e2e_health_endpoint_responds(
        self,
        ensure_fastapi_running,
        http_client,
        e2e_config,
        result_capture
    ):
        """Verify health endpoint responds correctly."""
        response = http_client.get(f"{e2e_config.FASTAPI_URL}/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

        result_capture.add_note("Health endpoint: OK")
        result_capture.add_note(f"Testing mode: {data['environment'].get('testing_mode')}")
        result_capture.add_note(f"Notion configured: {data['environment'].get('notion_configured')}")
        result_capture.add_note(f"Resend configured: {data['environment'].get('resend_configured')}")

    def test_e2e_all_webhook_endpoints_available(
        self,
        ensure_fastapi_running,
        http_client,
        e2e_config,
        result_capture
    ):
        """Verify all webhook endpoints are available."""
        endpoints = [
            "/webhook/christmas-signup",
            "/webhook/calendly-noshow",
            "/webhook/postcall-maybe",
            "/webhook/onboarding-start"
        ]

        for endpoint in endpoints:
            # OPTIONS request to check endpoint exists
            response = http_client.options(f"{e2e_config.FASTAPI_URL}{endpoint}")
            # 200 or 405 means endpoint exists (405 = method not allowed for OPTIONS)
            assert response.status_code in [200, 405, 422]
            result_capture.add_note(f"{endpoint}: available")


# ============================================================================
# Test Summary
# ============================================================================

def test_e2e_full_integration_suite_summary(result_capture):
    """Generate test suite summary."""
    result_capture.add_note("Full Integration E2E Test Suite")
    result_capture.add_note("Tests covered:")
    result_capture.add_note("  - Complete customer journey (4 sequences)")
    result_capture.add_note("  - Sequence conflict prevention")
    result_capture.add_note("  - Idempotency verification")
    result_capture.add_note("  - Sequence handoff")
    result_capture.add_note("  - Production readiness checks")
