"""
events.py
Domain events emitted by aggregates inside the Tenant Management context.
"""

from datetime import datetime
from src.domain.common.domain_event import DomainEvent


class TenantCreatedEvent(DomainEvent):
    """
    Domain event published when a new Tenant is registered.
    """

    def __init__(
        self,
        aggregate_id: str,
        name: str,
        organization_id: str | None = None,
        correlation_id: str = "",
        trace_id: str = "",
        user_id: str = "system",
        version: int = 1,
        occurred_at: datetime | None = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            tenant_id=aggregate_id,
            organization_id=organization_id,
            correlation_id=correlation_id,
            trace_id=trace_id,
            user_id=user_id,
            version=version,
            occurred_at=occurred_at
        )
        self.name = name


class MembershipAssignedEvent(DomainEvent):
    """
    Domain event published when a practitioner joins a facility.
    """

    def __init__(
        self,
        aggregate_id: str,
        tenant_id: str,
        user_id: str,
        organization_id: str,
        role_name: str,
        correlation_id: str = "",
        trace_id: str = "",
        version: int = 1,
        occurred_at: datetime | None = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            tenant_id=tenant_id,
            organization_id=organization_id,
            correlation_id=correlation_id,
            trace_id=trace_id,
            user_id=user_id,
            version=version,
            occurred_at=occurred_at
        )
        self.user_id = user_id
        self.organization_id = organization_id
        self.role_name = role_name


class InvitationSentEvent(DomainEvent):
    """
    Domain event published when an invitation email triggers.
    """

    def __init__(
        self,
        aggregate_id: str,
        tenant_id: str,
        recipient_email: str,
        token: str,
        organization_id: str | None = None,
        correlation_id: str = "",
        trace_id: str = "",
        user_id: str = "system",
        version: int = 1,
        occurred_at: datetime | None = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            tenant_id=tenant_id,
            organization_id=organization_id,
            correlation_id=correlation_id,
            trace_id=trace_id,
            user_id=user_id,
            version=version,
            occurred_at=occurred_at
        )
        self.recipient_email = recipient_email
        self.token = token


class WorkspaceCreatedEvent(DomainEvent):
    """
    Domain event published when an operational workspace is established.
    """

    def __init__(
        self,
        aggregate_id: str,
        tenant_id: str,
        organization_id: str,
        name: str,
        correlation_id: str = "",
        trace_id: str = "",
        user_id: str = "system",
        version: int = 1,
        occurred_at: datetime | None = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            tenant_id=tenant_id,
            organization_id=organization_id,
            correlation_id=correlation_id,
            trace_id=trace_id,
            user_id=user_id,
            version=version,
            occurred_at=occurred_at
        )
        self.organization_id = organization_id
        self.name = name
