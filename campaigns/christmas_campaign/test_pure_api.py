"""
Pure API test - No Prefect, just direct Notion and Resend API calls.

This verifies the core functionality works:
1. Notion template fetching
2. Variable substitution
3. Email sending via Resend

Usage:
    python campaigns/christmas_campaign/test_pure_api.py
"""

import os
from notion_client import Client
import resend
from dotenv import load_dotenv

# Load environment
load_dotenv()

def print_banner(text: str):
    """Print a formatted banner."""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")

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

def test_complete_flow():
    """Test the complete email sending flow."""

    print_banner("Christmas Campaign - Pure API Test")

    # Configuration
    template_id = "christmas_email_1"
    to_email = "test@example.com"
    first_name = "John"

    print(f"📧 Testing Email: {template_id}")
    print(f"📬 Recipient: {to_email}")
    print(f"👤 Name: {first_name}\n")

    # Step 1: Fetch template
    print_banner("Step 1: Fetch Template from Notion")

    try:
        template = fetch_template_from_notion(template_id)
        print(f"✓ Template fetched successfully")
        print(f"  Subject: {template['subject'][:60]}...")
        print(f"  Body length: {len(template['html_body'])} characters")
    except Exception as e:
        print(f"❌ Error: {e}")
        return

    # Step 2: Prepare variables
    print_banner("Step 2: Prepare Variables")

    variables = {
        "first_name": first_name,
        "email": to_email,
        "GPSScore": "45",
        "GenerateScore": "40",  # GPS subscore - Generate
        "PersuadeScore": "45",  # GPS subscore - Persuade
        "ServeScore": "50",     # GPS subscore - Serve
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
        "QuickWinExplanation": "Reduce no-shows from 30% to 15%",
        "QuickWinImpact": "$4,200/month revenue recovery"
    }

    print(f"✓ Variables prepared: {len(variables)} total")

    # Step 3: Substitute variables
    print_banner("Step 3: Substitute Variables")

    subject = substitute_variables(template["subject"], variables)
    html_body = substitute_variables(template["html_body"], variables)

    print(f"✓ Subject: {subject[:60]}...")
    print(f"✓ Body length after substitution: {len(html_body)} characters")

    # Check for remaining placeholders
    import re
    remaining = re.findall(r'\{\{[^}]+\}\}', subject + html_body)
    if remaining:
        print(f"\n⚠️  Warning: {len(remaining)} placeholders not substituted:")
        for placeholder in list(set(remaining))[:5]:
            print(f"  - {placeholder}")
    else:
        print(f"✓ All placeholders substituted successfully!")

    # Step 4: Send email
    print_banner("Step 4: Send Email via Resend")

    try:
        result = send_email_via_resend(to_email, subject, html_body)
        print_banner("✅ Email Sent Successfully!")
        print(f"Resend Email ID: {result['id']}")

        print("\n📬 Next Steps:")
        print("  1. Check Resend dashboard: https://resend.com/emails")
        print(f"  2. Check {to_email} inbox")
        print("  3. Verify personalization ({{first_name}} → John)")
        print("  4. Verify assessment data is correct")

    except Exception as e:
        print_banner("❌ Error Sending Email")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_complete_flow()
