# Domain Guide: Cryptographic Encryption & Envelope Wrapping

The **Encryption** Bounded Context enforces envelope encryption at rest, tenant-scoped Key Encryption Keys (KEK), Data Encryption Keys (DEKs), key rotation workflows, and pluggable KMS/HSM keystores.

---

## Architectural Context Map

```mermaid
graph TD
    User([System Process]) -->|Plaintext| API[Encryption API Controller]
    API -->|1. encrypt_data| UseCase[EncryptTenantDataUseCase]
    UseCase -->|2. get_master_key| Secrets[ISecretsManagerPort]
    UseCase -->|3. generate_random_key| KMS[IKeyProviderPort]
    UseCase -->|4. wrap_key / encrypt| KMS
    KMS -->|AES-GCM-256| HSM([Future Hardware Security Module / HSM])
    UseCase -->|5. save_key_ring| Repo[IKeyRingRepository]
    Repo -->|Persist Keyring| DB[(InMemory Persistence Store)]
```

---

## Cryptographic Envelope Design

Symmetric data encryption utilizes envelope wrapping, isolating tenant data:
1. **Master Key**: Enclosed inside a secure key vault (Secrets Manager), wraps individual tenant Key Encryption Keys (KEKs).
2. **Key Encryption Key (KEK)**: Tenant-specific key stored wrapped by the system Master Key, used to wrap the tenant's active Data Encryption Key (DEK).
3. **Data Encryption Key (DEK)**: Tenant-specific key stored wrapped by the tenant's KEK, used directly to encrypt patient resources with AES-GCM-256.

---

## Key Rotation Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    Client->>API: POST /api/encryption/rotate
    API->>UseCase: execute(tenant_id)
    UseCase->>Repo: get_key_ring(tenant_id)
    Repo-->>UseCase: TenantKeyRing
    UseCase->>Secrets: get_master_key()
    Secrets-->>UseCase: Master Key bytes
    UseCase->>KMS: generate_random_key() (New KEK)
    KMS-->>UseCase: New KEK bytes
    UseCase->>KMS: wrap_key(New KEK, Master Key)
    KMS-->>UseCase: Wrapped New KEK
    Note over UseCase, KMS: Re-wrap existing DEKs with new KEK
    loop for each DEK
        UseCase->>KMS: unwrap_key(Wrapped DEK, Old KEK)
        KMS-->>UseCase: Raw DEK
        UseCase->>KMS: wrap_key(Raw DEK, New KEK)
        KMS-->>UseCase: Re-wrapped DEK
    end
    UseCase->>Repo: save_key_ring(TenantKeyRing)
    Repo-->>UseCase: Done
    UseCase-->>API: TenantKeyRing metadata
    API-->>Client: HTTP 200 OK (Rotation success)
```
