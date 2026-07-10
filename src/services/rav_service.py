"""RAV-Nachweis Service — generiert das offizielle Formular 716.007.

Erstellt das Schweizer RAV-Formular 'Nachweis der persoenlichen
Arbeitsbemuehungen' als PDF, befuellt mit Bewerbungsdaten aus der DB.

Zusaetzlich wird eine eigene Monats-Uebersicht als zweites PDF erstellt.
"""

import io
import logging
from datetime import datetime, timezone

from fpdf import FPDF

from src.models.application import Application
from src.models.job import Job

logger = logging.getLogger(__name__)

# Layout-Konstanten
DARK = (0, 0, 0)
GRAY = (100, 100, 100)
LIGHT_GRAY = (200, 200, 200)
TABLE_GRAY = (240, 240, 240)

# Spaltenbreiten fuer RAV-Tabelle (A4 = 210mm, Raender 10mm links/rechts = 190mm)
# Datum | Firma/Adresse | Stelle | RAV | VZ | TZ | Br | Pe | Te | offen | VG | An | Ab | Grund
COL_DATUM = 14       # Tag Monat
COL_FIRMA = 42       # Firma, Adresse
COL_STELLE = 30      # Stellenbezeichnung
COL_CHECK = 8        # Checkbox-Spalten (9 Stueck)
COL_GRUND = 24       # Absagegrund

ROW_HEIGHT = 16       # Zeilenhoehe fuer Datenzeilen
HEADER_HEIGHT = 28    # Header-Zeilenhoehe

MONTHS_DE = [
    "", "Januar", "Februar", "Maerz", "April", "Mai", "Juni",
    "Juli", "August", "September", "Oktober", "November", "Dezember",
]


def _clean(text: str) -> str:
    """Replace unsupported Unicode chars for Helvetica."""
    replacements = {
        "–": "-", "—": "-", "'": "'", "'": "'",
        "“": '"', "”": '"', "•": "-", "…": "...",
        "«": '"', "»": '"', "​": "", "\t": "    ",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def _status_to_rav(status: str) -> dict[str, bool]:
    """Map application status to RAV result checkboxes."""
    return {
        "noch_offen": status in ("found", "cv_generated", "review", "sent"),
        "vorstellungsgespraech": status == "interview",
        "anstellung": status == "offer",
        "absage": status == "rejected",
    }


def _draw_checkbox(pdf: FPDF, x: float, y: float, checked: bool) -> None:
    """Draw a small checkbox (checked = X)."""
    size = 3.5
    cx = x + (COL_CHECK - size) / 2
    cy = y + (ROW_HEIGHT - size) / 2
    pdf.rect(cx, cy, size, size)
    if checked:
        pdf.set_font("Helvetica", "B", 8)
        pdf.text(cx + 0.5, cy + size - 0.3, "X")


class RAVDocument(FPDF):
    """RAV Formular 716.007 — Nachweis der persoenlichen Arbeitsbemuehungen."""

    def __init__(
        self,
        name: str,
        ahv_nr: str,
        month: int,
        year: int,
    ) -> None:
        """Initialize RAV document with header data."""
        super().__init__(orientation="L", unit="mm", format="A4")
        self.applicant_name = name
        self.ahv_nr = ahv_nr
        self.month = month
        self.year = year
        self.set_auto_page_break(auto=False)

    def header(self) -> None:
        """Draw the RAV form header."""
        # Formular-Nummer
        self.set_font("Helvetica", "", 7)
        self.set_text_color(*GRAY)
        self.text(10, 8, "716.007 d 09.2019")

        # Titel
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*DARK)
        self.text(10, 14, "Arbeitslosenversicherung")

        self.set_font("Helvetica", "", 7)
        self.text(120, 12, "Einzureichen beim RAV")
        self.text(120, 16, "bis spaetestens am 5. Tag des Folgemonats")

        self.set_font("Helvetica", "B", 11)
        self.text(10, 22, "Nachweis der persoenlichen Arbeitsbemuehungen")

        # Name, AHV-Nr, Monat
        self.set_font("Helvetica", "", 8)
        y_info = 28
        self.text(10, y_info, "Name und Vorname:")
        self.set_font("Helvetica", "B", 9)
        self.text(45, y_info, _clean(self.applicant_name))

        self.set_font("Helvetica", "", 8)
        self.text(120, y_info, "AHV-Nr.:")
        self.set_font("Helvetica", "B", 9)
        self.text(140, y_info, self.ahv_nr)

        self.set_font("Helvetica", "", 8)
        self.text(200, y_info, "Monat und Jahr:")
        self.set_font("Helvetica", "B", 9)
        monat_text = f"{MONTHS_DE[self.month]} {self.year}"
        self.text(230, y_info, monat_text)

    def footer(self) -> None:
        """No automatic footer."""

    def draw_table_header(self, y: float) -> float:
        """Draw the table column headers. Returns y after header."""
        self.set_font("Helvetica", "", 6)
        self.set_text_color(*DARK)
        self.set_draw_color(*DARK)
        self.set_line_width(0.3)

        x = 10

        # Hauptgruppen-Header
        self.rect(x, y, COL_DATUM, HEADER_HEIGHT)
        self.rect(x + COL_DATUM, y, COL_FIRMA, HEADER_HEIGHT)
        self.rect(x + COL_DATUM + COL_FIRMA, y, COL_STELLE, HEADER_HEIGHT)

        # Zuweisung RAV
        x_check = x + COL_DATUM + COL_FIRMA + COL_STELLE
        self.rect(x_check, y, COL_CHECK, HEADER_HEIGHT)

        # Pensum (2 Spalten)
        self.rect(x_check + COL_CHECK, y, COL_CHECK * 2, HEADER_HEIGHT)

        # Bewerbung (3 Spalten)
        self.rect(x_check + COL_CHECK * 3, y, COL_CHECK * 3, HEADER_HEIGHT)

        # Ergebnis (4 Spalten + Grund)
        x_erg = x_check + COL_CHECK * 6
        self.rect(x_erg, y, COL_CHECK * 4 + COL_GRUND, HEADER_HEIGHT)

        # Texte
        self.set_font("Helvetica", "", 6)
        self.text(x + 1, y + 5, "Datum der")
        self.text(x + 1, y + 9, "Bewerbung")
        self.text(x + 1, y + 16, "Tag  Monat")

        self.text(x + COL_DATUM + 1, y + 5, "Firma, Adresse")
        self.text(x + COL_DATUM + 1, y + 9, "Kontaktperson, Tel.")

        self.text(x + COL_DATUM + COL_FIRMA + 1, y + 5, "Stellen-")
        self.text(x + COL_DATUM + COL_FIRMA + 1, y + 9, "bezeichnung")

        # Vertikale Labels fuer Checkboxen
        self._vertical_label(x_check, y, "Zuweis. RAV")
        self._vertical_label(x_check + COL_CHECK, y, "Vollzeit")
        self._vertical_label(x_check + COL_CHECK * 2, y, "Teilzeit (%)")
        self._vertical_label(x_check + COL_CHECK * 3, y, "Briefl./elektr.")
        self._vertical_label(x_check + COL_CHECK * 4, y, "Persoenlich")
        self._vertical_label(x_check + COL_CHECK * 5, y, "Telefonisch")
        self._vertical_label(x_check + COL_CHECK * 6, y, "noch offen")
        self._vertical_label(x_check + COL_CHECK * 7, y, "Vorst.gespr.")
        self._vertical_label(x_check + COL_CHECK * 8, y, "Anstellung")
        self._vertical_label(x_check + COL_CHECK * 9, y, "Absage")

        self.set_font("Helvetica", "", 6)
        self.text(x_check + COL_CHECK * 10 + 1, y + 14, "Absagegrund")

        # Gruppenheader
        self.set_font("Helvetica", "", 5)
        self.text(x_check + COL_CHECK + 1, y + 2, "Pensum")
        self.text(x_check + COL_CHECK * 3 + 2, y + 2, "Bewerbung")
        self.text(x_erg + 2, y + 2, "Ergebnis der Bewerbung")

        return y + HEADER_HEIGHT

    def _vertical_label(self, x: float, y: float, text: str) -> None:
        """Draw rotated text label in column header."""
        self.set_font("Helvetica", "", 5)
        # Simulate vertical text with small horizontal text
        self.text(x + 1.5, y + HEADER_HEIGHT - 2, text[:12])

    def draw_data_row(
        self,
        y: float,
        day: str,
        month_str: str,
        firma: str,
        stelle: str,
        vollzeit: bool = True,
        teilzeit_pct: str = "",
        brieflich: bool = True,
        persoenlich: bool = False,
        telefonisch: bool = False,
        noch_offen: bool = True,
        vorstellungsgespraech: bool = False,
        anstellung: bool = False,
        absage: bool = False,
        absagegrund: str = "",
    ) -> float:
        """Draw one application row. Returns y after row."""
        x = 10
        self.set_draw_color(*DARK)
        self.set_line_width(0.2)

        # Alle Zellen zeichnen
        x_pos = x
        widths = [
            COL_DATUM, COL_FIRMA, COL_STELLE,
            COL_CHECK,  # RAV
            COL_CHECK, COL_CHECK,  # Pensum
            COL_CHECK, COL_CHECK, COL_CHECK,  # Bewerbung
            COL_CHECK, COL_CHECK, COL_CHECK, COL_CHECK,  # Ergebnis
            COL_GRUND,  # Absagegrund
        ]
        for w in widths:
            self.rect(x_pos, y, w, ROW_HEIGHT)
            x_pos += w

        # Datum
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*DARK)
        self.text(x + 1, y + ROW_HEIGHT / 2 + 1, f"{day}  {month_str}")

        # Firma (mehrzeilig, gekuerzt)
        self.set_font("Helvetica", "", 7)
        firma_clean = _clean(firma)[:55]
        self.text(x + COL_DATUM + 1, y + ROW_HEIGHT / 2 + 1, firma_clean)

        # Stelle
        stelle_clean = _clean(stelle)[:35]
        self.text(
            x + COL_DATUM + COL_FIRMA + 1,
            y + ROW_HEIGHT / 2 + 1,
            stelle_clean,
        )

        # Checkboxen
        x_check = x + COL_DATUM + COL_FIRMA + COL_STELLE
        # Zuweisung RAV — immer leer (nicht via RAV zugewiesen)
        _draw_checkbox(self, x_check, y, False)
        # Pensum
        _draw_checkbox(self, x_check + COL_CHECK, y, vollzeit)
        if not vollzeit and teilzeit_pct:
            self.set_font("Helvetica", "", 6)
            self.text(x_check + COL_CHECK * 2 + 1, y + ROW_HEIGHT / 2 + 1, teilzeit_pct)
        _draw_checkbox(self, x_check + COL_CHECK * 2, y, not vollzeit)
        # Bewerbung
        _draw_checkbox(self, x_check + COL_CHECK * 3, y, brieflich)
        _draw_checkbox(self, x_check + COL_CHECK * 4, y, persoenlich)
        _draw_checkbox(self, x_check + COL_CHECK * 5, y, telefonisch)
        # Ergebnis
        _draw_checkbox(self, x_check + COL_CHECK * 6, y, noch_offen)
        _draw_checkbox(self, x_check + COL_CHECK * 7, y, vorstellungsgespraech)
        _draw_checkbox(self, x_check + COL_CHECK * 8, y, anstellung)
        _draw_checkbox(self, x_check + COL_CHECK * 9, y, absage)

        # Absagegrund
        if absagegrund:
            self.set_font("Helvetica", "", 6)
            self.text(
                x_check + COL_CHECK * 10 + 1,
                y + ROW_HEIGHT / 2 + 1,
                _clean(absagegrund)[:30],
            )

        return y + ROW_HEIGHT

    def draw_empty_row(self, y: float) -> float:
        """Draw an empty row for manual entries."""
        x = 10
        self.set_draw_color(*LIGHT_GRAY)
        self.set_line_width(0.2)

        x_pos = x
        widths = [
            COL_DATUM, COL_FIRMA, COL_STELLE,
            COL_CHECK, COL_CHECK, COL_CHECK,
            COL_CHECK, COL_CHECK, COL_CHECK,
            COL_CHECK, COL_CHECK, COL_CHECK, COL_CHECK,
            COL_GRUND,
        ]
        for w in widths:
            self.rect(x_pos, y, w, ROW_HEIGHT)
            x_pos += w

        return y + ROW_HEIGHT

    def draw_footer_section(self, y: float) -> None:
        """Draw the date/signature section."""
        y += 8
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*DARK)
        self.text(10, y, "Datum: ___________________________")
        self.text(160, y, "Unterschrift der versicherten Person:")
        self.text(10, y + 8, "Beilagen: ________________________")
        self.text(
            160, y + 8,
            "___________________________________",
        )


def render_rav_nachweis(
    applications: list[tuple[Application, Job]],
    name: str,
    ahv_nr: str,
    month: int,
    year: int,
) -> bytes:
    """Render the official RAV form 716.007 as PDF.

    Args:
        applications: List of (Application, Job) tuples for the month.
        name: Applicant name.
        ahv_nr: AHV number (Swiss social security).
        month: Month number (1-12).
        year: Year.

    Returns:
        PDF file as bytes.
    """
    pdf = RAVDocument(name=name, ahv_nr=ahv_nr, month=month, year=year)
    rows_per_page_1 = 8
    rows_per_page_2 = 6

    # Seite 1
    pdf.add_page()
    y = pdf.draw_table_header(34)

    for i in range(rows_per_page_1):
        if i < len(applications):
            app, job = applications[i]
            result = _status_to_rav(app.status)
            created = app.created_at or datetime.now(timezone.utc)
            pdf.draw_data_row(
                y=y,
                day=str(created.day).zfill(2),
                month_str=str(created.month).zfill(2),
                firma=job.company if job else "Unbekannt",
                stelle=job.title if job else "Unbekannt",
                vollzeit=True,
                brieflich=True,
                **result,
            )
        else:
            pdf.draw_empty_row(y)
        y += ROW_HEIGHT

    # Seite 2 (falls noetig oder fuer leere Zeilen)
    if len(applications) > rows_per_page_1 or True:  # Immer Seite 2
        pdf.add_page()
        y = pdf.draw_table_header(12)

        for i in range(rows_per_page_2):
            idx = rows_per_page_1 + i
            if idx < len(applications):
                app, job = applications[idx]
                result = _status_to_rav(app.status)
                created = app.created_at or datetime.now(timezone.utc)
                pdf.draw_data_row(
                    y=y,
                    day=str(created.day).zfill(2),
                    month_str=str(created.month).zfill(2),
                    firma=job.company if job else "Unbekannt",
                    stelle=job.title if job else "Unbekannt",
                    vollzeit=True,
                    brieflich=True,
                    **result,
                )
            else:
                pdf.draw_empty_row(y)
            y += ROW_HEIGHT

        pdf.draw_footer_section(y)

        # Hinweis-Text
        y += 20
        pdf.set_font("Helvetica", "B", 7)
        pdf.text(10, y, "Hinweis")
        pdf.set_font("Helvetica", "", 6)
        y += 5
        hinweis = (
            "Die versicherte Person muss alles Zumutbare unternehmen, um "
            "Arbeitslosigkeit zu vermeiden oder zu verkuerzen. Insbesondere ist "
            "es ihre Sache, Arbeit zu suchen, wenn noetig auch ausserhalb ihres "
            "bisherigen Berufes (Art. 17 AVIG)."
        )
        pdf.set_xy(10, y)
        pdf.multi_cell(270, 3.5, hinweis)

    buf = io.BytesIO()
    pdf.output(buf)
    pdf_bytes = buf.getvalue()

    logger.info(
        "RAV-Nachweis PDF erstellt",
        extra={
            "month": month,
            "year": year,
            "applications_count": len(applications),
            "size_bytes": len(pdf_bytes),
        },
    )
    return pdf_bytes


def render_monthly_overview(
    applications: list[tuple[Application, Job]],
    name: str,
    month: int,
    year: int,
) -> bytes:
    """Render a clean monthly overview as PDF.

    Eigene Uebersicht aller Bewerbungen — nicht das offizielle Formular,
    sondern eine saubere Liste fuer die eigene Dokumentation.

    Args:
        applications: List of (Application, Job) tuples.
        name: Applicant name.
        month: Month (1-12).
        year: Year.

    Returns:
        PDF as bytes.
    """
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    pdf.set_margins(15, 15, 15)

    # Titel
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(13, 71, 161)
    pdf.cell(
        0, 10,
        f"Bewerbungsuebersicht {MONTHS_DE[month]} {year}",
        new_x="LMARGIN", new_y="NEXT",
    )

    # Name
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*GRAY)
    pdf.cell(0, 6, _clean(name), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # Zusammenfassung
    total = len(applications)
    offen = sum(1 for a, _ in applications if a.status in ("found", "cv_generated", "review", "sent"))
    interview = sum(1 for a, _ in applications if a.status == "interview")
    abgesagt = sum(1 for a, _ in applications if a.status == "rejected")
    angestellt = sum(1 for a, _ in applications if a.status == "offer")

    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*DARK)
    pdf.cell(0, 6, f"Total: {total} Bewerbungen", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(
        0, 5,
        f"Offen: {offen}  |  Vorstellungsgespraech: {interview}  |  "
        f"Absage: {abgesagt}  |  Anstellung: {angestellt}",
        new_x="LMARGIN", new_y="NEXT",
    )
    pdf.ln(6)

    # Tabelle
    pdf.set_draw_color(*LIGHT_GRAY)
    pdf.set_line_width(0.3)

    # Header
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_fill_color(*TABLE_GRAY)
    col_w = [18, 55, 55, 30, 22]  # Datum, Firma, Stelle, Ort, Status
    headers = ["Datum", "Firma", "Stelle", "Ort", "Status"]
    for i, h in enumerate(headers):
        pdf.cell(col_w[i], 7, h, border=1, fill=True)
    pdf.ln()

    # Status-Labels
    status_labels = {
        "found": "Offen",
        "cv_generated": "CV erstellt",
        "review": "In Pruefung",
        "sent": "Gesendet",
        "interview": "Gespraech",
        "rejected": "Absage",
        "offer": "Angebot",
    }

    # Datenzeilen
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(*DARK)
    for app, job in applications:
        created = app.created_at or datetime.now(timezone.utc)
        datum = f"{created.day:02d}.{created.month:02d}.{created.year}"
        firma = _clean(job.company if job else "-")[:30]
        stelle = _clean(job.title if job else "-")[:30]
        ort = _clean(job.location if job else "-")[:18]
        status = status_labels.get(app.status, app.status)

        pdf.cell(col_w[0], 6, datum, border=1)
        pdf.cell(col_w[1], 6, firma, border=1)
        pdf.cell(col_w[2], 6, stelle, border=1)
        pdf.cell(col_w[3], 6, ort, border=1)
        pdf.cell(col_w[4], 6, status, border=1)
        pdf.ln()

    if not applications:
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(*GRAY)
        pdf.ln(4)
        pdf.cell(0, 6, "Keine Bewerbungen in diesem Monat.", new_x="LMARGIN", new_y="NEXT")

    # Erstellungsdatum
    pdf.ln(10)
    pdf.set_font("Helvetica", "", 7)
    pdf.set_text_color(*GRAY)
    now = datetime.now(timezone.utc)
    pdf.cell(
        0, 4,
        f"Erstellt am {now.day:02d}.{now.month:02d}.{now.year} "
        f"mit Alpine Career Bot",
    )

    buf = io.BytesIO()
    pdf.output(buf)
    pdf_bytes = buf.getvalue()

    logger.info(
        "Monatsuebersicht PDF erstellt",
        extra={
            "month": month,
            "year": year,
            "applications_count": len(applications),
            "size_bytes": len(pdf_bytes),
        },
    )
    return pdf_bytes
