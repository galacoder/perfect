"""
Simple test for single email send without Prefect Server.

This tests the atomic send_email_flow directly to verify:
1. Template fetching from Notion
2. Variable substitution
3. Email sending via Resend
4. Notion tracking

Usage:
    PYTHONPATH=. PREFECT_API_DATABASE_CONNECTION_URL="sqlite+aiosqlite:///./test_prefect.db" python campaigns/christmas_campaign/test_simple_email.py
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

from campaigns.christmas_campaign.flows.send_email_flow import send_email_flow

def print_banner(text: str):
    """Print a formatted banner."""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")

async def test_single_email():
    """Test sending a single email (Email 1)."""

    print_banner("Christmas Campaign - Single Email Test (Email 1)")

    # Test data
    print("📧 Test Email: Email 1 (Assessment Results)")
    print("📬 Recipient: test@example.com")
    print("🎯 Segment: CRITICAL\n")

    try:
        result = await send_email_flow(
            email="test@example.com",
            email_number=1,
            first_name="John",
            business_name="Test Salon",
            segment="CRITICAL",
            assessment_score=45
        )

        print_banner("✅ Email Send Complete")
        print(f"Result: {result}")

        print("\n✓ Next Steps:")
        print("  1. Check Resend dashboard: https://resend.com/emails")
        print("  2. Check test@example.com inbox")
        print("  3. Verify variables were substituted correctly")
        print("  4. Check Notion Email Analytics database")

    except Exception as e:
        print_banner("❌ Error During Email Send")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_single_email())
