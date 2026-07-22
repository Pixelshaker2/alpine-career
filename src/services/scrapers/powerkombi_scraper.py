"""powerkombi.ch scraper — Zentralschweiz Jobportal.

Source: powerkombi.ch (Sammlung aus Lokalzeitungen der Zentralschweiz)
Covers: Luzern, Zug, Schwyz, Obwalden, Nidwalden, Uri, Aargau.

WICHTIG: Dieses Portal zeigt Inserate als gescannte Zeitungsbilder.
Strukturierte Daten sind minimal — nur der Jobtitel ist als Text
im title-Attribut der Bilder verfuegbar. Wir filtern nach IT-Keywords
im Titel, um relevante Stellen zu finden.

Kein API. Kein Suchfilter per URL fuer IT-Branche.
Isotope-Filter ist nur Client-Side JS und fuer uns nicht nutzbar.
"""

import logging
import re
from datetime import datetime, timezone

import httpx
from bs4 import BeautifulSoup

from src.services.scrapers.base import ScrapedJob, make_external_id

logger = logging.getLogger(__name__)

BASE_URL = "https://powerkombi.ch"
JOBS_URL = "https://powerkombi.ch/jobs"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
    "Accept-Language": "de-CH,de;q=0.9",
}

# IT-relevante Keywords im Jobtitel (case-insensitive)
IT_KEYWORDS: list[str] = [
    "IT",
    "EDV",
    "ICT",
    "Informatik",
    "System",
    "Cloud",
    "Azure",
    "AWS",
    "DevOps",
    "Software",
    "Entwickler",
    "Developer",
    "Engineer",
    "Administrator",
    "Netzwerk",
    "Security",
    "Datenbank",
    "SAP",
    "Microsoft",
    "Linux",
    "Server",
    "Support",
    "Helpdesk",
    "Techniker",
    "Applikation",
    "Web",
    "Programmierer",
    "Cyber",
    "Data",
    "Digital",
]

# Kompiliertes Regex fuer schnelle Suche
_IT_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(kw) for kw in IT_KEYWORDS) + r")",
    re.IGNORECASE,
)


def _is_it_relevant(title: str) -> bool:
    """Check if a job title contains IT-related keywords."""
    return bool(_IT_PATTERN.search(title))


def _extract_kanton(image_url: str) -> str:
    """Try to determine the canton/region from the image path.

    Powerkombi organises images by newspaper source:
    - barni-post → Obwalden
    - woche-pass → Luzern/Zentralschweiz
    - wochen-post → Luzern
    - aktuell-obwalden → Obwalden
    - nidwaldner-blitz → Nidwalden
    - schwyzer-anzeiger → Schwyz
    - uristier → Uri
    """
    path = image_url.lower()
    if "barni-post" in path:
        return "Obwalden"
    if "aktuell-obwalden" in path:
        return "Obwalden"
    if "nidwaldner-blitz" in path:
        return "Nidwalden"
    if "schwyzer-anzeiger" in path or "schwyzer" in path:
        return "Schwyz"
    if "uristier" in path:
        return "Uri"
    if "woche-pass" in path:
        return "Luzern"
    if "wochen-post" in path:
        return "Luzern"
    return "Zentralschweiz"


def _parse_powerkombi_page(html: str) -> list[dict[str, str]]:
    """Parse job listings from powerkombi.ch HTML.

    Jobs are displayed as image thumbnails with the job title
    in the title and alt attributes of the <img> tag.
    """
    soup = BeautifulSoup(html, "html.parser")
    jobs: list[dict[str, str]] = []
    seen_titles: set[str] = set()

    # Jobs sind als <a> mit Bild-Links dargestellt
    # Titel steht im title-Attribut des <a> oder <img>
    for link in soup.find_all("a", title=True):
        title = link.get("title", "").strip()
        href = link.get("href", "")

        # Nur Bild-Links zu Inseraten (enthalten /stellen/ im Pfad)
        if "/stellen/" not in href:
            continue

        if not title or len(title) < 3:
            continue

        # Duplikate vermeiden
        if title in seen_titles:
            continue
        seen_titles.add(title)

        # Nur IT-relevante Stellen
        if not _is_it_relevant(title):
            continue

        # URL zusammenbauen
        image_url = href if href.startswith("http") else f"{BASE_URL}{href}"

        # Kanton aus dem Bildpfad ableiten
        location = _extract_kanton(image_url)

        jobs.append({
            "title": title,
            "url": image_url,
            "location": location,
        })

    return jobs


async def search_powerkombi() -> list[ScrapedJob]:
    """Scrape powerkombi.ch for IT-relevant jobs in Zentralschweiz.

    Since the portal has no search/filter API, we load the main
    jobs page and filter by IT keywords in the title.

    Returns:
        List of ScrapedJob objects matching IT criteria.
    """
    now = datetime.now(timezone.utc)

    try:
        async with httpx.AsyncClient(
            timeout=30.0,
            headers=HEADERS,
            follow_redirects=True,
        ) as client:
            response = await client.get(JOBS_URL)

            if response.status_code != 200:
                logger.warning(
                    "Powerkombi returned non-200",
                    extra={"status": response.status_code},
                )
                return []

            raw_jobs = _parse_powerkombi_page(response.text)
            jobs: list[ScrapedJob] = []

            for raw in raw_jobs:
                external_id = make_external_id(
                    "powerkombi", raw["url"], raw["title"]
                )
                jobs.append(
                    ScrapedJob(
                        external_id=external_id,
                        source="powerkombi",
                        title=raw["title"],
                        company="(via Powerkombi)",
                        location=raw["location"],
                        description=(
                            "Inserat von powerkombi.ch — Details nur als "
                            "Bild verfuegbar. Originalinserat oeffnen fuer "
                            "vollstaendige Stellenbeschreibung."
                        ),
                        url=raw["url"],
                        salary_range=None,
                        scraped_at=now,
                    )
                )

            logger.info(
                "Powerkombi search done",
                extra={"it_relevant": len(jobs)},
            )
            return jobs

    except httpx.TimeoutException:
        logger.error("Powerkombi timeout")
        return []
    except Exception as exc:
        logger.error(
            "Powerkombi scrape failed",
            extra={"error": str(exc)},
        )
        return []
