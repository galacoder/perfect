"""
Delete existing email sequence for test email from Notion Email Sequence database.

This script is used before E2E testing to bypass idempotency checks.
"""
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_EMAIL_SEQUENCE_DB_ID = os.getenv("NOTION_EMAIL_SEQUENCE_DB_ID")
TEST_EMAIL = "lengobaosang@gmail.com"

NOTION_API_VERSION = "2022-06-28"
NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": NOTION_API_VERSION
}

def search_sequence_by_email(email: str):
    """Search for existing email sequence record by email."""
    url = f"https://api.notion.com/v1/databases/{NOTION_EMAIL_SEQUENCE_DB_ID}/query"

    payload = {
        "filter": {
            "property": "Email",
            "email": {
                "equals": email
            }
        }
    }

    response = requests.post(url, json=payload, headers=NOTION_HEADERS)
    response.raise_for_status()

    results = response.json().get("results", [])
    return results

def archive_page(page_id: str):
    """Archive (soft delete) a Notion page."""
    url = f"https://api.notion.com/v1/pages/{page_id}"

    payload = {
        "archived": True
    }

    response = requests.patch(url, json=payload, headers=NOTION_HEADERS)
    response.raise_for_status()

    return response.json()

def main():
    print(f"Searching for existing email sequence for: {TEST_EMAIL}")
    print(f"Database ID: {NOTION_EMAIL_SEQUENCE_DB_ID}")

    # Search for existing records
    results = search_sequence_by_email(TEST_EMAIL)

    if not results:
        print(f"✅ No existing sequence found for {TEST_EMAIL}")
        return

    print(f"Found {len(results)} existing record(s)")

    # Archive each record
    for idx, record in enumerate(results, 1):
        page_id = record["id"]
        campaign = record.get("properties", {}).get("Campaign", {}).get("rich_text", [{}])[0].get("text", {}).get("content", "Unknown")

        print(f"\n{idx}. Archiving record:")
        print(f"   Page ID: {page_id}")
        print(f"   Campaign: {campaign}")

        archive_page(page_id)
        print(f"   ✅ Archived successfully")

    print(f"\n✅ All records archived. Ready for E2E test.")

if __name__ == "__main__":
    main()
