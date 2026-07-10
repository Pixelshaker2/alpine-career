"""PDF service — generates professional CV and cover letter PDFs.

Uses WeasyPrint to render HTML templates to PDF.
Templates use clean, professional styling suitable for
the German/Swiss job market.
"""

import logging
from datetime import datetime, timezone

from src.services.ai_service import GeneratedCoverLetter, GeneratedCV

logger = logging.getLogger(__name__)

# --- CV HTML Template ---

CV_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<style>
@page {{
    size: A4;
    margin: 2cm 2.5cm;
}}
body {{
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
    font-size: 10pt;
    line-height: 1.5;
    color: #1a1a1a;
    margin: 0;
}}
h1 {{
    font-size: 18pt;
    font-weight: 700;
    margin: 0 0 2pt 0;
    color: #0d47a1;
}}
.subtitle {{
    font-size: 11pt;
    color: #555;
    margin: 0 0 12pt 0;
}}
.contact {{
    font-size: 9pt;
    color: #666;
    margin-bottom: 16pt;
    padding-bottom: 8pt;
    border-bottom: 2px solid #0d47a1;
}}
h2 {{
    font-size: 12pt;
    font-weight: 700;
    color: #0d47a1;
    margin: 16pt 0 6pt 0;
    text-transform: uppercase;
    letter-spacing: 0.5pt;
    border-bottom: 1px solid #ddd;
    padding-bottom: 3pt;
}}
.section-content {{
    margin: 0 0 8pt 0;
    white-space: pre-wrap;
}}
.experience-item {{
    margin-bottom: 10pt;
}}
.job-header {{
    font-weight: 700;
    font-size: 10.5pt;
}}
.job-meta {{
    font-size: 9pt;
    color: #666;
    margin-bottom: 4pt;
}}
ul {{
    margin: 2pt 0;
    padding-left: 16pt;
}}
li {{
    margin-bottom: 2pt;
}}
.skills-grid {{
    display: flex;
    flex-wrap: wrap;
    gap: 4pt;
}}
.skill-tag {{
    background: #e8eaf6;
    color: #283593;
    padding: 2pt 8pt;
    border-radius: 3pt;
    font-size: 9pt;
}}
.footer {{
    font-size: 8pt;
    color: #999;
    margin-top: 20pt;
    text-align: center;
}}
</style>
</head>
<body>

<h1>{name}</h1>
<p class="subtitle">{subtitle}</p>
<p class="contact">{email} · {phone} · {location}</p>

<h2>Zusammenfassung</h2>
<div class="section-content">{summary}</div>

<h2>Berufserfahrung</h2>
<div class="section-content">{experience}</div>

<h2>Skills</h2>
<div class="section-content">{skills}</div>

<h2>Zertifizierungen</h2>
<div class="section-content">{certifications}</div>

<h2>Sprachen</h2>
<div class="section-content">{languages}</div>

</body>
</html>
"""

# --- Cover Letter HTML Template ---

COVER_LETTER_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<style>
@page {{
    size: A4;
    margin: 2.5cm 2.5cm 2cm 2.5cm;
}}
body {{
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #1a1a1a;
    margin: 0;
}}
.sender {{
    margin-bottom: 24pt;
}}
.sender-name {{
    font-size: 14pt;
    font-weight: 700;
    color: #0d47a1;
    margin: 0;
}}
.sender-info {{
    font-size: 9pt;
    color: #666;
    margin: 2pt 0 0 0;
}}
.recipient {{
    margin-bottom: 16pt;
    font-size: 10pt;
}}
.date {{
    margin-bottom: 16pt;
    font-size: 10pt;
    color: #666;
}}
.subject {{
    font-weight: 700;
    font-size: 11pt;
    margin-bottom: 16pt;
}}
.body-text {{
    white-space: pre-wrap;
    margin-bottom: 24pt;
}}
.signature {{
    margin-top: 24pt;
}}
.signature-name {{
    font-weight: 700;
}}
</style>
</head>
<body>

<div class="sender">
    <p class="sender-name">{name}</p>
    <p class="sender-info">{email} · {phone}</p>
    <p class="sender-info">{sender_location}</p>
</div>

<div class="recipient">
    <p>{company}</p>
    <p>{company_location}</p>
</div>

<p class="date">{date}</p>

<p class="subject">{subject}</p>

<div class="body-text">{body}</div>

<div class="signature">
    <p>Mit freundlichen Gruessen</p>
    <p class="signature-name">{name}</p>
</div>

</body>
</html>
"""


def _format_date_german() -> str:
    """Format current date in German style."""
    now = datetime.now(timezone.utc)
    months = [
        "", "Januar", "Februar", "Maerz", "April", "Mai", "Juni",
        "Juli", "August", "September", "Oktober", "November", "Dezember",
    ]
    return f"{now.day}. {months[now.month]} {now.year}"


def render_cv_pdf(
    cv: GeneratedCV,
    name: str,
    email: str,
    phone: str,
    location: str,
    languages: str = "Deutsch (Muttersprache), Englisch (verhandlungssicher)",
) -> bytes:
    """Render an optimized CV as PDF.

    Args:
        cv: Generated CV content from AI service.
        name: Applicant name.
        email: Contact email.
        phone: Contact phone.
        location: Current location.
        languages: Language skills.

    Returns:
        PDF file as bytes.
    """
    from weasyprint import HTML

    html_content = CV_HTML_TEMPLATE.format(
        name=name,
        subtitle="IT-Systemadministrator — Cloud & Modern Workplace",
        email=email,
        phone=phone,
        location=location,
        summary=_escape_html(cv.summary),
        experience=_escape_html(cv.experience),
        skills=_escape_html(cv.skills),
        certifications=_escape_html(cv.certifications),
        languages=_escape_html(languages),
    )

    pdf_bytes = HTML(string=html_content).write_pdf()
    logger.info("CV PDF rendered", extra={"size_bytes": len(pdf_bytes)})
    return pdf_bytes


def render_cover_letter_pdf(
    letter: GeneratedCoverLetter,
    name: str,
    email: str,
    phone: str,
    sender_location: str,
    company: str,
    company_location: str,
) -> bytes:
    """Render a cover letter as PDF.

    Args:
        letter: Generated cover letter from AI service.
        name: Applicant name.
        email: Contact email.
        phone: Contact phone.
        sender_location: Applicant's location.
        company: Target company name.
        company_location: Target company location.

    Returns:
        PDF file as bytes.
    """
    from weasyprint import HTML

    html_content = COVER_LETTER_HTML_TEMPLATE.format(
        name=name,
        email=email,
        phone=phone,
        sender_location=sender_location,
        company=_escape_html(company),
        company_location=_escape_html(company_location),
        date=_format_date_german(),
        subject=_escape_html(letter.subject),
        body=_escape_html(letter.body),
    )

    pdf_bytes = HTML(string=html_content).write_pdf()
    logger.info(
        "Cover letter PDF rendered",
        extra={"size_bytes": len(pdf_bytes)},
    )
    return pdf_bytes


def _escape_html(text: str) -> str:
    """Escape HTML special characters but preserve line breaks."""
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    return text
