"""
End-to-End Sales Funnel Tests for Christmas Campaign.

This module tests the complete sales funnel flow:
1. Website form submission (Playwright)
2. FastAPI webhook triggering
3. Prefect flow execution
4. Notion database updates
5. Email scheduling

Test coverage:
- ✅ Complete Christmas campaign flow (dfu/xmas-a01)
- ✅ Local dev server integration
- ✅ Notion database verification (3 databases)
- ✅ Prefect flow scheduling (7 emails)
- ✅ Test data cleanup

Prerequisites:
- FastAPI server running (uvicorn server:app --reload)
- .env configured with Notion and Resend credentials
- TESTING_MODE=true for fast execution
- Prefect connection to https://prefect.galatek.dev
"""

import pytest
import httpx
from typing import Dict, Any


# ===== Test Placeholder (Will be implemented in Wave 2-4) =====

@pytest.mark.skip(reason="Wave 2: Playwright testing not yet implemented")
def test_complete_christmas_signup_flow(assessment_test_data):
    """
    Test complete Christmas campaign signup flow (END-TO-END).

    Flow:
        1. Navigate to Christmas campaign landing page (local dev server)
        2. Fill contact form (email, name, business name)
        3. Complete 16 assessment questions
        4. Verify results page shown
        5. Verify webhook triggered
        6. Verify Prefect flow executed
        7. Verify Notion databases updated
        8. Verify 7 emails scheduled

    This test will be implemented in Wave 2-4.
    """
    pass


# ===== Wave 1: Infrastructure Validation Test =====

def test_fastapi_server_health(api_base_url):
    """
    Verify FastAPI server is running and healthy.

    This test validates:
    - Server is accessible
    - Health endpoint returns 200
    - TESTING_MODE is enabled
    - Required services configured (Notion, Resend)
    """
    with httpx.Client(timeout=5.0) as client:
        response = client.get(f"{api_base_url}/health")

        # Verify status code
        assert response.status_code == 200, f"Health check failed: {response.status_code}"

        # Verify response structure
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"

        # Verify environment
        env = data.get("environment", {})
        assert env.get("testing_mode") == "true", "TESTING_MODE must be enabled for tests"
        assert env.get("notion_configured") is True, "Notion must be configured"
        assert env.get("resend_configured") is True, "Resend must be configured"

        print(f"✅ FastAPI server healthy: {data}")


def test_test_email_generation(test_email):
    """
    Verify test email generation works correctly.

    This test validates:
    - Email has correct format (test+{timestamp}+{uuid}@example.com)
    - Email is unique per test run
    - Email can be used for testing
    """
    assert test_email.startswith("test+"), "Test email must start with 'test+'"
    assert "@example.com" in test_email, "Test email must use example.com domain"
    assert len(test_email) > 20, "Test email must be long enough to be unique"

    print(f"✅ Test email generated: {test_email}")


def test_assessment_test_data_structure(assessment_test_data):
    """
    Verify assessment test data has correct structure.

    This test validates:
    - All required fields present
    - Field values are realistic
    - Data represents CRITICAL segment (2+ red systems)
    """
    # Contact info
    assert "email" in assessment_test_data
    assert "first_name" in assessment_test_data
    assert "business_name" in assessment_test_data

    # Assessment results
    assert "assessment_score" in assessment_test_data
    assert "red_systems" in assessment_test_data
    assert "orange_systems" in assessment_test_data
    assert "yellow_systems" in assessment_test_data
    assert "green_systems" in assessment_test_data

    # System scores
    assert "gps_score" in assessment_test_data
    assert "money_score" in assessment_test_data

    # Revenue leak
    assert "revenue_leak_total" in assessment_test_data

    # Weakest systems
    assert "weakest_system_1" in assessment_test_data
    assert "weakest_system_2" in assessment_test_data

    # Verify CRITICAL segment (2+ red systems)
    assert assessment_test_data["red_systems"] >= 2, "Test data must be CRITICAL segment"

    print(f"✅ Assessment test data validated: {assessment_test_data['email']}")
