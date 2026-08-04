# Request-Scoped TenantContext Specification

This document details the design, configuration headers, and integration patterns of the request-scoped `TenantContext` in the medingest platform.

---

## 1. Architectural Pattern & Rationale

To comply with **Clean Architecture** boundaries, business logic (domain aggregates, use cases, and workflows) must remain decoupled from presentation layer protocols (HTTP, gRPC, or CLI).
* **The Rule**: No HTTP `Request`, `Header`, or `Form` objects may enter the Application or Domain layers.
* **The Solution**: An HTTP middleware or dependency resolver parses headers at the interface gateway, instantiates a type-safe `TenantContext` object, and injects it into application command payloads.

```
  [Client Request]
         │
         ▼
  ┌──────────────┐
  │ API Gateway  │ (Parses JWT, correlation IDs)
  └──────┬───────┘
         │
         ▼
  ┌──────────────┐
  │ FastAPI Deps │ ──► resolves TenantContext
  └──────┬───────┘
         │
         ▼
  ┌──────────────┐
  │ Intake Cmd   │ ──► carries TenantContext instance
  └──────┬───────┘
         │
         ▼
  ┌──────────────┐
  │ Intake UC    │ (Interacts solely with TenantContext properties)
  └──────────────┘
```

---

## 2. Inbound Header Mapping

The context resolver extracts the following headers from HTTP requests to hydrate the context:

| Header Name | Property Name | Type | Description / Default |
| :--- | :--- | :--- | :--- |
| `X-Tenant-ID` | `tenant_id` | `str` | Mandatory tenant UUID. |
| `X-Organization-ID` | `organization_id` | `str` | Optional facility UUID. |
| `X-User-ID` | `user_id` | `str` | Optional authenticated practitioner ID. |
| `X-Correlation-ID` | `correlation_id` | `str` | Trace correlation ID (Generates UUIDv4 if missing). |
| `X-Trace-ID` | `trace_id` | `str` | Trace identifier (Generates UUIDv4 if missing). |
| `Accept-Language` | `locale` | `str` | Target language locale (Default: `en-US`). |
| `X-Timezone` | `timezone` | `str` | Target local timezone (Default: `UTC`). |

---

## 3. Usage inside Use Case Handler

```python
class IngestDocumentUseCase:
    def execute(self, command: IngestDocumentCommand) -> str:
        # Resolve values directly from context payload
        tenant_id = command.context.tenant_id
        trace_id = command.context.trace_id
        
        # Enforce permissions checks
        if "document:write" not in command.context.permissions:
            raise PermissionError("Insufficient permissions")
            
        ...
```
