"""
End-to-End Integration Test for BusOS Email Sequence.

This script tests the complete workflow:
1. Signup webhook → Create Notion contact
2. Assessment webhook → Update Notion → Trigger email sequence
3. Email sequence → 5 emails sent with proper timing

Usage:
    # Test with mocked APIs (recommended for CI/CD)
    python test_integration_e2e.py --mock

    # Test with real APIs (requires valid credentials in .env)
    python test_integration_e2e.py --real

    # Test specific flow only
    python test_integration_e2e.py --flow signup
    python test_integration_e2e.py --flow assessment
    python test_integration_e2e.py --flow email_sequence
"""

import sys
import os
import time
import argparse
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("🧪 End-to-End Integration Test\n")
print("="*60)


def test_signup_flow(use_mock=True):
    """Test signup handler flow."""
    print("\n1️⃣ Testing Signup Flow")
    print("-" * 60)

    try:
        from campaigns.businessx_canada_lead_nurture.flows.signup_handler import signup_handler_flow

        if use_mock:
            print("   Using mocked Notion API...")
            # Mock Notion client
            from unittest.mock import Mock, patch

            with patch('campaigns.businessx_canada_lead_nurture.tasks.notion_operations.notion') as mock_notion:
                # Mock search returns no existing contact
                mock_notion.databases.query.return_value = {"results": []}

                # Mock create returns page ID
                mock_notion.pages.create.return_value = {"id": "test-page-123"}

                # Run flow
                result = signup_handler_flow(
                    email="test@example.com",
                    name="Test User",
                    first_name="Test",
                    business_name="Test Business",
                    signup_source="integration_test"
                )

                assert result["status"] == "created"
                assert result["page_id"] == "test-page-123"
                print("   ✅ Signup flow passed (mocked)")

        else:
            print("   Using real Notion API...")
            # Test with real API (use test email)
            test_email = f"test+{int(time.time())}@example.com"

            result = signup_handler_flow(
                email=test_email,
                name="Integration Test User",
                first_name="Integration",
                business_name="Test Business",
                signup_source="integration_test"
            )

            assert "page_id" in result
            print(f"   ✅ Signup flow passed (real API)")
            print(f"      Created contact: {result['page_id']}")

            return result["page_id"]

    except Exception as e:
        print(f"   ❌ Signup flow failed: {e}")
        return None


def test_assessment_flow(use_mock=True, page_id=None):
    """Test assessment handler flow."""
    print("\n2️⃣ Testing Assessment Flow")
    print("-" * 60)

    try:
        from campaigns.businessx_canada_lead_nurture.flows.assessment_handler import assessment_handler_flow

        if use_mock:
            print("   Using mocked Notion/Resend APIs...")
            from unittest.mock import Mock, patch

            # Mock Notion
            with patch('campaigns.businessx_canada_lead_nurture.tasks.notion_operations.notion') as mock_notion, \
                 patch('campaigns.businessx_canada_lead_nurture.tasks.resend_operations.httpx.Client') as mock_httpx, \
                 patch('campaigns.businessx_canada_lead_nurture.tasks.template_operations.notion') as mock_template_notion:

                # Mock search finds contact
                mock_notion.databases.query.return_value = {
                    "results": [{"id": "test-page-123"}]
                }

                # Mock get contact returns full data
                mock_notion.pages.retrieve.return_value = {
                    "id": "test-page-123",
                    "properties": {
                        "First Name": {"rich_text": [{"plain_text": "Test"}]},
                        "Business Name": {"rich_text": [{"plain_text": "Test Business"}]}
                    }
                }

                # Mock update contact
                mock_notion.pages.update.return_value = {"id": "test-page-123"}

                # Mock template fetch
                mock_template_notion.databases.query.return_value = {
                    "results": [{
                        "id": "template-1",
                        "properties": {
                            "Subject": {"rich_text": [{"plain_text": "Test Subject"}]},
                            "HTML Body": {"rich_text": [{"plain_text": "<p>Test Body</p>"}]}
                        }
                    }]
                }

                # Mock Resend email sending
                mock_response = Mock()
                mock_response.json.return_value = {"id": "email-123"}
                mock_response.raise_for_status = Mock()

                mock_client = Mock()
                mock_client.__enter__ = Mock(return_value=mock_client)
                mock_client.__exit__ = Mock(return_value=False)
                mock_client.post.return_value = mock_response
                mock_httpx.return_value = mock_client

                # Note: This will be slow because email_sequence_flow has sleep() calls
                print("   ⚠️  This will take ~10 seconds due to wait delays in testing mode...")

                result = assessment_handler_flow(
                    email="test@example.com",
                    red_systems=2,
                    orange_systems=1,
                    yellow_systems=2,
                    green_systems=3,
                    assessment_score=65
                )

                assert result["status"] == "success"
                assert result["segment"] == "CRITICAL"
                print("   ✅ Assessment flow passed (mocked)")

        else:
            print("   Using real Notion/Resend APIs...")

            if not page_id:
                print("   ❌ Need page_id from signup flow first")
                return None

            # Test with real APIs
            result = assessment_handler_flow(
                email="test@example.com",  # Use same email as signup
                red_systems=2,
                orange_systems=1,
                yellow_systems=2,
                green_systems=3,
                assessment_score=65
            )

            assert "segment" in result
            print(f"   ✅ Assessment flow passed (real API)")
            print(f"      Segment: {result['segment']}")

            return result

    except Exception as e:
        print(f"   ❌ Assessment flow failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_email_sequence_flow(use_mock=True):
    """Test email sequence flow."""
    print("\n3️⃣ Testing Email Sequence Flow")
    print("-" * 60)

    try:
        from campaigns.businessx_canada_lead_nurture.flows.email_sequence import email_sequence_flow

        if use_mock:
            print("   Using mocked Notion/Resend APIs...")
            from unittest.mock import Mock, patch

            with patch('campaigns.businessx_canada_lead_nurture.tasks.notion_operations.notion') as mock_notion, \
                 patch('campaigns.businessx_canada_lead_nurture.tasks.resend_operations.httpx.Client') as mock_httpx, \
                 patch('campaigns.businessx_canada_lead_nurture.tasks.template_operations.notion') as mock_template_notion:

                # Mock Notion updates
                mock_notion.pages.update.return_value = {"id": "test-page-123"}

                # Mock template fetch
                mock_template_notion.databases.query.return_value = {
                    "results": [{
                        "id": "template-1",
                        "properties": {
                            "Subject": {"rich_text": [{"plain_text": "Test Subject {{first_name}}"}]},
                            "HTML Body": {"rich_text": [{"plain_text": "<p>Hi {{first_name}} from {{business_name}}</p>"}]}
                        }
                    }]
                }

                # Mock Resend email sending
                mock_response = Mock()
                mock_response.json.return_value = {"id": f"email-{int(time.time())}"}
                mock_response.raise_for_status = Mock()

                mock_client = Mock()
                mock_client.__enter__ = Mock(return_value=mock_client)
                mock_client.__exit__ = Mock(return_value=False)
                mock_client.post.return_value = mock_response
                mock_httpx.return_value = mock_client

                print("   ⚠️  This will take ~10 seconds due to wait delays...")

                result = email_sequence_flow(
                    contact_page_id="test-page-123",
                    email="test@example.com",
                    first_name="Test",
                    business_name="Test Business",
                    red_systems=2,
                    orange_systems=1
                )

                assert result["status"] == "complete"
                assert result["segment"] == "CRITICAL"
                assert len(result["emails_sent"]) == 5
                print("   ✅ Email sequence flow passed (mocked)")
                print(f"      Emails sent: {len(result['emails_sent'])}")

        else:
            print("   ❌ Real API test not recommended for email sequence")
            print("      (Would send 5 real emails - use mock instead)")
            return None

    except Exception as e:
        print(f"   ❌ Email sequence flow failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_webhook_server():
    """Test FastAPI webhook server endpoints."""
    print("\n4️⃣ Testing Webhook Server")
    print("-" * 60)

    try:
        from fastapi.testclient import TestClient
        from server import app

        client = TestClient(app)

        # Test health check
        print("   Testing /health endpoint...")
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("   ✅ Health check passed")

        # Test signup webhook
        print("   Testing /webhook/signup endpoint...")
        response = client.post("/webhook/signup", json={
            "email": "test@example.com",
            "name": "Test User",
            "first_name": "Test",
            "business_name": "Test Business"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "accepted"
        print("   ✅ Signup webhook passed")

        # Test assessment webhook
        print("   Testing /webhook/assessment endpoint...")
        response = client.post("/webhook/assessment", json={
            "email": "test@example.com",
            "red_systems": 2,
            "orange_systems": 1,
            "yellow_systems": 2,
            "green_systems": 3,
            "assessment_score": 65
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "accepted"
        assert data["segment"] == "CRITICAL"
        print("   ✅ Assessment webhook passed")

        print("\n   ✅ All webhook endpoints working")

    except Exception as e:
        print(f"   ❌ Webhook server test failed: {e}")
        import traceback
        traceback.print_exc()


def run_all_tests(use_mock=True):
    """Run all integration tests."""
    print(f"\n🚀 Running Full Integration Test Suite")
    print(f"   Mode: {'MOCKED' if use_mock else 'REAL APIs'}")
    print("="*60)

    start_time = time.time()

    # Test 1: Signup Flow
    page_id = test_signup_flow(use_mock=use_mock)

    # Test 2: Assessment Flow
    test_assessment_flow(use_mock=use_mock, page_id=page_id)

    # Test 3: Email Sequence Flow (mocked only)
    if use_mock:
        test_email_sequence_flow(use_mock=True)

    # Test 4: Webhook Server
    test_webhook_server()

    elapsed = time.time() - start_time

    print("\n" + "="*60)
    print(f"✅ Integration Test Suite Complete")
    print(f"   Duration: {elapsed:.1f} seconds")
    print("="*60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="End-to-end integration tests")
    parser.add_argument(
        "--mode",
        choices=["mock", "real"],
        default="mock",
        help="Test mode: mock (fast, safe) or real (uses actual APIs)"
    )
    parser.add_argument(
        "--flow",
        choices=["signup", "assessment", "email", "webhook", "all"],
        default="all",
        help="Which flow to test"
    )

    args = parser.parse_args()

    use_mock = (args.mode == "mock")

    if args.flow == "signup":
        test_signup_flow(use_mock=use_mock)
    elif args.flow == "assessment":
        test_assessment_flow(use_mock=use_mock)
    elif args.flow == "email":
        test_email_sequence_flow(use_mock=True)  # Always mock for email
    elif args.flow == "webhook":
        test_webhook_server()
    else:
        run_all_tests(use_mock=use_mock)
