import abc

from src.domain.terminology.value_objects import TerminologyMapResult


class ITerminologyService(abc.ABC):
    """Outbound port interface defining terminology mapping and normalization."""

    @abc.abstractmethod
    def resolve_code(
        self,
        analyte_name: str,
        specimen: str | None = None,
        unit: str | None = None
    ) -> TerminologyMapResult:
        """Translates laboratory analyte, specimen, and unit to coding systems.

        Args:
            analyte_name: Raw analyte text (e.g. 'Fasting Glucose').
            specimen: Specimen type (e.g. 'Blood', 'Urine').
            unit: Lab unit of measure (e.g. 'mg/dL').

        Returns:
            The TerminologyMapResult detailing primary and alternative codes.
        """
        pass
