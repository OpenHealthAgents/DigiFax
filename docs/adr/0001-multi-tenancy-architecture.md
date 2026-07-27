# ADR 0001: Multi-Tenancy Architecture Design

## Status
Approved

## Context
The initial implementation of the DigiFax ingestion pipeline was single-tenant. To support enterprise SaaS operations where multiple clinical customers (hospitals, outpatient networks) share the same application cluster, the platform must transition to a secure multi-tenant design that enforces logical data partitioning, isolated physical/logical storage paths, and request authentication.

## Decision
We implement a **Logical Multi-Tenancy Partitioning Model** across all Clean Architecture layers:

1. **Domain Layer**:
   * Introduce a `Tenant` aggregate root managing tenant name, status (e.g. Active, Suspended), and ingestion limits.
   * Add a mandatory `tenant_id: str` to the `IntakeDocument` aggregate root and associated domain events.

2. **Application Layer**:
   * Enforce partition-aware repository signatures (e.g. requiring `tenant_id` in `IIntakeDocumentRepository.get_by_id`).
   * Introduce `ITenantRepository` for tenant directory checks.
   * Verify that the requesting tenant exists and is active inside the use case execution cycle.
   * Segment document storage paths: `raw/{tenant_id}/{document_id}.{extension}`.

3. **Infrastructure / Controller Layer**:
   * Resolve and authenticate the active tenant from incoming REST requests using an `X-Tenant-ID` header.
   * Reject request scopes with 401/403 errors if the tenant ID is missing or inactive.

## Consequences
* **Pros**: Logical partitioning is lightweight, does not require separate database connections, and guarantees query safety.
* **Cons**: Developers must remember to pass `tenant_id` parameters to repositories. This is mitigated by design-level signature checks.
