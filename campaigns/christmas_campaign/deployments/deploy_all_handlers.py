"""
Deploy ALL Christmas Campaign Handler Flows to Prefect Production.

This script deploys all 4 handler flows:
1. christmas-signup-handler - Lead nurture (7 emails)
2. christmas-noshow-recovery-handler - No-show recovery (3 emails)
3. christmas-postcall-maybe-handler - Post-call follow-up (3 emails)
4. christmas-onboarding-handler - Onboarding welcome (3 emails)

Plus:
5. christmas-send-email - Email sender flow (used by all handlers)

Usage:
    PREFECT_API_URL=https://prefect.galatek.dev/api python campaigns/christmas_campaign/deployments/deploy_all_handlers.py

Author: Christmas Campaign Team
Created: 2025-11-27 (Wave 10)
"""

from campaigns.christmas_campaign.flows.send_email_flow import send_email_flow
from campaigns.christmas_campaign.flows.signup_handler import signup_handler_flow
from campaigns.christmas_campaign.flows.noshow_recovery_handler import noshow_recovery_handler_flow
from campaigns.christmas_campaign.flows.postcall_maybe_handler import postcall_maybe_handler_flow
from campaigns.christmas_campaign.flows.onboarding_handler import onboarding_handler_flow


if __name__ == "__main__":
    print("=" * 80)
    print("🚀 Deploying ALL Christmas Campaign Handler Flows to Prefect Production")
    print("=" * 80)

    deployments = []

    # ==============================================================================
    # Deploy 1: Email Sender Flow (used by all handlers)
    # ==============================================================================

    print("\n📧 [1/5] Deploying Email Sender Flow...")

    deployment_id = send_email_flow.deploy(
        name="christmas-send-email",
        work_pool_name="default",
        tags=["christmas", "email", "sender", "christmas-2025"],
        description="Send individual email from Christmas campaign sequences (triggered by handlers)",
        version="1.0.0",
        parameters={
            "email": "placeholder@example.com",
            "email_number": 1,
            "first_name": "there",
            "business_name": "your business",
            "segment": "OPTIMIZE",
            "assessment_score": 50
        }
    )

    deployments.append(("christmas-send-email", deployment_id))
    print(f"✅ Deployed: christmas-send-email/christmas-send-email")

    # ==============================================================================
    # Deploy 2: Signup Handler (Lead Nurture - 7 emails)
    # ==============================================================================

    print("\n📝 [2/5] Deploying Signup Handler Flow...")

    deployment_id = signup_handler_flow.deploy(
        name="christmas-signup-handler",
        work_pool_name="default",
        tags=["christmas", "signup", "lead-nurture", "christmas-2025"],
        description="Handle assessment completion and trigger 7-email lead nurture sequence",
        version="1.0.0",
        parameters={
            "email": "placeholder@example.com",
            "first_name": "there",
            "business_name": "your business",
            "assessment_score": 50,
            "revenue": "$10K-$20K",
            "challenge": "None"
        }
    )

    deployments.append(("christmas-signup-handler", deployment_id))
    print(f"✅ Deployed: christmas-signup-handler/christmas-signup-handler")

    # ==============================================================================
    # Deploy 3: No-Show Recovery Handler (3 emails)
    # ==============================================================================

    print("\n🚫 [3/5] Deploying No-Show Recovery Handler Flow...")

    deployment_id = noshow_recovery_handler_flow.deploy(
        name="christmas-noshow-recovery-handler",
        work_pool_name="default",
        tags=["christmas", "noshow", "recovery", "christmas-2025"],
        description="Handle Calendly no-show event and trigger 3-email recovery sequence",
        version="1.0.0",
        parameters={
            "email": "placeholder@example.com",
            "first_name": "there",
            "business_name": "your business",
            "calendly_event_uri": "https://calendly.com/events/placeholder",
            "scheduled_time": "2025-12-01T14:00:00Z",
            "event_type": "Discovery Call - $2997 Diagnostic"
        }
    )

    deployments.append(("christmas-noshow-recovery-handler", deployment_id))
    print(f"✅ Deployed: christmas-noshow-recovery-handler/christmas-noshow-recovery-handler")

    # ==============================================================================
    # Deploy 4: Post-Call Maybe Handler (3 emails)
    # ==============================================================================

    print("\n📞 [4/5] Deploying Post-Call Maybe Handler Flow...")

    deployment_id = postcall_maybe_handler_flow.deploy(
        name="christmas-postcall-maybe-handler",
        work_pool_name="default",
        tags=["christmas", "postcall", "maybe", "christmas-2025"],
        description="Handle post-call maybe prospect and trigger 3-email follow-up sequence",
        version="1.0.0",
        parameters={
            "email": "placeholder@example.com",
            "first_name": "there",
            "business_name": "your business",
            "call_date": "2025-12-01T14:30:00Z",
            "call_outcome": "Maybe",
            "follow_up_priority": "Medium"
        }
    )

    deployments.append(("christmas-postcall-maybe-handler", deployment_id))
    print(f"✅ Deployed: christmas-postcall-maybe-handler/christmas-postcall-maybe-handler")

    # ==============================================================================
    # Deploy 5: Onboarding Handler (3 emails)
    # ==============================================================================

    print("\n🎉 [5/5] Deploying Onboarding Handler Flow...")

    deployment_id = onboarding_handler_flow.deploy(
        name="christmas-onboarding-handler",
        work_pool_name="default",
        tags=["christmas", "onboarding", "welcome", "christmas-2025"],
        description="Handle new client onboarding and trigger 3-email welcome sequence",
        version="1.0.0",
        parameters={
            "email": "placeholder@example.com",
            "first_name": "there",
            "business_name": "your business",
            "payment_confirmed": True,
            "payment_amount": 2997.00,
            "payment_date": "2025-12-01T15:00:00Z",
            "docusign_completed": True,
            "package_type": "Phase 1 - Traditional Service Diagnostic"
        }
    )

    deployments.append(("christmas-onboarding-handler", deployment_id))
    print(f"✅ Deployed: christmas-onboarding-handler/christmas-onboarding-handler")

    # ==============================================================================
    # Summary
    # ==============================================================================

    print("\n" + "=" * 80)
    print("✅ ALL DEPLOYMENTS COMPLETE!")
    print("=" * 80)

    print("\n📋 Deployment Summary:\n")
    for name, deployment_id in deployments:
        print(f"   ✅ {name}")
        print(f"      Deployment ID: {deployment_id}")

    print("\n" + "=" * 80)
    print("📝 Next Steps:")
    print("=" * 80)
    print("1. ✅ All 4 handler flows deployed to Prefect Production")
    print("2. 🧪 Test each webhook endpoint:")
    print("   - POST /webhook/christmas-assessment (Lead Nurture)")
    print("   - POST /webhook/calendly-noshow (No-Show Recovery)")
    print("   - POST /webhook/postcall-maybe (Post-Call Follow-Up)")
    print("   - POST /webhook/onboarding-start (Onboarding Welcome)")
    print("3. 📧 Verify emails scheduled in Prefect dashboard")
    print("4. 📊 Check Resend dashboard for email delivery")

    print("\n✅ Deployment script complete!")
