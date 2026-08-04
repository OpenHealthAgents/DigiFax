import abc

from src.domain.extraction.layout import NormalizedLayoutDocument


class ILayoutParserEngine(abc.ABC):
    """Outbound port interface defining structured layout parsing services."""

    @abc.abstractmethod
    def parse_layout(
        self,
        document_id: str,
        document_bytes: bytes,
        file_extension: str
    ) -> NormalizedLayoutDocument:
        """Parses document bytes to return layout structures, grids, and order.

        Args:
            document_id: Unique string identifying the extraction session.
            document_bytes: Raw binary file payload to parse.
            file_extension: Extension format (e.g. "pdf", "tiff").

        Returns:
            The NormalizedLayoutDocument value object detailing layout elements.
        """
        pass
