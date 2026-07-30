"""
value_objects.py
Domain Value Objects representing CryptographicKeys and envelope-encrypted payloads.
"""

from dataclasses import dataclass
from src.domain.common.value_object import ValueObject


@dataclass(frozen=True)
class CryptographicKey(ValueObject):
    """Immutable representation of a cryptographic key metadata."""
    key_id: str
    key_type: str  # KEK, DEK
    algorithm: str  # e.g., AES-GCM-256
    created_at: str

    def __post_init__(self) -> None:
        if not self.key_id.strip():
            raise ValueError("Key ID cannot be empty")
        if self.key_type not in ("KEK", "DEK"):
            raise ValueError("Key type must be KEK or DEK")
        if not self.algorithm.strip():
            raise ValueError("Algorithm cannot be empty")


@dataclass(frozen=True)
class EncryptedPayload(ValueObject):
    """Container for envelope-encrypted ciphertexts and DEKs."""
    ciphertext: str
    iv: str
    encrypted_dek: str  # DEK encrypted by KEK
    dek_id: str
    kek_id: str
