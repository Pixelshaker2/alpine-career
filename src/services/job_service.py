"""Job service — persists scraped jobs and handles search results."""

import json
import logging
import uuid as uuid_mod
from datetime import datetime, timezone

from sqlalchemy import select

from src.core.config import settings
from src.core.database import async_session_factory
from src.models.job import Job
from src.services.job_scraper import ScrapedJob, search_jobs

logger = logging.getLogger(__name__)


async def _get_redis():
    """Get Redis connection (lazy import to avoid startup issues)."""
    import redis.asyncio as aioredis

    return aioredis.from_url(settings.redis_url, decode_responses=True)


async def persist_jobs(scraped: list[ScrapedJob]) -> list[Job]:
    """Save scraped jobs to database, skip duplicates.

    Returns:
        List of Job model instances (new + existing).
    """
    jobs: list[Job] = []

    async with async_session_factory() as session:
        for item in scraped:
            result = await session.execute(
                select(Job).where(Job.external_id == item.external_id)
            )
            existing = result.scalar_one_or_none()

            if existing:
                jobs.append(existing)
                continue

            job = Job(
                external_id=item.external_id,
                source=item.source,
                title=item.title,
                company=item.company,
                location=item.location,
                description=item.description,
                url=item.url,
                salary_range=item.salary_range,
                scraped_at=item.scraped_at,
            )
            session.add(job)
            jobs.append(job)

        await session.commit()
        # Refresh to get IDs
        for job in jobs:
            await session.refresh(job)

    logger.info("Jobs persisted", extra={"count": len(jobs)})
    return jobs


def _cache_key(region: str | None) -> str:
    """Build Redis cache key for job search results."""
    return f"jobs:search:{region or 'all'}"


async def search_and_persist(
    region: str | None = None,
) -> list[Job]:
    """Search for jobs, cache results, persist to DB.

    Uses Redis cache with 6h TTL to avoid redundant API calls.

    Args:
        region: "berlin", "schweiz", or None for both.

    Returns:
        List of Job models sorted by scraped_at desc.
    """
    cache_key = _cache_key(region)

    # Check Redis cache
    try:
        r = await _get_redis()
        try:
            cached = await r.get(cache_key)
            if cached:
                raw_ids = json.loads(cached)
                # UUIDs korrekt casten (asyncpg ist strikt)
                job_ids = [uuid_mod.UUID(jid) for jid in raw_ids]
                logger.info(
                    "Cache hit",
                    extra={"key": cache_key, "count": len(job_ids)},
                )
                async with async_session_factory() as session:
                    result = await session.execute(
                        select(Job).where(Job.id.in_(job_ids))
                    )
                    return list(result.scalars().all())
        finally:
            await r.aclose()
    except Exception:
        logger.warning("Redis cache unavailable, falling back to API")

    # Scrape fresh results
    scraped = await search_jobs(region=region)
    if not scraped:
        return []

    # Persist to DB
    jobs = await persist_jobs(scraped)

    # Cache job IDs in Redis (TTL 6 hours)
    try:
        r = await _get_redis()
        job_ids = [str(j.id) for j in jobs]
        await r.setex(cache_key, 6 * 3600, json.dumps(job_ids))
        await r.aclose()
    except Exception:
        logger.warning("Could not write to Redis cache")

    return jobs
