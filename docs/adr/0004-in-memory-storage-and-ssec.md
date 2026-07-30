# ADR 0004: In-Memory Storage & SSE-C Encryption Simulation

## Status
Approved

## Context
HIPAA guidelines dictate that Protected Health Information (PHI) must be encrypted at rest, and each tenant must be isolated at the physical storage layer (e.g. S3 directories).

## Decision
We implement:
1. **InMemoryStorage Adapter**: Logical segmentation is maintained using a nested dict structure partitioned by `tenant_id`.
2. **Server-Side Encryption with Customer-Provided Keys (SSE-C)**: The storage engine accepts `encryption_key` parameters, simulating encryption transforms during file saving and decryption during retrieval.
3. **Compliance Hold**: File modifications or updates are blocked if active retention locks exist.

## Consequences
* **Pros**: In-memory adapter maps directly to AWS S3 SSE-C capabilities without mock drift.
* **Cons**: Key management keys must be secured in a cloud Key Management Service (KMS) or vault.
