"""
approve_concept_mapping.py
Use Case approving proposed terminology mapping rules.
"""

from src.application.ports.iterminology_repository import ITerminologyRepository
from src.domain.terminology.entities import TenantConceptMap


class ApproveConceptMappingUseCase:
    """
    Inbound Use Case approving local terminology mappings.
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
        target_code: str
    ) -> TenantConceptMap:
        """
        Loads the ConceptMap aggregate, transitions target rule status, and saves.
        """
        concept_map = self.repo.get_concept_map(tenant_id, mapping_key)
        if not concept_map:
            raise ValueError("Target concept map not found")

        concept_map.approve_rule(
            source_system=source_system,
            source_code=source_code,
            target_system=target_system,
            target_code=target_code
        )

        self.repo.save_concept_map(concept_map)
        return concept_map
