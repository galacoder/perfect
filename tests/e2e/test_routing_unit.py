"""
Unit tests for Christmas Campaign routing logic.

This module tests all routing functions with comprehensive edge cases:
- classify_segment() - Segment classification logic
- get_email_template_id() - Template selection logic
- should_send_discord_alert() - Discord alert logic
- get_segment_priority() - Priority assignment
- get_segment_description() - Segment descriptions

Coverage target: 100% of routing.py
"""

import pytest
from campaigns.christmas_campaign.tasks.routing import (
    classify_segment,
    get_email_template_id,
    should_send_discord_alert,
    get_segment_priority,
    get_segment_description
)


# ===== classify_segment() tests =====

class TestClassifySegment:
    """Test segment classification logic."""

    def test_critical_segment_2_red_systems(self):
        """CRITICAL: Exactly 2 red systems."""
        assert classify_segment(red_systems=2) == "CRITICAL"

    def test_critical_segment_3_red_systems(self):
        """CRITICAL: 3+ red systems."""
        assert classify_segment(red_systems=3, orange_systems=1) == "CRITICAL"

    def test_critical_segment_all_red(self):
        """CRITICAL: All 8 systems red."""
        assert classify_segment(red_systems=8) == "CRITICAL"

    def test_urgent_segment_1_red_system(self):
        """URGENT: Exactly 1 red system."""
        assert classify_segment(red_systems=1) == "URGENT"

    def test_urgent_segment_2_orange_systems(self):
        """URGENT: 2 orange systems, no red."""
        assert classify_segment(red_systems=0, orange_systems=2) == "URGENT"

    def test_urgent_segment_3_orange_systems(self):
        """URGENT: 3+ orange systems, no red."""
        assert classify_segment(red_systems=0, orange_systems=3) == "URGENT"

    def test_urgent_segment_1_red_2_orange(self):
        """URGENT: 1 red + 2 orange (red takes precedence)."""
        assert classify_segment(red_systems=1, orange_systems=2) == "URGENT"

    def test_optimize_segment_1_orange(self):
        """OPTIMIZE: Only 1 orange system."""
        assert classify_segment(red_systems=0, orange_systems=1, yellow_systems=3, green_systems=4) == "OPTIMIZE"

    def test_optimize_segment_all_green(self):
        """OPTIMIZE: All green systems."""
        assert classify_segment(red_systems=0, orange_systems=0, yellow_systems=0, green_systems=8) == "OPTIMIZE"

    def test_optimize_segment_all_yellow(self):
        """OPTIMIZE: All yellow systems."""
        assert classify_segment(red_systems=0, orange_systems=0, yellow_systems=8, green_systems=0) == "OPTIMIZE"

    def test_optimize_segment_mixed_yellow_green(self):
        """OPTIMIZE: Mixed yellow and green."""
        assert classify_segment(red_systems=0, orange_systems=0, yellow_systems=4, green_systems=4) == "OPTIMIZE"

    def test_optimize_segment_default_no_systems(self):
        """OPTIMIZE: No systems specified (default)."""
        assert classify_segment() == "OPTIMIZE"

    def test_edge_case_zero_systems(self):
        """OPTIMIZE: Explicitly all zeros."""
        assert classify_segment(red_systems=0, orange_systems=0, yellow_systems=0, green_systems=0) == "OPTIMIZE"


# ===== get_email_template_id() tests =====

class TestGetEmailTemplateId:
    """Test email template selection logic."""

    # Email 1 (Universal)
    def test_email_1_critical(self):
        """Email 1 is universal for CRITICAL."""
        assert get_email_template_id(1, "CRITICAL") == "christmas_email_1"

    def test_email_1_urgent(self):
        """Email 1 is universal for URGENT."""
        assert get_email_template_id(1, "URGENT") == "christmas_email_1"

    def test_email_1_optimize(self):
        """Email 1 is universal for OPTIMIZE."""
        assert get_email_template_id(1, "OPTIMIZE") == "christmas_email_1"

    # Email 2 (Segment-specific)
    def test_email_2_critical(self):
        """Email 2 is segment-specific for CRITICAL."""
        assert get_email_template_id(2, "CRITICAL") == "christmas_email_2a_critical"

    def test_email_2_urgent(self):
        """Email 2 is segment-specific for URGENT."""
        assert get_email_template_id(2, "URGENT") == "christmas_email_2b_urgent"

    def test_email_2_optimize(self):
        """Email 2 is segment-specific for OPTIMIZE."""
        assert get_email_template_id(2, "OPTIMIZE") == "christmas_email_2c_optimize"

    # Email 3 (Universal)
    def test_email_3_critical(self):
        """Email 3 is universal for CRITICAL."""
        assert get_email_template_id(3, "CRITICAL") == "christmas_email_3"

    def test_email_3_urgent(self):
        """Email 3 is universal for URGENT."""
        assert get_email_template_id(3, "URGENT") == "christmas_email_3"

    def test_email_3_optimize(self):
        """Email 3 is universal for OPTIMIZE."""
        assert get_email_template_id(3, "OPTIMIZE") == "christmas_email_3"

    # Email 4 (Universal)
    def test_email_4_all_segments(self):
        """Email 4 is universal for all segments."""
        assert get_email_template_id(4, "CRITICAL") == "christmas_email_4"
        assert get_email_template_id(4, "URGENT") == "christmas_email_4"
        assert get_email_template_id(4, "OPTIMIZE") == "christmas_email_4"

    # Email 5 (Universal)
    def test_email_5_all_segments(self):
        """Email 5 is universal for all segments."""
        assert get_email_template_id(5, "CRITICAL") == "christmas_email_5"
        assert get_email_template_id(5, "URGENT") == "christmas_email_5"
        assert get_email_template_id(5, "OPTIMIZE") == "christmas_email_5"

    # Email 6 (Universal)
    def test_email_6_all_segments(self):
        """Email 6 is universal for all segments."""
        assert get_email_template_id(6, "CRITICAL") == "christmas_email_6"
        assert get_email_template_id(6, "URGENT") == "christmas_email_6"
        assert get_email_template_id(6, "OPTIMIZE") == "christmas_email_6"

    # Email 7 (Segment-specific)
    def test_email_7_critical(self):
        """Email 7 is segment-specific for CRITICAL."""
        assert get_email_template_id(7, "CRITICAL") == "christmas_email_7a_critical"

    def test_email_7_urgent(self):
        """Email 7 is segment-specific for URGENT."""
        assert get_email_template_id(7, "URGENT") == "christmas_email_7b_urgent"

    def test_email_7_optimize(self):
        """Email 7 is segment-specific for OPTIMIZE."""
        assert get_email_template_id(7, "OPTIMIZE") == "christmas_email_7c_optimize"

    # Edge cases
    def test_email_0_fallback(self):
        """Email 0 (invalid) returns fallback."""
        assert get_email_template_id(0, "CRITICAL") == "christmas_email_1"

    def test_email_8_fallback(self):
        """Email 8 (out of range) returns fallback."""
        assert get_email_template_id(8, "CRITICAL") == "christmas_email_1"

    def test_email_negative_fallback(self):
        """Negative email number returns fallback."""
        assert get_email_template_id(-1, "CRITICAL") == "christmas_email_1"

    def test_email_100_fallback(self):
        """Large email number returns fallback."""
        assert get_email_template_id(100, "CRITICAL") == "christmas_email_1"


# ===== should_send_discord_alert() tests =====

class TestShouldSendDiscordAlert:
    """Test Discord alert logic."""

    def test_discord_alert_critical(self):
        """Discord alert sent for CRITICAL segment."""
        assert should_send_discord_alert("CRITICAL") is True

    def test_no_discord_alert_urgent(self):
        """No Discord alert for URGENT segment."""
        assert should_send_discord_alert("URGENT") is False

    def test_no_discord_alert_optimize(self):
        """No Discord alert for OPTIMIZE segment."""
        assert should_send_discord_alert("OPTIMIZE") is False


# ===== get_segment_priority() tests =====

class TestGetSegmentPriority:
    """Test segment priority assignment."""

    def test_critical_priority_1(self):
        """CRITICAL has priority 1 (highest)."""
        assert get_segment_priority("CRITICAL") == 1

    def test_urgent_priority_2(self):
        """URGENT has priority 2 (medium)."""
        assert get_segment_priority("URGENT") == 2

    def test_optimize_priority_3(self):
        """OPTIMIZE has priority 3 (lowest)."""
        assert get_segment_priority("OPTIMIZE") == 3

    def test_priority_ordering(self):
        """Verify priority ordering (CRITICAL < URGENT < OPTIMIZE)."""
        critical = get_segment_priority("CRITICAL")
        urgent = get_segment_priority("URGENT")
        optimize = get_segment_priority("OPTIMIZE")

        assert critical < urgent < optimize


# ===== get_segment_description() tests =====

class TestGetSegmentDescription:
    """Test segment description retrieval."""

    def test_critical_description(self):
        """CRITICAL segment description is complete."""
        desc = get_segment_description("CRITICAL")

        assert desc["name"] == "Critical"
        assert "crisis" in desc["description"].lower()
        assert "2+" in desc["description"]
        assert "characteristics" in desc
        assert "action_needed" in desc
        assert len(desc["characteristics"]) > 0
        assert len(desc["action_needed"]) > 0

    def test_urgent_description(self):
        """URGENT segment description is complete."""
        desc = get_segment_description("URGENT")

        assert desc["name"] == "Urgent"
        assert "struggling" in desc["description"].lower()
        assert "1+" in desc["description"]
        assert "characteristics" in desc
        assert "action_needed" in desc

    def test_optimize_description(self):
        """OPTIMIZE segment description is complete."""
        desc = get_segment_description("OPTIMIZE")

        assert desc["name"] == "Optimize"
        assert "functional" in desc["description"].lower()
        assert "improvement" in desc["description"].lower()
        assert "characteristics" in desc
        assert "action_needed" in desc

    def test_description_structure(self):
        """All descriptions have required keys."""
        required_keys = {"name", "description", "characteristics", "action_needed"}

        for segment in ["CRITICAL", "URGENT", "OPTIMIZE"]:
            desc = get_segment_description(segment)
            assert set(desc.keys()) == required_keys

    def test_description_unique_content(self):
        """Each segment has unique description content."""
        critical_desc = get_segment_description("CRITICAL")
        urgent_desc = get_segment_description("URGENT")
        optimize_desc = get_segment_description("OPTIMIZE")

        # Verify descriptions are different
        assert critical_desc["description"] != urgent_desc["description"]
        assert urgent_desc["description"] != optimize_desc["description"]
        assert critical_desc["description"] != optimize_desc["description"]


# ===== Integration tests =====

class TestRoutingIntegration:
    """Test routing functions work together correctly."""

    def test_critical_contact_full_workflow(self):
        """Test complete workflow for CRITICAL contact."""
        # Step 1: Classify
        segment = classify_segment(red_systems=3, orange_systems=1)
        assert segment == "CRITICAL"

        # Step 2: Check Discord alert
        assert should_send_discord_alert(segment) is True

        # Step 3: Get priority
        assert get_segment_priority(segment) == 1

        # Step 4: Get email templates
        assert get_email_template_id(1, segment) == "christmas_email_1"
        assert get_email_template_id(2, segment) == "christmas_email_2a_critical"
        assert get_email_template_id(7, segment) == "christmas_email_7a_critical"

        # Step 5: Get description
        desc = get_segment_description(segment)
        assert desc["name"] == "Critical"

    def test_urgent_contact_full_workflow(self):
        """Test complete workflow for URGENT contact."""
        # Step 1: Classify
        segment = classify_segment(red_systems=1, orange_systems=1)
        assert segment == "URGENT"

        # Step 2: Check Discord alert
        assert should_send_discord_alert(segment) is False

        # Step 3: Get priority
        assert get_segment_priority(segment) == 2

        # Step 4: Get email templates
        assert get_email_template_id(1, segment) == "christmas_email_1"
        assert get_email_template_id(2, segment) == "christmas_email_2b_urgent"
        assert get_email_template_id(7, segment) == "christmas_email_7b_urgent"

    def test_optimize_contact_full_workflow(self):
        """Test complete workflow for OPTIMIZE contact."""
        # Step 1: Classify
        segment = classify_segment(red_systems=0, orange_systems=1, yellow_systems=3, green_systems=4)
        assert segment == "OPTIMIZE"

        # Step 2: Check Discord alert
        assert should_send_discord_alert(segment) is False

        # Step 3: Get priority
        assert get_segment_priority(segment) == 3

        # Step 4: Get email templates
        assert get_email_template_id(1, segment) == "christmas_email_1"
        assert get_email_template_id(2, segment) == "christmas_email_2c_optimize"
        assert get_email_template_id(7, segment) == "christmas_email_7c_optimize"

    def test_all_segments_get_universal_emails(self):
        """Verify all segments receive same universal emails."""
        universal_emails = [1, 3, 4, 5, 6]

        for email_num in universal_emails:
            critical_template = get_email_template_id(email_num, "CRITICAL")
            urgent_template = get_email_template_id(email_num, "URGENT")
            optimize_template = get_email_template_id(email_num, "OPTIMIZE")

            assert critical_template == urgent_template == optimize_template
            assert critical_template == f"christmas_email_{email_num}"

    def test_segment_specific_emails_differ(self):
        """Verify segment-specific emails (2, 7) differ by segment."""
        segment_specific_emails = [2, 7]

        for email_num in segment_specific_emails:
            critical_template = get_email_template_id(email_num, "CRITICAL")
            urgent_template = get_email_template_id(email_num, "URGENT")
            optimize_template = get_email_template_id(email_num, "OPTIMIZE")

            # All three should be different
            assert critical_template != urgent_template
            assert urgent_template != optimize_template
            assert critical_template != optimize_template
