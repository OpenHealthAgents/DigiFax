"""
in_memory_tenant_repository.py
InMemory implementation of ITenantRepository inheriting from BaseInMemoryRepository.
"""

from src.application.ports.itenant_repository import ITenantRepository
from src.domain.organizations.entities import Tenant, TenantStatus
from src.domain.organizations.value_objects import TenantConfiguration
from src.infrastructure.persistence.base_repository import BaseInMemoryRepository


class InMemoryTenantRepository(BaseInMemoryRepository, ITenantRepository):
    """
    Thread-safe, in-memory implementation of ITenantRepository.

    Purpose:
        Store and retrieve Tenant aggregates locally in memory with concurrency and auditing.
    Business Reasoning:
        Allows high-speed local testing and verification loops.
    """

    def __init__(self) -> None:
        super().__init__()
        
        # Prepopulate sandbox data for local testing and runs
        default_config = TenantConfiguration(max_daily_uploads=100, allowed_mime_types=["application/pdf"])
        
        # Default Active Tenant
        active_tenant = Tenant("tenant-123", "OpenHealth Hospital", TenantStatus.ACTIVE, default_config)
        self.save(active_tenant)

        # Default Suspended Tenant
        suspended_tenant = Tenant("tenant-suspended", "St. Jude Outpatient Clinic", TenantStatus.SUSPENDED, default_config)
        self.save(suspended_tenant)

    def save(self, tenant: Tenant) -> None:
        """
        Saves or updates a Tenant.

        Purpose:
            Persist tenant aggregates.
        Business Reasoning:
            Keeps administrative records in sync.
        Inputs:
            tenant (Tenant): Tenant aggregate.
        Outputs:
            None.
        """
        record_data = {
            "id": tenant.id,
            "tenant_id": tenant.id,  # A tenant belongs to itself as root boundary
            "name": tenant.name,
            "status": tenant.status.value,
            "max_daily_uploads": tenant.configuration.max_daily_uploads,
            "allowed_mime_types": tenant.configuration.allowed_mime_types,
            "version": getattr(tenant, "version", 1)
        }

        self._save_record(tenant.id, record_data)
        
        # Sync version back
        saved_record = self._records[tenant.id]
        tenant.version = saved_record["version"]

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
        """
        # A tenant lookup queries itself, so we use its own ID as the tenant_id constraint
        record = self._get_record_by_id(id, tenant_id=id)
        if not record:
            return None

        config = TenantConfiguration(
            max_daily_uploads=record["max_daily_uploads"],
            allowed_mime_types=record["allowed_mime_types"]
        )
        tenant = Tenant(
            id=record["id"],
            name=record["name"],
            status=TenantStatus(record["status"]),
            configuration=config
        )
        tenant.version = record["version"]
        return tenant
