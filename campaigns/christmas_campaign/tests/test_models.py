"""
Unit tests for Pydantic models in models.py.

Tests all data models for:
- Valid data acceptance
- Invalid data rejection
- Field validation
- Default values
- Custom validators

Author: Christmas Campaign Team
Created: 2025-11-28 (Wave 6)
"""

import pytest
from pydantic import ValidationError
from datetime import datetime

from campaigns.christmas_campaign.tasks.models import (
    AssessmentData,
    ContactData,
    EmailTemplate,
    EmailVariables,
    BookingData,
    CallCompleteData,
    FlowRunMetadata
)


# ==============================================================================
# AssessmentData Tests
# ==============================================================================

class TestAssessmentData:
    """Test AssessmentData model validation."""

    def test_valid_assessment_data(self):
        """Test creating valid AssessmentData."""
        data = AssessmentData(
            email="test@example.com",
            red_systems=2,
            orange_systems=3,
            yellow_systems=2,
            green_systems=1,
            assessment_score=35,
            first_name="John",
            business_name="Test Corp"
        )

        assert data.email == "test@example.com"
        assert data.red_systems == 2
        assert data.assessment_score == 35
        assert data.first_name == "John"

    def test_assessment_with_minimal_fields(self):
        """Test creating AssessmentData with only required fields."""
        data = AssessmentData(
            email="test@example.com",
            red_systems=2,
            orange_systems=3,
            yellow_systems=2,
            green_systems=1,
            assessment_score=35
        )

        assert data.email == "test@example.com"
        assert data.first_name is None
        assert data.business_name is None

    def test_assessment_total_systems_validation(self):
        """Test that total systems must equal 8."""
        # Total != 8 should raise error
        with pytest.raises(ValidationError, match="Total systems must equal 8"):
            AssessmentData(
                email="test@example.com",
                red_systems=2,
                orange_systems=2,
                yellow_systems=2,
                green_systems=1,  # Total = 7 (WRONG)
                assessment_score=50
            )

        # Total = 8 should work
        data = AssessmentData(
            email="test@example.com",
            red_systems=2,
            orange_systems=3,
            yellow_systems=2,
            green_systems=1,  # Total = 8 (CORRECT)
            assessment_score=35
        )
        assert data is not None

    def test_assessment_score_bounds(self):
        """Test assessment score must be 0-100."""
        # Score too low
        with pytest.raises(ValidationError):
            AssessmentData(
                email="test@example.com",
                red_systems=2,
                orange_systems=3,
                yellow_systems=2,
                green_systems=1,
                assessment_score=-1
            )

        # Score too high
        with pytest.raises(ValidationError):
            AssessmentData(
                email="test@example.com",
                red_systems=2,
                orange_systems=3,
                yellow_systems=2,
                green_systems=1,
                assessment_score=101
            )

    def test_assessment_systems_bounds(self):
        """Test system counts must be 0-8."""
        with pytest.raises(ValidationError):
            AssessmentData(
                email="test@example.com",
                red_systems=9,  # Too many
                orange_systems=0,
                yellow_systems=0,
                green_systems=0,
                assessment_score=0
            )

    def test_assessment_invalid_email(self):
        """Test invalid email is rejected."""
        with pytest.raises(ValidationError):
            AssessmentData(
                email="not-an-email",
                red_systems=2,
                orange_systems=3,
                yellow_systems=2,
                green_systems=1,
                assessment_score=35
            )


# ==============================================================================
# ContactData Tests
# ==============================================================================

class TestContactData:
    """Test ContactData model validation."""

    def test_valid_contact_data(self):
        """Test creating valid ContactData."""
        data = ContactData(
            email="john@testcorp.com",
            first_name="John",
            business_name="Test Corp",
            segment="URGENT",
            phase="Phase 1 Assessment",
            assessment_score=45,
            notion_page_id="abc123"
        )

        assert data.email == "john@testcorp.com"
        assert data.segment == "URGENT"
        assert data.phase == "Phase 1 Assessment"

    def test_contact_with_defaults(self):
        """Test ContactData default values."""
        data = ContactData(email="test@example.com")

        assert data.first_name == "there"
        assert data.business_name == "your business"
        assert data.segment == "OPTIMIZE"
        assert data.phase == "Phase 1 Assessment"

    def test_contact_segment_validation(self):
        """Test segment must be CRITICAL/URGENT/OPTIMIZE."""
        with pytest.raises(ValidationError):
            ContactData(
                email="test@example.com",
                segment="INVALID"
            )

    def test_contact_phase_validation(self):
        """Test phase must be valid phase name."""
        with pytest.raises(ValidationError):
            ContactData(
                email="test@example.com",
                phase="Invalid Phase"
            )

        # Valid phases should work
        valid_phases = [
            "Phase 1 Assessment",
            "Phase 1 Diagnostic",
            "Phase 2A Done-For-You",
            "Phase 2B Coaching",
            "Phase 2C DIY"
        ]

        for phase in valid_phases:
            data = ContactData(email="test@example.com", phase=phase)
            assert data.phase == phase


# ==============================================================================
# EmailTemplate Tests
# ==============================================================================

class TestEmailTemplate:
    """Test EmailTemplate model validation."""

    def test_valid_email_template(self):
        """Test creating valid EmailTemplate."""
        template = EmailTemplate(
            template_id="christmas_email_1",
            subject="Test Subject",
            html_body="<html><body>Hi {{first_name}}</body></html>",
            segment="ALL"
        )

        assert template.template_id == "christmas_email_1"
        assert template.subject == "Test Subject"
        assert template.segment == "ALL"

    def test_email_template_with_segment(self):
        """Test EmailTemplate with specific segment."""
        template = EmailTemplate(
            template_id="christmas_email_2a_critical",
            subject="Urgent: Your Business Needs Help",
            html_body="<html><body>Critical segment</body></html>",
            segment="CRITICAL"
        )

        assert template.segment == "CRITICAL"

    def test_email_template_segment_validation(self):
        """Test segment must be valid value."""
        with pytest.raises(ValidationError):
            EmailTemplate(
                template_id="test",
                subject="Test",
                html_body="<html><body>Test</body></html>",
                segment="INVALID"
            )

    def test_email_template_required_fields(self):
        """Test template_id, subject, html_body are required."""
        with pytest.raises(ValidationError):
            EmailTemplate(subject="Test", html_body="Test")

        with pytest.raises(ValidationError):
            EmailTemplate(template_id="test", html_body="Test")

        with pytest.raises(ValidationError):
            EmailTemplate(template_id="test", subject="Test")


# ==============================================================================
# EmailVariables Tests
# ==============================================================================

class TestEmailVariables:
    """Test EmailVariables model validation."""

    def test_valid_email_variables(self):
        """Test creating valid EmailVariables."""
        vars = EmailVariables(
            first_name="John",
            business_name="Test Corp",
            assessment_score=45,
            segment="URGENT",
            diagnostic_call_date="2025-11-20",
            portal_url="https://notion.so/portal"
        )

        assert vars.first_name == "John"
        assert vars.assessment_score == 45

    def test_email_variables_defaults(self):
        """Test EmailVariables default values."""
        vars = EmailVariables()

        assert vars.first_name == "there"
        assert vars.business_name == "your business"
        assert vars.assessment_score is None
        assert vars.segment is None


# ==============================================================================
# BookingData Tests
# ==============================================================================

class TestBookingData:
    """Test BookingData model validation."""

    def test_valid_booking_data(self):
        """Test creating valid BookingData."""
        booking = BookingData(
            email="john@testcorp.com",
            booking_id="12345",
            booking_uid="booking-uid-123",
            call_title="BusOS Diagnostic Call",
            start_time=datetime(2025, 11, 20, 10, 0, 0),
            end_time=datetime(2025, 11, 20, 11, 0, 0),
            attendee_name="John Doe",
            attendee_timezone="America/Toronto",
            business_name="Test Corp"
        )

        assert booking.email == "john@testcorp.com"
        assert booking.booking_id == "12345"
        assert booking.attendee_timezone == "America/Toronto"

    def test_booking_with_default_timezone(self):
        """Test BookingData default timezone."""
        booking = BookingData(
            email="john@testcorp.com",
            booking_id="12345",
            booking_uid="uid-123",
            call_title="Call",
            start_time=datetime(2025, 11, 20, 10, 0, 0),
            end_time=datetime(2025, 11, 20, 11, 0, 0),
            attendee_name="John"
        )

        assert booking.attendee_timezone == "America/Toronto"

    def test_booking_required_fields(self):
        """Test all required fields must be present."""
        with pytest.raises(ValidationError):
            BookingData(
                email="john@testcorp.com"
                # Missing other required fields
            )


# ==============================================================================
# CallCompleteData Tests
# ==============================================================================

class TestCallCompleteData:
    """Test CallCompleteData model validation."""

    def test_valid_call_complete_data(self):
        """Test creating valid CallCompleteData."""
        call = CallCompleteData(
            email="john@testcorp.com",
            call_date="2025-11-20",
            call_notes="Great call",
            next_steps="Phase 2A Done-For-You",
            portal_url="https://notion.so/portal"
        )

        assert call.email == "john@testcorp.com"
        assert call.next_steps == "Phase 2A Done-For-You"

    def test_call_next_steps_validation(self):
        """Test next_steps must be valid phase."""
        with pytest.raises(ValidationError):
            CallCompleteData(
                email="john@testcorp.com",
                call_date="2025-11-20",
                next_steps="Invalid Phase"
            )

        # Valid next_steps should work
        valid_steps = [
            "Phase 2A Done-For-You",
            "Phase 2B Coaching",
            "Phase 2C DIY",
            "No Phase 2"
        ]

        for step in valid_steps:
            call = CallCompleteData(
                email="john@testcorp.com",
                call_date="2025-11-20",
                next_steps=step
            )
            assert call.next_steps == step


# ==============================================================================
# FlowRunMetadata Tests
# ==============================================================================

class TestFlowRunMetadata:
    """Test FlowRunMetadata model validation."""

    def test_valid_flow_run_metadata(self):
        """Test creating valid FlowRunMetadata."""
        metadata = FlowRunMetadata(
            email_number=1,
            flow_run_id="flow-run-id-123",
            scheduled_time=datetime(2025, 11, 16, 12, 0, 0),
            actual_send_time=datetime(2025, 11, 16, 12, 0, 5),
            status="completed"
        )

        assert metadata.email_number == 1
        assert metadata.status == "completed"

    def test_flow_run_with_defaults(self):
        """Test FlowRunMetadata default values."""
        metadata = FlowRunMetadata(
            email_number=1,
            flow_run_id="flow-id",
            scheduled_time=datetime(2025, 11, 16, 12, 0, 0)
        )

        assert metadata.status == "scheduled"
        assert metadata.actual_send_time is None
        assert metadata.error_message is None

    def test_flow_run_email_number_bounds(self):
        """Test email_number must be 1-7."""
        with pytest.raises(ValidationError):
            FlowRunMetadata(
                email_number=0,  # Too low
                flow_run_id="flow-id",
                scheduled_time=datetime(2025, 11, 16, 12, 0, 0)
            )

        with pytest.raises(ValidationError):
            FlowRunMetadata(
                email_number=8,  # Too high
                flow_run_id="flow-id",
                scheduled_time=datetime(2025, 11, 16, 12, 0, 0)
            )

    def test_flow_run_status_validation(self):
        """Test status must be valid value."""
        with pytest.raises(ValidationError):
            FlowRunMetadata(
                email_number=1,
                flow_run_id="flow-id",
                scheduled_time=datetime(2025, 11, 16, 12, 0, 0),
                status="invalid_status"
            )

        # Valid statuses
        valid_statuses = ["scheduled", "running", "completed", "failed", "cancelled"]
        for status in valid_statuses:
            metadata = FlowRunMetadata(
                email_number=1,
                flow_run_id="flow-id",
                scheduled_time=datetime(2025, 11, 16, 12, 0, 0),
                status=status
            )
            assert metadata.status == status


# ==============================================================================
# Model Serialization Tests
# ==============================================================================

class TestModelSerialization:
    """Test model JSON serialization and deserialization."""

    def test_assessment_data_json_round_trip(self):
        """Test AssessmentData can be serialized and deserialized."""
        original = AssessmentData(
            email="test@example.com",
            red_systems=2,
            orange_systems=3,
            yellow_systems=2,
            green_systems=1,
            assessment_score=35
        )

        # Serialize to JSON
        json_str = original.model_dump_json()

        # Deserialize from JSON
        loaded = AssessmentData.model_validate_json(json_str)

        assert loaded.email == original.email
        assert loaded.red_systems == original.red_systems

    def test_contact_data_dict_conversion(self):
        """Test ContactData can convert to/from dict."""
        original = ContactData(
            email="test@example.com",
            first_name="John",
            segment="URGENT"
        )

        # Convert to dict
        data_dict = original.model_dump()

        # Create from dict
        loaded = ContactData(**data_dict)

        assert loaded.email == original.email
        assert loaded.segment == original.segment
