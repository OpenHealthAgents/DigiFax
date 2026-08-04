"""
value_objects.py
Domain value objects for the organizations domain namespace.
"""

from typing import Any
from src.domain.common.value_object import ValueObject


class TenantConfiguration(ValueObject):
    """
    Value object representing configurations, feature flags, and policy limits assigned to a tenant.

    Purpose:
        Define operational boundaries and SaaS toggles for clinical tenants.
    Business Reasoning:
        Tiered product versions require toggling advanced, beta, or administrative features dynamically.
    """

    def __init__(
        self,
        max_daily_uploads: int,
        allowed_mime_types: list[str],
        feature_flags: dict[str, Any] | None = None
    ):
        if max_daily_uploads < 0:
            raise ValueError("max_daily_uploads must be non-negative")
        self.max_daily_uploads = max_daily_uploads
        self.allowed_mime_types = allowed_mime_types
        self.feature_flags = feature_flags or {}

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TenantConfiguration):
            return False
        return (
            self.max_daily_uploads == other.max_daily_uploads
            and self.allowed_mime_types == other.allowed_mime_types
            and self.feature_flags == other.feature_flags
        )
