"""
repositories.py
Repository interfaces for the Tenant Management context.
"""

import abc
from src.domain.tenant_management.entities import Tenant, Workspace


class ITenantManagementRepository(abc.ABC):
    """
    Outbound port interface for managing Tenant aggregate persistence.

    Why It Exists:
        Decouple persistence infrastructure (PostgreSQL, DynamoDB) from core Tenant domain entities.
    """

    @abc.abstractmethod
    def save(self, tenant: Tenant) -> None:
        """Saves or updates a Tenant."""
        pass

    @abc.abstractmethod
    def get_by_id(self, id: str) -> Tenant | None:
        """Retrieves a Tenant by identifier."""
        pass


class IWorkspaceRepository(abc.ABC):
    """
    Outbound port interface for managing Workspace entity persistence.

    Why It Exists:
        Abstract workspace data access logic.
    """

    @abc.abstractmethod
    def save(self, workspace: Workspace) -> None:
        """Saves or updates a Workspace."""
        pass

    @abc.abstractmethod
    def get_by_id(self, id: str) -> Workspace | None:
        """Retrieves a Workspace by identifier."""
        pass
