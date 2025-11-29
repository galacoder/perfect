#!/usr/bin/env python3
"""
Send test emails for ALL sequence templates to verify formatting.

This script:
1. Fetches all active email templates from Notion
2. Renders each template with sample variables
3. Sends test email to specified recipient
4. Reports delivery status for each email

Usage:
    # Send all 5-Day sequence emails
    python campaigns/christmas_campaign/scripts/send_test_emails.py --sequence "5-Day"

    # Send all templates
    python campaigns/christmas_campaign/scripts/send_test_emails.py --all

    # Send specific template
    python campaigns/christmas_campaign/scripts/send_test_emails.py --template "5-Day E1"

Author: Christmas Campaign Team
Created: 2025-11-28
"""

import os
import sys
import re
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from typing import Dict, List

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv()

# Set Prefect API URL for Secret blocks
PREFECT_API_URL = os.getenv("PREFECT_API_URL", "https://prefect.galatek.dev/api")
os.environ["PREFECT_API_URL"] = PREFECT_API_URL

# Load credentials
try:
    from prefect.blocks.system import Secret
    NOTION_TOKEN = Secret.load("notion-token").get()
    NOTION_TEMPLATES_DB_ID = Secret.load("notion-email-templates-db-id").get()
    RESEND_API_KEY = Secret.load("resend-api-key").get()
    print(f"✅ Loaded credentials from Prefect Secret blocks (via {PREFECT_API_URL})")
except Exception as e:
    print(f"⚠️  Failed to load from Secret blocks, using environment variables: {e}")
    NOTION_TOKEN = os.getenv("NOTION_TOKEN")
    NOTION_TEMPLATES_DB_ID = os.getenv("NOTION_EMAIL_TEMPLATES_DB_ID")
    RESEND_API_KEY = os.getenv("RESEND_API_KEY")

if not all([NOTION_TOKEN, NOTION_TEMPLATES_DB_ID, RESEND_API_KEY]):
    print("❌ Missing required credentials")
    sys.exit(1)

from notion_client import Client
import resend

notion = Client(auth=NOTION_TOKEN)
resend.api_key = RESEND_API_KEY


def get_sample_variables() -> Dict[str, str]:
    """Get sample variables for template rendering."""
    from datetime import datetime

    deadline = datetime(2025, 12, 5)
    today = datetime.now()
    days_to_deadline = max(0, (deadline - today).days)

    return {
        # Core variables
        "first_name": "Sarah",
        "business_name": "Sarah's Beauty Salon",

        # Assessment data
        "overall_score": "45",
        "assessment_score": "45",
        "segment": "CRITICAL",
        "readiness_zone": "Crisis Zone",

        # Weakest/Strongest systems
        "weakest_system_1": "GPS (Navigation)",
        "weakest_system_2": "FUEL (Marketing)",
        "strongest_system": "CABIN (Customer Experience)",
        "WeakestSystem1": "GPS",
        "WeakestSystem2": "FUEL",
        "StrongestSystem": "CABIN",
        "weakest_system": "GPS",

        # Revenue leak
        "revenue_leak_total": "14700",
        "TotalRevenueLeak_K": "15",

        # Deadline info
        "days_to_deadline": str(days_to_deadline),
        "deadline_date": "December 5, 2025",

        # Personalized tips
        "personalized_tip_1": "Map your customer journey from first contact to payment in a Google Doc",
        "personalized_tip_2": "Write down 3 tasks you do every day that someone else could do with a checklist",
        "personalized_tip_3": "Block 2 hours this weekend to plan your December capacity.",

        # Links
        "calendly_link": "https://cal.com/sangletech/discovery-call",
        "pdf_download_link": "https://sangletech.com/en/flows/businessX/dfu/xmas-a01/assessment",

        # Spot tracking
        "spots_remaining": "12",
        "bookings_count": "18",
        "Christmas_Slots_Remaining": "7",

        # System counts
        "red_systems": "2",
        "orange_systems": "1",
        "yellow_systems": "3",
        "green_systems": "2",

        # Additional variables for other sequences
        "link": "https://sangletech.com/en/flows/businessX/dfu/xmas-a01",
        "call_time": "Tuesday at 2pm",
        "calendly_link_5min": "https://cal.com/sangletech/5min",
        "q1_foundation_deadline": "December 31, 2025",
        "broken_area_1": "GPS (Navigation)",
        "broken_area_2": "FUEL (Marketing)",
        "broken_area_3": "RADAR (Analytics)",
        "observation_dates": "December 10-12, 2025",
        "salon_address": "123 Main St, Toronto ON",
        "start_time": "9:00 AM",
    }


def substitute_variables(template: str, variables: Dict[str, str]) -> str:
    """Replace {{variable}} placeholders in template."""
    result = template
    for key, value in variables.items():
        pattern = r'\{\{' + re.escape(key) + r'\}\}'
        result = re.sub(pattern, str(value), result)
    return result


def fetch_templates(sequence_filter: str = None) -> List[Dict]:
    """
    Fetch templates from Notion database.

    Args:
        sequence_filter: Filter by sequence name (e.g., "5-Day", "7-Day", "lead_nurture")

    Returns:
        List of template dictionaries
    """
    print(f"\n📊 Fetching templates from database...")

    results = notion.databases.query(database_id=NOTION_TEMPLATES_DB_ID)
    templates = results.get("results", [])

    filtered_templates = []

    for template_page in templates:
        props = template_page["properties"]

        # Get template name
        template_name = "Unknown"
        for name_field in ["Name", "Template Name", "Title"]:
            name_prop = props.get(name_field, {})
            if "title" in name_prop and name_prop["title"]:
                template_name = name_prop["title"][0].get("plain_text", "Unknown")
                break
            elif "rich_text" in name_prop and name_prop["rich_text"]:
                template_name = name_prop["rich_text"][0].get("plain_text", "Unknown")
                break

        # Get status
        status_prop = props.get("Status", {})
        status = "Unknown"
        if "select" in status_prop and status_prop["select"]:
            status = status_prop["select"].get("name", "Unknown")

        # Skip archived templates
        if status == "Archived":
            continue

        # Apply sequence filter
        if sequence_filter and sequence_filter not in template_name:
            continue

        # Get subject
        subject = ""
        for subject_field in ["Subject", "Subject Line"]:
            subject_prop = props.get(subject_field, {})
            if "rich_text" in subject_prop and subject_prop["rich_text"]:
                subject = subject_prop["rich_text"][0].get("plain_text", "")
                break

        # Get body
        body = ""
        for body_field in ["Body", "Email Body", "Email Body Plain Text", "Content"]:
            body_prop = props.get(body_field, {})
            if "rich_text" in body_prop and body_prop["rich_text"]:
                body = body_prop["rich_text"][0].get("plain_text", "")
                break

        if subject and body:
            filtered_templates.append({
                "name": template_name,
                "subject": subject,
                "body": body
            })

    return filtered_templates


def send_test_email(template: Dict, to_email: str, variables: Dict[str, str]) -> str:
    """
    Send test email with template.

    Args:
        template: Template dictionary
        to_email: Recipient email
        variables: Variable substitution dictionary

    Returns:
        Resend email ID or None if failed
    """
    try:
        # Substitute variables
        final_subject = substitute_variables(template["subject"], variables)
        final_body = substitute_variables(template["body"], variables)

        # Convert plain text to HTML (basic formatting)
        html_body = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: #4CAF50;
                    color: white;
                    padding: 10px 20px;
                    text-align: center;
                    border-radius: 5px;
                    margin-bottom: 20px;
                }}
                .content {{
                    white-space: pre-wrap;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <small>🧪 TEST EMAIL - {template["name"]}</small>
            </div>
            <div class="content">{final_body}</div>
        </body>
        </html>
        """

        # Send email
        params = {
            "from": "Sang Le - BusOS <value@galatek.dev>",
            "to": [to_email],
            "subject": f"[TEST] {final_subject}",
            "html": html_body
        }

        response = resend.Emails.send(params)
        return response["id"]

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(description="Send test emails for template verification")
    parser.add_argument("--sequence", help="Filter by sequence (e.g., '5-Day', '7-Day')")
    parser.add_argument("--template", help="Send specific template by name")
    parser.add_argument("--all", action="store_true", help="Send all active templates")
    parser.add_argument("--email", default="lengobaosang@gmail.com", help="Recipient email")

    args = parser.parse_args()

    print("\n🚀 Email Template Test Suite")
    print("=" * 80)

    # Get sample variables
    variables = get_sample_variables()

    # Fetch templates
    if args.template:
        templates = fetch_templates()
        templates = [t for t in templates if t["name"] == args.template]
        if not templates:
            print(f"❌ Template '{args.template}' not found")
            return 1
    elif args.sequence:
        templates = fetch_templates(sequence_filter=args.sequence)
    elif args.all:
        templates = fetch_templates()
    else:
        # Default: 5-Day sequence
        templates = fetch_templates(sequence_filter="5-Day")

    if not templates:
        print("❌ No templates found matching criteria")
        return 1

    print(f"✅ Found {len(templates)} templates to test\n")

    # Send test emails
    results = []

    for i, template in enumerate(templates, 1):
        print(f"\n📧 {i}/{len(templates)}: {template['name']}")
        print(f"   Subject: {template['subject'][:60]}...")

        email_id = send_test_email(template, args.email, variables)

        if email_id:
            print(f"   ✅ Sent! Email ID: {email_id}")
            results.append({"template": template["name"], "status": "sent", "email_id": email_id})
        else:
            print(f"   ❌ Failed to send")
            results.append({"template": template["name"], "status": "failed", "email_id": None})

    # Summary
    print("\n" + "=" * 80)
    print("📊 Test Email Summary:")
    print("-" * 80)

    sent_count = sum(1 for r in results if r["status"] == "sent")
    failed_count = sum(1 for r in results if r["status"] == "failed")

    print(f"   ✅ Sent: {sent_count}")
    print(f"   ❌ Failed: {failed_count}")

    print("\n📋 Details:")
    for result in results:
        status_emoji = "✅" if result["status"] == "sent" else "❌"
        print(f"   {status_emoji} {result['template']}")
        if result["email_id"]:
            print(f"      Email ID: {result['email_id']}")

    print("\n" + "=" * 80)
    print("✅ Test email suite complete!")
    print(f"\n💡 Check inbox: {args.email}")
    print("💡 Verify formatting and variable substitution")
    print("💡 Check Resend dashboard: https://resend.com/emails")

    return 0 if failed_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
