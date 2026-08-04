import sys
from unittest.mock import MagicMock, patch

# --- Pre-emptively mock all document understanding packages in sys.modules ---

mock_docling_converter = MagicMock()
sys.modules["docling"] = MagicMock()
sys.modules["docling.document_converter"] = mock_docling_converter

mock_layoutparser = MagicMock()
sys.modules["layoutparser"] = mock_layoutparser

mock_marker_convert = MagicMock()
mock_marker_models = MagicMock()
sys.modules["marker"] = MagicMock()
sys.modules["marker.convert"] = mock_marker_convert
sys.modules["marker.models"] = mock_marker_models

mock_unstructured_pdf = MagicMock()
sys.modules["unstructured"] = MagicMock()
sys.modules["unstructured.partition"] = MagicMock()
sys.modules["unstructured.partition.pdf"] = mock_unstructured_pdf

mock_fitz = MagicMock()
sys.modules["fitz"] = mock_fitz

# --- Import remaining modules ---
import pytest
from PIL import Image

from src.domain.common.exceptions import DomainException
from src.infrastructure.extraction.docling_adapter import DoclingAdapter
from src.infrastructure.extraction.layout_engine_factory import LayoutEngineFactory
from src.infrastructure.extraction.layoutparser_adapter import LayoutParserAdapter
from src.infrastructure.extraction.marker_adapter import MarkerAdapter
from src.infrastructure.extraction.pymupdf_adapter import PyMuPdfAdapter
from src.infrastructure.extraction.unstructured_adapter import UnstructuredAdapter

# --- 1. Factory Resolution Tests ---

def test_layout_engine_factory_success() -> None:
    assert isinstance(LayoutEngineFactory.create("docling"), DoclingAdapter)
    assert isinstance(LayoutEngineFactory.create("LAYOUTPARSER"), LayoutParserAdapter)
    assert isinstance(LayoutEngineFactory.create("marker"), MarkerAdapter)
    assert isinstance(LayoutEngineFactory.create("Unstructured  "), UnstructuredAdapter)
    assert isinstance(LayoutEngineFactory.create("pymupdf"), PyMuPdfAdapter)


def test_layout_engine_factory_failure() -> None:
    with pytest.raises(DomainException) as exc_info:
        LayoutEngineFactory.create("unknown_layout_parser")
    assert exc_info.value.code == "UNSUPPORTED_LAYOUT_PROVIDER"


# --- 2. Docling Adapter Mapping Test ---

def test_docling_adapter_mapping() -> None:
    # Setup mock docling output
    mock_cell = MagicMock()
    mock_cell.text = "CellText"

    mock_row = MagicMock()
    mock_row.cells = [mock_cell]

    mock_table_el = MagicMock()
    mock_table_el.rows = [mock_row]

    mock_heading_el = MagicMock()
    mock_heading_el.text = "DoclingHeading"
    mock_heading_el.label = "heading"
    del mock_heading_el.rows

    mock_legacy_doc = MagicMock()
    mock_legacy_doc.elements = [mock_heading_el, mock_table_el]

    mock_conv_result = MagicMock()
    mock_conv_result.legacy_document = mock_legacy_doc

    mock_converter_instance = MagicMock()
    mock_converter_instance.convert_stream.return_value = mock_conv_result
    mock_docling_converter.DocumentConverter.return_value = mock_converter_instance

    adapter = DoclingAdapter()
    result = adapter.parse_layout("doc-123", b"fake_bytes", "pdf")

    assert result.document_id == "doc-123"
    assert len(result.sections) == 1
    assert result.sections[0].text == "DoclingHeading"
    assert result.sections[0].header_level == 1

    assert len(result.tables) == 1
    assert result.tables[0].rows == [["CellText"]]
    assert result.reading_order == ["section_0", "table_0"]


# --- 3. LayoutParser Adapter Mapping Test ---

@patch("PIL.Image.open")
def test_layoutparser_adapter_mapping(mock_open: MagicMock) -> None:
    mock_open.return_value = Image.new("RGB", (1000, 1000))

    mock_block1 = MagicMock()
    mock_block1.coordinates = [100, 200, 300, 400]
    mock_block1.type = "Title"
    mock_block1.text = "TitleText"

    mock_block2 = MagicMock()
    mock_block2.coordinates = [100, 500, 800, 900]
    mock_block2.type = "Table"

    mock_model_instance = MagicMock()
    mock_model_instance.detect.return_value = [mock_block1, mock_block2]
    mock_layoutparser.DetectronLayoutModel.return_value = mock_model_instance

    # Mock sys.modules numpy
    sys.modules["numpy"] = MagicMock()

    adapter = LayoutParserAdapter()
    result = adapter.parse_layout("doc-123", b"fake_bytes", "png")

    assert len(result.sections) == 1
    assert result.sections[0].text == "TitleText"
    assert result.sections[0].header_level == 1

    assert len(result.tables) == 1
    assert result.reading_order == ["section_0", "table_0"]


# --- 4. Marker Adapter Mapping Test ---

def test_marker_adapter_mapping() -> None:
    mock_marker_models.load_all_models.return_value = []
    mock_marker_convert.convert_single_pdf.return_value = ("# HeaderTitle\n\nSome Paragraph text", None, {})

    adapter = MarkerAdapter()
    result = adapter.parse_layout("doc-123", b"fake_bytes", "pdf")

    assert len(result.sections) == 2
    assert result.sections[0].text == "HeaderTitle"
    assert result.sections[0].header_level == 1
    assert result.sections[1].text == "Some Paragraph text"
    assert result.sections[1].header_level == 0


# --- 5. Unstructured Adapter Mapping Test ---

def test_unstructured_adapter_mapping() -> None:
    mock_el1 = MagicMock()
    mock_el1.category = "Title"
    mock_el1.text = "UnstructuredTitle"

    mock_el2 = MagicMock()
    mock_el2.category = "Table"
    mock_el2.text = "UnstructuredGrid"

    mock_unstructured_pdf.partition_pdf.return_value = [mock_el1, mock_el2]

    adapter = UnstructuredAdapter()
    result = adapter.parse_layout("doc-123", b"fake_bytes", "pdf")

    assert len(result.sections) == 1
    assert result.sections[0].text == "UnstructuredTitle"
    assert result.sections[0].header_level == 1

    assert len(result.tables) == 1
    assert result.tables[0].rows == [["UnstructuredGrid"]]


# --- 6. PyMuPDF Adapter Mapping Test ---

def test_pymupdf_adapter_mapping() -> None:
    # Set up mock block coordinates: x0, y0, x1, y1, text, block_no, block_type
    mock_block1 = (100, 100, 500, 150, "HEADING TITLE", 0, 0)
    mock_block2 = (100, 200, 500, 300, "paragraph body text", 1, 0)

    mock_page = MagicMock()
    mock_page.rect.width = 1000
    mock_page.rect.height = 1000
    mock_page.get_text.return_value = [mock_block2, mock_block1]  # out of reading order

    mock_doc_instance = MagicMock()
    mock_doc_instance.__iter__.return_value = [mock_page]
    mock_fitz.open.return_value = mock_doc_instance

    adapter = PyMuPdfAdapter()
    result = adapter.parse_layout("doc-123", b"fake_bytes", "pdf")

    assert len(result.sections) == 2
    # Verify sorting by vertical coordinate (mock_block1 has y0=100, mock_block2 has y0=200)
    assert result.sections[0].text == "HEADING TITLE"
    assert result.sections[0].header_level == 1  # Estimated as header because of uppercase
    assert result.sections[1].text == "paragraph body text"
    assert result.sections[1].header_level == 0
