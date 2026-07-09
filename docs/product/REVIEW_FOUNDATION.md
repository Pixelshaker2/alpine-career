# Foundation Review — alpine-career

> Datum: 2026-07-02 | Phase: 0 (Foundation) abgeschlossen
> Erstellt von: CTO / Lead Architect

---

## 1. Zusammenfassung

Das Fundament fuer die alpine-career SaaS-Plattform ist erstellt. Es umfasst 65+ Dateien:
13 Root-Dokumente, 5 ADRs, 4 Engineering-Docs, 4 Operations-Docs, 33 Verzeichnisse mit .gitkeep,
6 Konfigurationsdateien und 3 GitHub-Templates.

Jedes Dokument enthaelt substanziellen Inhalt — keine leeren Platzhalter.

---

## 2. Getroffene Annahmen

| # | Annahme | Risiko | Validierung noetig |
|---|---|---|---|
| A1 | Python 3.11+ ist ausreichend fuer alle Anforderungen | Niedrig | Nein |
| A2 | Ein einzelner Entwickler startet, Team waechst spaeter | Mittel | Ja — Teamplanung |
| A3 | Hetzner Cloud bietet ausreichend Leistung und Zuverlaessigkeit | Mittel | Ja — Benchmark in Phase 1 |
| A4 | Row-Level Multi-Tenancy reicht fuer die ersten 1000 Nutzer | Mittel | Ja — Lasttest in Phase 2 |
| A5 | Google OAuth ist der einzige Auth-Provider zum Start | Niedrig | Nein |
| A6 | Claude API bleibt verfuegbar und preislich stabil | Hoch | Ja — Fallback-Strategie noetig |
| A7 | Schweizer Datenschutzgesetz (DSG) erlaubt Cloud-Hosting bei Hetzner (DE) | Hoch | Ja — rechtliche Pruefung |
| A8 | Traefik kann alle Routing-Anforderungen abdecken | Niedrig | Nein |
| A9 | Modular Monolith laesst sich spaeter sauber in Microservices aufteilen | Mittel | Ja — bei Modul-Design beachten |
| A10 | Frontend-Technologie kann spaeter entschieden werden | Niedrig | Nein |

---

## 3. Identifizierte Risiken

### Hohe Prioritaet

**R1: Abhaengigkeit von Claude API**
Die gesamte AI-Funktionalitaet haengt von einer einzigen API ab. Preisaenderungen, Rate Limits oder Ausfaelle wuerden den Kernwert der Plattform direkt betreffen.
Mitigation: Abstraktionsschicht fuer AI-Provider implementieren (Strategy Pattern). Fallback zu alternativen LLMs vorbereiten.

**R2: Datenschutz-Compliance (DSG/DSGVO)**
Nutzerdaten (Lebenslaeufe, Bewerbungen) sind hochsensibel. Hosting in Deutschland (Hetzner) muss mit Schweizer DSG kompatibel sein. Datenverarbeitung durch Claude API (Anthropic, USA) ist ein Compliance-Risiko.
Mitigation: Rechtliche Beratung einholen. Datenschutzerklaerung erstellen. Pruefen, ob Anthropic einen DPA (Data Processing Agreement) anbietet.

**R3: Single Developer / Bus Factor**
Aktuell kein Team, kein Backup. Alles Wissen liegt bei einer Person.
Mitigation: Dokumentation ist bereits umfassend. Code-Qualitaet und Tests priorisieren, damit Onboarding neuer Entwickler einfach ist.

### Mittlere Prioritaet

**R4: Scope Creep beim Career Agent**
7 Feature-Bereiche sind definiert. Versuchung ist gross, zu viel gleichzeitig zu bauen.
Mitigation: Striktes MVP-Scoping. Sprint 1-2 nur Core + Profilerstellung.

**R5: Integration-Komplexitaet**
4 externe APIs (Gmail, Drive, Telegram, Claude) erhoehen Komplexitaet und Fehlerquellen.
Mitigation: Integrationen schrittweise einfuehren. Jede Integration isoliert testen.

**R6: Multi-Tenancy Bugs**
Row-Level Isolation erfordert Disziplin bei jeder Query. Ein vergessener WHERE-Filter kann Nutzerdaten vermischen.
Mitigation: Middleware-erzwungener Tenant-Filter. Tests explizit fuer Tenant-Isolation. PostgreSQL Row-Level Security als zusaetzliche Absicherung.

### Niedrige Prioritaet

**R7: Technologie-Alterung**
FastAPI, Traefik und gewaehlte Tools koennten in 2-3 Jahren veralten.
Mitigation: Clean Architecture entkoppelt Business-Logik von Frameworks.

---

## 4. Offene Entscheidungen

| # | Entscheidung | Dringlichkeit | Deadline |
|---|---|---|---|
| OE1 | Frontend-Technologie (React, Next.js, Vue, oder rein API?) | Niedrig | Phase 2 |
| OE2 | Hosting-Standort: Hetzner DE oder Hetzner FI fuer DSG-Compliance? | Hoch | Phase 1 |
| OE3 | Claude API Pricing-Modell und Budget-Limits pro Nutzer | Hoch | Phase 2 |
| OE4 | Lizenzmodell fuer die Software (Open Source, Proprietary, Dual?) | Mittel | Phase 1 |
| OE5 | Freemium vs. Paid-only Geschaeftsmodell | Mittel | Phase 2 |
| OE6 | Domain und Branding (Name, Domain, Logo) | Niedrig | Phase 2 |
| OE7 | Backup-Strategie: Hetzner Storage Box oder S3-kompatibel? | Mittel | Phase 1 |
| OE8 | Monitoring-Stack: Self-hosted Prometheus/Grafana oder SaaS (z.B. Grafana Cloud Free)? | Niedrig | Phase 3 |
| OE9 | E-Mail-Versand: Gmail API oder separater SMTP-Service? | Mittel | Phase 3 |
| OE10 | Terraform vs. manuelle Hetzner-Konfiguration zum Start? | Niedrig | Phase 1 |

---

## 5. Sprint 1 Plan

**Ziel:** Vom Fundament zum lauffaehigen Skeleton — ein leeres aber funktionierendes System.

**Dauer:** 2 Wochen (KW 28-29, 2026)

**Erfolgskriterien:**
- Git-Repository auf GitHub, mit allen Foundation-Dateien
- Docker-Compose startet alle Services (App, DB, Redis, Traefik)
- FastAPI-App antwortet auf Health-Endpoint
- PostgreSQL mit initialer Migration (Alembic)
- CI-Pipeline laeuft (Lint + Tests)
- Erste Tests bestehen

### Sprint Backlog

| # | Task | Prioritaet | Schaetzung | Abhaengigkeit |
|---|---|---|---|---|
| S1.1 | Git-Repository initialisieren, GitHub-Repo erstellen, Foundation pushen | P0 | 1h | — |
| S1.2 | Python-Projektstruktur: `__init__.py` Dateien, Package-Setup mit uv | P0 | 2h | S1.1 |
| S1.3 | FastAPI-App Skeleton: `main.py`, Health-Endpoint (`GET /health`) | P0 | 2h | S1.2 |
| S1.4 | Docker-Setup: Dockerfile, docker-compose.yml funktionsfaehig machen | P0 | 4h | S1.3 |
| S1.5 | PostgreSQL-Verbindung: SQLAlchemy async, Alembic Setup | P0 | 4h | S1.4 |
| S1.6 | Redis-Verbindung: redis-py async, Connection Pool | P1 | 2h | S1.4 |
| S1.7 | Konfigurationsmodul: pydantic-settings, .env Handling | P0 | 3h | S1.3 |
| S1.8 | Logging-Setup: structlog, JSON-Output, Correlation ID | P1 | 3h | S1.7 |
| S1.9 | Erste Alembic-Migration: Tenant-Tabelle, User-Tabelle (Skeleton) | P0 | 3h | S1.5 |
| S1.10 | GitHub Actions CI: Lint (ruff), Type Check (mypy), Tests (pytest) | P0 | 3h | S1.2 |
| S1.11 | Erste Tests: Health-Endpoint, DB-Connection, Config-Loading | P0 | 3h | S1.3-S1.7 |
| S1.12 | Traefik-Konfiguration: Routing zur App, Dashboard | P2 | 2h | S1.4 |
| S1.13 | Middleware: Tenant-Context, Request-ID, Error-Handler | P1 | 4h | S1.7-S1.8 |
| S1.14 | .env.example erstellen mit allen benoetigten Variablen | P0 | 1h | S1.7 |

**Gesamtschaetzung:** ~37h ueber 2 Wochen

### Sprint 1 Definition of Done

- Alle P0-Tasks abgeschlossen
- `docker compose up` startet das gesamte System
- `GET /health` gibt `{"status": "healthy", "version": "0.1.0"}` zurueck
- `make test` laeuft ohne Fehler
- `make lint` laeuft ohne Fehler
- CI-Pipeline auf GitHub ist gruen
- Mindestens 3 Tests bestehen
- CHANGELOG.md aktualisiert

---

## 6. Empfehlungen

1. **Sofort:** Git initialisieren und auf GitHub pushen. Das Fundament ist komplett.
2. **Diese Woche:** Rechtliche Klaerung zum Hosting-Standort starten (OE2).
3. **Sprint 1:** Fokus auf lauffaehiges Skeleton, nicht auf Features.
4. **Nicht vergessen:** Claude API Abstraktionsschicht von Anfang an einplanen (R1).
5. **Disziplin:** Jede Architekturentscheidung als ADR dokumentieren.

---

> Dieses Review wird am Ende jeder Phase aktualisiert.
