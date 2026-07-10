"""Job scraper service — fetches jobs from Indeed and LinkedIn.

Uses python-jobspy library (no API key required).
Indeed: best scraper, no rate limiting.
LinkedIn: global search via location parameter.
Results are stored in the jobs table and cached in Redis.
"""

import asyncio
import hashlib
import logging
from dataclasses import dataclass
from datetime import datetime, timezone

from jobspy import scrape_jobs as _scrape_jobs

logger = logging.getLogger(__name__)

# Marcos Zielrollen als Suchbegriffe
SEARCH_TERMS = [
    "System Administrator Azure",
    "Cloud Administrator Microsoft 365",
    "IT Administrator Azure",
    "Modern Workplace Engineer",
]

# Regionen-Konfiguration
REGION_CONFIG = {
    "berlin": {
        "searches": [
            {
                "location": "Berlin, Germany",
                "country_indeed": "Germany",
            },
        ],
    },
    "schweiz": {
        "searches": [
            {
                "location": "Zürich, Schweiz",
                "country_indeed": "Switzerland",
            },
            {
                "location": "Bern, Schweiz",
                "country_indeed": "Switzerland",
            },
            {
                "location": "Basel, Schweiz",
                "country_indeed": "Switzerland",
            },
            {
                "location": "Luzern, Schweiz",
                "country_indeed": "Switzerland",
            },
        ],
    },
}


@dataclass
class ScrapedJob:
    """A job fetched from an external source."""

    external_id: str
    source: str
    title: str
    company: str
    location: str
    description: str
    url: str
    salary_range: str | None
    scraped_at: datetime


def _make_external_id(source: str, url: str, title: str) -> str:
    """Create a stable external ID from job data."""
    raw = f"{source}:{url}:{title}"
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


def _scrape_region(
    search_term: str,
    location: str,
    country_indeed: str,
    results_wanted: int = 10,
) -> list[ScrapedJob]:
    """Run a single JobSpy scrape (synchronous).

    Args:
        search_term: Job search query.
        location: Location string (e.g. "Berlin, Germany").
        country_indeed: Country for Indeed (e.g. "Germany").
        results_wanted: Max results per site.

    Returns:
        List of ScrapedJob objects.
    """
    jobs: list[ScrapedJob] = []

    try:
        df = _scrape_jobs(
            site_name=["indeed", "linkedin"],
            search_term=search_term,
            location=location,
            country_indeed=country_indeed,
            results_wanted=results_wanted,
            hours_old=72,
            verbose=0,
        )

        if df is None or df.empty:
            return jobs

        now = datetime.now(timezone.utc)

        for _, row in df.iterrows():
            title = str(row.get("title", "Unbekannt"))
            company = str(row.get("company", "Unbekannt"))
            job_url = str(row.get("job_url", ""))
            site = str(row.get("site", "unknown"))
            city = str(row.get("city", ""))
            state = str(row.get("state", ""))
            description = str(row.get("description", ""))

            # Standort zusammenbauen
            loc_parts = [p for p in [city, state] if p and p != "nan"]
            job_location = ", ".join(loc_parts) if loc_parts else location

            # Gehalt formatieren
            salary_range = None
            min_amount = row.get("min_amount")
            max_amount = row.get("max_amount")
            currency = row.get("currency", "")
            if min_amount and max_amount and str(min_amount) != "nan":
                try:
                    currency_str = str(currency) if str(currency) != "nan" else ""
                    salary_range = (
                        f"{int(float(min_amount)):,}–"
                        f"{int(float(max_amount)):,} {currency_str}".strip()
                    )
                except (ValueError, TypeError):
                    pass

            external_id = _make_external_id(site, job_url, title)

            jobs.append(
                ScrapedJob(
                    external_id=external_id,
                    source=site,
                    title=title,
                    company=company,
                    location=job_location,
                    description=description[:5000] if description else "",
                    url=job_url,
                    salary_range=salary_range,
                    scraped_at=now,
                )
            )

    except Exception as exc:
        logger.error(
            "JobSpy scrape failed",
            extra={
                "error": str(exc),
                "location": location,
                "search_term": search_term,
            },
        )

    return jobs


async def search_jobs(
    region: str | None = None,
    max_per_search: int = 10,
) -> list[ScrapedJob]:
    """Search for jobs matching Marcos profile.

    Args:
        region: Optional filter — "berlin", "schweiz", or None for both.
        max_per_search: Max results per site per search.

    Returns:
        Combined list of ScrapedJob objects, deduplicated.
    """
    all_jobs: list[ScrapedJob] = []
    seen_ids: set[str] = set()

    regions = []
    if region == "berlin" or region is None:
        regions.append("berlin")
    if region == "schweiz" or region is None:
        regions.append("schweiz")

    for reg in regions:
        config = REGION_CONFIG[reg]
        for search_cfg in config["searches"]:
            # Verwende den ersten Suchbegriff (breiteste Abdeckung)
            search_term = SEARCH_TERMS[0]
            scraped = await asyncio.to_thread(
                _scrape_region,
                search_term=search_term,
                location=search_cfg["location"],
                country_indeed=search_cfg["country_indeed"],
                results_wanted=max_per_search,
            )

            for job in scraped:
                if job.external_id not in seen_ids:
                    seen_ids.add(job.external_id)
                    all_jobs.append(job)

            logger.info(
                "Region search completed",
                extra={
                    "location": search_cfg["location"],
                    "results": len(scraped),
                },
            )

    logger.info(
        "Job search completed",
        extra={"region": region or "all", "total": len(all_jobs)},
    )
    return all_jobs
