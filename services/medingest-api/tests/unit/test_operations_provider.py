"""
test_operations_provider.py
Unit and controller integration tests asserting maintenance switches, flag changes, and health checks updates.
"""

import pytest
from fastapi.testclient import TestClient

from src.domain.operations.value_objects import HealthMetric
from src.domain.operations.entities import PlatformOperationsConfig
from src.application.use_cases.operations.toggle_maintenance_mode import ToggleMaintenanceModeUseCase
from src.application.use_cases.operations.update_platform_health import UpdatePlatformHealthUseCase
from src.infrastructure.persistence.in_memory_operations_repository import InMemoryOperationsRepository
from src.main import app


def test_operations_value_object_validations() -> None:
    # 1. Unsupported health component status
    with pytest.raises(ValueError):
        HealthMetric("DATABASE", "CRITICAL", 120.0, "2026-07-30")

    # 2. Unsupported health component name
    with pytest.raises(ValueError):
        HealthMetric("PRACTITIONERS", "HEALTHY", 10.0, "2026-07-30")

    # 3. Negative latency value
    with pytest.raises(ValueError):
        HealthMetric("AI_PROVIDER", "HEALTHY", -5.5, "2026-07-30")


def test_operations_toggles_and_health_accruals() -> None:
    repo = InMemoryOperationsRepository()
    toggle_use_case = ToggleMaintenanceModeUseCase(repo)
    update_use_case = UpdatePlatformHealthUseCase(repo)

    tenant_id = "tenant-ops-test"

    # 1. Toggle Maintenance mode
    config = toggle_use_case.execute(tenant_id, True)
    assert config.maintenance_mode_enabled is True

    # 2. Record subsystem health checks
    config = update_use_case.execute_health_metric(tenant_id, "DATABASE", "HEALTHY", 14.5)
    assert config.health_metrics["DATABASE"].latency_ms == 14.5
    assert config.health_metrics["DATABASE"].status == "HEALTHY"

    # 3. Modify active feature flags
    config = update_use_case.execute_feature_flag(tenant_id, "LLM_VALIDATION", True)
    assert config.active_feature_flags["LLM_VALIDATION"] is True


def test_operations_http_endpoints() -> None:
    client = TestClient(app)

    # 1. Toggle Maintenance endpoint
    maint_res = client.post(
        "/api/operations/maintenance",
        headers={"X-Tenant-Id": "tenant-ops-http"},
        json={"enabled": True}
    )
    assert maint_res.status_code == 200
    assert maint_res.json()["maintenance_mode_enabled"] is True

    # 2. Update health endpoint
    health_res = client.post(
        "/api/operations/health",
        headers={"X-Tenant-Id": "tenant-ops-http"},
        json={"component_name": "AI_PROVIDER", "status": "DEGRADED", "latency_ms": 950.0}
    )
    assert health_res.status_code == 200
    assert health_res.json()["health_metrics"]["AI_PROVIDER"]["status"] == "DEGRADED"

    # 3. Update feature flag endpoint
    flag_res = client.post(
        "/api/operations/flag",
        headers={"X-Tenant-Id": "tenant-ops-http"},
        json={"flag_name": "AUTO_INGEST", "enabled": False}
    )
    assert flag_res.status_code == 200
    assert flag_res.json()["active_feature_flags"]["AUTO_INGEST"] is False

    # 4. Get Status endpoint
    status_res = client.get(
        "/api/operations/status",
        headers={"X-Tenant-Id": "tenant-ops-http"}
    )
    assert status_res.status_code == 200
    assert status_res.json()["maintenance_mode_enabled"] is True
    assert status_res.json()["active_feature_flags"]["AUTO_INGEST"] is False
    assert status_res.json()["health_metrics"]["AI_PROVIDER"]["latency_ms"] == 950.0
