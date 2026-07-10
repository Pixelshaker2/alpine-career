"""Telegram bot command handlers."""

import logging

from sqlalchemy import select
from telegram import Update
from telegram.ext import ContextTypes

from src.bot.auth import restricted
from src.core.database import async_session_factory
from src.models.job import Job
from src.models.profile import Profile
from src.models.user import User
from src.services.job_matcher import score_job, score_jobs
from src.services.job_service import search_and_persist

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


async def handle_unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle unknown commands."""
    await update.message.reply_text(
        "Unbekannter Befehl. Tippe /help fuer alle Befehle."
    )
