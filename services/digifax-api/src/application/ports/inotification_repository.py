"""
inotification_repository.py
Outbound port repository interface for notification settings configuration and request logs.
"""

from abc import ABC, abstractmethod
from src.domain.notification.entities import TenantNotificationConfig, NotificationRequest


class INotificationRepository(ABC):
    """
    Interface for persistence of TenantNotificationConfigs and NotificationRequests logs.
    """

    @abstractmethod
    def save_config(self, config: TenantNotificationConfig) -> None:
        """Saves a tenant's notification templates and branding preferences."""
        pass

    @abstractmethod
    def get_config(self, tenant_id: str) -> TenantNotificationConfig | None:
        """Loads a tenant's notification templates and branding preferences."""
        pass

    @abstractmethod
    def save_request(self, req: NotificationRequest) -> None:
        """Saves a notification request dispatch log."""
        pass

    @abstractmethod
    def get_request(self, tenant_id: str, notification_id: str) -> NotificationRequest | None:
        """Loads a notification request dispatch log."""
        pass
