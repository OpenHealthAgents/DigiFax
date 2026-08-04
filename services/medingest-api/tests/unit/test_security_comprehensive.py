"""
test_security_comprehensive.py
Comprehensive security test suite asserting RBAC guards, session refresh, API key expirations, and compliance audit policies.
"""

import pytest
from datetime import datetime, timedelta
from fastapi import HTTPException

# Security Guards
from src.application.common.tenant_context import TenantContext
from src.infrastructure.controllers.api_guard import require_permissions

# Auth and API Keys
from src.domain.tenant_management.entities import ApiKey
from src.infrastructure.auth.better_auth_adapter import BetterAuthAdapter

# Compliance Auditing
from src.domain.tenant_management.value_objects import AuditPolicy
from src.infrastructure.persistence.base_repository import BaseInMemoryRepository


# --- 1. RBAC API GUARDS TESTS ---

def test_api_guard_permission_enforcement() -> None:
    # 1. Access with valid permissions (should pass without exception)
    context_ok = TenantContext(
        tenant_id="tenant-123",
        roles=["CLINICAL_REVIEWER"],
        permissions=["document:read", "document:write"]
    )
    guard_ok = require_permissions("document:read")
    res = guard_ok(context_ok)
    assert res == context_ok

    # 2. Access with invalid permissions (should raise 403 Forbidden)
    context_no_perms = TenantContext(
        tenant_id="tenant-123",
        roles=["VIEWER"],
        permissions=["document:read"]
    )
    guard_forbidden = require_permissions("billing:write")
    with pytest.raises(HTTPException) as exc_info:
        guard_forbidden(context_no_perms)
    
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail["code"] == "FORBIDDEN_PERMISSIONS"


# --- 2. SESSION TIMEOUTS & REFRESH TESTS ---

def test_authentication_session_renewal() -> None:
    adapter = BetterAuthAdapter()
    
    # Refresh session using mock refresh token
    session = adapter.refresh_session("refresh_token_for_usr-1")
    assert session.user_id == "usr-1"
    assert session.token.value == "jwt_token_for_usr-1"
    assert session.token.expires_at > datetime.now()


# --- 3. API KEYS EXPIRATION TESTS ---

def test_api_key_validations_and_expiries() -> None:
    # 1. Active key (no expiration or far expiration)
    key_active = ApiKey("key-1", "hash-abc", "Production Inbound Gateway")
    assert key_active.is_expired(datetime.now()) is False

    # 2. Expired key
    expired_date = datetime.now() - timedelta(minutes=5)
    key_expired = ApiKey("key-2", "hash-xyz", "Legacy Scanner Gateway", expires_at=expired_date)
    assert key_expired.is_expired(datetime.now()) is True

    # 3. Label validation
    with pytest.raises(ValueError):
        ApiKey("key-3", "hash", "  ")


# --- 4. COMPLIANCE AUDITING TESTS ---

def test_compliance_auditing_policy() -> None:
    repo = BaseInMemoryRepository()
    
    # Save record with auditing user context
    repo._save_record("rec-10", {"id": "rec-10", "tenant_id": "tenant-alice", "val": "data"}, user_id="user-alice")

    record = repo._get_record_by_id("rec-10", "tenant-alice")
    
    # Assert auditing metadata timestamps and creator ID are recorded
    assert record["created_by"] == "user-alice"
    assert isinstance(record["created_at"], datetime)
    assert record["updated_by"] == "user-alice"
    assert isinstance(record["updated_at"], datetime)
    assert record["version"] == 1
