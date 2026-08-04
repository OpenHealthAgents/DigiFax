"""
toggle_maintenance_mode.py
Use case toggling maintenance mode states.
"""

from src.application.ports.ioperations_repository import IOperationsRepository
from src.domain.operations.entities import PlatformOperationsConfig


class ToggleMaintenanceModeUseCase:
    """
    Usecase switching global system lock levels.
    """

    def __init__(self, repo: IOperationsRepository) -> None:
        self.repo = repo

    def execute(self, tenant_id: str, enabled: bool) -> PlatformOperationsConfig:
        """Sets the system maintenance toggle and commits the setting."""
        config = self.repo.get_config(tenant_id)
        if not config:
            config = PlatformOperationsConfig(tenant_id=tenant_id)

        config.toggle_maintenance(enabled)
        self.repo.save_config(config)
        return config
