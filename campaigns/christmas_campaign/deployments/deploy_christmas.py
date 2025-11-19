"""
Deploy Christmas Campaign Flows to Prefect.

This script creates a Prefect Deployment for the send_email_flow, allowing it to be
triggered programmatically with scheduled execution.

The deployment is NOT scheduled via cron - instead, it's triggered on-demand by the
signup_handler_flow, which schedules 7 separate flow runs with calculated delays.

Usage:
    python campaigns/christmas_campaign/deployments/deploy_christmas.py

After deployment, the signup_handler can schedule emails like this:
    from prefect.deployments import run_deployment

    run_deployment(
        name="christmas-send-email/christmas-send-email",
        parameters={
            "email": "customer@example.com",
            "email_number": 1,
            "first_name": "John",
            ...
        },
        scheduled_time=datetime.now() + timedelta(hours=24)  # Schedule for 24h later
    )

Author: Christmas Campaign Team
Created: 2025-11-19 (Wave 2)
"""

from prefect import deploy
from campaigns.christmas_campaign.flows.send_email_flow import send_email_flow


if __name__ == "__main__":
    print("🚀 Deploying Christmas Campaign Email Flow to Prefect...")

    # Deploy send_email_flow
    deployment = deploy(
        send_email_flow,
        name="christmas-send-email",
        work_pool_name="default-pool",
        cron=None,  # No cron schedule - triggered programmatically
        tags=["christmas", "email", "nurture", "christmas-2025"],
        description="Send individual email from Christmas campaign 7-email sequence (triggered by signup_handler)",
        version="1.0.0",
        parameters={
            # Default parameters (will be overridden at runtime)
            "email": "placeholder@example.com",
            "email_number": 1,
            "first_name": "there",
            "business_name": "your business",
            "segment": "OPTIMIZE",
            "assessment_score": 50
        }
    )

    print(f"\n✅ Deployment created successfully!")
    print(f"   Deployment Name: christmas-send-email/christmas-send-email")
    print(f"   Deployment ID: {deployment.id}")
    print(f"   Work Pool: default-pool")
    print(f"   Tags: christmas, email, nurture, christmas-2025")
    print(f"\n📋 Deployment Details:")
    print(f"   - Flow: send_email_flow")
    print(f"   - Trigger: Programmatic (via signup_handler)")
    print(f"   - Schedule: On-demand with delays (not cron)")
    print(f"   - Retries: 1 retry with 5-minute delay")

    print(f"\n🧪 To test manually:")
    print(f"   prefect deployment run 'christmas-send-email/christmas-send-email' \\")
    print(f"     --param email=test@example.com \\")
    print(f"     --param email_number=1 \\")
    print(f"     --param first_name=Test \\")
    print(f"     --param business_name='Test Corp' \\")
    print(f"     --param segment=OPTIMIZE \\")
    print(f"     --param assessment_score=50")

    print(f"\n📝 Next Steps:")
    print(f"   1. Update signup_handler.py to schedule 7 emails via this deployment")
    print(f"   2. Test the complete flow: webhook → signup → 7 scheduled emails")
    print(f"   3. Verify Notion Email Sequence DB updates after each send")

    print(f"\n✅ Deployment complete!")
