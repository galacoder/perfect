#!/usr/bin/env python3
"""
Query Notion Email Sequence database for lengobaosang@gmail.com.
"""
from notion_client import Client
from dotenv import load_dotenv
import os
import json

load_dotenv("/Users/sangle/Dev/action/projects/perfect/.env")

notion = Client(auth=os.getenv("NOTION_TOKEN"))
SEQUENCE_DB_ID = "576de1aa-6064-4201-a5e6-623b7f2be79a"

print(f"🔍 Querying Email Sequence database for lengobaosang@gmail.com...\n")

response = notion.databases.query(
    database_id=SEQUENCE_DB_ID,
    filter={
        "property": "Email",
        "email": {"equals": "lengobaosang@gmail.com"}
    }
)

if not response["results"]:
    print("❌ No email sequence record found for lengobaosang@gmail.com")
    exit(1)

print(f"✅ Found {len(response['results'])} email sequence record(s)\n")

for result in response["results"]:
    props = result["properties"]

    print(f"📧 Email Sequence Record:")
    print(f"   ID: {result['id']}")
    print(f"   Email: {props.get('Email', {}).get('email', 'N/A')}")
    print(f"   First Name: {props.get('First Name', {}).get('title', [{}])[0].get('text', {}).get('content', 'N/A')}")
    print(f"   Business: {props.get('Business', {}).get('rich_text', [{}])[0].get('text', {}).get('content', 'N/A')}")
    print(f"   Campaign: {props.get('Campaign', {}).get('select', {}).get('name', 'N/A')}")
    print(f"   Segment: {props.get('Segment', {}).get('select', {}).get('name', 'N/A')}")
    print(f"   Assessment Score: {props.get('Assessment Score', {}).get('number', 'N/A')}")
    print(f"   Red Systems: {props.get('Red Systems', {}).get('number', 'N/A')}")
    print(f"   Created: {result.get('created_time', 'N/A')}")
    print()

    # Check email sent statuses
    print("📬 Email Delivery Status:")
    for i in range(1, 8):
        email_sent = props.get(f"Email {i} Sent", {}).get("date", {})
        if email_sent:
            start_date = email_sent.get("start", "Scheduled")
            print(f"   Email {i}: ✅ Sent at {start_date}")
        else:
            print(f"   Email {i}: ⏸️ Not yet sent")
    print()

    # Check for scheduled flow run IDs
    print("🚀 Scheduled Prefect Flow Runs:")
    for i in range(1, 8):
        flow_run_prop = props.get(f"Email {i} Flow Run ID", {}).get("rich_text", [])
        if flow_run_prop:
            flow_run_id = flow_run_prop[0].get("text", {}).get("content", "N/A")
            print(f"   Email {i}: {flow_run_id}")
        else:
            print(f"   Email {i}: Not scheduled")

print("\n✅ Verification complete!")
