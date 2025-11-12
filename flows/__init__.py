"""
BusOS Email Sequence Flows - Prefect workflow orchestration.

This package contains three main flows:
- signup_handler: Process new user signups
- assessment_handler: Process completed BusOS assessments
- email_sequence: Execute 5-email nurture sequence with timing

All flows integrate with Notion (contacts DB) and Resend (email delivery).
"""

from flows.signup_handler import signup_handler_flow
from flows.assessment_handler import assessment_handler_flow
from flows.email_sequence import email_sequence_flow

__all__ = [
    "signup_handler_flow",
    "assessment_handler_flow",
    "email_sequence_flow"
]
