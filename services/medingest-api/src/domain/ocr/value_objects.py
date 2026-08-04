
from src.domain.common.value_object import ValueObject


class BoundingBox(ValueObject):
    """Normalized coordinates defining boundaries of a word or table in layout."""

    def __init__(self, x_min: float, y_min: float, x_max: float, y_max: float):
        self.x_min = x_min
        self.y_min = y_min
        self.x_max = x_max
        self.y_max = y_max


class OcrWord(ValueObject):
    """A single recognized word token, its position, and confidence score."""

    def __init__(self, text: str, bounding_box: BoundingBox, confidence: float):
        self.text = text
        self.bounding_box = bounding_box
        self.confidence = confidence


class OcrTable(ValueObject):
    """Tabular grid structure identified on the page."""

    def __init__(self, rows: list[list[str]], bounding_box: BoundingBox):
        self.rows = rows
        self.bounding_box = bounding_box


class OcrPage(ValueObject):
    """Extracted content, layout elements, and metadata for a single document page."""

    def __init__(
        self,
        page_number: int,
        words: list[OcrWord],
        full_text: str,
        tables: list[OcrTable],
        metadata: dict[str, str]
    ):
        self.page_number = page_number
        self.words = words
        self.full_text = full_text
        self.tables = tables
        self.metadata = metadata


class OcrResult(ValueObject):
    """The unified document representation returned by all OCR adapters."""

    def __init__(
        self,
        document_id: str,
        pages: list[OcrPage],
        engine_name: str,
        execution_time_seconds: float
    ):
        self.document_id = document_id
        self.pages = pages
        self.engine_name = engine_name
        self.execution_time_seconds = execution_time_seconds
