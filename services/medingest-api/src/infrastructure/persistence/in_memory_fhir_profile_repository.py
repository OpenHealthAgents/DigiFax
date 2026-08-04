"""
in_memory_fhir_profile_repository.py
In-memory persistence adapter for TenantFHIRProfileConfiguration and FHIRStructureDefinition.
"""

from src.application.ports.ifhir_profile_repository import IFHIRProfileRepository
from src.domain.fhir_profile.entities import TenantFHIRProfileConfiguration, FHIRStructureDefinition
from src.infrastructure.persistence.base_repository import BaseInMemoryRepository


class InMemoryFHIRProfileRepository(BaseInMemoryRepository, IFHIRProfileRepository):
    """
    Thread-safe in-memory adapter storing configuration settings and StructureDefinitions profiles.
    """

    def __init__(self) -> None:
        super().__init__()
        # Pre-seed standard global StructureDefinitions for US Core and IPS
        self._seed_default_profiles()

    def _seed_default_profiles(self) -> None:
        """Seeds default standard US Core and International Patient Summary (IPS) StructureDefinitions."""
        defaults = [
            FHIRStructureDefinition(
                url="http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient",
                resource_type="Patient",
                required_paths=["name", "identifier", "gender"]
            ),
            FHIRStructureDefinition(
                url="http://hl7.org/fhir/us/core/StructureDefinition/us-core-observationlab",
                resource_type="Observation",
                required_paths=["status", "code", "subject", "valueQuantity"]
            ),
            FHIRStructureDefinition(
                url="http://hl7.org/fhir/uv/ips/StructureDefinition/Patient-uv-ips",
                resource_type="Patient",
                required_paths=["name", "gender"]
            ),
            FHIRStructureDefinition(
                url="http://hl7.org/fhir/uv/ips/StructureDefinition/AllergyIntolerance-uv-ips",
                resource_type="AllergyIntolerance",
                required_paths=["clinicalStatus", "verificationStatus", "patient", "code"]
            )
        ]
        for sd in defaults:
            self.save_structure_definition(sd)

    def save_configuration(self, config: TenantFHIRProfileConfiguration) -> None:
        """Saves configuration settings for a tenant."""
        record_data = {
            "id": config.tenant_id,
            "tenant_id": config.tenant_id,
            "active_igs": list(config.active_igs),
            "custom_profiles": list(config.custom_profiles),
            "version": config.version
        }
        with self._lock:
            # Overwrite directly to allow thread-safe config updates
            self._records[config.tenant_id] = record_data

    def get_configuration(self, tenant_id: str) -> TenantFHIRProfileConfiguration | None:
        """Loads configuration settings for a tenant."""
        record = self._get_record_by_id(tenant_id, tenant_id)
        if not record:
            return None

        return TenantFHIRProfileConfiguration(
            tenant_id=record["tenant_id"],
            active_igs=record["active_igs"],
            custom_profiles=record["custom_profiles"],
            version=record["version"]
        )

    def save_structure_definition(self, sd: FHIRStructureDefinition) -> None:
        """Saves a StructureDefinition constraints profile."""
        record_data = {
            "id": sd.id,
            "url": sd.url,
            "resource_type": sd.resource_type,
            "tenant_id": sd.tenant_id,
            "required_paths": list(sd.required_paths),
            "version": sd.version
        }
        with self._lock:
            self._records[sd.id] = record_data

    def get_structure_definitions(self, tenant_id: str | None = None) -> list[FHIRStructureDefinition]:
        """Lists StructureDefinitions active for the system or a specific tenant."""
        with self._lock:
            results = []
            for r in self._records.values():
                # Filter StructureDefinition records
                if "url" in r and r.get("tenant_id") == tenant_id:
                    results.append(
                        FHIRStructureDefinition(
                            url=r["url"],
                            resource_type=r["resource_type"],
                            tenant_id=r["tenant_id"],
                            required_paths=r["required_paths"],
                            version=r["version"]
                        )
                    )
            return results

    def get_structure_definition_by_url(
        self,
        url: str,
        tenant_id: str | None = None
    ) -> FHIRStructureDefinition | None:
        """Finds a StructureDefinition matching a canonical URL profile."""
        with self._lock:
            target_id = f"{tenant_id or 'global'}:{url}"
            r = self._records.get(target_id)
            if not r:
                return None

            return FHIRStructureDefinition(
                url=r["url"],
                resource_type=r["resource_type"],
                tenant_id=r["tenant_id"],
                required_paths=r["required_paths"],
                version=r["version"]
            )
