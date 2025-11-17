"""
Deploy all Christmas Campaign flows to Prefect Server.

This script creates deployments for:
1. 7 email sender flows (one per email in the sequence)
2. 1 email sequence orchestrator flow

Deployments are created using Prefect's deployment API and
can be scheduled via the orchestrator flow.

Usage:
    python campaigns/christmas_campaign/deployments/deploy_all.py

After deployment, update .env with deployment IDs for scheduling.

Author: Christmas Campaign Team
Created: 2025-11-16
"""

import asyncio
import os
from prefect import get_client
from prefect.deployments import Deployment
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import flows
from campaigns.christmas_campaign.flows.send_email_flow import send_email_flow
from campaigns.christmas_campaign.flows.email_sequence_orchestrator import email_sequence_orchestrator


async def deploy_email_flows():
    """
    Deploy all 7 email sender flows to Prefect Server.

    Each email gets its own deployment:
    - christmas-email-1
    - christmas-email-2
    - christmas-email-3
    - christmas-email-4
    - christmas-email-5
    - christmas-email-6
    - christmas-email-7

    Returns:
        List of deployment IDs
    """
    print("🚀 Deploying 7 email sender flows...")

    deployment_ids = []

    async with get_client() as client:
        for email_number in range(1, 8):  # Emails 1-7
            deployment_name = f"christmas-email-{email_number}"

            print(f"\n📧 Deploying {deployment_name}...")

            # Create deployment
            deployment = await Deployment.build_from_flow(
                flow=send_email_flow,
                name=deployment_name,
                version=1,
                tags=["christmas-campaign", f"email-{email_number}", "nurture-sequence"],
                description=f"Send Christmas campaign email #{email_number} in nurture sequence",
                work_pool_name=None,  # Use default process work pool
                parameters={
                    "email_number": email_number
                }
            )

            deployment_id = await client.create_deployment(
                flow_id=deployment.flow_id,
                name=deployment_name,
                version=deployment.version,
                tags=deployment.tags,
                parameters=deployment.parameters,
                description=deployment.description
            )

            deployment_ids.append({
                "email_number": email_number,
                "deployment_name": deployment_name,
                "deployment_id": str(deployment_id)
            })

            print(f"✅ Deployed {deployment_name}: {deployment_id}")

    return deployment_ids


async def deploy_orchestrator_flow():
    """
    Deploy email sequence orchestrator flow to Prefect Server.

    Deployment name: christmas-email-sequence-orchestrator

    Returns:
        Deployment ID
    """
    print("\n🚀 Deploying email sequence orchestrator flow...")

    async with get_client() as client:
        deployment = await Deployment.build_from_flow(
            flow=email_sequence_orchestrator,
            name="christmas-email-sequence-orchestrator",
            version=1,
            tags=["christmas-campaign", "orchestrator", "nurture-sequence"],
            description="Orchestrate 7-email Christmas campaign nurture sequence",
            work_pool_name=None  # Use default process work pool
        )

        deployment_id = await client.create_deployment(
            flow_id=deployment.flow_id,
            name="christmas-email-sequence-orchestrator",
            version=deployment.version,
            tags=deployment.tags,
            description=deployment.description
        )

        print(f"✅ Deployed orchestrator: {deployment_id}")

    return str(deployment_id)


async def main():
    """
    Main deployment function.

    Deploys all flows and prints deployment IDs for .env configuration.
    """
    print("=" * 80)
    print("Christmas Campaign - Prefect Deployment")
    print("=" * 80)

    # Check Prefect Server connection
    try:
        async with get_client() as client:
            health = await client.api_healthcheck()
            print(f"\n✅ Connected to Prefect Server: {os.getenv('PREFECT_API_URL')}")
    except Exception as e:
        print(f"\n❌ Failed to connect to Prefect Server: {e}")
        print("Please ensure Prefect Server is running: prefect server start")
        return

    # Deploy email sender flows
    email_deployments = await deploy_email_flows()

    # Deploy orchestrator flow
    orchestrator_id = await deploy_orchestrator_flow()

    # Print summary
    print("\n" + "=" * 80)
    print("✅ Deployment Complete!")
    print("=" * 80)

    print("\n📋 Copy these deployment IDs to your .env file:\n")

    for item in email_deployments:
        env_var = f"DEPLOYMENT_ID_CHRISTMAS_EMAIL_{item['email_number']}"
        print(f"{env_var}={item['deployment_id']}")

    print(f"DEPLOYMENT_ID_CHRISTMAS_ORCHESTRATOR={orchestrator_id}")

    print("\n" + "=" * 80)
    print("📝 Next Steps:")
    print("=" * 80)
    print("1. Update .env file with the deployment IDs above")
    print("2. Test the orchestrator flow:")
    print("   python campaigns/christmas_campaign/flows/email_sequence_orchestrator.py")
    print("3. Trigger via webhook:")
    print("   POST /webhook/christmas-assessment")
    print("\n")


if __name__ == "__main__":
    asyncio.run(main())
