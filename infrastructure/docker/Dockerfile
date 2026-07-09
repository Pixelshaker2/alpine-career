FROM python:3.12-slim

# System-Dependencies fuer WeasyPrint
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    libcairo2 \
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
