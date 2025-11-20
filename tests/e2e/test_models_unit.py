"""
Unit tests for Christmas Campaign Pydantic models.

This module tests all data validation models:
- AssessmentData - Assessment data validation
- ContactData - Contact data validation
- EmailTemplate - Email template data validation
- EmailVariables - Email variable validation
- BookingData - Cal.com booking data validation
- CallCompleteData - Call completion data validation
- FlowRunMetadata - Flow run metadata validation

Coverage target: 100% of models.py
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


# ===== AssessmentData tests =====

class TestAssessmentData:
    """Test AssessmentData model validation."""

    def test_valid_assessment_data(self):
        """Valid assessment data passes validation."""
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

    def test_assessment_minimal_required_fields(self):
        """Assessment with only required fields passes."""
        data = AssessmentData(
            email="test@example.com",
            red_systems=2,
            orange_systems=2,
            yellow_systems=2,
            green_systems=2,
            assessment_score=50
        )
        assert data.first_name is None
        assert data.business_name is None

    def test_invalid_email_format(self):
        """Invalid email format raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            AssessmentData(
                email="not-an-email",
                red_systems=2,
                orange_systems=2,
                yellow_systems=2,
                green_systems=2,
                assessment_score=50
            )
        assert "email" in str(exc_info.value).lower()

    def test_systems_total_not_8_fails(self):
        """Total systems != 8 raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            AssessmentData(
                email="test@example.com",
                red_systems=2,
                orange_systems=2,
                yellow_systems=2,
                green_systems=3,  # Total = 9, should be 8
                assessment_score=50
            )
        assert "Total systems must equal 8" in str(exc_info.value)

    def test_red_systems_exceeds_max(self):
        """red_systems > 8 raises ValidationError."""
        with pytest.raises(ValidationError):
            AssessmentData(
                email="test@example.com",
                red_systems=9,  # Max is 8
                orange_systems=0,
                yellow_systems=0,
                green_systems=0,
                assessment_score=0
            )

    def test_negative_systems_fails(self):
        """Negative system count raises ValidationError."""
        with pytest.raises(ValidationError):
            AssessmentData(
                email="test@example.com",
                red_systems=-1,  # Negative not allowed
                orange_systems=3,
                yellow_systems=3,
                green_systems=3,
                assessment_score=50
            )

    def test_assessment_score_out_of_range(self):
        """Assessment score outside 0-100 raises ValidationError."""
        with pytest.raises(ValidationError):
            AssessmentData(
                email="test@example.com",
                red_systems=2,
                orange_systems=2,
                yellow_systems=2,
                green_systems=2,
                assessment_score=101  # Max is 100
            )

    def test_all_green_systems(self):
        """All 8 systems green is valid."""
        data = AssessmentData(
            email="test@example.com",
            red_systems=0,
            orange_systems=0,
            yellow_systems=0,
            green_systems=8,
            assessment_score=100
        )
        assert data.green_systems == 8

    def test_all_red_systems(self):
        """All 8 systems red is valid."""
        data = AssessmentData(
            email="test@example.com",
            red_systems=8,
            orange_systems=0,
            yellow_systems=0,
            green_systems=0,
            assessment_score=0
        )
        assert data.red_systems == 8


# ===== ContactData tests =====

class TestContactData:
    """Test ContactData model validation."""

    def test_valid_contact_data(self):
        """Valid contact data passes validation."""
        data = ContactData(
            email="john@testcorp.com",
            first_name="John",
            business_name="Test Corp",
            segment="URGENT",
            phase="Phase 1 Diagnostic",
            assessment_score=45,
            notion_page_id="abc123"
        )
        assert data.email == "john@testcorp.com"
        assert data.segment == "URGENT"

    def test_contact_minimal_required_fields(self):
        """Contact with only email passes (defaults applied)."""
        data = ContactData(email="test@example.com")
        assert data.first_name == "there"  # Default
        assert data.business_name == "your business"  # Default
        assert data.segment == "OPTIMIZE"  # Default
        assert data.phase == "Phase 1 Assessment"  # Default

    def test_invalid_segment_fails(self):
        """Invalid segment value raises ValidationError."""
        with pytest.raises(ValidationError):
            ContactData(
                email="test@example.com",
                segment="INVALID_SEGMENT"  # Not in Literal
            )

    def test_invalid_phase_fails(self):
        """Invalid phase value raises ValidationError."""
        with pytest.raises(ValidationError):
            ContactData(
                email="test@example.com",
                phase="Invalid Phase"  # Not in Literal
            )

    def test_assessment_score_validation(self):
        """Assessment score must be 0-100."""
        with pytest.raises(ValidationError):
            ContactData(
                email="test@example.com",
                assessment_score=150  # Out of range
            )

    def test_all_phases_valid(self):
        """All valid phase values work."""
        phases = [
            "Phase 1 Assessment",
            "Phase 1 Diagnostic",
            "Phase 2A Done-For-You",
            "Phase 2B Coaching",
            "Phase 2C DIY"
        ]
        for phase in phases:
            data = ContactData(email="test@example.com", phase=phase)
            assert data.phase == phase

    def test_all_segments_valid(self):
        """All valid segment values work."""
        for segment in ["CRITICAL", "URGENT", "OPTIMIZE"]:
            data = ContactData(email="test@example.com", segment=segment)
            assert data.segment == segment


# ===== EmailTemplate tests =====

class TestEmailTemplate:
    """Test EmailTemplate model validation."""

    def test_valid_email_template(self):
        """Valid email template passes validation."""
        template = EmailTemplate(
            template_id="christmas_email_1",
            subject="Your BusOS Assessment Results",
            html_body="<html><body>Hi {{first_name}}...</body></html>",
            segment="ALL"
        )
        assert template.template_id == "christmas_email_1"
        assert "{{first_name}}" in template.html_body

    def test_template_minimal_fields(self):
        """Template with required fields only passes."""
        template = EmailTemplate(
            template_id="test_email",
            subject="Test Subject",
            html_body="<html><body>Test</body></html>"
        )
        assert template.segment == "ALL"  # Default

    def test_missing_required_fields_fails(self):
        """Missing required fields raises ValidationError."""
        with pytest.raises(ValidationError):
            EmailTemplate(
                template_id="test",
                subject="Test"
                # Missing html_body
            )

    def test_segment_specific_template(self):
        """Segment-specific template validates."""
        for segment in ["CRITICAL", "URGENT", "OPTIMIZE"]:
            template = EmailTemplate(
                template_id=f"christmas_email_2a_{segment.lower()}",
                subject="Test",
                html_body="<html>Test</html>",
                segment=segment
            )
            assert template.segment == segment

    def test_invalid_segment_fails(self):
        """Invalid segment value raises ValidationError."""
        with pytest.raises(ValidationError):
            EmailTemplate(
                template_id="test",
                subject="Test",
                html_body="<html>Test</html>",
                segment="INVALID"
            )


# ===== EmailVariables tests =====

class TestEmailVariables:
    """Test EmailVariables model validation."""

    def test_valid_email_variables(self):
        """Valid email variables pass validation."""
        variables = EmailVariables(
            first_name="John",
            business_name="Test Corp",
            assessment_score=45,
            segment="URGENT",
            diagnostic_call_date="2025-11-20",
            portal_url="https://notion.so/portal-123"
        )
        assert variables.first_name == "John"
        assert variables.assessment_score == 45

    def test_variables_with_defaults(self):
        """Variables use defaults for missing fields."""
        variables = EmailVariables()
        assert variables.first_name == "there"  # Default
        assert variables.business_name == "your business"  # Default
        assert variables.assessment_score is None
        assert variables.segment is None

    def test_custom_first_name(self):
        """Custom first_name overrides default."""
        variables = EmailVariables(first_name="Jane")
        assert variables.first_name == "Jane"

    def test_optional_fields_can_be_none(self):
        """Optional fields can be None."""
        variables = EmailVariables(
            first_name="John",
            assessment_score=None,
            diagnostic_call_date=None
        )
        assert variables.assessment_score is None
        assert variables.diagnostic_call_date is None


# ===== BookingData tests =====

class TestBookingData:
    """Test BookingData model validation."""

    def test_valid_booking_data(self):
        """Valid booking data passes validation."""
        booking = BookingData(
            email="john@testcorp.com",
            booking_id="12345",
            booking_uid="booking-uid-123",
            call_title="BusOS Diagnostic Call",
            start_time=datetime(2025, 11, 20, 10, 0),
            end_time=datetime(2025, 11, 20, 11, 0),
            attendee_name="John Doe",
            attendee_timezone="America/Toronto",
            business_name="Test Corp"
        )
        assert booking.email == "john@testcorp.com"
        assert booking.start_time.hour == 10

    def test_booking_minimal_required_fields(self):
        """Booking with only required fields passes."""
        booking = BookingData(
            email="test@example.com",
            booking_id="123",
            booking_uid="uid-123",
            call_title="Test Call",
            start_time=datetime(2025, 11, 20, 10, 0),
            end_time=datetime(2025, 11, 20, 11, 0),
            attendee_name="Test User"
        )
        assert booking.attendee_timezone == "America/Toronto"  # Default
        assert booking.business_name is None

    def test_invalid_email_fails(self):
        """Invalid email raises ValidationError."""
        with pytest.raises(ValidationError):
            BookingData(
                email="not-an-email",
                booking_id="123",
                booking_uid="uid-123",
                call_title="Test",
                start_time=datetime(2025, 11, 20, 10, 0),
                end_time=datetime(2025, 11, 20, 11, 0),
                attendee_name="Test"
            )

    def test_datetime_fields_required(self):
        """DateTime fields are required."""
        with pytest.raises(ValidationError):
            BookingData(
                email="test@example.com",
                booking_id="123",
                booking_uid="uid-123",
                call_title="Test",
                # Missing start_time and end_time
                attendee_name="Test"
            )


# ===== CallCompleteData tests =====

class TestCallCompleteData:
    """Test CallCompleteData model validation."""

    def test_valid_call_complete_data(self):
        """Valid call complete data passes validation."""
        data = CallCompleteData(
            email="john@testcorp.com",
            call_date="2025-11-20",
            call_notes="Great call, customer ready for DFY",
            next_steps="Phase 2A Done-For-You",
            portal_url="https://notion.so/portal-123"
        )
        assert data.email == "john@testcorp.com"
        assert data.next_steps == "Phase 2A Done-For-You"

    def test_call_complete_minimal_fields(self):
        """Call complete with only required fields passes."""
        data = CallCompleteData(
            email="test@example.com",
            call_date="2025-11-20",
            next_steps="No Phase 2"
        )
        assert data.call_notes is None
        assert data.portal_url is None

    def test_invalid_next_steps_fails(self):
        """Invalid next_steps value raises ValidationError."""
        with pytest.raises(ValidationError):
            CallCompleteData(
                email="test@example.com",
                call_date="2025-11-20",
                next_steps="Invalid Phase"  # Not in Literal
            )

    def test_all_next_steps_valid(self):
        """All valid next_steps values work."""
        next_steps_options = [
            "Phase 2A Done-For-You",
            "Phase 2B Coaching",
            "Phase 2C DIY",
            "No Phase 2"
        ]
        for next_steps in next_steps_options:
            data = CallCompleteData(
                email="test@example.com",
                call_date="2025-11-20",
                next_steps=next_steps
            )
            assert data.next_steps == next_steps


# ===== FlowRunMetadata tests =====

class TestFlowRunMetadata:
    """Test FlowRunMetadata model validation."""

    def test_valid_flow_run_metadata(self):
        """Valid flow run metadata passes validation."""
        metadata = FlowRunMetadata(
            email_number=1,
            flow_run_id="flow-run-id-123",
            scheduled_time=datetime(2025, 11, 16, 12, 0),
            actual_send_time=datetime(2025, 11, 16, 12, 0, 5),
            status="completed"
        )
        assert metadata.email_number == 1
        assert metadata.status == "completed"

    def test_flow_run_minimal_fields(self):
        """Flow run with only required fields passes."""
        metadata = FlowRunMetadata(
            email_number=3,
            flow_run_id="flow-123",
            scheduled_time=datetime(2025, 11, 20, 10, 0)
        )
        assert metadata.status == "scheduled"  # Default
        assert metadata.actual_send_time is None
        assert metadata.error_message is None

    def test_email_number_validation(self):
        """email_number must be 1-7."""
        # Valid range
        for num in range(1, 8):
            metadata = FlowRunMetadata(
                email_number=num,
                flow_run_id="flow-123",
                scheduled_time=datetime(2025, 11, 20, 10, 0)
            )
            assert metadata.email_number == num

        # Out of range
        with pytest.raises(ValidationError):
            FlowRunMetadata(
                email_number=0,  # Too low
                flow_run_id="flow-123",
                scheduled_time=datetime(2025, 11, 20, 10, 0)
            )

        with pytest.raises(ValidationError):
            FlowRunMetadata(
                email_number=8,  # Too high
                flow_run_id="flow-123",
                scheduled_time=datetime(2025, 11, 20, 10, 0)
            )

    def test_all_status_values_valid(self):
        """All valid status values work."""
        statuses = ["scheduled", "running", "completed", "failed", "cancelled"]
        for status in statuses:
            metadata = FlowRunMetadata(
                email_number=1,
                flow_run_id="flow-123",
                scheduled_time=datetime(2025, 11, 20, 10, 0),
                status=status
            )
            assert metadata.status == status

    def test_invalid_status_fails(self):
        """Invalid status value raises ValidationError."""
        with pytest.raises(ValidationError):
            FlowRunMetadata(
                email_number=1,
                flow_run_id="flow-123",
                scheduled_time=datetime(2025, 11, 20, 10, 0),
                status="invalid_status"
            )

    def test_failed_status_with_error_message(self):
        """Failed status can include error message."""
        metadata = FlowRunMetadata(
            email_number=1,
            flow_run_id="flow-123",
            scheduled_time=datetime(2025, 11, 20, 10, 0),
            status="failed",
            error_message="Email send failed: API error"
        )
        assert metadata.status == "failed"
        assert "API error" in metadata.error_message


# ===== Integration tests =====

class TestModelsIntegration:
    """Test models work together correctly."""

    def test_assessment_to_contact_workflow(self):
        """Test converting assessment data to contact data."""
        # Step 1: Receive assessment
        assessment = AssessmentData(
            email="john@testcorp.com",
            red_systems=3,
            orange_systems=2,
            yellow_systems=2,
            green_systems=1,
            assessment_score=32,
            first_name="John",
            business_name="Test Corp"
        )

        # Step 2: Create contact from assessment
        contact = ContactData(
            email=assessment.email,
            first_name=assessment.first_name or "there",
            business_name=assessment.business_name or "your business",
            segment="CRITICAL",  # Would be determined by classify_segment()
            assessment_score=assessment.assessment_score
        )

        assert contact.email == assessment.email
        assert contact.first_name == assessment.first_name
        assert contact.segment == "CRITICAL"

    def test_email_template_with_variables(self):
        """Test email template with variable substitution."""
        template = EmailTemplate(
            template_id="christmas_email_1",
            subject="Hi {{first_name}}!",
            html_body="<html><body>Hi {{first_name}} from {{business_name}}</body></html>",
            segment="ALL"
        )

        variables = EmailVariables(
            first_name="John",
            business_name="Test Corp"
        )

        # Verify placeholders exist
        assert "{{first_name}}" in template.subject
        assert "{{first_name}}" in template.html_body
        assert "{{business_name}}" in template.html_body

    def test_booking_to_flow_run_workflow(self):
        """Test booking triggering flow run."""
        # Step 1: Receive booking
        booking = BookingData(
            email="john@testcorp.com",
            booking_id="12345",
            booking_uid="uid-123",
            call_title="BusOS Diagnostic",
            start_time=datetime(2025, 11, 25, 10, 0),
            end_time=datetime(2025, 11, 25, 11, 0),
            attendee_name="John Doe"
        )

        # Step 2: Create flow run metadata
        flow_run = FlowRunMetadata(
            email_number=1,
            flow_run_id="flow-run-abc123",
            scheduled_time=booking.start_time,
            status="scheduled"
        )

        assert flow_run.scheduled_time == booking.start_time
        assert flow_run.status == "scheduled"
