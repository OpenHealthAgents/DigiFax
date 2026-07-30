"""
rotate_tenant_keys.py
Use case rotating a tenant's Key Encryption Key (KEK) and re-wrapping Data Encryption Keys (DEK).
"""

import base64
import uuid
from src.application.ports.isecrets_manager_port import ISecretsManagerPort
from src.application.ports.ikey_provider_port import IKeyProviderPort
from src.application.ports.ikey_ring_repository import IKeyRingRepository
from src.domain.encryption.entities import TenantKeyRing


class RotateTenantKeysUseCase:
    """
    Usecase rotating active KEKs, re-wrapping historical DEKs with the new KEK for continuity.
    """

    def __init__(
        self,
        repo: IKeyRingRepository,
        secrets_manager: ISecretsManagerPort,
        key_provider: IKeyProviderPort
    ) -> None:
        self.repo = repo
        self.secrets_manager = secrets_manager
        self.key_provider = key_provider

    def execute(self, tenant_id: str) -> TenantKeyRing:
        """Rotates active KEK and re-wraps all existing DEKs with the new KEK."""
        key_ring = self.repo.get_key_ring(tenant_id)
        if not key_ring or not key_ring.active_kek_id:
            raise ValueError(f"No active keyring configuration found for tenant: {tenant_id}")

        master_key = self.secrets_manager.get_master_key()
        old_kek_id = key_ring.active_kek_id

        # 1. Unmarshal active old KEK
        old_wrapped_kek_b64 = key_ring.keks[old_kek_id]["key_bytes_b64"]
        old_wrapped_kek = base64.b64decode(old_wrapped_kek_b64)
        old_raw_kek = self.key_provider.unwrap_key(old_wrapped_kek, master_key)

        # 2. Generate new active KEK
        new_kek_id = f"kek-{tenant_id}-{uuid.uuid4().hex[:8]}"
        new_raw_kek = self.key_provider.generate_random_key()
        new_wrapped_kek = self.key_provider.wrap_key(new_raw_kek, master_key)
        new_wrapped_kek_b64 = base64.b64encode(new_wrapped_kek).decode("utf-8")

        # Rotate KEK on keyring (adds to history)
        key_ring.rotate_kek(new_kek_id, new_wrapped_kek_b64)

        # 3. Re-wrap all existing DEKs using the new KEK
        for dek_id, dek_data in list(key_ring.deks.items()):
            wrapped_dek_b64 = dek_data["key_bytes_b64"]
            wrapped_dek = base64.b64decode(wrapped_dek_b64)
            
            # Decrypt/unwrap DEK with old KEK
            raw_dek = self.key_provider.unwrap_key(wrapped_dek, old_raw_kek)

            # Re-wrap DEK with the new KEK
            re_wrapped_dek = self.key_provider.wrap_key(raw_dek, new_raw_kek)
            re_wrapped_dek_b64 = base64.b64encode(re_wrapped_dek).decode("utf-8")

            # Update DEK reference
            key_ring.deks[dek_id]["key_bytes_b64"] = re_wrapped_dek_b64
            key_ring.deks[dek_id]["kek_id"] = new_kek_id

        # 4. Generate a new active DEK wrapped by the new KEK
        new_dek_id = f"dek-{tenant_id}-{uuid.uuid4().hex[:8]}"
        new_raw_dek = self.key_provider.generate_random_key()
        new_wrapped_dek = self.key_provider.wrap_key(new_raw_dek, new_raw_kek)
        new_wrapped_dek_b64 = base64.b64encode(new_wrapped_dek).decode("utf-8")

        key_ring.add_dek(new_dek_id, new_wrapped_dek_b64, new_kek_id)

        self.repo.save_key_ring(key_ring)
        return key_ring
