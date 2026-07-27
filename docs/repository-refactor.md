# Multi-Tenant Repository Refactoring Specification

This document details the features, design patterns, and compliance controls implemented across all data repositories in the DigiFax platform.

---

## 1. Unified Repository Features

Every database repository implements the following requirements:

### 1.1 Tenant & Organization Isolation
* **Direct Scoping**: Repository methods (e.g. `get_by_id`, `find_all`) enforce `tenant_id` and optional `organization_id` filters.
* **Leak Protection**: Database engine policies and repository query code prevent users from accidentally fetching other tenants' data.

### 1.2 Soft Deletes
* **Logical Flags**: Deletion mutates a record's attributes (`is_deleted = True`, `deleted_at = datetime.now()`, `deleted_by = user_id`) instead of purging physical rows.
* **Automatic Exclusions**: Queries automatically omit soft-deleted records unless explicitly requested using `include_deleted=True`.

### 1.3 Auditing
* Every write transaction records audit trails:
  * `created_at` / `created_by` on instantiation.
  * `updated_at` / `updated_by` on mutation.

### 1.4 Optimistic Concurrency Control (OCC)
* Protects against concurrent modifications (race conditions) without utilizing blocking database locks.
* **The Logic**:
  1. Every record contains a `version` field (defaults to `1`).
  2. On update, the repository verifies that the database version matches the version in memory:
     ```sql
     UPDATE intake_documents SET ... version = version + 1
     WHERE id = :id AND version = :expected_version;
     ```
  3. If zero rows are mutated (indicating another process updated the record in the meantime), the repository raises a `ConcurrencyException`.

### 1.5 Pagination
* Avoids database memory saturation when querying large datasets.
* All list retrieval methods support `limit` and `offset` parameter pagination.

---

## 2. In-Memory Base Implementation Class

To ensure consistency and prevent code duplication, a `BaseInMemoryRepository` class is implemented. This class encapsulates thread-safe locks, logical maps, OCC version checks, soft deletes, and pagination loops, allowing concrete domain repositories to subclass and inherit these functionalities directly.
