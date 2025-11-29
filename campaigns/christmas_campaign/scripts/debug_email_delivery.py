"""
Debug Email Delivery Issues - Wave 7 Feature 7.1 & 7.2

This script investigates why production funnel signup did not trigger email delivery:
1. Queries Prefect API for flow runs associated with test email (lengobaosang@gmail.com)
2. Checks if flow runs exist and their status
3. Provides diagnostic information about webhook integration

Usage:
    PREFECT_API_URL=https://prefect.galatek.dev/api python campaigns/christmas_campaign/scripts/debug_email_delivery.py

Author: Wave 7 Email Debugging
Created: 2025-11-28
"""

import asyncio
import os
from datetime import datetime, timedelta
from prefect.client.orchestration import get_client
from dotenv import load_dotenv

load_dotenv()

TEST_EMAIL = "lengobaosang@gmail.com"
DEPLOYMENT_NAMES = [
    "christmas-signup-handler/christmas-signup-handler",
    "christmas-send-email/christmas-send-email",
    "christmas-noshow-recovery-handler/christmas-noshow-recovery-handler",
    "christmas-postcall-maybe-handler/christmas-postcall-maybe-handler",
    "christmas-onboarding-handler/christmas-onboarding-handler"
]


async def check_flow_runs_for_email():
    """
    Query Prefect API to find flow runs associated with test email.

    This checks:
    - All flow runs in the last 7 days
    - Filters by parameters containing test email
    - Shows flow run status, logs, and any errors
    """
    print("=" * 80)
    print("🔍 Debugging Email Delivery for lengobaosang@gmail.com")
    print("=" * 80)

    async with get_client() as client:
        # Check each deployment
        for deployment_name in DEPLOYMENT_NAMES:
            print(f"\n📋 Checking deployment: {deployment_name}")
            print("-" * 80)

            try:
                # Get deployment
                deployment = await client.read_deployment_by_name(deployment_name)
                print(f"✅ Deployment found: {deployment.id}")

                # Get flow runs for this deployment (last 7 days)
                since = datetime.now() - timedelta(days=7)

                from prefect.client.schemas.filters import FlowRunFilter, DeploymentFilter
                from prefect.client.schemas.sorting import FlowRunSort

                flow_runs = await client.read_flow_runs(
                    deployment_filter=DeploymentFilter(id={"any_": [deployment.id]}),
                    sort=FlowRunSort.EXPECTED_START_TIME_DESC,
                    limit=50
                )

                print(f"📊 Found {len(flow_runs)} flow runs in last 7 days")

                # Filter by test email in parameters
                matching_runs = []
                for run in flow_runs:
                    params = run.parameters or {}
                    if any(TEST_EMAIL in str(v) for v in params.values()):
                        matching_runs.append(run)

                if matching_runs:
                    print(f"✅ Found {len(matching_runs)} flow runs with test email!")

                    for run in matching_runs:
                        print(f"\n  Flow Run: {run.name}")
                        print(f"    ID: {run.id}")
                        print(f"    State: {run.state_type} - {run.state_name}")
                        print(f"    Created: {run.created}")
                        print(f"    Expected Start: {run.expected_start_time}")
                        print(f"    Start Time: {run.start_time}")
                        print(f"    End Time: {run.end_time}")
                        print(f"    Parameters: {run.parameters}")

                        # Get logs
                        logs = await client.read_logs(
                            log_filter={"flow_run_id": {"any_": [run.id]}},
                            limit=50
                        )

                        if logs:
                            print(f"    📝 Logs ({len(logs)} entries):")
                            for log in logs[-10:]:  # Show last 10 logs
                                print(f"      [{log.level}] {log.message}")
                        else:
                            print("    ⚠️  No logs found")
                else:
                    print(f"❌ No flow runs found with email: {TEST_EMAIL}")

            except Exception as e:
                print(f"❌ Error checking deployment {deployment_name}: {e}")

        print("\n" + "=" * 80)
        print("🔍 Investigation Summary")
        print("=" * 80)
        print(f"""
Checked deployments: {len(DEPLOYMENT_NAMES)}
Test email: {TEST_EMAIL}
Date range: Last 7 days

Possible causes if NO flow runs found:
1. ❌ Website is NOT calling the Prefect webhook endpoint
2. ❌ Website is calling WRONG webhook URL
3. ❌ Webhook authentication failing
4. ❌ Worker not running (flow run scheduled but never executed)
5. ❌ Deployment ID mismatch between website and actual deployment

Next steps:
1. Check website code - what URL is it calling?
2. Check Prefect deployments - get correct deployment ID
3. Check Prefect worker status - is it running?
4. Check Notion Email Sequence database - any records created?
5. Test webhook manually with curl

Manual test command:
PREFECT_API_URL=https://prefect.galatek.dev/api \\
prefect deployment run christmas-signup-handler/christmas-signup-handler \\
  --param email="{TEST_EMAIL}" \\
  --param first_name="Test" \\
  --param business_name="Test Business" \\
  --param assessment_score=50 \\
  --param red_systems=2
""")


async def check_deployments():
    """List all Christmas campaign deployments and their IDs."""
    print("\n" + "=" * 80)
    print("📦 Christmas Campaign Deployments")
    print("=" * 80)

    async with get_client() as client:
        for deployment_name in DEPLOYMENT_NAMES:
            try:
                deployment = await client.read_deployment_by_name(deployment_name)
                print(f"\n✅ {deployment.name}")
                print(f"   ID: {deployment.id}")
                print(f"   Flow: {deployment.flow_id}")
                print(f"   Work Pool: {deployment.work_pool_name}")
                print(f"   Webhook URL: https://prefect.galatek.dev/api/deployments/{deployment.id}/create_flow_run")
            except Exception as e:
                print(f"\n❌ {deployment_name}: {e}")


async def check_worker_status():
    """Check if there are active workers in the default work pool."""
    print("\n" + "=" * 80)
    print("🔧 Worker Status Check")
    print("=" * 80)

    async with get_client() as client:
        try:
            # Get default work pool
            work_pool = await client.read_work_pool("default")
            print(f"✅ Work pool 'default' found: {work_pool.id}")

            # Check for workers
            workers = await client.read_workers_for_work_pool("default")

            if workers:
                print(f"\n✅ Found {len(workers)} worker(s):")
                for worker in workers:
                    print(f"\n  Worker: {worker.name}")
                    print(f"    ID: {worker.id}")
                    print(f"    Status: {worker.status}")
                    print(f"    Last Heartbeat: {worker.last_heartbeat_time}")
            else:
                print("\n❌ NO WORKERS FOUND IN 'default' WORK POOL!")
                print("   This is likely the problem - workers must be running to execute flows.")

        except Exception as e:
            print(f"❌ Error checking workers: {e}")


if __name__ == "__main__":
    print(f"🕐 Current time: {datetime.now()}")
    print(f"🌐 Prefect API: {os.getenv('PREFECT_API_URL', 'http://127.0.0.1:4200/api')}")
    print("")

    asyncio.run(check_deployments())
    asyncio.run(check_worker_status())
    asyncio.run(check_flow_runs_for_email())
