"""Gmail service — send application emails with PDF attachments.

Uses Gmail API with OAuth2 for Marcos Gmail account (m.vonburg94@gmail.com).
Token is stored encrypted in the database (Application.gmail_message_id
tracks the sent message for later reply detection).

Setup:
1. Google Cloud Console: Create OAuth2 credentials (Desktop App)
2. Download credentials.json → set GMAIL_CREDENTIALS_FILE in .env
3. First run: opens browser for authorization, stores token
4. Token refresh is automatic

IMPORTANT: No credentials or tokens are ever logged or stored in code.
"""

import base64
import logging
import pickle
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from src.models.application import Application
from src.models.job import Job

logger = logging.getLogger(__name__)

# Scopes fuer Gmail API — nur Senden
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

# Token-Datei — wird beim ersten OAuth2-Flow erstellt
TOKEN_PATH = Path("/app/data/gmail_token.pickle")


def _get_gmail_service():
    """Build Gmail API service with OAuth2 credentials.

    Token must be pre-generated via scripts/gmail_auth.py.
    This function only loads and refreshes existing tokens.

    Returns:
        Gmail API service object.

    Raises:
        RuntimeError: If no valid token is available.
    """
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    creds = None

    # Token laden falls vorhanden
    if TOKEN_PATH.exists():
        with open(TOKEN_PATH, "rb") as f:
            creds = pickle.load(f)

    # Token erneuern (kein Browser-Flow auf dem Server!)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Erneuerten Token speichern
            TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(TOKEN_PATH, "wb") as f:
                pickle.dump(creds, f)
        else:
            raise RuntimeError(
                "Kein gueltiger Gmail-Token vorhanden. "
                "Bitte lokal 'python scripts/gmail_auth.py' ausfuehren "
                "und den Token auf den Server kopieren. "
                "Siehe scripts/gmail_auth.py fuer Details."
            )

    return build("gmail", "v1", credentials=creds)



# Verzeichnis fuer statische Anhaenge (Zeugnisse, Diplome, Zertifikate)
ZEUGNISSE_DIR = Path("/app/data/zeugnisse")


def _is_swiss_job(location: str) -> bool:
    """Determine if a job is in Switzerland based on location string."""
    ch_markers = [
        "zürich", "zurich", "zuerich", "bern", "basel", "luzern", "lucerne",
        "schweiz", "switzerland", "swiss", "genf", "geneva", "lausanne",
        "winterthur", "st. gallen", "st.gallen", "aargau", "solothurn",
        "zug", "thun", "aarau", "schaffhausen", "chur", "baden",
    ]
    loc_lower = location.lower()
    return any(marker in loc_lower for marker in ch_markers)


def _load_zeugnisse(job_location: str = "") -> list[tuple[str, bytes]]:
    """Load Arbeitszeugnisse PDFs from the Zeugnisse directory.

    Lebenslaeufe werden NICHT geladen — sie werden separat als
    CV-Anhang von application_service.py behandelt.
    Nur Arbeitszeugnisse, Diplome und Zertifikate werden hier geladen.

    Args:
        job_location: Job-Standort (nicht mehr fuer Filterung benoetigt).

    Returns:
        List of (filename, pdf_bytes) tuples.
    """
    if not ZEUGNISSE_DIR.exists():
        logger.info("Kein Zeugnisse-Verzeichnis vorhanden")
        return []

    zeugnisse: list[tuple[str, bytes]] = []
    for pdf_file in sorted(ZEUGNISSE_DIR.glob("*.pdf")):
        name_lower = pdf_file.name.lower()

        # Lebenslauf ueberspringen — wird separat als CV angehaengt
        if "lebenslauf" in name_lower:
            logger.info(
                "Lebenslauf uebersprungen (wird separat angehaengt)",
                extra={"pdf_name": pdf_file.name},
            )
            continue

        try:
            zeugnisse.append((pdf_file.name, pdf_file.read_bytes()))
            logger.info(
                "Zeugnis geladen",
                extra={"pdf_name": pdf_file.name, "size": pdf_file.stat().st_size},
            )
        except Exception as exc:
            logger.error(
                "Zeugnis konnte nicht geladen werden",
                extra={"pdf_name": pdf_file.name, "error": str(exc)},
            )

    return zeugnisse


def _build_email(
    sender: str,
    to: str,
    subject: str,
    body: str,
    cv_pdf: bytes,
    cover_letter_pdf: bytes,
    applicant_name: str,
    company: str,
    job_location: str = "",
) -> str:
    """Build a MIME email with PDF attachments.

    Attaches: CV, Anschreiben, plus region-filtered PDFs from /app/data/zeugnisse/.

    Returns:
        Base64url-encoded email string for Gmail API.
    """
    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = to
    msg["Subject"] = subject

    # E-Mail-Body
    msg.attach(MIMEText(body, "plain", "utf-8"))

    # Lebenslauf als Anhang (hochgeladenes Original-PDF)
    cv_attachment = MIMEApplication(cv_pdf, _subtype="pdf")
    cv_filename = f"Lebenslauf_{applicant_name.replace(' ', '_')}.pdf"
    cv_attachment.add_header(
        "Content-Disposition", "attachment", filename=cv_filename
    )
    msg.attach(cv_attachment)

    # Anschreiben als Anhang
    letter_attachment = MIMEApplication(cover_letter_pdf, _subtype="pdf")
    letter_filename = f"Anschreiben_{applicant_name.replace(' ', '_')}_{company}.pdf"
    letter_attachment.add_header(
        "Content-Disposition", "attachment", filename=letter_filename
    )
    msg.attach(letter_attachment)

    # Zeugnisse, Diplome, Zertifikate — regional gefiltert
    zeugnisse = _load_zeugnisse(job_location=job_location)
    for filename, pdf_bytes in zeugnisse:
        zeugnis_attachment = MIMEApplication(pdf_bytes, _subtype="pdf")
        zeugnis_attachment.add_header(
            "Content-Disposition", "attachment", filename=filename
        )
        msg.attach(zeugnis_attachment)

    if zeugnisse:
        logger.info(
            "Zeugnisse angehaengt",
            extra={"count": len(zeugnisse)},
        )

    # Base64url encoding fuer Gmail API
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
    return raw


EMAIL_BODY_FALLBACK = """\
Sehr geehrte Damen und Herren,

anbei erhalten Sie meine Bewerbungsunterlagen fuer die ausgeschriebene Position \
als {job_title} bei {company}.

Im Anhang finden Sie meinen Lebenslauf sowie mein Bewerbungsanschreiben.

Ich freue mich auf Ihre Rueckmeldung.

Mit freundlichen Gruessen
{name}
"""


async def send_application_email(
    application: Application,
    job: Job | None = None,
    sender_name: str = "",
    sender_email: str = "",
) -> str:
    """Send application email via Gmail API.

    Args:
        application: Application with PDFs and email data.
        job: Job posting (for metadata).
        sender_name: Applicant name (from DB, not hardcoded).
        sender_email: Sender Gmail address (from DB, not hardcoded).

    Returns:
        Gmail message ID.

    Raises:
        RuntimeError: If Gmail is not configured.
        ValueError: If application has no PDFs.
    """
    import asyncio

    from src.core.database import async_session_factory
    from src.models.user import User

    if not application.cv_pdf or not application.cover_letter_pdf:
        raise ValueError("Bewerbung hat keine generierten PDFs")

    # Absender-Daten aus DB laden falls nicht uebergeben
    if not sender_name or not sender_email:
        async with async_session_factory() as session:
            user = await session.get(User, application.user_id)
            if user:
                sender_name = sender_name or user.name
                sender_email = sender_email or user.email or ""

    if not sender_email:
        raise ValueError("Keine Absender-E-Mail konfiguriert")

    recipient = application.email_to
    if not recipient:
        raise ValueError(
            "Keine Empfaenger-Adresse gesetzt. "
            "Bitte setze email_to in der Bewerbung."
        )

    job_title = job.title if job else "Fachkraft"
    company = job.company if job else "Ihr Unternehmen"

    # E-Mail-Body: Kurze Begleitnotiz (Anschreiben ist als PDF im Anhang)
    body = EMAIL_BODY_FALLBACK.format(
        job_title=job_title,
        company=company,
        name=sender_name,
    )

    subject = application.email_subject or f"Bewerbung als {job_title}"

    job_location = job.location if job else ""

    raw_email = _build_email(
        sender=sender_email,
        to=recipient,
        subject=subject,
        body=body,
        cv_pdf=application.cv_pdf,
        cover_letter_pdf=application.cover_letter_pdf,
        applicant_name=sender_name,
        company=company,
        job_location=job_location,
    )

    # Gmail API aufrufen (synchron → Thread)
    service = _get_gmail_service()
    result = await asyncio.to_thread(
        service.users().messages().send(
            userId="me",
            body={"raw": raw_email},
        ).execute
    )

    message_id = result.get("id", "")
    logger.info(
        "Application email sent",
        extra={
            "gmail_message_id": message_id,
            "recipient": recipient,
            "subject": subject,
        },
    )

    return message_id
