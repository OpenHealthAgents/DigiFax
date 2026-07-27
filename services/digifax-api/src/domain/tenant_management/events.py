"""
events.py
Domain events emitted by aggregates inside the Tenant Management context.
"""

from datetime import datetime
from src.domain.common.domain_event import DomainEvent


class TenantCreatedEvent(DomainEvent):
    """
    Domain event published when a new Tenant is registered.

    Purpose:
        Trigger downstream automation scripts (e.g. workspace creation, billing setups).
    Business Reasoning:
        Notifies billing systems to activate subscriptions.
    """

    def __init__(self, aggregate_id: str, name: str, occurred_at: datetime | None = None):
        super().__init__(aggregate_id, occurred_at)
        self.name = name


class MembershipAssignedEvent(DomainEvent):
    """
    Domain event published when a practitioner joins a facility.

    Purpose:
        Signal role provisioning inside facility rosters.
    Business Reasoning:
        Maintains compliance trace logs.
    """

    def __init__(
        self,
        aggregate_id: str,
        user_id: str,
        organization_id: str,
        role_name: str,
        occurred_at: datetime | None = None
    ):
        super().__init__(aggregate_id, occurred_at)
        self.user_id = user_id
        self.organization_id = organization_id
        self.role_name = role_name


class InvitationSentEvent(DomainEvent):
    """
    Domain event published when an invitation email triggers.

    Purpose:
        Notify mail dispatchers to send verification link tokens.
    Business Reasoning:
        Decouples email delivery services from core application workflows.
    """

    def __init__(
        self,
        aggregate_id: str,
        recipient_email: str,
        token: str,
        occurred_at: datetime | None = None
    ):
        super().__init__(aggregate_id, occurred_at)
        self.recipient_email = recipient_email
        self.token = token


class WorkspaceCreatedEvent(DomainEvent):
    """
    Domain event published when an operational workspace is established.

    Purpose:
        Trigger downstream setups.
    Business Reasoning:
        Notifies S3 folder creators to provision tenant folder structures.
    """

    def __init__(
        self,
        aggregate_id: str,
        organization_id: str,
        name: str,
        occurred_at: datetime | None = None
    ):
        super().__init__(aggregate_id, occurred_at)
        self.organization_id = organization_id
        self.name = name
