"""Insert Marco's profile into the database.

Usage: python -m src.seeds.run_seed
"""

import asyncio
import logging

from sqlalchemy import select

from src.core.database import async_session_factory
from src.models.profile import Profile
from src.models.user import User
from src.seeds.marco_profile import (
    MARCO_CV_TEXT,
    MARCO_PREFERENCES,
    MARCO_SALARY,
    MARCO_SKILLS,
    MARCO_TARGET_LOCATIONS,
    MARCO_TARGET_ROLES,
    MARCO_USER,
)

logger = logging.getLogger(__name__)


async def seed_marco() -> None:
    """Create or update Marco's user and profile."""
    async with async_session_factory() as session:
        # Check if user already exists
        result = await session.execute(
            select(User).where(User.telegram_username == MARCO_USER["telegram_username"])
        )
        user = result.scalar_one_or_none()

        if user:
            logger.info("User Marco existiert bereits — wird aktualisiert")
            user.name = MARCO_USER["name"]
            user.email = MARCO_USER["email"]
        else:
            logger.info("User Marco wird erstellt")
            user = User(
                telegram_username=MARCO_USER["telegram_username"],
                telegram_chat_id=0,  # wird beim ersten /start gesetzt
                name=MARCO_USER["name"],
                email=MARCO_USER["email"],
            )
            session.add(user)
            await session.flush()

        # Profile
        result = await session.execute(
            select(Profile).where(Profile.user_id == user.id)
        )
        profile = result.scalar_one_or_none()

        profile_data = {
            "user_id": user.id,
            "raw_cv_text": MARCO_CV_TEXT,
            "skills": MARCO_SKILLS,
            "target_roles": MARCO_TARGET_ROLES,
            "target_locations": MARCO_TARGET_LOCATIONS,
            "salary_expectations": MARCO_SALARY,
            "preferences": MARCO_PREFERENCES,
            "availability": "2026-10-01",
        }

        if profile:
            logger.info("Profil wird aktualisiert")
            for key, value in profile_data.items():
                if key != "user_id":
                    setattr(profile, key, value)
        else:
            logger.info("Profil wird erstellt")
            profile = Profile(**profile_data)
            session.add(profile)

        await session.commit()
        logger.info("Seed abgeschlossen: Marco von Burg")


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    asyncio.run(seed_marco())


if __name__ == "__main__":
    main()
