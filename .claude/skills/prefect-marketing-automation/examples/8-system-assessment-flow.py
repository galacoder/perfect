#!/usr/bin/env python3
"""
8-System Business Assessment Lead Magnet Flow
============================================

Production-ready example demonstrating:
- Lead magnet delivery automation
- 8-System BusOS assessment scoring
- Personalized results generation
- Lead scoring and routing
- Hot lead immediate notification
- Automated nurture trigger

Based on BusOS 8-System Diagnostic Framework:
1. Strategy & Vision
2. Team & Culture
3. Revenue & Growth
4. Marketing & Sales
5. Operations & Delivery
6. Finance & Metrics
7. Technology & Systems
8. Leadership & Execution

Prerequisites:
--------------
1. Environment variables:
   - LOOPS_API_KEY
   - NOTION_API_KEY
   - DISCORD_WEBHOOK_URL

2. Notion databases:
   - Leads database with Score, Status, Priority fields

3. Loops.so templates:
   - assessment-results-low (Score < 50)
   - assessment-results-medium (Score 50-79)
   - assessment-results-high (Score ≥ 80)
   - assessment-immediate-cta

4. Prefect server running

Usage:
------
1. Deploy flow:
   python 8-system-assessment-flow.py

2. Trigger via webhook (from landing page form):
   from prefect.events import emit_event
   emit_event(
       event="lead.assessment_complete",
       resource={"prefect.resource.id": "lead.test@example.com"},
       payload={
           "email": "test@example.com",
           "first_name": "John",
           "notion_id": "page-id-here",
           "assessment_data": {
               "strategy": 8,
               "team": 6,
               "revenue": 7,
               "marketing": 5,
               "operations": 9,
               "finance": 6,
               "technology": 4,
               "leadership": 7
           }
       }
   )

3. Monitor results in Prefect UI

Author: Marketing Automation Team
Date: 2025-01-10
Version: 1.0.0
"""

import os
import httpx
from datetime import datetime
from typing import Dict, List, Optional
from prefect import flow, task, get_run_logger
from prefect.deployments import DeploymentEventTrigger
from notion_client import Client

# ============================================================================
# Configuration
# ============================================================================

LOOPS_API_KEY = os.getenv("LOOPS_API_KEY")
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
NOTION_LEADS_DB_ID = os.getenv("NOTION_LEADS_DB_ID")

# 8-System Scoring Weights (Total = 100 points)
SYSTEM_WEIGHTS = {
    "strategy": 15,      # Strategy & Vision (15%)
    "team": 12,          # Team & Culture (12%)
    "revenue": 15,       # Revenue & Growth (15%)
    "marketing": 13,     # Marketing & Sales (13%)
    "operations": 12,    # Operations & Delivery (12%)
    "finance": 10,       # Finance & Metrics (10%)
    "technology": 8,     # Technology & Systems (8%)
    "leadership": 15     # Leadership & Execution (15%)
}

# System Descriptions for Personalized Results
SYSTEM_DESCRIPTIONS = {
    "strategy": {
        "name": "Strategy & Vision",
        "low": "Your business lacks clear direction. We'll help you define a compelling vision and strategic roadmap.",
        "medium": "Your strategy is developing but needs refinement. We'll help you sharpen focus and align execution.",
        "high": "Your strategy is strong. We'll help you optimize execution and scale faster."
    },
    "team": {
        "name": "Team & Culture",
        "low": "Team challenges are holding you back. We'll help you build a high-performance culture.",
        "medium": "Your team is functional but has growth potential. We'll help you level up leadership.",
        "high": "Your team is a competitive advantage. We'll help you maintain and scale it."
    },
    "revenue": {
        "name": "Revenue & Growth",
        "low": "Revenue growth is stagnant. We'll help you unlock new growth channels and optimize pricing.",
        "medium": "You're growing but leaving money on the table. We'll help you accelerate revenue.",
        "high": "Your revenue engine is strong. We'll help you maximize profitability and valuation."
    },
    "marketing": {
        "name": "Marketing & Sales",
        "low": "Marketing isn't driving results. We'll build a systematic lead generation machine.",
        "medium": "Marketing is working but inefficient. We'll optimize conversion and reduce CAC.",
        "high": "Your marketing is dialed in. We'll help you scale while maintaining efficiency."
    },
    "operations": {
        "name": "Operations & Delivery",
        "low": "Operations are chaotic and inefficient. We'll systemize delivery and improve quality.",
        "medium": "Operations work but aren't scalable. We'll build systems for predictable delivery.",
        "high": "Your operations are efficient. We'll help you maintain quality while scaling."
    },
    "finance": {
        "name": "Finance & Metrics",
        "low": "Financial visibility is limited. We'll implement dashboards and profit optimization.",
        "medium": "You track finances but need deeper insights. We'll upgrade your metrics and forecasting.",
        "high": "Your financials are solid. We'll help you optimize capital allocation and valuation."
    },
    "technology": {
        "name": "Technology & Systems",
        "low": "Tech is holding you back. We'll modernize systems and automate manual work.",
        "medium": "Tech is adequate but inefficient. We'll streamline tools and improve integration.",
        "high": "Your tech stack is strong. We'll help you leverage data and AI for competitive advantage."
    },
    "leadership": {
        "name": "Leadership & Execution",
        "low": "Leadership gaps are limiting growth. We'll develop decision-making and accountability.",
        "medium": "Leadership is functional but reactive. We'll build proactive systems and delegation.",
        "high": "Your leadership is strong. We'll help you scale your time and amplify impact."
    }
}

# ============================================================================
# Core Scoring Logic
# ============================================================================

@task
def calculate_8_system_score(assessment_data: dict) -> Dict:
    """
    Calculate weighted score for 8-System assessment.

    Each system scored 0-10 by user, weighted to total 100 points.

    Returns:
        {
            "total_score": int (0-100),
            "system_scores": dict,
            "weakest_systems": list,
            "strongest_systems": list,
            "priority_focus": str
        }
    """
    logger = get_run_logger()

    # Normalize each system score (0-10) to weighted value
    system_scores = {}
    for system, weight in SYSTEM_WEIGHTS.items():
        user_score = assessment_data.get(system, 0)  # 0-10
        weighted_score = (user_score / 10.0) * weight
        system_scores[system] = {
            "raw": user_score,
            "weighted": weighted_score,
            "weight": weight
        }

    # Calculate total score
    total_score = int(sum(s["weighted"] for s in system_scores.values()))

    # Identify weakest systems (bottom 3)
    weakest = sorted(
        system_scores.items(),
        key=lambda x: x[1]["raw"]
    )[:3]

    # Identify strongest systems (top 3)
    strongest = sorted(
        system_scores.items(),
        key=lambda x: x[1]["raw"],
        reverse=True
    )[:3]

    # Determine priority focus (weakest system)
    priority_system = weakest[0][0]
    priority_focus = SYSTEM_DESCRIPTIONS[priority_system]["name"]

    logger.info(f"📊 8-System Score: {total_score}/100 | Priority: {priority_focus}")

    return {
        "total_score": total_score,
        "system_scores": system_scores,
        "weakest_systems": [{"system": s[0], "score": s[1]["raw"]} for s in weakest],
        "strongest_systems": [{"system": s[0], "score": s[1]["raw"]} for s in strongest],
        "priority_focus": priority_focus,
        "priority_system": priority_system
    }

@task
def generate_personalized_insights(score_data: dict) -> Dict:
    """
    Generate personalized insights based on system scores.

    Returns formatted text for email and Notion.
    """
    logger = get_run_logger()

    total_score = score_data["total_score"]
    priority_system = score_data["priority_system"]
    weakest = score_data["weakest_systems"]

    # Overall assessment
    if total_score >= 80:
        overall = "Your business is performing well across most systems. You're ready for significant scaling."
    elif total_score >= 50:
        overall = "Your business has a solid foundation but key systems need optimization for growth."
    else:
        overall = "Several critical systems need immediate attention to unlock growth potential."

    # Priority recommendation
    priority_desc = SYSTEM_DESCRIPTIONS[priority_system]
    priority_score = weakest[0]["score"]

    if priority_score <= 3:
        priority_message = priority_desc["low"]
    elif priority_score <= 7:
        priority_message = priority_desc["medium"]
    else:
        priority_message = priority_desc["high"]

    # Generate action items
    action_items = []
    for weak_system in weakest:
        system_name = weak_system["system"]
        action_items.append({
            "system": SYSTEM_DESCRIPTIONS[system_name]["name"],
            "score": weak_system["score"],
            "recommendation": SYSTEM_DESCRIPTIONS[system_name]["medium"]  # Simplified
        })

    logger.info(f"✅ Generated personalized insights for score: {total_score}")

    return {
        "overall_assessment": overall,
        "priority_message": priority_message,
        "action_items": action_items,
        "next_step": "Schedule a 15-minute strategy call to discuss your personalized growth plan."
    }

# ============================================================================
# Integration Tasks
# ============================================================================

@task(retries=3, retry_delay_seconds=60, retry_jitter_factor=0.5)
def send_assessment_results_email(
    email: str,
    first_name: str,
    total_score: int,
    insights: dict,
    score_data: dict
):
    """
    Send personalized assessment results via Loops.so.

    Email template selected based on score:
    - Low (<50): assessment-results-low
    - Medium (50-79): assessment-results-medium
    - High (≥80): assessment-results-high
    """
    logger = get_run_logger()

    # Select template based on score
    if total_score < 50:
        template_id = "assessment-results-low"
    elif total_score < 80:
        template_id = "assessment-results-medium"
    else:
        template_id = "assessment-results-high"

    # Format action items for email
    action_items_text = "\n\n".join([
        f"**{item['system']}** (Current: {item['score']}/10)\n{item['recommendation']}"
        for item in insights["action_items"]
    ])

    # Send email
    response = httpx.post(
        "https://app.loops.so/api/v1/transactional",
        headers={"Authorization": f"Bearer {LOOPS_API_KEY}"},
        json={
            "transactionalId": template_id,
            "email": email,
            "dataVariables": {
                "first_name": first_name,
                "total_score": total_score,
                "overall_assessment": insights["overall_assessment"],
                "priority_message": insights["priority_message"],
                "action_items": action_items_text,
                "next_step": insights["next_step"],
                "priority_focus": score_data["priority_focus"],
                "booking_url": "https://yourdomain.com/book-call"
            }
        },
        timeout=30
    )

    response.raise_for_status()
    logger.info(f"✅ Sent assessment results to {email} (Template: {template_id})")

@task(retries=2, retry_delay_seconds=30)
def update_lead_with_assessment(
    notion_id: str,
    total_score: int,
    priority_focus: str,
    insights: dict
):
    """
    Update lead in Notion with assessment results.
    """
    logger = get_run_logger()
    notion = Client(auth=NOTION_API_KEY)

    # Determine status and priority
    if total_score >= 80:
        status = "hot"
        priority = "high"
    elif total_score >= 50:
        status = "warm"
        priority = "medium"
    else:
        status = "cold"
        priority = "low"

    # Update Notion
    notion.pages.update(
        page_id=notion_id,
        properties={
            "Score": {"number": total_score},
            "Status": {"select": {"name": status}},
            "Priority": {"select": {"name": priority}},
            "Stage": {"select": {"name": "assessment_complete"}}
        }
    )

    logger.info(f"✅ Updated lead in Notion: {notion_id} (Score: {total_score}, Status: {status})")

@task(retries=2, retry_delay_seconds=10)
def send_hot_lead_alert(
    email: str,
    first_name: str,
    total_score: int,
    notion_id: str,
    priority_focus: str
):
    """
    Send immediate Discord alert for hot leads (score ≥ 80).

    Hot leads = ready to buy, immediate follow-up required.
    """
    logger = get_run_logger()

    payload = {
        "content": "🔥 **HOT LEAD ALERT - IMMEDIATE ACTION REQUIRED**",
        "embeds": [{
            "title": f"{first_name} - Assessment Score: {total_score}/100",
            "description": f"**Priority Focus:** {priority_focus}\n\n**Action:** Contact within 24 hours for sales call booking.",
            "color": 0xff0000,  # Red
            "timestamp": datetime.now().isoformat(),
            "fields": [
                {"name": "Email", "value": email, "inline": True},
                {"name": "Score", "value": f"{total_score}/100", "inline": True},
                {"name": "Priority", "value": "🔥 HIGH", "inline": True},
                {"name": "Notion Link", "value": f"[Open in Notion](https://notion.so/{notion_id})", "inline": False}
            ]
        }]
    }

    response = httpx.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
    response.raise_for_status()
    logger.info(f"🔥 Sent hot lead alert for {email}")

@task(retries=2, retry_delay_seconds=10)
def send_standard_notification(
    email: str,
    first_name: str,
    total_score: int,
    status: str
):
    """
    Send standard Discord notification for warm/cold leads.
    """
    logger = get_run_logger()

    color = 0xffff00 if status == "warm" else 0x808080  # Yellow for warm, gray for cold

    payload = {
        "content": f"📋 **Assessment Complete - {status.upper()}**",
        "embeds": [{
            "title": f"{first_name} - Score: {total_score}/100",
            "description": f"Lead entered nurture sequence based on score.",
            "color": color,
            "timestamp": datetime.now().isoformat(),
            "fields": [
                {"name": "Email", "value": email, "inline": True},
                {"name": "Status", "value": status.capitalize(), "inline": True}
            ]
        }]
    }

    response = httpx.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
    response.raise_for_status()
    logger.info(f"📋 Sent notification for {email} ({status})")

# ============================================================================
# Main Assessment Flow
# ============================================================================

@flow(name="8-system-assessment-delivery", log_prints=True)
def deliver_assessment_results(
    email: str,
    first_name: str,
    notion_id: str,
    assessment_data: dict
):
    """
    Complete 8-System assessment delivery flow.

    Triggered by webhook when lead completes assessment form.

    Steps:
    1. Calculate weighted score (0-100)
    2. Generate personalized insights
    3. Update lead in Notion CRM
    4. Send personalized results email
    5. Send hot lead alert if score ≥ 80
    6. Trigger nurture sequence

    Args:
        email: Lead email address
        first_name: Lead first name
        notion_id: Notion page ID for lead
        assessment_data: Dict with 8 system scores (0-10 each)
            {
                "strategy": 8,
                "team": 6,
                "revenue": 7,
                "marketing": 5,
                "operations": 9,
                "finance": 6,
                "technology": 4,
                "leadership": 7
            }
    """
    logger = get_run_logger()
    logger.info(f"🎯 Processing 8-System assessment for {email}")

    # 1. Calculate score
    score_data = calculate_8_system_score(assessment_data)
    total_score = score_data["total_score"]

    # 2. Generate personalized insights
    insights = generate_personalized_insights(score_data)

    # 3. Update lead in Notion
    update_lead_with_assessment(
        notion_id=notion_id,
        total_score=total_score,
        priority_focus=score_data["priority_focus"],
        insights=insights
    )

    # 4. Send personalized results email
    send_assessment_results_email(
        email=email,
        first_name=first_name,
        total_score=total_score,
        insights=insights,
        score_data=score_data
    )

    # 5. Send hot lead alert if score ≥ 80
    if total_score >= 80:
        send_hot_lead_alert(
            email=email,
            first_name=first_name,
            total_score=total_score,
            notion_id=notion_id,
            priority_focus=score_data["priority_focus"]
        )
    else:
        # Standard notification for warm/cold leads
        status = "warm" if total_score >= 50 else "cold"
        send_standard_notification(
            email=email,
            first_name=first_name,
            total_score=total_score,
            status=status
        )

    # 6. Trigger nurture sequence
    # (Nurture sequence will be triggered automatically by scheduled flow
    #  based on assessment_complete stage in Notion)

    logger.info(f"✅ Assessment delivery complete for {email} (Score: {total_score})")

    return {
        "status": "success",
        "email": email,
        "total_score": total_score,
        "priority_focus": score_data["priority_focus"],
        "lead_status": "hot" if total_score >= 80 else "warm" if total_score >= 50 else "cold"
    }

# ============================================================================
# Deployment Configuration
# ============================================================================

if __name__ == "__main__":
    """
    Deploy assessment delivery flow with event trigger.

    Triggered by webhook from assessment form submission.
    """
    print("🎯 Deploying 8-System Assessment Flow...")

    deliver_assessment_results.serve(
        name="8-system-assessment",
        triggers=[
            DeploymentEventTrigger(
                match={"prefect.resource.id": "lead.*"},
                expect=["lead.assessment_complete"],
                parameters={
                    "email": "{{ event.payload.email }}",
                    "first_name": "{{ event.payload.first_name }}",
                    "notion_id": "{{ event.payload.notion_id }}",
                    "assessment_data": "{{ event.payload.assessment_data }}"
                }
            )
        ]
    )

    print("✅ 8-System Assessment Flow deployed!")
    print("📊 Monitor at: http://localhost:4200")
    print("\n📝 Test Event:")
    print("""
from prefect.events import emit_event

emit_event(
    event="lead.assessment_complete",
    resource={"prefect.resource.id": "lead.test@example.com"},
    payload={
        "email": "test@example.com",
        "first_name": "John",
        "notion_id": "your-notion-page-id",
        "assessment_data": {
            "strategy": 8,
            "team": 6,
            "revenue": 7,
            "marketing": 5,
            "operations": 9,
            "finance": 6,
            "technology": 4,
            "leadership": 7
        }
    }
)
    """)
