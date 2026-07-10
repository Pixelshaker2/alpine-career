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
    cmd_bewerben,
    cmd_bewerbungen,
    cmd_botstatus,
    cmd_detail,
    cmd_help,
    cmd_nachweis,
    cmd_profil,
    cmd_senden,
    cmd_start,
    cmd_stats,
    cmd_status,
    cmd_suche,
    cmd_vorschau,
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


def main() -> None:
    """Start the Telegram bot in polling mode."""
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

    # Unknown commands
    app.add_handler(MessageHandler(filters.COMMAND, handle_unknown))

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
