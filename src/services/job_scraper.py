"""Job scraper orchestrator — combines multiple job sources.

Sources:
- JobSpy (Indeed + LinkedIn) — primary, no API key needed
- SwissDevJobs.ch — JSON API, Swiss IT jobs with salary
- Berlin Startup Jobs — HTML scraping, Berlin startup scene
- CH Media Portals — HTML scraping (zentraljob.ch, jobzueri.ch, jobbern.ch, jobbasel.ch)

All sources run concurrently. Results are deduplicated by external_id.
"""

import asyncio
import logging

from src.services.scrapers.base import ScrapedJob
from src.services.scrapers.berlin_startups_scraper import search_berlin_startups
from src.services.scrapers.jobspy_scraper import search_jobspy
from src.services.scrapers.swissdevjobs_scraper import search_swissdevjobs
from src.services.scrapers.zentraljob_scraper import search_chmedia_portals

logger = logging.getLogger(__name__)

# Re-export fuer Abwaertskompatibilitaet
__all__ = ["ScrapedJob", "search_jobs"]


async def search_jobs(
    region: str | None = None,
    max_per_search: int = 10,
) -> list[ScrapedJob]:
    """Search all sources for jobs matching Marcos profile.

    Runs all applicable scrapers concurrently and deduplicates results.

    Args:
        region: "berlin", "schweiz", or None for both.
        max_per_search: Max results per source per search.

    Returns:
        Combined, deduplicated list of ScrapedJob objects.
    """
    tasks: list[asyncio.Task[list[ScrapedJob]]] = []

    # JobSpy laeuft immer (Indeed + LinkedIn)
    tasks.append(
        asyncio.create_task(
            search_jobspy(region=region, max_per_search=max_per_search),
            name="jobspy",
        )
    )

    # Schweiz-spezifische Quellen
    if region == "schweiz" or region is None:
        tasks.append(
            asyncio.create_task(
                search_swissdevjobs(),
                name="swissdevjobs",
            )
        )
        tasks.append(
            asyncio.create_task(
                search_chmedia_portals(),
                name="chmedia",
            )
        )

    # Berlin-spezifische Quellen
    if region == "berlin" or region is None:
        tasks.append(
            asyncio.create_task(
                search_berlin_startups(max_pages=2),
                name="berlinstartups",
            )
        )

    # Alle parallel ausfuehren, Fehler einzeln abfangen
    all_jobs: list[ScrapedJob] = []
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for task, result in zip(tasks, results):
        source_name = task.get_name()
        if isinstance(result, Exception):
            logger.error(
                "Source failed",
                extra={"source": source_name, "error": str(result)},
            )
            continue
        logger.info(
            "Source completed",
            extra={"source": source_name, "count": len(result)},
        )
        all_jobs.extend(result)

    # Deduplizierung nach external_id
    seen: set[str] = set()
    unique_jobs: list[ScrapedJob] = []
    for job in all_jobs:
        if job.external_id not in seen:
            seen.add(job.external_id)
            unique_jobs.append(job)

    logger.info(
        "Multi-source search completed",
        extra={
            "region": region or "all",
            "total_raw": len(all_jobs),
            "unique": len(unique_jobs),
            "sources": len(tasks),
        },
    )
    return unique_jobs
