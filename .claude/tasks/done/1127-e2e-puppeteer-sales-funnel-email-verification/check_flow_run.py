#!/usr/bin/env python3
"""
Check for recent christmas-signup-handler flow runs via Prefect API.
"""
import asyncio
from prefect.client.orchestration import get_client
from datetime import datetime, timezone, timedelta


async def check_flow_runs():
    """Query Prefect API for recent christmas-signup-handler flow runs."""
    async with get_client() as client:
        # Get the flow
        flows = await client.read_flows(limit=50)
        signup_flow = None
        for flow in flows:
            if flow.name == "christmas-signup-handler":
                signup_flow = flow
                break

        if not signup_flow:
            print("❌ Flow 'christmas-signup-handler' not found")
            return None

        print(f"✅ Found flow: {signup_flow.name} (ID: {signup_flow.id})")

        # Get recent flow runs for this flow
        from prefect.client.schemas.filters import FlowFilter, FlowRunFilter

        flow_runs = await client.read_flow_runs(
            flow_filter=FlowFilter(id={"any_": [signup_flow.id]}),
            limit=5,
            sort="START_TIME_DESC"
        )

        print(f"\n📊 Found {len(flow_runs)} recent flow runs:\n")

        for run in flow_runs:
            print(f"  Flow Run: {run.name}")
            print(f"  ID: {run.id}")
            print(f"  State: {run.state.type if run.state else 'Unknown'}")
            print(f"  Started: {run.start_time}")
            print(f"  Parameters: {run.parameters}")
            print()

        # Check if any runs are for lengobaosang@gmail.com
        target_email = "lengobaosang@gmail.com"
        matching_runs = [
            run for run in flow_runs
            if run.parameters and run.parameters.get("email") == target_email
        ]

        if matching_runs:
            print(f"✅ Found {len(matching_runs)} flow run(s) for {target_email}")
            return matching_runs[0]
        else:
            print(f"❌ No flow runs found for {target_email}")
            return None


if __name__ == "__main__":
    import os
    os.environ["PREFECT_API_URL"] = "https://prefect.galatek.dev/api"

    result = asyncio.run(check_flow_runs())

    if result:
        print(f"\n🎯 Most recent flow run for lengobaosang@gmail.com:")
        print(f"   ID: {result.id}")
        print(f"   State: {result.state.type if result.state else 'Unknown'}")
        print(f"   Started: {result.start_time}")
