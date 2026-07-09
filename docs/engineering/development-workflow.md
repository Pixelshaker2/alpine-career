# Development Workflow

> Letzte Aktualisierung: 2026-07-02

## Uebersicht

Diese Dokumentation beschreibt den lokalen Entwicklungs-Workflow fuer alpine-career. Sie richtet sich an alle Entwickler, die am Projekt mitarbeiten.

## Voraussetzungen

Folgende Tools muessen installiert sein:

| Tool           | Version   | Zweck                              |
|----------------|-----------|-------------------------------------|
| Python         | >= 3.12   | Laufzeitumgebung                    |
| Docker         | >= 24.0   | Container-Runtime                   |
| Docker Compose | >= 2.20   | Multi-Container-Orchestrierung      |
| Git            | >= 2.40   | Versionskontrolle                   |
| uv             | >= 0.4    | Python-Paketmanager und Virtualenv  |

## Lokale Entwicklungsumgebung einrichten

### 1. Repository klonen

```bash
git clone git@github.com:alpine-career/alpine-career.git
cd alpine-career
```

### 2. Python-Umgebung erstellen

```bash
# Virtualenv erstellen und Abhaengigkeiten installieren
uv sync

# Virtualenv aktivieren
source .venv/bin/activate
```

### 3. Pre-Commit Hooks installieren

```bash
uv run pre-commit install
```

### 4. Infrastruktur starten

```bash
# PostgreSQL und Redis starten
docker compose up -d db redis
```

### 5. Datenbank initialisieren

```bash
# Migrationen ausfuehren
alembic upgrade head

# Optional: Testdaten laden
python scripts/seed_database.py
```

## Umgebungsvariablen

Umgebungsvariablen werden ueber eine `.env`-Datei im Root-Verzeichnis konfiguriert. Eine Vorlage liegt unter `.env.example`:

```bash
# Aus Vorlage kopieren
cp .env.example .env
```

### Pflicht-Variablen (lokal)

```env
# Datenbank
DATABASE_URL=postgresql+asyncpg://alpine_career:alpine_career@localhost:5432/alpine_career

# Redis
REDIS_URL=redis://localhost:6379/0

# Applikation
SECRET_KEY=local-development-secret-key-change-in-production
ENVIRONMENT=local
LOG_LEVEL=DEBUG
DEBUG=true

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

### Optionale Variablen

```env
# Externe Services (fuer Integration-Tests)
OPENAI_API_KEY=sk-...
SMTP_HOST=localhost
SMTP_PORT=1025
```

Sensible Variablen (API-Keys, Secrets) werden **niemals** ins Git committed. Die `.env`-Datei ist in `.gitignore` eingetragen.

## Datenbank-Setup

### PostgreSQL via Docker

```bash
# Container starten
docker compose up -d db

# Verbindung pruefen
docker compose exec db psql -U alpine_career -d alpine_career -c "SELECT 1;"
```

### Migrationen

```bash
# Alle Migrationen ausfuehren
alembic upgrade head

# Neue Migration erstellen
alembic revision --autogenerate -m "beschreibung_der_aenderung"

# Letzte Migration rueckgaengig machen
alembic downgrade -1

# Migrationsstatus anzeigen
alembic current
alembic history
```

### Datenbank zuruecksetzen

```bash
# Komplette Datenbank loeschen und neu erstellen
docker compose exec db dropdb -U alpine_career alpine_career
docker compose exec db createdb -U alpine_career alpine_career
alembic upgrade head
```

## Applikation starten

### Entwicklungsserver

```bash
# FastAPI mit Auto-Reload starten
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Die API ist dann unter `http://localhost:8000` erreichbar. Die automatisch generierte API-Dokumentation ist unter:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Alles via Docker Compose

```bash
# Gesamtes System starten (App + DB + Redis)
docker compose up

# Im Hintergrund starten
docker compose up -d

# Logs anzeigen
docker compose logs -f app
```

## Tests ausfuehren

```bash
# Alle Tests
pytest

# Nur Unit Tests
pytest tests/unit

# Nur Integration Tests
pytest tests/integration

# Mit Coverage-Report
pytest --cov=src --cov-report=term-missing

# Einzelne Testdatei
pytest tests/unit/core/test_auth.py

# Einzelnen Test
pytest tests/unit/core/test_auth.py::test_create_token_with_valid_user_returns_jwt

# Tests parallel ausfuehren
pytest -n auto

# Nur fehlgeschlagene Tests erneut ausfuehren
pytest --lf
```

### Test-Datenbank

Integration-Tests verwenden eine separate Datenbank:

```bash
# Test-Datenbank wird automatisch erstellt/zurueckgesetzt
# Konfiguration in tests/conftest.py
DATABASE_URL_TEST=postgresql+asyncpg://alpine_career:alpine_career@localhost:5432/alpine_career_test
```

## Code-Qualitaet

### Linting und Formatierung

```bash
# Linting mit ruff
ruff check src/ tests/

# Automatische Korrektur
ruff check --fix src/ tests/

# Formatierung
ruff format src/ tests/

# Formatierung pruefen (ohne Aenderung)
ruff format --check src/ tests/
```

### Type Checking

```bash
# Type Checking mit mypy
mypy src/
```

### Alle Checks auf einmal

```bash
# Pre-Commit fuer alle Dateien ausfuehren
pre-commit run --all-files
```

### Pre-Commit Konfiguration

Die `.pre-commit-config.yaml` enthaelt:

- ruff (Linting und Formatierung)
- mypy (Type Checking)
- detect-secrets (Secret Scanning)
- check-yaml, check-toml (Syntax-Checks)

## Debugging

### Python Debugger

```python
# Breakpoint im Code setzen
breakpoint()  # Startet pdb

# Oder mit ipdb (falls installiert)
import ipdb; ipdb.set_trace()
```

### Logging hochsetzen

```bash
# In der .env Datei
LOG_LEVEL=DEBUG
```

### Datenbank-Queries anzeigen

```bash
# SQLAlchemy Echo-Modus aktivieren
SQLALCHEMY_ECHO=true uvicorn src.main:app --reload
```

### Docker Container inspizieren

```bash
# Shell in Container oeffnen
docker compose exec app bash

# Logs eines Services anzeigen
docker compose logs -f app

# Datenbank inspizieren
docker compose exec db psql -U alpine_career -d alpine_career
```

### HTTP-Requests testen

```bash
# Mit httpie (empfohlen)
http GET localhost:8000/health
http POST localhost:8000/api/v1/auth/login email=test@example.com password=test

# Oder mit curl
curl -s localhost:8000/health | python -m json.tool
```

## IDE-Setup

### VS Code (empfohlen)

Empfohlene Extensions:

| Extension             | Zweck                          |
|-----------------------|--------------------------------|
| Python                | Python-Support                 |
| Pylance               | Type Checking und IntelliSense |
| Ruff                  | Linting und Formatierung       |
| Docker                | Docker-Support                 |
| GitLens               | Git-Integration                |
| Thunder Client        | API-Testing                    |

Empfohlene `settings.json`:

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll.ruff": "explicit",
      "source.organizeImports.ruff": "explicit"
    }
  },
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests"]
}
```

### PyCharm / IntelliJ

- Python Interpreter auf `.venv/bin/python` setzen
- pytest als Test-Runner konfigurieren
- ruff als External Tool einrichten
- Docker-Integration aktivieren
