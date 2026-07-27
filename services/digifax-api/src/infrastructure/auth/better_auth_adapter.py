"""
better_auth_adapter.py
Infrastructure adapter isolating Better Auth library behind the IAuthenticationService contract.
"""

from datetime import datetime, timedelta

from src.application.ports.iauthentication_service import IAuthenticationService
from src.domain.auth.value_objects import UserSession, AuthToken


class BetterAuthAdapter(IAuthenticationService):
    """
    Adapter implementing IAuthenticationService, simulating "Better Auth" provider mechanisms.

    Purpose:
        Perform token assertions, session scoping, and invitation validations.
    Business Reasoning:
        Ensures compliance with ports & adapters separation rules.
    """

    def __init__(self) -> None:
        # Mock storage database mimicking Better Auth session rows
        self._mock_users = {
            "practitioner@openhealth.org": {
                "user_id": "usr-1",
                "memberships": {
                    "org-main": "CLINICAL_REVIEWER",
                    "org-stjude": "CLINICAL_REVIEWER"
                }
            }
        }
        self._mock_invitations = {
            "inv-token-valid": {
                "email": "practitioner@stjude.org",
                "org_id": "org-stjude",
                "role": "CLINICAL_REVIEWER"
            }
        }

    def login_tenant(self, email: str, tenant_id: str) -> UserSession:
        """Logs in a user under a specific Tenant subscription boundary."""
        if email not in self._mock_users:
            raise ValueError("Invalid user credentials")

        user_data = self._mock_users[email]
        # Generate raw JWT token
        token_expires = datetime.now() + timedelta(hours=8)
        token = AuthToken(value=f"jwt_token_for_{user_data['user_id']}", expires_at=token_expires)

        # Default to first membership organization
        org_id = list(user_data["memberships"].keys())[0]
        role_name = user_data["memberships"][org_id]

        return UserSession(
            token=token,
            user_id=user_data["user_id"],
            email=email,
            tenant_id=tenant_id,
            organization_id=org_id,
            roles=[role_name],
            permissions=["document:read", "document:write"] if role_name == "CLINICAL_REVIEWER" else []
        )

    def switch_organization(self, token_value: str, target_org_id: str) -> AuthToken:
        """Switches the active membership context to a different Organization."""
        # Validate active session token (mock verification)
        if not token_value.startswith("jwt_token_for_"):
            raise PermissionError("Invalid session token")

        # Resolve user details
        user_id = token_value.replace("jwt_token_for_", "")
        
        # Locate memberships
        matched_user = None
        for email, details in self._mock_users.items():
            if details["user_id"] == user_id:
                matched_user = details
                break

        if not matched_user or target_org_id not in matched_user["memberships"]:
            raise PermissionError("User does not hold membership in target organization")

        # Issue new AuthToken scoped to target facility
        new_expires = datetime.now() + timedelta(hours=8)
        return AuthToken(value=f"jwt_token_for_{user_id}_scoped_{target_org_id}", expires_at=new_expires)

    def refresh_session(self, refresh_token: str) -> UserSession:
        """Renews an expired AuthToken."""
        if not refresh_token.startswith("refresh_token_for_"):
            raise ValueError("Invalid refresh token")
        
        user_id = refresh_token.replace("refresh_token_for_", "")
        new_expires = datetime.now() + timedelta(hours=8)
        token = AuthToken(value=f"jwt_token_for_{user_id}", expires_at=new_expires)

        return UserSession(
            token=token,
            user_id=user_id,
            email="practitioner@openhealth.org",
            tenant_id="tenant-123",
            organization_id="org-main",
            roles=["CLINICAL_REVIEWER"],
            permissions=["document:read", "document:write"]
        )

    def verify_invitation_token(self, token: str) -> dict[str, str]:
        """Verifies register link verification tokens."""
        if token not in self._mock_invitations:
            raise ValueError("Invalid or expired invitation token")
        return self._mock_invitations[token]
