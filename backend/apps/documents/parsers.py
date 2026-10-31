import io
import re
from pypdf import PdfReader
from docx import Document

class DocumentParserError(Exception):
    pass

def extract_text_from_pdf(file_bytes_or_path) -> str:
    """Extracts text content from a PDF file using pypdf."""
    try:
        if isinstance(file_bytes_or_path, bytes):
            stream = io.BytesIO(file_bytes_or_path)
            reader = PdfReader(stream)
        elif hasattr(file_bytes_or_path, 'read'):
            content = file_bytes_or_path.read()
            if isinstance(content, str):
                content = content.encode('utf-8')
            stream = io.BytesIO(content)
            reader = PdfReader(stream)
        else:
            reader = PdfReader(file_bytes_or_path)

        text_pages = []
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text_pages.append(page_text.strip())
        return "\n\n".join(text_pages)
    except Exception as e:
        raise DocumentParserError(f"Failed to parse PDF document: {str(e)}")

def extract_text_from_docx(file_bytes_or_path) -> str:
    """Extracts text content from a DOCX file using python-docx."""
    try:
        if isinstance(file_bytes_or_path, bytes):
            stream = io.BytesIO(file_bytes_or_path)
            doc = Document(stream)
        elif hasattr(file_bytes_or_path, 'read'):
            stream = io.BytesIO(file_bytes_or_path.read())
            doc = Document(stream)
        else:
            doc = Document(file_bytes_or_path)

        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        # Also extract table text
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                if row_text:
                    paragraphs.append(row_text)
        return "\n\n".join(paragraphs)
    except Exception as e:
        raise DocumentParserError(f"Failed to parse DOCX document: {str(e)}")

def parse_uploaded_document(file_obj, filename: str) -> str:
    """Detects format by extension and extracts plain text."""
    lower_name = filename.lower()
    if lower_name.endswith('.pdf'):
        return extract_text_from_pdf(file_obj)
    elif lower_name.endswith('.docx') or lower_name.endswith('.doc'):
        return extract_text_from_docx(file_obj)
    elif lower_name.endswith('.txt'):
        if hasattr(file_obj, 'read'):
            content = file_obj.read()
            return content.decode('utf-8', errors='ignore') if isinstance(content, bytes) else str(content)
        return ""
    else:
        raise DocumentParserError("Unsupported file type. Please upload a PDF, DOCX, or TXT file.")


def extract_sections_heuristic(text: str) -> dict:
    """
    Lightweight heuristic extractor to categorize reference resume text into basic sections.
    The LLM service will refine this into validated structured JSON.
    """
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    phone_match = re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)

    return {
        'raw_text': text,
        'detected_email': email_match.group(0) if email_match else '',
        'detected_phone': phone_match.group(0) if phone_match else '',
        'first_few_lines': lines[:5] if lines else [],
    }
