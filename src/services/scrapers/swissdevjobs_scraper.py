"""SwissDevJobs.ch scraper — JSON API, no key required.

Endpoint: https://swissdevjobs.ch/api/jobsLight
Returns all active jobs with salary, tech stack, and location.
"""

import logging
from datetime import datetime, timezone

import httpx

from src.services.scrapers.base import ScrapedJob, make_external_id

logger = logging.getLogger(__name__)

API_URL = "https://swissdevjobs.ch/api/jobsLight"
BASE_URL = "https://swissdevjobs.ch/jobs"

# Nur Deutschschweizer Staedte
ALLOWED_CITIES = {"zurich", "zürich", "bern", "basel", "luzern", "lucerne", "zug"}

# Keywords die zu Marcos Profil passen
RELEVANT_TAGS = {
    "azure", "microsoft", "m365", "cloud", "devops", "sysadmin",
    "system administrator", "infrastructure", "active directory",
    "intune", "exchange", "powershell", "windows", "it support",
    "it operations", "workplace", "entra", "security", "network",
    "linux", "docker", "kubernetes",
}


def _is_relevant(job: dict) -> bool:
    """Check if a job matches Marcos profile based on tags and technologies."""
    tags = {t.lower() for t in job.get("filterTags", [])}
    techs = {t.lower() for t in job.get("technologies", [])}
    name_lower = job.get("name", "").lower()
    category = job.get("techCategory", "").lower()

    all_terms = tags | techs | {name_lower} | {category}

    return bool(all_terms & RELEVANT_TAGS)


def _is_in_deutschschweiz(job: dict) -> bool:
    """Check if job is in German-speaking Switzerland."""
    city = job.get("actualCity", "").lower()
    city_cat = job.get("cityCategory", "").lower()
    return city in ALLOWED_CITIES or city_cat in ALLOWED_CITIES


async def search_swissdevjobs() -> list[ScrapedJob]:
    """Fetch IT jobs from SwissDevJobs API.

    Filters for Deutschschweiz locations and relevant tech skills.

    Returns:
        List of ScrapedJob objects matching Marcos profile.
    """
    jobs: list[ScrapedJob] = []
    now = datetime.now(timezone.utc)

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(API_URL)
            response.raise_for_status()
            data = response.json()

        if not isinstance(data, list):
            logger.warning("SwissDevJobs API returned unexpected format")
            return jobs

        for item in data:
            # Nur aktive, nicht pausierte Jobs
            if item.get("isPaused", False):
                continue

            # Nur Deutschschweiz
            if not _is_in_deutschschweiz(item):
                continue

            # Nur relevante IT-Jobs
            if not _is_relevant(item):
                continue

            title = item.get("name", "Unbekannt")
            company = item.get("company", "Unbekannt")
            city = item.get("actualCity", "Schweiz")
            job_slug = item.get("jobUrl", "")
            job_url = f"{BASE_URL}/{job_slug}" if job_slug else ""

            # Gehalt formatieren
            salary_range = None
            sal_from = item.get("annualSalaryFrom")
            sal_to = item.get("annualSalaryTo")
            if sal_from and sal_to:
                salary_range = f"{int(sal_from):,}–{int(sal_to):,} CHF"

            # Tech-Stack als Beschreibung
            techs = item.get("technologies", [])
            workplace = item.get("workplace", "")
            job_type = item.get("jobType", "")
            exp_level = item.get("expLevel", "")
            desc_parts = []
            if techs:
                desc_parts.append(f"Tech: {', '.join(techs)}")
            if workplace:
                desc_parts.append(f"Arbeitsmodell: {workplace}")
            if job_type:
                desc_parts.append(f"Typ: {job_type}")
            if exp_level:
                desc_parts.append(f"Level: {exp_level}")
            description = " | ".join(desc_parts)

            external_id = make_external_id("swissdevjobs", job_url, title)

            jobs.append(
                ScrapedJob(
                    external_id=external_id,
                    source="swissdevjobs",
                    title=title,
                    company=company,
                    location=city,
                    description=description,
                    url=job_url,
                    salary_range=salary_range,
                    scraped_at=now,
                )
            )

        logger.info(
            "SwissDevJobs search done",
            extra={"total_api": len(data), "matched": len(jobs)},
        )

    except httpx.HTTPStatusError as exc:
        logger.error(
            "SwissDevJobs API error",
            extra={"status": exc.response.status_code},
        )
    except Exception as exc:
        logger.error(
            "SwissDevJobs scrape failed",
            extra={"error": str(exc)},
        )

    return jobs
