"""
isso_provider.py
Outbound port interface abstracting federated Single Sign-On (SAML / OIDC).
"""

import abc
from src.domain.auth.value_objects import SsoConfig


class ISsoProvider(abc.ABC):
    """
    Outbound port interface defining Single Sign-On configuration and handshakes.

    Why It Exists:
        To support custom SAML / OIDC login redirections for enterprise health networks.
    """

    @abc.abstractmethod
    def configure_sso(self, tenant_id: str, config: SsoConfig) -> None:
        """Configures federated metadata boundaries for a tenant."""
        pass

    @abc.abstractmethod
    def get_redirect_url(self, tenant_id: str) -> str:
        """Returns the IDP redirection login endpoint URL."""
        pass

    @abc.abstractmethod
    def handle_callback_assertion(self, callback_data: dict[str, str]) -> dict[str, str]:
        """Validates SAML assertions/OIDC codes, returning user details."""
        pass
