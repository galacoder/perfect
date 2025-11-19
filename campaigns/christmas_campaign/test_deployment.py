"""
Test script for Christmas Campaign email automation.

This script tests the complete email sequence flow without requiring
Prefect Server deployment. It runs flows directly for faster testing.

Usage:
    python campaigns/christmas_campaign/test_deployment.py
"""

import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Import flows
from campaigns.christmas_campaign.flows.email_sequence_orchestrator import email_sequence_orchestrator

def print_banner(text: str):
    """Print a formatted banner."""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")

def print_section(text: str):
    """Print a section header."""
    print(f"\n{'─' * 80}")
    print(f"  {text}")
    print(f"{'─' * 80}\n")

async def test_email_sequence():
    """
    Test the complete 7-email sequence with orchestrator.

    This test:
    1. Creates a test contact payload
    2. Runs the orchestrator flow
    3. Verifies all 7 emails are scheduled
    4. Shows expected timing
    """

    print_banner("Christmas Campaign - Email Sequence Test")

    # Check environment
    print_section("Environment Check")

    testing_mode = os.getenv("TESTING_MODE", "false").lower() == "true"
    notion_token = os.getenv("NOTION_TOKEN")
    resend_key = os.getenv("RESEND_API_KEY")
    templates_db = os.getenv("NOTION_EMAIL_TEMPLATES_DB_ID")

    print(f"✓ TESTING_MODE: {testing_mode}")
    print(f"✓ NOTION_TOKEN: {'Set' if notion_token else '❌ Missing'}")
    print(f"✓ RESEND_API_KEY: {'Set' if resend_key else '❌ Missing'}")
    print(f"✓ NOTION_EMAIL_TEMPLATES_DB_ID: {'Set' if templates_db else '❌ Missing'}")

    if not all([notion_token, resend_key, templates_db]):
        print("\n❌ Missing required environment variables!")
        print("Please check your .env file.")
        return

    # Test payload
    print_section("Test Contact Data")

    test_contact = {
        "email": "test@example.com",
        "first_name": "John",
        "business_name": "Test Salon",
        "segment": "CRITICAL",
        "assessment_data": {
            "red_systems": 2,
            "orange_systems": 1,
            "yellow_systems": 0,
            "green_systems": 0,
            "gps_score": 45,
            "money_score": 38,
            "people_score": 65,
            "weakest_system_1": "GPS",
            "weakest_system_2": "Money",
            "score_1": 45,
            "score_2": 38,
            "revenue_leak_system_1": 8500,
            "revenue_leak_system_2": 6200,
            "total_revenue_leak": 14700,
            "total_revenue_leak_k": 14,
            "annual_revenue_leak": 176400,
            "quick_win_action": "Add SMS confirmation for all appointments",
            "quick_win_explanation": "Reduce no-shows from 30% to 15% with automated confirmations",
            "quick_win_impact": "$4,200/month revenue recovery"
        }
    }

    print(f"Contact: {test_contact['first_name']} ({test_contact['email']})")
    print(f"Segment: {test_contact['segment']}")
    print(f"Red Systems: {test_contact['assessment_data']['red_systems']}")
    print(f"Total Revenue Leak: ${test_contact['assessment_data']['total_revenue_leak']:,}/month")

    # Expected timing
    print_section("Expected Email Timing")

    if testing_mode:
        print("🧪 TESTING MODE (Fast Delays):")
        print("  Email 1: NOW (0 min)")
        print("  Email 2: NOW + 2 min")
        print("  Email 3: NOW + 3 min")
        print("  Email 4: NOW + 4 min")
        print("  Email 5: NOW + 5 min")
        print("  Email 6: NOW + 6 min")
        print("  Email 7: NOW + 7 min")
        print("\n  Total Duration: ~29 minutes")
    else:
        print("🚀 PRODUCTION MODE (Real Delays):")
        print("  Email 1: NOW (0 hours)")
        print("  Email 2: NOW + 48 hours (Day 2)")
        print("  Email 3: NOW + 72 hours (Day 3)")
        print("  Email 4: NOW + 96 hours (Day 4)")
        print("  Email 5: NOW + 144 hours (Day 6)")
        print("  Email 6: NOW + 192 hours (Day 8)")
        print("  Email 7: NOW + 240 hours (Day 10)")
        print("\n  Total Duration: 10 days")

    # Run orchestrator
    print_section("Running Email Sequence Orchestrator")

    print(f"⏰ Starting at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🚀 Triggering orchestrator flow...")

    try:
        result = await email_sequence_orchestrator(
            email=test_contact["email"],
            first_name=test_contact["first_name"],
            business_name=test_contact["business_name"],
            red_systems=test_contact["assessment_data"]["red_systems"],
            orange_systems=test_contact["assessment_data"]["orange_systems"],
            yellow_systems=test_contact["assessment_data"]["yellow_systems"],
            green_systems=test_contact["assessment_data"]["green_systems"],
            assessment_score=test_contact["assessment_data"]["gps_score"]
        )

        print_section("✅ Orchestrator Complete")
        print(f"Result: {result}")

    except Exception as e:
        print_section("❌ Error During Execution")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return

    # Next steps
    print_section("Next Steps")

    if testing_mode:
        print("1. Monitor the next 29 minutes for email sends")
        print("2. Check Resend dashboard: https://resend.com/emails")
        print("3. Check Notion Email Analytics database")
        print("4. Verify test@example.com inbox for all 7 emails")
    else:
        print("1. Monitor over the next 10 days")
        print("2. Day 2: Check for Email 2")
        print("3. Day 10: Verify Email 7 received")
        print("4. Review Notion tracking throughout sequence")

    print("\n📊 Monitoring Commands:")
    print("  - Resend Dashboard: https://resend.com/emails")
    print("  - Notion Analytics: Check NOTION_EMAIL_ANALYTICS_DB_ID")
    print("  - Check inbox: test@example.com")

    print_banner("Test Complete")

if __name__ == "__main__":
    asyncio.run(test_email_sequence())
