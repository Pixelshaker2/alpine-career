"""Access control — only allowed Telegram users can use the bot."""

import logging
from functools import wraps
from typing import Any, Callable, Coroutine

from telegram import Update
from telegram.ext import ContextTypes

from src.core.config import settings

logger = logging.getLogger(__name__)


def restricted(
    func: Callable[..., Coroutine[Any, Any, None]],
) -> Callable[..., Coroutine[Any, Any, None]]:
    """Decorator: block users not in TELEGRAM_ALLOWED_USERNAMES."""

    @wraps(func)
    async def wrapper(
        update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        username = update.effective_user.username if update.effective_user else None
        if username not in settings.allowed_usernames_list:
            chat_id = update.effective_chat.id if update.effective_chat else 0
            logger.warning(
                "Unauthorized access attempt",
                extra={"username": username, "chat_id": chat_id},
            )
            if update.message:
                await update.message.reply_text(
                    "Zugriff verweigert. Dieser Bot ist nicht oeffentlich."
                )
            return
        return await func(update, context)

    return wrapper
