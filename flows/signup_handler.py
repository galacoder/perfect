"""
DEPRECATED: This module has been moved to campaigns/businessx_canada_lead_nurture/flows/signup_handler.py

This shim provides backward compatibility during migration.
Please update your imports to use the new campaign-based structure.
"""
import warnings
from campaigns.businessx_canada_lead_nurture.flows.signup_handler import *

warnings.warn(
    "flows.signup_handler is deprecated. "
    "Use campaigns.businessx_canada_lead_nurture.flows.signup_handler instead.",
    DeprecationWarning,
    stacklevel=2
)
