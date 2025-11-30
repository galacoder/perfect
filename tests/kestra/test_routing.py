"""
Test routing logic for Kestra implementation.

Tests the ported classify_segment and get_email_template_id functions
from Prefect routing.py module.

Author: Kestra Migration Team
Created: 2025-11-29
"""

import pytest
import sys
from pathlib import Path

# Add kestra lib to path
kestra_lib_path = Path(__file__).parent.parent.parent / "kestra" / "flows" / "christmas" / "lib"
sys.path.insert(0, str(kestra_lib_path))

from routing import classify_segment, get_email_template_id, get_sequence_template_id


class TestClassifySegment:
    """Test segment classification logic."""

    def test_classify_critical_with_2_red_systems(self):
        """CRITICAL segment: 2+ red systems."""
        assert classify_segment(red_systems=2, orange_systems=0) == "CRITICAL"

    def test_classify_critical_with_3_red_systems(self):
        """CRITICAL segment: 3+ red systems."""
        assert classify_segment(red_systems=3, orange_systems=1) == "CRITICAL"

    def test_classify_urgent_with_1_red_system(self):
        """URGENT segment: exactly 1 red system."""
        assert classify_segment(red_systems=1, orange_systems=0) == "URGENT"

    def test_classify_urgent_with_2_orange_systems(self):
        """URGENT segment: 2+ orange systems."""
        assert classify_segment(red_systems=0, orange_systems=2) == "URGENT"

    def test_classify_urgent_with_1_red_and_2_orange(self):
        """URGENT segment: 1 red OR 2+ orange."""
        assert classify_segment(red_systems=1, orange_systems=2) == "URGENT"

    def test_classify_optimize_fallback(self):
        """OPTIMIZE segment: all others (fallback)."""
        assert classify_segment(red_systems=0, orange_systems=1) == "OPTIMIZE"

    def test_classify_optimize_all_green(self):
        """OPTIMIZE segment: all green systems."""
        assert classify_segment(red_systems=0, orange_systems=0, yellow_systems=0, green_systems=8) == "OPTIMIZE"

    def test_classify_segment_handles_none_values(self):
        """Handle None values gracefully (default to 0)."""
        assert classify_segment(red_systems=None, orange_systems=None) == "OPTIMIZE"

    def test_classify_segment_handles_negative_numbers(self):
        """Handle negative numbers (treat as 0)."""
        assert classify_segment(red_systems=-1, orange_systems=-2) == "OPTIMIZE"


class TestGetEmailTemplateId:
    """Test email template ID generation for 5-day sequence."""

    def test_template_email_1(self):
        """Email 1 template: '5-Day E1' (universal)."""
        assert get_email_template_id(email_number=1, segment="CRITICAL") == "5-Day E1"
        assert get_email_template_id(email_number=1, segment="URGENT") == "5-Day E1"
        assert get_email_template_id(email_number=1, segment="OPTIMIZE") == "5-Day E1"

    def test_template_email_2(self):
        """Email 2 template: '5-Day E2' (universal)."""
        assert get_email_template_id(email_number=2, segment="CRITICAL") == "5-Day E2"

    def test_template_email_3(self):
        """Email 3 template: '5-Day E3' (universal)."""
        assert get_email_template_id(email_number=3, segment="OPTIMIZE") == "5-Day E3"

    def test_template_email_4(self):
        """Email 4 template: '5-Day E4' (universal)."""
        assert get_email_template_id(email_number=4, segment="URGENT") == "5-Day E4"

    def test_template_email_5(self):
        """Email 5 template: '5-Day E5' (universal)."""
        assert get_email_template_id(email_number=5, segment="CRITICAL") == "5-Day E5"

    def test_template_fallback_invalid_email_number(self):
        """Fallback to Email 1 for invalid email numbers."""
        assert get_email_template_id(email_number=0, segment="OPTIMIZE") == "5-Day E1"
        assert get_email_template_id(email_number=999, segment="CRITICAL") == "5-Day E1"

    def test_template_segment_ignored_for_christmas(self):
        """Segment parameter is ignored for Christmas templates (all universal)."""
        # All segments get same template for email 2
        assert get_email_template_id(email_number=2, segment="CRITICAL") == "5-Day E2"
        assert get_email_template_id(email_number=2, segment="URGENT") == "5-Day E2"
        assert get_email_template_id(email_number=2, segment="OPTIMIZE") == "5-Day E2"


class TestGetSequenceTemplateId:
    """Test template ID generation for secondary sequences."""

    def test_noshow_sequence_email_1(self):
        """No-show recovery sequence: email 1."""
        assert get_sequence_template_id(sequence_type="noshow", email_number=1) == "noshow_recovery_email_1"

    def test_noshow_sequence_email_2(self):
        """No-show recovery sequence: email 2."""
        assert get_sequence_template_id(sequence_type="noshow", email_number=2) == "noshow_recovery_email_2"

    def test_noshow_sequence_email_3(self):
        """No-show recovery sequence: email 3."""
        assert get_sequence_template_id(sequence_type="noshow", email_number=3) == "noshow_recovery_email_3"

    def test_postcall_sequence_email_1(self):
        """Post-call maybe sequence: email 1."""
        assert get_sequence_template_id(sequence_type="postcall", email_number=1) == "postcall_maybe_email_1"

    def test_postcall_sequence_email_2(self):
        """Post-call maybe sequence: email 2."""
        assert get_sequence_template_id(sequence_type="postcall", email_number=2) == "postcall_maybe_email_2"

    def test_onboarding_sequence_email_1(self):
        """Onboarding sequence: email 1."""
        assert get_sequence_template_id(sequence_type="onboarding", email_number=1) == "onboarding_phase1_email_1"

    def test_onboarding_sequence_email_3(self):
        """Onboarding sequence: email 3."""
        assert get_sequence_template_id(sequence_type="onboarding", email_number=3) == "onboarding_phase1_email_3"

    def test_invalid_sequence_type_raises_error(self):
        """Invalid sequence_type raises ValueError."""
        with pytest.raises(ValueError, match="Invalid sequence_type"):
            get_sequence_template_id(sequence_type="invalid", email_number=1)

    def test_invalid_email_number_raises_error(self):
        """Invalid email_number raises ValueError."""
        with pytest.raises(ValueError, match="Invalid email_number"):
            get_sequence_template_id(sequence_type="noshow", email_number=0)

        with pytest.raises(ValueError, match="Invalid email_number"):
            get_sequence_template_id(sequence_type="postcall", email_number=4)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
