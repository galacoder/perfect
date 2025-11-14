"""
DEPRECATED: This module has been moved to campaigns/businessx_canada_lead_nurture/tasks/resend_operations.py

This shim provides backward compatibility during migration.
Please update your imports to use the new campaign-based structure.
"""
import warnings
from campaigns.businessx_canada_lead_nurture.tasks.resend_operations import *

warnings.warn(
    "tasks.resend_operations is deprecated. "
    "Use campaigns.businessx_canada_lead_nurture.tasks.resend_operations instead.",
    DeprecationWarning,
    stacklevel=2
)
