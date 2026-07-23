"""Entry point for the Telegram bot."""

import logging

import structlog
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from src.bot.handlers import (
    cmd_ahv,
    cmd_anpassen,
    cmd_bewerben,
    cmd_bewerbungen,
    cmd_botstatus,
    cmd_detail,
    cmd_email,
    cmd_help,
    cmd_nachweis,
    cmd_profil,
    cmd_senden,
    cmd_start,
    cmd_stats,
    cmd_status,
    cmd_suche,
    cmd_vorschau,
    handle_text_message,
    handle_unknown,
)
from src.bot.scheduled import register_scheduled_jobs
from src.core.config import settings


def configure_logging() -> None:
    """Set up structured logging with structlog."""
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    if settings.log_format == "json":
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer()

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            renderer,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(level=log_level, format="%(message)s")


def _startup_health_check(logger: structlog.stdlib.BoundLogger) -> None:
    """Verify critical services are reachable before starting polling.

    Runs synchronously to avoid initializing the async DB engine
    on a separate event loop (which breaks run_polling).
    """
    from pathlib import Path

    # 1. Datenbank — synchroner Check mit psycopg2
    try:
        from sqlalchemy import create_engine, text

        sync_url = settings.database_url.replace(
            "postgresql+asyncpg", "postgresql+psycopg2"
        )
        sync_engine = create_engine(sync_url)
        with sync_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        sync_engine.dispose()
        logger.info("Startup-Check: PostgreSQL OK")
    except Exception as exc:
        logger.error("Startup-Check: PostgreSQL FEHLGESCHLAGEN", error=str(exc))
        raise SystemExit(1)

    # 2. Redis — synchroner Check
    try:
        import redis

        r = redis.from_url(settings.redis_url)
        r.ping()
        r.close()
        logger.info("Startup-Check: Redis OK")
    except Exception as exc:
        logger.warning(
            "Startup-Check: Redis nicht erreichbar (Fallback aktiv)",
            error=str(exc),
        )

    # 3. Claude API Key
    if settings.anthropic_api_key:
        logger.info("Startup-Check: Claude API Key vorhanden")
    else:
        logger.error("Startup-Check: ANTHROPIC_API_KEY fehlt")
        raise SystemExit(1)

    # 4. Gmail Token (nicht kritisch)
    token_path = Path("/app/data/gmail_token.pickle")
    if token_path.exists():
        logger.info("Startup-Check: Gmail Token vorhanden")
    else:
        logger.warning("Startup-Check: Gmail Token fehlt — /senden wird nicht funktionieren")

    # 5. Zeugnisse
    zeugnisse_dir = Path("/app/data/zeugnisse")
    if zeugnisse_dir.exists():
        count = len(list(zeugnisse_dir.glob("*.pdf")))
        logger.info("Startup-Check: Zeugnisse-Ordner OK", count=count)
    else:
        logger.warning("Startup-Check: Kein Zeugnisse-Ordner vorhanden")


def main() -> None:
    """Start the Telegram bot in polling mode."""
    import asyncio

    configure_logging()
    logger = structlog.get_logger()

    if not settings.telegram_bot_token:
        logger.error("TELEGRAM_BOT_TOKEN ist nicht gesetzt")
        raise SystemExit(1)

    logger.info(
        "Bot wird gestartet",
        app_name=settings.app_name,
        app_env=settings.app_env,
        allowed_users=settings.allowed_usernames_list,
    )

    # Startup Health Check — synchron, damit der async DB-Engine
    # erst im Bot-Event-Loop initialisiert wird
    _startup_health_check(logger)

    app = ApplicationBuilder().token(settings.telegram_bot_token).build()

    # Command handlers
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("hilfe", cmd_help))
    app.add_handler(CommandHandler("botstatus", cmd_botstatus))
    app.add_handler(CommandHandler("profil", cmd_profil))
    app.add_handler(CommandHandler("suche", cmd_suche))
    app.add_handler(CommandHandler("detail", cmd_detail))
    app.add_handler(CommandHandler("bewerben", cmd_bewerben))
    app.add_handler(CommandHandler("vorschau", cmd_vorschau))
    app.add_handler(CommandHandler("senden", cmd_senden))
    app.add_handler(CommandHandler("bewerbungen", cmd_bewerbungen))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("stats", cmd_stats))
    app.add_handler(CommandHandler("nachweis", cmd_nachweis))
    app.add_handler(CommandHandler("rav", cmd_nachweis))
    app.add_handler(CommandHandler("ahv", cmd_ahv))
    app.add_handler(CommandHandler("email", cmd_email))
    app.add_handler(CommandHandler("anpassen", cmd_anpassen))

    # Unknown commands
    app.add_handler(MessageHandler(filters.COMMAND, handle_unknown))

    # Free-text messages (e.g. email address input)
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, handle_text_message
    ))

    # Global error handler
    async def error_handler(
        update: object, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Log errors and notify user."""
        logger.error(
            "Bot error",
            error=str(context.error),
            exc_info=context.error,
        )
        if isinstance(update, Update) and update.effective_message:
            try:
                await update.effective_message.reply_text(
                    "❌ Ein unerwarteter Fehler ist aufgetreten. "
                    "Bitte versuche es spaeter nochmal."
                )
            except Exception:
                pass  # Wenn auch die Fehlermeldung scheitert

    app.add_error_handler(error_handler)

    # Scheduled tasks (taegliche Jobsuche)
    register_scheduled_jobs(app)

    logger.info("Bot laeuft — warte auf Nachrichten")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
