"""
ikey_provider_port.py
Outbound port abstracting Key Management Services (KMS) or Hardware Security Modules (HSM).
"""

from abc import ABC, abstractmethod


class IKeyProviderPort(ABC):
    """
    Cryptographic key generator and provider port interface.
    """

    @abstractmethod
    def generate_random_key(self) -> bytes:
        """Generates random 256-bit symmetric key bytes."""
        pass

    @abstractmethod
    def wrap_key(self, raw_key: bytes, wrapping_key: bytes) -> bytes:
        """Encrypts/wraps key bytes using a wrapping key with AES-GCM."""
        pass

    @abstractmethod
    def unwrap_key(self, wrapped_key: bytes, wrapping_key: bytes) -> bytes:
        """Decrypts/unwraps key bytes using a wrapping key with AES-GCM."""
        pass

    @abstractmethod
    def encrypt_data_with_key(self, plaintext: bytes, key: bytes) -> tuple[bytes, bytes]:
        """Encrypts plaintext bytes with raw key using AES-GCM. Returns (ciphertext, iv)."""
        pass

    @abstractmethod
    def decrypt_data_with_key(self, ciphertext: bytes, iv: bytes, key: bytes) -> bytes:
        """Decrypts ciphertext bytes with raw key using AES-GCM."""
        pass
