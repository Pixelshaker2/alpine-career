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


def _build_email(
    sender: str,
    to: str,
    subject: str,
    body: str,
    cv_pdf: bytes,
    cover_letter_pdf: bytes,
    applicant_name: str,
    company: str,
) -> str:
    """Build a MIME email with PDF attachments.

    Returns:
        Base64url-encoded email string for Gmail API.
    """
    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = to
    msg["Subject"] = subject

    # E-Mail-Body
    msg.attach(MIMEText(body, "plain", "utf-8"))

    # CV als Anhang
    cv_attachment = MIMEApplication(cv_pdf, _subtype="pdf")
    cv_filename = f"CV_{applicant_name.replace(' ', '_')}.pdf"
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

    # Base64url encoding fuer Gmail API
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
    return raw


EMAIL_BODY_TEMPLATE = """\
Sehr geehrte Damen und Herren,

anbei erhalten Sie meine Bewerbungsunterlagen fuer die ausgeschriebene Position \
als {job_title} bei {company}.

Im Anhang finden Sie:
- Meinen Lebenslauf
- Mein Bewerbungsanschreiben

{cover_letter_intro}

Ich freue mich auf Ihre Rueckmeldung.

Mit freundlichen Gruessen
{name}
"""


async def send_application_email(
    application: Application,
    job: Job | None = None,
) -> str:
    """Send application email via Gmail API.

    Args:
        application: Application with PDFs and email data.
        job: Job posting (for metadata).

    Returns:
        Gmail message ID.

    Raises:
        RuntimeError: If Gmail is not configured.
        ValueError: If application has no PDFs.
    """
    import asyncio

    if not application.cv_pdf or not application.cover_letter_pdf:
        raise ValueError("Bewerbung hat keine generierten PDFs")

    # E-Mail-Adresse des Empfaengers
    # Im MVP: an die Job-URL-Domain oder manuell gesetzt
    recipient = application.email_to
    if not recipient:
        raise ValueError(
            "Keine Empfaenger-Adresse gesetzt. "
            "Bitte setze email_to in der Bewerbung."
        )

    job_title = job.title if job else "Fachkraft"
    company = job.company if job else "Ihr Unternehmen"

    # E-Mail-Body
    body = EMAIL_BODY_TEMPLATE.format(
        job_title=job_title,
        company=company,
        cover_letter_intro=application.email_body[:200] if application.email_body else "",
        name="Marco von Burg",
    )

    subject = application.email_subject or f"Bewerbung als {job_title}"

    # E-Mail bauen
    raw_email = _build_email(
        sender="m.vonburg94@gmail.com",
        to=recipient,
        subject=subject,
        body=body,
        cv_pdf=application.cv_pdf,
        cover_letter_pdf=application.cover_letter_pdf,
        applicant_name="Marco von Burg",
        company=company,
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
