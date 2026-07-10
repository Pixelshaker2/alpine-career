"""Berlin Startup Jobs scraper — HTML parsing.

Source: berlinstartupjobs.com/engineering/
No API available, uses BeautifulSoup for HTML parsing.
"""

import logging
from datetime import datetime, timezone

import httpx
from bs4 import BeautifulSoup

from src.services.scrapers.base import ScrapedJob, make_external_id

logger = logging.getLogger(__name__)

BASE_URL = "https://berlinstartupjobs.com"
ENGINEERING_URL = f"{BASE_URL}/engineering/"

# Nur IT-relevante Jobs behalten (basierend auf Skills/Keywords)
RELEVANT_SKILLS = {
    "cloud", "azure", "devops", "infrastructure", "kubernetes",
    "docker", "linux", "backend", "sysadmin", "system",
    "platform", "operations", "security", "network", "it",
    "python", "powershell", "ci/cd", "aws", "gcp",
}

# Headers um nicht als Bot erkannt zu werden
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
    "Accept-Language": "de-DE,de;q=0.9,en;q=0.8",
}


def _parse_jobs_page(html: str) -> list[dict[str, str]]:
    """Parse job listings from Berlin Startup Jobs HTML.

    Returns:
        List of dicts with title, company, url, description, skills.
    """
    soup = BeautifulSoup(html, "html.parser")
    jobs: list[dict[str, str]] = []

    # Job-Eintraege sind <li> Elemente im Hauptbereich
    # Titel ist in <h4> mit Link, Firma folgt danach
    for heading in soup.find_all("h4"):
        link = heading.find("a")
        if not link or not link.get("href"):
            continue

        href = link["href"]
        if "/engineering/" not in href and "/operations/" not in href:
            continue

        title = link.get_text(strip=True)
        job_url = href if href.startswith("http") else f"{BASE_URL}{href}"

        # Firma steht oft im naechsten Element nach dem h4
        company = "Unbekannt"
        parent = heading.parent
        if parent:
            # Suche nach Company-Link
            company_links = parent.find_all("a")
            for cl in company_links:
                cl_href = cl.get("href", "")
                if "/companies/" in cl_href:
                    company = cl.get_text(strip=True)
                    break

        # Beschreibung: Text im gleichen Container
        description = ""
        if parent:
            # Hol den Fliesstext
            texts = parent.find_all(string=True, recursive=True)
            desc_parts = []
            for t in texts:
                text = t.strip()
                if text and len(text) > 20 and text != title and text != company:
                    desc_parts.append(text)
            description = " ".join(desc_parts[:3])[:2000]

        # Skills aus Skill-Links extrahieren
        skills: list[str] = []
        if parent:
            for skill_link in parent.find_all("a"):
                skill_href = skill_link.get("href", "")
                if "/skill-areas/" in skill_href:
                    skills.append(skill_link.get_text(strip=True).lower())

        jobs.append({
            "title": title,
            "company": company,
            "url": job_url,
            "description": description,
            "skills": ",".join(skills),
        })

    return jobs


def _is_relevant(job: dict[str, str]) -> bool:
    """Check if job matches IT infrastructure / Cloud / SysAdmin profile."""
    title_lower = job["title"].lower()
    skills = set(job.get("skills", "").split(","))
    desc_lower = job.get("description", "").lower()

    all_text = f"{title_lower} {' '.join(skills)} {desc_lower}"
    return bool(any(skill in all_text for skill in RELEVANT_SKILLS))


async def search_berlin_startups(max_pages: int = 2) -> list[ScrapedJob]:
    """Scrape IT jobs from Berlin Startup Jobs.

    Args:
        max_pages: Number of pages to scrape (each ~20 jobs).

    Returns:
        List of ScrapedJob objects.
    """
    all_raw: list[dict[str, str]] = []
    now = datetime.now(timezone.utc)

    async with httpx.AsyncClient(timeout=30.0, headers=HEADERS) as client:
        for page in range(1, max_pages + 1):
            url = ENGINEERING_URL if page == 1 else f"{ENGINEERING_URL}page/{page}/"
            try:
                response = await client.get(url)
                if response.status_code == 404:
                    break  # Keine weiteren Seiten
                response.raise_for_status()

                raw_jobs = _parse_jobs_page(response.text)
                all_raw.extend(raw_jobs)

                logger.info(
                    "Berlin Startup Jobs page scraped",
                    extra={"page": page, "jobs": len(raw_jobs)},
                )

            except httpx.HTTPStatusError as exc:
                logger.error(
                    "Berlin Startup Jobs HTTP error",
                    extra={"page": page, "status": exc.response.status_code},
                )
                break
            except Exception as exc:
                logger.error(
                    "Berlin Startup Jobs scrape failed",
                    extra={"page": page, "error": str(exc)},
                )
                break

    # Filtern auf relevante IT-Jobs
    jobs: list[ScrapedJob] = []
    for raw in all_raw:
        if not _is_relevant(raw):
            continue

        external_id = make_external_id("berlinstartups", raw["url"], raw["title"])
        jobs.append(
            ScrapedJob(
                external_id=external_id,
                source="berlinstartups",
                title=raw["title"],
                company=raw["company"],
                location="Berlin",
                description=raw.get("description", "")[:5000],
                url=raw["url"],
                salary_range=None,
                scraped_at=now,
            )
        )

    logger.info(
        "Berlin Startup Jobs done",
        extra={"total_scraped": len(all_raw), "relevant": len(jobs)},
    )
    return jobs
