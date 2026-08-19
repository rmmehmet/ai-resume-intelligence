"""
Text extraction from resume files.

Handles the mechanics of getting plain text out of a PDF or DOCX
file. Does not attempt to understand or structure that text - see
services/resume/structurer.py for that.
"""
from io import BytesIO

from docx import Document
from pypdf import PdfReader


class TextExtractionError(Exception):
    """Raised when text could not be extracted from a file."""


def extract_text(content: bytes, extension: str) -> str:
    """Extract plain text from PDF or DOCX file content."""
    try:
        if extension == "pdf":
            return _extract_pdf_text(content)
        if extension == "docx":
            return _extract_docx_text(content)
    except Exception as exc:  # noqa: BLE001 - normalize all parser errors
        raise TextExtractionError(f"Failed to extract text from .{extension} file: {exc}") from exc

    raise TextExtractionError(f"Unsupported extension for text extraction: {extension}")


def _extract_pdf_text(content: bytes) -> str:
    reader = PdfReader(BytesIO(content))
    pages_text = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages_text).strip()


def _extract_docx_text(content: bytes) -> str:
    document = Document(BytesIO(content))
    paragraphs = [p.text for p in document.paragraphs if p.text.strip()]
    return "\n".join(paragraphs).strip()