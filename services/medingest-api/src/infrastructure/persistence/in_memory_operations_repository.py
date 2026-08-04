"""
in_memory_operations_repository.py
In-memory persistence store storing PlatformOperationsConfig configurations.
"""

from src.application.ports.ioperations_repository import IOperationsRepository
from src.domain.operations.entities import PlatformOperationsConfig
from src.domain.operations.value_objects import HealthMetric
from src.infrastructure.persistence.base_repository import BaseInMemoryRepository


class InMemoryOperationsRepository(BaseInMemoryRepository, IOperationsRepository):
    """
    Thread-safe in-memory adapter storing platform settings.
    """

    def __init__(self) -> None:
        super().__init__()

    def save_config(self, config: PlatformOperationsConfig) -> None:
        """Saves operations config state."""
        metrics_data = {
            cname: {
                "component_name": m.component_name,
                "status": m.status,
                "latency_ms": m.latency_ms,
                "timestamp": m.timestamp
            } for cname, m in config.health_metrics.items()
        }
        record_data = {
            "id": f"ops:{config.tenant_id}",
            "tenant_id": config.tenant_id,
            "maintenance_mode_enabled": config.maintenance_mode_enabled,
            "active_feature_flags": dict(config.active_feature_flags),
            "health_metrics": metrics_data,
            "version": config.version
        }
        with self._lock:
            # Overwrite directly to allow thread-safe config updates
            self._records[record_data["id"]] = record_data

    def get_config(self, tenant_id: str) -> PlatformOperationsConfig | None:
        """Loads operations config state."""
        ops_key = f"ops:{tenant_id}"
        record = self._get_record_by_id(ops_key, tenant_id)
        if not record:
            return None

        metrics = {
            cname: HealthMetric(
                component_name=m["component_name"],
                status=m["status"],
                latency_ms=m["latency_ms"],
                timestamp=m["timestamp"]
            ) for cname, m in record["health_metrics"].items()
        }

        return PlatformOperationsConfig(
            tenant_id=record["tenant_id"],
            maintenance_mode_enabled=record["maintenance_mode_enabled"],
            active_feature_flags=record["active_feature_flags"],
            health_metrics=metrics,
            version=record["version"]
        )
