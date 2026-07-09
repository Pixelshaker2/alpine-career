# CONTRIBUTING.md -- Beitragsrichtlinien

Vielen Dank fuer dein Interesse an Alpine Career. Dieses Dokument beschreibt, wie du zum Projekt beitragen kannst -- sei es durch Code, Dokumentation oder Fehlermeldungen.

## Voraussetzungen

Bevor du loslegst, lies bitte:

- [README.md](../../README.md) -- Projektuebersicht und Vision
- [CLAUDE.md](../../CLAUDE.md) -- Entwicklungsregeln (auch fuer menschliche Entwickler relevant)
- [AGENTS.md](../ai/AGENTS.md) -- Agenten-Architektur

## Entwicklungsumgebung einrichten

### Systemvoraussetzungen

- Python 3.12 oder neuer
- Docker und Docker Compose
- Git
- PostgreSQL 16+ (lokal oder via Docker)
- Redis 7+ (lokal oder via Docker)

### Setup

```bash
# Repository klonen
git clone <repo-url>
cd alpine-career

# Virtuelle Umgebung erstellen
python -m venv .venv
source .venv/bin/activate

# Abhaengigkeiten installieren
pip install -e ".[dev]"

# Umgebungsvariablen konfigurieren
cp .env.example .env
# .env mit eigenen Werten befuellen

# Datenbank und Redis starten
docker compose up -d postgres redis

# Datenbankmigrationen ausfuehren
alembic upgrade head

# Tests ausfuehren
pytest
```

### Editor-Setup

- Empfohlen: VS Code oder PyCharm
- Ruff-Extension installieren fuer automatische Formatierung
- Python-Typ-Pruefung aktivieren (mypy oder pyright)

## Branch-Namenskonvention

Jeder Branch folgt diesem Schema:

```
<typ>/<kurze-beschreibung>
```

### Erlaubte Typen

| Typ | Verwendung | Beispiel |
|---|---|---|
| `feature/` | Neues Feature | `feature/lebenslauf-parser` |
| `fix/` | Bugfix | `fix/tenant-filter-fehlt` |
| `docs/` | Dokumentation | `docs/api-beschreibung-career` |
| `refactor/` | Umstrukturierung | `refactor/service-layer-career` |
| `test/` | Tests hinzufuegen | `test/job-matching-unit-tests` |
| `chore/` | Build, CI, Tooling | `chore/docker-compose-update` |

### Regeln

- Immer von `main` abzweigen
- Beschreibung in Kleinbuchstaben, Woerter mit Bindestrich trennen
- Kurz und praegnant (max. 5 Woerter)
- Keine Issue-Nummern im Branch-Namen (gehoeren in die Commit-Message)

## Commit-Message-Format

Wir verwenden **Conventional Commits** auf Deutsch. Vollstaendige Regeln stehen in [CLAUDE.md](CLAUDE.md).

```
<typ>(<scope>): <beschreibung>

[optionaler body mit mehr Details]

[optionaler footer, z.B. Closes #42]
```

### Beispiele

```
feat(career): Job-Matching-Score berechnen
fix(core): Race Condition beim Tenant-Lookup behoben
docs(agents): Lebenszyklus-Dokumentation ergaenzt
test(career): Unit Tests fuer ApplicationService hinzugefuegt
chore(ci): GitHub Actions Pipeline konfiguriert
```

### Regeln

- Erste Zeile maximal 72 Zeichen
- Beschreibung im Imperativ: "Score berechnen", nicht "Score berechnet"
- Scope ist optional, aber empfohlen (z.B. `career`, `core`, `shared`)
- Body erklaert das *Warum*, nicht das *Was* (das sieht man im Diff)

## Pull-Request-Prozess

### Einen PR erstellen

1. **Branch erstellen** nach der Namenskonvention
2. **Aenderungen committen** mit korrekten Commit-Messages
3. **Tests lokal ausfuehren** und sicherstellen, dass alles besteht
4. **PR erstellen** mit ausgefuelltem Template:
   - Was wurde geaendert?
   - Warum wurde es geaendert?
   - Wie kann man es testen?
   - Screenshots (falls UI-relevant)
5. **Review anfordern**

### PR-Regeln

- Maximal **400 Zeilen** geaenderter Code (ohne generierte Dateien und Migrationen)
- Jeder PR loest **ein** Problem oder fuegt **ein** Feature hinzu
- PR-Titel folgt dem Conventional-Commits-Format
- Beschreibung ist vollstaendig und verstaendlich
- Alle CI-Checks muessen bestehen
- Mindestens ein Approval erforderlich

### Grosse Aenderungen

Fuer Aenderungen ueber 400 Zeilen:

- In mehrere PRs aufteilen
- Reihenfolge der PRs dokumentieren
- Jeden PR einzeln reviewen lassen

## Code-Review-Checkliste

Reviewer pruefen jeden PR anhand dieser Checkliste:

### Korrektheit

- [ ] Loest der Code das beschriebene Problem?
- [ ] Gibt es Edge Cases, die nicht behandelt werden?
- [ ] Sind Fehler korrekt behandelt (keine stillen Failures)?

### Architektur

- [ ] Schichtentrennung eingehalten (siehe CLAUDE.md)?
- [ ] Keine zirkulaeren Imports?
- [ ] Dependency Injection korrekt angewendet?
- [ ] Kein Agent importiert von einem anderen Agenten?

### Sicherheit

- [ ] Keine Secrets im Code?
- [ ] Tenant-Isolation in allen DB-Abfragen?
- [ ] Keine personenbezogenen Daten in Logs?
- [ ] SQL-Injection ausgeschlossen (parametrisierte Queries)?

### Qualitaet

- [ ] Typ-Annotationen vollstaendig?
- [ ] Keine `Any`-Typen, keine `print()`-Statements?
- [ ] Keine hartcodierten Werte?
- [ ] Code ist lesbar und selbsterklaerend?

### Tests

- [ ] Unit Tests fuer neue Domain-Logik vorhanden?
- [ ] Integration Tests fuer neue Services vorhanden?
- [ ] Bestehende Tests nicht gebrochen?
- [ ] Coverage mindestens 80% fuer neuen Code?

## Testing

### Test-Hierarchie

1. **Unit Tests** -- Domain-Logik isoliert testen, keine externen Abhaengigkeiten
2. **Integration Tests** -- Services mit gemockten Repositories und APIs testen
3. **API Tests** -- Endpunkte mit TestClient testen (FastAPI)
4. **End-to-End Tests** -- Kritische Workflows komplett durchspielen

### Namenskonvention fuer Tests

```
tests/
  agents/
    career/
      test_job_matching.py        # Unit Tests
      test_application_service.py # Integration Tests
  core/
    test_auth_middleware.py
  api/
    test_career_endpoints.py      # API Tests
```

### Tests ausfuehren

```bash
# Alle Tests
pytest

# Nur Unit Tests
pytest tests/agents/ -m unit

# Mit Coverage-Report
pytest --cov=src --cov-report=html

# Bestimmter Agent
pytest tests/agents/career/
```

## Dokumentation

### Was muss dokumentiert werden?

- Jedes neue Modul: Docstring im `__init__.py`
- Jede oeffentliche Funktion: Docstring mit Parametern und Rueckgabewert
- Jeder API-Endpunkt: OpenAPI-Beschreibung via FastAPI
- Jede Architekturentscheidung: ADR in `docs/adr/`
- Jede Aenderung: Eintrag in CHANGELOG.md

### Sprache

- Code-Dokumentation (Docstrings): Englisch
- Projekt-Dokumentation (Markdown): Deutsch, Schweizer Rechtschreibung
- Kein Eszett -- immer `ss` verwenden

## Fragen und Hilfe

Bei Fragen zum Beitragsprozess, erstelle ein Issue mit dem Label `question`. Fuer Diskussionen ueber Architekturentscheidungen, nutze Issues mit dem Label `discussion`.
