"""PDF service — generates professional CV and cover letter PDFs.

Uses fpdf2 (pure Python, keine System-Dependencies).
Templates mit sauberem, professionellem Layout fuer den
deutsch/schweizerischen Arbeitsmarkt.
"""

import io
import logging
from datetime import datetime, timezone

from fpdf import FPDF

from src.services.ai_service import GeneratedCoverLetter, GeneratedCV

logger = logging.getLogger(__name__)

# Farben
BLUE = (13, 71, 161)        # Akzentfarbe
DARK = (26, 26, 26)         # Haupttext
GRAY = (100, 100, 100)      # Sekundaertext
LIGHT_GRAY = (200, 200, 200)  # Linien


class CVDocument(FPDF):
    """Professional CV PDF document."""

    def header(self) -> None:
        """No default header — we build our own."""

    def footer(self) -> None:
        """Page number in footer."""
        self.set_y(-15)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*GRAY)
        self.cell(0, 10, f"Seite {self.page_no()}", align="C")

    def add_section_header(self, title: str) -> None:
        """Add a styled section header with blue underline."""
        self.ln(6)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(*BLUE)
        self.cell(0, 7, title.upper(), new_x="LMARGIN", new_y="NEXT")
        # Trennlinie
        self.set_draw_color(*LIGHT_GRAY)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(3)

    def add_body_text(self, text: str) -> None:
        """Add body text in standard formatting."""
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*DARK)
        # Ersetze problematische Zeichen
        clean = _clean_text(text)
        self.multi_cell(0, 5, clean)
        self.ln(2)


class CoverLetterDocument(FPDF):
    """Professional cover letter PDF document."""

    def header(self) -> None:
        """No default header."""

    def footer(self) -> None:
        """No page number on cover letter."""


def _clean_text(text: str) -> str:
    """Clean text for fpdf2 — replace unsupported chars."""
    # fpdf2 mit Helvetica unterstuetzt kein volles Unicode
    # Ersetze gaengige Sonderzeichen
    replacements = {
        "–": "-",   # en-dash
        "—": "-",   # em-dash
        "‘": "'",   # left single quote
        "’": "'",   # right single quote
        "“": '"',   # left double quote
        "”": '"',   # right double quote
        "•": "-",   # bullet
        "…": "...", # ellipsis
        "«": '"',   # guillemet left
        "»": '"',   # guillemet right
        "​": "",    # zero-width space
        "\t": "    ",    # tab
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


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
    pdf = CVDocument(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    pdf.set_margins(25, 20, 25)

    # === Name ===
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(*BLUE)
    pdf.cell(0, 10, _clean_text(name), new_x="LMARGIN", new_y="NEXT")

    # === Untertitel ===
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(*GRAY)
    pdf.cell(
        0, 6,
        "IT-Systemadministrator - Cloud & Modern Workplace",
        new_x="LMARGIN", new_y="NEXT",
    )

    # === Kontakt ===
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*GRAY)
    contact = f"{email}  |  {phone}  |  {location}"
    pdf.cell(0, 6, _clean_text(contact), new_x="LMARGIN", new_y="NEXT")

    # Blaue Trennlinie
    pdf.ln(2)
    pdf.set_draw_color(*BLUE)
    pdf.set_line_width(0.5)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
    pdf.ln(4)

    # === Zusammenfassung ===
    pdf.add_section_header("Zusammenfassung")
    pdf.add_body_text(cv.summary)

    # === Berufserfahrung ===
    pdf.add_section_header("Berufserfahrung")
    pdf.add_body_text(cv.experience)

    # === Skills ===
    pdf.add_section_header("Skills")
    pdf.add_body_text(cv.skills)

    # === Zertifizierungen ===
    pdf.add_section_header("Zertifizierungen")
    pdf.add_body_text(cv.certifications)

    # === Sprachen ===
    pdf.add_section_header("Sprachen")
    pdf.add_body_text(languages)

    # Output
    buf = io.BytesIO()
    pdf.output(buf)
    pdf_bytes = buf.getvalue()

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
    pdf = CoverLetterDocument(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=25)
    pdf.add_page()
    pdf.set_margins(25, 25, 25)

    # === Absender ===
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(*BLUE)
    pdf.cell(0, 8, _clean_text(name), new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*GRAY)
    pdf.cell(
        0, 5,
        f"{email}  |  {phone}",
        new_x="LMARGIN", new_y="NEXT",
    )
    pdf.cell(0, 5, _clean_text(sender_location), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)

    # === Empfaenger ===
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*DARK)
    pdf.cell(0, 5, _clean_text(company), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, _clean_text(company_location), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)

    # === Datum ===
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*GRAY)
    pdf.cell(0, 5, _format_date_german(), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)

    # === Betreff ===
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*DARK)
    pdf.cell(0, 6, _clean_text(letter.subject), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)

    # === Brieftext ===
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(*DARK)
    clean_body = _clean_text(letter.body)
    pdf.multi_cell(0, 6, clean_body)
    pdf.ln(12)

    # === Grussformel ===
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 6, "Mit freundlichen Gruessen", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 6, _clean_text(name), new_x="LMARGIN", new_y="NEXT")

    # Output
    buf = io.BytesIO()
    pdf.output(buf)
    pdf_bytes = buf.getvalue()

    logger.info(
        "Cover letter PDF rendered",
        extra={"size_bytes": len(pdf_bytes)},
    )
    return pdf_bytes
