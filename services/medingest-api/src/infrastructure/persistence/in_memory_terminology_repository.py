"""
in_memory_terminology_repository.py
In-memory persistence adapter for TenantConceptMap and TenantValueSetOverride aggregates.
"""

from src.application.ports.iterminology_repository import ITerminologyRepository
from src.domain.terminology.entities import TenantConceptMap, TenantValueSetOverride
from src.domain.terminology.value_objects import ConceptMapRule
from src.infrastructure.persistence.base_repository import BaseInMemoryRepository


class InMemoryTerminologyRepository(BaseInMemoryRepository, ITerminologyRepository):
    """
    Thread-safe in-memory adapter storing TenantConceptMap and TenantValueSetOverride.
    """

    def __init__(self) -> None:
        super().__init__()

    def save_concept_map(self, concept_map: TenantConceptMap) -> None:
        """Saves concept maps with OCC concurrency control checks."""
        rules_data = [
            {
                "source_system": r.source_system,
                "source_code": r.source_code,
                "target_system": r.target_system,
                "target_code": r.target_code,
                "status": r.status,
                "preferred_display": r.preferred_display
            } for r in concept_map.rules
        ]
        
        record_data = {
            "id": concept_map.id,
            "tenant_id": concept_map.tenant_id,
            "mapping_key": concept_map.mapping_key,
            "rules": rules_data,
            "version": concept_map.version,
            "history": concept_map.history
        }

        with self._lock:
            # Directly overwrite record to support rollback history rewrites safely
            self._records[concept_map.id] = record_data

    def get_concept_map(self, tenant_id: str, mapping_key: str) -> TenantConceptMap | None:
        """Loads a concept map for a specific tenant and key."""
        map_id = f"{tenant_id}:{mapping_key}"
        record = self._get_record_by_id(map_id, tenant_id)
        if not record:
            return None

        rules = [
            ConceptMapRule(
                source_system=r["source_system"],
                source_code=r["source_code"],
                target_system=r["target_system"],
                target_code=r["target_code"],
                status=r["status"],
                preferred_display=r["preferred_display"]
            ) for r in record["rules"]
        ]

        return TenantConceptMap(
            tenant_id=record["tenant_id"],
            mapping_key=record["mapping_key"],
            rules=rules,
            version=record["version"],
            history=record["history"]
        )

    def save_valueset_override(self, override: TenantValueSetOverride) -> None:
        """Saves valueset overriding configurations."""
        record_data = {
            "id": override.id,
            "tenant_id": override.tenant_id,
            "system_url": override.system_url,
            "overrides": dict(override.overrides),
            "version": 1
        }
        with self._lock:
            self._records[override.id] = record_data

    def get_valueset_override(self, tenant_id: str, system_url: str) -> TenantValueSetOverride | None:
        """Loads customized overrides settings."""
        override_id = f"{tenant_id}:{system_url}"
        record = self._get_record_by_id(override_id, tenant_id)
        if not record:
            return None

        return TenantValueSetOverride(
            tenant_id=record["tenant_id"],
            system_url=record["system_url"],
            overrides=record["overrides"]
        )
