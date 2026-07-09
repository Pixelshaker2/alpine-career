# Engineering-Prinzipien -- alpine-career

> Status: Entwurf | Letzte Aktualisierung: 2026-07-02

Dieses Dokument definiert die technischen Prinzipien, nach denen alpine-career entwickelt wird. Alle Entwickler halten sich an diese Prinzipien. Abweichungen werden in Architecture Decision Records (ADRs) dokumentiert und begruendet.

## 1. Architekturprinzipien

### Clean Architecture
Abhaengigkeiten zeigen immer nach innen. Die Domain-Schicht hat keine Abhaengigkeiten zu Frameworks, Datenbanken oder externen Services. Aeussere Schichten implementieren Interfaces, die von inneren Schichten definiert werden.

### SOLID
- **Single Responsibility:** Jede Klasse hat genau eine Verantwortung.
- **Open/Closed:** Erweiterbar durch neue Klassen, nicht durch Aenderung bestehender.
- **Liskov Substitution:** Subtypen muessen ihre Basistypen ersetzen koennen.
- **Interface Segregation:** Kleine, spezifische Interfaces statt grosser, generischer.
- **Dependency Inversion:** Abhaengigkeiten auf Abstraktionen, nicht auf Implementierungen.

### Domain-Driven Design (DDD)
- Ubiquitous Language: Einheitliche Begriffe in Code, Dokumentation und Kommunikation
- Bounded Contexts: Klare Grenzen zwischen Modulen (Core, Career Agent, Shared)
- Aggregates: Konsistenzgrenzen innerhalb der Domain
- Domain Events: Lose Kopplung zwischen Bounded Contexts

### KISS, YAGNI, DRY
- **KISS:** Die einfachste Loesung, die funktioniert. Komplexitaet nur einfuehren, wenn der Nutzen klar belegt ist.
- **YAGNI:** Kein Code fuer zukuenftige Anforderungen, die nicht konkret geplant sind. Abstraktion nur dort, wo heute mehrere Implementierungen existieren oder die Testbarkeit es erfordert.
- **DRY:** Duplizierter Code wird extrahiert, wenn er dreimal vorkommt (Rule of Three). Vorzeitige Abstraktion ist schlimmer als Duplikation.

## 2. API-Design

### REST-Konventionen
- Ressourcenorientierte URLs: `/api/v1/applications/{id}`
- HTTP-Methoden semantisch korrekt: GET liest, POST erstellt, PUT ersetzt, PATCH aktualisiert, DELETE loescht
- Konsistente Response-Struktur mit `data`, `meta`, `errors`
- HTTP-Statuscodes korrekt verwenden (201 bei Erstellung, 204 bei Loeschung)

### Versionierung
- URL-basiert: `/api/v1/`, `/api/v2/`
- Alte Versionen werden mindestens 6 Monate nach Einfuehrung einer neuen Version unterstuetzt
- Breaking Changes erfordern eine neue Version

### Fehlerbehandlung
- Einheitliches Fehlerformat: `{"errors": [{"code": "VALIDATION_ERROR", "message": "...", "field": "email"}]}`
- Fehlercodes sind stabil und dokumentiert
- Interne Details (Stack Traces, DB-Fehler) werden nie an den Client gesendet
- Validierungsfehler listen alle fehlerhaften Felder auf, nicht nur das erste

### Paginierung
- Cursor-basiert fuer Listen mit vielen Eintraegen (keine Offset-Paginierung)
- Response enthaelt `next_cursor` und `has_more`
- Standard-Limit: 20, Maximum: 100

## 3. Datenbankprinzipien

### Migrationen
- Alembic fuer alle Schema-Aenderungen
- Migrationen sind vorwaerts- und rueckwaerts-kompatibel
- Jede Migration hat eine `upgrade()` und `downgrade()` Funktion
- Destructive Migrationen (Spalten loeschen) in separaten Releases
- Migrationen werden im Code-Review geprueft

### Namensgebung
- Tabellen: Plural, snake_case (`job_applications`, `user_profiles`)
- Spalten: snake_case, ohne Tabellenpraefixe (`created_at`, nicht `application_created_at`)
- Indizes: `idx_{tabelle}_{spalte}` (`idx_applications_tenant_id`)
- Fremdschluessel: `fk_{tabelle}_{referenz}` (`fk_applications_user_id`)
- Constraints: `chk_{tabelle}_{beschreibung}` (`chk_applications_status_valid`)

### Indizierung
- Primaerschluessel: UUID v4
- Fremdschluessel immer indiziert
- Composite Indexes fuer haeufige Query-Kombinationen
- Partial Indexes wo sinnvoll (z.B. nur aktive Datensaetze)
- Index-Nutzung wird mit `EXPLAIN ANALYZE` verifiziert

## 4. Testing

### Test-Pyramide
```
       E2E Tests        (wenige, kritische Flows)
      /          \
   Integrationstests    (API-Endpunkte, DB-Zugriff)
  /                \
    Unit Tests          (Geschaeftslogik, Services)
```

### Coverage-Ziele
- Domain-Schicht: >= 90% Line Coverage
- Service-Schicht: >= 80% Line Coverage
- Infrastruktur-Schicht: >= 60% Line Coverage (Integrationstests)
- Gesamt: >= 75% Line Coverage

### Testprinzipien
- Tests sind deterministisch -- keine Abhaengigkeit von Reihenfolge oder Zeitpunkt
- Jeder Test hat genau eine Assertion (logisch, nicht syntaktisch)
- Fixtures statt Factories fuer Testdaten
- Externe Services werden in Unit Tests gemockt
- Integrationstests verwenden eine echte Testdatenbank (Docker)
- E2E-Tests decken kritische User Journeys ab

## 5. Sicherheitsprinzipien

### Zero Trust
- Jeder Request wird authentifiziert und autorisiert
- Kein Vertrauen in interne Netzwerkgrenzen
- Tokens haben kurze Laufzeiten (Access: 15 Min, Refresh: 7 Tage)

### Least Privilege
- Dienste erhalten nur die minimal noetige Berechtigung
- Datenbankbenutzer haben eingeschraenkte Rechte (kein DROP, kein TRUNCATE)
- API-Keys sind an spezifische Scopes gebunden

### Defense in Depth
- Validierung auf jeder Schicht (API, Service, Domain)
- SQL-Injection-Schutz durch ORM und parametrisierte Queries
- XSS-Schutz durch Content-Type-Headers und Output-Encoding
- CSRF-Schutz fuer Web-Clients
- Rate Limiting auf API- und Nutzerebene

### Secrets Management
- Keine Secrets im Code oder in Git
- Umgebungsvariablen fuer Konfiguration
- OAuth-Tokens verschluesselt in der Datenbank
- API-Keys werden bei Verdacht sofort rotiert

## 6. Logging

### Strukturiertes Logging
- JSON-Format fuer alle Log-Eintraege
- Pflichtfelder: `timestamp`, `level`, `message`, `service`, `correlation_id`
- Optionale Felder: `tenant_id`, `user_id`, `request_id`, `duration_ms`

### Correlation IDs
- Jeder eingehende Request erhaelt eine UUID als `correlation_id`
- Diese ID wird an alle internen Aufrufe, Events und Log-Eintraege weitergegeben
- Ermoeglicht End-to-End-Tracing eines Requests durch das gesamte System

### Log Levels
- **ERROR:** Fehler, die sofortige Aufmerksamkeit erfordern
- **WARNING:** Unerwartetes Verhalten, das keinen sofortigen Eingriff erfordert
- **INFO:** Wichtige Geschaeftsereignisse (Nutzer erstellt, Bewerbung gesendet)
- **DEBUG:** Detailinformationen fuer Entwicklung und Fehlersuche

### Datenschutz in Logs
- Keine persoenlichen Daten in Logs (Namen, E-Mails, Telefonnummern)
- IDs statt Klartextdaten
- OAuth-Tokens und Passwoerter werden nie geloggt

## 7. Dokumentation

### Docs as Code
- Dokumentation lebt im gleichen Repository wie der Code
- Aenderungen an Dokumentation durchlaufen den gleichen Review-Prozess
- Markdown als Format

### Architecture Decision Records (ADRs)
- Jede signifikante Architekturentscheidung wird als ADR dokumentiert
- Format: Kontext, Entscheidung, Konsequenzen, Status
- ADRs werden nie geloescht, nur als "superseded" markiert

### API-Dokumentation
- OpenAPI 3.0 Spezifikation, automatisch aus Code generiert (FastAPI)
- Jeder Endpunkt hat Beschreibung, Beispiele und Fehlerszenarien
- Swagger UI im Entwicklungsmodus verfuegbar

## 8. Performance

- Antwortzeiten: P95 < 200ms fuer synchrone API-Calls
- Langlaufende Operationen (KI-Generierung) sind asynchron
- Datenbankqueries: Maximal 5 Queries pro Request (N+1 vermeiden)
- Caching mit Redis fuer haeufig gelesene, selten geaenderte Daten
- Lazy Loading fuer Relationen, Eager Loading nur wenn nachweislich noetig
- Connection Pooling fuer Datenbank und Redis

## 9. Dependency Management

- `pyproject.toml` als zentrale Konfiguration
- Abhaengigkeiten werden gepinnt (exakte Versionen)
- Sicherheitsupdates werden innerhalb von 48 Stunden eingespielt
- Neue Abhaengigkeiten erfordern Begruendung im Pull Request
- Minimale Abhaengigkeiten: Standardbibliothek bevorzugen wo moeglich
- Lock-File (`uv.lock` oder `poetry.lock`) wird versioniert

## 10. Fehlerbehandlung

### Strategie
- Exceptions werden so frueh wie moeglich gefangen und so spaet wie noetig behandelt
- Eigene Exception-Hierarchie fuer Domain-Fehler (`DomainError`, `NotFoundError`, `ValidationError`)
- Infrastruktur-Exceptions werden in Domain-Exceptions uebersetzt
- Globaler Exception Handler in FastAPI wandelt Exceptions in HTTP-Responses um

### Retry-Logik
- Externe API-Aufrufe haben Retry mit exponentiellem Backoff
- Maximale Retry-Anzahl: 3
- Idempotente Operationen: Sicher zu wiederholen
- Nicht-idempotente Operationen: Kein automatisches Retry

### Circuit Breaker
- Externe Services erhalten einen Circuit Breaker
- Nach X aufeinanderfolgenden Fehlern wird der Circuit geoeffnet
- Fallback-Verhalten wird pro Integration definiert

## Naechste Schritte

- [ ] ADR-Template erstellen und ersten ADR schreiben (Multi-Tenancy)
- [ ] Exception-Hierarchie implementieren
- [ ] Logging-Konfiguration aufsetzen
- [ ] CI-Pipeline mit Linting und Tests einrichten
- [ ] Performance-Baseline nach erstem Deployment messen
