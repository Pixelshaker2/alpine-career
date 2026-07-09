# CLAUDE.md -- Entwicklungsregeln fuer KI-Assistenten

Dieses Dokument definiert verbindliche Regeln fuer alle KI-Assistenten (Claude, Copilot, etc.), die an diesem Projekt arbeiten. Jeder Code, jede Aenderung und jede Entscheidung muss diesen Regeln entsprechen.

## Sprache und Rechtschreibung

- Alle Dokumentation, Kommentare und Commit-Messages werden auf **Deutsch** verfasst
- **Schweizer Rechtschreibung**: Kein Eszett (ss). Immer `ss` statt `ss`. Beispiele: `Strasse`, `Gruss`, `Fussball`, `dass`, `muss`
- Code (Variablennamen, Funktionsnamen, Klassennamen) wird auf **Englisch** geschrieben
- Docstrings in Python-Code: Englisch
- User-facing Texte (E-Mails, UI): Deutsch mit Schweizer Rechtschreibung

## Python Code Style

### Allgemein

- Python 3.12+ als Mindestversion
- Typ-Annotationen sind **Pflicht** fuer alle Funktionssignaturen und Rueckgabewerte
- `ruff` als Linter und Formatter (Konfiguration in `pyproject.toml`)
- Maximale Zeilenlaenge: 100 Zeichen
- Imports werden nach Standard Library, Third Party, Local gruppiert

### Namenskonventionen

- Klassen: `PascalCase` (z.B. `JobApplication`, `CareerAgent`)
- Funktionen und Methoden: `snake_case` (z.B. `create_application`, `get_user_profile`)
- Konstanten: `UPPER_SNAKE_CASE` (z.B. `MAX_RETRY_COUNT`, `DEFAULT_TIMEOUT`)
- Private Attribute: Einfacher Unterstrich `_internal_state`
- Module und Pakete: `snake_case` (z.B. `job_matching`, `email_service`)
- Keine Abkuerzungen ausser gaengige (z.B. `id`, `url`, `api`, `db`)

### Pydantic

- Alle API-Schemas als Pydantic v2 `BaseModel`
- Domain-Entitaeten als eigene Klassen, nicht als Pydantic-Modelle
- Validierung gehoert in die Schemas, Geschaeftslogik in die Domain

## Architektur-Regeln

### Schichtentrennung (strikt einzuhalten)

```
api/          -> Darf nur services/ importieren
services/     -> Darf domain/ und shared/ importieren
domain/       -> Darf NUR shared/utils importieren, KEINE externen Abhaengigkeiten
integrations/ -> Implementiert Interfaces aus domain/, darf externe APIs aufrufen
```

### Wo gehoert was hin?

| Element | Verzeichnis | Beispiel |
|---|---|---|
| FastAPI-Router | `agents/<name>/api/` | `router.py`, `schemas.py` |
| Use Cases | `agents/<name>/services/` | `application_service.py` |
| Entitaeten, Value Objects | `agents/<name>/domain/` | `job_application.py` |
| Repository-Interfaces | `agents/<name>/domain/` | `repositories.py` |
| Repository-Implementierungen | `agents/<name>/integrations/` | `postgres_repo.py` |
| Externe API-Clients | `agents/<name>/integrations/` | `gmail_client.py` |
| Gemeinsame Modelle | `shared/models/` | `user.py`, `tenant.py` |
| Hilfsfunktionen | `shared/utils/` | `date_utils.py` |
| Middleware, Auth | `core/` | `auth_middleware.py` |

### Dependency Injection

- Alle Services erhalten ihre Abhaengigkeiten ueber den Konstruktor
- FastAPI `Depends()` fuer Request-Scope-Abhaengigkeiten
- Keine globalen Singletons ausser Konfiguration

## Commit-Messages

Format: **Conventional Commits** auf Deutsch.

```
<typ>(<scope>): <beschreibung>

[optionaler body]

[optionaler footer]
```

### Erlaubte Typen

- `feat`: Neues Feature
- `fix`: Bugfix
- `docs`: Nur Dokumentation
- `style`: Formatierung (kein Code-Aenderung)
- `refactor`: Weder Feature noch Bugfix
- `test`: Tests hinzufuegen oder korrigieren
- `chore`: Build, CI, Abhaengigkeiten

### Beispiele

```
feat(career): Lebenslauf-Parser implementiert
fix(core): Tenant-ID wird korrekt aus JWT extrahiert
docs(agents): Agenten-Lebenszyklus dokumentiert
```

## Pull-Request-Regeln

- Jeder PR braucht eine Beschreibung mit Kontext und Motivation
- Maximal 400 Zeilen geaenderter Code pro PR (ohne generierte Dateien)
- Mindestens ein Review erforderlich
- Alle Tests muessen bestehen
- Keine `TODO`-Kommentare ohne verlinktes Issue
- PR-Titel folgt dem Conventional-Commits-Format

## Was NICHT gemacht werden darf

### Sicherheit

- **Keine Secrets im Code** -- Alle Zugangsdaten gehoeren in Umgebungsvariablen oder einen Secret Manager
- **Keine Tenant-Daten mischen** -- Jede Datenbankabfrage MUSS nach `tenant_id` filtern
- **Keine SQL-Strings zusammenbauen** -- Immer parametrisierte Queries oder ORM verwenden

### Geschaeftslogik

- **Keine Bewerbungen automatisch absenden** -- Der Nutzer muss jeden Versand explizit bestaetigen
- **Keine Entscheidungen fuer den Nutzer treffen** -- Der Agent schlaegt vor, der Nutzer entscheidet
- **Keine personenbezogenen Daten loggen** -- Weder Namen, E-Mails noch Lebenslaufinhalte in Logs

### Code-Qualitaet

- **Keine `Any`-Typen** -- Immer konkrete Typen verwenden
- **Keine `print()`-Statements** -- Logging-Framework verwenden
- **Keine hartcodierten Werte** -- Konfiguration ueber Settings-Klassen
- **Keine zirkulaeren Imports** -- Die Schichtenarchitektur verhindert dies, wenn korrekt umgesetzt

## Testing

- Minimum 80% Code-Coverage fuer neue Features
- Unit Tests fuer Domain-Logik (keine externen Abhaengigkeiten)
- Integration Tests fuer Services (mit Mocks fuer externe APIs)
- End-to-End Tests fuer kritische API-Flows
- Test-Dateien: `tests/<agent>/test_<modul>.py`
- Fixtures und Factories statt hartcodierter Testdaten
- `pytest` als Test-Framework, `pytest-asyncio` fuer async Code

## Dokumentation

- Jedes neue Modul erhaelt einen Docstring im `__init__.py`
- Komplexe Geschaeftslogik wird mit Inline-Kommentaren erklaert
- API-Endpunkte werden mit OpenAPI-Beschreibungen versehen (FastAPI generiert automatisch)
- Architekturentscheidungen werden als ADR (Architecture Decision Record) festgehalten
- CHANGELOG.md wird bei jeder relevanten Aenderung aktualisiert
