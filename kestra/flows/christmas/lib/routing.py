"""
Routing logic for Kestra Christmas Campaign.

Ported from Prefect campaigns/christmas_campaign/tasks/routing.py

This module provides functions for:
- Classifying contacts into segments (CRITICAL/URGENT/OPTIMIZE)
- Determining email template IDs for 5-day sequence
- Determining email template IDs for secondary sequences (noshow, postcall, onboarding)

Author: Kestra Migration Team
Created: 2025-11-29
Ported from: campaigns/christmas_campaign/tasks/routing.py
"""

from typing import Literal


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
        segment = classify_segment(red_systems=3, orange_systems=2)
        # Returns: "CRITICAL"

        segment = classify_segment(red_systems=1, orange_systems=1)
        # Returns: "URGENT"

        segment = classify_segment(red_systems=0, orange_systems=1)
        # Returns: "OPTIMIZE"
    """
    # Handle None values (default to 0)
    red_systems = red_systems or 0
    orange_systems = orange_systems or 0
    yellow_systems = yellow_systems or 0
    green_systems = green_systems or 0

    # Handle negative numbers (treat as 0)
    red_systems = max(0, red_systems)
    orange_systems = max(0, orange_systems)
    yellow_systems = max(0, yellow_systems)
    green_systems = max(0, green_systems)

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
    - Email 1: "5-Day E1" (Your Assessment Results + Dec 5 Deadline - GIVE)
    - Email 2: "5-Day E2" (The $500K Mistake + BusOS Framework - GIVE)
    - Email 3: "5-Day E3" (Van Tiny Case Study + Soft ASK)
    - Email 4: "5-Day E4" (Value Stack + Medium ASK)
    - Email 5: "5-Day E5" (Final Call - HARD ASK, Last Email)

    Note: Template names in Notion use SHORT format ("5-Day E1") without descriptive suffixes.
    The segment parameter is kept for compatibility but not used for template selection.

    Args:
        email_number: Email number in sequence (1-5)
        segment: Contact segment (not used for Christmas templates)

    Returns:
        Template ID to use (exact Notion template name)

    Example:
        template_id = get_email_template_id(email_number=1, segment="CRITICAL")
        # Returns: "5-Day E1"

        template_id = get_email_template_id(email_number=2, segment="CRITICAL")
        # Returns: "5-Day E2"
    """
    # Christmas 2025: 5-Day Sequence templates (exact Notion names - SHORT format)
    templates = {
        1: "5-Day E1",
        2: "5-Day E2",
        3: "5-Day E3",
        4: "5-Day E4",
        5: "5-Day E5"
    }

    if email_number in templates:
        return templates[email_number]
    else:
        # Fallback to Email 1
        return templates[1]


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


if __name__ == "__main__":
    # Quick test
    print("Testing routing logic...")

    # Test classify_segment
    print(f"classify_segment(2, 0) = {classify_segment(2, 0)}")  # CRITICAL
    print(f"classify_segment(1, 0) = {classify_segment(1, 0)}")  # URGENT
    print(f"classify_segment(0, 2) = {classify_segment(0, 2)}")  # URGENT
    print(f"classify_segment(0, 1) = {classify_segment(0, 1)}")  # OPTIMIZE

    # Test get_email_template_id
    print(f"get_email_template_id(1, 'CRITICAL') = {get_email_template_id(1, 'CRITICAL')}")
    print(f"get_email_template_id(2, 'URGENT') = {get_email_template_id(2, 'URGENT')}")

    # Test get_sequence_template_id
    print(f"get_sequence_template_id('noshow', 1) = {get_sequence_template_id('noshow', 1)}")
    print(f"get_sequence_template_id('postcall', 2) = {get_sequence_template_id('postcall', 2)}")
    print(f"get_sequence_template_id('onboarding', 3) = {get_sequence_template_id('onboarding', 3)}")

    print("✅ Routing logic working!")
