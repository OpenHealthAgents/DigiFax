# ADR 0005: Event Bus Scoping & Temporal Workflow Isolation

## Status
Approved

## Context
Asynchronous integrations (NATS event bus, Temporal orchestration workflow worker tasks) execute outside the context of direct HTTP requests. We must ensure events and workflows are isolated.

## Decision
We implement:
1. **Tenant-Aware Event Subscription**: `InMemoryEventBus.subscribe` takes an optional `consumer_tenant_id`.
2. **Scoping Guards**: During publishing, the bus asserts that if a subscriber is tenant-scoped, the event `tenant_id` must match `consumer_tenant_id`. Mismatches raise `PermissionError`.
3. **TenantContext Interceptor**: Workflows propagate `TenantContext` parameters down to activity layers, verifying isolation boundaries throughout.

## Consequences
* **Pros**: Prevents cross-tenant ingestion leaks on async loops.
* **Cons**: Interceptor overhead on Temporal state contexts.
