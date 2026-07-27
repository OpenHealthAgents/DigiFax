"""
sso_adapter.py
SSO adapter implementing ISsoProvider for federated OIDC/SAML configurations.
"""

from src.application.ports.isso_provider import ISsoProvider
from src.domain.auth.value_objects import SsoConfig


class SsoAdapter(ISsoProvider):
    """
    Adapter implementing ISsoProvider interfaces.

    Purpose:
        Store federated configs and mock redirection assertions.
    """

    def __init__(self) -> None:
        self._configs: dict[str, SsoConfig] = {}

    def configure_sso(self, tenant_id: str, config: SsoConfig) -> None:
        """Configures federated metadata boundaries for a tenant."""
        self._configs[tenant_id] = config

    def get_redirect_url(self, tenant_id: str) -> str:
        """Returns the IDP redirection login endpoint URL."""
        if tenant_id not in self._configs:
            raise ValueError(f"SSO is not configured for tenant: {tenant_id}")
        config = self._configs[tenant_id]
        return f"{config.entry_point}?client_id=digifax&response_type=code"

    def handle_callback_assertion(self, callback_data: dict[str, str]) -> dict[str, str]:
        """Validates SAML assertions/OIDC codes, returning user details."""
        code = callback_data.get("code")
        if not code or code == "invalid-code":
            raise ValueError("Invalid OAuth code or SAML assertion")
        
        return {
            "email": "federated-practitioner@openhealth.org",
            "first_name": "Elizabeth",
            "last_name": "Blackwell"
        }
