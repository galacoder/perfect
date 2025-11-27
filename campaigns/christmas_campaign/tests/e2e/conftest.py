"""
E2E Test Fixtures for pytest

Re-exports fixtures from conftest_e2e.py for pytest auto-discovery.
"""

# Import all fixtures from conftest_e2e for pytest to discover
from .conftest_e2e import (
    E2EConfig,
    e2e_config,
    http_client,
    async_http_client,
    load_fixture,
    calendly_noshow_fixtures,
    postcall_fixtures,
    onboarding_fixtures,
    customer_data,
    unique_email,
    make_unique_payload,
    TestResultCapture,
    result_capture,
    ensure_fastapi_running,
    ensure_prefect_running,
    post_webhook,
    take_screenshot,
    e2e_session_setup,
)
