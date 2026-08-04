"""
test_tenant_context.py
Unit tests verifying TenantContext properties and FastAPI header resolution dependencies.
"""

import pytest
from fastapi import Request, HTTPException

from src.application.common.tenant_context import TenantContext
from src.infrastructure.controllers.tenant_context_resolver import resolve_tenant_context


def test_tenant_context_creation() -> None:
    context = TenantContext(
        tenant_id="tenant-123",
        organization_id="org-456",
        user_id="user-789",
        roles=["REVIEWER"],
        permissions=["document:read"],
        subscription_tier="Enterprise",
        feature_flags={"auto_ocr": True},
        locale="en-US",
        timezone="EST",
        correlation_id="corr-abc",
        trace_id="trace-xyz",
        audit_ip_address="127.0.0.1",
        audit_user_agent="Firefox"
    )

    assert context.tenant_id == "tenant-123"
    assert context.organization_id == "org-456"
    assert context.user_id == "user-789"
    assert "REVIEWER" in context.roles
    assert "document:read" in context.permissions
    assert context.subscription_tier == "Enterprise"
    assert context.feature_flags["auto_ocr"] is True
    assert context.locale == "en-US"
    assert context.timezone == "EST"
    assert context.correlation_id == "corr-abc"
    assert context.trace_id == "trace-xyz"
    assert context.audit_ip_address == "127.0.0.1"
    assert context.audit_user_agent == "Firefox"


def test_tenant_context_creation_empty_tenant() -> None:
    with pytest.raises(ValueError):
        TenantContext(tenant_id="   ")


@pytest.mark.anyio
async def test_resolve_tenant_context_success() -> None:
    # Build mock request
    scope = {
        "type": "http",
        "headers": [
            (b"x-tenant-id", b"tenant-123"),
            (b"x-organization-id", b"org-456"),
            (b"x-user-id", b"user-789"),
            (b"x-correlation-id", b"corr-abc"),
            (b"x-trace-id", b"trace-xyz"),
            (b"accept-language", b"en-GB"),
            (b"x-timezone", b"PST"),
            (b"user-agent", b"Chrome")
        ],
        "client": ("127.0.0.1", 8080)
    }
    request = Request(scope=scope)

    context = await resolve_tenant_context(request)

    assert context.tenant_id == "tenant-123"
    assert context.organization_id == "org-456"
    assert context.user_id == "user-789"
    assert context.correlation_id == "corr-abc"
    assert context.trace_id == "trace-xyz"
    assert context.locale == "en-GB"
    assert context.timezone == "PST"
    assert context.audit_ip_address == "127.0.0.1"
    assert context.audit_user_agent == "Chrome"
    assert "CLINICAL_REVIEWER" in context.roles
    assert "document:read" in context.permissions


@pytest.mark.anyio
async def test_resolve_tenant_context_missing_tenant() -> None:
    scope = {
        "type": "http",
        "headers": []
    }
    request = Request(scope=scope)

    with pytest.raises(HTTPException) as exc_info:
        await resolve_tenant_context(request)
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "X-Tenant-ID header is required"


@pytest.mark.anyio
async def test_resolve_tenant_context_defaults() -> None:
    scope = {
        "type": "http",
        "headers": [
            (b"x-tenant-id", b"tenant-custom")
        ]
    }
    request = Request(scope=scope)

    context = await resolve_tenant_context(request)

    assert context.tenant_id == "tenant-custom"
    assert context.organization_id is None
    assert context.user_id is None
    assert context.correlation_id != ""
    assert context.trace_id != ""
    assert context.locale == "en-US"
    assert context.timezone == "UTC"
    assert context.roles == []
    assert context.permissions == []
    assert context.subscription_tier == "Standard"
