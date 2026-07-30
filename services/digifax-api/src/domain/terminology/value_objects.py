"""
value_objects.py
Domain Value Objects representing FHIR codings, terminology mappings, and local-to-standard mapping rules.
"""

from dataclasses import dataclass, field
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


@dataclass(frozen=True)
class FHIRCoding(ValueObject):
    """Immutable FHIR Coding representation."""
    system: str
    code: str
    display: str

    def __post_init__(self) -> None:
        if not self.system.strip():
            raise ValueError("FHIR System URI cannot be empty")
        if not self.code.strip():
            raise ValueError("FHIR Code cannot be empty")


@dataclass(frozen=True)
class ConceptMapRule(ValueObject):
    """Immutable mapping mapping local clinic codes to standard clinical terminology."""
    source_system: str
    source_code: str
    target_system: str
    target_code: str
    status: str = "PENDING_APPROVAL"  # PENDING_APPROVAL, APPROVED, REJECTED
    preferred_display: str | None = None

    def __post_init__(self) -> None:
        if not self.source_system.strip():
            raise ValueError("Source system cannot be empty")
        if not self.source_code.strip():
            raise ValueError("Source code cannot be empty")
        if not self.target_system.strip():
            raise ValueError("Target system cannot be empty")
        if not self.target_code.strip():
            raise ValueError("Target code cannot be empty")
        if self.status not in ("PENDING_APPROVAL", "APPROVED", "REJECTED"):
            raise ValueError("Invalid rule approval status")
