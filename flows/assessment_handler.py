"""
DEPRECATED: This module has been moved to campaigns/businessx_canada_lead_nurture/flows/assessment_handler.py

This shim provides backward compatibility during migration.
Please update your imports to use the new campaign-based structure.
"""
import warnings
from campaigns.businessx_canada_lead_nurture.flows.assessment_handler import *

warnings.warn(
    "flows.assessment_handler is deprecated. "
    "Use campaigns.businessx_canada_lead_nurture.flows.assessment_handler instead.",
    DeprecationWarning,
    stacklevel=2
)
