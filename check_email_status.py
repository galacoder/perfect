#!/usr/bin/env python3
"""Check status of all 16 emails sent to lengobaosang@gmail.com"""
import requests
import os

# Load API key
with open('.env', 'r') as f:
    for line in f:
        if line.startswith('RESEND_API_KEY='):
            api_key = line.strip().split('=', 1)[1]
            break

headers = {"Authorization": f"Bearer {api_key}"}

# All 16 email IDs
email_ids = {
    "Lead Nurture": [
        "da5120ee-3723-485e-a9fb-51ae56b8c6dc",  # Email 1
        "25ee3725-dddd-460c-bfe3-9d99500bebba",  # Email 2
        "4f325123-0b16-494c-ac63-9ee1f0050d72",  # Email 3
        "c82ff0f1-09c8-45c4-9f6a-c359883638a4",  # Email 4
        "eea5ea4b-a665-4224-830b-ccd32027c4d8",  # Email 5
        "e708b513-1a20-403f-a0c8-dde80a197a3f",  # Email 6
        "e53fd6fc-e113-45ea-938c-60b787f53f00",  # Email 7
    ],
    "No-Show Recovery": [
        "b4d9d731-8b0a-4cd7-a5cc-8697afcceabf",  # Email 1
        "e3de381b-7ca7-4228-951e-dc75d0ddc12f",  # Email 2
        "5d782b35-376e-4bd1-963c-8228b79b29cf",  # Email 3
    ],
    "Post-Call Maybe": [
        "e5a96449-cad3-49f7-9b0f-5a731ea8652f",  # Email 1
        "3ed98083-ab2d-4d4f-96ff-13724b1c3e84",  # Email 2
        "0763cd88-b137-412a-8847-5cfefedbe483",  # Email 3
    ],
    "Onboarding": [
        "eb0d2989-d423-412c-be48-a385c718cd64",  # Email 1
        "b957850a-5e5b-4f86-ac7c-342b147a893f",  # Email 2
        "081ee9f1-dcd3-4ee5-bc79-5580aabdf916",  # Email 3
    ]
}

print("=" * 60)
print("📧 EMAIL DELIVERY STATUS REPORT")
print("=" * 60)
print(f"Recipient: lengobaosang@gmail.com")
print()

total_sent = 0
total_delivered = 0
total_opened = 0

for sequence_name, ids in email_ids.items():
    print(f"\n📨 {sequence_name} ({len(ids)} emails)")
    print("-" * 40)

    for i, eid in enumerate(ids, 1):
        try:
            resp = requests.get(f"https://api.resend.com/emails/{eid}", headers=headers)
            data = resp.json()
            status = data.get("last_event", "unknown")
            subject = data.get("subject", "No subject")[:35]

            emoji = "✅" if status in ["delivered", "opened"] else "⏳" if status == "sent" else "❌"
            print(f"  {i}. {emoji} {status:10} | {subject}...")

            total_sent += 1
            if status in ["delivered", "opened"]:
                total_delivered += 1
            if status == "opened":
                total_opened += 1
        except Exception as e:
            print(f"  {i}. ❓ Error checking: {e}")

print()
print("=" * 60)
print("📊 SUMMARY")
print("=" * 60)
print(f"Total emails sent:     {total_sent}/16")
print(f"Total delivered:       {total_delivered}/16")
print(f"Total opened:          {total_opened}/16")
print(f"Delivery rate:         {total_delivered/16*100:.1f}%")
print(f"Open rate:             {total_opened/16*100:.1f}%")
