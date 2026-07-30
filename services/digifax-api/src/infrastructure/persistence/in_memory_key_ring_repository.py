"""
in_memory_key_ring_repository.py
In-memory persistence adapter for TenantKeyRing aggregate.
"""

from src.application.ports.ikey_ring_repository import IKeyRingRepository
from src.domain.encryption.entities import TenantKeyRing
from src.infrastructure.persistence.base_repository import BaseInMemoryRepository


class InMemoryKeyRingRepository(BaseInMemoryRepository, IKeyRingRepository):
    """
    Thread-safe in-memory adapter storing TenantKeyRing records.
    """

    def __init__(self) -> None:
        super().__init__()

    def save_key_ring(self, key_ring: TenantKeyRing) -> None:
        """Saves a tenant's KeyRing configuration."""
        record_data = {
            "id": key_ring.tenant_id,
            "tenant_id": key_ring.tenant_id,
            "active_kek_id": key_ring.active_kek_id,
            "active_dek_id": key_ring.active_dek_id,
            "keks": dict(key_ring.keks),
            "deks": dict(key_ring.deks),
            "history": list(key_ring.history),
            "version": key_ring.version
        }
        with self._lock:
            # Overwrite directly to allow thread-safe config updates
            self._records[key_ring.tenant_id] = record_data

    def get_key_ring(self, tenant_id: str) -> TenantKeyRing | None:
        """Loads a tenant's KeyRing configuration."""
        record = self._get_record_by_id(tenant_id, tenant_id)
        if not record:
            return None

        return TenantKeyRing(
            tenant_id=record["tenant_id"],
            active_kek_id=record["active_kek_id"],
            active_dek_id=record["active_dek_id"],
            keks=record["keks"],
            deks=record["deks"],
            history=record["history"],
            version=record["version"]
        )
