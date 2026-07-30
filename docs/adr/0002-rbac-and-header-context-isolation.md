# ADR 0002: Role-Based Access Control (RBAC) & Header Context Isolation

## Status
Approved

## Context
Multiple operators inside a single Tenant (e.g. clinicians, billers, super admins) require differentiated administrative and clinical capabilities. Uncontrolled request scopes could lead to privilege escalations.

## Decision
We enforce a structured Role-Based Access Control (RBAC) model:
1. **TenantContext**: Every HTTP request maps variables into a `TenantContext` container including active roles and permissions.
2. **FastAPI Guards**: Endpoints use dependency injected route guards (`require_permissions`) confirming required permissions before routing requests.
3. **Role Hierarchy**: Standardize roles (`Platform Super Admin`, `Tenant Owner`, `Clinician`, `Reviewer`, `Auditor`) with specific permissions boundaries (e.g. `document:read`, `billing:write`).

## Consequences
* **Pros**: Simple, declarative endpoint annotations that are easily auditable.
* **Cons**: Relies on header resolution in mock environments. This requires edge API gateways to strip outside user headers before routing.
