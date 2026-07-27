"""
in_memory_tenant_repository.py
InMemory implementation of ITenantRepository for testing and sandbox execution.
"""

import threading

from src.application.ports.itenant_repository import ITenantRepository
from src.domain.organizations.entities import Tenant, TenantStatus
from src.domain.organizations.value_objects import TenantConfiguration


class InMemoryTenantRepository(ITenantRepository):
    """
    Thread-safe, in-memory implementation of ITenantRepository.

    Purpose:
        Store and retrieve Tenant aggregates locally in memory without external database engines.
    Business Reasoning:
        Allows high-speed local testing, development sandboxes, and verification loops.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._tenants: dict[str, Tenant] = {}
        
        # Prepopulate sandbox data for local testing and runs
        default_config = TenantConfiguration(max_daily_uploads=100, allowed_mime_types=["application/pdf"])
        
        # Default Active Tenant
        active_tenant = Tenant("tenant-123", "OpenHealth Hospital", TenantStatus.ACTIVE, default_config)
        self._tenants[active_tenant.id] = active_tenant

        # Suspended Tenant
        suspended_tenant = Tenant("tenant-suspended", "St. Jude Outpatient Clinic", TenantStatus.SUSPENDED, default_config)
        self._tenants[suspended_tenant.id] = suspended_tenant

    def save(self, tenant: Tenant) -> None:
        """
        Saves or updates a Tenant.

        Purpose:
            Persist tenant aggregates.
        Business Reasoning:
            Keeps administrative records in sync.
        Inputs:
            tenant (Tenant): Aggregate root.
        Outputs:
            None.
        Assumptions:
            Target dictionary is writable.
        Edge Cases:
            Uses thread-safe locking to prevent write collisions.
        """
        with self._lock:
            self._tenants[tenant.id] = tenant

    def get_by_id(self, id: str) -> Tenant | None:
        """
        Locates a Tenant by identifier.

        Purpose:
            Load subscriber metadata.
        Business Reasoning:
            Verifies credentials on ingress transactions.
        Inputs:
            id (str): Tenant UUID.
        Outputs:
            Tenant | None: Tenant instance or None.
        Assumptions:
            None.
        Edge Cases:
            Keys missing return None.
        """
        with self._lock:
            return self._tenants.get(id)
