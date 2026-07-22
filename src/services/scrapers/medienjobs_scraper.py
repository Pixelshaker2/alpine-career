"""medienjobs.ch + ictjobs.ch scraper — Schweizer Stellenportale.

Source: medienjobs.ch (Kommunikation/Marketing/Medien)
        ictjobs.ch (IT/Informatik — Schwesterseite)

Gleiche Plattform und HTML-Struktur. WordPress-basiert, serverseitig
gerendert. Jobs als .offer.publish Elemente mit:
  - h2[itemprop="title"] > a → Titel + Link
  - Text "bei {Firma}" und "in {Ort}"

ictjobs.ch hat Top-Firmen: Google, SAP, Microsoft, NVIDIA, Meta, Apple.
medienjobs.ch hat Digital/Web/Marketing-Stellen.

Kein API. WebFetch liefert leere Seite (JS-Rendering fuer Navigation,
aber Hauptinhalt ist SSR). httpx funktioniert mit dem richtigen HTML-Parser.
"""

import logging
import re
from datetime import datetime, timezone

import httpx
from bs4 import BeautifulSoup

from src.services.scrapers.base import ScrapedJob, make_external_id

logger = logging.getLogger(__name__)

# Beide Portale — gleiche HTML-Struktur
PORTALS = {
    "ictjobs": {
        "url": "https://ictjobs.ch/",
        "source": "ictjobs",
    },
    "medienjobs": {
        "url": "https://medienjobs.ch/",
        "source": "medienjobs",
    },
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
    "Accept-Language": "de-CH,de;q=0.9",
}

# IT-Keywords fuer medienjobs.ch (ictjobs.ch ist schon IT-only)
IT_KEYWORDS_PATTERN = re.compile(
    r"\b(IT|ICT|Cloud|Azure|AWS|DevOps|Software|Engineer|Developer|"
    r"Informatik|System|Security|Cyber|Data|Digital|Web|Fullstack|"
    r"Backend|Frontend|SAP|Network|Admin|Support|Architect)\b",
    re.IGNORECASE,
)


def _parse_jobs_page(html: str, source: str) -> list[dict[str, str]]:
    """Parse job listings from medienjobs/ictjobs HTML.

    Structure: .offer.publish > .description > h2 > a (title+link)
    Text contains "bei {company}" and "in {location}".
    """
    soup = BeautifulSoup(html, "html.parser")
    jobs: list[dict[str, str]] = []

    for offer in soup.find_all("div", class_="offer"):
        if "publish" not in offer.get("class", []):
            continue

        desc_div = offer.find("div", class_="description")
        if not desc_div:
            continue

        # Titel + Link
        h2 = desc_div.find("h2")
        if not h2:
            continue

        link = h2.find("a", href=True)
        if not link:
            continue

        title = link.get_text(strip=True)
        url = link.get("href", "")
        if not title or not url:
            continue

        # Firma und Ort aus dem Text extrahieren
        full_text = desc_div.get_text("\n", strip=True)
        company = ""
        location = ""

        # "bei {Firma}" Pattern
        bei_match = re.search(r"bei\s+(.+?)(?:\n|$)", full_text)
        if bei_match:
            company = bei_match.group(1).strip()

        # "in {Ort}" Pattern
        in_match = re.search(r"\bin\s+(.+?)(?:\n|$)", full_text)
        if in_match:
            location = in_match.group(1).strip()

        # Datum
        time_el = offer.find("time")
        date_str = time_el.get("datetime", "") if time_el else ""

        jobs.append({
            "title": title,
            "company": company or "Unbekannt",
            "location": location or "Schweiz",
            "url": url,
            "date": date_str,
        })

    return jobs


async def _scrape_portal(
    client: httpx.AsyncClient,
    portal_key: str,
    portal_url: str,
    filter_it: bool = False,
) -> list[ScrapedJob]:
    """Scrape a single portal (ictjobs or medienjobs)."""
    now = datetime.now(timezone.utc)
    source = portal_key

    try:
        response = await client.get(portal_url)
        if response.status_code != 200:
            logger.warning(
                f"{portal_key} returned non-200",
                extra={"status": response.status_code},
            )
            return []

        raw_jobs = _parse_jobs_page(response.text, source)
        jobs: list[ScrapedJob] = []

        for raw in raw_jobs:
            # Bei medienjobs.ch: nur IT-relevante Stellen
            if filter_it and not IT_KEYWORDS_PATTERN.search(raw["title"]):
                continue

            external_id = make_external_id(source, raw["url"], raw["title"])
            jobs.append(
                ScrapedJob(
                    external_id=external_id,
                    source=source,
                    title=raw["title"],
                    company=raw["company"],
                    location=raw["location"],
                    description="",
                    url=raw["url"],
                    salary_range=None,
                    scraped_at=now,
                )
            )

        logger.info(
            f"{portal_key} search done",
            extra={"total_raw": len(raw_jobs), "matched": len(jobs)},
        )
        return jobs

    except httpx.TimeoutException:
        logger.error(f"{portal_key} timeout")
        return []
    except Exception as exc:
        logger.error(
            f"{portal_key} scrape failed",
            extra={"error": str(exc)},
        )
        return []


async def search_medienjobs() -> list[ScrapedJob]:
    """Scrape ictjobs.ch + medienjobs.ch for IT jobs.

    ictjobs.ch: All jobs (already IT-focused)
    medienjobs.ch: Only IT-relevant jobs (filtered by keywords)

    Returns:
        Combined list of ScrapedJob objects.
    """
    all_jobs: list[ScrapedJob] = []

    async with httpx.AsyncClient(
        timeout=30.0,
        headers=HEADERS,
        follow_redirects=True,
    ) as client:
        # ictjobs.ch — alle Jobs sind IT
        ict_jobs = await _scrape_portal(
            client, "ictjobs", PORTALS["ictjobs"]["url"], filter_it=False
        )
        all_jobs.extend(ict_jobs)

        # medienjobs.ch — nur IT-relevante
        media_jobs = await _scrape_portal(
            client, "medienjobs", PORTALS["medienjobs"]["url"], filter_it=True
        )
        all_jobs.extend(media_jobs)

    logger.info(
        "medienjobs+ictjobs search done",
        extra={"total": len(all_jobs)},
    )
    return all_jobs
