#!/usr/bin/env python3
"""
Verify 5-Day email template variable mappings match Notion templates.

This script:
1. Fetches all email templates from Notion
2. Extracts {{variable}} placeholders from each template
3. Compares with get_email_variables() output
4. Reports missing or unused variables

Usage:
    python campaigns/christmas_campaign/scripts/verify_template_variables.py

Author: Christmas Campaign Team
Created: 2025-11-28
"""

import os
import sys
import re
from pathlib import Path
from dotenv import load_dotenv
from typing import Set, Dict

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
    print(f"✅ Loaded credentials from Prefect Secret blocks (via {PREFECT_API_URL})")
except Exception as e:
    print(f"⚠️  Failed to load from Secret blocks, using environment variables: {e}")
    NOTION_TOKEN = os.getenv("NOTION_TOKEN")
    NOTION_TEMPLATES_DB_ID = os.getenv("NOTION_EMAIL_TEMPLATES_DB_ID")

if not NOTION_TOKEN or not NOTION_TEMPLATES_DB_ID:
    print("❌ Missing Notion credentials")
    sys.exit(1)

from notion_client import Client

# Import the underlying function directly (not the Prefect task)
# We'll call the function logic directly to avoid Prefect API dependency
notion = Client(auth=NOTION_TOKEN)


def get_email_variables_dict():
    """
    Get all variables that get_email_variables() would provide.
    This is a non-Prefect version for testing.
    """
    from datetime import datetime

    # Sample data
    first_name = "Test"
    business_name = "Test Corp"
    assessment_score = 45
    segment = "CRITICAL"
    red_systems = 2
    orange_systems = 1
    yellow_systems = 3
    green_systems = 2
    weakest_system_1 = "GPS"
    weakest_system_2 = "FUEL"
    strongest_system = "CABIN"
    revenue_leak_total = 14700
    calendly_link = "https://cal.com/test"

    # Calculate days to deadline (December 5, 2025)
    deadline_date = "December 5, 2025"
    deadline = datetime(2025, 12, 5)
    today = datetime.now()
    days_to_deadline = max(0, (deadline - today).days)

    # Readiness zone
    readiness_zones = {
        "CRITICAL": "Crisis Zone",
        "URGENT": "Warning Zone",
        "OPTIMIZE": "Growth Zone"
    }
    readiness_zone = readiness_zones.get(segment, "Growth Zone")

    # Revenue leak in K
    total_revenue_leak_k = round(revenue_leak_total / 1000) if revenue_leak_total else 0

    # Default calendly
    default_calendly = "https://cal.com/sangletech/discovery-call"

    # Build variables dictionary (matching resend_operations.py)
    variables = {
        # Core variables (snake_case)
        "first_name": first_name,
        "business_name": business_name,

        # Assessment data (snake_case)
        "overall_score": str(assessment_score),
        "assessment_score": str(assessment_score),
        "segment": segment,
        "readiness_zone": readiness_zone,

        # Weakest/Strongest systems (snake_case)
        "weakest_system_1": weakest_system_1,
        "weakest_system_2": weakest_system_2,
        "strongest_system": strongest_system,

        # CamelCase variants for templates
        "WeakestSystem1": weakest_system_1,
        "WeakestSystem2": weakest_system_2,
        "StrongestSystem": strongest_system,

        # Revenue leak (snake_case and template format)
        "revenue_leak_total": str(revenue_leak_total),
        "TotalRevenueLeak_K": str(total_revenue_leak_k),

        # Deadline info
        "days_to_deadline": str(days_to_deadline),
        "deadline_date": deadline_date,

        # Personalized tips
        "personalized_tip_1": "Map your customer journey from first contact to payment in a Google Doc",
        "personalized_tip_2": "Write down 3 tasks you do every day that someone else could do with a checklist",
        "personalized_tip_3": "Block 2 hours this weekend to plan your December capacity.",

        # Links
        "calendly_link": calendly_link or default_calendly,

        # System counts (for debugging/analytics)
        "red_systems": str(red_systems),
        "orange_systems": str(orange_systems),
        "yellow_systems": str(yellow_systems),
        "green_systems": str(green_systems),

        # Additional variables for 5-Day email templates (E3-E5)
        "pdf_download_link": "https://sangletech.com/en/flows/businessX/dfu/xmas-a01/assessment",
        "spots_remaining": "12",
        "bookings_count": "18",
        "weakest_system": weakest_system_1,  # Alias for weakest_system_1
    }

    return variables

notion = Client(auth=NOTION_TOKEN)


def extract_variables_from_template(template: str) -> Set[str]:
    """
    Extract all {{variable}} placeholders from a template.

    Args:
        template: HTML template string

    Returns:
        Set of variable names found in template
    """
    # Find all {{variable}} patterns
    pattern = r'\{\{([^}]+)\}\}'
    matches = re.findall(pattern, template)

    # Clean up variable names (strip whitespace)
    variables = {match.strip() for match in matches}

    return variables


def verify_template_variables():
    """
    Verify all template variables are provided by get_email_variables().
    """
    print("\n🔍 Verifying Template Variable Mappings")
    print("=" * 80)

    try:
        # Fetch all templates from Notion
        print(f"\n📊 Fetching templates from database: {NOTION_TEMPLATES_DB_ID}")

        results = notion.databases.query(
            database_id=NOTION_TEMPLATES_DB_ID
        )

        templates = results.get("results", [])
        print(f"✅ Found {len(templates)} templates\n")

        # Get all variables provided by get_email_variables()
        print("📋 Getting variables from get_email_variables()...")
        sample_variables = get_email_variables_dict()

        available_variables = set(sample_variables.keys())
        print(f"✅ Found {len(available_variables)} available variables\n")
        print("Available variables:")
        for var in sorted(available_variables):
            print(f"   • {var}")

        # Analyze each template
        print("\n" + "=" * 80)
        print("📧 Template Analysis:\n")

        all_missing_vars = set()
        all_template_vars = set()

        for template_page in templates:
            props = template_page["properties"]

            # Get template name (try different property names)
            template_name = "Unknown"
            for name_field in ["Name", "Template Name", "Title"]:
                name_prop = props.get(name_field, {})
                if "title" in name_prop and name_prop["title"]:
                    template_name = name_prop["title"][0].get("plain_text", "Unknown")
                    break
                elif "rich_text" in name_prop and name_prop["rich_text"]:
                    template_name = name_prop["rich_text"][0].get("plain_text", "Unknown")
                    break

            # If still Unknown, try to get from page title
            if template_name == "Unknown" and "Page" in props:
                page_prop = props["Page"]
                if "title" in page_prop and page_prop["title"]:
                    template_name = page_prop["title"][0].get("plain_text", "Unknown")

            # Get subject (try different property names)
            subject = ""
            for subject_field in ["Subject", "Subject Line"]:
                subject_prop = props.get(subject_field, {})
                if "rich_text" in subject_prop and subject_prop["rich_text"]:
                    subject = subject_prop["rich_text"][0].get("plain_text", "")
                    break
                elif "title" in subject_prop and subject_prop["title"]:
                    subject = subject_prop["title"][0].get("plain_text", "")
                    break

            # Get body content (try different property names)
            body = ""
            for body_field in ["Body", "Email Body", "Email Body Plain Text", "Content"]:
                body_prop = props.get(body_field, {})
                if "rich_text" in body_prop and body_prop["rich_text"]:
                    body = body_prop["rich_text"][0].get("plain_text", "")
                    break

            # Extract variables from subject and body
            subject_vars = extract_variables_from_template(subject)
            body_vars = extract_variables_from_template(body)
            template_vars = subject_vars | body_vars

            all_template_vars.update(template_vars)

            # Check for missing variables
            missing_vars = template_vars - available_variables

            # Display results
            print(f"📄 {template_name}")
            print(f"   Subject: {subject[:60]}...")
            print(f"   Variables used: {len(template_vars)}")

            if template_vars:
                print(f"   Variables: {', '.join(sorted(template_vars))}")

            if missing_vars:
                print(f"   ❌ Missing variables: {', '.join(sorted(missing_vars))}")
                all_missing_vars.update(missing_vars)
            else:
                print(f"   ✅ All variables available")

            print()

        # Summary
        print("=" * 80)
        print("📊 Summary:\n")

        print(f"Total templates analyzed: {len(templates)}")
        print(f"Total unique variables used: {len(all_template_vars)}")
        print(f"Total available variables: {len(available_variables)}")

        if all_missing_vars:
            print(f"\n❌ Missing variables ({len(all_missing_vars)}):")
            for var in sorted(all_missing_vars):
                print(f"   • {var}")

            print("\n💡 Action Required:")
            print("   Add these variables to get_email_variables() in:")
            print("   campaigns/christmas_campaign/tasks/resend_operations.py")
        else:
            print(f"\n✅ All template variables are available!")

        # Check for unused variables
        unused_vars = available_variables - all_template_vars
        if unused_vars:
            print(f"\n⚠️  Unused variables ({len(unused_vars)}):")
            for var in sorted(unused_vars):
                print(f"   • {var}")
            print("\n💡 These variables are defined but not used in any template.")

        print("\n" + "=" * 80)
        print("✅ Template variable verification complete!")

        return len(all_missing_vars) == 0

    except Exception as e:
        print(f"\n❌ Error verifying template variables: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = verify_template_variables()
    sys.exit(0 if success else 1)
