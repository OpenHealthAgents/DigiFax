from src.domain.common.value_object import ValueObject
from src.domain.ocr.value_objects import BoundingBox


class LayoutSection(ValueObject):
    """Represents a structural text block (e.g. Header, Paragraph) in reading order."""

    def __init__(
        self,
        text: str,
        header_level: int,  # 0 for plain text, 1-6 for headers
        page_number: int,
        reading_order_index: int,
        bounding_box: BoundingBox
    ):
        self.text = text
        self.header_level = header_level
        self.page_number = page_number
        self.reading_order_index = reading_order_index
        self.bounding_box = bounding_box


class LayoutTable(ValueObject):
    """Represents grid matrix data extracted from a document page."""

    def __init__(
        self,
        rows: list[list[str]],
        page_number: int,
        bounding_box: BoundingBox
    ):
        self.rows = rows
        self.page_number = page_number
        self.bounding_box = bounding_box


class LayoutKeyValuePair(ValueObject):
    """Represents key-value pairs parsed from forms or layout elements."""

    def __init__(
        self,
        key: str,
        value: str,
        key_bounding_box: BoundingBox,
        value_bounding_box: BoundingBox,
        confidence: float
    ):
        self.key = key
        self.value = value
        self.key_bounding_box = key_bounding_box
        self.value_bounding_box = value_bounding_box
        self.confidence = confidence


class LayoutHierarchyNode(ValueObject):
    """A node representing hierarchy trees of pages, headers, and child paragraphs."""

    def __init__(
        self,
        title: str,
        node_type: str,  # 'document', 'page', 'section', 'paragraph'
        bounding_box: BoundingBox | None,
        children: list['LayoutHierarchyNode'] | None = None
    ):
        self.title = title
        self.node_type = node_type
        self.bounding_box = bounding_box
        self.children = children or []


class NormalizedLayoutDocument(ValueObject):
    """Aggregates all parsed layout elements into a unified document structure."""

    def __init__(
        self,
        document_id: str,
        sections: list[LayoutSection],
        tables: list[LayoutTable],
        key_value_pairs: list[LayoutKeyValuePair],
        hierarchy_root: LayoutHierarchyNode,
        reading_order: list[str]
    ):
        self.document_id = document_id
        self.sections = sections
        self.tables = tables
        self.key_value_pairs = key_value_pairs
        self.hierarchy_root = hierarchy_root
        self.reading_order = reading_order
