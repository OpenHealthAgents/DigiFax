"""
test_rbac.py
Unit tests verifying hierarchical RBAC permissions and resource-based ABAC policy evaluation rules.
"""

import pytest

from src.domain.auth.authorization_engine import AuthorizationEngine


def test_role_permissions_resolve() -> None:
    engine = AuthorizationEngine()
    
    # Viewer direct permission
    viewer_perms = engine.resolve_permissions("VIEWER")
    assert "document:read" in viewer_perms
    assert "document:write" not in viewer_perms

    # Uploader inherits Viewer
    uploader_perms = engine.resolve_permissions("UPLOADER")
    assert "document:read" in uploader_perms
    assert "document:write" in uploader_perms

    # Tenant Admin inherits Organization Admin, Reviewer, Clinician, etc.
    admin_perms = engine.resolve_permissions("TENANT_ADMIN")
    assert "document:read" in admin_perms
    assert "document:write" in admin_perms
    assert "document:verify" in admin_perms
    assert "workspace:manage" in admin_perms
    assert "billing:read" in admin_perms
    assert "billing:write" not in admin_perms  # Tenant Owner has billing:write


def test_custom_role_registration() -> None:
    engine = AuthorizationEngine()
    
    # Custom billing assistant inherits Viewer + has billing:read
    engine.register_custom_role(
        role_name="BILLING_ASSISTANT",
        parent_roles=["VIEWER"],
        permissions=["billing:read"]
    )

    perms = engine.resolve_permissions("BILLING_ASSISTANT")
    assert "document:read" in perms
    assert "billing:read" in perms
    assert "document:write" not in perms

    with pytest.raises(ValueError):
        engine.register_custom_role("   ", [], [])


def test_authorization_evaluation() -> None:
    engine = AuthorizationEngine()

    # Case A: Tenant Admin reads tenant document (Matching Tenant ID)
    assert engine.is_authorized(
        user_role="TENANT_ADMIN",
        user_tenant_id="tenant-123",
        required_permission="document:read",
        target_tenant_id="tenant-123"
    ) is True

    # Case B: Tenant Admin reads other tenant document (Cross-Tenant check)
    assert engine.is_authorized(
        user_role="TENANT_ADMIN",
        user_tenant_id="tenant-123",
        required_permission="document:read",
        target_tenant_id="tenant-456"
    ) is False

    # Case C: Platform Super Admin accesses any tenant document (Bypasses ABAC)
    assert engine.is_authorized(
        user_role="PLATFORM_SUPER_ADMIN",
        user_tenant_id="admin-tenant",
        required_permission="document:read",
        target_tenant_id="tenant-123"
    ) is True

    # Case D: Role lacks permission
    assert engine.is_authorized(
        user_role="VIEWER",
        user_tenant_id="tenant-123",
        required_permission="document:write",
        target_tenant_id="tenant-123"
    ) is False
