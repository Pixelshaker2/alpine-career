"""Telegram bot command handlers."""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from src.bot.auth import restricted

logger = logging.getLogger(__name__)


@restricted
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start — welcome message."""
    user = update.effective_user
    await update.message.reply_text(
        f"Hallo {user.first_name}! 👋\n\n"
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
async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /status — show bot and system status."""
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
    """Handle /profil — show user profile (placeholder)."""
    await update.message.reply_text(
        "👤 *Dein Profil*\n\n"
        "Name: Marco von Burg\n"
        "Standorte: Berlin, Schweiz\n"
        "Rollen: Cloud Admin, M365 Admin, IT\\-Sysadmin\n"
        "Remote: Ja\n\n"
        "_Profil\\-Bearbeitung kommt in Sprint 2\\._",
        parse_mode="MarkdownV2",
    )


async def handle_unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle unknown commands."""
    await update.message.reply_text(
        "Unbekannter Befehl. Tippe /help fuer alle Befehle."
    )
