"""
entities.py
Domain Entities representing PlatformOperationsConfig aggregate roots.
"""

from src.domain.common.entity import Entity
from src.domain.operations.value_objects import HealthMetric


class PlatformOperationsConfig(Entity):
    """
    Aggregate Root containing global settings locks, feature flags, and health check cache registries.
    """

    def __init__(
        self,
        tenant_id: str,
        maintenance_mode_enabled: bool = False,
        active_feature_flags: dict[str, bool] = None,
        health_metrics: dict[str, HealthMetric] = None,
        version: int = 1
    ):
        super().__init__(id=tenant_id)
        self.tenant_id = tenant_id
        self.maintenance_mode_enabled = maintenance_mode_enabled
        self.active_feature_flags = active_feature_flags or {
            "AUTO_INGEST": True,
            "LLM_VALIDATION": False,
            "TERM_ROLLBACK": True
        }
        self.health_metrics = health_metrics or {}
        self.version = version

    def toggle_maintenance(self, enabled: bool) -> None:
        """Enables/Disables global system lock modes."""
        self.maintenance_mode_enabled = enabled

    def set_feature_flag(self, flag: str, enabled: bool) -> None:
        """Adds or modifies feature flag availability registers."""
        self.active_feature_flags[flag] = enabled

    def record_health_metric(self, metric: HealthMetric) -> None:
        """Records latency metrics statistics for a component."""
        self.health_metrics[metric.component_name] = metric
