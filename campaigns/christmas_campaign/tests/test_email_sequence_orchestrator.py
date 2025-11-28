"""
Unit tests for email_sequence_orchestrator.py.

Tests the email sequence orchestration flow including:
- Segment classification
- Notion contact lookup and update
- Email scheduling for all 7 emails
- Discord alerts for CRITICAL segments
- Testing mode support

Author: Christmas Campaign Team
Created: 2025-11-28 (Wave 6)
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime


# ==============================================================================
# Test Fixtures
# ==============================================================================

@pytest.fixture
def mock_contact_response():
    """Mock Notion contact response."""
    return {
        "id": "contact-page-id-123",
        "object": "page",
        "properties": {
            "email": {"email": "test@example.com"},
            "first_name": {"rich_text": [{"text": {"content": "John"}}]},
            "business_name": {"title": [{"text": {"content": "Test Corp"}}]},
            "Segment": {"select": {"name": "URGENT"}},
            "Assessment Score": {"number": 45}
        }
    }


@pytest.fixture
def sample_orchestrator_input():
    """Sample input for orchestrator."""
    return {
        "email": "test@example.com",
        "red_systems": 1,
        "orange_systems": 2,
        "yellow_systems": 3,
        "green_systems": 2,
        "assessment_score": 45,
        "first_name": "John",
        "business_name": "Test Corp"
    }


# ==============================================================================
# Flow Structure Tests
# ==============================================================================

class TestEmailSequenceOrchestratorStructure:
    """Test email_sequence_orchestrator structure and parameters."""

    def test_flow_exists(self):
        """Test that email_sequence_orchestrator exists."""
        from campaigns.christmas_campaign.flows.email_sequence_orchestrator import (
            email_sequence_orchestrator
        )
        assert email_sequence_orchestrator is not None

    def test_flow_has_correct_name(self):
        """Test flow has correct Prefect name."""
        from campaigns.christmas_campaign.flows.email_sequence_orchestrator import (
            email_sequence_orchestrator
        )
        assert email_sequence_orchestrator.name == "christmas-email-sequence-orchestrator"

    def test_sync_wrapper_exists(self):
        """Test synchronous wrapper function exists."""
        from campaigns.christmas_campaign.flows.email_sequence_orchestrator import (
            email_sequence_orchestrator_sync
        )
        assert email_sequence_orchestrator_sync is not None

    def test_flow_accepts_required_parameters(self):
        """Test flow accepts required parameters."""
        from campaigns.christmas_campaign.flows.email_sequence_orchestrator import (
            email_sequence_orchestrator
        )
        import inspect
        sig = inspect.signature(email_sequence_orchestrator.fn)
        params = list(sig.parameters.keys())

        assert "email" in params
        assert "red_systems" in params
        assert "orange_systems" in params


# ==============================================================================
# Segment Classification Tests
# ==============================================================================

class TestSegmentClassification:
    """Test segment classification within orchestrator."""

    @pytest.mark.asyncio
    @patch('campaigns.christmas_campaign.flows.email_sequence_orchestrator.search_contact_by_email')
    @patch('campaigns.christmas_campaign.flows.email_sequence_orchestrator.update_assessment_data')
    @patch('campaigns.christmas_campaign.flows.email_sequence_orchestrator.update_contact_phase')
    @patch('campaigns.christmas_campaign.flows.email_sequence_orchestrator.schedule_email_flow')
    async def test_classifies_critical_segment(
        self, mock_schedule, mock_phase, mock_update, mock_search,
        mock_contact_response
    ):
        """Test CRITICAL segment classification."""
        from campaigns.christmas_campaign.flows.email_sequence_orchestrator import (
            email_sequence_orchestrator
        )

        mock_search.return_value = mock_contact_response
        mock_schedule.return_value = "test-flow-run-id"

        result = await email_sequence_orchestrator(
            email="test@example.com",
            red_systems=3,  # CRITICAL: 2+ red systems
            orange_systems=1,
            yellow_systems=2,
            green_systems=2,
            assessment_score=20
        )

        assert result["segment"] == "CRITICAL"

    @pytest.mark.asyncio
    @patch('campaigns.christmas_campaign.flows.email_sequence_orchestrator.search_contact_by_email')
    @patch('campaigns.christmas_campaign.flows.email_sequence_orchestrator.update_assessment_data')
    @patch('campaigns.christmas_campaign.flows.email_sequence_orchestrator.update_contact_phase')
    @patch('campaigns.christmas_campaign.flows.email_sequence_orchestrator.schedule_email_flow')
    async def test_classifies_urgent_segment(
        self, mock_schedule, mock_phase, mock_update, mock_search,
        mock_contact_response
    ):
        """Test URGENT segment classification."""
        from campaigns.christmas_campaign.flows.email_sequence_orchestrator import (
            email_sequence_orchestrator
        )

        mock_search.return_value = mock_contact_response
        mock_schedule.return_value = "test-flow-run-id"

        result = await email_sequence_orchestrator(
            email="test@example.com",
            red_systems=1,  # URGENT: 1 red system
            orange_systems=2,
            yellow_systems=3,
            green_systems=2,
            assessment_score=40
        )

        assert result["segment"] == "URGENT"

    @pytest.mark.asyncio
    @patch('campaigns.christmas_campaign.flows.email_sequence_orchestrator.search_contact_by_email')
    @patch('campaigns.christmas_campaign.flows.email_sequence_orchestrator.update_assessment_data')
    @patch('campaigns.christmas_campaign.flows.email_sequence_orchestrator.update_contact_phase')
    @patch('campaigns.christmas_campaign.flows.email_sequence_orchestrator.schedule_email_flow')
    async def test_classifies_optimize_segment(
        self, mock_schedule, mock_phase, mock_update, mock_search,
        mock_contact_response
    ):
        """Test OPTIMIZE segment classification."""
        from campaigns.christmas_campaign.flows.email_sequence_orchestrator import (
            email_sequence_orchestrator
        )

        mock_search.return_value = mock_contact_response
        mock_schedule.return_value = "test-flow-run-id"

        result = await email_sequence_orchestrator(
            email="test@example.com",
            red_systems=0,  # OPTIMIZE: no red systems, <2 orange
            orange_systems=1,
            yellow_systems=4,
            green_systems=3,
            assessment_score=65
        )

        assert result["segment"] == "OPTIMIZE"


# ==============================================================================
# Contact Lookup Tests
# ==============================================================================

class TestContactLookup:
    """Test Notion contact lookup behavior."""

    @pytest.mark.asyncio
    @patch('campaigns.christmas_campaign.flows.email_sequence_orchestrator.search_contact_by_email')
    async def test_returns_error_when_contact_not_found(self, mock_search):
        """Test flow returns error when contact not found."""
        from campaigns.christmas_campaign.flows.email_sequence_orchestrator import (
            email_sequence_orchestrator
        )

        mock_search.return_value = None

        result = await email_sequence_orchestrator(
            email="unknown@example.com",
            red_systems=1,
            orange_systems=2,
            yellow_systems=3,
            green_systems=2,  # Total = 8
            assessment_score=45
        )

        assert result["status"] == "failed"
        assert "not found" in result["error"].lower()

    @pytest.mark.asyncio
    @patch('campaigns.christmas_campaign.flows.email_sequence_orchestrator.search_contact_by_email')
    @patch('campaigns.christmas_campaign.flows.email_sequence_orchestrator.update_assessment_data')
    @patch('campaigns.christmas_campaign.flows.email_sequence_orchestrator.update_contact_phase')
    @patch('campaigns.christmas_campaign.flows.email_sequence_orchestrator.schedule_email_flow')
    async def test_finds_contact_successfully(
        self, mock_schedule, mock_phase, mock_update, mock_search,
        mock_contact_response
    ):
        """Test flow finds contact successfully."""
        from campaigns.christmas_campaign.flows.email_sequence_orchestrator import (
            email_sequence_orchestrator
        )

        mock_search.return_value = mock_contact_response
        mock_schedule.return_value = "test-flow-run-id"

        result = await email_sequence_orchestrator(
            email="test@example.com",
            red_systems=0,
            orange_systems=1,
            yellow_systems=3,
            green_systems=4,  # Total = 8
            assessment_score=65
        )

        mock_search.assert_called_once_with("test@example.com")
        assert result["status"] == "success"


# ==============================================================================
# Notion Update Tests
# ==============================================================================

class TestNotionUpdates:
    """Test Notion database updates."""

    @pytest.mark.asyncio
    @patch('campaigns.christmas_campaign.flows.email_sequence_orchestrator.search_contact_by_email')
    @patch('campaigns.christmas_campaign.flows.email_sequence_orchestrator.update_assessment_data')
    @patch('campaigns.christmas_campaign.flows.email_sequence_orchestrator.update_contact_phase')
    @patch('campaigns.christmas_campaign.flows.email_sequence_orchestrator.schedule_email_flow')
    async def test_updates_assessment_data(
        self, mock_schedule, mock_phase, mock_update, mock_search,
        mock_contact_response
    ):
        """Test flow updates assessment data in Notion."""
        from campaigns.christmas_campaign.flows.email_sequence_orchestrator import (
            email_sequence_orchestrator
        )

        mock_search.return_value = mock_contact_response
        mock_schedule.return_value = "test-flow-run-id"

        await email_sequence_orchestrator(
            email="test@example.com",
            red_systems=2,
            orange_systems=3,
            yellow_systems=2,
            green_systems=1,
            assessment_score=35
        )

        mock_update.assert_called_once()
        call_kwargs = mock_update.call_args[1]

        assert call_kwargs["page_id"] == "contact-page-id-123"
        assert call_kwargs["assessment_score"] == 35
        assert call_kwargs["red_systems"] == 2
        assert call_kwargs["orange_systems"] == 3

    @pytest.mark.asyncio
    @patch('campaigns.christmas_campaign.flows.email_sequence_orchestrator.search_contact_by_email')
    @patch('campaigns.christmas_campaign.flows.email_sequence_orchestrator.update_assessment_data')
    @patch('campaigns.christmas_campaign.flows.email_sequence_orchestrator.update_contact_phase')
    @patch('campaigns.christmas_campaign.flows.email_sequence_orchestrator.schedule_email_flow')
    async def test_updates_contact_phase(
        self, mock_schedule, mock_phase, mock_update, mock_search,
        mock_contact_response
    ):
        """Test flow updates contact phase in Notion."""
        from campaigns.christmas_campaign.flows.email_sequence_orchestrator import (
            email_sequence_orchestrator
        )

        mock_search.return_value = mock_contact_response
        mock_schedule.return_value = "test-flow-run-id"

        await email_sequence_orchestrator(
            email="test@example.com",
            red_systems=0,
            orange_systems=1,
            yellow_systems=3,
            green_systems=4,  # Total = 8
            assessment_score=70
        )

        mock_phase.assert_called_once_with(
            "contact-page-id-123",
            "Phase 1 Assessment"
        )


# ==============================================================================
# Email Scheduling Tests
# ==============================================================================

class TestEmailScheduling:
    """Test email flow scheduling."""

    @pytest.mark.asyncio
    @patch('campaigns.christmas_campaign.flows.email_sequence_orchestrator.search_contact_by_email')
    @patch('campaigns.christmas_campaign.flows.email_sequence_orchestrator.update_assessment_data')
    @patch('campaigns.christmas_campaign.flows.email_sequence_orchestrator.update_contact_phase')
    @patch('campaigns.christmas_campaign.flows.email_sequence_orchestrator.schedule_email_flow')
    async def test_schedules_all_seven_emails(
        self, mock_schedule, mock_phase, mock_update, mock_search,
        mock_contact_response
    ):
        """Test flow schedules all 7 email flows."""
        from campaigns.christmas_campaign.flows.email_sequence_orchestrator import (
            email_sequence_orchestrator
        )

        mock_search.return_value = mock_contact_response
        mock_schedule.return_value = "test-flow-run-id"

        result = await email_sequence_orchestrator(
            email="test@example.com",
            red_systems=0,
            orange_systems=1,
            yellow_systems=3,
            green_systems=4,  # Total = 8
            assessment_score=70
        )

        # Verify 7 emails were scheduled
        assert mock_schedule.call_count == 7
        assert len(result["scheduled_flows"]) == 7

    @pytest.mark.asyncio
    @patch('campaigns.christmas_campaign.flows.email_sequence_orchestrator.search_contact_by_email')
    @patch('campaigns.christmas_campaign.flows.email_sequence_orchestrator.update_assessment_data')
    @patch('campaigns.christmas_campaign.flows.email_sequence_orchestrator.update_contact_phase')
    @patch('campaigns.christmas_campaign.flows.email_sequence_orchestrator.schedule_email_flow')
    async def test_scheduled_flows_have_correct_structure(
        self, mock_schedule, mock_phase, mock_update, mock_search,
        mock_contact_response
    ):
        """Test scheduled flow entries have correct structure."""
        from campaigns.christmas_campaign.flows.email_sequence_orchestrator import (
            email_sequence_orchestrator
        )

        mock_search.return_value = mock_contact_response
        mock_schedule.return_value = "test-flow-run-123"

        result = await email_sequence_orchestrator(
            email="test@example.com",
            red_systems=0,
            orange_systems=1,
            yellow_systems=3,
            green_systems=4,  # Total = 8
            assessment_score=70
        )

        for i, scheduled in enumerate(result["scheduled_flows"], 1):
            assert scheduled["email_number"] == i
            assert "flow_run_id" in scheduled
            assert "delay" in scheduled
            assert "delay_unit" in scheduled

    @pytest.mark.asyncio
    @patch.dict('os.environ', {'TESTING_MODE': 'true'})
    @patch('campaigns.christmas_campaign.flows.email_sequence_orchestrator.search_contact_by_email')
    @patch('campaigns.christmas_campaign.flows.email_sequence_orchestrator.update_assessment_data')
    @patch('campaigns.christmas_campaign.flows.email_sequence_orchestrator.update_contact_phase')
    @patch('campaigns.christmas_campaign.flows.email_sequence_orchestrator.schedule_email_flow')
    async def test_testing_mode_uses_minutes(
        self, mock_schedule, mock_phase, mock_update, mock_search,
        mock_contact_response
    ):
        """Test testing mode uses minutes for delays."""
        from campaigns.christmas_campaign.flows.email_sequence_orchestrator import (
            email_sequence_orchestrator
        )

        mock_search.return_value = mock_contact_response
        mock_schedule.return_value = "test-flow-run-id"

        result = await email_sequence_orchestrator(
            email="test@example.com",
            red_systems=0,
            orange_systems=1,
            yellow_systems=3,
            green_systems=4,  # Total = 8
            assessment_score=70
        )

        assert result["testing_mode"] == True
        for scheduled in result["scheduled_flows"]:
            assert scheduled["delay_unit"] == "minutes"


# ==============================================================================
# Discord Alert Tests
# ==============================================================================

class TestDiscordAlerts:
    """Test Discord alerting for CRITICAL segments."""

    @pytest.mark.asyncio
    @patch('campaigns.christmas_campaign.flows.email_sequence_orchestrator.search_contact_by_email')
    @patch('campaigns.christmas_campaign.flows.email_sequence_orchestrator.update_assessment_data')
    @patch('campaigns.christmas_campaign.flows.email_sequence_orchestrator.update_contact_phase')
    @patch('campaigns.christmas_campaign.flows.email_sequence_orchestrator.schedule_email_flow')
    @patch('campaigns.christmas_campaign.flows.email_sequence_orchestrator.should_send_discord_alert')
    async def test_discord_alert_triggered_for_critical(
        self, mock_discord_check, mock_schedule, mock_phase, mock_update, mock_search,
        mock_contact_response
    ):
        """Test Discord alert is triggered for CRITICAL segment."""
        from campaigns.christmas_campaign.flows.email_sequence_orchestrator import (
            email_sequence_orchestrator
        )

        mock_search.return_value = mock_contact_response
        mock_schedule.return_value = "test-flow-run-id"
        mock_discord_check.return_value = True

        result = await email_sequence_orchestrator(
            email="test@example.com",
            red_systems=3,  # CRITICAL
            orange_systems=1,
            yellow_systems=2,
            green_systems=2,  # Total = 8
            assessment_score=20
        )

        # Verify discord alert check was called
        mock_discord_check.assert_called_with("CRITICAL")
        assert result["segment"] == "CRITICAL"


# ==============================================================================
# Error Handling Tests
# ==============================================================================

class TestErrorHandling:
    """Test error handling in orchestrator."""

    @pytest.mark.asyncio
    @patch('campaigns.christmas_campaign.flows.email_sequence_orchestrator.search_contact_by_email')
    async def test_handles_notion_search_error(self, mock_search):
        """Test flow handles Notion search error gracefully."""
        from campaigns.christmas_campaign.flows.email_sequence_orchestrator import (
            email_sequence_orchestrator
        )

        mock_search.side_effect = Exception("Notion API error")

        result = await email_sequence_orchestrator(
            email="test@example.com",
            red_systems=0,
            orange_systems=1,
            yellow_systems=3,
            green_systems=4,  # Total = 8
            assessment_score=70
        )

        assert result["status"] == "failed"
        assert "error" in result

    @pytest.mark.asyncio
    @patch('campaigns.christmas_campaign.flows.email_sequence_orchestrator.search_contact_by_email')
    @patch('campaigns.christmas_campaign.flows.email_sequence_orchestrator.update_assessment_data')
    async def test_handles_update_error(
        self, mock_update, mock_search, mock_contact_response
    ):
        """Test flow handles update error gracefully."""
        from campaigns.christmas_campaign.flows.email_sequence_orchestrator import (
            email_sequence_orchestrator
        )

        mock_search.return_value = mock_contact_response
        mock_update.side_effect = Exception("Update failed")

        result = await email_sequence_orchestrator(
            email="test@example.com",
            red_systems=0,
            orange_systems=1,
            yellow_systems=3,
            green_systems=4,  # Total = 8
            assessment_score=70
        )

        assert result["status"] == "failed"
        assert "error" in result


# ==============================================================================
# End-to-End Flow Tests
# ==============================================================================

class TestOrchestratorE2E:
    """End-to-end tests for orchestrator."""

    @pytest.mark.asyncio
    @patch('campaigns.christmas_campaign.flows.email_sequence_orchestrator.search_contact_by_email')
    @patch('campaigns.christmas_campaign.flows.email_sequence_orchestrator.update_assessment_data')
    @patch('campaigns.christmas_campaign.flows.email_sequence_orchestrator.update_contact_phase')
    @patch('campaigns.christmas_campaign.flows.email_sequence_orchestrator.schedule_email_flow')
    async def test_complete_successful_orchestration(
        self, mock_schedule, mock_phase, mock_update, mock_search,
        mock_contact_response, sample_orchestrator_input
    ):
        """Test complete successful orchestration flow."""
        from campaigns.christmas_campaign.flows.email_sequence_orchestrator import (
            email_sequence_orchestrator
        )

        mock_search.return_value = mock_contact_response
        mock_schedule.return_value = "test-e2e-flow-id"

        result = await email_sequence_orchestrator(**sample_orchestrator_input)

        # Verify all steps completed
        assert result["status"] == "success"
        assert result["email"] == "test@example.com"
        assert "segment" in result
        assert result["assessment_score"] == 45
        assert len(result["scheduled_flows"]) == 7
        assert "orchestrated_at" in result

        # Verify call sequence
        mock_search.assert_called_once()
        mock_update.assert_called_once()
        mock_phase.assert_called_once()
        assert mock_schedule.call_count == 7

    @pytest.mark.asyncio
    @patch('campaigns.christmas_campaign.flows.email_sequence_orchestrator.search_contact_by_email')
    @patch('campaigns.christmas_campaign.flows.email_sequence_orchestrator.update_assessment_data')
    @patch('campaigns.christmas_campaign.flows.email_sequence_orchestrator.update_contact_phase')
    @patch('campaigns.christmas_campaign.flows.email_sequence_orchestrator.schedule_email_flow')
    async def test_result_contains_all_required_fields(
        self, mock_schedule, mock_phase, mock_update, mock_search,
        mock_contact_response
    ):
        """Test result contains all required fields."""
        from campaigns.christmas_campaign.flows.email_sequence_orchestrator import (
            email_sequence_orchestrator
        )

        mock_search.return_value = mock_contact_response
        mock_schedule.return_value = "test-flow-id"

        result = await email_sequence_orchestrator(
            email="test@example.com",
            red_systems=0,
            orange_systems=1,
            yellow_systems=3,
            green_systems=4,  # Total = 8
            assessment_score=60
        )

        required_fields = [
            "status", "email", "segment", "assessment_score",
            "testing_mode", "scheduled_flows", "total_duration_hours",
            "orchestrated_at"
        ]

        for field in required_fields:
            assert field in result, f"Missing field: {field}"
