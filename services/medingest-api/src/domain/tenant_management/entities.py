"""
entities.py
Domain aggregate roots and entities for the Tenant Management bounded context.
"""

import enum
from datetime import datetime

from src.domain.common.entity import AggregateRoot, Entity
from src.domain.tenant_management.value_objects import (
    Role,
    BillingPlan,
    AuditPolicy,
    RetentionPolicy,
    SubscriptionUsage
)


class TenantStatus(enum.StrEnum):
    """Lifecycle statuses for a Tenant."""
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    ARCHIVED = "ARCHIVED"


class InvitationStatus(enum.StrEnum):
    """Lifecycle statuses for an invitation link."""
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    EXPIRED = "EXPIRED"


class Subscription(Entity):
    """
    Entity representing a Tenant's billing subscription context and consumption quotas.

    Purpose:
        Link a Tenant to active billing plans and check limits.
    Business Reasoning:
        Controls operational usage bounds programmatically based on payments.
    """

    def __init__(
        self,
        id: str,
        plan: BillingPlan,
        start_date: datetime,
        current_usage: SubscriptionUsage | None = None
    ):
        super().__init__(id)
        self.plan = plan
        self.start_date = start_date
        self.current_usage = current_usage or SubscriptionUsage(
            storage_used_mb=0.0,
            ocr_pages_used=0,
            api_calls_used=0,
            documents_used=0
        )

    def has_exceeded_limits(self) -> dict[str, bool]:
        """
        Evaluates consumption quotas and returns true flags for any breaches.
        """
        quotas = self.plan.quotas
        usage = self.current_usage

        return {
            "storage": usage.storage_used_mb >= quotas.max_storage_mb,
            "ocr": usage.ocr_pages_used >= quotas.max_ocr_pages,
            "api": usage.api_calls_used >= quotas.max_api_calls_monthly,
            "documents": usage.documents_used >= quotas.max_documents_monthly
        }


class ApiKey(Entity):
    """Entity representing an automated integration API key."""

    def __init__(self, id: str, hashed_key: str, label: str, expires_at: datetime | None = None):
        super().__init__(id)
        if not label.strip():
            raise ValueError("ApiKey label cannot be empty")
        self.hashed_key = hashed_key
        self.label = label
        self.expires_at = expires_at

    def is_expired(self, current_time: datetime) -> bool:
        """Checks if the key is expired."""
        if not self.expires_at:
            return False
        return current_time > self.expires_at


class Tenant(AggregateRoot):
    """
    Aggregate Root representing the Tenant subscription boundary.

    Purpose:
        Top-level boundary enclosing billing status, API integrations, and policies.
    """

    def __init__(
        self,
        id: str,
        name: str,
        status: TenantStatus,
        subscription: Subscription,
        audit_policy: AuditPolicy,
        retention_policy: RetentionPolicy
    ):
        super().__init__(id)
        if not name.strip():
            raise ValueError("Tenant name cannot be empty")
        self.name = name
        self.status = status
        self.subscription = subscription
        self.audit_policy = audit_policy
        self.retention_policy = retention_policy
        self.api_keys: list[ApiKey] = []

    def suspend(self) -> None:
        """Suspends the Tenant."""
        self.status = TenantStatus.SUSPENDED

    def activate(self) -> None:
        """Activates the Tenant."""
        self.status = TenantStatus.ACTIVE

    def archive(self) -> None:
        """Archives the Tenant."""
        self.status = TenantStatus.ARCHIVED

    def add_api_key(self, api_key: ApiKey) -> None:
        """Registers a new programmatic API key."""
        self.api_keys.append(api_key)


class Organization(AggregateRoot):
    """Aggregate Root representing a single healthcare facility (clinic or campus)."""

    def __init__(self, id: str, tenant_id: str, name: str, npi: str):
        super().__init__(id)
        if not name.strip():
            raise ValueError("Organization name cannot be empty")
        if not npi.strip():
            raise ValueError("Organization NPI cannot be empty")
        self.tenant_id = tenant_id
        self.name = name
        self.npi = npi


class Workspace(Entity):
    """Entity representing a department upload queue (e.g. Pediatrics)."""

    def __init__(self, id: str, organization_id: str, name: str):
        super().__init__(id)
        if not name.strip():
            raise ValueError("Workspace name cannot be empty")
        self.organization_id = organization_id
        self.name = name


class Membership(Entity):
    """Entity mapping a user profile to a specific Organization role."""

    def __init__(self, id: str, user_id: str, organization_id: str, role: Role):
        super().__init__(id)
        self.user_id = user_id
        self.organization_id = organization_id
        self.role = role


class Invitation(Entity):
    """Entity governing user onboarding cycles."""

    def __init__(
        self,
        id: str,
        organization_id: str,
        recipient_email: str,
        role: Role,
        token: str,
        expires_at: datetime,
        status: InvitationStatus = InvitationStatus.PENDING
    ):
        super().__init__(id)
        if not recipient_email.strip():
            raise ValueError("recipient_email cannot be empty")
        self.organization_id = organization_id
        self.recipient_email = recipient_email
        self.role = role
        self.token = token
        self.expires_at = expires_at
        self.status = status

    def accept(self, current_time: datetime) -> None:
        """Accepts the invitation if not expired."""
        if self.status != InvitationStatus.PENDING:
            raise ValueError("Invitation is not in a pending state")
        if current_time > self.expires_at:
            self.status = InvitationStatus.EXPIRED
            raise ValueError("Invitation token has expired")
        self.status = InvitationStatus.ACCEPTED
