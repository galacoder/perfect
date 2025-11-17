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

    Email Template Mapping:
    - Email 1: Universal (christmas_email_1)
    - Email 2: Segment-specific (christmas_email_2a_critical, 2b_urgent, 2c_optimize)
    - Email 3: Universal (christmas_email_3)
    - Email 4: Universal (christmas_email_4)
    - Email 5: Universal (christmas_email_5)
    - Email 6: Universal (christmas_email_6)
    - Email 7: Segment-specific (christmas_email_7a_critical, 7b_urgent, 7c_optimize)

    Args:
        email_number: Email number in sequence (1-7)
        segment: Contact segment

    Returns:
        Template ID to use

    Example:
        template_id = get_email_template_id(email_number=1, segment="CRITICAL")
        # Returns: "christmas_email_1" (universal)

        template_id = get_email_template_id(email_number=2, segment="CRITICAL")
        # Returns: "christmas_email_2a_critical" (segment-specific)
    """
    # Email 1: Universal
    if email_number == 1:
        return "christmas_email_1"

    # Email 2: Segment-specific
    elif email_number == 2:
        if segment == "CRITICAL":
            return "christmas_email_2a_critical"
        elif segment == "URGENT":
            return "christmas_email_2b_urgent"
        else:
            return "christmas_email_2c_optimize"

    # Email 3-6: Universal
    elif email_number in [3, 4, 5, 6]:
        return f"christmas_email_{email_number}"

    # Email 7: Segment-specific
    elif email_number == 7:
        if segment == "CRITICAL":
            return "christmas_email_7a_critical"
        elif segment == "URGENT":
            return "christmas_email_7b_urgent"
        else:
            return "christmas_email_7c_optimize"

    else:
        # Fallback
        return "christmas_email_1"


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
