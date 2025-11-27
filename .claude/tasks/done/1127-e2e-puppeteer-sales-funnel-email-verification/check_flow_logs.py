#!/usr/bin/env python3
"""
Get logs from the most recent christmas-signup-handler flow run.
"""
import asyncio
from prefect.client.orchestration import get_client
import os

os.environ["PREFECT_API_URL"] = "https://prefect.galatek.dev/api"


async def get_flow_logs():
    async with get_client() as client:
        # Get the flow
        flows = await client.read_flows(limit=50)
        signup_flow = None
        for flow in flows:
            if flow.name == "christmas-signup-handler":
                signup_flow = flow
                break

        if not signup_flow:
            print("❌ Flow not found")
            return

        # Get recent flow runs
        from prefect.client.schemas.filters import FlowFilter

        flow_runs = await client.read_flow_runs(
            flow_filter=FlowFilter(id={"any_": [signup_flow.id]}),
            limit=5,
            sort="START_TIME_DESC"
        )

        # Find the one for lengobaosang@gmail.com
        target_run = None
        for run in flow_runs:
            if run.parameters and run.parameters.get("email") == "lengobaosang@gmail.com":
                target_run = run
                break

        if not target_run:
            print("❌ No flow run found for lengobaosang@gmail.com")
            return

        print(f"📋 Flow Run: {target_run.name}")
        print(f"   ID: {target_run.id}")
        print(f"   State: {target_run.state.type if target_run.state else 'Unknown'}")
        print(f"   Started: {target_run.start_time}")
        print(f"   Parameters: {target_run.parameters}\n")

        # Get logs for this flow run
        print("📝 Flow Run Logs:\n")
        print("=" * 80)

        from prefect.client.schemas.filters import LogFilter

        logs = await client.read_logs(
            log_filter=LogFilter(flow_run_id={"any_": [target_run.id]}),
            limit=200
        )

        for log in logs:
            timestamp = log.timestamp.strftime("%H:%M:%S")
            level = log.level
            message = log.message
            print(f"[{timestamp}] {level:8} | {message}")

        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(get_flow_logs())
