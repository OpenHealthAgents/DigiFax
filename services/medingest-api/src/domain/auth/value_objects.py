"""
value_objects.py
Domain value objects representing sessions, tokens, and Single Sign-On configs.
"""

from datetime import datetime
from src.domain.common.value_object import ValueObject


class AuthToken(ValueObject):
    """
    Value object wrapping a raw JWT access credential string.

    Purpose:
        Wrap token values securely.
    Business Reasoning:
        Decouples token generation formats from controller routing logic.
    """

    def __init__(self, value: str, expires_at: datetime):
        if not value.strip():
            raise ValueError("Token value cannot be empty")
        self.value = value
        self.expires_at = expires_at

    def is_expired(self, current_time: datetime) -> bool:
        """Checks expiration."""
        return current_time > self.expires_at


class UserSession(ValueObject):
    """
    Value object representing a logged-in practitioner's session context.

    Purpose:
        Carries validated tenant roles, permission lists, and active tokens.
    Business Reasoning:
        Clinical review sessions must map explicitly to verified identities.
    """

    def __init__(
        self,
        token: AuthToken,
        user_id: str,
        email: str,
        tenant_id: str,
        organization_id: str | None,
        roles: list[str],
        permissions: list[str]
    ):
        self.token = token
        self.user_id = user_id
        self.email = email
        self.tenant_id = tenant_id
        self.organization_id = organization_id
        self.roles = roles
        self.permissions = permissions


class SsoConfig(ValueObject):
    """
    Value object mapping SAML / OIDC metadata entrypoint specifications.

    Purpose:
        Hold enterprise identity provider configs.
    Business Reasoning:
        Enterprise clients require integrating custom SSO loops.
    """

    def __init__(self, provider_type: str, entry_point: str, certificate: str | None = None):
        if provider_type not in ["SAML", "OIDC"]:
            raise ValueError("Unsupported provider_type. Allowed: SAML, OIDC")
        if not entry_point.strip():
            raise ValueError("SSO entry_point cannot be empty")
        self.provider_type = provider_type
        self.entry_point = entry_point
        self.certificate = certificate
