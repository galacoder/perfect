"""
Segment classification and routing logic for Christmas Campaign.

This module provides Prefect tasks for:
- Classifying contacts into segments (CRITICAL/URGENT/OPTIMIZE)
- Determining email template variants
- Routing logic for personalized content

Author: Christmas Campaign Team
Created: 2025-11-16
"""

from typing import Literal, Dict, Any


def classify_segment(
    red_systems: int = 0,
    orange_systems: int = 0,
    yellow_systems: int = 0,
    green_systems: int = 0
) -> Literal["CRITICAL", "URGENT", "OPTIMIZE"]:
    """
    Classify contact into segment based on BusOS assessment results.

    Segment Classification Rules:
    - CRITICAL: 2+ red systems (business in crisis)
    - URGENT: 1 red system OR 2+ orange systems (business struggling)
    - OPTIMIZE: All others (business functional but can improve)

    Args:
        red_systems: Number of red (broken) systems
        orange_systems: Number of orange (struggling) systems
        yellow_systems: Number of yellow (functional) systems
        green_systems: Number of green (optimized) systems

    Returns:
        Segment classification (CRITICAL/URGENT/OPTIMIZE)

    Example:
        segment = classify_segment(red_systems=3, orange_systems=2, yellow_systems=2, green_systems=1)
        # Returns: "CRITICAL"

        segment = classify_segment(red_systems=1, orange_systems=1, yellow_systems=3, green_systems=3)
        # Returns: "URGENT"

        segment = classify_segment(red_systems=0, orange_systems=1, yellow_systems=3, green_systems=4)
        # Returns: "OPTIMIZE"
    """
    # CRITICAL: 2+ red systems
    if red_systems >= 2:
        return "CRITICAL"

    # URGENT: 1 red OR 2+ orange
    if red_systems == 1 or orange_systems >= 2:
        return "URGENT"

    # OPTIMIZE: Everyone else
    return "OPTIMIZE"


def get_email_template_id(
    email_number: int,
    segment: Literal["CRITICAL", "URGENT", "OPTIMIZE"]
) -> str:
    """
    Get template ID for a specific email and segment combination.

    Email Template Mapping (Christmas 2025 - 5-Day Sequence):
    - Email 1: "5-Day E1: Your Assessment Results + Dec 5 Deadline (GIVE)"
    - Email 2: "5-Day E2: The $500K Mistake + BusOS Framework (GIVE)"
    - Email 3: "5-Day E3: Van Tiny Case Study + Soft ASK"
    - Email 4: "5-Day E4: Value Stack + Medium ASK"
    - Email 5: "5-Day E5: Final Call - HARD ASK (Last Email)"

    Note: The Christmas 2025 campaign now uses a 5-day sequence (not 7-day).
    The segment parameter is kept for compatibility but not used for template selection.
    Website sends Email 1, Prefect sends Emails 2-5.

    Args:
        email_number: Email number in sequence (1-5)
        segment: Contact segment (not used for Christmas templates)

    Returns:
        Template ID to use (exact Notion template name)

    Example:
        template_id = get_email_template_id(email_number=1, segment="CRITICAL")
        # Returns: "5-Day E1: Your Assessment Results + Dec 5 Deadline (GIVE)"

        template_id = get_email_template_id(email_number=2, segment="CRITICAL")
        # Returns: "5-Day E2: The $500K Mistake + BusOS Framework (GIVE)"
    """
    # Christmas 2025: 5-Day Sequence templates (exact Notion names)
    templates = {
        1: "5-Day E1: Your Assessment Results + Dec 5 Deadline (GIVE)",
        2: "5-Day E2: The $500K Mistake + BusOS Framework (GIVE)",
        3: "5-Day E3: Van Tiny Case Study + Soft ASK",
        4: "5-Day E4: Value Stack + Medium ASK",
        5: "5-Day E5: Final Call - HARD ASK (Last Email)"
    }

    if email_number in templates:
        return templates[email_number]
    else:
        # Fallback to Email 1
        return templates[1]


def should_send_discord_alert(segment: Literal["CRITICAL", "URGENT", "OPTIMIZE"]) -> bool:
    """
    Determine if Discord alert should be sent for hot leads.

    Discord alerts are sent for CRITICAL segment only (2+ red systems).

    Args:
        segment: Contact segment

    Returns:
        True if Discord alert should be sent, False otherwise

    Example:
        if should_send_discord_alert("CRITICAL"):
            send_discord_notification(...)
    """
    return segment == "CRITICAL"


def get_segment_priority(segment: Literal["CRITICAL", "URGENT", "OPTIMIZE"]) -> int:
    """
    Get numeric priority for segment (for sorting/filtering).

    Priority levels:
    - CRITICAL: 1 (highest priority)
    - URGENT: 2 (medium priority)
    - OPTIMIZE: 3 (lowest priority)

    Args:
        segment: Contact segment

    Returns:
        Priority number (1-3)

    Example:
        priority = get_segment_priority("CRITICAL")
        # Returns: 1
    """
    priorities = {
        "CRITICAL": 1,
        "URGENT": 2,
        "OPTIMIZE": 3
    }
    return priorities.get(segment, 3)


def get_segment_description(segment: Literal["CRITICAL", "URGENT", "OPTIMIZE"]) -> Dict[str, str]:
    """
    Get human-readable description and characteristics of a segment.

    Args:
        segment: Contact segment

    Returns:
        Dictionary with 'name', 'description', 'characteristics', 'action_needed'

    Example:
        info = get_segment_description("CRITICAL")
        print(info["description"])
        # "Business in crisis mode with 2+ broken systems"
    """
    descriptions = {
        "CRITICAL": {
            "name": "Critical",
            "description": "Business in crisis mode with 2+ broken systems",
            "characteristics": "High pain, immediate need, ready to invest",
            "action_needed": "Immediate outreach, personalized support, fast-track diagnostic call"
        },
        "URGENT": {
            "name": "Urgent",
            "description": "Business struggling with 1+ critical issues",
            "characteristics": "Moderate pain, aware of problems, evaluating solutions",
            "action_needed": "Regular outreach, case studies, clear ROI demonstration"
        },
        "OPTIMIZE": {
            "name": "Optimize",
            "description": "Business functional but seeking improvement",
            "characteristics": "Low pain, growth-focused, longer decision cycle",
            "action_needed": "Educational content, best practices, community building"
        }
    }
    return descriptions.get(segment, descriptions["OPTIMIZE"])


def get_sequence_template_id(
    sequence_type: Literal["noshow", "postcall", "onboarding"],
    email_number: int
) -> str:
    """
    Get template ID for new sequence types (no-show recovery, post-call maybe, onboarding).

    Template Mapping:
    - No-Show Recovery: noshow_recovery_email_1, noshow_recovery_email_2, noshow_recovery_email_3
    - Post-Call Maybe: postcall_maybe_email_1, postcall_maybe_email_2, postcall_maybe_email_3
    - Onboarding Phase 1: onboarding_phase1_email_1, onboarding_phase1_email_2, onboarding_phase1_email_3

    Args:
        sequence_type: Type of sequence (noshow, postcall, onboarding)
        email_number: Email number in sequence (1-3)

    Returns:
        Template ID to use

    Raises:
        ValueError: If sequence_type or email_number is invalid

    Example:
        template_id = get_sequence_template_id("noshow", 1)
        # Returns: "noshow_recovery_email_1"

        template_id = get_sequence_template_id("postcall", 2)
        # Returns: "postcall_maybe_email_2"

        template_id = get_sequence_template_id("onboarding", 3)
        # Returns: "onboarding_phase1_email_3"
    """
    # Validate email_number
    if email_number not in [1, 2, 3]:
        raise ValueError(f"Invalid email_number: {email_number}. Must be 1, 2, or 3.")

    # Template mapping
    templates = {
        "noshow": f"noshow_recovery_email_{email_number}",
        "postcall": f"postcall_maybe_email_{email_number}",
        "onboarding": f"onboarding_phase1_email_{email_number}"
    }

    # Validate sequence_type
    if sequence_type not in templates:
        raise ValueError(
            f"Invalid sequence_type: '{sequence_type}'. "
            f"Must be one of: {list(templates.keys())}"
        )

    return templates[sequence_type]
