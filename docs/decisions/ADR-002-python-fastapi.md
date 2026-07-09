# ADR-002: Python und FastAPI als Technologie-Stack

- **Status:** Akzeptiert
- **Datum:** 2026-07-02
- **Beteiligte:** David Gabriel

## Kontext

alpine-career benoetigt ein Backend-Framework, das folgende Anforderungen erfuellt:

- **Hohe Performance** fuer API-Requests, insbesondere bei gleichzeitigen AI-Aufrufen (Claude API) und externen Integrationen (Gmail, Google Drive, Telegram)
- **Modernes API-Design** mit automatischer Dokumentation und Validierung
- **AI-Oekosystem-Kompatibilitaet**: Die meisten AI/ML-Bibliotheken und SDKs sind Python-native (Anthropic SDK, LangChain, etc.)
- **Entwicklerproduktivitaet**: Schnelle Iteration, gute Debugging-Moeglichkeiten
- **Typsicherheit** zur Reduktion von Laufzeitfehlern
- **Async-Support** fuer parallele I/O-Operationen (API-Calls, Datenbank-Queries)

Das Framework wird die Grundlage fuer alle API-Endpunkte, die Agent-Kommunikation und die Integration mit Drittanbietern bilden.

## Entscheidung

Wir verwenden **Python 3.12+** mit **FastAPI** als Web-Framework.

Kern-Stack:

| Komponente | Technologie |
|-----------|-------------|
| Sprache | Python 3.12+ |
| Web-Framework | FastAPI |
| ASGI-Server | Uvicorn |
| ORM | SQLAlchemy 2.0 (async) |
| Validierung | Pydantic v2 |
| Migrations | Alembic |
| Task Queue | Celery oder ARQ (async) |
| HTTP-Client | httpx (async) |

## Begruendung

### Performance

FastAPI ist eines der schnellsten Python-Frameworks. Durch den nativen Async-Support (ASGI) kann der Server waehrend wartender I/O-Operationen (z.B. Claude-API-Aufruf) andere Requests bearbeiten. Das ist entscheidend fuer alpine-career, wo viele Requests auf externe APIs warten.

### Automatische API-Dokumentation

FastAPI generiert automatisch OpenAPI-Spezifikationen (Swagger UI und ReDoc) aus den Type Hints und Pydantic-Modellen. Das spart Dokumentationsaufwand und haelt die API-Dokumentation immer synchron mit dem Code.

### Type Hints und Pydantic

Python Type Hints in Kombination mit Pydantic v2 bieten:

- Automatische Request-Validierung mit klaren Fehlermeldungen
- IDE-Unterstuetzung (Autovervollstaendigung, Refactoring)
- Serialisierung und Deserialisierung out of the box
- Schema-Generierung fuer API-Clients

### AI-Oekosystem

Python ist die Standardsprache im AI-Bereich. Das Anthropic SDK, die meisten Embedding-Bibliotheken und Tooling-Frameworks sind Python-first. Die Wahl von Python vermeidet Sprach-Bridging und ermoeglicht direkten Zugriff auf das gesamte AI-Oekosystem.

### Dependency Injection

FastAPI bietet ein elegantes Dependency-Injection-System, das sich gut mit Clean Architecture vereinbaren laesst. Services, Repositories und Use Cases koennen sauber injiziert werden, ohne externes DI-Framework.

### Developer Experience

- Hot Reload waehrend der Entwicklung (Uvicorn --reload)
- Klare Fehlermeldungen bei Validierungsfehlern
- Testbarkeit durch Dependency Injection und httpx TestClient
- Grosse Community und umfangreiche Dokumentation

## Konsequenzen

### Positiv

- Schnelle API-Entwicklung mit automatischer Dokumentation
- Direkter Zugriff auf das Python-AI-Oekosystem ohne Sprachbrueche
- Typsicherheit reduziert Laufzeitfehler signifikant
- Async-Support ermoeglicht effiziente Ressourcennutzung
- Pydantic-Modelle dienen gleichzeitig als API-Schema und Validierung
- Umfangreiche Drittanbieter-Bibliotheken fuer alle Integrationen

### Negativ

- **Python-Expertise noetig:** Gute Python-Kenntnisse (insbesondere async/await, Type Hints) sind Voraussetzung fuer die Mitarbeit am Projekt
- **Async-Komplexitaet:** Asynchroner Code kann schwieriger zu debuggen sein. Race Conditions und Deadlocks erfordern sorgfaeltigen Umgang mit Concurrency
- **GIL-Limitation:** Pythons Global Interpreter Lock limitiert echte CPU-Parallelitaet. Fuer alpine-career ist das unkritisch (I/O-bound Workload), muss aber fuer potenzielle CPU-intensive Aufgaben bedacht werden
- **Deployment-Groesse:** Python-Anwendungen mit allen Dependencies sind groesser als kompilierte Go-Binaries

## Alternativen

### Django REST Framework

- **Vorteile:** Umfangreiches Oekosystem, Admin-Interface, Batteries-included, grosse Community
- **Nachteile:** Synchron by default (async erst spaet und unvollstaendig), schwerfaelliger als FastAPI, Admin-Interface wird nicht benoetigt
- **Verworfen:** Zu viel Overhead fuer ein API-only-Projekt, schlechtere Async-Unterstuetzung

### Flask

- **Vorteile:** Minimalistisch, einfach zu lernen, flexible Struktur
- **Nachteile:** Kein nativer Async-Support, keine automatische Validierung, keine automatische API-Doku, erfordert viele Erweiterungen
- **Verworfen:** FastAPI bietet alles, was Flask kann, plus deutlich mehr out of the box

### Go (Gin/Echo/Fiber)

- **Vorteile:** Exzellente Performance, native Concurrency (Goroutines), kompilierte Binaries, kleiner Footprint
- **Nachteile:** AI-Oekosystem ist deutlich kleiner, kein Pydantic-Aequivalent, laengere Entwicklungszeit fuer API-Features, weniger Drittanbieter-Integrationen
- **Verworfen:** Der Vorteil der Go-Performance ueberwiegt nicht den Nachteil der schlechteren AI-Integration und langsameren Feature-Entwicklung
