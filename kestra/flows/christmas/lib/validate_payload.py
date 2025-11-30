"""
Webhook payload validator for assessment handler.

Validates incoming webhook payloads including:
- email_1_sent_at timestamp (ISO 8601 format)
- email_1_status field
- Assessment data (red_systems, orange_systems)
"""

from datetime import datetime
from typing import Dict, Any, List


class ValidationError(Exception):
    """Raised when payload validation fails."""
    pass


def validate_assessment_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate assessment webhook payload.

    Args:
        payload: Dictionary containing webhook data

    Returns:
        Dictionary with validated/normalized data and any warnings

    Raises:
        ValidationError: If payload is invalid
    """
    warnings: List[str] = []

    # Required fields
    required_fields = ["email", "first_name", "business_name", "red_systems", "orange_systems"]

    for field in required_fields:
        if field not in payload:
            raise ValidationError(f"Missing required field: {field}")

    # Validate email format (basic check)
    if "@" not in payload["email"]:
        raise ValidationError("Invalid email format")

    # Validate assessment data types
    try:
        red_systems = int(payload["red_systems"])
    except (ValueError, TypeError):
        raise ValidationError("red_systems must be an integer")

    try:
        orange_systems = int(payload["orange_systems"])
    except (ValueError, TypeError):
        raise ValidationError("orange_systems must be an integer")

    # Validate email_1_sent_at timestamp
    email_1_sent_at = payload.get("email_1_sent_at")

    if not email_1_sent_at:
        # Default to current time with warning
        email_1_sent_at = datetime.utcnow().isoformat() + "Z"
        warnings.append("⚠️  email_1_sent_at missing, defaulting to current time")
        print(warnings[-1])
    else:
        # Validate ISO 8601 format
        try:
            datetime.fromisoformat(email_1_sent_at.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            raise ValidationError(f"Invalid timestamp format for email_1_sent_at: {email_1_sent_at}. Must be ISO 8601.")

    # Validate email_1_status (optional, defaults to 'sent')
    email_1_status = payload.get("email_1_status", "sent")

    # Build validated result
    result = {
        "valid": True,
        "email": payload["email"],
        "first_name": payload["first_name"],
        "business_name": payload["business_name"],
        "red_systems": red_systems,
        "orange_systems": orange_systems,
        "email_1_sent_at": email_1_sent_at,
        "email_1_status": email_1_status
    }

    if warnings:
        result["warnings"] = warnings

    return result


# For standalone testing
if __name__ == "__main__":
    # Test valid payload
    valid_payload = {
        "email": "test@example.com",
        "first_name": "John",
        "business_name": "Acme Corp",
        "red_systems": 2,
        "orange_systems": 1,
        "email_1_sent_at": "2025-11-29T10:30:00Z",
        "email_1_status": "sent"
    }

    result = validate_assessment_payload(valid_payload)
    print("Valid payload result:", result)

    # Test payload with missing email_1_sent_at
    missing_timestamp_payload = {
        "email": "test@example.com",
        "first_name": "Jane",
        "business_name": "Tech Co",
        "red_systems": 1,
        "orange_systems": 2
    }

    result = validate_assessment_payload(missing_timestamp_payload)
    print("\nMissing timestamp result:", result)

    # Test invalid payload
    try:
        invalid_payload = {
            "email": "test@example.com",
            "first_name": "Bob",
            "business_name": "Corp Inc",
            "red_systems": "invalid",  # Should be int
            "orange_systems": 1
        }
        validate_assessment_payload(invalid_payload)
    except ValidationError as e:
        print(f"\nExpected error caught: {e}")
