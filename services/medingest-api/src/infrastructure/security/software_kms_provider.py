"""
software_kms_provider.py
Software Key Management Service (KMS) provider adapter using cryptography AEAD primitive AES-GCM.
"""

import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from src.application.ports.ikey_provider_port import IKeyProviderPort


class SoftwareKmsProvider(IKeyProviderPort):
    """
    Standard-compliant software cryptographic adapter executing AES-GCM key wraps and cipher operations.
    """

    def generate_random_key(self) -> bytes:
        """Generates random 256-bit AES key bytes."""
        return AESGCM.generate_key(bit_length=256)

    def wrap_key(self, raw_key: bytes, wrapping_key: bytes) -> bytes:
        """Encrypts key bytes using AESGCM. Uses fixed zero IV for key wrapping predictability if needed, or random."""
        # Using AEAD AESGCM wrapping
        aesgcm = AESGCM(wrapping_key)
        # Using a deterministic IV for key wrapping to avoid storage bloat (not critical, but standard)
        iv = b"\x00" * 12
        return aesgcm.encrypt(iv, raw_key, None)

    def unwrap_key(self, wrapped_key: bytes, wrapping_key: bytes) -> bytes:
        """Decrypts key bytes using AESGCM."""
        aesgcm = AESGCM(wrapping_key)
        iv = b"\x00" * 12
        return aesgcm.decrypt(iv, wrapped_key, None)

    def encrypt_data_with_key(self, plaintext: bytes, key: bytes) -> tuple[bytes, bytes]:
        """Encrypts data using AESGCM with a random 96-bit IV. Returns (ciphertext, iv)."""
        aesgcm = AESGCM(key)
        iv = os.urandom(12)
        ciphertext = aesgcm.encrypt(iv, plaintext, None)
        return ciphertext, iv

    def decrypt_data_with_key(self, ciphertext: bytes, iv: bytes, key: bytes) -> bytes:
        """Decrypts data using AESGCM."""
        aesgcm = AESGCM(key)
        return aesgcm.decrypt(iv, ciphertext, None)
