"""
Unit tests for Christmas Campaign routing and segment classification.

Tests cover:
- Segment classification logic
- Template ID selection
- Discord alert triggers
- Segment metadata

Author: Christmas Campaign Team
Created: 2025-11-16
"""

import pytest
import os

# Set testing mode to avoid Prefect Server connection
os.environ["PREFECT__LOGGING__LEVEL"] = "ERROR"

from campaigns.christmas_campaign.tasks.routing import (
    classify_segment,
    get_email_template_id,
    should_send_discord_alert,
    get_segment_priority,
    get_segment_description
)


class TestClassifySegment:
    """Test segment classification logic."""

    def test_critical_segment_two_red_systems(self):
        """Test CRITICAL classification with 2 red systems."""
        segment = classify_segment(red_systems=2, orange_systems=1, yellow_systems=3, green_systems=2)
        assert segment == "CRITICAL"

    def test_critical_segment_three_red_systems(self):
        """Test CRITICAL classification with 3+ red systems."""
        segment = classify_segment(red_systems=3, orange_systems=2, yellow_systems=2, green_systems=1)
        assert segment == "CRITICAL"

    def test_urgent_segment_one_red_system(self):
        """Test URGENT classification with 1 red system."""
        segment = classify_segment(red_systems=1, orange_systems=1, yellow_systems=3, green_systems=3)
        assert segment == "URGENT"

    def test_urgent_segment_two_orange_systems(self):
        """Test URGENT classification with 2+ orange systems."""
        segment = classify_segment(red_systems=0, orange_systems=2, yellow_systems=3, green_systems=3)
        assert segment == "URGENT"

    def test_urgent_segment_three_orange_systems(self):
        """Test URGENT classification with 3+ orange systems."""
        segment = classify_segment(red_systems=0, orange_systems=3, yellow_systems=2, green_systems=3)
        assert segment == "URGENT"

    def test_optimize_segment_one_orange(self):
        """Test OPTIMIZE classification with 1 orange system."""
        segment = classify_segment(red_systems=0, orange_systems=1, yellow_systems=3, green_systems=4)
        assert segment == "OPTIMIZE"

    def test_optimize_segment_all_green(self):
        """Test OPTIMIZE classification with all green systems."""
        segment = classify_segment(red_systems=0, orange_systems=0, yellow_systems=0, green_systems=8)
        assert segment == "OPTIMIZE"

    def test_optimize_segment_mostly_yellow(self):
        """Test OPTIMIZE classification with mostly yellow systems."""
        segment = classify_segment(red_systems=0, orange_systems=0, yellow_systems=5, green_systems=3)
        assert segment == "OPTIMIZE"

    def test_boundary_case_exactly_one_red(self):
        """Test boundary case: exactly 1 red system should be URGENT."""
        segment = classify_segment(red_systems=1, orange_systems=0, yellow_systems=4, green_systems=3)
        assert segment == "URGENT"

    def test_boundary_case_exactly_two_orange(self):
        """Test boundary case: exactly 2 orange systems should be URGENT."""
        segment = classify_segment(red_systems=0, orange_systems=2, yellow_systems=3, green_systems=3)
        assert segment == "URGENT"


class TestGetEmailTemplateId:
    """Test email template ID selection logic."""

    def test_email_1_universal(self):
        """Test Email 1 is universal (same for all segments)."""
        assert get_email_template_id(1, "CRITICAL") == "christmas_email_1"
        assert get_email_template_id(1, "URGENT") == "christmas_email_1"
        assert get_email_template_id(1, "OPTIMIZE") == "christmas_email_1"

    def test_email_2_segment_specific_critical(self):
        """Test Email 2 is segment-specific for CRITICAL."""
        assert get_email_template_id(2, "CRITICAL") == "christmas_email_2a_critical"

    def test_email_2_segment_specific_urgent(self):
        """Test Email 2 is segment-specific for URGENT."""
        assert get_email_template_id(2, "URGENT") == "christmas_email_2b_urgent"

    def test_email_2_segment_specific_optimize(self):
        """Test Email 2 is segment-specific for OPTIMIZE."""
        assert get_email_template_id(2, "OPTIMIZE") == "christmas_email_2c_optimize"

    def test_email_3_universal(self):
        """Test Email 3 is universal."""
        assert get_email_template_id(3, "CRITICAL") == "christmas_email_3"
        assert get_email_template_id(3, "URGENT") == "christmas_email_3"
        assert get_email_template_id(3, "OPTIMIZE") == "christmas_email_3"

    def test_email_4_universal(self):
        """Test Email 4 is universal."""
        assert get_email_template_id(4, "CRITICAL") == "christmas_email_4"

    def test_email_5_universal(self):
        """Test Email 5 is universal."""
        assert get_email_template_id(5, "OPTIMIZE") == "christmas_email_5"

    def test_email_6_universal(self):
        """Test Email 6 is universal."""
        assert get_email_template_id(6, "URGENT") == "christmas_email_6"

    def test_email_7_segment_specific_critical(self):
        """Test Email 7 is segment-specific for CRITICAL."""
        assert get_email_template_id(7, "CRITICAL") == "christmas_email_7a_critical"

    def test_email_7_segment_specific_urgent(self):
        """Test Email 7 is segment-specific for URGENT."""
        assert get_email_template_id(7, "URGENT") == "christmas_email_7b_urgent"

    def test_email_7_segment_specific_optimize(self):
        """Test Email 7 is segment-specific for OPTIMIZE."""
        assert get_email_template_id(7, "OPTIMIZE") == "christmas_email_7c_optimize"

    def test_invalid_email_number_fallback(self):
        """Test fallback for invalid email number."""
        assert get_email_template_id(99, "CRITICAL") == "christmas_email_1"


class TestShouldSendDiscordAlert:
    """Test Discord alert trigger logic."""

    def test_discord_alert_for_critical(self):
        """Test Discord alert is sent for CRITICAL segment."""
        assert should_send_discord_alert("CRITICAL") is True

    def test_no_discord_alert_for_urgent(self):
        """Test Discord alert is NOT sent for URGENT segment."""
        assert should_send_discord_alert("URGENT") is False

    def test_no_discord_alert_for_optimize(self):
        """Test Discord alert is NOT sent for OPTIMIZE segment."""
        assert should_send_discord_alert("OPTIMIZE") is False


class TestGetSegmentPriority:
    """Test segment priority calculation."""

    def test_critical_priority(self):
        """Test CRITICAL segment has priority 1 (highest)."""
        assert get_segment_priority("CRITICAL") == 1

    def test_urgent_priority(self):
        """Test URGENT segment has priority 2 (medium)."""
        assert get_segment_priority("URGENT") == 2

    def test_optimize_priority(self):
        """Test OPTIMIZE segment has priority 3 (lowest)."""
        assert get_segment_priority("OPTIMIZE") == 3

    def test_invalid_segment_fallback(self):
        """Test invalid segment defaults to priority 3."""
        assert get_segment_priority("INVALID") == 3

    def test_priority_ordering(self):
        """Test that priorities are correctly ordered."""
        assert get_segment_priority("CRITICAL") < get_segment_priority("URGENT")
        assert get_segment_priority("URGENT") < get_segment_priority("OPTIMIZE")


class TestGetSegmentDescription:
    """Test segment description metadata."""

    def test_critical_description(self):
        """Test CRITICAL segment description."""
        desc = get_segment_description("CRITICAL")
        assert desc["name"] == "Critical"
        assert "crisis" in desc["description"].lower()
        assert "2+" in desc["description"]

    def test_urgent_description(self):
        """Test URGENT segment description."""
        desc = get_segment_description("URGENT")
        assert desc["name"] == "Urgent"
        assert "struggling" in desc["description"].lower()

    def test_optimize_description(self):
        """Test OPTIMIZE segment description."""
        desc = get_segment_description("OPTIMIZE")
        assert desc["name"] == "Optimize"
        assert "functional" in desc["description"].lower()

    def test_description_has_required_keys(self):
        """Test all descriptions have required keys."""
        required_keys = ["name", "description", "characteristics", "action_needed"]
        for segment in ["CRITICAL", "URGENT", "OPTIMIZE"]:
            desc = get_segment_description(segment)
            for key in required_keys:
                assert key in desc, f"Missing key '{key}' in {segment} description"

    def test_invalid_segment_fallback(self):
        """Test invalid segment returns OPTIMIZE description."""
        desc = get_segment_description("INVALID")
        assert desc["name"] == "Optimize"


# ==============================================================================
# Integration Tests
# ==============================================================================

class TestSegmentClassificationIntegration:
    """Integration tests combining classification and template selection."""

    def test_critical_flow_complete(self):
        """Test complete flow for CRITICAL segment."""
        # Classify
        segment = classify_segment(red_systems=3, orange_systems=2, yellow_systems=2, green_systems=1)
        assert segment == "CRITICAL"

        # Template selection
        assert get_email_template_id(1, segment) == "christmas_email_1"
        assert get_email_template_id(2, segment) == "christmas_email_2a_critical"
        assert get_email_template_id(7, segment) == "christmas_email_7a_critical"

        # Discord alert
        assert should_send_discord_alert(segment) is True

        # Priority
        assert get_segment_priority(segment) == 1

    def test_urgent_flow_complete(self):
        """Test complete flow for URGENT segment."""
        # Classify
        segment = classify_segment(red_systems=1, orange_systems=1, yellow_systems=3, green_systems=3)
        assert segment == "URGENT"

        # Template selection
        assert get_email_template_id(1, segment) == "christmas_email_1"
        assert get_email_template_id(2, segment) == "christmas_email_2b_urgent"
        assert get_email_template_id(7, segment) == "christmas_email_7b_urgent"

        # Discord alert
        assert should_send_discord_alert(segment) is False

        # Priority
        assert get_segment_priority(segment) == 2

    def test_optimize_flow_complete(self):
        """Test complete flow for OPTIMIZE segment."""
        # Classify
        segment = classify_segment(red_systems=0, orange_systems=1, yellow_systems=3, green_systems=4)
        assert segment == "OPTIMIZE"

        # Template selection
        assert get_email_template_id(1, segment) == "christmas_email_1"
        assert get_email_template_id(2, segment) == "christmas_email_2c_optimize"
        assert get_email_template_id(7, segment) == "christmas_email_7c_optimize"

        # Discord alert
        assert should_send_discord_alert(segment) is False

        # Priority
        assert get_segment_priority(segment) == 3
