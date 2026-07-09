# AGENTS.md -- Agenten-Architektur

Dieses Dokument beschreibt, was ein Agent in Alpine Career ist, wie Agenten aufgebaut sind und wie neue Agenten zur Plattform hinzugefuegt werden.

## Was ist ein Agent?

Ein Agent ist ein **eigenstaendiges, KI-gestuetztes Modul**, das eine spezifische Aufgabe fuer den Nutzer loest. Jeder Agent hat:

- Einen klar definierten **Aufgabenbereich** (z.B. Jobsuche, Bewerbungen)
- Eigene **Domain-Logik** und **Datenmodelle**
- Eigene **Integrationen** mit externen Diensten
- Einen eigenen **API-Namespace** (z.B. `/api/v1/career/...`)
- Zugriff auf die **gemeinsame Kerninfrastruktur** (Auth, DB, Events, Logging)

Ein Agent ist kein Chatbot. Ein Agent ist ein autonomes System, das Aufgaben selbststaendig ausfuehrt -- unter der Kontrolle und mit der Zustimmung des Nutzers.

## Agenten-Architektur

### Prinzip: Unabhaengige Module, gemeinsamer Kern

```
alpine-career/
  src/
    core/               # Gemeinsamer Kern (wird von allen Agenten genutzt)
      auth/             # Authentifizierung und Autorisierung
      config/           # Zentrale Konfiguration
      database/         # Datenbankverbindung, Migrationen, Base Models
      events/           # Event Bus, Domain Event Handling
      logging/          # Strukturiertes Logging
      middleware/       # Request-Middleware (Tenant, CORS, etc.)
      security/         # Verschluesselung, Hashing, Rate Limiting
    agents/
      career/           # Career Agent (Referenzimplementierung)
        api/            # REST-Endpunkte
        domain/         # Geschaeftsregeln, Entitaeten
        services/       # Use Cases, Orchestrierung
        integrations/   # Gmail, Drive, Claude, Telegram
        templates/      # Vorlagen fuer E-Mails und Dokumente
      <neuer_agent>/    # Gleiche Struktur wie career/
    shared/             # Geteilte Bausteine (kein Agent darf diese veraendern)
      models/           # User, Tenant, gemeinsame Basismodelle
      schemas/          # Geteilte API-Schemas
      utils/            # Hilfsfunktionen (Datum, Text, Validierung)
```

### Isolation zwischen Agenten

Agenten sind **strikt voneinander isoliert**:

1. **Kein direkter Import** -- Agent A darf keine Module von Agent B importieren
2. **Keine gemeinsamen Tabellen** -- Jeder Agent definiert eigene Datenbanktabellen mit eigenem Praefix
3. **Kommunikation nur ueber Events** -- Wenn Agent A Agent B informieren muss, geschieht dies ueber Domain Events auf dem Event Bus
4. **Eigener API-Namespace** -- Jeder Agent registriert seine Router unter `/api/v1/<agent_name>/`
5. **Eigene Konfiguration** -- Agenten-spezifische Einstellungen in eigenen Config-Sections

### Was Agenten teilen duerfen

- `core/auth` -- Authentifizierung und Tenant-Aufloesung
- `core/database` -- Datenbankverbindung und Basisklassen
- `core/events` -- Event-Bus-Infrastruktur
- `core/logging` -- Logging-Setup
- `shared/models` -- User- und Tenant-Modelle (nur lesen)
- `shared/utils` -- Hilfsfunktionen

## Agenten-Lebenszyklus

### 1. Registrierung

Beim Start der Applikation registriert sich jeder Agent am zentralen `AgentRegistry`. Dabei meldet er:

- Seinen Namen und seine Version
- Seine FastAPI-Router (API-Endpunkte)
- Seine Event-Handler (auf welche Events er reagiert)
- Seine Abhaengigkeiten (welche Core-Services er braucht)

### 2. Initialisierung

Nach der Registrierung wird der Agent initialisiert:

- Datenbankmigrationen werden geprueft und ausgefuehrt
- Verbindungen zu externen Diensten werden hergestellt
- Background-Tasks werden gestartet (z.B. Polling von E-Mails)

### 3. Betrieb

Im laufenden Betrieb verarbeitet der Agent:

- **API-Requests** -- Direkte Anfragen vom Nutzer oder Frontend
- **Domain Events** -- Reaktionen auf Ereignisse anderer Agenten oder des Kerns
- **Scheduled Tasks** -- Periodische Aufgaben (z.B. taeglicher Job-Scan)
- **Webhooks** -- Eingehende Benachrichtigungen externer Dienste

### 4. Herunterfahren

Beim Herunterfahren schliesst der Agent sauber ab:

- Laufende Tasks werden abgeschlossen oder abgebrochen
- Verbindungen zu externen Diensten werden geschlossen
- Der Agent meldet sich vom Event Bus ab

## Einen neuen Agenten hinzufuegen

### Schritt-fuer-Schritt-Anleitung

1. **Verzeichnis erstellen**: `src/agents/<agent_name>/` mit den Unterordnern `api/`, `domain/`, `services/`, `integrations/`

2. **Domain definieren**: Entitaeten und Value Objects in `domain/` anlegen. Hier liegt die Geschaeftslogik -- unabhaengig von Frameworks und Datenbanken.

3. **Repository-Interfaces definieren**: In `domain/repositories.py` abstrakte Interfaces (Protocols) fuer Datenzugriff definieren.

4. **Services implementieren**: Use Cases in `services/` implementieren. Ein Service orchestriert Domain-Objekte und Repository-Aufrufe.

5. **API-Router erstellen**: FastAPI-Router in `api/` mit Pydantic-Schemas fuer Request und Response.

6. **Integrationen bauen**: Repository-Implementierungen und externe API-Clients in `integrations/`.

7. **Agent registrieren**: In `__init__.py` eine `register()`-Funktion exportieren, die Router und Event-Handler beim `AgentRegistry` anmeldet.

8. **Tests schreiben**: Unit Tests fuer Domain, Integration Tests fuer Services, API Tests fuer Endpunkte.

9. **Dokumentation**: Docstrings, API-Beschreibungen, Eintrag in CHANGELOG.md.

### Checkliste fuer neue Agenten

- [ ] Eigenes Verzeichnis unter `src/agents/`
- [ ] Domain-Modelle ohne externe Abhaengigkeiten
- [ ] Repository-Interfaces als Python Protocols
- [ ] Mindestens ein Service mit Use-Case-Logik
- [ ] API-Router mit OpenAPI-Dokumentation
- [ ] Tenant-Isolation in allen Datenbankabfragen
- [ ] Event-Handler registriert (falls noetig)
- [ ] Tests mit mindestens 80% Coverage
- [ ] Eintrag in CHANGELOG.md

## Career Agent (Referenzimplementierung)

Der Career Agent ist der erste und damit der Referenz-Agent. Er zeigt, wie ein Agent korrekt implementiert wird.

### Aufgabenbereich

- Stelleninserate aus verschiedenen Quellen durchsuchen und bewerten
- Lebenslauf und Motivationsschreiben erstellen und optimieren
- Bewerbungsprozess verwalten (Status-Tracking, Erinnerungen)
- Kommunikation mit Arbeitgebern unterstuetzen (E-Mail-Entwuerfe)

### Integrationen

| Dienst | Zweck |
|---|---|
| Claude API | Textgenerierung, Analyse, Matching |
| Gmail API | E-Mail-Versand und -Empfang (mit Nutzerzustimmung) |
| Google Drive | Dokumentenspeicherung (Lebenslauf, Anschreiben) |
| Telegram Bot | Benachrichtigungen und schnelle Interaktion |

### Wichtige Regel

Der Career Agent sendet **niemals** automatisch E-Mails oder Bewerbungen. Jede Aktion, die den Nutzer nach aussen repraesentiert, erfordert explizite Bestaetigung.

## Zukuenftige Agenten

Die Plattform ist darauf ausgelegt, weitere Agenten aufzunehmen. Moegliche zukuenftige Agenten:

- **Finance Agent** -- Persoenliches Finanzmanagement, Budgetierung, Steueroptimierung
- **Health Agent** -- Gesundheitstracking, Arzttermine, Versicherungsfragen
- **Learning Agent** -- Weiterbildungsplanung, Kursempfehlungen, Skill-Tracking
- **Housing Agent** -- Wohnungssuche, Umzugsplanung, Vertragsmanagement

Diese Liste ist illustrativ. Neue Agenten werden nach Nutzerbeduerfnissen priorisiert und folgen der hier beschriebenen Architektur.
