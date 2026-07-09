FROM python:3.12-slim

# System-Dependencies (WeasyPrint erst in Sprint 3)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Dependencies installieren
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# Source Code kopieren
COPY src/ src/
COPY alembic/ alembic/
COPY alembic.ini .

# Datenverzeichnis
RUN mkdir -p /app/data

CMD ["python", "-m", "src.bot.main"]
