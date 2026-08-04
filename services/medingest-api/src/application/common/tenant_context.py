"""
tenant_context.py
Request-scoped context container encapsulating tenant credentials, billing plans, and telemetry scopes.
"""

class TenantContext:
    """
    Request-scoped context carrying tenant configurations, security credentials, and tracing variables.

    Purpose:
        Unify request-specific parameters into a single object passed downstream.
    Business Reasoning:
        Clinical logs and actions must trace back to concrete users, IPs, and tenants for audit trails.
    """

    def __init__(
        self,
        tenant_id: str,
        organization_id: str | None = None,
        user_id: str | None = None,
        roles: list[str] | None = None,
        permissions: list[str] | None = None,
        subscription_tier: str = "Standard",
        feature_flags: dict[str, bool] | None = None,
        locale: str = "en-US",
        timezone: str = "UTC",
        correlation_id: str = "",
        trace_id: str = "",
        audit_user_agent: str | None = None,
        audit_ip_address: str | None = None
    ):
        if not tenant_id.strip():
            raise ValueError("tenant_id cannot be empty")
        self.tenant_id = tenant_id
        self.organization_id = organization_id
        self.user_id = user_id
        self.roles = roles or []
        self.permissions = permissions or []
        self.subscription_tier = subscription_tier
        self.feature_flags = feature_flags or {}
        self.locale = locale
        self.timezone = timezone
        self.correlation_id = correlation_id
        self.trace_id = trace_id
        self.audit_user_agent = audit_user_agent
        self.audit_ip_address = audit_ip_address
