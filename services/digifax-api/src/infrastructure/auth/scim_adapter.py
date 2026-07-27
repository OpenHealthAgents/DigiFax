"""
scim_adapter.py
SCIM directory sync adapter implementing IUserProvisioningService.
"""

from src.application.ports.iuser_provisioning_service import IUserProvisioningService


class ScimAdapter(IUserProvisioningService):
    """
    Adapter implementing IUserProvisioningService.

    Purpose:
        Handle programmatic provisioning hooks.
    """

    def __init__(self) -> None:
        self._provisioned_users: dict[str, dict] = {}

    def provision_user(self, tenant_id: str, user_email: str, raw_scim_payload: dict) -> str:
        """Provisions a new user from SCIM parameters."""
        if not user_email.strip():
            raise ValueError("SCIM user_email cannot be empty")
        
        user_key = f"{tenant_id}:{user_email}"
        user_id = f"usr-scim-{len(self._provisioned_users) + 1}"
        
        self._provisioned_users[user_key] = {
            "user_id": user_id,
            "tenant_id": tenant_id,
            "email": user_email,
            "scim_meta": raw_scim_payload
        }
        return user_id

    def deprovision_user(self, tenant_id: str, user_id: str) -> None:
        """De-provisions/deactivates a user account."""
        target_key = None
        for key, value in self._provisioned_users.items():
            if value["user_id"] == user_id and value["tenant_id"] == tenant_id:
                target_key = key
                break
        
        if not target_key:
            raise ValueError(f"SCIM user not found: {user_id}")
        
        del self._provisioned_users[target_key]
