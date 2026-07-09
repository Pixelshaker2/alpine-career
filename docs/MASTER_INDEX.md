# Master Index — alpine-career

> Zentrales Verzeichnis aller Dokumente, Entscheidungen und Ressourcen.
> Letzte Aktualisierung: 2026-07-02 | Status: Foundation Phase (Phase 0)

---

## Projekt-Root (operativ)

| Dokument | Beschreibung | Status |
|---|---|---|
| [README.md](../README.md) | Projektuebersicht, Vision, Tech Stack | Aktuell |
| [CLAUDE.md](../CLAUDE.md) | Entwicklungsregeln fuer AI-Assistenten | Aktuell |
| [pyproject.toml](../pyproject.toml) | Python-Projektmetadaten und Tool-Konfiguration | Aktuell |
| [docker-compose.yml](../docker-compose.yml) | Docker-Services (App, PostgreSQL, Redis, Traefik) | Aktuell |
| [Makefile](../Makefile) | Build-Targets und Entwickler-Shortcuts | Aktuell |
| [.env.example](../.env.example) | Umgebungsvariablen-Vorlage | Aktuell |

---

## Produkt-Dokumentation

| Dokument | Beschreibung | Pfad |
|---|---|---|
| Produktvision | Vision, Features, User Journey | [product/PRODUCT.md](product/PRODUCT.md) |
| Roadmap | Phasenplan und Meilensteine | [product/ROADMAP.md](product/ROADMAP.md) |
| Foundation Review | Annahmen, Risiken, Sprint 1 Plan | [product/REVIEW_FOUNDATION.md](product/REVIEW_FOUNDATION.md) |

---

## Architektur-Dokumentation

| Dokument | Beschreibung | Pfad |
|---|---|---|
| Systemarchitektur | Layer, Module, Datenfluss, Skalierung | [architecture/ARCHITECTURE.md](architecture/ARCHITECTURE.md) |
| ADR-Index | Architecture Decision Records | [architecture/DECISIONS.md](architecture/DECISIONS.md) |

### Architecture Decision Records (ADRs)

| ADR | Titel | Status |
|---|---|---|
| [ADR-001](decisions/ADR-001-monorepo-struktur.md) | Monorepo-Struktur | Accepted |
| [ADR-002](decisions/ADR-002-python-fastapi.md) | Python FastAPI als Backend | Accepted |
| [ADR-003](decisions/ADR-003-modular-monolith.md) | Modular Monolith als Startarchitektur | Accepted |
| [ADR-004](decisions/ADR-004-traefik-reverse-proxy.md) | Traefik als Reverse Proxy | Accepted |
| [ADR-005](decisions/ADR-005-row-level-multi-tenancy.md) | Row-Level Multi-Tenancy | Accepted |

---

## Engineering-Dokumentation

| Dokument | Beschreibung | Pfad |
|---|---|---|
| Engineering-Prinzipien | Core Principles, Best Practices | [engineering/ENGINEERING_PRINCIPLES.md](engineering/ENGINEERING_PRINCIPLES.md) |
| Coding-Standards | Code-Standards, Patterns, Konventionen | [engineering/CODING_STANDARDS.md](engineering/CODING_STANDARDS.md) |
| Beitragsrichtlinien | Setup, PRs, Code Review | [engineering/CONTRIBUTING.md](engineering/CONTRIBUTING.md) |
| Sicherheitsstrategie | Auth, Compliance, Datenschutz | [engineering/SECURITY.md](engineering/SECURITY.md) |
| Git-Strategie | Branch-Modell, Commits, PRs | [engineering/git-strategy.md](engineering/git-strategy.md) |
| Release-Strategie | SemVer, Release-Prozess, Hotfixes | [engineering/release-strategy.md](engineering/release-strategy.md) |
| Issue-Workflow | Issue-Typen, Lifecycle, DoR, DoD | [engineering/issue-workflow.md](engineering/issue-workflow.md) |
| Development-Workflow | Lokales Setup, Tools, Debugging | [engineering/development-workflow.md](engineering/development-workflow.md) |

---

## Operations-Dokumentation

| Dokument | Beschreibung | Pfad |
|---|---|---|
| Changelog | Aenderungsprotokoll | [operations/CHANGELOG.md](operations/CHANGELOG.md) |
| Testing-Strategie | Testpyramide, Tools, Coverage | [operations/testing-strategy.md](operations/testing-strategy.md) |
| Deployment-Strategie | Docker, Hetzner, CI/CD, Rollback | [operations/deployment-strategy.md](operations/deployment-strategy.md) |
| Logging-Strategie | Strukturiertes Logging, Audit Trail | [operations/logging-strategy.md](operations/logging-strategy.md) |
| Monitoring-Strategie | Prometheus, Grafana, Alerting | [operations/monitoring-strategy.md](operations/monitoring-strategy.md) |

---

## AI-Dokumentation

| Dokument | Beschreibung | Pfad |
|---|---|---|
| Agent-Architektur | Was Agents sind, Lifecycle, Isolation | [ai/AGENTS.md](ai/AGENTS.md) |

---

## Repository-Struktur

```
alpine-career/
├── README.md
├── CLAUDE.md
├── docker-compose.yml
├── pyproject.toml
├── Makefile
├── .env.example
├── apps/               # Applikations-Module (zukuenftig)
├── packages/           # Geteilte Packages (zukuenftig)
├── src/
│   ├── core/           # Plattform-Kern (Auth, DB, Config, Events, Logging, Security)
│   ├── agents/career/  # Erster Agent: Career Agent
│   ├── shared/         # Geteilte Utilities, Models, Schemas
│   └── api/v1/         # API Gateway und Router
├── tests/              # Unit, Integration, E2E, Fixtures
├── docs/
│   ├── MASTER_INDEX.md # Dieses Dokument
│   ├── product/        # Produkt: Vision, Roadmap, Reviews
│   ├── architecture/   # Systemarchitektur, ADR-Index
│   ├── decisions/      # Einzelne ADRs
│   ├── engineering/    # Standards, Workflows, Sicherheit
│   ├── operations/     # Betrieb, Deployment, Monitoring
│   ├── ai/             # Agent-Dokumentation
│   └── business/       # Business-Dokumentation (geplant)
├── infrastructure/     # Docker, Traefik, Scripts, Terraform
├── config/             # Umgebungskonfigurationen und Schemas
└── .github/            # Workflows, Issue- und PR-Templates
```

---

## Naechste Schritte

1. Git-Repository initialisieren und auf GitHub pushen
2. Sprint 1 starten (siehe [product/ROADMAP.md](product/ROADMAP.md))
3. CI/CD-Pipeline aufsetzen (GitHub Actions)
4. Docker-Entwicklungsumgebung funktionsfaehig machen
5. Core-Modul implementieren (Auth, Config, Database)

---

> Dieses Dokument wird bei jeder strukturellen Aenderung aktualisiert.
> Verantwortlich: Lead Engineer / CTO
