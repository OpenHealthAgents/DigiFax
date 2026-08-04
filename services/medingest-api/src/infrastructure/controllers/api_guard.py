"""
api_guard.py
FastAPI route dependency enforcing tenant scopes, permissions hierarchies, and feature flags.
"""

from fastapi import Depends, HTTPException

from src.application.common.tenant_context import TenantContext
from src.domain.auth.authorization_engine import AuthorizationEngine
from src.infrastructure.controllers.tenant_context_resolver import resolve_tenant_context


def require_permissions(required_permission: str, required_feature_flag: str | None = None):
    """
    Enforces authorization constraints against the resolved TenantContext.

    Purpose:
        Guard API controller endpoints.
    Business Reasoning:
        Verifies permission hierarchies and active SaaS flags before launching use cases.
    """
    def dependency(context: TenantContext = Depends(resolve_tenant_context)) -> TenantContext:
        # 1. Enforce RBAC permission checks using AuthorizationEngine
        auth_engine = AuthorizationEngine()
        user_role = context.roles[0] if context.roles else "VIEWER"

        if not auth_engine.is_authorized(
            user_role=user_role,
            user_tenant_id=context.tenant_id,
            required_permission=required_permission,
            target_tenant_id=context.tenant_id
        ):
            raise HTTPException(
                status_code=403,
                detail={
                    "message": "Forbidden: Insufficient permissions",
                    "code": "FORBIDDEN_PERMISSIONS"
                }
            )

        # 2. Enforce active subscription tier checks
        if context.subscription_tier == "Standard" and required_permission == "billing:write":
            raise HTTPException(
                status_code=403,
                detail={
                    "message": "Forbidden: Billing configurations require Enterprise subscription tier",
                    "code": "SUBSCRIPTION_LIMIT"
                }
            )

        # 3. Enforce optional feature flag restrictions
        if required_feature_flag and not context.feature_flags.get(required_feature_flag, False):
            raise HTTPException(
                status_code=403,
                detail={
                    "message": f"Forbidden: Feature {required_feature_flag} is not enabled for this tenant",
                    "code": "FEATURE_DISABLED"
                }
            )

        return context
    return dependency
