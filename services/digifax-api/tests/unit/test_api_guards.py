"""
test_api_guards.py
Integration tests asserting require_permissions endpoint authorization bounds, subscriptions, and flags.
"""

import pytest
from fastapi import HTTPException

from src.application.common.tenant_context import TenantContext
from src.infrastructure.controllers.api_guard import require_permissions


def test_require_permissions_authorized() -> None:
    # CLINICAL_REVIEWER has document:write permission
    context = TenantContext(
        tenant_id="tenant-123",
        roles=["CLINICAL_REVIEWER"]
    )
    guard = require_permissions("document:write")
    
    res = guard(context)
    assert res == context


def test_require_permissions_forbidden() -> None:
    # VIEWER lacks document:write permission
    context = TenantContext(
        tenant_id="tenant-123",
        roles=["VIEWER"]
    )
    guard = require_permissions("document:write")

    with pytest.raises(HTTPException) as exc_info:
        guard(context)
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail["code"] == "FORBIDDEN_PERMISSIONS"


def test_require_permissions_subscription_limit() -> None:
    # TENANT_OWNER has billing:write permission, but Standard tier blocks it
    context = TenantContext(
        tenant_id="tenant-123",
        roles=["TENANT_OWNER"],
        subscription_tier="Standard"
    )
    guard = require_permissions("billing:write")

    with pytest.raises(HTTPException) as exc_info:
        guard(context)
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail["code"] == "SUBSCRIPTION_LIMIT"


def test_require_permissions_feature_flag_missing() -> None:
    # CLINICAL_REVIEWER has document:write but auto_ocr flag is disabled
    context = TenantContext(
        tenant_id="tenant-123",
        roles=["CLINICAL_REVIEWER"],
        feature_flags={"auto_ocr": False}
    )
    guard = require_permissions("document:write", required_feature_flag="auto_ocr")

    with pytest.raises(HTTPException) as exc_info:
        guard(context)
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail["code"] == "FEATURE_DISABLED"
