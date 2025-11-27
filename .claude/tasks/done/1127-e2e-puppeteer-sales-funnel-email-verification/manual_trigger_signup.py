#!/usr/bin/env python3
"""
Manually trigger the signup_handler_flow to test scheduling.
"""
import sys
sys.path.insert(0, "/Users/sangle/Dev/action/projects/perfect")

from campaigns.christmas_campaign.flows.signup_handler import signup_handler_flow
import os

os.environ["PREFECT_API_URL"] = "https://prefect.galatek.dev/api"

print("🎄 Manually triggering Christmas signup handler flow...\n")

result = signup_handler_flow(
    email="lengobaosang@gmail.com",
    first_name="Sang",
    business_name="E2E Test Salon",
    assessment_score=31,
    red_systems=3,
    orange_systems=0,
    yellow_systems=5,
    green_systems=0
)

print("\n✅ Flow completed!")
print(f"Status: {result['status']}")
print(f"Sequence ID: {result.get('sequence_id')}")
print(f"Segment: {result.get('segment')}")
print(f"Orchestrator Result: {result.get('orchestrator_result')}")
