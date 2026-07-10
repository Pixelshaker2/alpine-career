FROM python:3.12-slim

# System-Dependencies: WeasyPrint (PDF-Generierung) benoetigt cairo + pango
RUN apt-get update && apt-get install -y --no-install-recommends \
    libffi-dev \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libglib2.0-0 \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Dependencies installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Source Code kopieren
COPY src/ src/
COPY alembic/ alembic/
COPY alembic.ini .

# Datenverzeichnis
RUN mkdir -p /app/data

CMD ["python", "-m", "src.bot.main"]
