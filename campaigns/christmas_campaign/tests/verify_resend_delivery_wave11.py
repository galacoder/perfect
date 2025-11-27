#!/usr/bin/env python3
"""
Wave 11 Feature 11.6: Verify All 16 Emails Delivered in Resend

Queries Resend API to verify delivery status of all 16 emails sent in Wave 11.
"""

import os
import sys
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
import httpx

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

load_dotenv()

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
TEST_EMAIL = "lengobaosang@gmail.com"

async def check_resend_emails():
    """Query Resend API for emails sent in last 30 minutes"""

    print("\n" + "=" * 80)
    print("Wave 11 Feature 11.6: Verify All 16 Emails Delivered")
    print("=" * 80)
    print(f"Resend API Key: {RESEND_API_KEY[:20]}...")
    print(f"Recipient: {TEST_EMAIL}")
    print()

    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Query emails from last 30 minutes
            response = await client.get(
                "https://api.resend.com/emails",
                headers=headers
            )

            if response.status_code == 200:
                result = response.json()
                emails = result.get("data", [])

                # Filter for our test email in last 30 minutes
                now = datetime.utcnow()
                thirty_mins_ago = now - timedelta(minutes=30)

                relevant_emails = []
                for email in emails:
                    # Parse created_at timestamp
                    created_at_str = email.get("created_at")
                    if created_at_str:
                        try:
                            created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
                            if created_at.replace(tzinfo=None) >= thirty_mins_ago:
                                # Check if sent to our test email
                                to_emails = email.get("to", [])
                                if isinstance(to_emails, list):
                                    if any(TEST_EMAIL in str(to_addr) for to_addr in to_emails):
                                        relevant_emails.append(email)
                                elif TEST_EMAIL in str(to_emails):
                                    relevant_emails.append(email)
                        except Exception as e:
                            print(f"⚠️  Error parsing timestamp {created_at_str}: {e}")

                print(f"Found {len(relevant_emails)} emails to {TEST_EMAIL} in last 30 minutes")
                print()

                # Group by status
                status_counts = {}
                for email in relevant_emails:
                    status = email.get("last_event", "unknown")
                    status_counts[status] = status_counts.get(status, 0) + 1

                    # Print each email
                    subject = email.get("subject", "No subject")
                    email_id = email.get("id", "unknown")
                    created_at = email.get("created_at", "unknown")

                    print(f"✉️  {subject[:60]}...")
                    print(f"   ID: {email_id}")
                    print(f"   Status: {status}")
                    print(f"   Created: {created_at}")
                    print()

                # Summary
                print("=" * 80)
                print("SUMMARY")
                print("=" * 80)
                print(f"Total emails found: {len(relevant_emails)}/16")
                print()

                if status_counts:
                    print("Status breakdown:")
                    for status, count in sorted(status_counts.items()):
                        print(f"  {status}: {count}")
                else:
                    print("⚠️  No emails found - may still be processing")

                print()

                if len(relevant_emails) == 16:
                    print("✅ ALL 16 EMAILS FOUND")
                    if all(email.get("last_event") in ["delivered", "opened"] for email in relevant_emails):
                        print("✅ ALL 16 EMAILS DELIVERED/OPENED")
                    else:
                        print("⚠️  Some emails not yet delivered - check statuses above")
                elif len(relevant_emails) > 0:
                    print(f"⚠️  Only {len(relevant_emails)}/16 emails found - may still be sending")
                else:
                    print("❌ NO EMAILS FOUND")
                    print("   Possible reasons:")
                    print("   1. Emails still being sent (wait a few more minutes)")
                    print("   2. Prefect flows didn't trigger properly")
                    print("   3. Check Prefect logs for errors")

                print()
                print("=" * 80)

                # Save results
                results_file = "wave11_resend_verification.json"
                with open(results_file, "w") as f:
                    json.dump({
                        "timestamp": datetime.now().isoformat(),
                        "test_email": TEST_EMAIL,
                        "total_emails": len(relevant_emails),
                        "expected_emails": 16,
                        "status_counts": status_counts,
                        "emails": relevant_emails
                    }, f, indent=2)
                print(f"Results saved to: {results_file}")

                return len(relevant_emails) == 16

            else:
                print(f"❌ Resend API error: {response.status_code}")
                print(f"   Response: {response.text}")
                return False

    except Exception as e:
        print(f"❌ Error querying Resend API: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import asyncio
    success = asyncio.run(check_resend_emails())
    sys.exit(0 if success else 1)
