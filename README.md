# Alpine Career

**AI-Agenten-Plattform fuer die Arbeitswelt von morgen.**

## Vision

Alpine Career ist eine SaaS-Plattform, die spezialisierte KI-Agenten bereitstellt. Jeder Agent loest ein konkretes Problem -- autonom, zuverlaessig und datenschutzkonform. Die Plattform ist modular aufgebaut: Neue Agenten koennen unabhaengig entwickelt und deployed werden, waehrend sie auf gemeinsame Infrastruktur zugreifen.

## Mission

Der erste Agent -- der **Career Agent** -- unterstuetzt Stellensuchende in der Schweiz dabei, passende Jobs zu finden, Bewerbungsunterlagen zu erstellen und den Bewerbungsprozess effizient zu managen. Weitere Agenten fuer andere Lebensbereiche folgen.

## Status

**Foundation Phase** -- Dokumentation und Architektur werden erarbeitet. Es existiert noch kein Produktionscode. Die Ordnerstruktur steht, die technischen Entscheidungen sind getroffen.

## Tech Stack

| Bereich | Technologie |
|---|---|
| Backend | Python 3.12+, FastAPI |
| Datenbank | PostgreSQL (Multi-Tenant) |
| Cache / Queue | Redis |
| KI | Claude API (Anthropic) |
| Integrationen | Gmail API, Google Drive API, Telegram Bot API |
| Infrastruktur | Docker, Hetzner Cloud |
| Architektur | Modularer Monolith, Clean Architecture, DDD |

## Architektur

Alpine Career folgt dem Prinzip eines **modularen Monolithen**. Das bedeutet: Ein einzelnes Deployment, aber intern strikt getrennte Module mit klaren Grenzen.

### Schichten (von aussen nach innen)

1. **API-Schicht** -- FastAPI-Router, Request/Response-Schemas, Authentifizierung
2. **Service-Schicht** -- Geschaeftslogik, Orchestrierung, Use Cases
3. **Domain-Schicht** -- Entitaeten, Value Objects, Domain Events, Geschaeftsregeln
4. **Infrastruktur-Schicht** -- Datenbank-Repositories, externe APIs, Messaging

Abhaengigkeiten zeigen immer nach innen: Die Domain-Schicht hat keine Abhaengigkeiten zu aeusseren Schichten. Externe Dienste werden ueber Interfaces (Ports) abstrahiert und durch konkrete Adapter implementiert.

### Kernprinzipien

- **SOLID** -- Jede Klasse hat eine Verantwortung, Erweiterung statt Aenderung
- **API-first** -- Jede Funktion ist ueber eine REST-API erreichbar
- **Event-driven** -- Lose Kopplung durch Domain Events wo sinnvoll
- **Multi-Tenant** -- Strikte Datentrennung pro Mandant auf Datenbankebene
- **Cloud-ready** -- Container-basiert, konfigurierbar ueber Umgebungsvariablen

### Verzeichnisstruktur

```
alpine-career/
  src/
    core/           # Gemeinsame Infrastruktur (Auth, Config, DB, Events, Logging)
    agents/         # Agenten-Module (jeder Agent ist ein eigenstaendiges Modul)
      career/       # Career Agent (Referenzimplementierung)
        api/        # Router, Schemas
        domain/     # Entitaeten, Value Objects
        services/   # Use Cases, Geschaeftslogik
        integrations/  # Externe APIs (Gmail, Drive, Claude)
        templates/  # E-Mail- und Dokumentvorlagen
    shared/         # Geteilte Modelle, Schemas, Hilfsfunktionen
```

## Dokumentation

| Dokument | Inhalt |
|---|---|
| [CLAUDE.md](CLAUDE.md) | Entwicklungsregeln fuer KI-Assistenten |
| [Master Index](docs/MASTER_INDEX.md) | Zentrales Verzeichnis aller Dokumente |
| [Agenten](docs/ai/AGENTS.md) | Agenten-Architektur und -Lebenszyklus |
| [Beitragsrichtlinien](docs/engineering/CONTRIBUTING.md) | Entwicklungsprozess und PR-Regeln |
| [Changelog](docs/operations/CHANGELOG.md) | Aenderungsprotokoll |
| [Architektur](docs/architecture/ARCHITECTURE.md) | Systemarchitektur im Detail |
| [Produkt](docs/product/PRODUCT.md) | Produktvision und Features |
| [Roadmap](docs/product/ROADMAP.md) | Phasenplan und Meilensteine |

## Mitarbeit

Beitraege sind willkommen. Bitte lies zuerst die [Beitragsrichtlinien](docs/engineering/CONTRIBUTING.md), bevor du einen Pull Request erstellst. Alle Regeln fuer KI-gestuetzte Entwicklung findest du in [CLAUDE.md](CLAUDE.md).

## Lizenz

TBD -- Die Lizenz wird vor dem ersten Release festgelegt.

---

*Alpine Career wird in der Schweiz entwickelt. Alle Dokumentation verwendet Schweizer Rechtschreibung (kein ss wird zu ss, kein Eszett).*
