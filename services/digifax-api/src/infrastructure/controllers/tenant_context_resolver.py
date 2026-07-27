"""
tenant_context_resolver.py
FastAPI dependency resolving header variables into request-scoped TenantContext containers.
"""

import uuid
from fastapi import Request, HTTPException

from src.application.common.tenant_context import TenantContext


async def resolve_tenant_context(request: Request) -> TenantContext:
    """
    Resolves request-scoped headers and maps them to a TenantContext container.

    Purpose:
        Extract and default request-level parameters.
    Business Reasoning:
        Decouples downstream business logic from direct FastAPI Request objects.
    Inputs:
        request (Request): The incoming FastAPI request instance.
    Outputs:
        TenantContext: Hydrated transaction context.
    Assumptions:
        None.
    Edge Cases:
        - Missing X-Tenant-ID header raises 400 Bad Request.
        - Missing correlation/trace IDs generate default UUIDv4s.
    """
    # 1. Resolve Tenant ID (Mandatory)
    tenant_id = request.headers.get("x-tenant-id")
    if not tenant_id:
        raise HTTPException(status_code=400, detail="X-Tenant-ID header is required")

    # 2. Resolve optional scoping IDs
    org_id = request.headers.get("x-organization-id")
    user_id = request.headers.get("x-user-id")

    # 3. Resolve request tracking identifiers
    correlation_id = request.headers.get("x-correlation-id") or str(uuid.uuid4())
    trace_id = request.headers.get("x-trace-id") or str(uuid.uuid4())

    # 4. Resolve client location properties
    locale = request.headers.get("accept-language") or "en-US"
    timezone = request.headers.get("x-timezone") or "UTC"

    # 5. Resolve client audit source properties
    ip_addr = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    # 6. Simulate role/permission/flag credentials resolving
    # Sandbox setup: tenant-123 and tenant-suspended get credentials
    if tenant_id in ["tenant-123", "tenant-suspended"]:
        roles = ["CLINICAL_REVIEWER"]
        permissions = ["document:read", "document:write"]
        sub_tier = "Gold"
        flags = {"auto_ocr": True, "loinc_mapping": True}
    else:
        roles = []
        permissions = []
        sub_tier = "Standard"
        flags = {}

    return TenantContext(
        tenant_id=tenant_id,
        organization_id=org_id,
        user_id=user_id,
        roles=roles,
        permissions=permissions,
        subscription_tier=sub_tier,
        feature_flags=flags,
        locale=locale,
        timezone=timezone,
        correlation_id=correlation_id,
        trace_id=trace_id,
        audit_ip_address=ip_addr,
        audit_user_agent=user_agent
    )
