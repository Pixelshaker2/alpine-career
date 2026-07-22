"""jobportalschweiz.ch scraper — schweizweites Stellenportal.

Source: jobportalschweiz.ch
Covers: Ganze Deutschschweiz — IT & Betrieb, Software Engineering, Data & KI
Saubere HTML-Struktur mit Titel, Firma, Ort, Gehalt, Beschreibung.
Keine API, aber gut strukturiertes Server-Side Rendering.

URL-Schema:
  /de/{kategorie}/jobs/{kanton}?page={n}
  Kategorien: it-betrieb, software-engineering, data-ki
  Kantone: kanton-luzern, kanton-zuerich, kanton-bern, kanton-basel-landschaft
"""

import asyncio
import logging
import re
from datetime import datetime, timezone

import httpx
from bs4 import BeautifulSoup

from src.services.scrapers.base import ScrapedJob, make_external_id

logger = logging.getLogger(__name__)

BASE_URL = "https://jobportalschweiz.ch"

# Kategorien die fuer Marco relevant sind
CATEGORIES = [
    "it-betrieb",
    "software-engineering",
    "data-ki",
]

# Kantone: Deutschschweiz (Marcos Zielmärkte)
CANTONS = [
    "kanton-luzern",
    "kanton-zuerich",
    "kanton-bern",
    "kanton-basel-landschaft",
    "kanton-zug",
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
    "Accept-Language": "de-CH,de;q=0.9",
}

# Kanton-Slug zu lesbarem Namen
CANTON_NAMES: dict[str, str] = {
    "kanton-luzern": "Luzern",
    "kanton-zuerich": "Zürich",
    "kanton-bern": "Bern",
    "kanton-basel-landschaft": "Basel",
    "kanton-zug": "Zug",
}


def _parse_salary(text: str) -> str | None:
    """Extract salary range from listing text."""
    match = re.search(
        r"CHF\s*([\d']+)\s*[–-]\s*([\d']+)",
        text,
    )
    if match:
        return f"CHF {match.group(1)}–{match.group(2)}"
    return None


def _parse_listing_page(html: str, category: str) -> list[dict[str, str]]:
    """Parse job listings from a jobportalschweiz.ch category page.

    Each job is an <li> or <a> block containing:
    - Job title as <h2> link
    - Company name
    - Location
    - Optional salary
    - Short description snippet
    """
    soup = BeautifulSoup(html, "html.parser")
    jobs: list[dict[str, str]] = []

    # Jobs sind als Liste von Links dargestellt
    # Jeder Job hat einen <h2> mit dem Titel als Link
    for heading in soup.find_all("h2"):
        link = heading.find("a", href=True)
        if not link:
            continue

        href = link.get("href", "")
        if "/de/jobs/" not in href:
            continue

        title = link.get_text(strip=True)
        if not title:
            continue

        job_url = href if href.startswith("http") else f"{BASE_URL}{href}"

        # Container um das <h2> herum fuer Metadaten
        # Gehe zum uebergeordneten <li> oder <div>
        container = heading.parent
        if container:
            container = container.parent or container
        full_text = container.get_text(" ", strip=True) if container else ""

        # Firma extrahieren — steht nach dem Titel
        company = ""
        # Suche nach Firmenname-Pattern: steht typisch in einem separaten Element
        if container:
            # Firmenname ist oft in einem Link mit /de/company/
            company_link = container.find("a", href=re.compile(r"/de/company/"))
            if company_link:
                company = company_link.get_text(strip=True)

        # Ort extrahieren
        location = ""
        location_match = re.search(
            r"(IT & Betrieb|Software Engineering|Data & KI)"
            r"[·\s]*([\w\s,]+?)(?:[·\s]*(?:CHF|Remote|Ausgeschrieben))",
            full_text,
        )
        if location_match:
            location = location_match.group(2).strip().rstrip("·").strip()

        # Gehalt
        salary = _parse_salary(full_text)

        # Beschreibung — letzter Textblock
        description = ""
        if container:
            # Text nach den Metadaten ist die Beschreibung
            all_text = container.get_text("\n", strip=True)
            lines = [
                line.strip() for line in all_text.split("\n")
                if line.strip() and len(line.strip()) > 30
            ]
            if lines:
                # Letzte laengere Zeile ist meist die Beschreibung
                description = lines[-1][:300]

        jobs.append({
            "title": title,
            "company": company or "Unbekannt",
            "location": location or "Schweiz",
            "url": job_url,
            "salary": salary or "",
            "description": description,
        })

    return jobs


async def _scrape_category_canton(
    client: httpx.AsyncClient,
    category: str,
    canton: str,
    max_pages: int = 2,
) -> list[ScrapedJob]:
    """Scrape one category+canton combination."""
    jobs: list[ScrapedJob] = []
    now = datetime.now(timezone.utc)
    canton_name = CANTON_NAMES.get(canton, canton)

    for page in range(1, max_pages + 1):
        url = f"{BASE_URL}/de/{category}/jobs/{canton}"
        params = {"page": page} if page > 1 else {}

        try:
            response = await client.get(url, params=params)
            if response.status_code != 200:
                break

            raw_jobs = _parse_listing_page(response.text, category)
            if not raw_jobs:
                break

            for raw in raw_jobs:
                external_id = make_external_id(
                    "jobportalschweiz", raw["url"], raw["title"]
                )
                location = raw["location"]
                if canton_name and canton_name not in location:
                    location = f"{location}, {canton_name}" if location else canton_name

                jobs.append(
                    ScrapedJob(
                        external_id=external_id,
                        source="jobportalschweiz",
                        title=raw["title"],
                        company=raw["company"],
                        location=location,
                        description=raw["description"],
                        url=raw["url"],
                        salary_range=raw["salary"] or None,
                        scraped_at=now,
                    )
                )

        except Exception as exc:
            logger.error(
                "jobportalschweiz scrape error",
                extra={
                    "category": category,
                    "canton": canton,
                    "page": page,
                    "error": str(exc),
                },
            )
            break

    return jobs


async def search_jobportalschweiz() -> list[ScrapedJob]:
    """Scrape jobportalschweiz.ch for IT jobs in Deutschschweiz.

    Covers IT & Betrieb, Software Engineering, Data & KI
    across LU, ZH, BE, BS, ZG.

    Returns:
        Combined, deduplicated list of ScrapedJob objects.
    """
    all_jobs: list[ScrapedJob] = []
    seen_ids: set[str] = set()

    async with httpx.AsyncClient(
        timeout=30.0,
        headers=HEADERS,
        follow_redirects=True,
    ) as client:
        for category in CATEGORIES:
            for canton in CANTONS:
                canton_jobs = await _scrape_category_canton(
                    client, category, canton, max_pages=1
                )
                for job in canton_jobs:
                    if job.external_id not in seen_ids:
                        seen_ids.add(job.external_id)
                        all_jobs.append(job)
                # Rate Limiting — 0.5s zwischen Requests
                await asyncio.sleep(0.5)

    logger.info(
        "jobportalschweiz search done",
        extra={
            "categories": len(CATEGORIES),
            "cantons": len(CANTONS),
            "total": len(all_jobs),
        },
    )
    return all_jobs
