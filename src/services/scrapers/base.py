"""Base types for all job scrapers."""

import hashlib
from dataclasses import dataclass
from datetime import datetime


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


def make_external_id(source: str, url: str, title: str) -> str:
    """Create a stable external ID from job data."""
    raw = f"{source}:{url}:{title}"
    return hashlib.sha256(raw.encode()).hexdigest()[:32]
