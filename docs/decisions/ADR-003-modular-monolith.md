# ADR-003: Modularer Monolith als Architekturstil

- **Status:** Akzeptiert
- **Datum:** 2026-07-02
- **Beteiligte:** David Gabriel

## Kontext

Die Architektur von alpine-career muss zwei gegenlaefige Anforderungen erfuellen:

1. **Schnelle Iteration:** In der Fruehphase muessen Features schnell entwickelt, getestet und geaendert werden koennen. Die Architektur darf nicht bremsen.
2. **Langfristige Skalierbarkeit:** Die Plattform soll mehrere Agenten unterstuetzen, moeglicherweise mit unabhaengigem Scaling pro Agent.

Microservices bieten Skalierbarkeit, verursachen aber erheblichen operationellen Overhead (Service Discovery, verteilte Transaktionen, Netzwerk-Debugging, Container-Orchestrierung). Ein klassischer Monolith ist einfach, wird aber bei wachsender Komplexitaet schnell unuebersichtlich und schwer zu zerteilen.

Das Team ist klein, die Domaene noch nicht vollstaendig verstanden, und die Service-Grenzen sind unklar. Premature Decomposition wuerde zu falschen Boundaries fuehren, die spaeter teuer zu korrigieren waeren.

## Entscheidung

Wir implementieren einen **modularen Monolith**: eine einzelne deploybare Einheit mit klar definierten, intern getrennten Modulen. Die Module kommunizieren ueber definierte Schnittstellen und koennen spaeter in eigenstaendige Services extrahiert werden.

### Modulstruktur

Jedes Modul folgt Clean-Architecture-Prinzipien:

```
src/agents/career/
  api/         # API-Routes und Request/Response-Schemas
  domain/      # Entities, Value Objects, Domain Events
  services/    # Application Services, Use Cases
  integrations/  # Externe APIs (Claude, Gmail, etc.)
  templates/   # Templates (E-Mails, Dokumente)
```

### Regeln fuer Modul-Grenzen

1. Module importieren **nie** direkt aus einem anderen Modul-Ordner
2. Geteilte Typen und Interfaces leben in `src/shared/`
3. Modul-uebergreifende Kommunikation erfolgt ueber Events oder definierte Service-Interfaces
4. Jedes Modul hat seine eigenen Datenbank-Tabellen (logische Trennung)

## Begruendung

### Schnellere Iteration als Microservices

Ein einzelnes Deployment bedeutet:

- Ein `docker-compose up` statt zehn
- Keine Netzwerk-Latenz zwischen Modulen
- Keine verteilten Transaktionen
- Einfacheres Debugging (ein Log, ein Prozess)
- Schnellere Tests (kein Service-Bootstrapping)

### Klarer Migrationspfad

Wenn ein Modul zu gross wird oder unabhaengig skaliert werden muss, kann es mit vertretbarem Aufwand extrahiert werden:

1. Die interne Schnittstelle wird zur API (HTTP oder Message Queue)
2. Die Datenbank-Tabellen werden in eine eigene Datenbank verschoben
3. Events werden von In-Process zu asynchron (z.B. Redis Pub/Sub)

Entscheidend ist: Die Module sind **jetzt schon** so gebaut, als waeren sie eigenstaendige Services — nur das Deployment ist vereinfacht.

### Domain-Driven Design

Die Modulstruktur orientiert sich an DDD Bounded Contexts. Der Career Agent bildet einen Bounded Context, der Core-Bereich (Auth, Tenancy) einen anderen. Diese Trennung zwingt dazu, die Domaene zu verstehen und saubere Grenzen zu ziehen.

### Pragmatismus

Fuer ein Team von 1–3 Entwicklern sind Microservices unverhaehltnismaessig komplex. Die operationelle Last (Kubernetes, Service Mesh, verteiltes Tracing, Saga-Patterns) uebersteigt den Nutzen bei weitem. Ein modularer Monolith bietet 80% der Vorteile bei 20% der Komplexitaet.

## Konsequenzen

### Positiv

- Einfaches Deployment und Betrieb
- Schnelle Feature-Entwicklung ohne Cross-Service-Koordination
- Refactoring ueber Modulgrenzen hinweg bleibt einfach
- IDE-Support fuer Navigation und Refactoring
- Eine Datenbank, ein Migrations-System, ein Backup

### Negativ

- **Disziplin bei Modul-Grenzen:** Ohne technische Enforcement (z.B. Import-Linting-Regeln) koennen Modul-Grenzen erodieren. Entwickler muessen die Regeln kennen und einhalten.
- **Kein unabhaengiges Scaling:** Alle Module skalieren gemeinsam. Wenn der Career Agent 10x mehr Last hat als der Core, skaliert trotzdem alles zusammen. Fuer die naechsten 12–18 Monate ist das akzeptabel.
- **Geteilte Ausfalldomaene:** Ein Bug in einem Modul kann den gesamten Monolith zum Absturz bringen. Circuit-Breaker-Patterns und Error Isolation muessen in-process implementiert werden.
- **Deployment-Kopplung:** Jede Aenderung erfordert ein Deployment der gesamten Anwendung. Feature Flags helfen, die Auswirkungen zu kontrollieren.

## Alternativen

### Pure Microservices

- **Vorteile:** Unabhaengiges Deployment und Scaling, Technologie-Vielfalt moeglich, Fault Isolation
- **Nachteile:** Enormer operationeller Overhead, verteilte Transaktionen, Netzwerk-Debugging, Service Discovery, API-Versionierung zwischen Services
- **Verworfen:** Premature Decomposition bei unklaren Domaenengrenzen. Die Kosten ueberwiegen den Nutzen in der aktuellen Projektphase massiv.

### Traditioneller Monolith (ohne modulare Struktur)

- **Vorteile:** Maximal einfach, keine Regeln fuer Modul-Grenzen
- **Nachteile:** Keine klare Struktur, spaetere Extraktion extrem schwierig, "Big Ball of Mud"-Risiko
- **Verworfen:** Fehlende Struktur raecht sich mittelfristig. Die Investition in klare Modulgrenzen zahlt sich schnell aus.
