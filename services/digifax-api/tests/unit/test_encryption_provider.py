"""
test_encryption_provider.py
Unit and controller integration tests verifying Cryptographic envelope encryption and KEK/DEK rotations.
"""

import base64
import pytest
from fastapi.testclient import TestClient

from src.domain.encryption.value_objects import CryptographicKey, EncryptedPayload
from src.domain.encryption.entities import TenantKeyRing
from src.application.use_cases.encryption.initialize_key_ring import InitializeKeyRingUseCase
from src.application.use_cases.encryption.rotate_tenant_keys import RotateTenantKeysUseCase
from src.application.use_cases.encryption.encrypt_tenant_data import EncryptTenantDataUseCase
from src.application.use_cases.encryption.decrypt_tenant_data import DecryptTenantDataUseCase
from src.infrastructure.security.local_secrets_manager import LocalSecretsManager
from src.infrastructure.security.software_kms_provider import SoftwareKmsProvider
from src.infrastructure.persistence.in_memory_key_ring_repository import InMemoryKeyRingRepository
from src.main import app


def test_key_value_object_validations() -> None:
    # 1. Empty ID
    with pytest.raises(ValueError):
        CryptographicKey(" ", "KEK", "AES-GCM-256", "2026-07-30")

    # 2. Invalid Key type
    with pytest.raises(ValueError):
        CryptographicKey("key-123", "MASTER", "AES-GCM-256", "2026-07-30")

    # 3. Empty algorithm
    with pytest.raises(ValueError):
        CryptographicKey("key-123", "DEK", "", "2026-07-30")


def test_envelope_encryption_roundtrip() -> None:
    repo = InMemoryKeyRingRepository()
    secrets = LocalSecretsManager()
    kms = SoftwareKmsProvider()

    encrypt_use_case = EncryptTenantDataUseCase(repo, secrets, kms)
    decrypt_use_case = DecryptTenantDataUseCase(repo, secrets, kms)

    plaintext = "OpenHealth clinical PHI record payload elements"

    # 1. Encrypt
    payload = encrypt_use_case.execute(tenant_id="tenant-encryption", data=plaintext.encode("utf-8"))
    assert payload.ciphertext != plaintext
    assert payload.kek_id.startswith("kek-tenant-encryption-")
    assert payload.dek_id.startswith("dek-tenant-encryption-")

    # Verify base64 decodability
    assert len(base64.b64decode(payload.ciphertext)) > 0
    assert len(base64.b64decode(payload.iv)) == 12

    # 2. Decrypt
    decrypted_bytes = decrypt_use_case.execute(tenant_id="tenant-encryption", payload=payload)
    assert decrypted_bytes.decode("utf-8") == plaintext


def test_key_rotation_unwraps_historical_data() -> None:
    repo = InMemoryKeyRingRepository()
    secrets = LocalSecretsManager()
    kms = SoftwareKmsProvider()

    encrypt_use_case = EncryptTenantDataUseCase(repo, secrets, kms)
    decrypt_use_case = DecryptTenantDataUseCase(repo, secrets, kms)
    rotate_use_case = RotateTenantKeysUseCase(repo, secrets, kms)

    plaintext = "Patient clinical chart notes"

    # 1. Encrypt payload under KEK v1
    payload_v1 = encrypt_use_case.execute(tenant_id="tenant-rotation", data=plaintext.encode("utf-8"))
    kek_v1_id = payload_v1.kek_id

    # 2. Execute KEK and DEK rotation (KEK v2)
    key_ring_v2 = rotate_use_case.execute(tenant_id="tenant-rotation")
    assert key_ring_v2.active_kek_id != kek_v1_id

    # 3. Decrypt old payload (encrypted under KEK v1) using new keyring (which has re-wrapped old DEKs!)
    decrypted_bytes = decrypt_use_case.execute(tenant_id="tenant-rotation", payload=payload_v1)
    assert decrypted_bytes.decode("utf-8") == plaintext


def test_encryption_http_endpoints() -> None:
    client = TestClient(app)

    # 1. Init keyring
    init_res = client.post(
        "/api/encryption/init",
        headers={"X-Tenant-Id": "tenant-crypto-http"}
    )
    assert init_res.status_code == 201
    assert "active_kek_id" in init_res.json()
    
    # 2. Encrypt plaintext
    plaintext = "Secure Lab Results"
    encrypt_res = client.post(
        "/api/encryption/encrypt",
        headers={"X-Tenant-Id": "tenant-crypto-http"},
        json={"plaintext": plaintext}
    )
    assert encrypt_res.status_code == 200
    payload_data = encrypt_res.json()
    assert "ciphertext" in payload_data
    assert "iv" in payload_data
    
    # 3. Decrypt ciphertext
    decrypt_res = client.post(
        "/api/encryption/decrypt",
        headers={"X-Tenant-Id": "tenant-crypto-http"},
        json={
            "ciphertext": payload_data["ciphertext"],
            "iv": payload_data["iv"],
            "encrypted_dek": payload_data["encrypted_dek"],
            "dek_id": payload_data["dek_id"],
            "kek_id": payload_data["kek_id"]
        }
    )
    assert decrypt_res.status_code == 200
    assert decrypt_res.json()["plaintext"] == plaintext

    # 4. Rotate keys
    rotate_res = client.post(
        "/api/encryption/rotate",
        headers={"X-Tenant-Id": "tenant-crypto-http"}
    )
    assert rotate_res.status_code == 200
    assert rotate_res.json()["active_kek_id"] != payload_data["kek_id"]
