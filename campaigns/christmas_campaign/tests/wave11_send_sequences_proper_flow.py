#!/usr/bin/env python3
"""
Wave 11 Features 11.2-11.5: Send Updated Email Sequences via PROPER Flow

This script sends all 4 email sequences (16 emails total) using the CORRECT approach:
✅ Triggers webhook → FastAPI → Prefect production
✅ Templates fetched from Notion database
✅ NO hardcoded templates

Per user feedback: Wave 9 was WRONG because it used hardcoded templates.
This test uses the production flow with updated Notion templates.
"""

import asyncio
import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv
import httpx

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

load_dotenv()

TEST_EMAIL = "lengobaosang@gmail.com"
FASTAPI_URL = "http://localhost:8000"
PREFECT_API_URL = os.getenv("PREFECT_API_URL", "https://prefect.galatek.dev/api")

async def send_lead_nurture_sequence():
    """
    Feature 11.2: Send updated Lead Nurture sequence (7 emails)
    Triggers via christmas-signup-handler webhook
    """
    print("\n" + "=" * 80)
    print("Feature 11.2: Lead Nurture Sequence (7 emails)")
    print("=" * 80)
    print(f"Method: POST to {FASTAPI_URL}/webhook/christmas-signup")
    print(f"Test email: {TEST_EMAIL}")
    print()

    # Trigger signup webhook with realistic business data
    # Schema: ChristmasSignupRequest (assessment_score must be 0-100)
    payload = {
        "email": TEST_EMAIL,
        "first_name": "Lệ Ngọc",
        "business_name": "Bảo Sang Beauty Salon",
        "assessment_score": 52,  # CRITICAL segment (52% score = 2 red systems)
        "red_systems": 2,
        "orange_systems": 1,
        "yellow_systems": 2,
        "green_systems": 3,
        "gps_score": 45,
        "money_score": 38,
        "weakest_system_1": "Team & Hiring",
        "weakest_system_2": "Customer Experience",
        "revenue_leak_total": 17000
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{FASTAPI_URL}/webhook/christmas-signup",
                json=payload
            )

            if response.status_code == 200:
                result = response.json()
                flow_run_id = result.get("flow_run_id")
                print(f"✅ Webhook accepted: {response.status_code}")
                print(f"   Flow run ID: {flow_run_id}")
                print(f"   Segment: {result.get('segment')}")
                print(f"   Emails scheduled: 7 (TESTING_MODE = 1 min intervals)")
                print()
                return {"success": True, "flow_run_id": flow_run_id, "emails": 7}
            else:
                print(f"❌ Webhook failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return {"success": False, "error": response.text}

    except Exception as e:
        print(f"❌ Error triggering webhook: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}


async def send_noshow_recovery_sequence():
    """
    Feature 11.3: Send updated No-Show Recovery sequence (3 emails)
    Triggers via calendly-no-show webhook
    """
    print("\n" + "=" * 80)
    print("Feature 11.3: No-Show Recovery Sequence (3 emails)")
    print("=" * 80)
    print(f"Method: POST to {FASTAPI_URL}/webhook/calendly-noshow")
    print(f"Test email: {TEST_EMAIL}")
    print()

    # Schema: CalendlyNoShowRequest
    payload = {
        "email": TEST_EMAIL,
        "first_name": "Lệ Ngọc",
        "business_name": "Bảo Sang Beauty Salon",
        "calendly_event_uri": "https://calendly.com/test-event/no-show-test-wave11",
        "scheduled_time": datetime.now().isoformat(),
        "event_type": "Discovery Call - $2997 Diagnostic"
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{FASTAPI_URL}/webhook/calendly-noshow",
                json=payload
            )

            if response.status_code == 200:
                result = response.json()
                flow_run_id = result.get("flow_run_id")
                print(f"✅ Webhook accepted: {response.status_code}")
                print(f"   Flow run ID: {flow_run_id}")
                print(f"   Emails scheduled: 3 (TESTING_MODE = 1 min intervals)")
                print()
                return {"success": True, "flow_run_id": flow_run_id, "emails": 3}
            else:
                print(f"❌ Webhook failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return {"success": False, "error": response.text}

    except Exception as e:
        print(f"❌ Error triggering webhook: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}


async def send_postcall_maybe_sequence():
    """
    Feature 11.4: Send updated Post-Call Maybe sequence (3 emails)
    Triggers via calendly-postcall-maybe webhook
    """
    print("\n" + "=" * 80)
    print("Feature 11.4: Post-Call Maybe Sequence (3 emails)")
    print("=" * 80)
    print(f"Method: POST to {FASTAPI_URL}/webhook/postcall-maybe")
    print(f"Test email: {TEST_EMAIL}")
    print()

    # Schema: PostCallMaybeRequest
    payload = {
        "email": TEST_EMAIL,
        "first_name": "Lệ Ngọc",
        "business_name": "Bảo Sang Beauty Salon",
        "call_date": datetime.now().isoformat(),
        "call_outcome": "Maybe",
        "call_notes": "Interested but concerned about timing and budget",
        "objections": ["Price", "Timing"],
        "follow_up_priority": "High"
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{FASTAPI_URL}/webhook/postcall-maybe",
                json=payload
            )

            if response.status_code == 200:
                result = response.json()
                flow_run_id = result.get("flow_run_id")
                print(f"✅ Webhook accepted: {response.status_code}")
                print(f"   Flow run ID: {flow_run_id}")
                print(f"   Emails scheduled: 3 (TESTING_MODE = 1 min intervals)")
                print()
                return {"success": True, "flow_run_id": flow_run_id, "emails": 3}
            else:
                print(f"❌ Webhook failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return {"success": False, "error": response.text}

    except Exception as e:
        print(f"❌ Error triggering webhook: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}


async def send_onboarding_sequence():
    """
    Feature 11.5: Send updated Onboarding sequence (3 emails)
    Triggers via calendly-booked webhook
    """
    print("\n" + "=" * 80)
    print("Feature 11.5: Onboarding Sequence (3 emails)")
    print("=" * 80)
    print(f"Method: POST to {FASTAPI_URL}/webhook/onboarding-start")
    print(f"Test email: {TEST_EMAIL}")
    print()

    # Schema: OnboardingStartRequest
    payload = {
        "email": TEST_EMAIL,
        "first_name": "Lệ Ngọc",
        "business_name": "Bảo Sang Beauty Salon",
        "payment_confirmed": True,
        "payment_amount": 2997.00,
        "payment_date": datetime.now().isoformat(),
        "docusign_completed": True,
        "start_date": datetime.now().isoformat()
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{FASTAPI_URL}/webhook/onboarding-start",
                json=payload
            )

            if response.status_code == 200:
                result = response.json()
                flow_run_id = result.get("flow_run_id")
                print(f"✅ Webhook accepted: {response.status_code}")
                print(f"   Flow run ID: {flow_run_id}")
                print(f"   Emails scheduled: 3 (TESTING_MODE = 1 min intervals)")
                print()
                return {"success": True, "flow_run_id": flow_run_id, "emails": 3}
            else:
                print(f"❌ Webhook failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return {"success": False, "error": response.text}

    except Exception as e:
        print(f"❌ Error triggering webhook: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}


async def main():
    """Run all 4 email sequences"""
    print("\n" + "=" * 80)
    print("Wave 11 - Send Updated Email Sequences via PROPER Flow")
    print("=" * 80)
    print(f"Test email: {TEST_EMAIL}")
    print(f"FastAPI server: {FASTAPI_URL}")
    print(f"Prefect API: {PREFECT_API_URL}")
    print(f"Testing mode: true (1 min intervals)")
    print()
    print("🔴 CRITICAL: Using PROPER flow (webhook → Prefect → Notion templates)")
    print("❌ NOT using hardcoded templates like Wave 9")
    print()

    results = {}

    # Feature 11.2: Lead Nurture (7 emails)
    results["lead_nurture"] = await send_lead_nurture_sequence()
    await asyncio.sleep(2)  # Brief pause between sequences

    # Feature 11.3: No-Show Recovery (3 emails)
    results["noshow_recovery"] = await send_noshow_recovery_sequence()
    await asyncio.sleep(2)

    # Feature 11.4: Post-Call Maybe (3 emails)
    results["postcall_maybe"] = await send_postcall_maybe_sequence()
    await asyncio.sleep(2)

    # Feature 11.5: Onboarding (3 emails)
    results["onboarding"] = await send_onboarding_sequence()

    # Summary
    print("\n" + "=" * 80)
    print("WAVE 11 SUMMARY")
    print("=" * 80)

    total_emails = 0
    successful_sequences = 0

    for sequence_name, result in results.items():
        if result.get("success"):
            successful_sequences += 1
            total_emails += result.get("emails", 0)
            print(f"✅ {sequence_name}: {result.get('emails')} emails scheduled")
            print(f"   Flow run ID: {result.get('flow_run_id')}")
        else:
            print(f"❌ {sequence_name}: FAILED")
            print(f"   Error: {result.get('error')}")

    print()
    print(f"Total sequences triggered: {successful_sequences}/4")
    print(f"Total emails scheduled: {total_emails}/16")
    print()

    if successful_sequences == 4:
        print("✅ ALL SEQUENCES TRIGGERED SUCCESSFULLY")
        print()
        print("Next steps:")
        print("1. Wait ~12 minutes for all emails to send (TESTING_MODE)")
        print("2. Check Resend dashboard for delivery status")
        print("3. Check inbox at lengobaosang@gmail.com")
        print("4. Verify real testimonials appear in email content")
    else:
        print(f"⚠️  {4 - successful_sequences} sequences failed - check errors above")

    print()
    print("=" * 80)

    # Save results
    results_file = "wave11_test_results.json"
    with open(results_file, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "test_email": TEST_EMAIL,
            "results": results,
            "summary": {
                "successful_sequences": successful_sequences,
                "total_emails": total_emails
            }
        }, f, indent=2)
    print(f"Results saved to: {results_file}")


if __name__ == "__main__":
    asyncio.run(main())
