"""
Deployment utilities for Christmas Campaign email automation.

This module provides utilities for:
1. Scheduling email flows with calculated delays
2. Creating Prefect deployments programmatically
3. Managing deployment lifecycle

Author: Christmas Campaign Team
Created: 2025-11-16
"""

import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from prefect import get_client
from prefect.client.schemas.schedules import IntervalSchedule
import asyncio


async def schedule_email_flow(
    flow_name: str,
    email_number: int,
    contact_data: Dict[str, Any],
    delay_hours: int,
    testing_mode: bool = False
) -> str:
    """
    Schedule an email flow to run after a specified delay.

    Args:
        flow_name: Name of the flow deployment (e.g., "christmas-email-1")
        email_number: Email number in sequence (1-7)
        contact_data: Contact information and metadata
        delay_hours: Hours to delay before sending (production mode)
        testing_mode: If True, use minutes instead of hours for delays

    Returns:
        Flow run ID

    Raises:
        ValueError: If deployment ID not found in environment
        Exception: If scheduling fails
    """
    # Convert hours to minutes in testing mode
    if testing_mode:
        delay_minutes = delay_hours  # In testing, delay_hours is actually delay_minutes
        scheduled_start = datetime.now() + timedelta(minutes=delay_minutes)
    else:
        scheduled_start = datetime.now() + timedelta(hours=delay_hours)

    # Get deployment ID from environment
    deployment_key = f"DEPLOYMENT_ID_{flow_name.upper().replace('-', '_')}"
    deployment_id = os.getenv(deployment_key)

    if not deployment_id:
        raise ValueError(
            f"Deployment ID not found for {flow_name}. "
            f"Please set {deployment_key} in .env file."
        )

    # Schedule flow run
    async with get_client() as client:
        flow_run = await client.create_flow_run_from_deployment(
            deployment_id=deployment_id,
            parameters={
                "email": contact_data.get("email"),
                "first_name": contact_data.get("first_name", "there"),
                "business_name": contact_data.get("business_name", "your business"),
                "segment": contact_data.get("segment", "OPTIMIZE"),
                "email_number": email_number
            },
            scheduled_start_time=scheduled_start
        )

    return flow_run.id


async def cancel_scheduled_flow(flow_run_id: str) -> bool:
    """
    Cancel a scheduled flow run (used when contact unsubscribes).

    Args:
        flow_run_id: ID of the flow run to cancel

    Returns:
        True if canceled successfully, False otherwise
    """
    try:
        async with get_client() as client:
            await client.set_flow_run_state(
                flow_run_id=flow_run_id,
                state_type="CANCELLED"
            )
        return True
    except Exception as e:
        print(f"Failed to cancel flow run {flow_run_id}: {e}")
        return False


def calculate_delay_hours(
    email_number: int,
    testing_mode: bool = False
) -> int:
    """
    Calculate cumulative delay hours for each email in the sequence.

    Email timing (production):
    - Email 1: Immediate (0 hours)
    - Email 2: Day 2 (+48 hours)
    - Email 3: Day 3 (+24 hours = 72 hours total)
    - Email 4: Day 4 (+24 hours = 96 hours total)
    - Email 5: Day 6 (+48 hours = 144 hours total)
    - Email 6: Day 8 (+48 hours = 192 hours total)
    - Email 7: Day 10 (+48 hours = 240 hours total)

    Email timing (testing - minutes instead of hours):
    - Email 1: Immediate (0 min)
    - Email 2: +2 min
    - Email 3: +3 min (5 min total)
    - Email 4: +4 min (9 min total)
    - Email 5: +5 min (14 min total)
    - Email 6: +6 min (20 min total)
    - Email 7: +7 min (27 min total)

    Args:
        email_number: Email number in sequence (1-7)
        testing_mode: If True, return minutes instead of hours

    Returns:
        Cumulative delay in hours (or minutes if testing_mode=True)
    """
    if testing_mode:
        # Testing mode: cumulative delays in minutes
        delays = {
            1: 0,    # Immediate
            2: 2,    # +2 min
            3: 5,    # +3 min (total: 5)
            4: 9,    # +4 min (total: 9)
            5: 14,   # +5 min (total: 14)
            6: 20,   # +6 min (total: 20)
            7: 27    # +7 min (total: 27)
        }
    else:
        # Production mode: cumulative delays in hours
        delays = {
            1: 0,      # Immediate
            2: 48,     # Day 2 (+48h)
            3: 72,     # Day 3 (+24h)
            4: 96,     # Day 4 (+24h)
            5: 144,    # Day 6 (+48h)
            6: 192,    # Day 8 (+48h)
            7: 240     # Day 10 (+48h)
        }

    return delays.get(email_number, 0)


async def get_deployment_info(deployment_name: str) -> Optional[Dict[str, Any]]:
    """
    Get deployment information by name.

    Args:
        deployment_name: Name of the deployment

    Returns:
        Deployment information dict or None if not found
    """
    try:
        async with get_client() as client:
            deployments = await client.read_deployments(
                deployment_filter={"name": {"any_": [deployment_name]}}
            )
            if deployments:
                return {
                    "id": str(deployments[0].id),
                    "name": deployments[0].name,
                    "flow_name": deployments[0].flow_name,
                    "is_schedule_active": deployments[0].is_schedule_active
                }
        return None
    except Exception as e:
        print(f"Failed to get deployment info for {deployment_name}: {e}")
        return None


async def list_all_deployments() -> list:
    """
    List all deployments in the Prefect server.

    Returns:
        List of deployment dicts with id, name, flow_name
    """
    try:
        async with get_client() as client:
            deployments = await client.read_deployments()
            return [
                {
                    "id": str(d.id),
                    "name": d.name,
                    "flow_name": d.flow_name,
                    "is_schedule_active": d.is_schedule_active
                }
                for d in deployments
            ]
    except Exception as e:
        print(f"Failed to list deployments: {e}")
        return []


# Convenience function for synchronous usage
def schedule_email_sync(
    flow_name: str,
    email_number: int,
    contact_data: Dict[str, Any],
    delay_hours: int,
    testing_mode: bool = False
) -> str:
    """
    Synchronous wrapper for schedule_email_flow.

    Use this when calling from non-async code.
    """
    return asyncio.run(
        schedule_email_flow(
            flow_name=flow_name,
            email_number=email_number,
            contact_data=contact_data,
            delay_hours=delay_hours,
            testing_mode=testing_mode
        )
    )
