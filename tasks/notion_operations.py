"""
DEPRECATED: This module has been moved to campaigns/businessx_canada_lead_nurture/tasks/notion_operations.py

This shim provides backward compatibility during migration.
Please update your imports to use the new campaign-based structure.
"""
import warnings
from campaigns.businessx_canada_lead_nurture.tasks.notion_operations import *

warnings.warn(
    "tasks.notion_operations is deprecated. "
    "Use campaigns.businessx_canada_lead_nurture.tasks.notion_operations instead.",
    DeprecationWarning,
    stacklevel=2
)
