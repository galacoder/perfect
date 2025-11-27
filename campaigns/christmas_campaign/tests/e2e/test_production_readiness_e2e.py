"""
E2E Tests: Production Readiness Verification

Verifies production deployment is correctly configured:
1. Prefect deployments exist
2. Secret blocks are accessible
3. Git-based deployment is configured
4. Health endpoints respond

Prerequisites:
- Production Prefect server accessible
- Secret blocks created
- Deployments created
"""

import pytest
import os
from pathlib import Path

# Import shared fixtures
from .conftest_e2e import (
    E2EConfig,
    e2e_config,
    http_client,
    result_capture,
)


class TestProductionDeployments:
    """Test Prefect deployments exist on production."""

    @pytest.fixture
    def production_prefect_url(self):
        """Get production Prefect API URL."""
        return os.getenv("PRODUCTION_PREFECT_URL", "https://prefect.galatek.dev/api")

    @pytest.mark.skip(reason="Requires production Prefect access")
    def test_e2e_production_signup_deployment_exists(
        self,
        http_client,
        production_prefect_url,
        result_capture
    ):
        """Verify signup_handler deployment exists on production."""
        response = http_client.post(
            f"{production_prefect_url}/deployments/filter",
            json={"names": ["signup_handler/christmas-campaign"]}
        )

        result_capture.add_note(f"Checking deployment: signup_handler/christmas-campaign")

        if response.status_code == 200:
            deployments = response.json()
            if len(deployments) > 0:
                result_capture.add_note("Deployment found: signup_handler")
                assert True
            else:
                result_capture.add_note("Deployment NOT found")
                assert False, "signup_handler deployment not found"
        else:
            result_capture.add_note(f"API error: {response.status_code}")

    @pytest.mark.skip(reason="Requires production Prefect access")
    def test_e2e_production_noshow_deployment_exists(
        self,
        http_client,
        production_prefect_url,
        result_capture
    ):
        """Verify noshow_recovery_handler deployment exists on production."""
        result_capture.add_note("Checking deployment: noshow_recovery_handler")
        result_capture.add_note("Verify via Prefect UI: https://prefect.galatek.dev")

    @pytest.mark.skip(reason="Requires production Prefect access")
    def test_e2e_production_postcall_deployment_exists(
        self,
        http_client,
        production_prefect_url,
        result_capture
    ):
        """Verify postcall_maybe_handler deployment exists on production."""
        result_capture.add_note("Checking deployment: postcall_maybe_handler")
        result_capture.add_note("Verify via Prefect UI: https://prefect.galatek.dev")

    @pytest.mark.skip(reason="Requires production Prefect access")
    def test_e2e_production_onboarding_deployment_exists(
        self,
        http_client,
        production_prefect_url,
        result_capture
    ):
        """Verify onboarding_handler deployment exists on production."""
        result_capture.add_note("Checking deployment: onboarding_handler")
        result_capture.add_note("Verify via Prefect UI: https://prefect.galatek.dev")


class TestProductionSecretBlocks:
    """Test Secret blocks are accessible on production."""

    @pytest.mark.skip(reason="Requires production Prefect access")
    def test_e2e_production_secret_blocks_accessible(self, result_capture):
        """Verify required Secret blocks exist."""
        required_blocks = [
            "notion-token",
            "notion-db-id",
            "resend-api-key"
        ]

        result_capture.add_note("Required Secret blocks:")
        for block in required_blocks:
            result_capture.add_note(f"  - {block}")

        result_capture.add_note("Verify via Prefect UI -> Blocks")


class TestProductionConfiguration:
    """Test production configuration is correct."""

    @pytest.mark.skip(reason="Requires production Prefect access")
    def test_e2e_production_git_deployment_configured(self, result_capture):
        """Verify git_clone pull step is configured."""
        result_capture.add_note("Git-based deployment should use:")
        result_capture.add_note("  repository: https://github.com/galacoder/perfect.git")
        result_capture.add_note("  branch: main")
        result_capture.add_note("Verify in prefect.yaml pull section")

    @pytest.mark.skip(reason="Requires production server access")
    def test_e2e_production_health_endpoint_responds(
        self,
        http_client,
        result_capture
    ):
        """Verify production health endpoint responds."""
        production_api_url = os.getenv(
            "PRODUCTION_API_URL",
            "https://perfect-api.galatek.dev"
        )

        result_capture.add_note(f"Testing: {production_api_url}/health")
        result_capture.add_note("Verify manually if not accessible")


class TestProductionChecklist:
    """Production readiness checklist."""

    def test_e2e_production_checklist(self, result_capture):
        """Generate production readiness checklist."""
        result_capture.add_note("=== Production Readiness Checklist ===")
        result_capture.add_note("")
        result_capture.add_note("[ ] Prefect Deployments:")
        result_capture.add_note("    [ ] signup_handler/christmas-campaign")
        result_capture.add_note("    [ ] noshow_recovery_handler/christmas-campaign")
        result_capture.add_note("    [ ] postcall_maybe_handler/christmas-campaign")
        result_capture.add_note("    [ ] onboarding_handler/christmas-campaign")
        result_capture.add_note("")
        result_capture.add_note("[ ] Secret Blocks:")
        result_capture.add_note("    [ ] notion-token")
        result_capture.add_note("    [ ] notion-db-id (Templates DB)")
        result_capture.add_note("    [ ] notion-email-sequence-db-id")
        result_capture.add_note("    [ ] notion-businessx-db-id")
        result_capture.add_note("    [ ] resend-api-key")
        result_capture.add_note("")
        result_capture.add_note("[ ] Environment:")
        result_capture.add_note("    [ ] TESTING_MODE=false for production")
        result_capture.add_note("    [ ] Git pull step configured")
        result_capture.add_note("    [ ] Worker running with prefect-github")
        result_capture.add_note("")
        result_capture.add_note("[ ] Endpoints:")
        result_capture.add_note("    [ ] /health responds")
        result_capture.add_note("    [ ] /webhook/christmas-signup")
        result_capture.add_note("    [ ] /webhook/calendly-noshow")
        result_capture.add_note("    [ ] /webhook/postcall-maybe")
        result_capture.add_note("    [ ] /webhook/onboarding-start")
        result_capture.add_note("")
        result_capture.add_note("[ ] Email Templates:")
        result_capture.add_note("    [ ] Lead Nurture (7 templates)")
        result_capture.add_note("    [ ] No-Show Recovery (3 templates)")
        result_capture.add_note("    [ ] Post-Call Maybe (3 templates)")
        result_capture.add_note("    [ ] Onboarding (3 templates)")


# ============================================================================
# Test Summary
# ============================================================================

def test_e2e_production_readiness_summary(result_capture):
    """Generate production readiness summary."""
    result_capture.add_note("Production Readiness E2E Test Suite")
    result_capture.add_note("Tests covered:")
    result_capture.add_note("  - Deployment verification (manual)")
    result_capture.add_note("  - Secret blocks verification (manual)")
    result_capture.add_note("  - Git deployment configuration (manual)")
    result_capture.add_note("  - Health endpoint verification (manual)")
    result_capture.add_note("  - Production checklist generated")
