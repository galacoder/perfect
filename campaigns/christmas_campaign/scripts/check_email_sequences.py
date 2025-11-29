#!/usr/bin/env python3
"""
Check Notion Email Sequence database for scheduled/sent emails.

This script:
1. Connects to Notion Email Sequence database
2. Filters by test email (lengobaosang@gmail.com)
3. Shows all scheduled/sent emails across all sequences
4. Reports which emails were sent and which are pending

Usage:
    python campaigns/christmas_campaign/scripts/check_email_sequences.py

Author: Christmas Campaign Team
Created: 2025-11-28
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv()

# Set Prefect API URL for Secret blocks
PREFECT_API_URL = os.getenv("PREFECT_API_URL", "https://prefect.galatek.dev/api")
os.environ["PREFECT_API_URL"] = PREFECT_API_URL

# Load credentials from Prefect Secret blocks or .env
try:
    from prefect.blocks.system import Secret
    NOTION_TOKEN = Secret.load("notion-token").get()
    NOTION_SEQUENCE_DB_ID = Secret.load("notion-email-sequence-db-id").get()
    print(f"✅ Loaded credentials from Prefect Secret blocks (via {PREFECT_API_URL})")
except Exception as e:
    print(f"⚠️  Failed to load from Secret blocks, using environment variables: {e}")
    NOTION_TOKEN = os.getenv("NOTION_TOKEN")
    NOTION_SEQUENCE_DB_ID = os.getenv("NOTION_EMAIL_SEQUENCE_DB_ID")

if not NOTION_TOKEN or not NOTION_SEQUENCE_DB_ID:
    print("❌ Missing Notion credentials")
    sys.exit(1)

from notion_client import Client

notion = Client(auth=NOTION_TOKEN)


def check_email_sequences(test_email: str = "lengobaosang@gmail.com"):
    """
    Check Notion Email Sequence database for scheduled/sent emails.

    Args:
        test_email: Email address to filter by
    """
    print(f"\n🔍 Checking Email Sequence database for: {test_email}")
    print("=" * 80)

    try:
        # Query Notion database filtered by email
        print(f"\n📊 Querying database: {NOTION_SEQUENCE_DB_ID}")

        # First, query without filter to see all entries (for debugging)
        results = notion.databases.query(
            database_id=NOTION_SEQUENCE_DB_ID
        )

        sequences = results.get("results", [])

        # Filter by email in Python (since we need to handle different property structures)
        filtered_sequences = []
        for seq in sequences:
            props = seq["properties"]
            email_prop = props.get("Email", {})

            # Handle different email property types
            email_value = None
            if "email" in email_prop:
                email_value = email_prop["email"]
            elif "rich_text" in email_prop and email_prop["rich_text"]:
                email_value = email_prop["rich_text"][0].get("plain_text", "")
            elif "title" in email_prop and email_prop["title"]:
                email_value = email_prop["title"][0].get("plain_text", "")

            if email_value == test_email:
                filtered_sequences.append(seq)

        sequences = filtered_sequences

        if not sequences:
            print(f"\n⚠️  No email sequences found for {test_email}")
            print("\nPossible reasons:")
            print("1. No flows have been triggered yet")
            print("2. Email address doesn't match (check spelling)")
            print("3. Database ID is incorrect")
            print("\nNext steps:")
            print("1. Trigger a flow: POST /webhook/christmas-signup")
            print("2. Check Prefect flow runs: prefect flow-run ls")
            print("3. Verify database ID matches production")
            return []

        # Group by sequence type
        sequences_by_type = {}
        for seq in sequences:
            props = seq["properties"]

            sequence_type = props.get("Sequence Type", {}).get("select", {}).get("name", "Unknown")
            email_number = props.get("Email Number", {}).get("number", 0)
            template_name = props.get("Template Name", {}).get("rich_text", [{}])[0].get("plain_text", "N/A")
            scheduled_time = props.get("Scheduled Time", {}).get("date", {}).get("start", "N/A")
            status = props.get("Status", {}).get("select", {}).get("name", "Unknown")
            sent_at = props.get("Sent At", {}).get("date", {}).get("start", "N/A")
            resend_email_id = props.get("Resend Email ID", {}).get("rich_text", [{}])[0].get("plain_text", "N/A")

            if sequence_type not in sequences_by_type:
                sequences_by_type[sequence_type] = []

            sequences_by_type[sequence_type].append({
                "email_number": email_number,
                "template_name": template_name,
                "scheduled_time": scheduled_time,
                "status": status,
                "sent_at": sent_at,
                "resend_email_id": resend_email_id
            })

        # Display results
        print(f"\n✅ Found {len(sequences)} email sequence entries")
        print("\n" + "=" * 80)

        for seq_type, emails in sorted(sequences_by_type.items()):
            print(f"\n📧 {seq_type} ({len(emails)} emails)")
            print("-" * 80)

            for email in sorted(emails, key=lambda x: x["email_number"]):
                status_emoji = "✅" if email["status"] == "Sent" else "⏰" if email["status"] == "Scheduled" else "❌"
                print(f"   {status_emoji} Email {email['email_number']}: {email['template_name']}")
                print(f"      Status: {email['status']}")
                print(f"      Scheduled: {email['scheduled_time']}")
                if email['sent_at'] != "N/A":
                    print(f"      Sent: {email['sent_at']}")
                if email['resend_email_id'] != "N/A":
                    print(f"      Resend ID: {email['resend_email_id']}")
                print()

        # Summary
        print("=" * 80)
        print("📊 Summary by Status:")
        print("-" * 80)

        status_counts = {}
        for seq_type, emails in sequences_by_type.items():
            for email in emails:
                status = email['status']
                status_counts[status] = status_counts.get(status, 0) + 1

        for status, count in sorted(status_counts.items()):
            status_emoji = "✅" if status == "Sent" else "⏰" if status == "Scheduled" else "❌"
            print(f"   {status_emoji} {status}: {count}")

        print("\n" + "=" * 80)
        print("✅ Email sequence check complete!")

        return sequences

    except Exception as e:
        print(f"\n❌ Error checking email sequences: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Verify Notion token is valid")
        print("   2. Check database ID is correct")
        print("   3. Ensure database has Email property")
        print("   4. Check Prefect API connection")
        return []


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Check Notion Email Sequence database")
    parser.add_argument("--email", default="lengobaosang@gmail.com", help="Email address to filter by")

    args = parser.parse_args()

    sequences = check_email_sequences(test_email=args.email)
    sys.exit(0 if sequences else 1)
