# Testing-Strategie

> Letzte Aktualisierung: 2026-07-02

## Uebersicht

Diese Dokumentation beschreibt die Testing-Strategie fuer alpine-career. Ziel ist es, durch eine strukturierte Testabdeckung die Qualitaet des Codes sicherzustellen und Regressionen fruehzeitig zu erkennen.

## Testpyramide

alpine-career folgt der klassischen Testpyramide:

```
        /  E2E  \          ~10% der Tests
       /----------\
      / Integration \       ~30% der Tests
     /----------------\
    /     Unit Tests    \   ~60% der Tests
   /--------------------\
```

- **Unit Tests**: Testen einzelne Funktionen und Klassen isoliert. Schnell, deterministisch, zahlreich.
- **Integration Tests**: Testen das Zusammenspiel mehrerer Komponenten (z.B. API-Endpoint mit Datenbank).
- **E2E Tests**: Testen komplette Benutzerflows ueber die gesamte Applikation hinweg.

## Coverage-Ziele

| Teststufe   | Ziel-Coverage | Messung                        |
|-------------|---------------|--------------------------------|
| Unit        | 80%           | pytest-cov, Line Coverage      |
| Integration | 60%           | pytest-cov, Branch Coverage    |
| E2E         | Kritische Pfade | Manuelle Pflege der Szenarien |

Coverage wird bei jedem Pull Request in der CI gemessen. Ein PR wird blockiert, wenn die Unit-Coverage unter 80% faellt.

## Testing-Tools

| Tool             | Zweck                                        |
|------------------|----------------------------------------------|
| pytest           | Test-Framework und Test-Runner               |
| pytest-asyncio   | Async-Tests fuer FastAPI-Endpoints            |
| httpx            | HTTP-Client fuer API-Tests (AsyncClient)      |
| factory_boy      | Test-Fixtures und Testdaten-Generierung       |
| pytest-cov       | Coverage-Messung                              |
| faker            | Generierung realistischer Testdaten           |
| respx            | Mocking externer HTTP-Aufrufe                 |
| pytest-xdist     | Parallele Testausfuehrung in der CI           |

## Testbenennung

Tests folgen einem einheitlichen Namensschema:

```
test_<was>_<bedingung>_<erwartetes_ergebnis>
```

Beispiele:

```python
def test_create_user_with_valid_data_returns_201():
    ...

def test_create_user_with_duplicate_email_raises_conflict():
    ...

def test_get_agent_without_auth_returns_401():
    ...
```

## Testorganisation

Die Teststruktur spiegelt die `src/`-Verzeichnisstruktur wider:

```
tests/
  unit/
    core/
      test_auth.py
      test_config.py
    agents/
      career/
        test_services.py
        test_domain.py
    shared/
      test_utils.py
  integration/
    api/
      test_v1_endpoints.py
    core/
      test_database.py
  e2e/
    test_user_registration_flow.py
    test_agent_execution_flow.py
  fixtures/
    factories.py
    conftest.py
```

Gemeinsame Fixtures werden in `tests/fixtures/conftest.py` definiert und per `conftest.py` in den jeweiligen Testverzeichnissen importiert.

## Mocking-Strategie

alpine-career bevorzugt Fakes gegenueber Mocks:

- **Fakes verwenden**: In-Memory-Implementierungen von Repositories, Fake-Redis-Clients, SQLite statt PostgreSQL fuer einfache Unit Tests.
- **Mocks minimieren**: `unittest.mock` nur fuer externe Services (z.B. API-Aufrufe an Drittanbieter).
- **Keine Implementierungsdetails mocken**: Tests sollen Verhalten pruefen, nicht interne Aufrufe.

```python
# Bevorzugt: Fake-Repository
class FakeUserRepository(UserRepository):
    def __init__(self):
        self.users = {}

    async def get_by_id(self, user_id: UUID) -> User:
        return self.users.get(user_id)

# Vermeiden: Uebermässiges Mocking
# mock.patch("src.agents.career.services.repository.get_by_id")
```

Fuer Datenbank-Integration-Tests wird eine dedizierte PostgreSQL-Testdatenbank verwendet, die vor jedem Testlauf zurueckgesetzt wird.

## CI-Integration

Tests werden automatisch in der GitHub Actions CI-Pipeline ausgefuehrt:

1. **Pre-Commit**: Linting und Type-Checking (ruff, mypy)
2. **Unit Tests**: Laufen bei jedem Push und PR (~2 Minuten)
3. **Integration Tests**: Laufen bei jedem PR mit Docker-Compose-Setup (~5 Minuten)
4. **E2E Tests**: Laufen nur auf dem `main`-Branch nach dem Merge (~10 Minuten)

```yaml
# Auszug aus .github/workflows/tests.yml
jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pytest tests/unit --cov=src --cov-fail-under=80

  integration-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
      redis:
        image: redis:7
    steps:
      - run: pytest tests/integration
```

## Performance-Testing

Performance-Tests werden manuell vor groesseren Releases durchgefuehrt:

- **Tool**: locust fuer Lasttests
- **Fokus**: API-Endpunkte mit hohem Traffic, Agent-Ausfuehrungen
- **Metriken**: Antwortzeit (P50, P95, P99), Durchsatz, Fehlerrate
- **Baseline**: Ergebnisse werden dokumentiert und mit frueheren Releases verglichen

Performance-Tests laufen gegen die Staging-Umgebung mit produktionsnahen Daten.

## Security-Testing

Sicherheitstests sind Teil des regulaeren Testprozesses:

- **Dependency Scanning**: Automatisch via `pip-audit` in der CI
- **SAST**: Statische Code-Analyse mit `bandit` fuer Python-spezifische Sicherheitsprobleme
- **Input Validation Tests**: Spezifische Tests fuer SQL-Injection, XSS und andere OWASP-Top-10-Schwachstellen
- **Auth-Tests**: Explizite Tests fuer Authentifizierung und Autorisierung an jedem Endpoint
- **Secret Scanning**: Pre-Commit-Hook mit `detect-secrets` zur Vermeidung versehentlich committeter Credentials

```python
# Beispiel: Security-fokussierter Test
@pytest.mark.security
def test_login_with_sql_injection_payload_returns_422():
    payload = {"email": "' OR 1=1 --", "password": "test"}
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 422
```
