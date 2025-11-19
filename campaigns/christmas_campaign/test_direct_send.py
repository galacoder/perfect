"""
Direct test of email sending without Prefect flows.

This bypasses Prefect entirely and tests the core logic:
1. Fetch template from Notion
2. Substitute variables
3. Send email via Resend

Usage:
    PYTHONPATH=/Users/sangle/Dev/action/projects/perfect python campaigns/christmas_campaign/test_direct_send.py
"""

import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

from campaigns.christmas_campaign.tasks.notion_operations import fetch_email_template
from campaigns.christmas_campaign.tasks.routing import get_email_template_id
from campaigns.christmas_campaign.tasks.resend_operations import send_template_email

def print_banner(text: str):
    """Print a formatted banner."""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")

def test_direct_email_send():
    """Test sending email directly without Prefect."""

    print_banner("Christmas Campaign - Direct Email Send Test")

    # Test data
    email = "test@example.com"
    first_name = "John"
    business_name = "Test Salon"
    segment = "CRITICAL"
    email_number = 1
    assessment_score = 45

    print(f"📧 Email: {email}")
    print(f"👤 Name: {first_name}")
    print(f"🏢 Business: {business_name}")
    print(f"🎯 Segment: {segment}")
    print(f"📬 Email Number: {email_number}")
    print(f"📊 Assessment Score: {assessment_score}")

    # Step 1: Get template ID
    print_banner("Step 1: Get Template ID")

    template_id = get_email_template_id(email_number, segment)
    print(f"✓ Template ID: {template_id}")

    # Step 2: Fetch template from Notion
    print_banner("Step 2: Fetch Template from Notion")

    try:
        template = fetch_email_template(template_id)
        print(f"✓ Template fetched successfully")
        print(f"  - Subject: {template['subject'][:50]}...")
        print(f"  - Body Length: {len(template['html_body'])} characters")
    except Exception as e:
        print(f"❌ Error fetching template: {e}")
        return

    # Step 3: Prepare variables
    print_banner("Step 3: Prepare Variables")

    variables = {
        "first_name": first_name,
        "email": email,
        "business_name": business_name,
        "GPSScore": "45",
        "MoneyScore": "38",
        "PeopleScore": "65",
        "WeakestSystem1": "GPS",
        "WeakestSystem2": "Money",
        "Score1": "45",
        "Score2": "38",
        "RevenueLeakSystem1": "$8,500",
        "RevenueLeakSystem2": "$6,200",
        "TotalRevenueLeak": "$14,700",
        "TotalRevenueLeak_K": "14",
        "AnnualRevenueLeak": "$176,400",
        "QuickWinAction": "Add SMS confirmation for all appointments",
        "QuickWinExplanation": "Reduce no-shows from 30% to 15% with automated confirmations",
        "QuickWinImpact": "$4,200/month revenue recovery"
    }

    print(f"✓ Variables prepared: {len(variables)} total")
    for key in list(variables.keys())[:5]:
        print(f"  - {key}: {variables[key]}")
    print("  - ...")

    # Step 4: Send email
    print_banner("Step 4: Send Email via Resend")

    try:
        result = send_template_email(
            to_email=email,
            subject=template["subject"],
            html_body=template["html_body"],
            variables=variables
        )

        print_banner("✅ Email Sent Successfully!")
        print(f"Result: {result}")

        print("\n📬 Next Steps:")
        print("  1. Check Resend dashboard: https://resend.com/emails")
        print("  2. Check test@example.com inbox")
        print("  3. Verify variables were substituted correctly")
        print("  4. Look for no {{variable}} placeholders in email")

    except Exception as e:
        print_banner("❌ Error Sending Email")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_direct_email_send()
