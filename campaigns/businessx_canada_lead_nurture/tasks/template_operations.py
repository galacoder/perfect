"""
Notion email template operations for BusOS Email Sequence.

This module provides Prefect tasks for fetching email templates dynamically from
the Notion Templates database, allowing on-the-fly editing without code changes.

Templates DB Schema:
- Template Name (Title): Unique identifier (e.g., "email_1", "email_2a_critical")
- Subject (Rich Text): Email subject line with {{variable}} placeholders
- HTML Body (Rich Text): Email HTML content with {{variable}} placeholders
- Active (Checkbox): Whether template is active/published
- Last Modified (Last edited time): Automatic timestamp

All templates use {{variable}} placeholders for substitution.
"""

from prefect import task
from notion_client import Client
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load environment variables
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_TEMPLATES_DB_ID = os.getenv("NOTION_TEMPLATES_DB_ID")

# Initialize Notion client
notion = Client(auth=NOTION_TOKEN)


@task(retries=3, retry_delay_seconds=60, name="template-fetch-from-notion")
def fetch_template_from_notion(template_name: str) -> Dict[str, str]:
    """
    Fetch email template from Notion Templates database by name.

    Args:
        template_name: Template identifier (e.g., "email_1", "email_2a_critical")

    Returns:
        Dictionary with "subject" and "html" keys containing template strings

    Raises:
        ValueError: If template not found or not active
        Exception: If Notion API error

    Example:
        template = fetch_template_from_notion("email_1")
        subject = template["subject"]  # "Your Free BusOS Assessment is Ready, {{first_name}}"
        html = template["html"]  # "<!DOCTYPE html><html>..."
    """
    if not NOTION_TOKEN or not NOTION_TEMPLATES_DB_ID:
        raise ValueError("NOTION_TOKEN and NOTION_TEMPLATES_DB_ID must be set in environment")

    try:
        # Query Templates database for specific template
        response = notion.databases.query(
            database_id=NOTION_TEMPLATES_DB_ID,
            filter={
                "and": [
                    {
                        "property": "Template Name",
                        "title": {
                            "equals": template_name
                        }
                    },
                    {
                        "property": "Status",
                        "select": {
                            "equals": "Active"
                        }
                    }
                ]
            }
        )

        if not response["results"]:
            raise ValueError(
                f"Template '{template_name}' not found or not active in Notion Templates DB. "
                f"Please create template in Notion with Template Name = '{template_name}' and Status = 'Active'."
            )

        # Extract template data from first result
        template_page = response["results"][0]
        properties = template_page["properties"]

        # Extract subject (Rich Text property)
        subject_property = properties.get("Subject", {})
        subject_text = subject_property.get("rich_text", [])
        subject = "".join([text["plain_text"] for text in subject_text]) if subject_text else ""

        # Extract HTML body (Rich Text property - may be long, so handle pagination)
        html_property = properties.get("HTML Body", {})
        html_text = html_property.get("rich_text", [])
        html = "".join([text["plain_text"] for text in html_text]) if html_text else ""

        if not subject or not html:
            raise ValueError(
                f"Template '{template_name}' is missing Subject or HTML Body. "
                f"Please ensure both fields are filled in Notion."
            )

        print(f"✅ Fetched template '{template_name}' from Notion (subject: {len(subject)} chars, html: {len(html)} chars)")

        return {
            "subject": subject,
            "html": html
        }

    except Exception as e:
        print(f"❌ Error fetching template '{template_name}' from Notion: {e}")
        raise


# Cache for templates (simple dict-based cache)
_template_cache: Dict[str, Dict[str, str]] = {}

@task(name="template-cache-from-notion")
def fetch_template_cached(template_name: str) -> Dict[str, str]:
    """
    Fetch email template from Notion with caching to reduce API calls.

    Caches templates in memory. Cache persists for duration of flow run.
    Use this for production to minimize Notion API rate limit usage.

    Args:
        template_name: Template identifier (e.g., "email_1", "email_2a_critical")

    Returns:
        Dictionary with "subject" and "html" keys

    Example:
        # First call fetches from Notion
        template1 = fetch_template_cached("email_1")

        # Subsequent calls return cached version (no API call)
        template2 = fetch_template_cached("email_1")
    """
    if template_name not in _template_cache:
        _template_cache[template_name] = fetch_template_from_notion(template_name)
    return _template_cache[template_name]


@task(retries=3, retry_delay_seconds=60, name="template-list-all")
def list_all_templates() -> list[Dict[str, Any]]:
    """
    List all active templates in Notion Templates database.

    Useful for debugging, validation, or displaying available templates.

    Returns:
        List of template dictionaries with metadata

    Example:
        templates = list_all_templates()
        for template in templates:
            print(f"- {template['name']}: {template['subject'][:50]}...")
    """
    if not NOTION_TOKEN or not NOTION_TEMPLATES_DB_ID:
        raise ValueError("NOTION_TOKEN and NOTION_TEMPLATES_DB_ID must be set in environment")

    try:
        response = notion.databases.query(
            database_id=NOTION_TEMPLATES_DB_ID,
            filter={
                "property": "Status",
                "select": {
                    "equals": "Active"
                }
            },
            sorts=[
                {
                    "property": "Template Name",
                    "direction": "ascending"
                }
            ]
        )

        templates = []
        for page in response["results"]:
            properties = page["properties"]

            # Extract template name
            name_property = properties.get("Template Name", {})
            name_text = name_property.get("title", [])
            name = "".join([text["plain_text"] for text in name_text]) if name_text else "Unnamed"

            # Extract subject
            subject_property = properties.get("Subject", {})
            subject_text = subject_property.get("rich_text", [])
            subject = "".join([text["plain_text"] for text in subject_text]) if subject_text else ""

            # Extract last modified
            last_modified = properties.get("Last Modified", {}).get("last_edited_time", "")

            templates.append({
                "name": name,
                "subject": subject,
                "last_modified": last_modified,
                "page_id": page["id"]
            })

        print(f"✅ Found {len(templates)} active templates in Notion")
        return templates

    except Exception as e:
        print(f"❌ Error listing templates from Notion: {e}")
        raise


@task(retries=3, retry_delay_seconds=60, name="template-seed-notion-db")
def seed_templates_to_notion(templates: Dict[str, Dict[str, str]]) -> Dict[str, str]:
    """
    Seed email templates to Notion Templates database (one-time setup).

    Use this to populate the Notion Templates DB with initial templates from
    config/email_templates.py. After seeding, you can edit templates in Notion.

    Args:
        templates: Dictionary mapping template names to {"subject": str, "html": str}

    Returns:
        Dictionary mapping template names to created page IDs

    Example:
        from config.email_templates import TEMPLATES
        result = seed_templates_to_notion(TEMPLATES)
        print(f"Created {len(result)} templates in Notion")
    """
    if not NOTION_TOKEN or not NOTION_TEMPLATES_DB_ID:
        raise ValueError("NOTION_TOKEN and NOTION_TEMPLATES_DB_ID must be set in environment")

    created_pages = {}

    for template_name, template_data in templates.items():
        try:
            # Check if template already exists
            existing = notion.databases.query(
                database_id=NOTION_TEMPLATES_DB_ID,
                filter={
                    "property": "Template Name",
                    "title": {
                        "equals": template_name
                    }
                }
            )

            if existing["results"]:
                print(f"⏭️  Template '{template_name}' already exists, skipping")
                created_pages[template_name] = existing["results"][0]["id"]
                continue

            # Create new template page
            properties = {
                "Template Name": {
                    "title": [{"text": {"content": template_name}}]
                },
                "Subject": {
                    "rich_text": [{"text": {"content": template_data["subject"]}}]
                },
                "HTML Body": {
                    "rich_text": [{"text": {"content": template_data["html"][:2000]}}]
                    # Note: Notion rich_text has 2000 char limit per block
                    # For long HTML, may need to split or use Code block
                },
                "Status": {
                    "select": {"name": "Active"}
                }
            }

            response = notion.pages.create(
                parent={"database_id": NOTION_TEMPLATES_DB_ID},
                properties=properties
            )

            created_pages[template_name] = response["id"]
            print(f"✅ Created template '{template_name}' in Notion (page_id: {response['id']})")

        except Exception as e:
            print(f"❌ Error creating template '{template_name}': {e}")
            continue

    return created_pages


# Helper function for backward compatibility
def get_template(template_name: str, use_notion: bool = True) -> Dict[str, str]:
    """
    Get email template from Notion (default) or fallback to static config.

    Args:
        template_name: Template identifier
        use_notion: If True, fetch from Notion; if False, use static config

    Returns:
        Dictionary with "subject" and "html" keys

    Example:
        # Fetch from Notion (dynamic, editable)
        template = get_template("email_1")

        # Use static fallback (for testing or offline)
        template = get_template("email_1", use_notion=False)
    """
    if use_notion:
        return fetch_template_cached(template_name)
    else:
        # Fallback to static templates
        from config.email_templates import TEMPLATES
        if template_name not in TEMPLATES:
            raise KeyError(f"Template '{template_name}' not found in static config")
        return TEMPLATES[template_name]
