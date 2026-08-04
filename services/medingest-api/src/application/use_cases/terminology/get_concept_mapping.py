"""
get_concept_mapping.py
Use Case resolving local-to-standard clinical mappings with overrides.
"""

from src.application.ports.iterminology_repository import ITerminologyRepository
from src.domain.terminology.value_objects import FHIRCoding


class GetConceptMappingUseCase:
    """
    Inbound Use Case translating concept codes to standard FHIRCoding references.
    """

    def __init__(self, repo: ITerminologyRepository):
        self.repo = repo

    def execute(
        self,
        tenant_id: str,
        mapping_key: str,
        source_system: str,
        source_code: str
    ) -> FHIRCoding | None:
        """
        Translates a local code to standard code, applying tenant overrides if present.
        """
        concept_map = self.repo.get_concept_map(tenant_id, mapping_key)
        if not concept_map:
            return None

        # Find approved mapping rule
        active_rule = None
        for rule in concept_map.rules:
            if (rule.source_system == source_system 
                    and rule.source_code == source_code 
                    and rule.status == "APPROVED"):
                active_rule = rule
                break

        if not active_rule:
            return None

        # Resolve display (checking value set override mappings first)
        display = active_rule.preferred_display or f"Concept {active_rule.target_code}"
        override = self.repo.get_valueset_override(tenant_id, active_rule.target_system)
        if override and active_rule.target_code in override.overrides:
            display = override.overrides[active_rule.target_code]

        return FHIRCoding(
            system=active_rule.target_system,
            code=active_rule.target_code,
            display=display
        )
