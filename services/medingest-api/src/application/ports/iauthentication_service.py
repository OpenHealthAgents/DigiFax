"""
iauthentication_service.py
Outbound port interface abstracting authentication actions (login, switch, refresh).
"""

import abc
from src.domain.auth.value_objects import UserSession, AuthToken


class IAuthenticationService(abc.ABC):
    """
    Outbound port interface defining identity authentication transactions.

    Why It Exists:
        To decouple security libraries (e.g. Better Auth, Auth0) from application domain codes.
    """

    @abc.abstractmethod
    def login_tenant(self, email: str, tenant_id: str) -> UserSession:
        """
        Logs in a user under a specific Tenant subscription boundary.

        Purpose:
            Establish access context.
        Business Reasoning:
            Ensures credentials resolve to correct subscribers.
        """
        pass

    @abc.abstractmethod
    def switch_organization(self, token_value: str, target_org_id: str) -> AuthToken:
        """
        Switches the active membership context to a different Organization.

        Purpose:
            Change current active facility.
        Business Reasoning:
            Supports practitioners holding memberships across separate facilities.
        """
        pass

    @abc.abstractmethod
    def refresh_session(self, refresh_token: str) -> UserSession:
        """
        Renews an expired AuthToken.

        Purpose:
            Refresh active tokens without requesting password logins.
        """
        pass

    @abc.abstractmethod
    def verify_invitation_token(self, token: str) -> dict[str, str]:
        """
        Verifies register link verification tokens.

        Purpose:
            Confirm invitation token is valid.
        """
        pass
class_names = ["IAuthenticationService"]
