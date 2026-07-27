"""
value_objects.py
Domain value objects for the organizations domain namespace.
"""

from src.domain.common.value_object import ValueObject


class TenantConfiguration(ValueObject):
    """
    Value object representing configurations and policy limits assigned to a tenant.

    Purpose:
        Define operational boundaries (e.g. max uploads) for clinical tenants.
    Business Reasoning:
        Clinical facilities operate on tiered SaaS plans. Configurations enforce limits programmatically.
    Inputs:
        max_daily_uploads (int): Maximum ingestion sessions per day.
        allowed_mime_types (list[str]): Permitted file format types.
    Outputs:
        An immutable TenantConfiguration instance.
    Assumptions:
        Values passed are pre-validated (e.g. positive upload limits).
    Edge Cases:
        MIME lists can be empty, disabling uploads. Checked at construction.
    """

    def __init__(self, max_daily_uploads: int, allowed_mime_types: list[str]):
        # Validation checks
        if max_daily_uploads < 0:
            raise ValueError("max_daily_uploads must be non-negative")
        self.max_daily_uploads = max_daily_uploads
        self.allowed_mime_types = allowed_mime_types

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TenantConfiguration):
            return False
        return (
            self.max_daily_uploads == other.max_daily_uploads
            and self.allowed_mime_types == other.allowed_mime_types
        )
