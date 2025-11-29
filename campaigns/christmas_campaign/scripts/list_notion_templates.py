"""
List all templates in Notion Email Templates database.

Usage:
    python campaigns/christmas_campaign/scripts/list_notion_templates.py
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
load_dotenv()


async def list_all_templates():
    """List all templates in the database."""
    try:
        NOTION_TOKEN = os.getenv("NOTION_TOKEN")
        NOTION_DB_ID = os.getenv("NOTION_EMAIL_TEMPLATES_DB_ID")

        if not NOTION_TOKEN or not NOTION_DB_ID:
            print("❌ Missing credentials")
            return

        from notion_client import AsyncClient
        notion = AsyncClient(auth=NOTION_TOKEN)

        response = await notion.databases.query(database_id=NOTION_DB_ID)
        templates = response.get("results", [])

        print(f"📧 Found {len(templates)} templates:\n")

        for i, page in enumerate(templates, 1):
            props = page.get("properties", {})

            # Get template name
            name_prop = props.get("Name") or props.get("Template Name")
            if name_prop and name_prop.get("title"):
                name = name_prop["title"][0]["plain_text"]

                # Get subject
                subject_prop = props.get("Subject")
                subject = subject_prop["rich_text"][0]["plain_text"] if subject_prop and subject_prop.get("rich_text") else "N/A"

                # Get template type
                type_prop = props.get("Template Type")
                template_type = type_prop["select"]["name"] if type_prop and type_prop.get("select") else "N/A"

                # Get body length
                body_prop = props.get("Body") or props.get("HTML Body")
                body_length = len(body_prop["rich_text"][0]["plain_text"]) if body_prop and body_prop.get("rich_text") else 0

                print(f"{i}. {name}")
                print(f"   Type: {template_type}")
                print(f"   Subject: {subject}")
                print(f"   Body length: {body_length} chars")
                print(f"   Page ID: {page['id']}")
                print("")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(list_all_templates())
