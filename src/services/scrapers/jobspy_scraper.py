"""JobSpy scraper — Indeed + LinkedIn via python-jobspy.

No API key required. Indeed has no rate limiting.
LinkedIn may rate-limit after ~10 pages.
"""

import asyncio
import logging
from datetime import datetime, timezone

from jobspy import scrape_jobs as _scrape_jobs

from src.services.scrapers.base import ScrapedJob, make_external_id

logger = logging.getLogger(__name__)

# Marcos Zielrollen als Suchbegriffe
SEARCH_TERMS = [
    "System Administrator Azure",
    "Cloud Administrator Microsoft 365",
    "IT Administrator Azure",
    "Modern Workplace Engineer",
]

# Regionen-Konfiguration
REGION_CONFIG: dict[str, list[dict[str, str]]] = {
    "berlin": [
        {"location": "Berlin, Germany", "country_indeed": "Germany"},
    ],
    "schweiz": [
        {"location": "Zürich, Schweiz", "country_indeed": "Switzerland"},
        {"location": "Bern, Schweiz", "country_indeed": "Switzerland"},
        {"location": "Basel, Schweiz", "country_indeed": "Switzerland"},
        {"location": "Luzern, Schweiz", "country_indeed": "Switzerland"},
    ],
}


def _scrape_single(
    search_term: str,
    location: str,
    country_indeed: str,
    results_wanted: int = 10,
) -> list[ScrapedJob]:
    """Run a single JobSpy scrape (synchronous)."""
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

            loc_parts = [p for p in [city, state] if p and p != "nan"]
            job_location = ", ".join(loc_parts) if loc_parts else location

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

            external_id = make_external_id(site, job_url, title)

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
            extra={"error": str(exc), "location": location},
        )

    return jobs


async def search_jobspy(
    region: str | None = None,
    max_per_search: int = 10,
) -> list[ScrapedJob]:
    """Search Indeed + LinkedIn via JobSpy.

    Args:
        region: "berlin", "schweiz", or None for both.
        max_per_search: Max results per site per search.

    Returns:
        List of ScrapedJob objects.
    """
    all_jobs: list[ScrapedJob] = []

    regions = []
    if region == "berlin" or region is None:
        regions.append("berlin")
    if region == "schweiz" or region is None:
        regions.append("schweiz")

    seen_ids: set[str] = set()

    for reg in regions:
        for search_cfg in REGION_CONFIG[reg]:
            # Alle Suchbegriffe verwenden fuer bessere Abdeckung
            for term in SEARCH_TERMS:
                scraped = await asyncio.to_thread(
                    _scrape_single,
                    search_term=term,
                    location=search_cfg["location"],
                    country_indeed=search_cfg["country_indeed"],
                    results_wanted=max_per_search,
                )
                # Duplikate filtern
                for job in scraped:
                    if job.external_id not in seen_ids:
                        seen_ids.add(job.external_id)
                        all_jobs.append(job)

                logger.info(
                    "JobSpy search done",
                    extra={
                        "term": term,
                        "location": search_cfg["location"],
                        "results": len(scraped),
                    },
                )

    return all_jobs
