"""
DEPRECATED: This module has been moved to campaigns/businessx_canada_lead_nurture/tasks/routing.py

This shim provides backward compatibility during migration.
Please update your imports to use the new campaign-based structure.
"""
import warnings
from campaigns.businessx_canada_lead_nurture.tasks.routing import *

warnings.warn(
    "tasks.routing is deprecated. "
    "Use campaigns.businessx_canada_lead_nurture.tasks.routing instead.",
    DeprecationWarning,
    stacklevel=2
)
