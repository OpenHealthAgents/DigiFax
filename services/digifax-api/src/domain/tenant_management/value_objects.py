"""
value_objects.py
Domain value objects representing permissions, roles, billing configurations, and compliance policies.
"""

from src.domain.common.value_object import ValueObject


class Permission(ValueObject):
    """
    Value object representing a granular security capability.

    Purpose:
        Track access controls at a system capability level.
    Business Reasoning:
        Clinical platforms require tight access controls to comply with HIPAA policies.
    Inputs:
        name (str): Unique key representing capability (e.g. "document:read").
    Outputs:
        Permission instance.
    Assumptions:
        None.
    Edge Cases:
        Empty strings throw ValueError.
    """

    def __init__(self, name: str):
        if not name.strip():
            raise ValueError("Permission name cannot be empty")
        self.name = name

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Permission):
            return False
        return self.name == other.name


class Role(ValueObject):
    """
    Value object grouping multiple security permissions.

    Purpose:
        Define user role boundaries.
    Business Reasoning:
        Simplifies system user administration using RBAC patterns.
    Inputs:
        name (str): Role identifier (e.g. "CLINICAL_REVIEWER").
        permissions (list[Permission]): Associated access capabilities.
    Outputs:
        Role instance.
    Assumptions:
        None.
    Edge Cases:
        Empty role name throws ValueError.
    """

    def __init__(self, name: str, permissions: list[Permission]):
        if not name.strip():
            raise ValueError("Role name cannot be empty")
        self.name = name
        self.permissions = permissions

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Role):
            return False
        return self.name == other.name and self.permissions == other.permissions


class BillingPlan(ValueObject):
    """
    Value object defining subscription tiers.

    Purpose:
        Specify invoice costs and operational limits per billing tier.
    Business Reasoning:
        SaaS platforms require tiered pricing options to service small clinics up to enterprise hospital systems.
    Inputs:
        name (str): Plan name (e.g. "SaaS Gold").
        monthly_price_usd (float): Pricing cost.
        max_daily_uploads (int): Daily upload limit.
    Outputs:
        BillingPlan instance.
    Assumptions:
        Price and upload limits are non-negative.
    Edge Cases:
        Negative values throw ValueError.
    """

    def __init__(self, name: str, monthly_price_usd: float, max_daily_uploads: int):
        if not name.strip():
            raise ValueError("Billing plan name cannot be empty")
        if monthly_price_usd < 0:
            raise ValueError("monthly_price_usd must be non-negative")
        if max_daily_uploads < 0:
            raise ValueError("max_daily_uploads must be non-negative")
        self.name = name
        self.monthly_price_usd = monthly_price_usd
        self.max_daily_uploads = max_daily_uploads

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BillingPlan):
            return False
        return (
            self.name == other.name
            and self.monthly_price_usd == other.monthly_price_usd
            and self.max_daily_uploads == other.max_daily_uploads
        )


class AuditPolicy(ValueObject):
    """
    Value object specifying audit logging rules.

    Purpose:
        Define compliance audit tracing directives.
    Business Reasoning:
        Meets clinical software compliance auditing requirements.
    Inputs:
        log_retention_days (int): Archive retention duration.
        tracked_events (list[str]): Event keys captured.
    Outputs:
        AuditPolicy instance.
    """

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
    """
    Value object defining storage durations for parsed files.

    Purpose:
        Govern physical file deletion lifecycle timelines.
    Business Reasoning:
        Protects patient privacy by pruning historical raw fax images.
    Inputs:
        raw_retention_days (int): Retention for source PDFs.
        processed_retention_days (int): Retention for extracted JSON records.
    Outputs:
        RetentionPolicy instance.
    """

    def __init__(self, raw_retention_days: int, processed_retention_days: int):
        if raw_retention_days < 0:
            raise ValueError("raw_retention_days must be non-negative")
        if processed_retention_days < 0:
            raise ValueError("processed_retention_days must be non-negative")
        self.raw_retention_days = raw_retention_days
        self.processed_retention_days = processed_retention_days

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RetentionPolicy):
            return False
        return (
            self.raw_retention_days == other.raw_retention_days
            and self.processed_retention_days == other.processed_retention_days
        )
