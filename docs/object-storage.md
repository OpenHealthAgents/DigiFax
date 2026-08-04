# Multi-Tenant Document Storage, Encryption, & Retention Policies

This document details the multi-tenant directory partitioning strategy, encryption models, compliance retention locks, and lifecycle policies.

---

## 1. Directory Partitioning Strategy

To guarantee absolute data isolation, all raw fax files and clinical parsing outcomes are physically structured using a tenant-namespaced directory layout:

```
  s3://medingest-clinical-bucket/
       ├── documents/
       │     ├── tenant-abc/
       │     │     ├── doc-11111.pdf
       │     │     └── doc-22222.pdf
       │     └── tenant-xyz/
       │           ├── doc-33333.pdf
       │           └── doc-44444.pdf
       └── cold-archive/
             └── tenant-abc/
                   └── doc-55555.pdf
```

### 1.1 Directory Schema
* `documents/{tenant_id}/{document_id}.{extension}`
* Standard prefixes ensure that IAM policies can dynamically restrict access using IAM Policy variables (e.g., matching `${aws:PrincipalTag/TenantID}`).

---

## 2. Server-Side Encryption (SSE-C)

To meet HIPAA audit specifications, every file is encrypted at rest using unique keys:
* **Write Pipeline**: File bytes are encrypted on ingest using an AES/XOR symmetric transform. If a customer-managed key is provided (SSE-C), it scrambles the payload.
* **Read Pipeline**: Retrieval requires providing the matching decryption key. Unauthorized reads with missing/incorrect keys raise `PermissionError`.

---

## 3. Compliance Retention & Lifecycle Policies

### 3.1 Retention Locks
* Files can declare a retention duration (`retention_days`).
* While under active retention, the adapter blocks any delete, overwrite, or modification requests, raising `PermissionError("File is locked under active retention hold")`.

### 3.2 Lifecycle Archiving Policies
* Automates clinical data transitions from hot tiers to cold archive tiers (e.g. S3 Glacier Deep Archive):
  ```python
  storage.apply_lifecycle_policy(tenant_id="tenant-abc", rule_name="ArchiveAfter90Days", days_to_archive=90)
  ```
* Transitions hot objects under the target prefix `documents/{tenant_id}/` to an archived status, simulating cold restore delays.
