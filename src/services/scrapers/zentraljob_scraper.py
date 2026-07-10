"""zentraljob.ch scraper — HTML parsing.

Source: zentraljob.ch (CH Media Netzwerk)
Covers Zentralschweiz: Luzern, Zug, Schwyz, Obwalden, Nidwalden, Uri.
No API available, uses BeautifulSoup for HTML parsing.

Zusaetzlich: jobzueri.ch (Zuerich), jobbern.ch (Bern), jobbasel.ch (Basel)
— alle gleiche Plattform/Struktur von CH Media.
"""

import logging
from datetime import datetime, timezone

import httpx
from bs4 import BeautifulSoup

from src.services.scrapers.base import ScrapedJob, make_external_id

logger = logging.getLogger(__name__)

# CH Media Netzwerk — alle haben die gleiche HTML-Struktur
PORTALS = {
    "zentraljob": {
        "base_url": "https://www.zentraljob.ch",
        "search_url": (
            "https://www.zentraljob.ch/job/alle-jobs"
            "?q={query}&berufsgruppe=informatik-telekommunikation"
        ),
        "location": "Zentralschweiz",
    },
    "jobzueri": {
        "base_url": "https://www.jobzueri.ch",
        "search_url": (
            "https://www.jobzueri.ch/job/alle-jobs"
            "?q={query}&berufsgruppe=informatik-telekommunikation"
        ),
        "location": "Zürich",
    },
    "jobbern": {
        "base_url": "https://www.jobbern.ch",
        "search_url": (
            "https://www.jobbern.ch/job/alle-jobs"
            "?q={query}&berufsgruppe=informatik-telekommunikation"
        ),
        "location": "Bern",
    },
    "jobbasel": {
        "base_url": "https://www.jobbasel.ch",
        "search_url": (
            "https://www.jobbasel.ch/job/alle-jobs"
            "?q={query}&berufsgruppe=informatik-telekommunikation"
        ),
        "location": "Basel",
    },
}

SEARCH_QUERIES = ["Cloud", "System Administrator", "Azure", "Microsoft 365"]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
    "Accept-Language": "de-CH,de;q=0.9",
}


def _parse_chmedia_page(html: str, base_url: str) -> list[dict[str, str]]:
    """Parse job listings from CH Media portal HTML.

    CH Media portals render job cards as article/div blocks with
    title links and company info.
    """
    soup = BeautifulSoup(html, "html.parser")
    jobs: list[dict[str, str]] = []

    # CH Media Portale: Jobs sind oft in <a> Links mit /job/ Pfad
    # und Titel als Text
    for link in soup.find_all("a", href=True):
        href = link.get("href", "")
        # Job-Detail-Links enthalten typisch /job/ oder /stelle/
        if "/job/" not in href and "/stelle/" not in href:
            continue
        # Filtere Navigationslinks
        if href.endswith("/alle-jobs") or "berufsgruppe" in href:
            continue

        title = link.get_text(strip=True)
        if not title or len(title) < 5:
            continue

        job_url = href if href.startswith("http") else f"{base_url}{href}"

        # Versuche Firma und Ort aus dem umgebenden Container zu lesen
        company = "Unbekannt"
        location = ""
        parent = link.parent
        if parent:
            parent_parent = parent.parent
            if parent_parent:
                text = parent_parent.get_text(" ", strip=True)
                # Firma steht oft nach dem Titel
                parts = text.split(title)
                if len(parts) > 1:
                    rest = parts[1].strip()
                    # Erste Woerter koennten Firma sein
                    if rest:
                        company_candidate = rest.split("\n")[0].strip()
                        if company_candidate and len(company_candidate) < 100:
                            company = company_candidate

        jobs.append({
            "title": title,
            "company": company,
            "url": job_url,
            "location": location,
        })

    return jobs


async def _scrape_portal(
    portal_key: str,
    portal_config: dict[str, str],
    client: httpx.AsyncClient,
) -> list[ScrapedJob]:
    """Scrape a single CH Media portal for IT jobs."""
    jobs: list[ScrapedJob] = []
    now = datetime.now(timezone.utc)
    seen_urls: set[str] = set()

    for query in SEARCH_QUERIES[:2]:  # Max 2 Queries pro Portal
        url = portal_config["search_url"].format(query=query)
        try:
            response = await client.get(url)
            if response.status_code != 200:
                continue

            raw_jobs = _parse_chmedia_page(
                response.text, portal_config["base_url"]
            )

            for raw in raw_jobs:
                if raw["url"] in seen_urls:
                    continue
                seen_urls.add(raw["url"])

                external_id = make_external_id(
                    portal_key, raw["url"], raw["title"]
                )
                location = raw.get("location") or portal_config["location"]

                jobs.append(
                    ScrapedJob(
                        external_id=external_id,
                        source=portal_key,
                        title=raw["title"],
                        company=raw["company"],
                        location=location,
                        description="",
                        url=raw["url"],
                        salary_range=None,
                        scraped_at=now,
                    )
                )

        except Exception as exc:
            logger.error(
                "CH Media portal scrape failed",
                extra={
                    "portal": portal_key,
                    "query": query,
                    "error": str(exc),
                },
            )

    logger.info(
        "CH Media portal done",
        extra={"portal": portal_key, "results": len(jobs)},
    )
    return jobs


async def search_chmedia_portals() -> list[ScrapedJob]:
    """Scrape all CH Media job portals for IT jobs.

    Covers: zentraljob.ch, jobzueri.ch, jobbern.ch, jobbasel.ch.

    Returns:
        Combined list of ScrapedJob objects.
    """
    all_jobs: list[ScrapedJob] = []

    async with httpx.AsyncClient(
        timeout=30.0,
        headers=HEADERS,
        follow_redirects=True,
    ) as client:
        for portal_key, portal_config in PORTALS.items():
            portal_jobs = await _scrape_portal(portal_key, portal_config, client)
            all_jobs.extend(portal_jobs)

    logger.info(
        "CH Media portals search done",
        extra={"total": len(all_jobs)},
    )
    return all_jobs
