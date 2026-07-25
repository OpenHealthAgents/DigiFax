
from src.domain.common.value_object import ValueObject


class TerminologyMapping(ValueObject):
    """Holds a mapped terminology code, display name, coding system, and confidence."""

    def __init__(self, code: str, display: str, system: str, confidence_score: float):
        self.code = code
        self.display = display
        self.system = system  # e.g., LOINC, UCUM, SNOMED_CT, ICD_10, RXNORM
        self.confidence_score = confidence_score


class TerminologyMapResult(ValueObject):
    """Container for the primary mapping and alternative matching candidate mappings."""

    def __init__(
        self,
        primary_mapping: TerminologyMapping,
        alternative_mappings: list[TerminologyMapping]
    ):
        self.primary_mapping = primary_mapping
        self.alternative_mappings = alternative_mappings
