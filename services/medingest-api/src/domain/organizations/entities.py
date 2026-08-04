"""
entities.py
Tenant aggregate root representing a medical facility customer in the system.
"""

import enum

from src.domain.common.entity import AggregateRoot
from src.domain.organizations.value_objects import TenantConfiguration


class TenantStatus(enum.StrEnum):
    """
    Enum defining the active state of a clinical Tenant.

    Purpose:
        Track administrative lifecycles of clinical facility accounts.
    Business Reasoning:
        Suspended facilities must immediately block further ingestion workflows to prevent overages or unauthorized access.
    """
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"


class Tenant(AggregateRoot):
    """
    Aggregate Root representing a single tenant organization (clinic system or hospital).

    Purpose:
        Define identity, status, configurations, and policy bounds for a SaaS subscriber.
    Business Reasoning:
        Every clinical transaction in MedIngest must resolve back to a verified, active subscriber entity.
    Inputs:
        id (str): Tenant identifier UUID.
        name (str): Clinical facility name.
        status (TenantStatus): Account status.
        configuration (TenantConfiguration): Assigned limits and configurations.
    Outputs:
        A Tenant aggregate root instance.
    Assumptions:
        Tenant identities are unique.
    Edge Cases:
        A suspended tenant must reject ingest queries.
    """

    def __init__(
        self,
        id: str,
        name: str,
        status: TenantStatus,
        configuration: TenantConfiguration
    ):
        super().__init__(id)
        if not name.strip():
            raise ValueError("Tenant name cannot be empty")
        self.name = name
        self.status = status
        self.configuration = configuration

    @classmethod
    def create(
        cls,
        id: str,
        name: str,
        configuration: TenantConfiguration
    ) -> 'Tenant':
        """
        Factory method to instantiate a new Tenant aggregate root.

        Purpose:
            Create a fresh tenant profile. Default status is ACTIVE.
        Business Reasoning:
            Initializes facilities immediately for ingestion workflows.
        Inputs:
            id (str): Tenant UUID.
            name (str): Facility name.
            configuration (TenantConfiguration): Limits.
        Outputs:
            A new Tenant aggregate root instance.
        Assumptions:
            Passed UUID does not collide with existing database listings.
        Edge Cases:
            Empty facility names throw a ValueError.
        """
        return cls(id, name, TenantStatus.ACTIVE, configuration)

    def suspend(self) -> None:
        """
        Suspends the tenant from operational activities.

        Purpose:
            Mark the tenant status as SUSPENDED.
        Business Reasoning:
            Billing issues or data lock requests require administrative suspensions.
        Inputs:
            None.
        Outputs:
            None (mutates self.status).
        Assumptions:
            Target tenant is currently ACTIVE.
        Edge Cases:
            Calling suspend on an already SUSPENDED tenant is a no-op.
        """
        self.status = TenantStatus.SUSPENDED

    def activate(self) -> None:
        """
        Activates the suspended tenant.

        Purpose:
            Mark the tenant status as ACTIVE.
        Business Reasoning:
            Resume services after payment resolution.
        Inputs:
            None.
        Outputs:
            None (mutates self.status).
        Assumptions:
            Target tenant is currently SUSPENDED.
        Edge Cases:
            Calling activate on an already ACTIVE tenant is a no-op.
        """
        self.status = TenantStatus.ACTIVE

    def is_active(self) -> bool:
        """
        Helper checking if the tenant is active.

        Purpose:
            Boolean helper evaluating active state.
        Business Reasoning:
            Fast evaluation check inside use case execution handler blocks.
        Inputs:
            None.
        Outputs:
            bool: True if ACTIVE, else False.
        Assumptions:
            None.
        Edge Cases:
            None.
        """
        return self.status == TenantStatus.ACTIVE
