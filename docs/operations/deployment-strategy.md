# Deployment-Strategie

> Letzte Aktualisierung: 2026-07-02

## Uebersicht

alpine-career wird als Docker-basierte Applikation auf Hetzner Cloud betrieben. Diese Dokumentation beschreibt den gesamten Deployment-Prozess von der lokalen Entwicklung bis zur Produktion.

## Umgebungen

| Umgebung    | Zweck                          | URL                              | Infrastruktur        |
|-------------|--------------------------------|----------------------------------|----------------------|
| Local       | Entwicklung und Debugging      | http://localhost:8000            | Docker Compose       |
| Staging     | Integrationstests, QA          | https://staging.alpine-career.ch    | Hetzner VPS (CX22)   |
| Production  | Live-System fuer Endnutzer     | https://app.alpine-career.ch        | Hetzner VPS (CX32)   |

Jede Umgebung hat ihre eigene Datenbank und ihren eigenen Redis-Instance.

## Docker-basiertes Deployment

Die Applikation wird als Multi-Container-Setup betrieben:

```yaml
# docker-compose.prod.yml (vereinfacht)
services:
  app:
    image: ghcr.io/alpine-career/api:${VERSION}
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    depends_on:
      - db
      - redis
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: postgres:16-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
      - "80:80"
```

## Hetzner Cloud Setup

Die Infrastruktur auf Hetzner Cloud ist wie folgt aufgebaut:

- **VPS**: CX32 (4 vCPU, 8 GB RAM, 80 GB SSD) fuer Produktion
- **Netzwerk**: Privates Netzwerk zwischen den Servern
- **Firewall**: Nur Ports 80, 443 und 22 (SSH mit Key-Auth) offen
- **DNS**: Verwaltet ueber Hetzner DNS
- **Backups**: Automatische Server-Snapshots (taeglich)
- **Floating IP**: Fuer zukuenftige Failover-Szenarien reserviert

## CI/CD Pipeline (GitHub Actions)

Der Deployment-Prozess ist vollstaendig automatisiert:

```
Push auf main → Tests → Build → Deploy auf Staging → Smoke Tests → Deploy auf Produktion
```

### Pipeline-Schritte

1. **Lint & Type-Check**: ruff, mypy
2. **Unit Tests**: pytest mit Coverage-Check
3. **Integration Tests**: Mit Docker-Compose-Services
4. **Docker Build**: Multi-Stage-Build, Image wird auf GHCR gepusht
5. **Deploy Staging**: Automatisch nach erfolgreichem Build
6. **Smoke Tests**: Automatische Health-Check-Validierung auf Staging
7. **Deploy Production**: Manueller Trigger (Approval erforderlich)

```yaml
# .github/workflows/deploy.yml (vereinfacht)
on:
  push:
    branches: [main]

jobs:
  deploy-staging:
    needs: [test, build]
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Staging
        run: |
          ssh deploy@staging.alpine-career.ch \
            "cd /opt/alpine-career && docker compose pull && docker compose up -d"

  deploy-production:
    needs: [deploy-staging, smoke-tests]
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Deploy to Production
        run: |
          ssh deploy@app.alpine-career.ch \
            "cd /opt/alpine-career && ./scripts/deploy.sh ${GITHUB_SHA}"
```

## Datenbank-Migrationen (Alembic)

Datenbankmigrationen werden mit Alembic verwaltet:

- Migrationen befinden sich unter `src/core/database/migrations/`
- Neue Migrationen werden mit `alembic revision --autogenerate -m "beschreibung"` erstellt
- Migrationen werden vor dem App-Start automatisch ausgefuehrt
- Jede Migration muss eine `downgrade()`-Funktion enthalten
- Destruktive Migrationen (DROP TABLE, DROP COLUMN) erfordern ein separates Review

```bash
# Migration erstellen
alembic revision --autogenerate -m "add_agent_status_column"

# Migration ausfuehren
alembic upgrade head

# Migration rueckgaengig machen
alembic downgrade -1
```

## Zero-Downtime Deployment

Zero-Downtime wird durch folgende Massnahmen sichergestellt:

1. **Rolling Updates**: Nginx leitet Traffic erst zum neuen Container, wenn der Health-Check erfolgreich ist
2. **Graceful Shutdown**: Die App verarbeitet laufende Requests fertig, bevor sie sich beendet (SIGTERM-Handler)
3. **Backward-kompatible Migrationen**: Schema-Aenderungen muessen mit der alten und neuen Applikationsversion funktionieren
4. **Connection Draining**: Bestehende Verbindungen werden nicht abrupt beendet

## Rollback-Strategie

Im Fehlerfall kann schnell auf die vorherige Version zurueckgesetzt werden:

```bash
# Rollback auf vorherige Version
./scripts/rollback.sh

# Der Script macht Folgendes:
# 1. Stoppt den aktuellen Container
# 2. Startet den Container mit dem vorherigen Image-Tag
# 3. Prueft den Health-Check
# 4. Bei Bedarf: alembic downgrade -1
```

- Alle Docker-Images der letzten 10 Releases werden im Registry aufbewahrt
- Datenbank-Rollbacks sind nur moeglich, wenn die Migration reversibel ist
- Bei nicht-reversiblen Migrationen wird ein Forward-Fix bevorzugt

## Umgebungskonfiguration

Umgebungsvariablen werden nach Umgebung getrennt verwaltet:

- **Local**: `.env`-Datei (nicht im Git)
- **Staging/Production**: GitHub Secrets, injiziert via CI/CD
- **Sensible Werte**: Nur als GitHub Encrypted Secrets gespeichert

Pflicht-Variablen:

```
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/alpine_career
REDIS_URL=redis://host:6379/0
SECRET_KEY=<random-256-bit-key>
ENVIRONMENT=production|staging|local
LOG_LEVEL=INFO
CORS_ORIGINS=https://app.alpine-career.ch
```

## Health Checks

Die Applikation stellt folgende Health-Endpoints bereit:

- `GET /health` - Grundlegender Liveness-Check (HTTP 200)
- `GET /health/ready` - Readiness-Check (DB- und Redis-Verbindung)
- `GET /health/detailed` - Detaillierter Status aller Subsysteme (nur intern)

Health Checks werden von Docker, Nginx und dem Monitoring-System verwendet.

## Backup-Strategie

| Ressource     | Methode                    | Intervall  | Aufbewahrung |
|---------------|----------------------------|------------|--------------|
| PostgreSQL    | pg_dump (komprimiert)      | Taeglich   | 30 Tage      |
| Redis         | RDB Snapshots              | Stuendlich | 7 Tage       |
| Server        | Hetzner Snapshots          | Taeglich   | 7 Tage       |
| Uploads       | Rsync auf Backup-Server    | Taeglich   | 30 Tage      |

Backups werden regelmaessig auf Wiederherstellbarkeit getestet (mindestens quartalsweise).
