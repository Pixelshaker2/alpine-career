"""Application service — orchestrates the job application workflow.

Flow:
1. User selects a job (/bewerben [id])
2. Load user profile + job details
3. Claude API optimizes CV for the job
4. Claude API generates cover letter
5. PDF rendering for both documents
6. Store Application record in DB
7. User reviews via /vorschau
8. User confirms send via /senden
"""

import logging
import uuid

from sqlalchemy import select

from src.core.database import async_session_factory
from src.models.application import Application
from src.models.job import Job
from src.models.profile import Profile
from src.models.user import User
from src.services.ai_service import (
    GeneratedCoverLetter,
    GeneratedCV,
    generate_cover_letter,
    optimize_cv,
)
from src.services.pdf_service import render_cover_letter_pdf, render_cv_pdf

logger = logging.getLogger(__name__)


async def create_application(
    user_id: uuid.UUID,
    job_id: uuid.UUID,
) -> Application:
    """Create a full application: optimized CV + cover letter + PDFs.

    Args:
        user_id: The applying user's ID.
        job_id: The target job's ID.

    Returns:
        Application record with generated PDFs.

    Raises:
        ValueError: If user, profile, or job not found.
        RuntimeError: If AI generation fails.
    """
    # 1. Daten laden
    async with async_session_factory() as session:
        user = await session.get(User, user_id)
        if not user:
            raise ValueError("Nutzer nicht gefunden")

        result = await session.execute(
            select(Profile).where(Profile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()
        if not profile:
            raise ValueError("Kein Profil hinterlegt")

        job = await session.get(Job, job_id)
        if not job:
            raise ValueError("Stelle nicht gefunden")

        # Pruefen ob bereits eine Bewerbung existiert
        existing = await session.execute(
            select(Application).where(
                Application.user_id == user_id,
                Application.job_id == job_id,
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError(
                "Fuer diese Stelle existiert bereits eine Bewerbung. "
                "Nutze /vorschau um sie anzusehen."
            )

    # Profildaten extrahieren
    skills = profile.skills or {}
    core_skills = skills.get("core", [])
    target_roles = (profile.target_roles or {}).get("titles_de", [])
    certs_in_progress = skills.get("certifications_in_progress", [])

    # Kontaktdaten aus Profil (nicht hardcoden)
    locations = profile.target_locations or {}
    primary_loc = locations.get("primary", {})
    user_location = primary_loc.get("city", "Berlin")
    user_phone = skills.get("phone", "+41 79 876 38 81")

    logger.info("Generating CV", extra={"job_id": str(job_id)})
    cv = await optimize_cv(
        cv_text=profile.raw_cv_text or "",
        skills=core_skills,
        target_roles=target_roles,
        availability=profile.availability or "",
        job_title=job.title,
        job_company=job.company,
        job_location=job.location,
        job_description=job.description or "",
    )

    # 3. Anschreiben generieren
    logger.info("Generating cover letter", extra={"job_id": str(job_id)})
    letter = await generate_cover_letter(
        name=user.name,
        skills=core_skills,
        certs_in_progress=certs_in_progress,
        cv_summary=cv.summary,
        job_title=job.title,
        job_company=job.company,
        job_location=job.location,
        job_description=job.description or "",
    )

    # 4. PDFs rendern
    logger.info("Rendering PDFs", extra={"job_id": str(job_id)})
    cv_pdf = render_cv_pdf(
        cv=cv,
        name=user.name,
        email=user.email,
        phone=user_phone,
        location=user_location,
    )

    cover_letter_pdf = render_cover_letter_pdf(
        letter=letter,
        name=user.name,
        email=user.email,
        phone=user_phone,
        sender_location=user_location,
        company=job.company,
        company_location=job.location,
    )

    # 5. Application in DB speichern
    async with async_session_factory() as session:
        application = Application(
            user_id=user_id,
            job_id=job_id,
            status="cv_generated",
            cv_pdf=cv_pdf,
            cover_letter_pdf=cover_letter_pdf,
            email_subject=letter.subject,
            email_body=letter.body,
        )
        session.add(application)
        await session.commit()
        await session.refresh(application)

    logger.info(
        "Application created",
        extra={
            "application_id": str(application.id),
            "job_title": job.title,
            "cv_pdf_size": len(cv_pdf),
            "letter_pdf_size": len(cover_letter_pdf),
        },
    )

    return application


async def create_application_with_feedback(
    user_id: uuid.UUID,
    job_id: uuid.UUID,
    feedback: str,
    email_to: str | None = None,
) -> Application:
    """Recreate application with user feedback incorporated.

    Same as create_application but adds feedback to the AI prompts.

    Args:
        user_id: The applying user's ID.
        job_id: The target job's ID.
        feedback: User feedback like "formeller" or "mehr Azure".
        email_to: Preserved recipient email from previous version.

    Returns:
        New Application record with regenerated PDFs.
    """
    # 1. Daten laden
    async with async_session_factory() as session:
        user = await session.get(User, user_id)
        if not user:
            raise ValueError("Nutzer nicht gefunden")

        result = await session.execute(
            select(Profile).where(Profile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()
        if not profile:
            raise ValueError("Kein Profil hinterlegt")

        job = await session.get(Job, job_id)
        if not job:
            raise ValueError("Stelle nicht gefunden")

    # Profildaten extrahieren
    skills = profile.skills or {}
    core_skills = skills.get("core", [])
    target_roles = (profile.target_roles or {}).get("titles_de", [])
    certs_in_progress = skills.get("certifications_in_progress", [])

    # Kontaktdaten aus Profil
    locations = profile.target_locations or {}
    primary_loc = locations.get("primary", {})
    user_location = primary_loc.get("city", "Berlin")
    user_phone = skills.get("phone", "+41 79 876 38 81")

    # Feedback an die Job-Beschreibung anhaengen damit Claude es beruecksichtigt
    enhanced_description = (
        f"{job.description or ''}\n\n"
        f"WICHTIG — Feedback vom Bewerber zur Anpassung:\n{feedback}"
    )

    logger.info(
        "Regenerating CV with feedback",
        extra={"job_id": str(job_id), "feedback": feedback},
    )

    cv = await optimize_cv(
        cv_text=profile.raw_cv_text or "",
        skills=core_skills,
        target_roles=target_roles,
        availability=profile.availability or "",
        job_title=job.title,
        job_company=job.company,
        job_location=job.location,
        job_description=enhanced_description,
    )

    # 3. Anschreiben mit Feedback
    letter = await generate_cover_letter(
        name=user.name,
        skills=core_skills,
        certs_in_progress=certs_in_progress,
        cv_summary=cv.summary,
        job_title=job.title,
        job_company=job.company,
        job_location=job.location,
        job_description=enhanced_description,
    )

    # 4. PDFs rendern
    cv_pdf = render_cv_pdf(
        cv=cv,
        name=user.name,
        email=user.email,
        phone=user_phone,
        location=user_location,
    )

    cover_letter_pdf = render_cover_letter_pdf(
        letter=letter,
        name=user.name,
        email=user.email,
        phone=user_phone,
        sender_location=user_location,
        company=job.company,
        company_location=job.location,
    )

    # 5. Neue Application speichern
    async with async_session_factory() as session:
        application = Application(
            user_id=user_id,
            job_id=job_id,
            status="cv_generated",
            cv_pdf=cv_pdf,
            cover_letter_pdf=cover_letter_pdf,
            email_subject=letter.subject,
            email_body=letter.body,
            email_to=email_to,
        )
        session.add(application)
        await session.commit()
        await session.refresh(application)

    logger.info(
        "Application regenerated with feedback",
        extra={
            "application_id": str(application.id),
            "feedback": feedback,
        },
    )

    return application


async def get_application(
    user_id: uuid.UUID,
    application_id: uuid.UUID,
) -> Application | None:
    """Load an application by ID, ensuring it belongs to the user."""
    async with async_session_factory() as session:
        result = await session.execute(
            select(Application).where(
                Application.id == application_id,
                Application.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()


async def get_application_by_job(
    user_id: uuid.UUID,
    job_id: uuid.UUID,
) -> Application | None:
    """Load an application by job ID."""
    async with async_session_factory() as session:
        result = await session.execute(
            select(Application).where(
                Application.user_id == user_id,
                Application.job_id == job_id,
            )
        )
        return result.scalar_one_or_none()


async def update_application_status(
    application_id: uuid.UUID,
    new_status: str,
) -> Application:
    """Update application status."""
    valid_statuses = {
        "found", "cv_generated", "review", "sent",
        "interview", "rejected", "offer",
    }
    if new_status not in valid_statuses:
        raise ValueError(
            f"Ungueltiger Status: {new_status}. "
            f"Erlaubt: {', '.join(sorted(valid_statuses))}"
        )

    async with async_session_factory() as session:
        app = await session.get(Application, application_id)
        if not app:
            raise ValueError("Bewerbung nicht gefunden")
        app.status = new_status
        await session.commit()
        await session.refresh(app)
        return app
