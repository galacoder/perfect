#!/usr/bin/env python3
"""
Collect Resend IDs from Prefect flow run logs for all 7 emails.
"""

import subprocess
import re
import json

PREFECT_API_URL = "https://prefect.galatek.dev/api"

# Flow run IDs for each email
FLOW_RUNS = {
    1: "d5f213f5-cd1d-4eb9-b1fc-574c3dc45776",
    2: "3ba344a7-07ab-4979-ac30-8fa2e6105616",
    3: "d1f1c895-d363-4980-80cd-74cbe30e97f6",
    4: "78f96082-330c-4b8d-ae03-ee5071bd828e",
    5: "f0350558-e351-45ba-b493-1f0799579690",
    6: "a814551a-ec2f-41c1-a453-99943dcd5d56",
    7: "1d412511-1ac0-481d-ac8f-1b079ef7da1f",
}

def get_resend_id(flow_run_id):
    """Extract Resend ID from flow run logs."""
    try:
        result = subprocess.run(
            ["prefect", "flow-run", "logs", flow_run_id],
            env={"PREFECT_API_URL": PREFECT_API_URL},
            capture_output=True,
            text=True,
            timeout=10
        )

        logs = result.stdout

        # Look for pattern: "✅ Email sent: <uuid>"
        match = re.search(r"✅ Email sent: ([a-f0-9-]+)", logs)
        if match:
            return match.group(1)

        # Check if flow crashed
        if "CRASHED" in logs or "Failed to start flow run" in logs:
            return "CRASHED"

        return None

    except Exception as e:
        print(f"Error getting logs for flow {flow_run_id}: {e}")
        return None

def main():
    print("\n" + "="*80)
    print("COLLECTING RESEND IDS FROM PREFECT FLOW LOGS")
    print("="*80 + "\n")

    results = {}

    for email_num, flow_run_id in FLOW_RUNS.items():
        print(f"Email {email_num}: {flow_run_id}", end=" ... ")
        resend_id = get_resend_id(flow_run_id)

        if resend_id == "CRASHED":
            print("❌ CRASHED")
        elif resend_id:
            print(f"✅ {resend_id}")
        else:
            print("⚠️  No Resend ID found")

        results[email_num] = {
            "flow_run_id": flow_run_id,
            "resend_id": resend_id
        }

    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80 + "\n")

    print(json.dumps(results, indent=2))

    # Count successes
    success_count = sum(1 for r in results.values() if r["resend_id"] and r["resend_id"] != "CRASHED")
    print(f"\n✅ {success_count}/7 emails sent successfully")

    return results

if __name__ == "__main__":
    main()
