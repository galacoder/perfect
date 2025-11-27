#!/usr/bin/env python3
"""
Inspect Notion template structure to understand how content is stored
"""

import os
import json
from dotenv import load_dotenv
from notion_client import Client

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_EMAIL_TEMPLATES_DB_ID = os.getenv("NOTION_EMAIL_TEMPLATES_DB_ID")

def inspect_notion_template():
    """Query one template and show complete structure"""

    notion = Client(auth=NOTION_TOKEN)

    print("Querying Notion templates...")

    response = notion.databases.query(
        database_id=NOTION_EMAIL_TEMPLATES_DB_ID,
        filter={
            "property": "Template Name",
            "title": {
                "contains": "postcall_maybe_email_2"
            }
        }
    )

    if response.get("results"):
        template = response["results"][0]
        print("\n" + "=" * 80)
        print("TEMPLATE STRUCTURE")
        print("=" * 80)
        print(json.dumps(template, indent=2))

        # Also retrieve the page content (blocks)
        page_id = template["id"]
        print("\n" + "=" * 80)
        print("PAGE CONTENT (BLOCKS)")
        print("=" * 80)

        blocks = notion.blocks.children.list(block_id=page_id)
        print(json.dumps(blocks, indent=2))

if __name__ == "__main__":
    inspect_notion_template()
