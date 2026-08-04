"""
rollback_concept_map.py
Use Case rolling back mapping rules list back to target version index.
"""

from src.application.ports.iterminology_repository import ITerminologyRepository
from src.domain.terminology.entities import TenantConceptMap


class RollbackConceptMapUseCase:
    """
    Inbound Use Case reverting TenantConceptMap versions.
    """

    def __init__(self, repo: ITerminologyRepository):
        self.repo = repo

    def execute(
        self,
        tenant_id: str,
        mapping_key: str,
        target_version: int
    ) -> TenantConceptMap:
        """
        Loads the ConceptMap aggregate, executes state rollback, and saves.
        """
        concept_map = self.repo.get_concept_map(tenant_id, mapping_key)
        if not concept_map:
            raise ValueError("Target concept map not found")

        concept_map.rollback_to_version(target_version)
        self.repo.save_concept_map(concept_map)
        return concept_map
