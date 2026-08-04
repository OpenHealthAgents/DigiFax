"""
update_platform_health.py
Use case logging subsystem health parameters and modifying feature flags.
"""

from datetime import datetime
from src.application.ports.ioperations_repository import IOperationsRepository
from src.domain.operations.entities import PlatformOperationsConfig
from src.domain.operations.value_objects import HealthMetric


class UpdatePlatformHealthUseCase:
    """
    Usecase writing components latency metrics and updating active flags.
    """

    def __init__(self, repo: IOperationsRepository) -> None:
        self.repo = repo

    def execute_health_metric(
        self,
        tenant_id: str,
        component_name: str,
        status: str,
        latency_ms: float
    ) -> PlatformOperationsConfig:
        """Appends a components status check entry."""
        config = self.repo.get_config(tenant_id)
        if not config:
            config = PlatformOperationsConfig(tenant_id=tenant_id)

        metric = HealthMetric(
            component_name=component_name,
            status=status,
            latency_ms=latency_ms,
            timestamp=datetime.now().isoformat()
        )
        config.record_health_metric(metric)
        self.repo.save_config(config)
        return config

    def execute_feature_flag(
        self,
        tenant_id: str,
        flag_name: str,
        enabled: bool
    ) -> PlatformOperationsConfig:
        """Modifies flag toggle status."""
        config = self.repo.get_config(tenant_id)
        if not config:
            config = PlatformOperationsConfig(tenant_id=tenant_id)

        config.set_feature_flag(flag_name, enabled)
        self.repo.save_config(config)
        return config
