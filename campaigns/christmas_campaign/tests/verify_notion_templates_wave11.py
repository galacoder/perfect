#!/usr/bin/env python3
"""
Wave 11 Feature 11.1: Verify Notion Email Templates Have Updated Testimonials

This script checks all 16 email templates in Notion to verify:
1. Real testimonials are present (Van Tiny, Hera Nguyen, Loc Diem)
2. NO fabricated testimonials remain (Jennifer K, Sarah P, Linh, Marcus Chen, etc.)

Per user feedback: Wave 9 was WRONG because it used hardcoded templates.
This verification reads ACTUAL Notion templates to confirm audit changes.
"""

import os
import sys
from dotenv import load_dotenv
from notion_client import Client

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_EMAIL_TEMPLATES_DB_ID = os.getenv("NOTION_EMAIL_TEMPLATES_DB_ID")

# Real testimonials we expect to find (from task 1127)
EXPECTED_REAL_TESTIMONIALS = [
    "Van Tiny",
    "Hera Nguyen",
    "Loc Diem"
]

# Fabricated testimonials that should NOT appear
FABRICATED_TESTIMONIALS = [
    "Jennifer K",
    "Sarah P",
    "Linh",
    "Marcus Chen",
    "Sofia Rodriguez",
    "James Thompson"
]

def verify_notion_templates():
    """Query all email templates from Notion and verify testimonials"""

    notion = Client(auth=NOTION_TOKEN)

    print("=" * 80)
    print("Wave 11 Feature 11.1: Verify Notion Email Templates")
    print("=" * 80)
    print(f"Notion Database ID: {NOTION_EMAIL_TEMPLATES_DB_ID}")
    print()

    # Query all templates
    try:
        response = notion.databases.query(
            database_id=NOTION_EMAIL_TEMPLATES_DB_ID,
            sorts=[
                {
                    "property": "Template Name",
                    "direction": "ascending"
                }
            ]
        )

        templates = response.get("results", [])
        print(f"Found {len(templates)} email templates in Notion")
        print()

        # Track results
        templates_with_real_testimonials = []
        templates_with_fabricated_testimonials = []
        templates_checked = []

        # Check each template
        for template in templates:
            props = template.get("properties", {})

            # Get template name
            template_name_prop = props.get("Template Name", {})
            if template_name_prop.get("type") == "title":
                title_items = template_name_prop.get("title", [])
                template_name = title_items[0].get("plain_text", "Unknown") if title_items else "Unknown"
            else:
                template_name = "Unknown"

            # Get Email Body Plain Text (this is where testimonials are stored)
            body_prop = props.get("Email Body Plain Text", {})
            body_content = ""
            if body_prop.get("type") == "rich_text":
                rich_text_items = body_prop.get("rich_text", [])
                body_content = "".join([item.get("plain_text", "") for item in rich_text_items])

            # Also check HTML content (backup)
            html_content_prop = props.get("Email Body HTML", {})
            html_content = ""
            if html_content_prop.get("type") == "rich_text":
                rich_text_items = html_content_prop.get("rich_text", [])
                html_content = "".join([item.get("plain_text", "") for item in rich_text_items])

            # Combined content
            combined_content = body_content + " " + html_content

            # Get Subject
            subject_prop = props.get("Subject", {})
            subject = ""
            if subject_prop.get("type") == "rich_text":
                subject_items = subject_prop.get("rich_text", [])
                subject = "".join([item.get("plain_text", "") for item in subject_items])

            # Get Version (it's rich_text, not number)
            version_prop = props.get("Version", {})
            version = "1"
            if version_prop.get("type") == "rich_text":
                version_items = version_prop.get("rich_text", [])
                version = "".join([item.get("plain_text", "1") for item in version_items]) if version_items else "1"

            # Get Subject Line (backup field)
            subject_line_prop = props.get("Subject Line", {})
            if not subject and subject_line_prop.get("type") == "rich_text":
                subject_items = subject_line_prop.get("rich_text", [])
                subject = "".join([item.get("plain_text", "") for item in subject_items])

            templates_checked.append(template_name)

            # Check for real testimonials
            has_real = any(name in combined_content for name in EXPECTED_REAL_TESTIMONIALS)
            if has_real:
                templates_with_real_testimonials.append(template_name)

            # Check for fabricated testimonials
            has_fabricated = any(name in combined_content for name in FABRICATED_TESTIMONIALS)
            if has_fabricated:
                fabricated_found = [name for name in FABRICATED_TESTIMONIALS if name in combined_content]
                templates_with_fabricated_testimonials.append({
                    "template": template_name,
                    "fabricated": fabricated_found
                })

            print(f"✓ {template_name} (v{version})")
            print(f"  Subject: {subject[:60]}{'...' if len(subject) > 60 else ''}")

            if has_real:
                found_real = [name for name in EXPECTED_REAL_TESTIMONIALS if name in html_content]
                print(f"  ✅ Real testimonials found: {', '.join(found_real)}")

            if has_fabricated:
                print(f"  ❌ FABRICATED testimonials found: {', '.join(fabricated_found)}")

            print()

        # Summary
        print("=" * 80)
        print("VERIFICATION SUMMARY")
        print("=" * 80)
        print(f"Total templates checked: {len(templates_checked)}")
        print(f"Templates with real testimonials: {len(templates_with_real_testimonials)}")
        print(f"Templates with fabricated testimonials: {len(templates_with_fabricated_testimonials)}")
        print()

        if templates_with_fabricated_testimonials:
            print("❌ FAILED: Found fabricated testimonials in:")
            for item in templates_with_fabricated_testimonials:
                print(f"   - {item['template']}: {', '.join(item['fabricated'])}")
            print()
            return False
        else:
            print("✅ PASSED: No fabricated testimonials found")
            print()

        if templates_with_real_testimonials:
            print(f"✅ {len(templates_with_real_testimonials)} templates contain real testimonials:")
            for name in templates_with_real_testimonials:
                print(f"   - {name}")
        else:
            print("⚠️  WARNING: No templates contain real testimonials (Van Tiny, Hera Nguyen, Loc Diem)")

        print()
        print("=" * 80)
        return True

    except Exception as e:
        print(f"❌ ERROR querying Notion: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = verify_notion_templates()
    sys.exit(0 if success else 1)
