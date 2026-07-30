"""
decrypt_tenant_data.py
Use case executing envelope decryption over wrapped payloads.
"""

import base64
from src.application.ports.isecrets_manager_port import ISecretsManagerPort
from src.application.ports.ikey_provider_port import IKeyProviderPort
from src.application.ports.ikey_ring_repository import IKeyRingRepository
from src.domain.encryption.domain_services import EnvelopeEncryptionEngine
from src.domain.encryption.value_objects import EncryptedPayload


class DecryptTenantDataUseCase:
    """
    Usecase executing envelope decryption over tenant ciphertexts.
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

    def execute(self, tenant_id: str, payload: EncryptedPayload) -> bytes:
        """Unwraps DEKs and decrypts ciphertexts using envelope encryption."""
        key_ring = self.repo.get_key_ring(tenant_id)
        if not key_ring:
            raise ValueError(f"No keyring found for tenant: {tenant_id}")

        kek_id = payload.kek_id
        if kek_id not in key_ring.keks:
            raise ValueError(f"Target KEK {kek_id} not found on keyring history.")

        master_key = self.secrets_manager.get_master_key()

        # 1. Resolve raw KEK used in this payload
        wrapped_kek_b64 = key_ring.keks[kek_id]["key_bytes_b64"]
        wrapped_kek = base64.b64decode(wrapped_kek_b64)
        raw_kek = self.key_provider.unwrap_key(wrapped_kek, master_key)

        # 2. Decrypt data using the engine
        return self.engine.decrypt_data(
            tenant_id=tenant_id,
            payload=payload,
            kek_bytes=raw_kek,
            key_provider=self.key_provider
        )
