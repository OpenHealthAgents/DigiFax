import abc

from src.domain.extraction.layout import NormalizedLayoutDocument
from src.domain.extraction.schemas import StructuredClinicalReport


class IAiExtractor(abc.ABC):
    """Outbound port interface defining structured clinical variables extraction."""

    @abc.abstractmethod
    def extract_clinical_data(
        self,
        layout_document: NormalizedLayoutDocument,
        target_model: str | None = None
    ) -> StructuredClinicalReport:
        """Executes LLM-based structured extraction from parsed layout document.

        Args:
            layout_document: The parsed document structure including sections/tables.
            target_model: Optional specific model endpoint override to call.

        Returns:
            The parsed and validated StructuredClinicalReport Pydantic model.
        """
        pass
