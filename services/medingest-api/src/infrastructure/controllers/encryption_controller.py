"""
encryption_controller.py
FastAPI controller routing tenant key initializations, rotations, and crypt operations.
"""

from typing import Any
from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel, Field

from src.application.use_cases.encryption.initialize_key_ring import InitializeKeyRingUseCase
from src.application.use_cases.encryption.rotate_tenant_keys import RotateTenantKeysUseCase
from src.application.use_cases.encryption.encrypt_tenant_data import EncryptTenantDataUseCase
from src.application.use_cases.encryption.decrypt_tenant_data import DecryptTenantDataUseCase
from src.domain.encryption.value_objects import EncryptedPayload
from src.infrastructure.security.local_secrets_manager import LocalSecretsManager
from src.infrastructure.security.software_kms_provider import SoftwareKmsProvider
from src.infrastructure.persistence.in_memory_key_ring_repository import InMemoryKeyRingRepository

router = APIRouter(prefix="/api/encryption", tags=["Encryption Management"])

_key_ring_repo = InMemoryKeyRingRepository()
_secrets_manager = LocalSecretsManager()
_kms_provider = SoftwareKmsProvider()


# --- REQUEST & RESPONSE SCHEMAS ---

class EncryptRequest(BaseModel):
    plaintext: str = Field(..., description="Plaintext data string to envelope encrypt")


class DecryptRequest(BaseModel):
    ciphertext: str
    iv: str
    encrypted_dek: str
    dek_id: str
    kek_id: str


class EncryptResponse(BaseModel):
    ciphertext: str
    iv: str
    encrypted_dek: str
    dek_id: str
    kek_id: str


# --- ROUTERS ---

@router.post("/init", status_code=status.HTTP_201_CREATED)
def initialize_key_ring(
    x_tenant_id: str = Header(..., alias="X-Tenant-Id")
) -> Any:
    """Initializes tenant-scoped envelope KeyRings."""
    use_case = InitializeKeyRingUseCase(_key_ring_repo, _secrets_manager, _kms_provider)
    key_ring = use_case.execute(tenant_id=x_tenant_id)
    return {
        "tenant_id": key_ring.tenant_id,
        "active_kek_id": key_ring.active_kek_id,
        "active_dek_id": key_ring.active_dek_id,
        "history_count": len(key_ring.history)
    }


@router.post("/rotate", status_code=status.HTTP_200_OK)
def rotate_tenant_keys(
    x_tenant_id: str = Header(..., alias="X-Tenant-Id")
) -> Any:
    """Rotates active KEK keys and re-wraps existing DEKs."""
    use_case = RotateTenantKeysUseCase(_key_ring_repo, _secrets_manager, _kms_provider)
    try:
        key_ring = use_case.execute(tenant_id=x_tenant_id)
        return {
            "tenant_id": key_ring.tenant_id,
            "active_kek_id": key_ring.active_kek_id,
            "active_dek_id": key_ring.active_dek_id,
            "history_count": len(key_ring.history)
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/encrypt", response_model=EncryptResponse)
def encrypt_data(
    req: EncryptRequest,
    x_tenant_id: str = Header(..., alias="X-Tenant-Id")
) -> Any:
    """Envelope encrypts data under active KEK/DEK keys."""
    use_case = EncryptTenantDataUseCase(_key_ring_repo, _secrets_manager, _kms_provider)
    payload = use_case.execute(tenant_id=x_tenant_id, data=req.plaintext.encode("utf-8"))
    return EncryptResponse(
        ciphertext=payload.ciphertext,
        iv=payload.iv,
        encrypted_dek=payload.encrypted_dek,
        dek_id=payload.dek_id,
        kek_id=payload.kek_id
    )


@router.post("/decrypt")
def decrypt_data(
    req: DecryptRequest,
    x_tenant_id: str = Header(..., alias="X-Tenant-Id")
) -> Any:
    """Decrypts data, resolving historic KEK wraps from history list keys."""
    use_case = DecryptTenantDataUseCase(_key_ring_repo, _secrets_manager, _kms_provider)
    payload = EncryptedPayload(
        ciphertext=req.ciphertext,
        iv=req.iv,
        encrypted_dek=req.encrypted_dek,
        dek_id=req.dek_id,
        kek_id=req.kek_id
    )
    try:
        decrypted_bytes = use_case.execute(tenant_id=x_tenant_id, payload=payload)
        return {"plaintext": decrypted_bytes.decode("utf-8")}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Decryption failed: {str(e)}")
