"""
value_objects.py
Domain value objects representing permissions, roles, billing plans, and quotas.
"""

import enum
from src.domain.common.value_object import ValueObject


class SubscriptionTier(enum.StrEnum):
    """SaaS licensing subscription tiers."""
    FREE = "FREE"
    PROFESSIONAL = "PROFESSIONAL"
    ENTERPRISE = "ENTERPRISE"


class Permission(ValueObject):
    """Value object representing a granular security capability."""

    def __init__(self, name: str):
        if not name.strip():
            raise ValueError("Permission name cannot be empty")
        self.name = name

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Permission):
            return False
        return self.name == other.name


class Role(ValueObject):
    """Value object grouping multiple security permissions."""

    def __init__(self, name: str, permissions: list[Permission]):
        if not name.strip():
            raise ValueError("Role name cannot be empty")
        self.name = name
        self.permissions = permissions

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Role):
            return False
        return self.name == other.name and self.permissions == other.permissions


class SubscriptionQuotas(ValueObject):
    """
    Value object specifying maximum consumption limits.

    Purpose:
        Define storage and process caps.
    """

    def __init__(
        self,
        max_storage_mb: int,
        max_ocr_pages: int,
        max_api_calls_monthly: int,
        max_documents_monthly: int
    ):
        if max_storage_mb < 0 or max_ocr_pages < 0 or max_api_calls_monthly < 0 or max_documents_monthly < 0:
            raise ValueError("Quotas must be non-negative values")
        self.max_storage_mb = max_storage_mb
        self.max_ocr_pages = max_ocr_pages
        self.max_api_calls_monthly = max_api_calls_monthly
        self.max_documents_monthly = max_documents_monthly

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SubscriptionQuotas):
            return False
        return (
            self.max_storage_mb == other.max_storage_mb
            and self.max_ocr_pages == other.max_ocr_pages
            and self.max_api_calls_monthly == other.max_api_calls_monthly
            and self.max_documents_monthly == other.max_documents_monthly
        )


class SubscriptionUsage(ValueObject):
    """
    Value object tracking dynamic consumption meters.

    Purpose:
        Evaluate usage status against quotas.
    """

    def __init__(
        self,
        storage_used_mb: float,
        ocr_pages_used: int,
        api_calls_used: int,
        documents_used: int
    ):
        if storage_used_mb < 0 or ocr_pages_used < 0 or api_calls_used < 0 or documents_used < 0:
            raise ValueError("Usage parameters must be non-negative")
        self.storage_used_mb = storage_used_mb
        self.ocr_pages_used = ocr_pages_used
        self.api_calls_used = api_calls_used
        self.documents_used = documents_used

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SubscriptionUsage):
            return False
        return (
            self.storage_used_mb == other.storage_used_mb
            and self.ocr_pages_used == other.ocr_pages_used
            and self.api_calls_used == other.api_calls_used
            and self.documents_used == other.documents_used
        )


class BillingPlan(ValueObject):
    """
    Value object defining subscription tiers and quota limits.

    Purpose:
        Enforce pricing structure plans.
    """

    def __init__(self, tier: SubscriptionTier, monthly_price_usd: float, quotas: SubscriptionQuotas):
        if monthly_price_usd < 0:
            raise ValueError("monthly_price_usd must be non-negative")
        self.tier = tier
        self.monthly_price_usd = monthly_price_usd
        self.quotas = quotas

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BillingPlan):
            return False
        return (
            self.tier == other.tier
            and self.monthly_price_usd == other.monthly_price_usd
            and self.quotas == other.quotas
        )


class AuditPolicy(ValueObject):
    """Value object specifying audit logging rules."""

    def __init__(self, log_retention_days: int, tracked_events: list[str]):
        if log_retention_days < 0:
            raise ValueError("log_retention_days must be non-negative")
        self.log_retention_days = log_retention_days
        self.tracked_events = tracked_events

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AuditPolicy):
            return False
        return (
            self.log_retention_days == other.log_retention_days
            and self.tracked_events == other.tracked_events
        )


class RetentionPolicy(ValueObject):
    """Value object defining storage durations for parsed files."""

    def __init__(self, raw_retention_days: int, processed_retention_days: int):
        if raw_retention_days < 0 or processed_retention_days < 0:
            raise ValueError("Retention days must be non-negative")
        self.raw_retention_days = raw_retention_days
        self.processed_retention_days = processed_retention_days

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RetentionPolicy):
            return False
        return (
            self.raw_retention_days == other.raw_retention_days
            and self.processed_retention_days == other.processed_retention_days
        )
