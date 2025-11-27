"""
E2E Test Configuration and Fixtures

Provides shared fixtures for end-to-end testing:
- HTTP client for webhook testing
- Browser automation helpers
- Test data loading
- Result capture utilities
"""

import pytest
import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import httpx

# Paths
E2E_DIR = Path(__file__).parent
FIXTURES_DIR = E2E_DIR / "fixtures"
SCREENSHOTS_DIR = E2E_DIR / "screenshots"
RESULTS_DIR = E2E_DIR / "results"


# ============================================================================
# Configuration
# ============================================================================

class E2EConfig:
    """E2E test configuration."""

    # Server URLs
    FASTAPI_URL: str = os.getenv("E2E_FASTAPI_URL", "http://localhost:8000")
    PREFECT_URL: str = os.getenv("E2E_PREFECT_URL", "http://localhost:4200")
    WEBSITE_URL: str = os.getenv("E2E_WEBSITE_URL", "http://localhost:3005")

    # Timeouts (seconds)
    WEBHOOK_TIMEOUT: int = int(os.getenv("E2E_WEBHOOK_TIMEOUT", "30"))
    FLOW_TIMEOUT: int = int(os.getenv("E2E_FLOW_TIMEOUT", "120"))
    BROWSER_TIMEOUT: int = int(os.getenv("E2E_BROWSER_TIMEOUT", "60"))

    # Testing mode
    TESTING_MODE: bool = os.getenv("TESTING_MODE", "true").lower() == "true"

    # Email timing in testing mode (minutes)
    EMAIL_WAIT_1: int = 1  # 1 minute
    EMAIL_WAIT_2: int = 2  # 2 minutes
    EMAIL_WAIT_3: int = 3  # 3 minutes


@pytest.fixture(scope="session")
def e2e_config() -> E2EConfig:
    """Get E2E configuration."""
    return E2EConfig()


# ============================================================================
# HTTP Client Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def http_client() -> httpx.Client:
    """Create HTTP client for webhook testing."""
    client = httpx.Client(
        timeout=30.0,
        follow_redirects=True
    )
    yield client
    client.close()


@pytest.fixture(scope="session")
async def async_http_client() -> httpx.AsyncClient:
    """Create async HTTP client for parallel testing."""
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        yield client


# ============================================================================
# Test Data Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def load_fixture():
    """Factory fixture for loading JSON fixtures."""
    def _load(fixture_name: str) -> Dict[str, Any]:
        fixture_path = FIXTURES_DIR / f"{fixture_name}.json"
        with open(fixture_path, "r") as f:
            return json.load(f)
    return _load


@pytest.fixture(scope="session")
def calendly_noshow_fixtures(load_fixture) -> Dict[str, Any]:
    """Load Calendly no-show test fixtures."""
    return load_fixture("calendly_noshow_payload")


@pytest.fixture(scope="session")
def postcall_fixtures(load_fixture) -> Dict[str, Any]:
    """Load post-call maybe test fixtures."""
    return load_fixture("crm_postcall_payload")


@pytest.fixture(scope="session")
def onboarding_fixtures(load_fixture) -> Dict[str, Any]:
    """Load onboarding test fixtures."""
    return load_fixture("docusign_completion_payload")


@pytest.fixture(scope="session")
def customer_data(load_fixture) -> Dict[str, Any]:
    """Load customer test data."""
    return load_fixture("test_customer_data")


# ============================================================================
# Unique Test Data Generator
# ============================================================================

@pytest.fixture
def unique_email():
    """Generate unique email for each test."""
    def _generate(prefix: str = "e2e-test") -> str:
        timestamp = int(time.time() * 1000)
        return f"{prefix}-{timestamp}@e2e-test.example.com"
    return _generate


@pytest.fixture
def make_unique_payload():
    """Create unique payload based on template."""
    def _make(template: Dict[str, Any], email_prefix: str = "e2e-test") -> Dict[str, Any]:
        payload = template.copy()
        timestamp = int(time.time() * 1000)
        payload["email"] = f"{email_prefix}-{timestamp}@e2e-test.example.com"
        return payload
    return _make


# ============================================================================
# Result Capture Utilities
# ============================================================================

class TestResultCapture:
    """Capture and store test results for reporting."""

    def __init__(self, test_name: str):
        self.test_name = test_name
        self.start_time = datetime.now()
        self.end_time: Optional[datetime] = None
        self.status: str = "pending"
        self.flow_run_ids: list = []
        self.webhook_responses: list = []
        self.screenshots: list = []
        self.errors: list = []
        self.notes: list = []

    def add_flow_run(self, flow_run_id: str, flow_name: str = None):
        """Record a flow run ID."""
        self.flow_run_ids.append({
            "id": flow_run_id,
            "name": flow_name,
            "timestamp": datetime.now().isoformat()
        })

    def add_webhook_response(self, endpoint: str, status_code: int, response: Dict):
        """Record webhook response."""
        self.webhook_responses.append({
            "endpoint": endpoint,
            "status_code": status_code,
            "response": response,
            "timestamp": datetime.now().isoformat()
        })

    def add_screenshot(self, path: str, description: str):
        """Record screenshot."""
        self.screenshots.append({
            "path": path,
            "description": description,
            "timestamp": datetime.now().isoformat()
        })

    def add_error(self, error: str, context: str = None):
        """Record error."""
        self.errors.append({
            "error": error,
            "context": context,
            "timestamp": datetime.now().isoformat()
        })

    def add_note(self, note: str):
        """Add note."""
        self.notes.append({
            "note": note,
            "timestamp": datetime.now().isoformat()
        })

    def complete(self, status: str = "passed"):
        """Mark test complete."""
        self.end_time = datetime.now()
        self.status = status

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "test_name": self.test_name,
            "status": self.status,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": (self.end_time - self.start_time).total_seconds() if self.end_time else None,
            "flow_run_ids": self.flow_run_ids,
            "webhook_responses": self.webhook_responses,
            "screenshots": self.screenshots,
            "errors": self.errors,
            "notes": self.notes
        }

    def save(self):
        """Save result to JSON file."""
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        result_path = RESULTS_DIR / f"{self.test_name}_{self.start_time.strftime('%Y%m%d_%H%M%S')}.json"
        with open(result_path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
        return result_path


@pytest.fixture
def result_capture(request):
    """Create result capture for test."""
    capture = TestResultCapture(request.node.name)
    yield capture
    capture.complete("passed" if not hasattr(request.node, "rep_call") or request.node.rep_call.passed else "failed")
    capture.save()


# ============================================================================
# Server Health Check Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def ensure_fastapi_running(http_client, e2e_config):
    """Ensure FastAPI server is running."""
    try:
        response = http_client.get(f"{e2e_config.FASTAPI_URL}/health")
        assert response.status_code == 200, f"FastAPI health check failed: {response.text}"
        return True
    except Exception as e:
        pytest.skip(f"FastAPI server not running at {e2e_config.FASTAPI_URL}: {e}")


@pytest.fixture(scope="session")
def ensure_prefect_running(http_client, e2e_config):
    """Ensure Prefect server is running."""
    try:
        response = http_client.get(f"{e2e_config.PREFECT_URL}/api/health")
        assert response.status_code == 200, f"Prefect health check failed: {response.text}"
        return True
    except Exception as e:
        pytest.skip(f"Prefect server not running at {e2e_config.PREFECT_URL}: {e}")


# ============================================================================
# Webhook Testing Helpers
# ============================================================================

@pytest.fixture
def post_webhook(http_client, e2e_config, result_capture):
    """Helper to POST to webhook endpoints."""
    def _post(endpoint: str, payload: Dict[str, Any]) -> httpx.Response:
        url = f"{e2e_config.FASTAPI_URL}{endpoint}"
        response = http_client.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        result_capture.add_webhook_response(
            endpoint=endpoint,
            status_code=response.status_code,
            response=response.json() if response.status_code < 500 else {"error": response.text}
        )
        return response
    return _post


# ============================================================================
# Screenshot Helpers (for Puppeteer integration)
# ============================================================================

@pytest.fixture
def take_screenshot():
    """Helper to save screenshots."""
    def _save(name: str, data: bytes) -> str:
        SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = SCREENSHOTS_DIR / f"{name}_{timestamp}.png"
        with open(path, "wb") as f:
            f.write(data)
        return str(path)
    return _save


# ============================================================================
# Cleanup Fixtures
# ============================================================================

@pytest.fixture(scope="session", autouse=True)
def e2e_session_setup():
    """Setup/teardown for E2E test session."""
    # Setup: Create directories
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    yield

    # Teardown: Generate session summary
    print("\n" + "=" * 60)
    print("E2E Test Session Complete")
    print("=" * 60)
    print(f"Results saved to: {RESULTS_DIR}")
    print(f"Screenshots saved to: {SCREENSHOTS_DIR}")
