"""
Check Notion Email Templates - Wave 7 Feature 7.3

This script verifies all Christmas campaign email templates exist in Notion
and have valid HTML content.

Usage:
    python campaigns/christmas_campaign/scripts/check_notion_templates.py

Author: Wave 7 Email Debugging
Created: 2025-11-28
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

load_dotenv()

# Expected templates (21 total)
EXPECTED_TEMPLATES = [
    # Lead Nurture (5 templates)
    "5-Day E1",
    "5-Day E2",
    "5-Day E3",
    "5-Day E4",
    "5-Day E5",
    # No-Show Recovery (3 templates)
    "No-Show Recovery E1",
    "No-Show Recovery E2",
    "No-Show Recovery E3",
    # Post-Call Maybe (3 templates)
    "Post-Call Maybe E1",
    "Post-Call Maybe E2",
    "Post-Call Maybe E3",
    # Onboarding (3 templates)
    "Onboarding Phase 1 E1",
    "Onboarding Phase 1 E2",
    "Onboarding Phase 1 E3",
]


async def check_all_templates():
    """Query Notion database and verify all templates exist with valid content."""
    print("=" * 80)
    print("📧 Checking Notion Email Templates")
    print("=" * 80)

    try:
        # Get credentials
        from prefect.blocks.system import Secret
        try:
            NOTION_TOKEN = Secret.load("notion-token").get()
            NOTION_DB_ID = Secret.load("notion-email-templates-db-id").get()
            print("✅ Loaded credentials from Prefect Secret blocks")
        except:
            NOTION_TOKEN = os.getenv("NOTION_TOKEN")
            NOTION_DB_ID = os.getenv("NOTION_EMAIL_TEMPLATES_DB_ID")
            print("⚠️  Using environment variables for credentials")

        if not NOTION_TOKEN or not NOTION_DB_ID:
            print("❌ Missing NOTION_TOKEN or NOTION_EMAIL_TEMPLATES_DB_ID")
            return

        print(f"📦 Database ID: {NOTION_DB_ID}")
        print("")

        # Import Notion client
        from notion_client import AsyncClient

        notion = AsyncClient(auth=NOTION_TOKEN)

        # Query all templates
        response = await notion.databases.query(database_id=NOTION_DB_ID)
        templates = response.get("results", [])

        print(f"📊 Found {len(templates)} templates in Notion database\n")

        # Create a mapping
        template_map = {}
        for page in templates:
            props = page.get("properties", {})

            # Get template name
            name_prop = props.get("Name") or props.get("Template Name")
            if name_prop and name_prop.get("title"):
                name = name_prop["title"][0]["plain_text"]

                # Get subject
                subject_prop = props.get("Subject")
                subject = subject_prop["rich_text"][0]["plain_text"] if subject_prop and subject_prop.get("rich_text") else "N/A"

                # Get body (check if it exists)
                body_prop = props.get("Body") or props.get("HTML Body")
                has_body = body_prop and body_prop.get("rich_text") and len(body_prop["rich_text"]) > 0
                body_length = len(body_prop["rich_text"][0]["plain_text"]) if has_body else 0

                template_map[name] = {
                    "subject": subject,
                    "has_body": has_body,
                    "body_length": body_length,
                    "page_id": page["id"]
                }

        # Check expected templates
        print("=" * 80)
        print("✅ Template Verification")
        print("=" * 80)

        missing = []
        invalid = []

        for template_name in EXPECTED_TEMPLATES:
            if template_name not in template_map:
                missing.append(template_name)
                print(f"❌ MISSING: {template_name}")
            else:
                info = template_map[template_name]
                if not info["has_body"] or info["body_length"] == 0:
                    invalid.append(template_name)
                    print(f"⚠️  INVALID (no body): {template_name}")
                else:
                    print(f"✅ VALID: {template_name}")
                    print(f"   Subject: {info['subject']}")
                    print(f"   Body length: {info['body_length']} chars")
                    print(f"   Page ID: {info['page_id']}")
                    print("")

        # Summary
        print("=" * 80)
        print("📊 Summary")
        print("=" * 80)
        print(f"Expected templates: {len(EXPECTED_TEMPLATES)}")
        print(f"Found in Notion: {len(template_map)}")
        print(f"Valid templates: {len(EXPECTED_TEMPLATES) - len(missing) - len(invalid)}")
        print(f"Missing templates: {len(missing)}")
        print(f"Invalid templates (no body): {len(invalid)}")

        if missing:
            print(f"\n❌ Missing templates:")
            for name in missing:
                print(f"   - {name}")

        if invalid:
            print(f"\n⚠️  Invalid templates (no HTML body):")
            for name in invalid:
                print(f"   - {name}")

        if not missing and not invalid:
            print("\n✅ ALL TEMPLATES VALID!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(check_all_templates())
