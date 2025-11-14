"""
DEPRECATED: This module has been moved to campaigns/businessx_canada_lead_nurture/flows/email_sequence.py

This shim provides backward compatibility during migration.
Please update your imports to use the new campaign-based structure.
"""
import warnings
from campaigns.businessx_canada_lead_nurture.flows.email_sequence import *

warnings.warn(
    "flows.email_sequence is deprecated. "
    "Use campaigns.businessx_canada_lead_nurture.flows.email_sequence instead.",
    DeprecationWarning,
    stacklevel=2
)
