"""
Test all 7 Christmas campaign emails using pure API approach.

This verifies all email templates work end-to-end:
1. Notion template fetching (for each of 7 templates)
2. Variable substitution (100% coverage)
3. Email sending via Resend (optional - can be disabled)

Usage:
    # Test all 7 emails (send to Resend)
    python campaigns/christmas_campaign/test_all_emails.py

    # Test all 7 emails (dry-run, no sending)
    python campaigns/christmas_campaign/test_all_emails.py --dry-run
"""

import os
import sys
from notion_client import Client
import resend
from dotenv import load_dotenv
import re

# Load environment
load_dotenv()

def print_banner(text: str, style: str = "="):
    """Print a formatted banner."""
    width = 80
    print("\n" + style * width)
    print(f"  {text}")
    print(style * width + "\n")

def fetch_template_from_notion(template_id: str):
    """Fetch email template from Notion."""
    notion = Client(auth=os.getenv("NOTION_TOKEN"))
    db_id = os.getenv("NOTION_EMAIL_TEMPLATES_DB_ID")

    # Query for template
    response = notion.databases.query(
        database_id=db_id,
        filter={
            "property": "Template Name",
            "title": {"equals": template_id}
        }
    )

    if not response["results"]:
        raise ValueError(f"Template not found: {template_id}")

    page = response["results"][0]

    # Extract subject and body
    subject = page["properties"]["Subject Line"]["rich_text"][0]["plain_text"]
    html_body = page["properties"]["Email Body HTML"]["rich_text"][0]["plain_text"]

    return {"subject": subject, "html_body": html_body}

def substitute_variables(text: str, variables: dict) -> str:
    """Substitute {{variable}} placeholders."""
    for key, value in variables.items():
        placeholder = "{{" + key + "}}"
        text = text.replace(placeholder, str(value))
    return text

def send_email_via_resend(to_email: str, subject: str, html_body: str):
    """Send email via Resend API."""
    resend.api_key = os.getenv("RESEND_API_KEY")
    from_email = os.getenv("RESEND_FROM_EMAIL", "hello@sanglescalinglabs.com")

    params = {
        "from": from_email,
        "to": [to_email],
        "subject": subject,
        "html": html_body
    }

    email = resend.Emails.send(params)
    return email

def get_test_variables():
    """Get comprehensive test variables for all emails."""
    return {
        # Basic contact info
        "first_name": "John",
        "email": "test@example.com",
        "business_name": "Test Salon",

        # Assessment scores
        "GPSScore": "45",
        "GenerateScore": "40",  # GPS subscore - Generate
        "PersuadeScore": "45",  # GPS subscore - Persuade
        "ServeScore": "50",     # GPS subscore - Serve
        "MoneyScore": "38",
        "PeopleScore": "65",

        # Weakest systems
        "WeakestSystem1": "GPS",
        "WeakestSystem2": "Money",
        "Score1": "45",
        "Score2": "38",

        # Revenue leak calculations
        "RevenueLeakSystem1": "$8,500",
        "RevenueLeakSystem2": "$6,200",
        "TotalRevenueLeak": "$14,700",
        "TotalRevenueLeak_K": "14",
        "AnnualRevenueLeak": "$176,400",

        # Quick wins (Email 1)
        "QuickWinAction": "Add SMS confirmation for all appointments",
        "QuickWinExplanation": "Reduce no-shows from 30% to 15%",
        "QuickWinImpact": "$4,200/month revenue recovery",

        # Email 2 variables
        "WeakestSystemDescription": "the system that brings customers through your door, converts them to bookings, and delivers exceptional service",
        "QuickWin1_Title": "Implement automated SMS confirmations",
        "QuickWin1_Time": "2 hours setup",
        "QuickWin1_Cost": "$29/month (Twilio)",
        "QuickWin1_Impact": "$2,500/month (50% no-show reduction)",
        "QuickWin2_Title": "Add online booking calendar",
        "QuickWin2_Time": "3 hours setup",
        "QuickWin2_Cost": "$50/month (Calendly/Acuity)",
        "QuickWin2_Impact": "$1,200/month (capture after-hours bookings)",
        "QuickWin3_Title": "Create referral incentive program",
        "QuickWin3_Time": "1 hour planning",
        "QuickWin3_Cost": "$0 (discount-based)",
        "QuickWin3_Impact": "$800/month (20% more referrals)",

        # Email 7 variables
        "Christmas_Slots_Remaining": "7",
        "Christmas_Slots_Claimed": "23",
    }

def check_variable_coverage(text: str, template_id: str) -> tuple[bool, list]:
    """Check if all variables are substituted."""
    remaining = re.findall(r'\{\{[^}]+\}\}', text)
    success = len(remaining) == 0
    return success, remaining

def test_email(template_id: str, email_number: int, dry_run: bool = False):
    """Test a single email template."""

    print_banner(f"Email {email_number}: {template_id}", "=")

    # Step 1: Fetch template
    print("Step 1: Fetch Template from Notion")
    try:
        template = fetch_template_from_notion(template_id)
        print(f"✓ Template fetched successfully")
        print(f"  Subject: {template['subject'][:60]}...")
        print(f"  Body length: {len(template['html_body'])} characters\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")
        return False

    # Step 2: Substitute variables
    print("Step 2: Substitute Variables")
    variables = get_test_variables()

    subject = substitute_variables(template["subject"], variables)
    html_body = substitute_variables(template["html_body"], variables)

    print(f"✓ Subject: {subject[:60]}...")
    print(f"✓ Body length after substitution: {len(html_body)} characters")

    # Check for remaining placeholders
    success, remaining = check_variable_coverage(subject + html_body, template_id)

    if remaining:
        print(f"\n⚠️  Warning: {len(remaining)} placeholders not substituted:")
        for placeholder in list(set(remaining))[:10]:
            print(f"  - {placeholder}")
        print()
        return False
    else:
        print(f"✓ All placeholders substituted successfully!\n")

    # Step 3: Send email (if not dry-run)
    if not dry_run:
        print("Step 3: Send Email via Resend")
        try:
            result = send_email_via_resend("test@example.com", subject, html_body)
            print(f"✅ Email sent successfully!")
            print(f"   Resend Email ID: {result['id']}\n")
            return True
        except Exception as e:
            print(f"❌ Error sending email: {str(e)}\n")
            return False
    else:
        print("Step 3: Send Email via Resend")
        print("⏭️  Skipped (dry-run mode)\n")
        return True

def test_all_emails(dry_run: bool = False):
    """Test all 7 Christmas campaign emails."""

    print_banner("Christmas Campaign - All Emails Test", "#")

    mode = "DRY-RUN (no emails sent)" if dry_run else "LIVE (emails will be sent)"
    print(f"Mode: {mode}")
    print(f"Test recipient: test@example.com")
    print(f"From email: {os.getenv('RESEND_FROM_EMAIL', 'hello@sanglescalinglabs.com')}\n")

    # Define all 7 emails
    emails = [
        ("christmas_email_1", 1),
        ("christmas_email_2", 2),
        ("christmas_email_3", 3),
        ("christmas_email_4", 4),
        ("christmas_email_5", 5),
        ("christmas_email_6", 6),
        ("christmas_email_7", 7),
    ]

    results = []

    for template_id, email_number in emails:
        success = test_email(template_id, email_number, dry_run)
        results.append({
            "email_number": email_number,
            "template_id": template_id,
            "success": success
        })

        # Pause between emails to avoid rate limits
        if not dry_run and success:
            import time
            time.sleep(1)

    # Summary
    print_banner("Test Summary", "#")

    successful = sum(1 for r in results if r["success"])
    failed = len(results) - successful

    print(f"Total emails tested: {len(results)}")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}\n")

    if failed > 0:
        print("Failed emails:")
        for r in results:
            if not r["success"]:
                print(f"  - Email {r['email_number']}: {r['template_id']}")
        print()

    # Success rate
    success_rate = (successful / len(results)) * 100
    print(f"Success rate: {success_rate:.1f}%\n")

    if success_rate == 100:
        print_banner("🎉 ALL EMAILS WORKING PERFECTLY!", "#")
        print("Next steps:")
        print("  1. Check Resend dashboard: https://resend.com/emails")
        print("  2. Verify emails in test@example.com inbox")
        print("  3. Ready for production deployment! 🚀\n")
    else:
        print_banner("⚠️  Some emails need attention", "#")
        print("Review the errors above and fix before deployment.\n")

    return success_rate == 100

if __name__ == "__main__":
    # Check for dry-run flag
    dry_run = "--dry-run" in sys.argv

    # Run tests
    all_passed = test_all_emails(dry_run)

    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)
