import io
import re
from typing import Dict, Any, Optional
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
    Table,
    TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from pypdf import PdfReader

def to_reportlab_xml(text: Any) -> str:
    """
    Normalizes text for ReportLab Paragraph XML parsing:
    1. Escapes standalone '&' to '&amp;' (preserving valid XML entities).
    2. Converts markdown bold syntax (**text** or __text__) to <b>text</b>.
    3. Converts markdown italics (*text* or _text_) if present.
    """
    if text is None:
        return ""
    if not isinstance(text, str):
        text = str(text)
    
    # Escape standalone '&' that aren't already xml entities
    text = re.sub(r'&(?!(amp|bull|ndash|mdash|nbsp|lt|gt|quot|apos|#\d+);)', '&amp;', text)
    # Convert **bold** and __bold__ to <b>bold</b>
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'__(.+?)__', r'<b>\1</b>', text)
    return text


def normalize_filename(
    candidate_name: str,
    company_name: str,
    target_role: str,
    version_number: int = 1
) -> str:
    """
    Produces normalized filename according to specifications:
    candidate_name_company_name_target_role_version_number.pdf
    Lowercase, spaces replaced with underscores, invalid characters stripped.
    """
    def sanitize(text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r'[^a-z0-9\s_-]', '', text)
        text = re.sub(r'[\s-]+', '_', text)
        return text.strip('_')

    name_clean = sanitize(candidate_name) or "candidate"
    company_clean = sanitize(company_name) or "company"
    role_clean = sanitize(target_role) or "target_role"
    ver_clean = str(version_number)

    return f"{name_clean}_{company_clean}_{role_clean}_{ver_clean}.pdf"


def _build_pdf_stream(
    resume_data: Dict[str, Any],
    scale: float = 1.0,
    is_one_page: bool = True
) -> bytes:
    """
    Renders 100% of the resume snapshot content into an in-memory PDF
    scaled precisely with dynamic typography, leadings, and spacing budgets.
    """
    buf = io.BytesIO()

    # Dynamic margins & available width
    horiz_margin = max(0.28, 0.40 * scale) * inch
    vert_margin = max(0.25, 0.35 * scale) * inch if is_one_page else 0.55 * inch
    content_width = letter[0] - (2 * horiz_margin)

    doc = SimpleDocTemplate(
        buf,
        pagesize=letter,
        leftMargin=horiz_margin,
        rightMargin=horiz_margin,
        topMargin=vert_margin,
        bottomMargin=vert_margin,
    )

    styles = getSampleStyleSheet()

    PRIMARY_COLOR = colors.HexColor("#1e293b")
    HEADING_COLOR = colors.HexColor("#0f172a")
    ACCENT_COLOR = colors.HexColor("#0284c7")
    MUTED_COLOR = colors.HexColor("#475569")

    # Scaled typography budget based on scale factor
    name_size = round(16.5 * scale, 1)
    name_leading = round(19 * scale, 1)
    headline_size = round(9.5 * scale, 1)
    headline_leading = round(11.5 * scale, 1)
    body_size = round(8.0 * scale, 1)
    body_leading = round(10.0 * scale, 1)
    section_size = round(9.5 * scale, 1)
    section_leading = round(11.5 * scale, 1)

    spacer_large = max(2, round(4.0 * scale))
    spacer_small = max(1, round(2.0 * scale))
    bullet_space = max(0.5, round(1.2 * scale, 1))

    name_style = ParagraphStyle(
        'ResumeName',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=name_size,
        leading=name_leading,
        alignment=TA_CENTER,
        textColor=HEADING_COLOR
    )

    headline_style = ParagraphStyle(
        'ResumeHeadline',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=headline_size,
        leading=headline_leading,
        alignment=TA_CENTER,
        textColor=ACCENT_COLOR
    )

    contact_style = ParagraphStyle(
        'ResumeContact',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=max(6.0, body_size - 0.5),
        leading=body_leading,
        alignment=TA_CENTER,
        textColor=MUTED_COLOR
    )

    section_heading_style = ParagraphStyle(
        'ResumeSection',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=section_size,
        leading=section_leading,
        textColor=HEADING_COLOR,
        spaceBefore=0,
        spaceAfter=0.5
    )

    item_title_style = ParagraphStyle(
        'ResumeItemTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=body_size + 0.3,
        leading=body_leading,
        textColor=HEADING_COLOR
    )

    proj_title_style = ParagraphStyle(
        'ResumeProjTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=body_size + 0.3,
        leading=body_leading,
        textColor=HEADING_COLOR,
        spaceAfter=1
    )

    item_sub_style = ParagraphStyle(
        'ResumeItemSub',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=max(5.8, body_size - 0.4),
        leading=body_leading,
        alignment=TA_RIGHT,
        textColor=MUTED_COLOR
    )

    body_style = ParagraphStyle(
        'ResumeBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=body_size,
        leading=body_leading,
        textColor=PRIMARY_COLOR,
        alignment=TA_JUSTIFY
    )

    bullet_style = ParagraphStyle(
        'ResumeBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=body_size,
        leading=body_leading,
        textColor=PRIMARY_COLOR,
        leftIndent=10,
        firstLineIndent=-7,
        spaceAfter=bullet_space
    )

    story = []

    # 1. HEADER
    header = resume_data.get('header', {})
    full_name = header.get('full_name') or 'Candidate Name'
    story.append(Paragraph(to_reportlab_xml(full_name), name_style))

    headline = header.get('headline')
    if headline:
        story.append(Spacer(1, 1))
        story.append(Paragraph(to_reportlab_xml(headline), headline_style))

    contact_parts = []
    if header.get('email'):
        contact_parts.append(to_reportlab_xml(header['email']))
    if header.get('phone'):
        contact_parts.append(to_reportlab_xml(header['phone']))
    if header.get('location'):
        contact_parts.append(to_reportlab_xml(header['location']))
    if header.get('linkedin_url'):
        contact_parts.append(f'<font color="#2563EB"><u><a href="{header["linkedin_url"]}">LinkedIn</a></u></font>')
    if header.get('github_url'):
        contact_parts.append(f'<font color="#2563EB"><u><a href="{header["github_url"]}">GitHub</a></u></font>')

    if contact_parts:
        story.append(Spacer(1, 1))
        story.append(Paragraph(" &bull; ".join(contact_parts), contact_style))

    story.append(Spacer(1, spacer_large))

    def add_section_header(title: str):
        story.append(Paragraph(title.upper(), section_heading_style))
        story.append(HRFlowable(width="100%", thickness=0.8, color=ACCENT_COLOR, spaceAfter=2, spaceBefore=1))

    # 2. PROFESSIONAL SUMMARY
    summary = resume_data.get('summary')
    if summary:
        add_section_header("Professional Summary")
        story.append(Paragraph(to_reportlab_xml(summary), body_style))
        story.append(Spacer(1, spacer_large))

    # 3. TECHNICAL SKILLS
    skills = resume_data.get('skills', {})
    if skills:
        add_section_header("Technical Skills")
        if isinstance(skills, dict):
            categories = [
                ("Languages", skills.get('languages', [])),
                ("Frameworks & Libraries", skills.get('frameworks', [])),
                ("Databases & Storage", skills.get('databases', [])),
                ("Cloud & DevOps", skills.get('cloud_and_devops', [])),
                ("Tools & Architecture", skills.get('developer_tools', [])),
            ]
            for label, items in categories:
                if items:
                    line = f"<b>{label}:</b> {', '.join(items)}"
                    story.append(Paragraph(to_reportlab_xml(line), body_style))
                    story.append(Spacer(1, 0.8))
        elif isinstance(skills, list):
            story.append(Paragraph(to_reportlab_xml(", ".join(skills)), body_style))
        story.append(Spacer(1, spacer_large - 1))

    # 4. WORK EXPERIENCE (Render ALL work experiences and ALL bullet points without exp technologies)
    work_exps = resume_data.get('work_experience') or resume_data.get('experiences') or resume_data.get('experience', [])
    if work_exps:
        add_section_header("Work Experience")
        for exp in work_exps:
            title_text = f"<b>{exp.get('company', '')}</b> &mdash; {exp.get('title', '')}"
            date_text = f"{exp.get('start_date', '')} &ndash; {exp.get('end_date', 'Present')}"
            loc_text = exp.get('location', '')
            right_meta = f"{loc_text} | {date_text}" if loc_text else date_text

            header_table = Table(
                [[Paragraph(to_reportlab_xml(title_text), item_title_style), Paragraph(to_reportlab_xml(right_meta), item_sub_style)]],
                colWidths=[content_width * 0.68, content_width * 0.32]
            )
            header_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
            ]))
            story.append(header_table)

            bullets = exp.get('bullet_points', [])
            for b in bullets:
                story.append(Paragraph(f"&bull; {to_reportlab_xml(b)}", bullet_style))

            story.append(Spacer(1, spacer_small))
        story.append(Spacer(1, spacer_large - 1))

    # 5. KEY PROJECTS (Format: Project Title | Technologies | GitHub • Live Demo)
    projects = resume_data.get('projects') or resume_data.get('key_projects', [])
    if projects:
        add_section_header("Key Projects")
        for proj in projects:
            proj_title = (proj.get('title') or '').strip()
            github_or_url = (proj.get('github_url') or proj.get('url') or '').strip()
            demo_url = (proj.get('demo_url') or '').strip()

            links_part = []
            if github_or_url:
                safe_git = github_or_url.replace('"', '&quot;')
                links_part.append(f'<a href="{safe_git}">GitHub</a>')
            if demo_url:
                safe_demo = demo_url.replace('"', '&quot;')
                links_part.append(f'<a href="{safe_demo}">Live Demo</a>')

            links_str = f'<font color="#2563EB">{" &bull; ".join(links_part)}</font>' if links_part else ""
            techs = ", ".join(str(t).strip() for t in (proj.get('technologies') or []) if str(t).strip())

            header_parts = []
            if proj_title:
                header_parts.append(proj_title)
            if techs:
                header_parts.append(techs)
            if links_str:
                header_parts.append(links_str)

            title_text = " | ".join(header_parts)
            story.append(Paragraph(to_reportlab_xml(title_text), proj_title_style))

            if proj.get('description'):
                story.append(Paragraph(to_reportlab_xml(proj['description']), body_style))
                story.append(Spacer(1, 0.8))

            highlights = proj.get('highlights', [])
            for h in highlights:
                story.append(Paragraph(f"&bull; {to_reportlab_xml(h)}", bullet_style))

            story.append(Spacer(1, spacer_small))
        story.append(Spacer(1, spacer_large - 1))

    # 6. EDUCATION
    education = resume_data.get('education', [])
    if education:
        add_section_header("Education")
        for edu in education:
            degree_str = f"<b>{edu.get('degree', '')}</b>"
            if edu.get('field_of_study'):
                degree_str += f" in {edu.get('field_of_study')}"
            inst_str = edu.get('institution', '')
            grade_str = f" ({edu.get('grade')})" if edu.get('grade') else ""
            left_text = f"{degree_str} &mdash; {inst_str}{grade_str}"
            date_text = f"{edu.get('start_date', '')} &ndash; {edu.get('end_date', '')}".strip(" –-")

            edu_table = Table(
                [[Paragraph(to_reportlab_xml(left_text), body_style), Paragraph(to_reportlab_xml(date_text), item_sub_style)]],
                colWidths=[content_width * 0.78, content_width * 0.22]
            )
            edu_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
            ]))
            story.append(edu_table)
        story.append(Spacer(1, spacer_large - 1))

    # 7. ACHIEVEMENTS & PROFILES
    achievements_coding = (
        resume_data.get('achievements_and_coding')
        or resume_data.get('achievements_hackathons_coding')
        or resume_data.get('coding_and_hackathons')
        or resume_data.get('achievements_and_hackathons')
        or (resume_data.get('achievements', []) + resume_data.get('coding_profiles', []) + resume_data.get('hackathons', []))
    )
    if achievements_coding:
        add_section_header("Achievements & Profiles")
        for item in achievements_coding:
            if isinstance(item, str) and item.strip():
                story.append(Paragraph(f"&bull; {to_reportlab_xml(item.strip())}", bullet_style))

    doc.build(story)
    return buf.getvalue()


def generate_ats_pdf(
    resume_data: Dict[str, Any],
    page_format: str = "ONE_PAGE",
    output_path: Optional[str] = None
) -> bytes:
    """
    Generates an ATS-compliant, pixel-perfect PDF using ReportLab.
    Dynamically adjusts typography and spacing budgets to guarantee
    that 100% of snapshot content fits on EXACTLY ONE PAGE for ONE_PAGE format.
    """
    is_one_page = (page_format.upper() == "ONE_PAGE")

    if not is_one_page:
        pdf_bytes = _build_pdf_stream(resume_data, scale=1.0, is_one_page=False)
    else:
        # Dynamic search for the optimal scale factor to fit exactly 1 page
        scale_steps = [1.0, 0.95, 0.90, 0.86, 0.82, 0.78, 0.74, 0.70]
        pdf_bytes = None
        for scale in scale_steps:
            attempt_bytes = _build_pdf_stream(resume_data, scale=scale, is_one_page=True)
            page_count = len(PdfReader(io.BytesIO(attempt_bytes)).pages)
            pdf_bytes = attempt_bytes
            if page_count == 1:
                break

    if output_path:
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)

    return pdf_bytes
