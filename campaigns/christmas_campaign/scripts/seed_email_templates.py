"""
Christmas Campaign Email Template Seeding Script

This script uploads email templates from config to Notion Email Templates database.
Supports idempotent operation (create new or update existing templates).

Usage:
    python campaigns/christmas_campaign/scripts/seed_email_templates.py
    python campaigns/christmas_campaign/scripts/seed_email_templates.py --template christmas_email_1
    python campaigns/christmas_campaign/scripts/seed_email_templates.py --dry-run

Author: Automation Developer
Created: 2025-11-18
"""

import os
import sys
from typing import Dict, Optional, Any
from pathlib import Path
from dotenv import load_dotenv
from notion_client import Client

# Add project root to path for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.insert(0, project_root)

from campaigns.christmas_campaign.config.email_templates_christmas import TEMPLATES

# Load environment variables from project root
env_path = Path(project_root) / ".env"
load_dotenv(dotenv_path=env_path)

# Environment variables
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_EMAIL_TEMPLATES_DB_ID = os.getenv("NOTION_EMAIL_TEMPLATES_DB_ID")

# Initialize Notion client
notion = Client(auth=NOTION_TOKEN)


def validate_environment() -> None:
    """Validate required environment variables are set."""
    if not NOTION_TOKEN:
        raise ValueError("❌ NOTION_TOKEN not found in environment variables")

    if not NOTION_EMAIL_TEMPLATES_DB_ID:
        raise ValueError("❌ NOTION_EMAIL_TEMPLATES_DB_ID not found in environment variables")

    print("✅ Environment validation passed")


def find_existing_template(template_id: str) -> Optional[Dict[str, Any]]:
    """
    Find existing template in Notion by Template Name.

    Args:
        template_id: Template identifier (e.g., 'christmas_email_1')

    Returns:
        Notion page object if found, None otherwise
    """
    try:
        # Query database for template with matching Template Name
        response = notion.databases.query(
            database_id=NOTION_EMAIL_TEMPLATES_DB_ID,
            filter={
                "property": "Template Name",
                "title": {"equals": template_id}
            }
        )

        if response["results"]:
            return response["results"][0]
        return None

    except Exception as e:
        print(f"❌ Error querying template {template_id}: {e}")
        raise


def create_template(template_id: str, template_data: Dict[str, Any]) -> str:
    """
    Create new template page in Notion.

    Args:
        template_id: Template identifier
        template_data: Template configuration from TEMPLATES dict

    Returns:
        Notion page ID of created template
    """
    try:
        # Build properties for Notion page matching database schema
        properties = {
            "Template Name": {
                "title": [{"type": "text", "text": {"content": template_id}}]
            },
            "Subject Line": {
                "rich_text": [{"type": "text", "text": {"content": template_data["subject"]}}]
            },
            "Email Body HTML": {
                "rich_text": [{"type": "text", "text": {"content": template_data["html_body"][:2000]}}]
            },
            "Email Number": {
                "number": template_data["email_number"]
            },
            "Status": {
                "select": {"name": "Active" if template_data["active"] else "Inactive"}
            },
            "Template Type": {
                "select": {"name": "Nurture Sequence"}
            }
        }

        # Add segment if it's a multi-select property
        if "segment" in template_data and template_data["segment"]:
            properties["Segment"] = {
                "multi_select": [{"name": seg} for seg in template_data["segment"]]
            }

        # Create page in Notion database
        page = notion.pages.create(
            parent={"database_id": NOTION_EMAIL_TEMPLATES_DB_ID},
            properties=properties
        )

        page_id = page["id"]
        print(f"✅ Created template: {template_id} (page_id: {page_id})")
        return page_id

    except Exception as e:
        print(f"❌ Error creating template {template_id}: {e}")
        raise


def update_template(page_id: str, template_id: str, template_data: Dict[str, Any]) -> str:
    """
    Update existing template page in Notion.

    Args:
        page_id: Notion page ID to update
        template_id: Template identifier
        template_data: Template configuration from TEMPLATES dict

    Returns:
        Notion page ID of updated template
    """
    try:
        # Build properties for update matching database schema
        properties = {
            "Subject Line": {
                "rich_text": [{"type": "text", "text": {"content": template_data["subject"]}}]
            },
            "Email Body HTML": {
                "rich_text": [{"type": "text", "text": {"content": template_data["html_body"][:2000]}}]
            },
            "Email Number": {
                "number": template_data["email_number"]
            },
            "Status": {
                "select": {"name": "Active" if template_data["active"] else "Inactive"}
            },
            "Template Type": {
                "select": {"name": "Nurture Sequence"}
            }
        }

        # Add segment if applicable
        if "segment" in template_data and template_data["segment"]:
            properties["Segment"] = {
                "multi_select": [{"name": seg} for seg in template_data["segment"]]
            }

        # Update page in Notion
        notion.pages.update(
            page_id=page_id,
            properties=properties
        )

        print(f"✅ Updated template: {template_id} (page_id: {page_id})")
        return page_id

    except Exception as e:
        print(f"❌ Error updating template {template_id}: {e}")
        raise


def upload_template_to_notion(template_id: str, template_data: Dict[str, Any]) -> str:
    """
    Upload template to Notion (idempotent: create or update).

    Args:
        template_id: Template identifier
        template_data: Template configuration from TEMPLATES dict

    Returns:
        Notion page ID (created or updated)
    """
    # Check if template already exists
    existing_page = find_existing_template(template_id)

    if existing_page:
        # Update existing template
        return update_template(existing_page["id"], template_id, template_data)
    else:
        # Create new template
        return create_template(template_id, template_data)


def seed_all_templates() -> Dict[str, str]:
    """
    Upload all templates from TEMPLATES config to Notion.

    Returns:
        Dict mapping template_id to page_id
    """
    print("\n" + "="*60)
    print("🎄 Christmas Campaign Email Template Seeding")
    print("="*60 + "\n")

    # Validate environment
    validate_environment()

    print(f"\n📊 Found {len(TEMPLATES)} templates to upload\n")

    results = {}

    for template_id, template_data in TEMPLATES.items():
        try:
            page_id = upload_template_to_notion(template_id, template_data)
            results[template_id] = page_id
        except Exception as e:
            print(f"❌ Failed to upload {template_id}: {e}")
            # Continue with other templates

    print("\n" + "="*60)
    print(f"✅ Upload Complete: {len(results)}/{len(TEMPLATES)} templates uploaded")
    print("="*60 + "\n")

    return results


def main():
    """Main entry point for CLI execution."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Upload Christmas Campaign email templates to Notion"
    )
    parser.add_argument(
        "--template",
        type=str,
        help="Upload specific template by ID (e.g., christmas_email_1)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be uploaded without making changes"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force update even if template exists"
    )

    args = parser.parse_args()

    if args.dry_run:
        print("\n🔍 DRY RUN MODE - No changes will be made\n")
        print(f"Found {len(TEMPLATES)} templates:")
        for template_id, template_data in TEMPLATES.items():
            print(f"  - {template_id}: {template_data['subject'][:50]}...")
        return

    if args.template:
        # Upload single template
        if args.template not in TEMPLATES:
            print(f"❌ Template '{args.template}' not found in config")
            print(f"Available templates: {', '.join(TEMPLATES.keys())}")
            sys.exit(1)

        print(f"\n🎯 Uploading single template: {args.template}\n")
        validate_environment()

        template_data = TEMPLATES[args.template]
        page_id = upload_template_to_notion(args.template, template_data)

        print(f"\n✅ Successfully uploaded {args.template} (page_id: {page_id})\n")
    else:
        # Upload all templates
        seed_all_templates()


if __name__ == "__main__":
    main()
