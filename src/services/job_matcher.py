"""Job matcher — scores how well a job matches Marcos profile.

Phase 1: Keyword-based scoring (no API costs).
Phase 2: Claude API for semantic matching (later).
"""

import logging

from src.models.job import Job

logger = logging.getLogger(__name__)

# Gewichtete Keywords aus Marcos Profil
SKILL_KEYWORDS = {
    # Core skills (hohe Gewichtung)
    "microsoft 365": 15,
    "m365": 15,
    "azure": 15,
    "entra id": 12,
    "active directory": 10,
    "intune": 10,
    "exchange online": 10,
    "sharepoint": 8,
    "teams": 5,
    "windows server": 8,
    "powershell": 10,
    "cloud": 8,
    "modern workplace": 12,
    # Zertifizierungen
    "az-104": 12,
    "az-900": 8,
    "az-500": 10,
    "itil": 8,
    "security+": 6,
    # Rollen-Keywords
    "system administrator": 10,
    "systemadministrator": 10,
    "cloud administrator": 12,
    "cloud engineer": 10,
    "it administrator": 8,
    "workplace engineer": 10,
    "it support": 5,
}

# Negative Keywords (Branchen-No-Go)
NEGATIVE_KEYWORDS = {
    "abfall": -20,
    "entsorgung": -20,
    "waste": -20,
    "müllabfuhr": -20,
}

MAX_SCORE = 100


def score_job(job: Job) -> float:
    """Calculate match score (0-100) for a job based on keyword matching.

    Args:
        job: Job model instance.

    Returns:
        Score between 0 and 100.
    """
    text = f"{job.title} {job.description or ''} {job.company}".lower()
    raw_score = 0

    for keyword, weight in SKILL_KEYWORDS.items():
        if keyword in text:
            raw_score += weight

    for keyword, penalty in NEGATIVE_KEYWORDS.items():
        if keyword in text:
            raw_score += penalty  # penalty ist negativ

    # Normalisieren auf 0-100
    # Max erreichbar waere ~150 bei perfektem Match
    score = min(max(raw_score / 1.5, 0), MAX_SCORE)
    return round(score, 1)


def score_jobs(jobs: list[Job]) -> list[tuple[Job, float]]:
    """Score and sort jobs by match quality.

    Returns:
        List of (job, score) tuples, sorted by score descending.
    """
    scored = [(job, score_job(job)) for job in jobs]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored
