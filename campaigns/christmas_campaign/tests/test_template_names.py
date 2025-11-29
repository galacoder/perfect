"""
Template Name Validation Tests (Wave 11: Template Naming Alignment).

This module validates that all template names used in code match the active templates in Notion.
These tests ensure no one accidentally references archived lead_nurture_email_* templates.

Active Templates in Notion (14 total):
- 5-Day E1, 5-Day E2, 5-Day E3, 5-Day E4, 5-Day E5 (main signup sequence)
- noshow_recovery_email_1, noshow_recovery_email_2, noshow_recovery_email_3
- postcall_maybe_email_1, postcall_maybe_email_2, postcall_maybe_email_3
- onboarding_phase1_email_1, onboarding_phase1_email_2, onboarding_phase1_email_3

Archived Templates (7 total - MUST NOT BE REFERENCED):
- lead_nurture_email_1, lead_nurture_email_2a_critical, lead_nurture_email_2b_urgent
- lead_nurture_email_2c_optimize, lead_nurture_email_3, lead_nurture_email_4, lead_nurture_email_5

Author: Coding Agent (Sonnet 4.5)
Created: 2025-11-28
Wave: 11 - Template Naming Alignment
"""

import pytest
from campaigns.christmas_campaign.tasks.routing import (
    get_email_template_id,
    get_sequence_template_id
)


# Active templates from Notion (verified by user 2025-11-28)
ACTIVE_TEMPLATES = {
    "5-Day E1",
    "5-Day E2",
    "5-Day E3",
    "5-Day E4",
    "5-Day E5",
    "noshow_recovery_email_1",
    "noshow_recovery_email_2",
    "noshow_recovery_email_3",
    "postcall_maybe_email_1",
    "postcall_maybe_email_2",
    "postcall_maybe_email_3",
    "onboarding_phase1_email_1",
    "onboarding_phase1_email_2",
    "onboarding_phase1_email_3"
}

# Archived templates (MUST NOT BE REFERENCED)
ARCHIVED_TEMPLATES = {
    "lead_nurture_email_1",
    "lead_nurture_email_2a_critical",
    "lead_nurture_email_2b_urgent",
    "lead_nurture_email_2c_optimize",
    "lead_nurture_email_3",
    "lead_nurture_email_4",
    "lead_nurture_email_5"
}


class TestActiveTemplateReferences:
    """Validate that all template references use ACTIVE templates only."""

    def test_5day_sequence_uses_active_templates(self):
        """Verify 5-Day sequence templates match active Notion templates."""
        for email_number in range(1, 6):
            for segment in ["CRITICAL", "URGENT", "OPTIMIZE"]:
                template_id = get_email_template_id(email_number, segment)

                # Assert template is in active list
                assert template_id in ACTIVE_TEMPLATES, (
                    f"Template '{template_id}' for Email {email_number} is not in active templates. "
                    f"Update routing.py to use correct template name."
                )

                # Assert template is NOT in archived list
                assert template_id not in ARCHIVED_TEMPLATES, (
                    f"Template '{template_id}' for Email {email_number} is archived! "
                    f"Must use active 5-Day E* templates instead."
                )

    def test_noshow_recovery_uses_active_templates(self):
        """Verify no-show recovery templates match active Notion templates."""
        for email_number in range(1, 4):
            template_id = get_sequence_template_id("noshow", email_number)

            assert template_id in ACTIVE_TEMPLATES, (
                f"No-show template '{template_id}' is not in active templates."
            )

            assert template_id not in ARCHIVED_TEMPLATES, (
                f"No-show template '{template_id}' is archived!"
            )

    def test_postcall_maybe_uses_active_templates(self):
        """Verify post-call maybe templates match active Notion templates."""
        for email_number in range(1, 4):
            template_id = get_sequence_template_id("postcall", email_number)

            assert template_id in ACTIVE_TEMPLATES, (
                f"Post-call template '{template_id}' is not in active templates."
            )

            assert template_id not in ARCHIVED_TEMPLATES, (
                f"Post-call template '{template_id}' is archived!"
            )

    def test_onboarding_uses_active_templates(self):
        """Verify onboarding templates match active Notion templates."""
        for email_number in range(1, 4):
            template_id = get_sequence_template_id("onboarding", email_number)

            assert template_id in ACTIVE_TEMPLATES, (
                f"Onboarding template '{template_id}' is not in active templates."
            )

            assert template_id not in ARCHIVED_TEMPLATES, (
                f"Onboarding template '{template_id}' is archived!"
            )


class TestArchivedTemplatesPrevention:
    """Ensure archived templates are NOT referenced anywhere."""

    def test_5day_templates_do_not_use_archived_names(self):
        """Ensure 5-Day sequence does NOT use archived lead_nurture_email_* names."""
        for email_number in range(1, 6):
            template_id = get_email_template_id(email_number, "CRITICAL")

            # Must NOT start with "lead_nurture_email"
            assert not template_id.startswith("lead_nurture_email"), (
                f"Template '{template_id}' uses ARCHIVED naming format! "
                f"Must use '5-Day E{email_number}' instead."
            )

            # Must start with "5-Day E"
            assert template_id.startswith("5-Day E"), (
                f"Template '{template_id}' does not follow '5-Day E*' naming convention."
            )


class TestTemplateNameFormat:
    """Validate template name format consistency."""

    def test_5day_templates_use_short_format(self):
        """Ensure 5-Day templates use SHORT format (no descriptive suffixes)."""
        for email_number in range(1, 6):
            template_id = get_email_template_id(email_number, "OPTIMIZE")

            # Must be exactly "5-Day E{N}" with no extra text
            expected = f"5-Day E{email_number}"
            assert template_id == expected, (
                f"Template name '{template_id}' should be '{expected}' (short format). "
                f"Notion templates use SHORT names without descriptive suffixes."
            )

    def test_noshow_templates_use_correct_format(self):
        """Ensure no-show templates use correct naming format."""
        for email_number in range(1, 4):
            template_id = get_sequence_template_id("noshow", email_number)
            expected = f"noshow_recovery_email_{email_number}"

            assert template_id == expected, (
                f"No-show template '{template_id}' should be '{expected}'."
            )

    def test_postcall_templates_use_correct_format(self):
        """Ensure post-call templates use correct naming format."""
        for email_number in range(1, 4):
            template_id = get_sequence_template_id("postcall", email_number)
            expected = f"postcall_maybe_email_{email_number}"

            assert template_id == expected, (
                f"Post-call template '{template_id}' should be '{expected}'."
            )

    def test_onboarding_templates_use_correct_format(self):
        """Ensure onboarding templates use correct naming format."""
        for email_number in range(1, 4):
            template_id = get_sequence_template_id("onboarding", email_number)
            expected = f"onboarding_phase1_email_{email_number}"

            assert template_id == expected, (
                f"Onboarding template '{template_id}' should be '{expected}'."
            )


class TestTemplateInventory:
    """Validate template inventory counts."""

    def test_total_active_templates_count(self):
        """Verify we have exactly 14 active templates."""
        assert len(ACTIVE_TEMPLATES) == 14, (
            f"Expected 14 active templates, found {len(ACTIVE_TEMPLATES)}. "
            f"Check Notion template database."
        )

    def test_5day_sequence_template_count(self):
        """Verify 5-Day sequence has exactly 5 templates."""
        five_day_templates = {t for t in ACTIVE_TEMPLATES if t.startswith("5-Day E")}
        assert len(five_day_templates) == 5, (
            f"Expected 5 templates in 5-Day sequence, found {len(five_day_templates)}."
        )

    def test_noshow_sequence_template_count(self):
        """Verify no-show recovery has exactly 3 templates."""
        noshow_templates = {t for t in ACTIVE_TEMPLATES if "noshow_recovery" in t}
        assert len(noshow_templates) == 3, (
            f"Expected 3 no-show recovery templates, found {len(noshow_templates)}."
        )

    def test_postcall_sequence_template_count(self):
        """Verify post-call maybe has exactly 3 templates."""
        postcall_templates = {t for t in ACTIVE_TEMPLATES if "postcall_maybe" in t}
        assert len(postcall_templates) == 3, (
            f"Expected 3 post-call maybe templates, found {len(postcall_templates)}."
        )

    def test_onboarding_sequence_template_count(self):
        """Verify onboarding has exactly 3 templates."""
        onboarding_templates = {t for t in ACTIVE_TEMPLATES if "onboarding_phase1" in t}
        assert len(onboarding_templates) == 3, (
            f"Expected 3 onboarding templates, found {len(onboarding_templates)}."
        )

    def test_archived_templates_count(self):
        """Verify we have exactly 7 archived templates."""
        assert len(ARCHIVED_TEMPLATES) == 7, (
            f"Expected 7 archived templates, found {len(ARCHIVED_TEMPLATES)}."
        )


class TestNoOverlap:
    """Ensure no overlap between active and archived templates."""

    def test_no_overlap_between_active_and_archived(self):
        """Verify no template appears in both active and archived lists."""
        overlap = ACTIVE_TEMPLATES & ARCHIVED_TEMPLATES
        assert len(overlap) == 0, (
            f"Templates found in BOTH active and archived lists: {overlap}. "
            f"Each template must be either active OR archived, not both."
        )
