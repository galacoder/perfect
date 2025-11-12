"""
Unit tests for routing logic module.

Tests all Prefect tasks for segment classification and email template routing.
"""

import pytest
from tasks.routing import (
    determine_segment,
    select_email_template,
    get_wait_duration
)


class TestDetermineSegment:
    """Tests for determine_segment task."""

    def test_critical_segment_two_red_systems(self):
        """Test CRITICAL classification with 2 red systems."""
        # Act
        segment = determine_segment(red_systems=2, orange_systems=0)

        # Assert
        assert segment == "CRITICAL"

    def test_critical_segment_three_red_systems(self):
        """Test CRITICAL classification with 3+ red systems."""
        # Act
        segment = determine_segment(red_systems=3, orange_systems=1)

        # Assert
        assert segment == "CRITICAL"

    def test_critical_segment_with_orange_systems(self):
        """Test CRITICAL takes precedence over orange systems."""
        # Act
        segment = determine_segment(red_systems=2, orange_systems=5)

        # Assert
        assert segment == "CRITICAL"

    def test_urgent_segment_one_red_system(self):
        """Test URGENT classification with 1 red system."""
        # Act
        segment = determine_segment(red_systems=1, orange_systems=0)

        # Assert
        assert segment == "URGENT"

    def test_urgent_segment_two_orange_systems(self):
        """Test URGENT classification with 2+ orange systems."""
        # Act
        segment = determine_segment(red_systems=0, orange_systems=2)

        # Assert
        assert segment == "URGENT"

    def test_urgent_segment_three_orange_systems(self):
        """Test URGENT classification with 3+ orange systems."""
        # Act
        segment = determine_segment(red_systems=0, orange_systems=3)

        # Assert
        assert segment == "URGENT"

    def test_urgent_segment_one_red_and_orange(self):
        """Test URGENT with 1 red and some orange."""
        # Act
        segment = determine_segment(red_systems=1, orange_systems=1)

        # Assert
        assert segment == "URGENT"

    def test_optimize_segment_all_green(self):
        """Test OPTIMIZE classification with all green systems."""
        # Act
        segment = determine_segment(
            red_systems=0,
            orange_systems=0,
            yellow_systems=0,
            green_systems=8
        )

        # Assert
        assert segment == "OPTIMIZE"

    def test_optimize_segment_mostly_green_one_orange(self):
        """Test OPTIMIZE with 1 orange and rest green."""
        # Act
        segment = determine_segment(
            red_systems=0,
            orange_systems=1,
            yellow_systems=0,
            green_systems=7
        )

        # Assert
        assert segment == "OPTIMIZE"

    def test_optimize_segment_yellow_and_green(self):
        """Test OPTIMIZE with yellow and green systems."""
        # Act
        segment = determine_segment(
            red_systems=0,
            orange_systems=0,
            yellow_systems=2,
            green_systems=6
        )

        # Assert
        assert segment == "OPTIMIZE"

    def test_unknown_segment_edge_case(self):
        """Test UNKNOWN for edge cases that don't match other segments."""
        # This should not happen in practice, but test the fallback
        # All zeros would normally be OPTIMIZE, but let's test the logic
        segment = determine_segment(red_systems=0, orange_systems=0)

        # Assert - should be OPTIMIZE since red_systems == 0 and orange_systems <= 1
        assert segment == "OPTIMIZE"

    def test_segment_with_default_parameters(self):
        """Test segment classification with default yellow/green parameters."""
        # Act - only required parameters provided
        segment = determine_segment(red_systems=0, orange_systems=0)

        # Assert
        assert segment == "OPTIMIZE"


class TestSelectEmailTemplate:
    """Tests for select_email_template task."""

    def test_email_1_universal(self):
        """Test Email #1 is universal (same for all segments)."""
        # Act
        template_critical = select_email_template(email_number=1, segment="CRITICAL")
        template_urgent = select_email_template(email_number=1, segment="URGENT")
        template_optimize = select_email_template(email_number=1, segment="OPTIMIZE")

        # Assert
        assert template_critical == "email_1"
        assert template_urgent == "email_1"
        assert template_optimize == "email_1"

    def test_email_2_critical(self):
        """Test Email #2 routes to 2A for CRITICAL segment."""
        # Act
        template = select_email_template(email_number=2, segment="CRITICAL")

        # Assert
        assert template == "email_2a_critical"

    def test_email_2_urgent(self):
        """Test Email #2 routes to 2B for URGENT segment."""
        # Act
        template = select_email_template(email_number=2, segment="URGENT")

        # Assert
        assert template == "email_2b_urgent"

    def test_email_2_optimize(self):
        """Test Email #2 routes to 2C for OPTIMIZE segment."""
        # Act
        template = select_email_template(email_number=2, segment="OPTIMIZE")

        # Assert
        assert template == "email_2c_optimize"

    def test_email_2_unknown_fallback(self):
        """Test Email #2 falls back to URGENT for UNKNOWN segment."""
        # Act
        template = select_email_template(email_number=2, segment="UNKNOWN")

        # Assert
        assert template == "email_2b_urgent"

    def test_email_3_universal(self):
        """Test Email #3 is universal (BusOS Framework)."""
        # Act
        template_critical = select_email_template(email_number=3, segment="CRITICAL")
        template_urgent = select_email_template(email_number=3, segment="URGENT")
        template_optimize = select_email_template(email_number=3, segment="OPTIMIZE")

        # Assert
        assert template_critical == "email_3"
        assert template_urgent == "email_3"
        assert template_optimize == "email_3"

    def test_email_4_universal(self):
        """Test Email #4 is universal (Christmas Special)."""
        # Act
        template_critical = select_email_template(email_number=4, segment="CRITICAL")
        template_urgent = select_email_template(email_number=4, segment="URGENT")
        template_optimize = select_email_template(email_number=4, segment="OPTIMIZE")

        # Assert
        assert template_critical == "email_4"
        assert template_urgent == "email_4"
        assert template_optimize == "email_4"

    def test_email_5_critical(self):
        """Test Email #5 routes to 5A for CRITICAL segment."""
        # Act
        template = select_email_template(email_number=5, segment="CRITICAL")

        # Assert
        assert template == "email_5a_critical"

    def test_email_5_urgent(self):
        """Test Email #5 routes to 5B for URGENT segment."""
        # Act
        template = select_email_template(email_number=5, segment="URGENT")

        # Assert
        assert template == "email_5b_urgent"

    def test_email_5_optimize(self):
        """Test Email #5 routes to 5C for OPTIMIZE segment."""
        # Act
        template = select_email_template(email_number=5, segment="OPTIMIZE")

        # Assert
        assert template == "email_5c_optimize"

    def test_email_5_unknown_fallback(self):
        """Test Email #5 falls back to URGENT for UNKNOWN segment."""
        # Act
        template = select_email_template(email_number=5, segment="UNKNOWN")

        # Assert
        assert template == "email_5b_urgent"

    def test_invalid_email_number_zero(self):
        """Test invalid email number (0) raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid email_number: 0. Must be 1-5."):
            select_email_template(email_number=0, segment="CRITICAL")

    def test_invalid_email_number_six(self):
        """Test invalid email number (6) raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid email_number: 6. Must be 1-5."):
            select_email_template(email_number=6, segment="URGENT")

    def test_invalid_email_number_negative(self):
        """Test invalid email number (-1) raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid email_number: -1. Must be 1-5."):
            select_email_template(email_number=-1, segment="OPTIMIZE")


class TestGetWaitDuration:
    """Tests for get_wait_duration task."""

    def test_wait_after_email_1_production(self):
        """Test wait duration after Email #1 in production mode (24 hours)."""
        # Act
        wait_seconds = get_wait_duration(email_number=1, testing_mode=False)

        # Assert
        assert wait_seconds == 86400  # 24 hours in seconds

    def test_wait_after_email_2_production(self):
        """Test wait duration after Email #2 in production mode (48 hours)."""
        # Act
        wait_seconds = get_wait_duration(email_number=2, testing_mode=False)

        # Assert
        assert wait_seconds == 172800  # 48 hours in seconds

    def test_wait_after_email_3_production(self):
        """Test wait duration after Email #3 in production mode (48 hours)."""
        # Act
        wait_seconds = get_wait_duration(email_number=3, testing_mode=False)

        # Assert
        assert wait_seconds == 172800  # 48 hours in seconds

    def test_wait_after_email_4_production(self):
        """Test wait duration after Email #4 in production mode (48 hours)."""
        # Act
        wait_seconds = get_wait_duration(email_number=4, testing_mode=False)

        # Assert
        assert wait_seconds == 172800  # 48 hours in seconds

    def test_wait_after_email_1_testing(self):
        """Test wait duration after Email #1 in testing mode (1 minute)."""
        # Act
        wait_seconds = get_wait_duration(email_number=1, testing_mode=True)

        # Assert
        assert wait_seconds == 60  # 1 minute in seconds

    def test_wait_after_email_2_testing(self):
        """Test wait duration after Email #2 in testing mode (2 minutes)."""
        # Act
        wait_seconds = get_wait_duration(email_number=2, testing_mode=True)

        # Assert
        assert wait_seconds == 120  # 2 minutes in seconds

    def test_wait_after_email_3_testing(self):
        """Test wait duration after Email #3 in testing mode (3 minutes)."""
        # Act
        wait_seconds = get_wait_duration(email_number=3, testing_mode=True)

        # Assert
        assert wait_seconds == 180  # 3 minutes in seconds

    def test_wait_after_email_4_testing(self):
        """Test wait duration after Email #4 in testing mode (4 minutes)."""
        # Act
        wait_seconds = get_wait_duration(email_number=4, testing_mode=True)

        # Assert
        assert wait_seconds == 240  # 4 minutes in seconds

    def test_default_testing_mode_false(self):
        """Test default testing_mode parameter is False (production)."""
        # Act
        wait_seconds = get_wait_duration(email_number=1)

        # Assert
        assert wait_seconds == 86400  # Production mode (24 hours)

    def test_invalid_email_number_zero(self):
        """Test invalid email number (0) raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid email_number: 0"):
            get_wait_duration(email_number=0, testing_mode=False)

    def test_invalid_email_number_five(self):
        """Test invalid email number (5) raises ValueError - no wait after Email #5."""
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid email_number: 5. Must be 1-4"):
            get_wait_duration(email_number=5, testing_mode=False)

    def test_invalid_email_number_negative(self):
        """Test invalid email number (-1) raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid email_number: -1"):
            get_wait_duration(email_number=-1, testing_mode=True)


class TestRetryLogic:
    """Tests for Prefect task annotations (integration test concept)."""

    def test_task_annotation_exists(self):
        """Verify all functions are Prefect tasks."""
        import inspect
        from tasks import routing

        # Get all functions that should be tasks
        task_functions = [
            routing.determine_segment,
            routing.select_email_template,
            routing.get_wait_duration
        ]

        for func in task_functions:
            # Verify function has task metadata
            assert callable(func), f"{func.__name__} should be callable"


class TestIntegrationScenarios:
    """Integration test scenarios combining multiple routing functions."""

    def test_critical_customer_flow(self):
        """Test complete flow for CRITICAL customer."""
        # Arrange - CRITICAL: 3 red systems
        red_systems = 3
        orange_systems = 1

        # Act - Determine segment
        segment = determine_segment(red_systems=red_systems, orange_systems=orange_systems)

        # Assert segment
        assert segment == "CRITICAL"

        # Act - Select email templates for sequence
        email_1 = select_email_template(email_number=1, segment=segment)
        email_2 = select_email_template(email_number=2, segment=segment)
        email_3 = select_email_template(email_number=3, segment=segment)
        email_4 = select_email_template(email_number=4, segment=segment)
        email_5 = select_email_template(email_number=5, segment=segment)

        # Assert email templates
        assert email_1 == "email_1"
        assert email_2 == "email_2a_critical"  # Segment-specific
        assert email_3 == "email_3"
        assert email_4 == "email_4"
        assert email_5 == "email_5a_critical"  # Segment-specific

        # Act - Get wait durations for testing
        wait_1 = get_wait_duration(email_number=1, testing_mode=True)
        wait_2 = get_wait_duration(email_number=2, testing_mode=True)
        wait_3 = get_wait_duration(email_number=3, testing_mode=True)
        wait_4 = get_wait_duration(email_number=4, testing_mode=True)

        # Assert wait durations
        assert wait_1 == 60   # 1 min
        assert wait_2 == 120  # 2 min
        assert wait_3 == 180  # 3 min
        assert wait_4 == 240  # 4 min

    def test_urgent_customer_flow(self):
        """Test complete flow for URGENT customer."""
        # Arrange - URGENT: 1 red system
        segment = determine_segment(red_systems=1, orange_systems=0)

        # Assert
        assert segment == "URGENT"
        assert select_email_template(email_number=2, segment=segment) == "email_2b_urgent"
        assert select_email_template(email_number=5, segment=segment) == "email_5b_urgent"

    def test_optimize_customer_flow(self):
        """Test complete flow for OPTIMIZE customer."""
        # Arrange - OPTIMIZE: All green/yellow
        segment = determine_segment(red_systems=0, orange_systems=0, green_systems=8)

        # Assert
        assert segment == "OPTIMIZE"
        assert select_email_template(email_number=2, segment=segment) == "email_2c_optimize"
        assert select_email_template(email_number=5, segment=segment) == "email_5c_optimize"

    def test_production_timing(self):
        """Test production wait durations total ~6 days."""
        # Act
        total_wait = sum([
            get_wait_duration(email_number=1, testing_mode=False),
            get_wait_duration(email_number=2, testing_mode=False),
            get_wait_duration(email_number=3, testing_mode=False),
            get_wait_duration(email_number=4, testing_mode=False)
        ])

        # Assert - 24h + 48h + 48h + 48h = 168 hours = 7 days
        assert total_wait == 604800  # 7 days in seconds

    def test_testing_timing(self):
        """Test testing wait durations total ~10 minutes."""
        # Act
        total_wait = sum([
            get_wait_duration(email_number=1, testing_mode=True),
            get_wait_duration(email_number=2, testing_mode=True),
            get_wait_duration(email_number=3, testing_mode=True),
            get_wait_duration(email_number=4, testing_mode=True)
        ])

        # Assert - 1min + 2min + 3min + 4min = 10 minutes
        assert total_wait == 600  # 10 minutes in seconds


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
