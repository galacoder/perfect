"""
One-time script to seed email templates to Notion Templates database.

Run this once to populate Notion with all 9 email templates from config/email_templates.py.
After seeding, you can edit templates directly in Notion for on-the-fly changes.

Usage:
    cd /Users/sangle/dev/action/projects/perfect
    python scripts/seed_templates.py
"""

import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from config.email_templates import TEMPLATES
from campaigns.businessx_canada_lead_nurture.tasks.template_operations import seed_templates_to_notion

# Load environment variables
load_dotenv()

def main():
    """Seed all email templates to Notion Templates database."""
    print("=" * 60)
    print("Email Template Seeding Script")
    print("=" * 60)
    print()

    # Verify environment variables
    notion_token = os.getenv("NOTION_TOKEN")
    templates_db_id = os.getenv("NOTION_TEMPLATES_DB_ID")

    if not notion_token:
        print("❌ Error: NOTION_TOKEN not found in environment")
        print("   Please set NOTION_TOKEN in .env file")
        sys.exit(1)

    if not templates_db_id:
        print("❌ Error: NOTION_TEMPLATES_DB_ID not found in environment")
        print("   Please set NOTION_TEMPLATES_DB_ID in .env file")
        sys.exit(1)

    print(f"✅ NOTION_TOKEN: {notion_token[:20]}...")
    print(f"✅ NOTION_TEMPLATES_DB_ID: {templates_db_id}")
    print()

    # Display templates to be seeded
    print(f"📋 Found {len(TEMPLATES)} templates to seed:")
    for i, template_name in enumerate(TEMPLATES.keys(), 1):
        template = TEMPLATES[template_name]
        subject = template["subject"][:60] + "..." if len(template["subject"]) > 60 else template["subject"]
        print(f"   {i}. {template_name}")
        print(f"      Subject: {subject}")

    print()
    print("🚀 Starting seeding process...")
    print()

    # Seed templates
    try:
        result = seed_templates_to_notion(TEMPLATES)

        print()
        print("=" * 60)
        print("✅ Seeding Complete!")
        print("=" * 60)
        print()
        print(f"Created/Found {len(result)} templates in Notion:")
        for template_name, page_id in result.items():
            print(f"   - {template_name}: {page_id}")

        print()
        print("🎉 You can now edit these templates in Notion!")
        print(f"   Visit: https://notion.so/{templates_db_id}")
        print()
        print("💡 Tip: Changes in Notion will be reflected immediately in the next email send.")

    except Exception as e:
        print()
        print("=" * 60)
        print("❌ Seeding Failed")
        print("=" * 60)
        print()
        print(f"Error: {e}")
        print()
        print("Troubleshooting:")
        print("1. Verify Notion integration has access to Templates database")
        print("2. Check that NOTION_TEMPLATES_DB_ID is correct")
        print("3. Ensure Notion database has required properties:")
        print("   - Template Name (Title)")
        print("   - Subject (Rich Text)")
        print("   - HTML Body (Rich Text)")
        print("   - Active (Checkbox)")
        print("   - Last Modified (Last edited time)")
        sys.exit(1)


if __name__ == "__main__":
    main()
