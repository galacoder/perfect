"""
Routing logic for BusOS Email Sequence.

This module provides tasks for segment-based email routing:
- Determine segment based on assessment results
- Route to appropriate email template based on segment

Segments:
- CRITICAL: 2+ red systems (broken)
- URGENT: 1 red OR 2+ orange systems (needs attention)
- OPTIMIZE: All systems green/yellow (opportunity for growth)
"""

from prefect import task
from typing import Literal

# Type definition for segments
Segment = Literal["CRITICAL", "URGENT", "OPTIMIZE", "UNKNOWN"]


@task(name="routing-determine-segment")
def determine_segment(
    red_systems: int,
    orange_systems: int,
    yellow_systems: int = 0,
    green_systems: int = 0
) -> Segment:
    """
    Determine customer segment based on assessment results.

    Segmentation logic (from n8n Switch nodes):
    - CRITICAL: 2+ red systems (broken, urgent fix needed)
    - URGENT: 1 red OR 2+ orange systems (attention needed soon)
    - OPTIMIZE: All green/yellow systems (growth opportunities)
    - UNKNOWN: Edge case fallback

    Args:
        red_systems: Number of critical (broken) systems
        orange_systems: Number of systems needing attention
        yellow_systems: Number of systems with minor issues (optional)
        green_systems: Number of healthy systems (optional)

    Returns:
        Segment classification: "CRITICAL", "URGENT", "OPTIMIZE", or "UNKNOWN"

    Example:
        segment = determine_segment(red_systems=3, orange_systems=1)
        # Returns: "CRITICAL"

        segment = determine_segment(red_systems=0, orange_systems=2)
        # Returns: "URGENT"

        segment = determine_segment(red_systems=0, orange_systems=0, yellow_systems=2, green_systems=6)
        # Returns: "OPTIMIZE"
    """
    # CRITICAL: 2 or more broken systems
    if red_systems >= 2:
        return "CRITICAL"

    # URGENT: 1 broken system OR 2+ systems needing attention
    if red_systems == 1 or orange_systems >= 2:
        return "URGENT"

    # OPTIMIZE: No critical issues, mostly healthy
    if red_systems == 0 and orange_systems <= 1:
        return "OPTIMIZE"

    # Fallback for edge cases
    return "UNKNOWN"


@task(name="routing-select-email-template")
def select_email_template(email_number: int, segment: Segment) -> str:
    """
    Select appropriate email template based on email number and segment.

    Email routing logic:
    - Email #1: Universal (assessment invitation)
    - Email #2: Segment-specific (2A/2B/2C based on CRITICAL/URGENT/OPTIMIZE)
    - Email #3: Universal (BusOS framework introduction)
    - Email #4: Universal (Christmas Special offer)
    - Email #5: Segment-specific (5A/5B/5C based on CRITICAL/URGENT/OPTIMIZE)

    Args:
        email_number: Email sequence number (1-5)
        segment: Customer segment ("CRITICAL", "URGENT", "OPTIMIZE", "UNKNOWN")

    Returns:
        Template name for use with email_templates.get_template()

    Raises:
        ValueError: If email_number is not 1-5

    Example:
        template_name = select_email_template(email_number=2, segment="CRITICAL")
        # Returns: "email_2a_critical"

        template_name = select_email_template(email_number=3, segment="URGENT")
        # Returns: "email_3" (universal, segment doesn't matter)

        template_name = select_email_template(email_number=5, segment="OPTIMIZE")
        # Returns: "email_5c_optimize"
    """
    if email_number not in [1, 2, 3, 4, 5]:
        raise ValueError(f"Invalid email_number: {email_number}. Must be 1-5.")

    # Email #1: Universal
    if email_number == 1:
        return "email_1"

    # Email #2: Segment-specific
    if email_number == 2:
        if segment == "CRITICAL":
            return "email_2a_critical"
        elif segment == "URGENT":
            return "email_2b_urgent"
        elif segment == "OPTIMIZE":
            return "email_2c_optimize"
        else:
            # Fallback to URGENT if segment is UNKNOWN
            return "email_2b_urgent"

    # Email #3: Universal
    if email_number == 3:
        return "email_3"

    # Email #4: Universal
    if email_number == 4:
        return "email_4"

    # Email #5: Segment-specific
    if email_number == 5:
        if segment == "CRITICAL":
            return "email_5a_critical"
        elif segment == "URGENT":
            return "email_5b_urgent"
        elif segment == "OPTIMIZE":
            return "email_5c_optimize"
        else:
            # Fallback to URGENT if segment is UNKNOWN
            return "email_5b_urgent"

    # Should never reach here due to earlier validation
    raise ValueError(f"Unexpected email_number: {email_number}")


@task(name="routing-get-wait-duration")
def get_wait_duration(email_number: int, testing_mode: bool = False) -> int:
    """
    Get wait duration (in seconds) between emails based on sequence position.

    Wait durations (from n8n Wait nodes):
    - After Email #1 → Email #2: 24 hours (or 1 min in testing)
    - After Email #2 → Email #3: 48 hours (or 2 min in testing)
    - After Email #3 → Email #4: 48 hours (or 3 min in testing)
    - After Email #4 → Email #5: 48 hours (or 4 min in testing)

    Args:
        email_number: Email that was just sent (1-4)
        testing_mode: If True, use short waits for testing (default: False from env)

    Returns:
        Wait duration in seconds

    Raises:
        ValueError: If email_number is not 1-4

    Example:
        wait_seconds = get_wait_duration(email_number=1, testing_mode=False)
        # Returns: 86400 (24 hours)

        wait_seconds = get_wait_duration(email_number=1, testing_mode=True)
        # Returns: 60 (1 minute)

        wait_seconds = get_wait_duration(email_number=2, testing_mode=False)
        # Returns: 172800 (48 hours)
    """
    if email_number not in [1, 2, 3, 4]:
        raise ValueError(f"Invalid email_number: {email_number}. Must be 1-4 (no wait after Email #5).")

    # Wait durations in seconds
    if testing_mode:
        # Testing mode: 1min, 2min, 3min, 4min
        wait_durations = {
            1: 60,      # 1 minute
            2: 120,     # 2 minutes
            3: 180,     # 3 minutes
            4: 240      # 4 minutes
        }
    else:
        # Production mode: 24h, 48h, 48h, 48h
        wait_durations = {
            1: 86400,   # 24 hours (1 day)
            2: 172800,  # 48 hours (2 days)
            3: 172800,  # 48 hours (2 days)
            4: 172800   # 48 hours (2 days)
        }

    return wait_durations[email_number]
