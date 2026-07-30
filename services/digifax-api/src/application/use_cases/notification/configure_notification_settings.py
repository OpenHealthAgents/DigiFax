"""
configure_notification_settings.py
Use case configuring tenant notification settings templates and branding elements.
"""

from src.application.ports.inotification_repository import INotificationRepository
from src.domain.notification.entities import TenantNotificationConfig
from src.domain.notification.value_objects import NotificationTemplate


class ConfigureNotificationSettingsUseCase:
    """
    Usecase registering notification branding configurations.
    """

    def __init__(self, repo: INotificationRepository) -> None:
        self.repo = repo

    def execute(
        self,
        tenant_id: str,
        templates: list[dict],
        branding_header: str,
        branding_footer: str
    ) -> TenantNotificationConfig:
        """Saves a tenant's notification configurations preferences."""
        config = self.repo.get_config(tenant_id)
        if not config:
            config = TenantNotificationConfig(tenant_id=tenant_id)

        config.configure_branding(header=branding_header, footer=branding_footer)

        # Register template configurations
        for t in templates:
            config.register_template(
                NotificationTemplate(
                    template_id=t["template_id"],
                    subject_template=t.get("subject_template", ""),
                    body_template=t["body_template"]
                )
            )

        self.repo.save_config(config)
        return config
class NotificationDispatchException(Exception):
    """Exception raised when notification dispatch fails."""
    pass
