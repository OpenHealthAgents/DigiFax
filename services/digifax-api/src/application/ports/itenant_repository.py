"""
itenant_repository.py
Outbound port interface for managing Tenant aggregate persistence.
"""

import abc

from src.domain.organizations.entities import Tenant


class ITenantRepository(abc.ABC):
    """
    Outbound port interface for persisting Tenant Aggregate state.

    Why It Exists:
        To abstract tenant data access logic (SQL, InMemory, Dynamo) from the core domain.
        Ensures use cases can check subscriber statuses without direct dependency on infrastructure drivers.
    """

    @abc.abstractmethod
    def save(self, tenant: Tenant) -> None:
        """
        Saves or updates a Tenant aggregate in the database.

        Purpose:
            Persist the tenant state.
        Business Reasoning:
            Subscribers undergo status updates (e.g. suspension) that must be recorded instantly.
        Inputs:
            tenant (Tenant): The Tenant aggregate root to persist.
        Outputs:
            None.
        Assumptions:
            Target storage is writable.
        Edge Cases:
            Concurrency conflicts on updates must be handled by infrastructure adapters.
        """
        pass

    @abc.abstractmethod
    def get_by_id(self, id: str) -> Tenant | None:
        """
        Retrieves a Tenant aggregate by its unique UUID.

        Purpose:
            Locate a tenant configuration.
        Business Reasoning:
            Required on every API ingestion transaction to confirm account permissions.
        Inputs:
            id (str): Tenant UUID.
        Outputs:
            Tenant | None: The matched aggregate, or None if not found.
        Assumptions:
            None.
        Edge Cases:
            Malformed UUID keys return None.
        """
        pass
