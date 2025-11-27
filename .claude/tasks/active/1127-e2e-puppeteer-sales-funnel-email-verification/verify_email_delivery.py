#!/usr/bin/env python3
"""
Verify email delivery for all 7 Christmas sequence emails.
Checks Notion Email Sequence database for sent timestamps.
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from notion_client import Client

# Load environment variables
load_dotenv("/Users/sangle/Dev/action/projects/perfect/.env")

# Initialize Notion client
notion = Client(auth=os.getenv("NOTION_TOKEN"))

# Database ID for Email Sequence
EMAIL_SEQUENCE_DB_ID = "576de1aa-6064-4201-a5e6-623b7f2be79a"
TEST_EMAIL = "lengobaosang@gmail.com"

def verify_email_delivery():
    """Query Notion to verify all 7 emails were sent."""

    print(f"\n{'='*80}")
    print(f"VERIFYING EMAIL DELIVERY FOR: {TEST_EMAIL}")
    print(f"{'='*80}\n")

    # Query Notion Email Sequence database
    try:
        response = notion.databases.query(
            database_id=EMAIL_SEQUENCE_DB_ID,
            filter={
                "property": "Email",
                "email": {"equals": TEST_EMAIL}
            }
        )

        if not response["results"]:
            print(f"❌ ERROR: No email sequence found for {TEST_EMAIL}")
            return False

        # Get the first (and should be only) result
        sequence = response["results"][0]
        props = sequence["properties"]

        print(f"Sequence ID: {sequence['id']}")
        print(f"Campaign: {props.get('Campaign', {}).get('select', {}).get('name', 'N/A')}")
        print(f"Segment: {props.get('Segment', {}).get('select', {}).get('name', 'N/A')}")
        print(f"\n{'='*80}")
        print("EMAIL DELIVERY STATUS:")
        print(f"{'='*80}\n")

        # Check each email's sent timestamp
        results = {}
        for i in range(1, 8):
            sent_field = f"Email {i} Sent"
            email_id_field = f"Email {i} ID"

            # Get sent timestamp
            sent_data = props.get(sent_field, {}).get("date")
            sent_timestamp = sent_data.get("start") if sent_data else None

            # Get email ID (Resend ID)
            email_id = props.get(email_id_field, {}).get("rich_text")
            email_id_value = email_id[0]["plain_text"] if email_id else None

            results[i] = {
                "sent": sent_timestamp,
                "resend_id": email_id_value
            }

            # Format output
            status = "✅ SENT" if sent_timestamp else "❌ NOT SENT"
            timestamp_str = sent_timestamp if sent_timestamp else "N/A"
            resend_str = email_id_value if email_id_value else "N/A"

            print(f"Email {i}: {status}")
            print(f"  Timestamp: {timestamp_str}")
            print(f"  Resend ID: {resend_str}")
            print()

        # Summary
        sent_count = sum(1 for r in results.values() if r["sent"])
        print(f"{'='*80}")
        print(f"SUMMARY: {sent_count}/7 emails delivered")
        print(f"{'='*80}\n")

        return sent_count == 7

    except Exception as e:
        print(f"❌ ERROR querying Notion: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = verify_email_delivery()
    sys.exit(0 if success else 1)
