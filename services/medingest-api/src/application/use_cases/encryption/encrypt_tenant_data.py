"""
encrypt_tenant_data.py
Use case executing envelope encryption over raw data payloads.
"""

import base64
from src.application.ports.isecrets_manager_port import ISecretsManagerPort
from src.application.ports.ikey_provider_port import IKeyProviderPort
from src.application.ports.ikey_ring_repository import IKeyRingRepository
from src.domain.encryption.domain_services import EnvelopeEncryptionEngine
from src.domain.encryption.value_objects import EncryptedPayload


class EncryptTenantDataUseCase:
    """
    Usecase executing envelope encryption over tenant clinical records at rest.
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
        self.engine = EnvelopeEncryptionEngine()

    def execute(self, tenant_id: str, data: bytes) -> EncryptedPayload:
        """Packs payload elements using AES-256-GCM envelope encryption."""
        key_ring = self.repo.get_key_ring(tenant_id)
        if not key_ring or not key_ring.active_kek_id or not key_ring.active_dek_id:
            # Lazy initialize keyring if missing
            from src.application.use_cases.encryption.initialize_key_ring import InitializeKeyRingUseCase
            init_use_case = InitializeKeyRingUseCase(self.repo, self.secrets_manager, self.key_provider)
            key_ring = init_use_case.execute(tenant_id)

        master_key = self.secrets_manager.get_master_key()
        active_kek_id = key_ring.active_kek_id
        active_dek_id = key_ring.active_dek_id

        # 1. Resolve raw active KEK
        wrapped_kek_b64 = key_ring.keks[active_kek_id]["key_bytes_b64"]
        wrapped_kek = base64.b64decode(wrapped_kek_b64)
        raw_kek = self.key_provider.unwrap_key(wrapped_kek, master_key)

        # 2. Resolve raw active DEK
        wrapped_dek_b64 = key_ring.deks[active_dek_id]["key_bytes_b64"]
        wrapped_dek = base64.b64decode(wrapped_dek_b64)
        raw_dek = self.key_provider.unwrap_key(wrapped_dek, raw_kek)

        # 3. Encrypt data using Envelope Encryption Engine
        return self.engine.encrypt_data(
            tenant_id=tenant_id,
            data=data,
            active_kek_id=active_kek_id,
            active_dek_id=active_dek_id,
            dek_bytes=raw_dek,
            kek_bytes=raw_kek,
            key_provider=self.key_provider
        )
