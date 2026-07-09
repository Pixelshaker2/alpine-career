# Architektur -- alpine-career

> Status: Entwurf | Letzte Aktualisierung: 2026-07-02

## 1. Systemueberblick

alpine-career ist eine Multi-Tenant-SaaS-Plattform fuer KI-Agenten. Die Plattform stellt eine gemeinsame Infrastruktur bereit (Authentifizierung, Mandantentrennung, Integrationen, Event-System), auf der spezialisierte Agenten aufbauen. Der erste Agent -- der Career Agent -- unterstuetzt Stellensuchende in der Schweiz bei der Bewerbung.

**Architekturstil:** Modularer Monolith mit klarer Modulgrenzen-Trennung, sodass einzelne Module spaeter als eigenstaendige Services extrahiert werden koennen.

**Technologie-Stack:**
- Runtime: Python 3.11+, FastAPI
- Datenbank: PostgreSQL 15+
- Cache / Queue: Redis
- KI: Claude API (Anthropic)
- Integrationen: Gmail API, Google Drive API, Telegram Bot API
- Deployment: Docker, Hetzner Cloud
- Reverse Proxy: Traefik (empfohlen)

## 2. Schichtenarchitektur

Die Anwendung folgt Clean Architecture mit vier Schichten. Abhaengigkeiten zeigen immer nach innen.

```
  API-Schicht (Controller, Router, Request/Response-Schemas)
       |
  Service-Schicht (Anwendungslogik, Orchestrierung)
       |
  Domain-Schicht (Entitaeten, Value Objects, Domain Events)
       |
  Infrastruktur-Schicht (Repositories, externe APIs, Datenbank)
```

**API-Schicht:** FastAPI-Router, Pydantic-Schemas fuer Request/Response, Authentifizierung, Rate Limiting. Keine Geschaeftslogik.

**Service-Schicht:** Orchestriert Domain-Objekte und Infrastruktur. Enthaelt Use Cases als eigenstaendige Klassen. Transaktionsgrenzen werden hier definiert.

**Domain-Schicht:** Reine Python-Klassen ohne Framework-Abhaengigkeiten. Enthaelt Entitaeten, Value Objects, Domain Events und Interfaces (Ports) fuer Repositories.

**Infrastruktur-Schicht:** Implementiert die Ports der Domain-Schicht. Enthaelt Datenbankzugriff (SQLAlchemy), externe API-Clients, Caching, Event-Publishing.

## 3. Modulstruktur

```
src/
  core/           # Plattform-Kern (fuer alle Agenten)
    auth/         # Authentifizierung, Autorisierung
    config/       # Konfigurationsmanagement
    database/     # DB-Verbindung, Basis-Modelle, Migrationen
    events/       # Event-Bus, Event-Definitionen
    logging/      # Strukturiertes Logging
    middleware/   # CORS, Rate Limiting, Request-ID
    security/     # Verschluesselung, Token-Verwaltung
  agents/
    career/       # Career Agent Modul
      api/        # Endpunkte des Career Agents
      domain/     # Entitaeten, Value Objects
      services/   # Use Cases, Orchestrierung
      integrations/  # Gmail, Drive, Telegram, Claude
      templates/  # Prompt-Templates, E-Mail-Templates
  shared/         # Geteilte Komponenten
    models/       # Basis-Datenbankmodelle
    schemas/      # Geteilte Pydantic-Schemas
    utils/        # Hilfsfunktionen
  api/
    v1/           # API Gateway, versionierte Endpunkte
```

Jedes Agentenmodul ist eigenstaendig und enthaelt alle vier Schichten. Module kommunizieren ueber definierte Interfaces oder den Event-Bus, niemals ueber direkte Datenbankzugriffe.

## 4. Datenfluss

**Typischer Request-Fluss:**
1. HTTP-Request trifft auf Traefik (SSL-Terminierung, Routing)
2. FastAPI-Middleware: Request-ID, Logging, Authentifizierung, Rate Limiting
3. Router leitet an Controller weiter, Pydantic validiert Input
4. Service-Schicht fuehrt Use Case aus
5. Domain-Logik wird angewendet, Domain Events werden erzeugt
6. Repository persistiert Aenderungen
7. Events werden ueber den Event-Bus publiziert
8. Response wird als Pydantic-Schema zurueckgegeben

**Asynchroner Fluss (z.B. CV-Generierung):**
1. API nimmt Anfrage entgegen, erstellt Job-Eintrag
2. Background Worker (Redis Queue) verarbeitet den Job
3. Claude API wird aufgerufen, Ergebnis wird gespeichert
4. Nutzer wird per Telegram/Webhook benachrichtigt

## 5. Multi-Tenancy

> **Entscheidung ausstehend** -- Empfehlung: Row-Level Isolation

**Empfohlener Ansatz: Row-Level mit `tenant_id`**
- Jede Tabelle enthaelt eine `tenant_id`-Spalte (UUID, NOT NULL, indiziert)
- Alle Queries filtern automatisch nach `tenant_id` (SQLAlchemy Session-Events)
- Middleware extrahiert `tenant_id` aus dem JWT-Token
- PostgreSQL Row-Level Security (RLS) als zusaetzliche Sicherheitsschicht

**Vorteile:** Einfache Verwaltung, kosteneffizient, funktioniert gut bis ca. 10'000 Mandanten.

**Alternativen (spaeter evaluieren):**
- Schema-pro-Mandant: Bessere Isolation, hoehere Komplexitaet
- Datenbank-pro-Mandant: Maximale Isolation, hoechste Kosten

## 6. Integrationsarchitektur

Alle externen Integrationen folgen dem Adapter-Pattern und sind hinter Interfaces abstrahiert.

**Gmail API:** OAuth 2.0 mit Offline-Tokens. Lesen von Stellenanzeigen-E-Mails, Entwurf von Bewerbungen (kein automatischer Versand). Token-Speicherung verschluesselt in der Datenbank.

**Google Drive API:** OAuth 2.0 (gleicher Flow wie Gmail). Speicherung von generierten CVs und Anschreiben. Zugriff nur auf App-eigenen Ordner.

**Telegram Bot API:** Webhook-basiert. Nutzerkommunikation, Benachrichtigungen, interaktive Abfragen. Kein Polling, sondern Webhook-Registrierung.

**Claude API:** Direkte API-Aufrufe mit API-Key. Prompt-Templates werden versioniert verwaltet. Retry-Logik mit exponentiellem Backoff. Token-Verbrauch wird pro Mandant getrackt.

## 7. Event-System

Internes Event-System fuer lose Kopplung zwischen Modulen.

**Implementierung (Phase 1):** In-Process Event-Bus mit asyncio. Events sind Pydantic-Modelle mit Typ, Timestamp, Correlation-ID und Payload.

**Spaetere Evolution (Phase 2+):** Redis Streams oder dedizierter Message Broker, wenn Module als eigene Services extrahiert werden.

**Beispiel-Events:**
- `ProfileCreated`, `ProfileUpdated`
- `JobSearchCompleted`, `JobMatchFound`
- `ApplicationDrafted`, `ApplicationSent`
- `InterviewScheduled`

## 8. Caching-Strategie (Redis)

- **Session-Cache:** JWT-Blacklist, aktive Sessions
- **API-Cache:** Externe API-Antworten (Stellenangebote, Firmendaten)
- **Rate-Limiting-Counter:** Request-Zaehler pro Nutzer/IP
- **Job-Queue:** Background-Tasks (CV-Generierung, E-Mail-Entwuerfe)
- **Konfigurationscache:** Feature Flags, Mandanten-Einstellungen

TTL-Werte werden pro Cache-Typ konfiguriert. Cache-Invalidierung erfolgt event-basiert.

## 9. Datenbankdesign-Prinzipien

- PostgreSQL als primaere Datenbank fuer alle strukturierten Daten
- Alembic fuer Migrationen (automatisch generiert, manuell geprueft)
- UUIDs als Primaerschluessel (v4)
- Timestamps: `created_at`, `updated_at` auf jeder Tabelle (UTC)
- Soft Deletes mit `deleted_at` wo geschaeftslogisch noetig
- Indizes auf alle Fremdschluessel und haeufig gefilterte Spalten
- JSONB fuer semi-strukturierte Daten (z.B. Agenten-Konfiguration)
- Keine gespeicherten Prozeduren -- Logik gehoert in die Anwendung

## 10. Deployment-Architektur

```
Internet
   |
Traefik (Reverse Proxy, SSL, Routing)
   |
   +-- FastAPI (Anwendung, 2+ Instanzen)
   +-- PostgreSQL (Datenbank)
   +-- Redis (Cache, Queue)
```

**Warum Traefik statt Nginx:**
- Automatische SSL-Zertifikate via Let's Encrypt
- Docker-native Service Discovery (Labels statt Konfigurationsdateien)
- Dynamisches Routing ohne Neustart
- Dashboard fuer Monitoring
- Geringerer operativer Aufwand

**Docker-Compose** fuer lokale Entwicklung und initiales Deployment. Docker-Images werden mehrstufig gebaut (Build-Stage, Runtime-Stage). Health Checks fuer alle Services.

**Hetzner Cloud:** Kosteneffizient fuer den Start. VPS mit Docker, spaeter Kubernetes wenn noetig.

## 11. Sicherheitsarchitektur

- JWT-basierte Authentifizierung (Access + Refresh Token)
- HTTPS ueberall (Traefik terminiert SSL)
- API-Keys fuer Service-zu-Service-Kommunikation
- Rate Limiting pro Nutzer und IP
- Input-Validierung auf allen Schichten (Pydantic)
- SQL-Injection-Schutz durch ORM (SQLAlchemy)
- CORS restriktiv konfiguriert
- Secrets in Umgebungsvariablen, niemals im Code
- Verschluesselung sensibler Daten at rest (OAuth-Tokens, persoenliche Daten)
- Audit-Log fuer sicherheitsrelevante Aktionen

## 12. Skalierungspfad

**Phase 1 -- Modularer Monolith (aktuell):**
Alles in einem Prozess, klare Modulgrenzen. Reicht fuer die ersten 1'000 Nutzer.

**Phase 2 -- Horizontale Skalierung:**
Mehrere Instanzen hinter Traefik. Redis fuer Session-Sharing. Stateless Application Server.

**Phase 3 -- Service-Extraktion:**
Module mit hoher Last oder unterschiedlichen Skalierungsanforderungen werden als eigenstaendige Services extrahiert. Event-Bus wechselt zu Redis Streams oder RabbitMQ.

**Phase 4 -- Kubernetes (optional):**
Migration auf Kubernetes wenn operativer Overhead gerechtfertigt ist.

## Naechste Schritte

- [ ] Multi-Tenancy-Ansatz final entscheiden und dokumentieren (ADR)
- [ ] Traefik-Konfiguration erstellen
- [ ] Docker-Compose fuer Entwicklungsumgebung aufsetzen
- [ ] Datenbankschema fuer Core-Modul entwerfen
- [ ] Event-Bus-Implementierung planen
- [ ] CI/CD-Pipeline definieren
