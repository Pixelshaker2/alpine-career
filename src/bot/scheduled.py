"""Scheduled tasks — daily job search with push notifications.

Uses python-telegram-bot's JobQueue (backed by APScheduler).
Runs daily at 07:00 UTC (08:00 Berlin / 08:00 Zuerich).
"""

import logging

from sqlalchemy import select
from telegram.ext import ContextTypes

from src.core.database import async_session_factory
from src.models.user import User
from src.services.job_matcher import score_jobs
from src.services.job_service import search_and_persist

logger = logging.getLogger(__name__)

# Mindest-Score fuer Push-Benachrichtigung
MIN_PUSH_SCORE = 30


async def daily_job_search(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Run daily job search and notify users about new matches.

    This callback is triggered by the JobQueue scheduler.
    """
    logger.info("Daily job search started")

    try:
        # Redis-Cache wird automatisch invalidiert nach 6h
        # → Morgens gibt es immer frische Ergebnisse
        jobs = await search_and_persist(region=None)

        if not jobs:
            logger.info("Daily search: no jobs found")
            return

        scored = score_jobs(jobs)
        good_matches = [(job, score) for job, score in scored if score >= MIN_PUSH_SCORE]

        if not good_matches:
            logger.info("Daily search: no matches above threshold")
            return

        # Alle registrierten User benachrichtigen
        async with async_session_factory() as session:
            result = await session.execute(
                select(User).where(User.telegram_chat_id.isnot(None))
            )
            users = list(result.scalars().all())

        for user in users:
            try:
                # Top 5 Ergebnisse
                top = good_matches[:5]
                lines = [f"🔔 {len(good_matches)} neue passende Stellen gefunden!\n"]

                for i, (job, match_score) in enumerate(top, 1):
                    score_bar = (
                        "🟢" if match_score >= 60
                        else "🟡" if match_score >= 30
                        else "🔴"
                    )
                    salary = f" | {job.salary_range}" if job.salary_range else ""
                    lines.append(
                        f"{i}. {score_bar} {job.title} ({match_score:.0f}%)\n"
                        f"   🏢 {job.company} | 📍 {job.location}{salary}"
                    )

                if len(good_matches) > 5:
                    lines.append(
                        f"\n... und {len(good_matches) - 5} weitere. "
                        "Tippe /suche fuer alle Ergebnisse."
                    )
                else:
                    lines.append("\nTippe /suche fuer Details.")

                await context.bot.send_message(
                    chat_id=user.telegram_chat_id,
                    text="\n".join(lines),
                )
                logger.info(
                    "Push notification sent",
                    extra={"user": user.name, "matches": len(good_matches)},
                )

            except Exception:
                logger.exception(
                    "Failed to send push notification",
                    extra={"user_id": str(user.id)},
                )

    except Exception:
        logger.exception("Daily job search failed")


def register_scheduled_jobs(app) -> None:
    """Register all scheduled tasks with the bot's JobQueue.

    Args:
        app: The telegram.ext.Application instance.
    """
    job_queue = app.job_queue

    if job_queue is None:
        logger.warning("JobQueue not available — scheduled tasks disabled")
        return

    # Taegliche Suche um 07:00 UTC (08:00 CET / 09:00 CEST)
    from datetime import time

    job_queue.run_daily(
        daily_job_search,
        time=time(hour=7, minute=0),
        name="daily_job_search",
    )

    logger.info("Scheduled jobs registered: daily_job_search at 07:00 UTC")
