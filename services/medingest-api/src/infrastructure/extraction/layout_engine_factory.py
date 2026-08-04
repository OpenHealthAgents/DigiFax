from src.application.ports.ilayout_parser_engine import ILayoutParserEngine
from src.domain.common.exceptions import DomainException
from src.infrastructure.extraction.docling_adapter import DoclingAdapter
from src.infrastructure.extraction.layoutparser_adapter import LayoutParserAdapter
from src.infrastructure.extraction.marker_adapter import MarkerAdapter
from src.infrastructure.extraction.pymupdf_adapter import PyMuPdfAdapter
from src.infrastructure.extraction.unstructured_adapter import UnstructuredAdapter


class LayoutEngineFactory:
    """Factory creating ILayoutParserEngine adapters based on configuration strings."""

    _PROVIDERS = {
        "docling": DoclingAdapter,
        "layoutparser": LayoutParserAdapter,
        "marker": MarkerAdapter,
        "unstructured": UnstructuredAdapter,
        "pymupdf": PyMuPdfAdapter
    }

    @classmethod
    def create(cls, provider_name: str) -> ILayoutParserEngine:
        """Instantiates the requested layout understanding engine adapter.

        Args:
            provider_name: The case-insensitive name of the engine (e.g. 'docling').

        Returns:
            The resolved ILayoutParserEngine adapter instance.

        Raises:
            DomainException if the provider name is unknown.
        """
        name = provider_name.strip().lower()
        adapter_cls = cls._PROVIDERS.get(name)
        if not adapter_cls:
            allowed = ", ".join(cls._PROVIDERS.keys())
            raise DomainException(
                message=f"Unsupported layout provider: {provider_name}. Supported providers are: {allowed}.",
                code="UNSUPPORTED_LAYOUT_PROVIDER"
            )
        return adapter_cls()  # type: ignore[abstract]
