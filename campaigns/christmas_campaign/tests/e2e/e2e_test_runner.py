#!/usr/bin/env python3
"""
E2E Test Runner for Christmas Traditional Service Campaign

This script orchestrates end-to-end testing across all sequences:
1. Lead Nurture Funnel (browser automation + webhook)
2. No-Show Recovery (webhook integration)
3. Post-Call Maybe (webhook integration)
4. Onboarding (webhook integration)
5. Full Integration (multi-sequence scenario)

Usage:
    # Run all E2E tests
    python campaigns/christmas_campaign/tests/e2e/e2e_test_runner.py

    # Run specific test suite
    python campaigns/christmas_campaign/tests/e2e/e2e_test_runner.py --suite noshow

    # Run with verbose output
    python campaigns/christmas_campaign/tests/e2e/e2e_test_runner.py -v

    # Generate summary report only
    python campaigns/christmas_campaign/tests/e2e/e2e_test_runner.py --summary

Prerequisites:
    - FastAPI server running: uvicorn server:app --reload --port 8000
    - Prefect server running: prefect server start
    - (Optional) Website running: npm run dev (localhost:3005)
    - TESTING_MODE=true in environment
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import httpx

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Paths
E2E_DIR = Path(__file__).parent
FIXTURES_DIR = E2E_DIR / "fixtures"
RESULTS_DIR = E2E_DIR / "results"
SCREENSHOTS_DIR = E2E_DIR / "screenshots"


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(text: str):
    """Print formatted header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.END}\n")


def print_subheader(text: str):
    """Print formatted subheader."""
    print(f"\n{Colors.CYAN}{'-' * 50}{Colors.END}")
    print(f"{Colors.CYAN}{text}{Colors.END}")
    print(f"{Colors.CYAN}{'-' * 50}{Colors.END}")


def print_success(text: str):
    """Print success message."""
    print(f"{Colors.GREEN}[PASS]{Colors.END} {text}")


def print_error(text: str):
    """Print error message."""
    print(f"{Colors.RED}[FAIL]{Colors.END} {text}")


def print_warning(text: str):
    """Print warning message."""
    print(f"{Colors.YELLOW}[WARN]{Colors.END} {text}")


def print_info(text: str):
    """Print info message."""
    print(f"{Colors.BLUE}[INFO]{Colors.END} {text}")


class E2ETestRunner:
    """E2E Test Runner for Christmas Campaign."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.fastapi_url = os.getenv("E2E_FASTAPI_URL", "http://localhost:8000")
        self.prefect_url = os.getenv("E2E_PREFECT_URL", "http://localhost:4200")
        self.website_url = os.getenv("E2E_WEBSITE_URL", "http://localhost:3005")
        self.results: List[Dict[str, Any]] = []
        self.client = httpx.Client(timeout=30.0)

    def load_fixture(self, name: str) -> Dict[str, Any]:
        """Load JSON fixture."""
        path = FIXTURES_DIR / f"{name}.json"
        with open(path, "r") as f:
            return json.load(f)

    def generate_unique_email(self, prefix: str = "e2e-test") -> str:
        """Generate unique email for testing."""
        timestamp = int(time.time() * 1000)
        return f"{prefix}-{timestamp}@e2e-test.example.com"

    # =========================================================================
    # Prerequisite Checks
    # =========================================================================

    def check_prerequisites(self) -> bool:
        """Check all prerequisites are running."""
        print_subheader("Checking Prerequisites")

        all_ok = True

        # Check FastAPI
        try:
            response = self.client.get(f"{self.fastapi_url}/health")
            if response.status_code == 200:
                print_success(f"FastAPI server running at {self.fastapi_url}")
            else:
                print_error(f"FastAPI health check failed: {response.status_code}")
                all_ok = False
        except Exception as e:
            print_error(f"FastAPI not accessible: {e}")
            all_ok = False

        # Check Prefect
        try:
            response = self.client.get(f"{self.prefect_url}/api/health")
            if response.status_code == 200:
                print_success(f"Prefect server running at {self.prefect_url}")
            else:
                print_error(f"Prefect health check failed: {response.status_code}")
                all_ok = False
        except Exception as e:
            print_warning(f"Prefect not accessible (optional): {e}")

        # Check Website (optional)
        try:
            response = self.client.get(self.website_url, follow_redirects=True)
            if response.status_code == 200:
                print_success(f"Website running at {self.website_url}")
            else:
                print_warning(f"Website not accessible (optional for API tests)")
        except Exception as e:
            print_warning(f"Website not accessible (optional): {e}")

        return all_ok

    # =========================================================================
    # Webhook Tests
    # =========================================================================

    def test_noshow_webhook(self) -> Dict[str, Any]:
        """Test no-show recovery webhook endpoint."""
        print_subheader("Test: No-Show Recovery Webhook")

        result = {
            "test_name": "noshow_webhook",
            "status": "pending",
            "tests": []
        }

        fixtures = self.load_fixture("calendly_noshow_payload")

        # Test 1: Valid payload
        print_info("Testing valid payload...")
        payload = fixtures["valid_payload"].copy()
        payload["email"] = self.generate_unique_email("e2e-noshow")

        try:
            response = self.client.post(
                f"{self.fastapi_url}/webhook/calendly-noshow",
                json=payload
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "accepted":
                    print_success(f"Valid payload accepted: {payload['email']}")
                    result["tests"].append({"name": "valid_payload", "status": "passed"})
                else:
                    print_error(f"Unexpected response: {data}")
                    result["tests"].append({"name": "valid_payload", "status": "failed", "error": str(data)})
            else:
                print_error(f"HTTP {response.status_code}: {response.text}")
                result["tests"].append({"name": "valid_payload", "status": "failed", "error": response.text})
        except Exception as e:
            print_error(f"Exception: {e}")
            result["tests"].append({"name": "valid_payload", "status": "error", "error": str(e)})

        # Test 2: Missing email
        print_info("Testing missing email (should fail)...")
        invalid_payload = fixtures["invalid_payload_missing_email"]
        try:
            response = self.client.post(
                f"{self.fastapi_url}/webhook/calendly-noshow",
                json=invalid_payload
            )
            if response.status_code == 422:
                print_success("Missing email correctly rejected (422)")
                result["tests"].append({"name": "missing_email_rejected", "status": "passed"})
            else:
                print_error(f"Expected 422, got {response.status_code}")
                result["tests"].append({"name": "missing_email_rejected", "status": "failed"})
        except Exception as e:
            print_error(f"Exception: {e}")
            result["tests"].append({"name": "missing_email_rejected", "status": "error", "error": str(e)})

        # Test 3: Malformed email
        print_info("Testing malformed email (should fail)...")
        invalid_payload = fixtures["invalid_payload_malformed_email"]
        try:
            response = self.client.post(
                f"{self.fastapi_url}/webhook/calendly-noshow",
                json=invalid_payload
            )
            if response.status_code == 422:
                print_success("Malformed email correctly rejected (422)")
                result["tests"].append({"name": "malformed_email_rejected", "status": "passed"})
            else:
                print_error(f"Expected 422, got {response.status_code}")
                result["tests"].append({"name": "malformed_email_rejected", "status": "failed"})
        except Exception as e:
            print_error(f"Exception: {e}")
            result["tests"].append({"name": "malformed_email_rejected", "status": "error", "error": str(e)})

        # Calculate overall status
        passed = sum(1 for t in result["tests"] if t["status"] == "passed")
        total = len(result["tests"])
        result["status"] = "passed" if passed == total else "failed"
        result["summary"] = f"{passed}/{total} tests passed"

        return result

    def test_postcall_webhook(self) -> Dict[str, Any]:
        """Test post-call maybe webhook endpoint."""
        print_subheader("Test: Post-Call Maybe Webhook")

        result = {
            "test_name": "postcall_webhook",
            "status": "pending",
            "tests": []
        }

        fixtures = self.load_fixture("crm_postcall_payload")

        # Test 1: Valid payload
        print_info("Testing valid payload...")
        payload = fixtures["valid_payload"].copy()
        payload["email"] = self.generate_unique_email("e2e-postcall")

        try:
            response = self.client.post(
                f"{self.fastapi_url}/webhook/postcall-maybe",
                json=payload
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "accepted":
                    print_success(f"Valid payload accepted: {payload['email']}")
                    result["tests"].append({"name": "valid_payload", "status": "passed"})
                else:
                    print_error(f"Unexpected response: {data}")
                    result["tests"].append({"name": "valid_payload", "status": "failed", "error": str(data)})
            else:
                print_error(f"HTTP {response.status_code}: {response.text}")
                result["tests"].append({"name": "valid_payload", "status": "failed", "error": response.text})
        except Exception as e:
            print_error(f"Exception: {e}")
            result["tests"].append({"name": "valid_payload", "status": "error", "error": str(e)})

        # Test 2: Minimal payload
        print_info("Testing minimal payload...")
        minimal_payload = fixtures["valid_payload_minimal"].copy()
        minimal_payload["email"] = self.generate_unique_email("e2e-postcall-min")

        try:
            response = self.client.post(
                f"{self.fastapi_url}/webhook/postcall-maybe",
                json=minimal_payload
            )
            if response.status_code == 200:
                print_success("Minimal payload accepted")
                result["tests"].append({"name": "minimal_payload", "status": "passed"})
            else:
                print_error(f"HTTP {response.status_code}")
                result["tests"].append({"name": "minimal_payload", "status": "failed"})
        except Exception as e:
            print_error(f"Exception: {e}")
            result["tests"].append({"name": "minimal_payload", "status": "error", "error": str(e)})

        # Test 3: Missing email
        print_info("Testing missing email (should fail)...")
        try:
            response = self.client.post(
                f"{self.fastapi_url}/webhook/postcall-maybe",
                json=fixtures["invalid_payload_missing_email"]
            )
            if response.status_code == 422:
                print_success("Missing email correctly rejected (422)")
                result["tests"].append({"name": "missing_email_rejected", "status": "passed"})
            else:
                print_error(f"Expected 422, got {response.status_code}")
                result["tests"].append({"name": "missing_email_rejected", "status": "failed"})
        except Exception as e:
            result["tests"].append({"name": "missing_email_rejected", "status": "error", "error": str(e)})

        # Calculate overall status
        passed = sum(1 for t in result["tests"] if t["status"] == "passed")
        total = len(result["tests"])
        result["status"] = "passed" if passed == total else "failed"
        result["summary"] = f"{passed}/{total} tests passed"

        return result

    def test_onboarding_webhook(self) -> Dict[str, Any]:
        """Test onboarding start webhook endpoint."""
        print_subheader("Test: Onboarding Start Webhook")

        result = {
            "test_name": "onboarding_webhook",
            "status": "pending",
            "tests": []
        }

        fixtures = self.load_fixture("docusign_completion_payload")

        # Test 1: Valid payload
        print_info("Testing valid payload with full details...")
        payload = fixtures["valid_payload"].copy()
        payload["email"] = self.generate_unique_email("e2e-onboarding")

        try:
            response = self.client.post(
                f"{self.fastapi_url}/webhook/onboarding-start",
                json=payload
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "accepted":
                    print_success(f"Valid payload accepted: {payload['email']}")
                    result["tests"].append({"name": "valid_payload", "status": "passed"})
                else:
                    print_error(f"Unexpected response: {data}")
                    result["tests"].append({"name": "valid_payload", "status": "failed", "error": str(data)})
            else:
                print_error(f"HTTP {response.status_code}: {response.text}")
                result["tests"].append({"name": "valid_payload", "status": "failed", "error": response.text})
        except Exception as e:
            print_error(f"Exception: {e}")
            result["tests"].append({"name": "valid_payload", "status": "error", "error": str(e)})

        # Test 2: Minimal payload
        print_info("Testing minimal payload...")
        minimal_payload = fixtures["valid_payload_minimal"].copy()
        minimal_payload["email"] = self.generate_unique_email("e2e-onboarding-min")

        try:
            response = self.client.post(
                f"{self.fastapi_url}/webhook/onboarding-start",
                json=minimal_payload
            )
            if response.status_code == 200:
                print_success("Minimal payload accepted")
                result["tests"].append({"name": "minimal_payload", "status": "passed"})
            else:
                print_error(f"HTTP {response.status_code}")
                result["tests"].append({"name": "minimal_payload", "status": "failed"})
        except Exception as e:
            result["tests"].append({"name": "minimal_payload", "status": "error", "error": str(e)})

        # Test 3: Missing email
        print_info("Testing missing email (should fail)...")
        try:
            response = self.client.post(
                f"{self.fastapi_url}/webhook/onboarding-start",
                json=fixtures["invalid_payload_missing_email"]
            )
            if response.status_code == 422:
                print_success("Missing email correctly rejected (422)")
                result["tests"].append({"name": "missing_email_rejected", "status": "passed"})
            else:
                print_error(f"Expected 422, got {response.status_code}")
                result["tests"].append({"name": "missing_email_rejected", "status": "failed"})
        except Exception as e:
            result["tests"].append({"name": "missing_email_rejected", "status": "error", "error": str(e)})

        # Calculate overall status
        passed = sum(1 for t in result["tests"] if t["status"] == "passed")
        total = len(result["tests"])
        result["status"] = "passed" if passed == total else "failed"
        result["summary"] = f"{passed}/{total} tests passed"

        return result

    def test_christmas_signup_webhook(self) -> Dict[str, Any]:
        """Test Christmas signup webhook endpoint (lead nurture)."""
        print_subheader("Test: Christmas Signup Webhook (Lead Nurture)")

        result = {
            "test_name": "christmas_signup_webhook",
            "status": "pending",
            "tests": []
        }

        customer_data = self.load_fixture("test_customer_data")

        # Test each segment
        for segment in ["critical", "urgent", "optimize"]:
            segment_data = customer_data[f"lead_nurture_{segment}"].copy()
            segment_data["email"] = self.generate_unique_email(f"e2e-{segment}")

            print_info(f"Testing {segment.upper()} segment payload...")

            try:
                response = self.client.post(
                    f"{self.fastapi_url}/webhook/christmas-signup",
                    json=segment_data
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "accepted":
                        print_success(f"{segment.upper()} segment accepted: {segment_data['email']}")
                        result["tests"].append({
                            "name": f"{segment}_segment",
                            "status": "passed",
                            "email": segment_data["email"]
                        })
                    else:
                        print_error(f"Unexpected response: {data}")
                        result["tests"].append({"name": f"{segment}_segment", "status": "failed"})
                else:
                    print_error(f"HTTP {response.status_code}")
                    result["tests"].append({"name": f"{segment}_segment", "status": "failed"})
            except Exception as e:
                print_error(f"Exception: {e}")
                result["tests"].append({"name": f"{segment}_segment", "status": "error", "error": str(e)})

        # Calculate overall status
        passed = sum(1 for t in result["tests"] if t["status"] == "passed")
        total = len(result["tests"])
        result["status"] = "passed" if passed == total else "failed"
        result["summary"] = f"{passed}/{total} tests passed"

        return result

    # =========================================================================
    # Test Suites
    # =========================================================================

    def run_noshow_suite(self) -> List[Dict[str, Any]]:
        """Run no-show recovery test suite."""
        print_header("No-Show Recovery Test Suite")
        return [self.test_noshow_webhook()]

    def run_postcall_suite(self) -> List[Dict[str, Any]]:
        """Run post-call maybe test suite."""
        print_header("Post-Call Maybe Test Suite")
        return [self.test_postcall_webhook()]

    def run_onboarding_suite(self) -> List[Dict[str, Any]]:
        """Run onboarding test suite."""
        print_header("Onboarding Test Suite")
        return [self.test_onboarding_webhook()]

    def run_lead_nurture_suite(self) -> List[Dict[str, Any]]:
        """Run lead nurture test suite."""
        print_header("Lead Nurture Test Suite")
        return [self.test_christmas_signup_webhook()]

    def run_all_suites(self) -> List[Dict[str, Any]]:
        """Run all test suites."""
        results = []
        results.extend(self.run_lead_nurture_suite())
        results.extend(self.run_noshow_suite())
        results.extend(self.run_postcall_suite())
        results.extend(self.run_onboarding_suite())
        return results

    # =========================================================================
    # Reporting
    # =========================================================================

    def generate_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate test summary."""
        total_tests = 0
        passed_tests = 0
        failed_tests = 0

        for suite in results:
            for test in suite.get("tests", []):
                total_tests += 1
                if test["status"] == "passed":
                    passed_tests += 1
                else:
                    failed_tests += 1

        return {
            "timestamp": datetime.now().isoformat(),
            "total_suites": len(results),
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "pass_rate": f"{(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "N/A",
            "results": results
        }

    def save_results(self, summary: Dict[str, Any]):
        """Save test results to file."""
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = RESULTS_DIR / f"e2e_results_{timestamp}.json"
        with open(path, "w") as f:
            json.dump(summary, f, indent=2)
        print_info(f"Results saved to: {path}")
        return path

    def print_summary(self, summary: Dict[str, Any]):
        """Print test summary to console."""
        print_header("Test Summary")

        print(f"Timestamp: {summary['timestamp']}")
        print(f"Total Suites: {summary['total_suites']}")
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {Colors.GREEN}{summary['passed']}{Colors.END}")
        print(f"Failed: {Colors.RED}{summary['failed']}{Colors.END}")
        print(f"Pass Rate: {summary['pass_rate']}")

        print_subheader("Suite Results")
        for suite in summary["results"]:
            status_color = Colors.GREEN if suite["status"] == "passed" else Colors.RED
            print(f"  {status_color}[{suite['status'].upper()}]{Colors.END} {suite['test_name']}: {suite.get('summary', 'N/A')}")

    def close(self):
        """Close HTTP client."""
        self.client.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="E2E Test Runner for Christmas Campaign")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--suite", choices=["all", "noshow", "postcall", "onboarding", "lead_nurture"],
                        default="all", help="Test suite to run")
    parser.add_argument("--summary", action="store_true", help="Only generate summary from existing results")
    args = parser.parse_args()

    runner = E2ETestRunner(verbose=args.verbose)

    try:
        print_header("Christmas Traditional Service E2E Tests")

        # Check prerequisites
        if not runner.check_prerequisites():
            print_error("Prerequisites not met. Please start required servers.")
            sys.exit(1)

        # Run tests
        if args.suite == "all":
            results = runner.run_all_suites()
        elif args.suite == "noshow":
            results = runner.run_noshow_suite()
        elif args.suite == "postcall":
            results = runner.run_postcall_suite()
        elif args.suite == "onboarding":
            results = runner.run_onboarding_suite()
        elif args.suite == "lead_nurture":
            results = runner.run_lead_nurture_suite()

        # Generate and save summary
        summary = runner.generate_summary(results)
        runner.save_results(summary)
        runner.print_summary(summary)

        # Exit with appropriate code
        if summary["failed"] > 0:
            sys.exit(1)
        else:
            print(f"\n{Colors.GREEN}{Colors.BOLD}All tests passed!{Colors.END}")
            sys.exit(0)

    finally:
        runner.close()


if __name__ == "__main__":
    main()
