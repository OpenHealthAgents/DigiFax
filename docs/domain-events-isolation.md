# Multi-Tenant Domain Events & Consumer Isolation

This document specifies the tracing metadata schema, event structures, and consumer tenant isolation guards designed for the DigiFax platform.

---

## 1. Unified Tracing Metadata Schema

All domain events emitted by aggregate roots in DigiFax must carry complete context tracking attributes to ensure audits and transactions are fully traceable.

### 1.1 Metadata Attributes:
* `tenant_id` (`str`): Mandatory SaaS subscriber partition ID.
* `organization_id` (`str | None`): Optional facility identifier.
* `correlation_id` (`str`): Identifies the initiating end-to-end request.
* `trace_id` (`str`): Tracing span scope.
* `user_id` (`str`): Authenticated user who performed the action.
* `occurred_at` (`datetime`): Event creation timestamp.
* `version` (`int`): Aggregate state version at emission time.

---

## 2. Consumer-Level Tenant Boundary Guard

When multiple tenants share an event-driven system (e.g. Kafka topics or RabbitMQ queues), an event consumer might receive events from multiple tenants. 

To satisfy HIPAA and multitenancy isolation compliance, the messaging consumer dispatch engine wraps all subscriber callbacks in a **Tenant Scoping Guard**:

```
  [Event Bus / Message Broker]
               │ (dispatches event)
               ▼
  ┌────────────────────────┐
  │  Tenant Scoping Guard  │ (Reads event.tenant_id)
  └────────────┬───────────┘
               │
      Matches consumer scope?
               │
        ┌──────┴──────┐
       Yes            No
        │             │
        ▼             ▼
  ┌──────────┐  ┌───────────┐
  │ Dispatch │  │   Block   │ (Raises PermissionError /
  │ Handler  │  │  Discard  │  Prevents cross-tenant leak)
  └──────────┘  └───────────┘
```

### 2.1 Guard Logic:
* If the consumer handler runs under a dedicated tenant boundary, it checks:
  ```python
  if event.tenant_id != consumer.tenant_id:
      raise PermissionError("Cross-tenant event consumption blocked")
  ```
* Shared platform-level services (e.g. central audit engines) can declare wildcard permissions to consume multi-tenant feeds.
