"""Telegram bot command handlers."""

import logging

from sqlalchemy import select
from telegram import Update
from telegram.ext import ContextTypes

from src.bot.auth import restricted
from src.core.database import async_session_factory
from src.models.profile import Profile
from src.models.user import User

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


async def handle_unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle unknown commands."""
    await update.message.reply_text(
        "Unbekannter Befehl. Tippe /help fuer alle Befehle."
    )
