"""
propose_local_mapping.py
Use Case managing proposals of local-to-standard clinical terminology mappings.
"""

from src.application.ports.iterminology_repository import ITerminologyRepository
from src.domain.terminology.entities import TenantConceptMap


class ProposeLocalMappingUseCase:
    """
    Inbound Use Case proposing local clinic mappings for LOINC/SNOMED codes.
    """

    def __init__(self, repo: ITerminologyRepository):
        self.repo = repo

    def execute(
        self,
        tenant_id: str,
        mapping_key: str,
        source_system: str,
        source_code: str,
        target_system: str,
        target_code: str,
        preferred_display: str | None = None
    ) -> TenantConceptMap:
        """
        Appends or updates proposed mapping rules.
        """
        concept_map = self.repo.get_concept_map(tenant_id, mapping_key)
        if not concept_map:
            concept_map = TenantConceptMap(tenant_id=tenant_id, mapping_key=mapping_key)
            
        concept_map.propose_rule(
            source_system=source_system,
            source_code=source_code,
            target_system=target_system,
            target_code=target_code,
            preferred_display=preferred_display
        )

        self.repo.save_concept_map(concept_map)
        return concept_map
