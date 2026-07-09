# Roadmap — alpine-career

> Letzte Aktualisierung: 2026-07-02
> Status: Phase 0 — Foundation

## Vision

alpine-career wird eine SaaS-Plattform fuer AI-Agenten, die Menschen bei komplexen Lebensbereichen unterstuetzen. Der erste Agent — der Career Agent — hilft Schweizer Stellensuchenden dabei, ihre Karriere aktiv zu gestalten: von der Profiloptimierung ueber die Stellensuche bis zur Bewerbungsverwaltung.

Die Plattform ist von Beginn an als Multi-Agent-System konzipiert. Jeder Agent operiert in einer eigenen, klar abgegrenzten Domaene, nutzt aber gemeinsame Infrastruktur fuer Authentifizierung, Datenhaltung und Kommunikation.

### Zeithorizont

| Phase | Zeitraum | Fokus |
|-------|----------|-------|
| Phase 0 | Q3 2026 | Foundation |
| Phase 1 | Q3–Q4 2026 | Core Infrastructure |
| Phase 2 | Q4 2026 – Q1 2027 | Career Agent MVP |
| Phase 3 | Q1–Q2 2027 | Career Agent Beta |
| Phase 4 | Q2–Q3 2027 | Production |
| Phase 5 | Ab Q4 2027 | Platform & Multi-Agent |

---

## Phase 0: Foundation (aktuell)

> Geschaetzte Dauer: 2–3 Wochen

### Ziele

Das Fundament legen: Dokumentation, Architekturentscheidungen und Repository-Struktur, die das gesamte Projekt traegt.

### Liefergegenstaende

- [x] Repository-Struktur (Monorepo mit klaren Modulen)
- [x] Grundlegende Dokumentation (README, CONTRIBUTING)
- [x] Architecture Decision Records (ADRs)
- [x] Sicherheitsrichtlinien (SECURITY.md)
- [x] Roadmap (dieses Dokument)
- [ ] Entwicklungsumgebung-Setup dokumentieren
- [ ] Coding Standards und Linting-Konfiguration
- [ ] EditorConfig und Pre-Commit-Hooks
- [ ] Initiales Domain-Modell fuer Career Agent

### Erfolgskriterien

- Jeder neue Entwickler kann das Projekt in unter 30 Minuten aufsetzen
- Alle Architekturentscheidungen sind dokumentiert und nachvollziehbar
- Repository-Struktur spiegelt die geplante Architektur wider

### Risiken

| Risiko | Wahrscheinlichkeit | Impact | Mitigation |
|--------|-------------------|--------|-----------|
| Over-Engineering der Dokumentation | Mittel | Niedrig | Pragmatisch bleiben, iterativ verbessern |
| Falsche Architekturannahmen | Niedrig | Hoch | ADRs machen Entscheidungen revidierbar |

---

## Phase 1: Core Infrastructure

> Geschaetzte Dauer: 6–8 Wochen
> Abhaengigkeit: Phase 0 abgeschlossen

### Ziele

Die technische Basisinfrastruktur aufbauen, auf der alle Agenten laufen. Authentifizierung, Datenbank, API-Gateway und CI/CD-Pipeline.

### Liefergegenstaende

- [ ] **Authentifizierung & Autorisierung**
  - Google OAuth 2.0 Login-Flow
  - JWT-Token-System (Access + Refresh Tokens)
  - RBAC-Middleware mit Rollen-Management
  - Session-Management via Redis

- [ ] **Datenbank**
  - PostgreSQL-Setup mit Alembic-Migrationen
  - Multi-Tenant-Schema (Row-Level Isolation)
  - Tenant-Middleware fuer automatische Query-Filterung
  - Initiales Datenmodell (User, Tenant, Role)

- [ ] **API-Gateway**
  - FastAPI-Grundstruktur mit Versionierung (v1)
  - Traefik als Reverse Proxy mit Auto-SSL
  - Rate Limiting via Redis
  - CORS-Konfiguration
  - Health-Check-Endpunkte

- [ ] **Docker-Setup**
  - Docker Compose fuer lokale Entwicklung
  - Produktions-Dockerfiles (Multi-Stage Builds)
  - Docker-Netzwerk-Isolation

- [ ] **CI/CD-Pipeline**
  - GitHub Actions: Linting, Tests, Security-Scanning
  - Automatisiertes Deployment auf Hetzner Cloud
  - Environment-spezifische Konfigurationen (dev, staging, prod)

### Erfolgskriterien

- Nutzer kann sich via Google einloggen und erhaelt ein JWT
- API-Endpunkte sind geschuetzt und liefern 401/403 korrekt
- Tenant-Isolation ist verifiziert (Nutzer A sieht keine Daten von Nutzer B)
- CI-Pipeline laeuft gruen bei jedem Push
- Deployment auf Staging funktioniert automatisch

### Risiken

| Risiko | Wahrscheinlichkeit | Impact | Mitigation |
|--------|-------------------|--------|-----------|
| OAuth-Integration komplex | Mittel | Mittel | Frueh mit Google Cloud Console starten |
| Multi-Tenancy-Bugs | Mittel | Kritisch | Umfangreiche Tests, Middleware-Reviews |
| Docker-Networking auf Hetzner | Niedrig | Mittel | Hetzner-Doku frueh studieren, Fallback-Plan |

---

## Phase 2: Career Agent MVP

> Geschaetzte Dauer: 8–10 Wochen
> Abhaengigkeit: Phase 1 (Auth, DB, API-Gateway)

### Ziele

Den Career Agent als Minimal Viable Product liefern: Nutzerprofil erfassen, Stellensuche unterstuetzen und Lebenslaeufe optimieren — alles ueber eine API.

### Liefergegenstaende

- [ ] **Profilverwaltung**
  - Nutzerprofil-Erfassung (Erfahrung, Skills, Praeferenzen)
  - Profil-Analyse durch Claude API
  - Staerken- und Luecken-Erkennung
  - Profil-Daten als strukturiertes Domain-Modell

- [ ] **Stellensuche**
  - Integration mit Schweizer Jobportalen (jobs.ch, LinkedIn)
  - AI-gestuetztes Matching (Profil vs. Stellenangebote)
  - Filterfunktionen (Region, Branche, Pensum)
  - Relevanz-Scoring und Erklaerung

- [ ] **CV-Optimierung**
  - Lebenslauf-Upload und -Parsing
  - AI-gestuetzte Verbesserungsvorschlaege
  - Anpassung an spezifische Stellenangebote
  - Export in gaengigen Formaten

- [ ] **API-Endpunkte**
  - RESTful API fuer alle Career-Agent-Funktionen
  - OpenAPI-Dokumentation (auto-generiert via FastAPI)
  - API-Versionierung

### Erfolgskriterien

- Nutzer kann Profil erstellen und erhaelt AI-Analyse
- Stellensuche liefert relevante Resultate mit Matching-Score > 70%
- CV-Optimierung produziert messbar bessere Lebenslaeufe
- API-Response-Zeiten < 2 Sekunden (ohne AI-Calls)
- Testabdeckung > 80% fuer Domain-Logik

### Risiken

| Risiko | Wahrscheinlichkeit | Impact | Mitigation |
|--------|-------------------|--------|-----------|
| Claude API Kosten unkontrolliert | Mittel | Hoch | Token-Budget pro Nutzer, Caching |
| Jobportal-Scraping instabil | Hoch | Mittel | Mehrere Quellen, Fallback-Strategie |
| CV-Parsing unzuverlaessig | Mittel | Mittel | Strukturierte Eingabe als Alternative |

---

## Phase 3: Career Agent Beta

> Geschaetzte Dauer: 8–10 Wochen
> Abhaengigkeit: Phase 2 (Profil, Stellensuche, CV)

### Ziele

Den Career Agent zu einem vollstaendigen Bewerbungsmanagement-Tool ausbauen. Telegram-Bot und Gmail-Integration bieten Nutzern mehrere Kanaele.

### Liefergegenstaende

- [ ] **Bewerbungsmanagement**
  - Bewerbungstracking (Status, Timeline, Notizen)
  - Automatische Erinnerungen und Follow-up-Vorschlaege
  - Bewerbungs-Analytics (Erfolgsrate, Dauer, Muster)
  - Anschreiben-Generierung mit AI

- [ ] **Telegram-Bot**
  - Bot-Registrierung und Nutzer-Verknuepfung
  - Job-Alerts via Telegram
  - Schnellaktionen (Status aendern, Notiz hinzufuegen)
  - Natuerlichsprachliche Interaktion via Claude

- [ ] **Gmail-Integration**
  - OAuth-basierter Zugriff auf Gmail
  - Automatische Erkennung von Bewerbungsantworten
  - E-Mail-Kategorisierung (Einladung, Absage, Rueckfrage)
  - Antwort-Vorschlaege via AI

- [ ] **Google-Drive-Integration**
  - Dokument-Ablage (CVs, Anschreiben, Zeugnisse)
  - Automatische Organisation nach Bewerbung
  - Versionierung von Dokumenten

### Erfolgskriterien

- Beta-Nutzer koennen vollstaendigen Bewerbungsprozess abbilden
- Telegram-Bot reagiert innerhalb von 3 Sekunden
- Gmail-Integration erkennt > 90% der Bewerbungsantworten korrekt
- Net Promoter Score (NPS) > 30 bei Beta-Nutzern
- System stabil bei 50 gleichzeitigen Beta-Nutzern

### Risiken

| Risiko | Wahrscheinlichkeit | Impact | Mitigation |
|--------|-------------------|--------|-----------|
| Gmail-API-Quotas | Mittel | Hoch | Batch-Processing, Rate-Limit-Handling |
| Telegram-Bot-Abuse | Niedrig | Mittel | Rate Limiting, Nutzer-Verifizierung |
| Beta-Feedback ueberfordernd | Mittel | Niedrig | Strukturiertes Feedback-Formular, Priorisierung |
| Datenschutz bei E-Mail-Zugriff | Niedrig | Kritisch | Minimale Scopes, klare Einwilligung, Audit-Log |

---

## Phase 4: Production

> Geschaetzte Dauer: 6–8 Wochen
> Abhaengigkeit: Phase 3 (Beta-Feedback eingearbeitet)

### Ziele

Das System produktionsreif machen: Monitoring, Skalierung, Sicherheitshaertung und operationelle Exzellenz.

### Liefergegenstaende

- [ ] **Monitoring & Observability**
  - Structured Logging (JSON) mit zentraler Aggregation
  - Metriken-Dashboard (Prometheus + Grafana)
  - Distributed Tracing fuer Request-Nachverfolgung
  - Alerting fuer kritische Fehler und SLA-Verletzungen

- [ ] **Skalierung**
  - Horizontale Skalierung via Docker Swarm oder Kubernetes
  - Datenbank-Optimierung (Indizes, Query-Analyse, Connection Pooling)
  - Redis-Caching-Strategie fuer haeufige Abfragen
  - CDN fuer statische Inhalte

- [ ] **Sicherheitshaertung**
  - Penetration Testing (intern oder extern)
  - Vulnerability Assessment und Behebung
  - Incident-Response-Plan finalisieren
  - Compliance-Dokumentation vervollstaendigen

- [ ] **Operationelle Exzellenz**
  - Runbooks fuer haeufige Operationen
  - Disaster-Recovery-Plan und Tests
  - Backup-Strategie verifiziert
  - On-Call-Prozess definiert

### Erfolgskriterien

- 99.5% Uptime ueber 30 Tage
- P95-Latenz < 500ms fuer API-Requests
- Mean Time to Recovery (MTTR) < 30 Minuten
- Alle kritischen Schwachstellen behoben
- Backup-Restore erfolgreich getestet

### Risiken

| Risiko | Wahrscheinlichkeit | Impact | Mitigation |
|--------|-------------------|--------|-----------|
| Performance-Probleme unter Last | Mittel | Hoch | Lasttests frueh, schrittweises Rollout |
| Unentdeckte Sicherheitsluecken | Niedrig | Kritisch | Externer Pentest, Bug Bounty |
| Hetzner-Ausfall | Niedrig | Hoch | Multi-Zone-Setup, Disaster-Recovery-Plan |

---

## Phase 5: Platform & Multi-Agent

> Geschaetzte Dauer: laufend
> Abhaengigkeit: Phase 4 (stabile Produktion)

### Ziele

Die Plattform fuer weitere Agenten oeffnen und ein Marketplace-Modell aufbauen.

### Liefergegenstaende

- [ ] **Agent-Framework**
  - Agent-SDK fuer die Entwicklung neuer Agenten
  - Agent-Lifecycle-Management (Registrierung, Deployment, Monitoring)
  - Gemeinsame Services (Auth, Billing, Notifications)
  - Event-Bus fuer Agent-uebergreifende Kommunikation

- [ ] **Marketplace**
  - Agent-Katalog mit Beschreibungen und Bewertungen
  - Self-Service-Onboarding fuer Agent-Entwickler
  - Abrechnungsmodell pro Agent (Subscription oder Pay-per-Use)
  - Review-Prozess fuer neue Agenten

- [ ] **Weitere Agenten (Ideen)**
  - Finance Agent: Budgetplanung, Steueroptimierung
  - Health Agent: Gesundheitsmanagement, Arzttermine
  - Learning Agent: Weiterbildungsplanung, Skill-Entwicklung
  - Relocation Agent: Umzugsplanung, Behoerden

### Erfolgskriterien

- Mindestens 2 weitere Agenten auf der Plattform
- Agent-SDK-Dokumentation ermoeglicht externen Entwicklern den Einstieg
- Marketplace hat funktionierendes Billing
- Plattform traegt 500+ aktive Nutzer

### Risiken

| Risiko | Wahrscheinlichkeit | Impact | Mitigation |
|--------|-------------------|--------|-----------|
| Kein Markt fuer weitere Agenten | Mittel | Hoch | Marktforschung, Beta-Tests pro Agent |
| SDK-Komplexitaet | Hoch | Mittel | Iterativer Aufbau, Dogfooding mit eigenem Agent |
| Plattform-Sicherheit bei Drittanbieter-Agenten | Mittel | Kritisch | Sandbox, Review-Prozess, Monitoring |

---

## Abhaengigkeiten zwischen Phasen

```
Phase 0: Foundation
    |
    v
Phase 1: Core Infrastructure
    |
    +---> Phase 2: Career Agent MVP
              |
              v
          Phase 3: Career Agent Beta
              |
              v
          Phase 4: Production
              |
              v
          Phase 5: Platform & Multi-Agent
```

**Kritischer Pfad:** Phase 0 → Phase 1 → Phase 2 → Phase 3 → Phase 4

Phase 5 kann teilweise parallel zu Phase 4 begonnen werden (Agent-Framework-Design), das Marketplace-Feature setzt jedoch eine stabile Produktion voraus.

### Bereichsuebergreifende Abhaengigkeiten

| Von | Nach | Abhaengigkeit |
|-----|------|--------------|
| Phase 1 | Phase 2 | Auth, DB, API-Gateway muessen stehen |
| Phase 2 | Phase 3 | Profil und Stellensuche als Grundlage fuer Bewerbungen |
| Phase 1 | Phase 3 | OAuth-Infrastruktur fuer Gmail/Drive |
| Phase 3 | Phase 4 | Beta-Feedback fuer Optimierungen |
| Phase 4 | Phase 5 | Stabile Plattform als Basis fuer Multi-Agent |

---

## Anpassung der Roadmap

Diese Roadmap ist ein lebendes Dokument. Sie wird angepasst, wenn:

- Neue Erkenntnisse aus der Entwicklung oder dem Markt vorliegen
- Beta-Feedback Prioritaeten verschiebt
- Technische Abhaengigkeiten sich aendern
- Ressourcen sich aendern

Aenderungen werden in den ADRs dokumentiert, wenn sie Architekturentscheidungen betreffen.
