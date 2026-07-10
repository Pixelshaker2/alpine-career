"""Job scrapers — multiple sources for job search.

Each scraper module implements a search function that returns
a list of ScrapedJob objects. The main orchestrator in
job_scraper.py combines results from all sources.
"""

from src.services.scrapers.base import ScrapedJob

__all__ = ["ScrapedJob"]
