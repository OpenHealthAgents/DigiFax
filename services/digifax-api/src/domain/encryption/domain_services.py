"""
domain_services.py
Domain service orchestrating AES-GCM envelope encryption.
"""

import base64
from typing import Any
from src.domain.encryption.value_objects import EncryptedPayload


class EnvelopeEncryptionEngine:
    """
    Domain service executing AES-GCM envelope encryption and decryption wrapping processes.
    """

    def encrypt_data(
        self,
        tenant_id: str,
        data: bytes,
        active_kek_id: str,
        active_dek_id: str,
        dek_bytes: bytes,  # Raw decrypted DEK bytes
        kek_bytes: bytes,  # Raw decrypted KEK bytes
        key_provider: Any  # IKeyProviderPort
    ) -> EncryptedPayload:
        """
        Envelope encrypts plaintext data:
            1. Encrypts data using DEK with AES-GCM.
            2. Wraps/Encrypts DEK using KEK.
        """
        # Encrypt the raw data using DEK
        ciphertext, iv = key_provider.encrypt_data_with_key(data, dek_bytes)
        
        # Encrypt/wrap the DEK using KEK
        encrypted_dek = key_provider.wrap_key(dek_bytes, kek_bytes)

        return EncryptedPayload(
            ciphertext=base64.b64encode(ciphertext).decode("utf-8"),
            iv=base64.b64encode(iv).decode("utf-8"),
            encrypted_dek=base64.b64encode(encrypted_dek).decode("utf-8"),
            dek_id=active_dek_id,
            kek_id=active_kek_id
        )

    def decrypt_data(
        self,
        tenant_id: str,
        payload: EncryptedPayload,
        kek_bytes: bytes,  # Raw decrypted KEK bytes
        key_provider: Any  # IKeyProviderPort
    ) -> bytes:
        """
        Envelope decrypts payload:
            1. Unwraps/Decrypts DEK using KEK.
            2. Decrypts ciphertext using DEK.
        """
        encrypted_dek_bytes = base64.b64decode(payload.encrypted_dek)
        ciphertext_bytes = base64.b64decode(payload.ciphertext)
        iv_bytes = base64.b64decode(payload.iv)

        # Unwrap DEK
        dek_bytes = key_provider.unwrap_key(encrypted_dek_bytes, kek_bytes)

        # Decrypt data
        return key_provider.decrypt_data_with_key(ciphertext_bytes, iv_bytes, dek_bytes)
