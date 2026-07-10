"""Telegram bot command handlers."""

import io
import logging
import uuid as uuid_mod

from sqlalchemy import select
from telegram import Update
from telegram.ext import ContextTypes

from src.bot.auth import restricted
from src.core.database import async_session_factory
from src.models.application import Application
from src.models.job import Job
from src.models.profile import Profile
from src.models.user import User
from src.services.application_service import (
    create_application,
    get_application_by_job,
    update_application_status,
)
from src.services.job_matcher import score_job, score_jobs
from src.services.job_service import search_and_persist
from src.services.rav_service import render_monthly_overview, render_rav_nachweis

logger = logging.getLogger(__name__)


async def _get_or_create_user(update: Update) -> User | None:
    """Find user by telegram username, update chat_id if needed."""
    username = update.effective_user.username
    chat_id = update.effective_chat.id

    async with async_session_factory() as session:
        result = await session.execute(
            select(User).where(User.telegram_username == username)
        )
        user = result.scalar_one_or_none()

        if user and user.telegram_chat_id != chat_id:
            user.telegram_chat_id = chat_id
            await session.commit()

        return user


@restricted
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start — welcome message and register chat_id."""
    user = await _get_or_create_user(update)
    name = user.name if user else update.effective_user.first_name

    await update.message.reply_text(
        f"Hallo {name}! 👋\n\n"
        "Ich bin dein Alpine Career Bot. Ich helfe dir bei der Jobsuche "
        "in Berlin und der Schweiz.\n\n"
        "Tippe /help fuer alle Befehle."
    )


@restricted
async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help — list all commands."""
    help_text = (
        "📋 *Verfuegbare Befehle:*\n\n"
        "/start — Begruessung\n"
        "/help — Diese Uebersicht\n"
        "/profil — Dein Profil anzeigen\n"
        "/suche — Stellensuche starten\n"
        "/suche berlin — Nur Berlin\n"
        "/suche schweiz — Nur Schweiz\n"
        "/detail \\[id\\] — Stellendetails\n"
        "/bewerben \\[id\\] — CV \\+ Anschreiben generieren\n"
        "/vorschau \\[id\\] — PDFs anzeigen\n"
        "/senden \\[id\\] — Bewerbung per Gmail senden\n"
        "/bewerbungen — Alle Bewerbungen\n"
        "/status \\[id\\] \\[s\\] — Status aendern\n"
        "/stats — Statistik\n"
        "/nachweis \\[monat\\] — RAV\\-Formular\n"
        "/ahv \\[nr\\] — AHV\\-Nr\\. setzen\n"
    )
    await update.message.reply_text(help_text, parse_mode="MarkdownV2")


@restricted
async def cmd_botstatus(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /botstatus — show bot and system status."""
    await update.message.reply_text(
        "✅ Bot laeuft.\n"
        "📊 System-Status:\n"
        "  • Datenbank: verbunden\n"
        "  • Redis: verbunden\n"
        "  • Claude API: bereit\n\n"
        "🔧 Version: 0.1.0 (MVP)"
    )


@restricted
async def cmd_profil(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /profil — show user profile from database."""
    username = update.effective_user.username

    async with async_session_factory() as session:
        result = await session.execute(
            select(User).where(User.telegram_username == username)
        )
        user = result.scalar_one_or_none()

        if not user:
            await update.message.reply_text(
                "Kein Profil gefunden. Bitte wende dich an den Administrator."
            )
            return

        result = await session.execute(
            select(Profile).where(Profile.user_id == user.id)
        )
        profile = result.scalar_one_or_none()

    if not profile:
        await update.message.reply_text(
            "Profil existiert, aber es sind noch keine CV-Daten hinterlegt."
        )
        return

    # Rollen formatieren
    roles = profile.target_roles or {}
    titles_de = roles.get("titles_de", [])
    roles_text = ", ".join(titles_de[:4]) if titles_de else "Nicht gesetzt"

    # Standorte formatieren
    locations = profile.target_locations or {}
    primary = locations.get("primary", {})
    secondary = locations.get("secondary", [])
    loc_parts = []
    if primary:
        loc_parts.append(f"{primary.get('city', '')} (Prioritaet)")
    for loc in secondary[:3]:
        loc_parts.append(loc.get("city", ""))
    locations_text = ", ".join(loc_parts) if loc_parts else "Nicht gesetzt"

    # Gehalt formatieren
    salary = profile.salary_expectations or {}
    salary_parts = []
    if "berlin" in salary:
        s = salary["berlin"]
        salary_parts.append(
            f"Berlin: {s['min']:,}–{s['max']:,} {s['currency']} "
            f"(Ziel {s['target']:,})"
        )
    if "schweiz" in salary:
        s = salary["schweiz"]
        salary_parts.append(
            f"Schweiz: {s['min']:,}–{s['max']:,} {s['currency']} "
            f"(Ziel {s['target']:,})"
        )
    salary_text = "\n  ".join(salary_parts) if salary_parts else "Nicht gesetzt"

    # Skills formatieren
    skills = profile.skills or {}
    core_skills = skills.get("core", [])
    skills_text = ", ".join(core_skills[:6]) if core_skills else "Nicht gesetzt"

    # Certs formatieren
    certs_in_progress = skills.get("certifications_in_progress", [])
    certs_done = skills.get("certifications_completed", [])
    certs_text = ""
    if certs_in_progress:
        certs_text += "In Arbeit: " + ", ".join(certs_in_progress)
    if certs_done:
        if certs_text:
            certs_text += "\n  "
        certs_text += "Abgeschlossen: " + ", ".join(certs_done)

    # Preferences
    prefs = profile.preferences or {}
    remote_text = "Ja (Full Remote)" if prefs.get("remote") == "full_remote" else "Nein"
    excluded = prefs.get("industries_excluded", [])
    excluded_text = ", ".join(excluded) if excluded else "Keine"

    text = (
        f"👤 Profil: {user.name}\n"
        f"📧 {user.email}\n"
        f"📅 Verfuegbar ab: {profile.availability or 'Nicht gesetzt'}\n\n"
        f"🎯 Zielrollen:\n  {roles_text}\n\n"
        f"📍 Standorte:\n  {locations_text}\n\n"
        f"💰 Gehalt:\n  {salary_text}\n\n"
        f"🔧 Skills:\n  {skills_text}\n\n"
        f"📜 Zertifizierungen:\n  {certs_text}\n\n"
        f"🏠 Remote: {remote_text}\n"
        f"🚫 No-Go Branchen: {excluded_text}"
    )

    await update.message.reply_text(text)


@restricted
async def cmd_suche(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /suche [berlin|schweiz] — search for matching jobs."""
    # Region aus Argument lesen
    region: str | None = None
    if context.args:
        arg = context.args[0].lower()
        if arg in ("berlin", "de", "deutschland"):
            region = "berlin"
        elif arg in ("schweiz", "ch", "swiss"):
            region = "schweiz"

    region_label = {
        "berlin": "Berlin",
        "schweiz": "Schweiz",
        None: "Berlin + Schweiz",
    }[region]

    await update.message.reply_text(
        f"🔍 Suche Stellen in {region_label}...\n"
        "Das kann einen Moment dauern."
    )

    jobs = await search_and_persist(region=region)

    if not jobs:
        await update.message.reply_text(
            "❌ Keine Stellen gefunden. Versuche es spaeter nochmal "
            "oder pruefe /profil fuer deine Suchkriterien."
        )
        return

    # Score und sortieren
    scored = score_jobs(jobs)

    # Ergebnisse in context speichern fuer /detail
    context.user_data["last_search"] = {
        str(i + 1): str(job.id) for i, (job, _score) in enumerate(scored[:20])
    }

    # Quellen zaehlen
    sources = {}
    for job, _ in scored:
        sources[job.source] = sources.get(job.source, 0) + 1
    source_info = ", ".join(f"{s}: {c}" for s, c in sorted(sources.items()))

    lines = [
        f"📋 {len(scored)} Stellen gefunden in {region_label}\n"
        f"🔎 Quellen: {source_info}\n"
    ]
    for i, (job, match_score) in enumerate(scored[:20], 1):
        salary = f" | {job.salary_range}" if job.salary_range else ""
        score_bar = "🟢" if match_score >= 60 else "🟡" if match_score >= 30 else "🔴"
        src_tag = job.source[:3].upper()
        lines.append(
            f"{i}. {score_bar} {job.title} ({match_score:.0f}%)\n"
            f"   🏢 {job.company} | 📍 {job.location} | 🌐 {src_tag}{salary}"
        )

    lines.append(f"\nTippe /detail [Nr] fuer Details (z.B. /detail 1)")

    # Telegram max 4096 Zeichen — aufteilen wenn noetig
    text = "\n".join(lines)
    if len(text) > 4000:
        text = text[:4000] + "\n\n... (weitere Ergebnisse abgeschnitten)"

    await update.message.reply_text(text)


@restricted
async def cmd_detail(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /detail [nr] — show job details."""
    if not context.args:
        await update.message.reply_text(
            "Bitte eine Nummer angeben: /detail 1"
        )
        return

    nr = context.args[0]
    search_map = context.user_data.get("last_search", {})

    if nr not in search_map:
        await update.message.reply_text(
            f"Nr. {nr} nicht gefunden. Starte zuerst eine /suche."
        )
        return

    job_id = search_map[nr]

    async with async_session_factory() as session:
        result = await session.execute(
            select(Job).where(Job.id == job_id)
        )
        job = result.scalar_one_or_none()

    if not job:
        await update.message.reply_text("Stelle nicht mehr in der Datenbank.")
        return

    match_score = score_job(job)
    score_bar = "🟢" if match_score >= 60 else "🟡" if match_score >= 30 else "🔴"
    salary = f"\n💰 Gehalt: {job.salary_range}" if job.salary_range else ""
    desc = job.description or "Keine Beschreibung verfuegbar."
    if len(desc) > 1500:
        desc = desc[:1500] + "..."

    text = (
        f"📌 {job.title}\n"
        f"🏢 {job.company}\n"
        f"📍 {job.location}{salary}\n"
        f"{score_bar} Match: {match_score:.0f}%\n"
        f"🌐 Quelle: {job.source}\n\n"
        f"📝 Beschreibung:\n{desc}\n\n"
        f"🔗 Link: {job.url}"
    )

    await update.message.reply_text(text)


@restricted
async def cmd_bewerben(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /bewerben [nr] — generate CV + cover letter for a job."""
    if not context.args:
        await update.message.reply_text(
            "Bitte eine Nummer angeben: /bewerben 1\n"
            "(Nummern aus der letzten /suche)"
        )
        return

    nr = context.args[0]
    search_map = context.user_data.get("last_search", {})

    if nr not in search_map:
        await update.message.reply_text(
            f"Nr. {nr} nicht gefunden. Starte zuerst eine /suche."
        )
        return

    job_id = uuid_mod.UUID(search_map[nr])
    user = await _get_or_create_user(update)
    if not user:
        await update.message.reply_text("Nutzer nicht gefunden.")
        return

    # Pruefen ob Bewerbung schon existiert
    existing = await get_application_by_job(user.id, job_id)
    if existing:
        await update.message.reply_text(
            "Fuer diese Stelle existiert bereits eine Bewerbung.\n"
            f"Status: {existing.status}\n\n"
            "Nutze /vorschau um die Dokumente anzusehen."
        )
        return

    await update.message.reply_text(
        "🤖 Generiere CV und Anschreiben...\n"
        "Das dauert ca. 30–60 Sekunden."
    )

    try:
        application = await create_application(
            user_id=user.id,
            job_id=job_id,
        )
    except ValueError as exc:
        await update.message.reply_text(f"❌ {exc}")
        return
    except Exception:
        logger.exception("Application generation failed")
        await update.message.reply_text(
            "❌ Fehler bei der Generierung. Bitte versuche es spaeter nochmal."
        )
        return

    # Job-Titel laden fuer die Ausgabe
    async with async_session_factory() as session:
        job = await session.get(Job, job_id)

    job_title = job.title if job else "Unbekannt"

    # Bewerbungs-ID in context speichern
    context.user_data.setdefault("applications", {})[nr] = str(application.id)

    await update.message.reply_text(
        f"✅ Bewerbung fuer «{job_title}» erstellt!\n\n"
        f"📄 CV: optimiert und als PDF generiert\n"
        f"✉️ Anschreiben: erstellt und als PDF generiert\n"
        f"📧 Betreff: {application.email_subject}\n\n"
        f"Naechste Schritte:\n"
        f"  /vorschau {nr} — PDFs ansehen\n"
        f"  /senden {nr} — Per Gmail versenden"
    )


@restricted
async def cmd_vorschau(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /vorschau [nr] — send CV and cover letter PDFs in chat."""
    if not context.args:
        await update.message.reply_text(
            "Bitte eine Nummer angeben: /vorschau 1"
        )
        return

    nr = context.args[0]

    # Versuche Application via gespeicherter ID oder ueber Suchindex
    app_map = context.user_data.get("applications", {})
    search_map = context.user_data.get("last_search", {})

    application = None
    user = await _get_or_create_user(update)
    if not user:
        await update.message.reply_text("Nutzer nicht gefunden.")
        return

    if nr in app_map:
        async with async_session_factory() as session:
            result = await session.execute(
                select(Application).where(Application.id == app_map[nr])
            )
            application = result.scalar_one_or_none()
    elif nr in search_map:
        application = await get_application_by_job(
            user.id, uuid_mod.UUID(search_map[nr])
        )

    if not application:
        await update.message.reply_text(
            f"Keine Bewerbung fuer Nr. {nr} gefunden.\n"
            "Erstelle zuerst eine mit /bewerben."
        )
        return

    if not application.cv_pdf or not application.cover_letter_pdf:
        await update.message.reply_text(
            "Dokumente noch nicht generiert. Bitte /bewerben ausfuehren."
        )
        return

    # Job-Titel laden
    async with async_session_factory() as session:
        job = await session.get(Job, application.job_id)
    job_title = job.title if job else "Stelle"
    company = job.company if job else "Unbekannt"

    # PDFs als Telegram-Dokumente senden
    cv_file = io.BytesIO(application.cv_pdf)
    cv_file.name = f"CV_{user.name.replace(' ', '_')}_{company}.pdf"

    letter_file = io.BytesIO(application.cover_letter_pdf)
    letter_file.name = f"Anschreiben_{user.name.replace(' ', '_')}_{company}.pdf"

    await update.message.reply_text(
        f"📄 Dokumente fuer: {job_title} bei {company}"
    )

    await update.message.reply_document(
        document=cv_file,
        caption="📄 Lebenslauf (optimiert)",
    )

    await update.message.reply_document(
        document=letter_file,
        caption="✉️ Bewerbungsanschreiben",
    )

    await update.message.reply_text(
        f"Zufrieden? Dann sende mit /senden {nr}\n"
        "Oder generiere neu mit /bewerben."
    )


@restricted
async def cmd_senden(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /senden [nr] — send application via Gmail (with confirmation)."""
    if not context.args:
        await update.message.reply_text(
            "Bitte eine Nummer angeben: /senden 1"
        )
        return

    nr = context.args[0]

    # Bestaetigungslogik: erst Vorschau, dann Freigabe
    pending_send = context.user_data.get("pending_send")

    if pending_send and pending_send.get("nr") == nr:
        # Zweiter Aufruf = Bestaetigung
        if len(context.args) > 1 and context.args[1].lower() == "ja":
            # Gmail-Versand ausfuehren
            try:
                from src.services.gmail_service import send_application_email

                application_id = pending_send["application_id"]
                async with async_session_factory() as session:
                    result = await session.execute(
                        select(Application).where(
                            Application.id == application_id
                        )
                    )
                    application = result.scalar_one_or_none()

                    if not application:
                        await update.message.reply_text(
                            "Bewerbung nicht gefunden."
                        )
                        return

                    job = await session.get(Job, application.job_id)

                await send_application_email(application, job)

                # Status aktualisieren
                from datetime import datetime, timezone

                async with async_session_factory() as session:
                    app = await session.get(Application, application_id)
                    app.status = "sent"
                    app.sent_at = datetime.now(timezone.utc)
                    await session.commit()

                context.user_data.pop("pending_send", None)

                await update.message.reply_text(
                    "✅ Bewerbung gesendet!\n\n"
                    f"📧 An: {application.email_to or 'Empfaenger'}\n"
                    f"📋 Betreff: {application.email_subject}\n"
                    f"📎 Anhaenge: CV + Anschreiben als PDF\n\n"
                    "Der Status wurde auf «sent» gesetzt."
                )
                return

            except ImportError:
                await update.message.reply_text(
                    "❌ Gmail-Service noch nicht konfiguriert.\n"
                    "Die Gmail API Integration kommt in Kuerze."
                )
                context.user_data.pop("pending_send", None)
                return
            except Exception:
                logger.exception("Gmail send failed")
                await update.message.reply_text(
                    "❌ Fehler beim E-Mail-Versand. "
                    "Bitte pruefe die Gmail-Konfiguration."
                )
                context.user_data.pop("pending_send", None)
                return
        else:
            context.user_data.pop("pending_send", None)
            await update.message.reply_text("Versand abgebrochen.")
            return

    # Erster Aufruf: Bewerbung laden und Bestaetigung anfordern
    app_map = context.user_data.get("applications", {})
    search_map = context.user_data.get("last_search", {})

    user = await _get_or_create_user(update)
    if not user:
        return

    application = None
    if nr in app_map:
        async with async_session_factory() as session:
            result = await session.execute(
                select(Application).where(Application.id == app_map[nr])
            )
            application = result.scalar_one_or_none()
    elif nr in search_map:
        application = await get_application_by_job(
            user.id, uuid_mod.UUID(search_map[nr])
        )

    if not application or not application.cv_pdf:
        await update.message.reply_text(
            f"Keine fertige Bewerbung fuer Nr. {nr}.\n"
            "Erstelle zuerst eine mit /bewerben."
        )
        return

    async with async_session_factory() as session:
        job = await session.get(Job, application.job_id)

    job_title = job.title if job else "Stelle"
    company = job.company if job else "Unbekannt"

    # Pending speichern und Bestaetigung anfordern
    context.user_data["pending_send"] = {
        "nr": nr,
        "application_id": str(application.id),
    }

    await update.message.reply_text(
        f"⚠️ Bewerbung versenden?\n\n"
        f"📌 Stelle: {job_title}\n"
        f"🏢 Firma: {company}\n"
        f"📧 Betreff: {application.email_subject}\n"
        f"📎 Anhaenge: CV + Anschreiben (PDF)\n\n"
        f"Zum Bestaetigen: /senden {nr} ja\n"
        f"Zum Abbrechen: /senden {nr} nein"
    )


@restricted
async def cmd_bewerbungen(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle /bewerbungen — list all applications with status."""
    user = await _get_or_create_user(update)
    if not user:
        await update.message.reply_text("Nutzer nicht gefunden.")
        return

    async with async_session_factory() as session:
        result = await session.execute(
            select(Application)
            .where(Application.user_id == user.id)
            .order_by(Application.created_at.desc())
        )
        applications = list(result.scalars().all())

    if not applications:
        await update.message.reply_text(
            "Noch keine Bewerbungen vorhanden.\n"
            "Starte mit /suche und /bewerben."
        )
        return

    STATUS_EMOJI = {
        "found": "🔍",
        "cv_generated": "📄",
        "review": "👀",
        "sent": "📨",
        "interview": "🎯",
        "rejected": "❌",
        "offer": "🎉",
    }

    lines = [f"📋 Deine Bewerbungen ({len(applications)}):\n"]

    for i, app in enumerate(applications, 1):
        emoji = STATUS_EMOJI.get(app.status, "❓")
        # Job-Daten sind via lazy="selectin" geladen
        job = app.job
        title = job.title if job else "Unbekannt"
        company = job.company if job else "—"
        sent_info = ""
        if app.sent_at:
            sent_info = f" | gesendet {app.sent_at.strftime('%d.%m.%Y')}"

        lines.append(
            f"{i}. {emoji} {app.status.upper()}\n"
            f"   {title} bei {company}{sent_info}"
        )

        # ID in context speichern fuer /status
        context.user_data.setdefault("app_list", {})[str(i)] = str(app.id)

    lines.append(
        "\nStatus aendern: /status [Nr] [neuer_status]\n"
        "Erlaubt: found, cv_generated, review, sent, interview, rejected, offer"
    )

    text = "\n".join(lines)
    if len(text) > 4000:
        text = text[:4000] + "\n\n... (abgeschnitten)"

    await update.message.reply_text(text)


@restricted
async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /status [nr] [neuer_status] — update application status."""
    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "Bitte Nummer und Status angeben: /status 1 interview\n\n"
            "Erlaubte Status:\n"
            "  found — gefunden\n"
            "  cv_generated — CV erstellt\n"
            "  review — in Pruefung\n"
            "  sent — gesendet\n"
            "  interview — Einladung\n"
            "  rejected — Absage\n"
            "  offer — Angebot"
        )
        return

    nr = context.args[0]
    new_status = context.args[1].lower()

    app_list = context.user_data.get("app_list", {})

    if nr not in app_list:
        await update.message.reply_text(
            f"Nr. {nr} nicht gefunden. Fuehre zuerst /bewerbungen aus."
        )
        return

    application_id = uuid_mod.UUID(app_list[nr])

    try:
        app = await update_application_status(application_id, new_status)
    except ValueError as exc:
        await update.message.reply_text(f"❌ {exc}")
        return

    STATUS_LABELS = {
        "found": "🔍 Gefunden",
        "cv_generated": "📄 CV erstellt",
        "review": "👀 In Pruefung",
        "sent": "📨 Gesendet",
        "interview": "🎯 Einladung",
        "rejected": "❌ Absage",
        "offer": "🎉 Angebot",
    }

    label = STATUS_LABELS.get(new_status, new_status)
    await update.message.reply_text(f"✅ Status aktualisiert: {label}")


@restricted
async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /stats — show application statistics."""
    user = await _get_or_create_user(update)
    if not user:
        await update.message.reply_text("Nutzer nicht gefunden.")
        return

    async with async_session_factory() as session:
        result = await session.execute(
            select(Application).where(Application.user_id == user.id)
        )
        applications = list(result.scalars().all())

    if not applications:
        await update.message.reply_text(
            "Noch keine Bewerbungen vorhanden."
        )
        return

    total = len(applications)
    by_status: dict[str, int] = {}
    for app in applications:
        by_status[app.status] = by_status.get(app.status, 0) + 1

    sent = by_status.get("sent", 0)
    interviews = by_status.get("interview", 0)
    offers = by_status.get("offer", 0)
    rejected = by_status.get("rejected", 0)

    # Quote berechnen
    responded = interviews + offers + rejected
    interview_rate = (
        f"{(interviews + offers) / responded * 100:.0f}%"
        if responded > 0
        else "—"
    )

    text = (
        f"📊 Bewerbungs-Statistik\n\n"
        f"📋 Total: {total}\n"
        f"📄 CV erstellt: {by_status.get('cv_generated', 0)}\n"
        f"📨 Gesendet: {sent}\n"
        f"🎯 Einladungen: {interviews}\n"
        f"🎉 Angebote: {offers}\n"
        f"❌ Absagen: {rejected}\n\n"
        f"📈 Einladungsquote: {interview_rate}\n"
        f"   (basierend auf {responded} Rueckmeldungen)"
    )

    await update.message.reply_text(text)


@restricted
async def cmd_nachweis(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle /nachweis [monat] — generate RAV form + monthly overview."""
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)

    # Monat aus Argument oder aktueller Monat
    if context.args:
        try:
            arg = context.args[0]
            if "." in arg:
                # Format: 07.2026 oder 7.2026
                parts = arg.split(".")
                month = int(parts[0])
                year = int(parts[1])
            else:
                month = int(arg)
                year = now.year
        except (ValueError, IndexError):
            await update.message.reply_text(
                "Format: /nachweis 7 oder /nachweis 07.2026"
            )
            return
    else:
        month = now.month
        year = now.year

    if not (1 <= month <= 12):
        await update.message.reply_text("Unguelter Monat (1-12).")
        return

    MONTHS_DE = [
        "", "Januar", "Februar", "Maerz", "April", "Mai", "Juni",
        "Juli", "August", "September", "Oktober", "November", "Dezember",
    ]

    await update.message.reply_text(
        f"📋 Erstelle RAV-Nachweis fuer {MONTHS_DE[month]} {year}..."
    )

    user = await _get_or_create_user(update)
    if not user:
        await update.message.reply_text("Nutzer nicht gefunden.")
        return

    # Bewerbungen des Monats laden
    from sqlalchemy import extract

    async with async_session_factory() as session:
        result = await session.execute(
            select(Application)
            .where(
                Application.user_id == user.id,
                extract("month", Application.created_at) == month,
                extract("year", Application.created_at) == year,
            )
            .order_by(Application.created_at.asc())
        )
        apps = list(result.scalars().all())

        # Jobs nachladen
        app_job_pairs: list[tuple[Application, Job]] = []
        for app in apps:
            job = await session.get(Job, app.job_id)
            if job:
                app_job_pairs.append((app, job))

    # Marcos AHV-Nummer muss er selbst angeben — Platzhalter
    ahv_nr = context.user_data.get("ahv_nr", "756.____.____.__)

    # RAV-Formular generieren
    try:
        rav_pdf = render_rav_nachweis(
            applications=app_job_pairs,
            name=user.name,
            ahv_nr=ahv_nr,
            month=month,
            year=year,
        )

        overview_pdf = render_monthly_overview(
            applications=app_job_pairs,
            name=user.name,
            month=month,
            year=year,
        )
    except Exception:
        logger.exception("RAV PDF generation failed")
        await update.message.reply_text(
            "❌ Fehler bei der PDF-Erstellung."
        )
        return

    # PDFs senden
    month_str = f"{month:02d}_{year}"

    rav_file = io.BytesIO(rav_pdf)
    rav_file.name = f"RAV_Nachweis_{month_str}.pdf"

    overview_file = io.BytesIO(overview_pdf)
    overview_file.name = f"Bewerbungsuebersicht_{month_str}.pdf"

    await update.message.reply_document(
        document=rav_file,
        caption=f"📋 RAV-Nachweis {MONTHS_DE[month]} {year} "
        f"({len(app_job_pairs)} Bewerbungen)",
    )

    await update.message.reply_document(
        document=overview_file,
        caption=f"📊 Bewerbungsuebersicht {MONTHS_DE[month]} {year}",
    )

    if not app_job_pairs:
        await update.message.reply_text(
            f"Keine Bewerbungen im {MONTHS_DE[month]} gefunden.\n"
            "Die Formulare sind leer — du kannst sie manuell ausfuellen."
        )
    else:
        await update.message.reply_text(
            f"✅ {len(app_job_pairs)} Bewerbungen eingetragen.\n\n"
            "Hinweis: AHV-Nr. ist ein Platzhalter. "
            "Bitte vor der Abgabe manuell ergaenzen oder "
            "mit /ahv 756.xxxx.xxxx.xx setzen."
        )


@restricted
async def cmd_ahv(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle /ahv [nummer] — set AHV number for RAV forms."""
    if not context.args:
        current = context.user_data.get("ahv_nr", "Nicht gesetzt")
        await update.message.reply_text(
            f"AHV-Nr.: {current}\n\n"
            "Setzen mit: /ahv 756.1234.5678.90"
        )
        return

    ahv_nr = " ".join(context.args)
    context.user_data["ahv_nr"] = ahv_nr
    await update.message.reply_text(f"✅ AHV-Nr. gespeichert: {ahv_nr}")


async def handle_unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle unknown commands."""
    await update.message.reply_text(
        "Unbekannter Befehl. Tippe /help fuer alle Befehle."
    )
