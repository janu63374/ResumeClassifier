
import pymupdf
from docx import Document
from pathlib import Path


def extract_pdf_text(file_path: str) -> str:
    """Extract text from a PDF resume."""

    extracted_text = []

    try:
        with pymupdf.open(file_path) as pdf:
            for page in pdf:
                text = page.get_text()
                if text.strip():
                    extracted_text.append(text)

        return "\n".join(extracted_text).strip()

    except Exception as error:
        raise ValueError(f"PDF extraction failed: {error}")


def extract_docx_text(file_path: str) -> str:
    """Extract text from a DOCX resume."""

    try:
        document = Document(file_path)

        extracted_text = []

        # Extract paragraphs
        for paragraph in document.paragraphs:
            if paragraph.text.strip():
                extracted_text.append(paragraph.text)

        # Extract table contents
        for table in document.tables:
            for row in table.rows:
                row_text = [
                    cell.text.strip()
                    for cell in row.cells
                    if cell.text.strip()
                ]

                if row_text:
                    extracted_text.append(" | ".join(row_text))

        return "\n".join(extracted_text).strip()

    except Exception as error:
        raise ValueError(f"DOCX extraction failed: {error}")


def extract_resume_text(file_path: str) -> dict:
    """Extract resume text based on file extension."""

    path = Path(file_path)
    extension = path.suffix.lower()

    if not path.exists():
        raise FileNotFoundError("Resume file not found.")

    if extension == ".pdf":
        text = extract_pdf_text(str(path))

    elif extension == ".docx":
        text = extract_docx_text(str(path))

    else:
        raise ValueError("Unsupported file format.")

    if not text:
        raise ValueError(
            "No readable text found. The resume may be scanned or image-based."
        )

    return {
        "filename": path.name,
        "file_type": extension,
        "text": text,
        "character_count": len(text)
    }
