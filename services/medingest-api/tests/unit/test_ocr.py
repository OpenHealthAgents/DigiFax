import sys
from unittest.mock import MagicMock, patch

# --- Pre-emptively mock all heavy OCR libraries in sys.modules with proper attributes ---

# Mock pytesseract
mock_pytesseract = MagicMock()
mock_pytesseract.Output = MagicMock()
mock_pytesseract.Output.DICT = "dict"
sys.modules["pytesseract"] = mock_pytesseract

# Mock paddleocr
mock_paddleocr_module = MagicMock()
sys.modules["paddleocr"] = mock_paddleocr_module

# Mock numpy
sys.modules["numpy"] = MagicMock()

# Mock ocrmypdf & pypdf
sys.modules["ocrmypdf"] = MagicMock()
mock_pypdf_module = MagicMock()
sys.modules["pypdf"] = mock_pypdf_module

# Mock surya
mock_surya_ocr = MagicMock()
sys.modules["surya"] = MagicMock()
sys.modules["surya.ocr"] = mock_surya_ocr
sys.modules["surya.model.detection.model"] = MagicMock()
sys.modules["surya.model.recognition.model"] = MagicMock()

# Mock doctr
mock_doctr_io = MagicMock()
mock_doctr_models = MagicMock()
sys.modules["doctr"] = MagicMock()
sys.modules["doctr.io"] = mock_doctr_io
sys.modules["doctr.models"] = mock_doctr_models

# --- Now import target modules ---
import pytest
from PIL import Image

from src.domain.common.exceptions import DomainException
from src.infrastructure.ocr.doctr_adapter import DocTrAdapter
from src.infrastructure.ocr.ocr_engine_factory import OcrEngineFactory
from src.infrastructure.ocr.ocrmypdf_adapter import OcrMyPdfAdapter
from src.infrastructure.ocr.paddleocr_adapter import PaddleOcrAdapter
from src.infrastructure.ocr.surya_adapter import SuryaOcrAdapter
from src.infrastructure.ocr.tesseract_adapter import TesseractAdapter

# --- 1. Factory Resolution Tests ---

def test_ocr_engine_factory_success() -> None:
    assert isinstance(OcrEngineFactory.create("tesseract"), TesseractAdapter)
    assert isinstance(OcrEngineFactory.create("PADDLEOCR"), PaddleOcrAdapter)
    assert isinstance(OcrEngineFactory.create("OcrMyPdf  "), OcrMyPdfAdapter)
    assert isinstance(OcrEngineFactory.create("surya"), SuryaOcrAdapter)
    assert isinstance(OcrEngineFactory.create("doctr"), DocTrAdapter)


def test_ocr_engine_factory_failure() -> None:
    with pytest.raises(DomainException) as exc_info:
        OcrEngineFactory.create("unknown_ocr")
    assert exc_info.value.code == "UNSUPPORTED_OCR_PROVIDER"


# --- 2. Tesseract Adapter Mock Mapping Test ---

@patch("PIL.Image.open")
def test_tesseract_adapter_mapping(mock_open: MagicMock) -> None:
    # Return a real PIL image with custom size to prevent decoding errors
    mock_open.return_value = Image.new("RGB", (1000, 2000))

    # Configure pytesseract mock response
    mock_pytesseract.image_to_data.return_value = {
        "text": ["", "Clinic", "Report"],
        "left": [0, 100, 200],
        "top": [0, 50, 150],
        "width": [0, 80, 120],
        "height": [0, 20, 30],
        "conf": [0, 90, 95]
    }

    adapter = TesseractAdapter()
    result = adapter.perform_ocr("doc-123", b"fake_bytes", "png")

    assert result.document_id == "doc-123"
    assert result.engine_name == "Tesseract"
    assert len(result.pages) == 1
    page = result.pages[0]

    assert len(page.words) == 2
    assert page.words[0].text == "Clinic"
    assert page.words[0].confidence == 0.90

    bbox = page.words[0].bounding_box
    assert bbox.x_min == 100 / 1000
    assert bbox.y_min == 50 / 2000
    assert bbox.x_max == 180 / 1000
    assert bbox.y_max == 70 / 2000


# --- 3. PaddleOCR Adapter Mock Mapping Test ---

@patch("PIL.Image.open")
def test_paddleocr_adapter_mapping(mock_open: MagicMock) -> None:
    mock_open.return_value = Image.new("RGB", (1000, 1000))

    # Configure PaddleOCR mock instance directly in sys.modules mock
    mock_ocr_instance = MagicMock()
    mock_ocr_instance.ocr.return_value = [[
        [[[100, 100], [200, 100], [200, 150], [100, 150]], ("TestPaddle", 0.94)]
    ]]
    mock_paddleocr_module.PaddleOCR.return_value = mock_ocr_instance

    adapter = PaddleOcrAdapter()
    result = adapter.perform_ocr("doc-123", b"fake_bytes", "png")

    assert result.engine_name == "PaddleOCR"
    assert len(result.pages) == 1
    page = result.pages[0]
    assert len(page.words) == 1
    assert page.words[0].text == "TestPaddle"
    assert page.words[0].confidence == 0.94
    assert page.words[0].bounding_box.x_min == 0.1
    assert page.words[0].bounding_box.y_min == 0.1


# --- 4. OCRmyPDF Adapter Mock Mapping Test ---

def test_ocrmypdf_adapter_mapping() -> None:
    # Configure PdfReader mock in sys.modules mock
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Searchable PDF Text"

    mock_reader_instance = MagicMock()
    mock_reader_instance.pages = [mock_page]
    mock_pypdf_module.PdfReader.return_value = mock_reader_instance

    adapter = OcrMyPdfAdapter()
    result = adapter.perform_ocr("doc-123", b"fake_pdf_bytes", "pdf")

    assert result.engine_name == "OCRmyPDF"
    assert len(result.pages) == 1
    page = result.pages[0]
    assert page.full_text == "Searchable PDF Text"
    assert len(page.words) == 3
    assert page.words[0].text == "Searchable"


# --- 5. Surya OCR Adapter Mock Mapping Test ---

@patch("PIL.Image.open")
def test_surya_adapter_mapping(mock_open: MagicMock) -> None:
    mock_open.return_value = Image.new("RGB", (1000, 1000))

    # Configure run_ocr mock in sys.modules mock
    mock_line = MagicMock()
    mock_line.bbox = [100, 200, 300, 400]
    mock_line.text = "SuryaLine"
    mock_line.confidence = 0.98

    mock_prediction = MagicMock()
    mock_prediction.text_lines = [mock_line]
    mock_surya_ocr.run_ocr.return_value = [mock_prediction]

    adapter = SuryaOcrAdapter()
    result = adapter.perform_ocr("doc-123", b"fake_bytes", "png")

    assert result.engine_name == "SuryaOCR"
    assert len(result.pages) == 1
    page = result.pages[0]
    assert len(page.words) == 1
    assert page.words[0].text == "SuryaLine"
    assert page.words[0].bounding_box.x_min == 0.1
    assert page.words[0].bounding_box.y_min == 0.2


# --- 6. DocTR Adapter Mock Mapping Test ---

def test_doctr_adapter_mapping() -> None:
    # Setup mock DocTR elements
    mock_word = MagicMock()
    mock_word.value = "DocTRWord"
    mock_word.confidence = 0.89
    mock_word.geometry = ((0.1, 0.1), (0.3, 0.2))

    mock_line = MagicMock()
    mock_line.words = [mock_word]

    mock_block = MagicMock()
    mock_block.lines = [mock_line]

    mock_page = MagicMock()
    mock_page.blocks = [mock_block]

    mock_result = MagicMock()
    mock_result.pages = [mock_page]

    mock_predictor_instance = MagicMock()
    mock_predictor_instance.return_value = mock_result

    # Configure doctr mock in sys.modules
    mock_doctr_models.ocr_predictor.return_value = mock_predictor_instance
    mock_doctr_io.DocumentFile.from_images.return_value = MagicMock()

    adapter = DocTrAdapter()
    result = adapter.perform_ocr("doc-123", b"fake_bytes", "png")

    assert result.engine_name == "DocTR"
    assert len(result.pages) == 1
    page = result.pages[0]
    assert len(page.words) == 1
    assert page.words[0].text == "DocTRWord"
    assert page.words[0].confidence == 0.89
    assert page.words[0].bounding_box.x_min == 0.1
    assert page.words[0].bounding_box.y_min == 0.1
