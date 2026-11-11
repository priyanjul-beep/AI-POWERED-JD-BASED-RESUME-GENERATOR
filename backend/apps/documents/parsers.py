import io
import re
from typing import Dict, Any, List, Tuple
from pypdf import PdfReader
from docx import Document

class DocumentParserError(Exception):
    pass

def _get_pdf_reader(file_bytes_or_path) -> Tuple[PdfReader, bytes]:
    """Helper to get a PdfReader and raw bytes."""
    if isinstance(file_bytes_or_path, bytes):
        raw_bytes = file_bytes_or_path
        stream = io.BytesIO(file_bytes_or_path)
        reader = PdfReader(stream)
    elif hasattr(file_bytes_or_path, 'read'):
        content = file_bytes_or_path.read()
        if hasattr(file_bytes_or_path, 'seek'):
            file_bytes_or_path.seek(0)
        if isinstance(content, str):
            content = content.encode('utf-8')
        raw_bytes = content
        stream = io.BytesIO(content)
        reader = PdfReader(stream)
    else:
        with open(file_bytes_or_path, 'rb') as f:
            raw_bytes = f.read()
        reader = PdfReader(io.BytesIO(raw_bytes))
    return reader, raw_bytes


def extract_pdf_with_links_and_projects(file_bytes_or_path) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Extracts text from PDF while parsing embedded link annotations (GitHub, Live Demo, Portfolio).
    Associates embedded links directly with project titles and appends explicit URLs inline.
    """
    try:
        reader, _ = _get_pdf_reader(file_bytes_or_path)
        pages_text = []
        extracted_projects = []

        for page in reader.pages:
            # 1. Collect all link annotations
            annots = []
            if '/Annots' in page:
                for a in page['/Annots']:
                    try:
                        obj = a.get_object()
                        if '/A' in obj and '/URI' in obj['/A']:
                            uri = str(obj['/A']['/URI']).strip()
                            rect = [float(v) for v in obj['/Rect']]
                            annots.append({
                                'uri': uri,
                                'x0': rect[0],
                                'y0': rect[1],
                                'x1': rect[2],
                                'y1': rect[3],
                                'y_mid': (rect[1] + rect[3]) / 2.0
                            })
                    except Exception:
                        pass

            # 2. Extract text lines with positions
            line_dict = {}
            def visitor(text, cm, tm, fontDict, fontSize):
                t = text.strip()
                if not t:
                    return
                y = round(cm[5] + tm[5], 1)
                x = round(cm[4] + tm[4], 1)
                matched_y = None
                for existing_y in line_dict:
                    if abs(existing_y - y) <= 2.5:
                        matched_y = existing_y
                        break
                target_y = matched_y if matched_y is not None else y
                if target_y not in line_dict:
                    line_dict[target_y] = []
                line_dict[target_y].append({'text': t, 'x': x, 'font': fontSize})

            try:
                page.extract_text(visitor_text=visitor)
            except Exception:
                # Fallback to standard extract_text if visitor fails
                page_text = page.extract_text() or ""
                pages_text.append(page_text.strip())
                continue

            sorted_ys = sorted(line_dict.keys(), reverse=True)
            page_lines = []
            for y in sorted_ys:
                tokens = sorted(line_dict[y], key=lambda t: t['x'])
                line_text = " ".join(t['text'] for t in tokens)
                
                # Match annotations whose bounding box contains or is very close to y
                line_annots = [
                    a for a in annots
                    if (a['y0'] - 1.5 <= y <= a['y1'] + 1.5) or (abs(a['y_mid'] - y) <= 3.0)
                ]
                line_annots.sort(key=lambda a: a['x0'])
                
                # Append link URLs inline so LLM and raw text clearly show destination
                if line_annots:
                    links_text = " ".join([f"[{a['uri']}]" for a in line_annots])
                    line_text_with_links = f"{line_text} {links_text}"
                else:
                    line_text_with_links = line_text
                
                page_lines.append((line_text, line_text_with_links, line_annots))

            pages_text.append("\n".join(t[1] for t in page_lines))

            # Detect projects from lines
            in_proj = False
            for original_line, line_text_with_links, line_annots in page_lines:
                clean_line = original_line.strip()
                lower = clean_line.lower()
                
                # Section boundary checks
                if any(sec in lower for sec in ['projects', 'key projects', 'academic projects', 'personal projects']):
                    if len(clean_line.split()) <= 4:
                        in_proj = True
                        continue
                elif in_proj and any(sec in lower for sec in ['education', 'experience', 'work experience', 'certifications', 'skills', 'achievements']):
                    if len(clean_line.split()) <= 4:
                        in_proj = False
                        continue

                if in_proj:
                    # Exclude bullets or sentences ending with a period
                    if clean_line.endswith('.') or clean_line.startswith('\x7f') or clean_line.startswith('•') or clean_line.startswith('-'):
                        continue
                    
                    # Project title line detection: has annotations or has '|' / '—' with link keywords
                    if line_annots or ('|' in clean_line and any(k in lower for k in ['github', 'demo', 'link', 'live'])):
                        clean_title = re.split(r'\s*\|\s*(github|live demo|demo|link)', clean_line, flags=re.IGNORECASE)[0].strip()
                        clean_title = clean_title.split('[')[0].strip()
                        
                        gh_link = ""
                        dm_link = ""
                        for a in line_annots:
                            uri = a['uri']
                            if 'github.com' in uri.lower() or 'gitlab' in uri.lower():
                                gh_link = uri
                            else:
                                dm_link = uri
                        
                        if clean_title and len(clean_title) > 3:
                            extracted_projects.append({
                                'title': clean_title,
                                'github_url': gh_link,
                                'demo_url': dm_link,
                                'url': gh_link or dm_link or ''
                            })

        return "\n\n".join(pages_text), extracted_projects
    except Exception as e:
        raise DocumentParserError(f"Failed to parse PDF document: {str(e)}")


def extract_text_from_pdf(file_bytes_or_path) -> str:
    """Extracts text content from a PDF file using pypdf, with embedded URLs preserved."""
    try:
        text, _ = extract_pdf_with_links_and_projects(file_bytes_or_path)
        return text
    except Exception:
        # Fallback to simple extraction
        reader, _ = _get_pdf_reader(file_bytes_or_path)
        text_pages = []
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text_pages.append(t.strip())
        return "\n\n".join(text_pages)


def extract_docx_with_links_and_projects(file_bytes_or_path) -> Tuple[str, List[Dict[str, Any]]]:
    """Extracts text and embedded hyperlinks from a DOCX file."""
    try:
        if isinstance(file_bytes_or_path, bytes):
            stream = io.BytesIO(file_bytes_or_path)
            doc = Document(stream)
        elif hasattr(file_bytes_or_path, 'read'):
            content = file_bytes_or_path.read()
            if hasattr(file_bytes_or_path, 'seek'):
                file_bytes_or_path.seek(0)
            stream = io.BytesIO(content)
            doc = Document(stream)
        else:
            doc = Document(file_bytes_or_path)

        paragraphs_text = []
        extracted_projects = []
        in_proj = False

        for p in doc.paragraphs:
            text = p.text.strip()
            if not text:
                continue

            # Check for embedded hyperlinks
            links = []
            try:
                for child in p._element:
                    tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                    if tag == 'hyperlink':
                        r_id = child.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
                        link_text = "".join(child.itertext()).strip()
                        target_url = p.part.rels[r_id].target_ref if (r_id and r_id in p.part.rels) else ""
                        if target_url:
                            links.append({'text': link_text, 'uri': target_url})
            except Exception:
                pass

            p_line = text
            if links:
                p_line += " " + " ".join([f"[{l['uri']}]" for l in links])
            paragraphs_text.append(p_line)

            lower = text.lower()
            if any(sec in lower for sec in ['projects', 'key projects', 'academic projects']):
                if len(text.split()) <= 4:
                    in_proj = True
                    continue
            elif in_proj and any(sec in lower for sec in ['education', 'experience', 'work experience', 'certifications', 'skills', 'achievements']):
                if len(text.split()) <= 4:
                    in_proj = False
                    continue

            if in_proj:
                if text.endswith('.') or text.startswith('•') or text.startswith('-') or text.startswith('*'):
                    continue
                if links or ('|' in text and any(k in lower for k in ['github', 'demo', 'link', 'live'])):
                    clean_title = re.split(r'\s*\|\s*(github|live demo|demo|link)', text, flags=re.IGNORECASE)[0].strip()
                    gh_link = ""
                    dm_link = ""
                    for l in links:
                        uri = l['uri']
                        if 'github.com' in uri.lower() or 'gitlab' in uri.lower():
                            gh_link = uri
                        else:
                            dm_link = uri
                    if clean_title and len(clean_title) > 3:
                        extracted_projects.append({
                            'title': clean_title,
                            'github_url': gh_link,
                            'demo_url': dm_link,
                            'url': gh_link or dm_link or ''
                        })

        # Also extract table text
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                if row_text:
                    paragraphs_text.append(row_text)

        return "\n\n".join(paragraphs_text), extracted_projects
    except Exception as e:
        raise DocumentParserError(f"Failed to parse DOCX document: {str(e)}")


def extract_text_from_docx(file_bytes_or_path) -> str:
    """Extracts text content from a DOCX file using python-docx."""
    text, _ = extract_docx_with_links_and_projects(file_bytes_or_path)
    return text


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
            if hasattr(file_obj, 'seek'):
                file_obj.seek(0)
            return content.decode('utf-8', errors='ignore') if isinstance(content, bytes) else str(content)
        return ""
    else:
        raise DocumentParserError("Unsupported file type. Please upload a PDF, DOCX, or TXT file.")


def parse_resume_document_full(file_obj, filename: str) -> Tuple[str, List[Dict[str, Any]]]:
    """Detects format by extension and extracts both plain text and structured project links."""
    lower_name = filename.lower()
    if lower_name.endswith('.pdf'):
        return extract_pdf_with_links_and_projects(file_obj)
    elif lower_name.endswith('.docx') or lower_name.endswith('.doc'):
        return extract_docx_with_links_and_projects(file_obj)
    elif lower_name.endswith('.txt'):
        text = parse_uploaded_document(file_obj, filename)
        return text, []
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
