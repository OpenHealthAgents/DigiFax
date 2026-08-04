"""
initialize_key_ring.py
Use case initializing a tenant's KeyRing aggregate.
"""

import base64
import uuid
from src.application.ports.isecrets_manager_port import ISecretsManagerPort
from src.application.ports.ikey_provider_port import IKeyProviderPort
from src.application.ports.ikey_ring_repository import IKeyRingRepository
from src.domain.encryption.entities import TenantKeyRing


class InitializeKeyRingUseCase:
    """
    Usecase generating initial KEK and DEK keys for a tenant cryptographic isolated partition.
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
        """Sets up a KEK (wrapped by Master Key) and DEK (wrapped by KEK) for a tenant."""
        key_ring = self.repo.get_key_ring(tenant_id)
        if not key_ring:
            key_ring = TenantKeyRing(tenant_id=tenant_id)

        master_key = self.secrets_manager.get_master_key()

        # 1. Generate new KEK (Tenant Key Encryption Key)
        kek_id = f"kek-{tenant_id}-{uuid.uuid4().hex[:8]}"
        raw_kek = self.key_provider.generate_random_key()
        wrapped_kek = self.key_provider.wrap_key(raw_kek, master_key)
        
        # 2. Add KEK to keyring
        wrapped_kek_b64 = base64.b64encode(wrapped_kek).decode("utf-8")
        key_ring.add_kek(kek_id, wrapped_kek_b64)

        # 3. Generate new DEK (Tenant Data Encryption Key)
        dek_id = f"dek-{tenant_id}-{uuid.uuid4().hex[:8]}"
        raw_dek = self.key_provider.generate_random_key()
        wrapped_dek = self.key_provider.wrap_key(raw_dek, raw_kek)

        # 4. Add DEK to keyring
        wrapped_dek_b64 = base64.b64encode(wrapped_dek).decode("utf-8")
        key_ring.add_dek(dek_id, wrapped_dek_b64, kek_id)

        self.repo.save_key_ring(key_ring)
        return key_ring
