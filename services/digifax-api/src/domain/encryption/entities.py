"""
entities.py
Domain Entities and Aggregate Roots for Tenant-scoped KeyRings.
"""

from datetime import datetime
from src.domain.common.entity import Entity
from src.domain.encryption.value_objects import CryptographicKey


class TenantKeyRing(Entity):
    """
    Aggregate Root scoping a tenant's cryptographic keys list, tracking wrapping histories.
    """

    def __init__(
        self,
        tenant_id: str,
        active_kek_id: str | None = None,
        active_dek_id: str | None = None,
        keks: dict[str, dict] = None,  # key_id -> { "key_bytes_b64": str, "algorithm": str }
        deks: dict[str, dict] = None,  # key_id -> { "key_bytes_b64": str, "kek_id": str, "algorithm": str }
        history: list[dict] = None,
        version: int = 1
    ):
        super().__init__(id=tenant_id)
        self.tenant_id = tenant_id
        self.active_kek_id = active_kek_id
        self.active_dek_id = active_dek_id
        self.keks = keks or {}
        self.deks = deks or {}
        self.history = history or []
        self.version = version

    def add_kek(self, key_id: str, encrypted_kek_b64: str, algorithm: str = "AES-GCM-256") -> None:
        """Registers a new Key Encryption Key (KEK) wrapped by the system Master Key."""
        self.keks[key_id] = {
            "key_bytes_b64": encrypted_kek_b64,
            "algorithm": algorithm,
            "created_at": datetime.now().isoformat()
        }
        self.active_kek_id = key_id
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "action": "ADD_KEK",
            "key_id": key_id,
            "details": f"Registered active KEK: {key_id}"
        })

    def add_dek(self, key_id: str, encrypted_dek_b64: str, kek_id: str, algorithm: str = "AES-GCM-256") -> None:
        """Registers a new Data Encryption Key (DEK) wrapped by the tenant's KEK."""
        self.deks[key_id] = {
            "key_bytes_b64": encrypted_dek_b64,
            "kek_id": kek_id,
            "algorithm": algorithm,
            "created_at": datetime.now().isoformat()
        }
        self.active_dek_id = key_id
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "action": "ADD_DEK",
            "key_id": key_id,
            "details": f"Registered active DEK wrapped by KEK: {kek_id}"
        })

    def rotate_kek(self, new_kek_id: str, new_encrypted_kek_b64: str) -> None:
        """Applies a new Key Encryption Key (KEK). Old DEKs will need re-wrapping."""
        self.keks[new_kek_id] = {
            "key_bytes_b64": new_encrypted_kek_b64,
            "algorithm": "AES-GCM-256",
            "created_at": datetime.now().isoformat()
        }
        self.active_kek_id = new_kek_id
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "action": "ROTATE_KEK",
            "key_id": new_kek_id,
            "details": f"Rotated tenant KEK to: {new_kek_id}"
        })
