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


def generate_ats_pdf(
    resume_data: Dict[str, Any],
    page_format: str = "ONE_PAGE",
    output_path: Optional[str] = None
) -> bytes:
    """
    Generates an ATS-compliant, pixel-perfect PDF using ReportLab.
    Enforces strict spacing budgets for ONE_PAGE vs TWO_PAGE layouts
    to eliminate text overflows and unintended blank pages.
    """
    buffer = io.BytesIO()
    target_doc = output_path if output_path else buffer

    is_one_page = (page_format.upper() == "ONE_PAGE")

    # Tight, consistent ATS margins
    left_margin = 0.5 * inch
    right_margin = 0.5 * inch
    top_margin = 0.45 * inch if is_one_page else 0.55 * inch
    bottom_margin = 0.45 * inch if is_one_page else 0.55 * inch

    doc = SimpleDocTemplate(
        target_doc,
        pagesize=letter,
        leftMargin=left_margin,
        rightMargin=right_margin,
        topMargin=top_margin,
        bottomMargin=bottom_margin,
    )

    styles = getSampleStyleSheet()

    # Color palette
    PRIMARY_COLOR = colors.HexColor("#1e293b") # Deep slate for text
    HEADING_COLOR = colors.HexColor("#0f172a") # Dark navy for headings
    ACCENT_COLOR = colors.HexColor("#0284c7")  # Subtle blue accent for rules
    MUTED_COLOR = colors.HexColor("#475569")   # Slate for meta info

    # Scaled typography budget based on page format
    name_size = 17 if is_one_page else 20
    name_leading = 20 if is_one_page else 24
    headline_size = 10 if is_one_page else 11
    body_size = 8.5 if is_one_page else 9.5
    body_leading = 11.5 if is_one_page else 13.0
    section_size = 10.5 if is_one_page else 11.5
    section_leading = 13 if is_one_page else 15
    spacer_large = 6 if is_one_page else 10
    spacer_small = 3 if is_one_page else 5

    # Styles
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
        leading=headline_size + 2,
        alignment=TA_CENTER,
        textColor=ACCENT_COLOR
    )

    contact_style = ParagraphStyle(
        'ResumeContact',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=body_size - 0.5,
        leading=body_size + 2,
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
        spaceAfter=1
    )

    item_title_style = ParagraphStyle(
        'ResumeItemTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=body_size + 0.5,
        leading=body_leading,
        textColor=HEADING_COLOR
    )

    item_sub_style = ParagraphStyle(
        'ResumeItemSub',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=body_size,
        leading=body_leading,
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
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=1.5
    )

    story = []

    # 1. HEADER
    header = resume_data.get('header', {})
    full_name = header.get('full_name') or 'Candidate Name'
    story.append(Paragraph(full_name, name_style))

    headline = header.get('headline')
    if headline:
        story.append(Spacer(1, 2))
        story.append(Paragraph(headline, headline_style))

    # Contact line
    contact_parts = []
    if header.get('email'):
        contact_parts.append(header['email'])
    if header.get('phone'):
        contact_parts.append(header['phone'])
    if header.get('location'):
        contact_parts.append(header['location'])
    if header.get('linkedin_url'):
        contact_parts.append(header['linkedin_url'].replace('https://www.', '').replace('https://', ''))
    if header.get('github_url'):
        contact_parts.append(header['github_url'].replace('https://www.', '').replace('https://', ''))

    if contact_parts:
        story.append(Spacer(1, 3))
        story.append(Paragraph(" &bull; ".join(contact_parts), contact_style))

    story.append(Spacer(1, spacer_large))

    def add_section_header(title: str):
        story.append(Paragraph(title.upper(), section_heading_style))
        story.append(HRFlowable(width="100%", thickness=1, color=ACCENT_COLOR, spaceAfter=4, spaceBefore=2))

    # 2. PROFESSIONAL SUMMARY
    summary = resume_data.get('summary')
    if summary:
        add_section_header("Professional Summary")
        story.append(Paragraph(summary, body_style))
        story.append(Spacer(1, spacer_large))

    # 3. TECHNICAL SKILLS
    skills = resume_data.get('skills', {})
    if skills:
        add_section_header("Technical Skills")
        skill_lines = []
        if isinstance(skills, dict):
            categories = [
                ("Languages", skills.get('languages', [])),
                ("Frameworks & Libraries", skills.get('frameworks', [])),
                ("Databases", skills.get('databases', [])),
                ("Cloud & DevOps", skills.get('cloud_and_devops', [])),
                ("Tools & Architecture", skills.get('developer_tools', [])),
            ]
            for label, items in categories:
                if items:
                    line = f"<b>{label}:</b> {', '.join(items)}"
                    story.append(Paragraph(line, body_style))
                    story.append(Spacer(1, 1.5))
        elif isinstance(skills, list):
            story.append(Paragraph(", ".join(skills), body_style))
        story.append(Spacer(1, spacer_large - 2))

    # 4. WORK EXPERIENCE
    work_exps = resume_data.get('work_experience', [])
    if work_exps:
        add_section_header("Work Experience")
        # Budget max items for ONE_PAGE if list is very long
        exps_to_render = work_exps[:2] if (is_one_page and len(work_exps) > 2) else work_exps
        for exp in exps_to_render:
            # Header line: Title & Company | Location & Dates
            title_text = f"<b>{exp.get('title', '')}</b> &mdash; {exp.get('company', '')}"
            date_text = f"{exp.get('start_date', '')} &ndash; {exp.get('end_date', 'Present')}"
            loc_text = exp.get('location', '')
            right_meta = f"{loc_text} | {date_text}" if loc_text else date_text

            header_table = Table(
                [[Paragraph(title_text, item_title_style), Paragraph(right_meta, item_sub_style)]],
                colWidths=[5.0 * inch, 2.5 * inch]
            )
            header_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 1),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ]))
            story.append(header_table)

            # Bullet points budget
            bullets = exp.get('bullet_points', [])
            bullet_limit = 3 if is_one_page else 5
            for b in bullets[:bullet_limit]:
                story.append(Paragraph(f"&bull; {b}", bullet_style))

            story.append(Spacer(1, spacer_small))
        story.append(Spacer(1, spacer_large - 3))

    # 5. PROJECTS
    projects = resume_data.get('projects', [])
    if projects:
        add_section_header("Key Projects")
        projs_to_render = projects[:2] if (is_one_page and len(projects) > 2) else projects
        for proj in projs_to_render:
            proj_title = proj.get('title', '')
            techs = ", ".join(proj.get('technologies', []))
            title_text = f"<b>{proj_title}</b>" + (f" | <i>{techs}</i>" if techs else "")
            role_text = proj.get('role', '')

            header_table = Table(
                [[Paragraph(title_text, item_title_style), Paragraph(role_text, item_sub_style)]],
                colWidths=[5.5 * inch, 2.0 * inch]
            )
            header_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 1),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ]))
            story.append(header_table)

            if proj.get('description'):
                story.append(Paragraph(proj['description'], body_style))

            highlights = proj.get('highlights', [])
            h_limit = 2 if is_one_page else 4
            for h in highlights[:h_limit]:
                story.append(Paragraph(f"&bull; {h}", bullet_style))

            story.append(Spacer(1, spacer_small))
        story.append(Spacer(1, spacer_large - 3))

    # 6. EDUCATION
    education = resume_data.get('education', [])
    if education:
        add_section_header("Education")
        for edu in education:
            edu_title = f"<b>{edu.get('degree', '')}</b> &mdash; {edu.get('institution', '')}"
            date_text = f"{edu.get('start_date', '')} - {edu.get('end_date', '')}".strip(" -")
            grade_info = f" ({edu.get('grade')})" if edu.get('grade') else ""

            header_table = Table(
                [[Paragraph(edu_title + grade_info, item_title_style), Paragraph(date_text, item_sub_style)]],
                colWidths=[5.5 * inch, 2.0 * inch]
            )
            header_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 1),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ]))
            story.append(header_table)
        story.append(Spacer(1, spacer_large - 3))

    # 7. CERTIFICATIONS
    certifications = resume_data.get('certifications', [])
    if certifications and (not is_one_page or len(story) < 40):
        add_section_header("Certifications")
        for cert in certifications:
            cert_name = f"&bull; <b>{cert.get('name', '')}</b> &mdash; {cert.get('issuing_organization', '')}"
            if cert.get('issue_date'):
                cert_name += f" ({cert['issue_date']})"
            story.append(Paragraph(cert_name, bullet_style))

    # Build PDF
    doc.build(story)

    if output_path:
        with open(output_path, 'rb') as f:
            return f.read()
    else:
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes
