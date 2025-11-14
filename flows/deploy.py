"""
Prefect Deployment Configuration for BusOS Email Sequence.

This script configures Prefect deployments for the three main flows:
1. signup_handler_flow - Process new signups
2. assessment_handler_flow - Process completed assessments
3. email_sequence_flow - Execute email sequence (triggered by assessment_handler)

Deployment modes:
- Local: Run on local machine (for development/testing)
- Server: Run on Prefect Cloud/Server (for production)

Usage:
    # Deploy all flows
    python flows/deploy.py

    # Deploy specific flow
    python flows/deploy.py --flow signup

Environment variables required:
- NOTION_TOKEN
- NOTION_CONTACTS_DB_ID
- NOTION_TEMPLATES_DB_ID
- RESEND_API_KEY
- TESTING_MODE (optional, default: false)
"""

from prefect.deployments import Deployment
from prefect.server.schemas.schedules import IntervalSchedule
from prefect.blocks.system import String
from datetime import timedelta
import argparse

# Import flows
from campaigns.businessx_canada_lead_nurture.flows.signup_handler import signup_handler_flow
from campaigns.businessx_canada_lead_nurture.flows.assessment_handler import assessment_handler_flow
from campaigns.businessx_canada_lead_nurture.flows.email_sequence import email_sequence_flow


def create_signup_deployment():
    """
    Create deployment for signup handler flow.
    This flow is triggered by webhook from frontend signup form.
    """
    deployment = Deployment.build_from_flow(
        flow=signup_handler_flow,
        name="signup-handler-production",
        version="1.0.0",
        description="Handle new user signups from website. Creates Notion contact and waits for assessment completion.",
        tags=["production", "webhook", "signup"],
        parameters={},  # Parameters provided at runtime via webhook
        work_queue_name="default"
    )

    return deployment


def create_assessment_deployment():
    """
    Create deployment for assessment handler flow.
    This flow is triggered by webhook when user completes BusOS assessment.
    """
    deployment = Deployment.build_from_flow(
        flow=assessment_handler_flow,
        name="assessment-handler-production",
        version="1.0.0",
        description="Process completed BusOS assessments. Updates Notion with results and triggers email sequence.",
        tags=["production", "webhook", "assessment"],
        parameters={},  # Parameters provided at runtime via webhook
        work_queue_name="default"
    )

    return deployment


def create_email_sequence_deployment():
    """
    Create deployment for email sequence flow.
    This flow is triggered internally by assessment_handler_flow.
    """
    deployment = Deployment.build_from_flow(
        flow=email_sequence_flow,
        name="email-sequence-production",
        version="1.0.0",
        description="Execute 5-email nurture sequence with segment-based routing. Triggered after assessment completion.",
        tags=["production", "email", "sequence"],
        parameters={},  # Parameters provided at runtime by assessment_handler
        work_queue_name="default"
    )

    return deployment


def deploy_all():
    """Deploy all three flows."""
    print("🚀 Deploying BusOS Email Sequence flows to Prefect...")

    # Create deployments
    signup_deployment = create_signup_deployment()
    assessment_deployment = create_assessment_deployment()
    email_sequence_deployment = create_email_sequence_deployment()

    # Apply deployments
    print("\n📦 Deploying signup-handler-production...")
    signup_deployment.apply()
    print("   ✅ Deployed")

    print("\n📦 Deploying assessment-handler-production...")
    assessment_deployment.apply()
    print("   ✅ Deployed")

    print("\n📦 Deploying email-sequence-production...")
    email_sequence_deployment.apply()
    print("   ✅ Deployed")

    print("\n🎉 All deployments complete!")
    print("\nNext steps:")
    print("1. Start Prefect agent: prefect agent start -q default")
    print("2. Trigger flows via webhook or Prefect UI")
    print("3. Monitor flow runs: prefect deployment ls")
    print("4. View logs: prefect flow-run logs <flow-run-id>")


def deploy_single(flow_name: str):
    """Deploy a single flow by name."""
    deployments = {
        "signup": create_signup_deployment,
        "assessment": create_assessment_deployment,
        "email": create_email_sequence_deployment
    }

    if flow_name not in deployments:
        print(f"❌ Unknown flow: {flow_name}")
        print(f"   Available flows: {', '.join(deployments.keys())}")
        return

    print(f"🚀 Deploying {flow_name} flow...")
    deployment = deployments[flow_name]()
    deployment.apply()
    print(f"   ✅ Deployed {deployment.name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deploy Prefect flows")
    parser.add_argument(
        "--flow",
        choices=["signup", "assessment", "email", "all"],
        default="all",
        help="Which flow to deploy (default: all)"
    )

    args = parser.parse_args()

    if args.flow == "all":
        deploy_all()
    else:
        deploy_single(args.flow)
