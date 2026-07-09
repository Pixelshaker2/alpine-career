# Coding-Standards -- alpine-career

> Status: Entwurf | Letzte Aktualisierung: 2026-07-02

Verbindliche Regeln fuer die Code-Qualitaet im alpine-career-Projekt. Alle Pull Requests werden gegen diese Standards geprueft.

## 1. Python-Version und Tooling

- **Python:** 3.11+ (fuer `StrEnum`, `ExceptionGroup`, Performance-Verbesserungen)
- **Formatter:** Black (Zeilenlaenge 88)
- **Linter:** Ruff (ersetzt flake8, isort, pyflakes, etc.)
- **Type Checker:** mypy im strict mode
- **Package Manager:** uv (bevorzugt) oder Poetry

Alle Tools laufen in der CI-Pipeline. Code, der nicht formatiert oder nicht lint-frei ist, wird nicht gemerged.

## 2. Type Hints

Type Hints sind Pflicht auf allen oeffentlichen Funktionen und Methoden.

```python
# Richtig
def get_user_by_id(user_id: UUID, tenant_id: UUID) -> User | None:
    ...

async def create_application(
    data: ApplicationCreate,
    user_id: UUID,
) -> Application:
    ...

# Falsch
def get_user_by_id(user_id, tenant_id):
    ...
```

- `Optional[X]` wird als `X | None` geschrieben (Python 3.10+ Syntax)
- Collections: `list[str]`, `dict[str, int]`, nicht `List[str]`, `Dict[str, int]`
- Private Hilfsfunktionen: Type Hints empfohlen, aber nicht erzwungen

## 3. Docstrings

Google-Style Docstrings fuer alle oeffentlichen Klassen, Methoden und Funktionen.

```python
def match_jobs(
    profile: UserProfile,
    filters: JobSearchFilters,
) -> list[JobMatch]:
    """Findet passende Stellen fuer ein Nutzerprofil.

    Durchsucht den Stellenindex nach Uebereinstimmungen mit dem
    Nutzerprofil und den angegebenen Filtern. Ergebnisse werden
    nach Relevanz-Score sortiert.

    Args:
        profile: Das vollstaendige Nutzerprofil mit Skills und Praeferenzen.
        filters: Suchfilter (Region, Pensum, Branche).

    Returns:
        Liste von Stellenvorschlaegen, sortiert nach Relevanz (absteigend).

    Raises:
        ProfileIncompleteError: Wenn das Profil keine Skills enthaelt.
    """
```

Kein Docstring noetig fuer:
- Offensichtliche Getter/Setter
- Private Methoden mit sprechendem Namen
- Test-Methoden (der Testname ist die Dokumentation)

## 4. Namenskonventionen

### Dateien und Verzeichnisse
- snake_case: `user_profile.py`, `job_search_service.py`
- Ein Modul pro Datei (Ausnahme: eng verwandte Klassen)
- Verzeichnisse: Plural fuer Sammlungen (`models/`, `services/`, `schemas/`)

### Klassen
- PascalCase: `UserProfile`, `JobSearchService`
- Suffix nach Rolle: `UserRepository`, `ApplicationService`, `JobMatchSchema`
- Abstrakte Klassen: Praefix `Base` oder `Abstract` (`BaseRepository`)
- Interfaces/Protocols: Beschreibender Name ohne Praefix (`UserRepository` als Protocol)

### Funktionen und Methoden
- snake_case: `create_application()`, `find_matching_jobs()`
- Verben am Anfang: `get_`, `create_`, `update_`, `delete_`, `find_`, `validate_`, `calculate_`
- Boolsche Funktionen: `is_`, `has_`, `can_` (`is_active()`, `has_permission()`)
- Private: Unterstrich-Praefix (`_validate_email()`)

### Variablen
- snake_case: `user_profile`, `tenant_id`, `job_matches`
- Keine Abkuerzungen ausser allgemein bekannte: `id`, `url`, `db`, `config`
- Iterator-Variablen: Beschreibend, nicht `i`, `j` (Ausnahme: mathematische Algorithmen)
- Boolsche Variablen: `is_active`, `has_applied`, `should_notify`

### Konstanten
- UPPER_SNAKE_CASE: `MAX_RETRY_COUNT`, `DEFAULT_PAGE_SIZE`
- In eigener Datei `constants.py` oder am Anfang des Moduls

### Enums
```python
class ApplicationStatus(StrEnum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    INTERVIEW = "interview"
    REJECTED = "rejected"
    ACCEPTED = "accepted"
```

## 5. Import-Reihenfolge

Drei Bloecke, durch Leerzeilen getrennt. Ruff erzwingt dies automatisch.

```python
# 1. Standardbibliothek
from datetime import datetime
from uuid import UUID

# 2. Drittanbieter
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

# 3. Projekt-intern
from src.core.auth.dependencies import get_current_user
from src.agents.career.services.job_search import JobSearchService
```

- Keine Wildcard-Imports (`from module import *`)
- Keine relativen Imports ueber Modulgrenzen hinweg

## 6. Projekt-spezifische Patterns

### Repository Pattern
```python
class UserRepository(Protocol):
    """Port fuer Nutzerzugriff -- definiert in der Domain-Schicht."""

    async def get_by_id(self, user_id: UUID, tenant_id: UUID) -> User | None: ...
    async def save(self, user: User) -> User: ...


class PostgresUserRepository:
    """Implementierung in der Infrastruktur-Schicht."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: UUID, tenant_id: UUID) -> User | None:
        stmt = select(UserModel).where(
            UserModel.id == user_id,
            UserModel.tenant_id == tenant_id,
        )
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        return row.to_domain() if row else None
```

### Service Layer
```python
class CreateApplicationUseCase:
    """Ein Use Case pro Klasse. Klarer Name, klare Verantwortung."""

    def __init__(
        self,
        application_repo: ApplicationRepository,
        profile_repo: UserProfileRepository,
        event_bus: EventBus,
    ) -> None:
        self._application_repo = application_repo
        self._profile_repo = profile_repo
        self._event_bus = event_bus

    async def execute(self, command: CreateApplicationCommand) -> Application:
        profile = await self._profile_repo.get_by_id(command.user_id, command.tenant_id)
        if profile is None:
            raise ProfileNotFoundError(command.user_id)

        application = Application.create(
            profile=profile,
            job_id=command.job_id,
            tenant_id=command.tenant_id,
        )
        saved = await self._application_repo.save(application)
        await self._event_bus.publish(ApplicationCreated(application_id=saved.id))
        return saved
```

### DTOs / Schemas
```python
class ApplicationCreate(BaseModel):
    """Request-Schema -- API-Schicht."""
    job_id: UUID
    cover_letter_tone: str = "formal"

class ApplicationResponse(BaseModel):
    """Response-Schema -- API-Schicht."""
    id: UUID
    status: ApplicationStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
```

## 7. Fehlerbehandlung

```python
# Domain-Exceptions
class DomainError(Exception):
    """Basis fuer alle Domain-Fehler."""
    def __init__(self, message: str, code: str) -> None:
        self.message = message
        self.code = code
        super().__init__(message)

class ProfileNotFoundError(DomainError):
    def __init__(self, user_id: UUID) -> None:
        super().__init__(
            message=f"Profil nicht gefunden: {user_id}",
            code="PROFILE_NOT_FOUND",
        )

# Kein nacktes except:
# Falsch
try:
    result = await service.execute()
except:
    pass

# Richtig
try:
    result = await service.execute()
except ProfileNotFoundError:
    raise HTTPException(status_code=404, detail="Profil nicht gefunden")
except DomainError as e:
    logger.warning("Domain-Fehler", extra={"code": e.code})
    raise HTTPException(status_code=400, detail=e.message)
```

## 8. Logging

```python
import structlog

logger = structlog.get_logger(__name__)

# Strukturiert, mit Kontext
logger.info(
    "Bewerbung erstellt",
    application_id=str(application.id),
    tenant_id=str(tenant_id),
    job_id=str(job_id),
)

# Keine String-Formatierung in Logs
# Falsch
logger.info(f"Bewerbung {application.id} erstellt fuer Nutzer {user.email}")

# Richtig
logger.info("Bewerbung erstellt", application_id=str(application.id))
```

## 9. API-Endpunkte

```python
router = APIRouter(prefix="/applications", tags=["applications"])

@router.post(
    "/",
    response_model=ApplicationResponse,
    status_code=201,
    summary="Neue Bewerbung erstellen",
)
async def create_application(
    data: ApplicationCreate,
    current_user: User = Depends(get_current_user),
    use_case: CreateApplicationUseCase = Depends(get_create_application_use_case),
) -> ApplicationResponse:
    application = await use_case.execute(
        CreateApplicationCommand(
            user_id=current_user.id,
            tenant_id=current_user.tenant_id,
            job_id=data.job_id,
        )
    )
    return ApplicationResponse.model_validate(application)
```

## 10. Test-Patterns

### Namensgebung
```
tests/
  unit/
    agents/career/services/
      test_job_search_service.py
  integration/
    agents/career/api/
      test_applications_api.py
```

Testfunktionen: `test_{was_wird_getestet}_{szenario}_{erwartetes_ergebnis}`

```python
async def test_create_application_with_valid_data_returns_application():
    ...

async def test_create_application_without_profile_raises_not_found():
    ...

async def test_match_jobs_with_empty_profile_returns_empty_list():
    ...
```

### Teststruktur (Arrange-Act-Assert)
```python
async def test_create_application_with_valid_data_returns_application():
    # Arrange
    profile = make_profile(skills=["Python", "FastAPI"])
    job = make_job(required_skills=["Python"])
    use_case = CreateApplicationUseCase(
        application_repo=InMemoryApplicationRepository(),
        profile_repo=InMemoryProfileRepository(profiles=[profile]),
        event_bus=FakeEventBus(),
    )

    # Act
    result = await use_case.execute(
        CreateApplicationCommand(user_id=profile.user_id, job_id=job.id)
    )

    # Assert
    assert result.status == ApplicationStatus.DRAFT
    assert result.job_id == job.id
```

## 11. Dateistruktur pro Modul

```
agents/career/
  __init__.py
  api/
    __init__.py
    router.py          # FastAPI-Router
    schemas.py         # Request/Response-Schemas
    dependencies.py    # Dependency Injection
  domain/
    __init__.py
    entities.py        # Domain-Entitaeten
    value_objects.py   # Value Objects
    events.py          # Domain Events
    errors.py          # Domain-Exceptions
    ports.py           # Repository-Interfaces
  services/
    __init__.py
    job_search.py      # Use Case
    cv_optimizer.py    # Use Case
  integrations/
    __init__.py
    gmail_adapter.py   # Gmail API Adapter
    claude_adapter.py  # Claude API Adapter
```

## 12. Anti-Patterns (vermeiden)

- **God Classes:** Keine Klasse mit mehr als 200 Zeilen. Aufteilen.
- **Magische Strings:** Enums oder Konstanten verwenden.
- **Business-Logik in Controllern:** Gehoert in die Service- oder Domain-Schicht.
- **print() statt Logger:** Immer structlog verwenden.
- **Direkte DB-Zugriffe in Services:** Immer ueber Repositories.
- **Zirkulaere Imports:** Zeigen fehlerhafte Modulstruktur an.
- **Uebertriebene Vererbung:** Composition over Inheritance.
- **Globaler State:** Kein mutierbarer globaler Zustand. Dependency Injection verwenden.
- **Catch-all Exception Handler:** Spezifische Exceptions fangen.
- **Hartcodierte Konfiguration:** Alles ueber Umgebungsvariablen oder Config-Dateien.
- **Kommentare statt klarer Code:** Code so schreiben, dass er Kommentare ueberfluessig macht.

## Naechste Schritte

- [ ] Ruff- und Black-Konfiguration in `pyproject.toml` einrichten
- [ ] mypy-Konfiguration erstellen
- [ ] Pre-Commit-Hooks einrichten (Black, Ruff, mypy)
- [ ] Basis-Exception-Klassen implementieren
- [ ] Beispiel-Modul mit allen Patterns erstellen
