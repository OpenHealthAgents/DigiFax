"""
iuser_provisioning_service.py
Outbound port interface abstracting programmatic SCIM user provisioning.
"""

import abc


class IUserProvisioningService(abc.ABC):
    """
    Outbound port interface defining SCIM user directory synchronization rules.

    Why It Exists:
        Allows enterprise client directories (Active Directory) to provision,
        update, and de-provision users programmatically.
    """

    @abc.abstractmethod
    def provision_user(self, tenant_id: str, user_email: str, raw_scim_payload: dict) -> str:
        """Provisions a new user from SCIM parameters."""
        pass

    @abc.abstractmethod
    def deprovision_user(self, tenant_id: str, user_id: str) -> None:
        """De-provisions/deactivates a user account."""
        pass
