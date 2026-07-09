# Sicherheitsrichtlinien — alpine-career

> Letzte Aktualisierung: 2026-07-02
> Status: Entwurf (Phase 0 — Foundation)

## Inhaltsverzeichnis

- [Sicherheitsphilosophie](#sicherheitsphilosophie)
- [Authentifizierung](#authentifizierung)
- [Autorisierung](#autorisierung)
- [Datenschutz](#datenschutz)
- [API-Sicherheit](#api-sicherheit)
- [Secret Management](#secret-management)
- [Dependency Security](#dependency-security)
- [Infrastruktur-Sicherheit](#infrastruktur-sicherheit)
- [Incident Response](#incident-response)
- [Compliance](#compliance)
- [Sicherheits-Checkliste fuer PRs](#sicherheits-checkliste-fuer-prs)
- [Responsible Disclosure](#responsible-disclosure)
- [Status und naechste Schritte](#status-und-naechste-schritte)

---

## Sicherheitsphilosophie

alpine-career verarbeitet sensible Karrieredaten von Nutzerinnen und Nutzern. Sicherheit ist kein Feature, sondern eine Grundvoraussetzung. Wir bauen auf vier Prinzipien:

### Security First

Sicherheit wird von Beginn an in jede Architekturentscheidung einbezogen — nicht nachtraeglich angehaengt. Jedes neue Feature durchlaeuft eine Sicherheitsbewertung, bevor die Implementierung beginnt.

### Zero Trust

Kein Service, kein Nutzer und keine Netzwerkverbindung wird als vertrauenswuerdig betrachtet. Jeder Request wird authentifiziert und autorisiert, unabhaengig davon, woher er stammt.

### Least Privilege

Jede Komponente erhaelt ausschliesslich die minimal notwendigen Berechtigungen. Nutzerinnen und Nutzer sehen nur ihre eigenen Daten. Services kommunizieren nur mit den Services, die sie tatsaechlich benoetigen.

### Defense in Depth

Sicherheit wird auf mehreren Ebenen implementiert. Faellt eine Schicht aus, greifen die dahinterliegenden Massnahmen. Verschluesselung, Zugriffskontrolle, Validierung und Monitoring arbeiten zusammen.

---

## Authentifizierung

### Google OAuth 2.0

- Primaere Authentifizierung ueber Google OAuth 2.0
- Kein eigenes Passwort-Management — Verantwortung liegt bei Google
- OAuth-Scopes werden minimal gehalten (E-Mail, Profil)
- Zusaetzliche Scopes (Gmail, Drive) werden nur bei Bedarf und mit expliziter Zustimmung angefordert
- Refresh Tokens werden serverseitig verschluesselt gespeichert

### JWT Tokens

- Access Tokens: kurzlebig (15 Minuten), enthalten User-ID und Tenant-ID
- Refresh Tokens: laengere Laufzeit (7 Tage), rotierend
- Token-Signierung mit RS256 (asymmetrisch)
- Token-Revocation bei Logout und Passwortwechsel
- Blacklisting kompromittierter Tokens via Redis

### Session-Management

- Serverseitige Session-Verwaltung in Redis
- Automatischer Session-Timeout nach Inaktivitaet
- Gleichzeitige Sessions pro Nutzer limitiert
- Session-Invalidierung bei verdaechtigen Aktivitaeten

---

## Autorisierung

### Role-Based Access Control (RBAC)

Rollen und deren Berechtigungen:

| Rolle | Beschreibung | Berechtigungen |
|-------|-------------|----------------|
| `user` | Standardnutzer | Eigene Daten lesen/schreiben, Agents nutzen |
| `admin` | Tenant-Administrator | Nutzerverwaltung, Tenant-Einstellungen |
| `platform_admin` | Plattform-Administrator | Systemkonfiguration, Tenant-Management |

### Berechtigungspruefung

- Middleware prueft bei jedem Request die Rolle und den Tenant-Kontext
- Berechtigungen werden auf API-Route-Ebene definiert
- Zusaetzliche Objekt-Level-Berechtigungen wo noetig (z.B. Dokumenten-Besitz)
- Alle Autorisierungsentscheide werden geloggt

---

## Datenschutz

### Verschluesselung

**At Rest:**
- PostgreSQL: Verschluesselung auf Dateisystem-Ebene (LUKS)
- Sensible Felder (OAuth-Tokens, API-Keys): anwendungsseitige Verschluesselung (AES-256-GCM)
- Backups: verschluesselt gespeichert

**In Transit:**
- Alle externen Verbindungen ueber TLS 1.3
- Interne Service-Kommunikation ueber verschluesseltes Docker-Netzwerk
- Strikte HSTS-Header

### Tenant-Isolation

- Jede Datenbankzeile traegt eine `tenant_id`
- Middleware injiziert automatisch den Tenant-Filter in alle Queries
- Kein Cross-Tenant-Datenzugriff moeglich — auch nicht fuer Administratoren ohne expliziten Kontext-Wechsel
- Regelmaessige Audits der Tenant-Isolation

### Datenkategorien

| Kategorie | Beispiele | Schutzstufe |
|-----------|-----------|-------------|
| Identifikation | Name, E-Mail | Hoch |
| Karrieredaten | Lebenslauf, Bewerbungen | Sehr hoch |
| Systemdaten | Logs, Metriken | Mittel |
| OAuth-Tokens | Google Tokens | Kritisch |

---

## API-Sicherheit

### Rate Limiting

- Globales Rate Limit: 100 Requests/Minute pro Nutzer
- Authentifizierungs-Endpunkte: 10 Requests/Minute pro IP
- AI-Endpunkte: separates Budget basierend auf Token-Verbrauch
- Rate Limits werden via Redis durchgesetzt
- HTTP 429 mit `Retry-After`-Header bei Ueberschreitung

### Input-Validierung

- Alle Eingaben werden via Pydantic-Schemas validiert
- Strikte Typpruefung auf API-Ebene
- SQL-Injection-Schutz durch SQLAlchemy ORM (keine Raw Queries)
- XSS-Praevention durch Output-Encoding
- Maximale Request-Groesse: 10 MB (konfigurierbar)

### CORS

- Explizite Origin-Whitelist (keine Wildcards in Produktion)
- Credentials nur fuer erlaubte Origins
- Preflight-Caching fuer Performance

### Weitere Massnahmen

- CSRF-Schutz fuer State-aendernde Operationen
- Content Security Policy (CSP) Headers
- Request-ID fuer Tracing und Debugging
- Keine sensiblen Daten in URLs oder Query-Parametern

---

## Secret Management

### Grundregeln

- **Keine Secrets in Code oder Git** — niemals, ohne Ausnahme
- Alle Secrets ueber Umgebungsvariablen
- `.env`-Dateien nur fuer lokale Entwicklung, in `.gitignore` eingetragen
- Produktions-Secrets ueber Hetzner Cloud Secrets oder Docker Secrets

### Gemanagete Secrets

| Secret | Verwendung | Rotation |
|--------|-----------|----------|
| `DATABASE_URL` | PostgreSQL-Verbindung | Bei Bedarf |
| `REDIS_URL` | Redis-Verbindung | Bei Bedarf |
| `JWT_PRIVATE_KEY` | Token-Signierung | Quartalsweise |
| `GOOGLE_CLIENT_SECRET` | OAuth-Authentifizierung | Jaehrlich |
| `CLAUDE_API_KEY` | AI-Funktionalitaet | Quartalsweise |
| `TELEGRAM_BOT_TOKEN` | Telegram-Integration | Bei Bedarf |
| `ENCRYPTION_KEY` | Feld-Verschluesselung | Jaehrlich |

### Secret-Scanning

- Pre-Commit-Hooks pruefen auf versehentlich committete Secrets
- CI-Pipeline enthaelt Secret-Scanning-Schritt
- Erkannte Secrets werden sofort rotiert

---

## Dependency Security

### Automatisiertes Scanning

- `safety` oder `pip-audit` in der CI-Pipeline fuer Python-Dependencies
- Dependabot oder Renovate fuer automatische Dependency-Updates
- Docker-Image-Scanning mit Trivy
- Woechentliche Vulnerability-Reports

### Dependency-Policy

- Nur Dependencies mit aktiver Maintenance
- Pinned Versions in `pyproject.toml` (keine offenen Ranges in Produktion)
- Lock-Files (`poetry.lock` oder `uv.lock`) committen
- Regelmaessige Pruefung auf veraltete Dependencies

---

## Infrastruktur-Sicherheit

### Docker-Hardening

- Non-Root-User in allen Containern
- Read-Only-Filesystems wo moeglich
- Keine privilegierten Container
- Resource Limits (CPU, Memory) fuer alle Container
- Minimale Base Images (z.B. `python:3.12-slim`)
- Multi-Stage Builds zur Reduktion der Angriffsflaeche

### Netzwerk-Policies

- Docker-Netzwerk-Isolation zwischen Services
- Nur Traefik exponiert Ports nach aussen (80, 443)
- Datenbank und Redis nicht direkt erreichbar
- Firewall-Regeln auf Hetzner-Cloud-Ebene
- SSH-Zugriff nur mit Key-basierter Authentifizierung

### Hetzner Cloud

- Server in Schweizer oder EU-Rechenzentren bevorzugt
- Automatische Sicherheitsupdates fuer das Betriebssystem
- Regelmaessige Snapshots fuer Disaster Recovery
- Monitoring und Alerting fuer Ressourcen-Auslastung

---

## Incident Response

> **Hinweis:** Dieses Kapitel wird in Phase 4 (Production) vollstaendig ausgearbeitet.

### Grundstruktur

1. **Erkennung:** Automatisiertes Monitoring, Log-Analyse, Nutzer-Meldungen
2. **Bewertung:** Schweregrad bestimmen (Kritisch / Hoch / Mittel / Niedrig)
3. **Eindaemmung:** Betroffene Systeme isolieren, Zugriffe sperren
4. **Behebung:** Ursache identifizieren, Fix implementieren, testen, deployen
5. **Nachbereitung:** Post-Mortem erstellen, Massnahmen dokumentieren, Prozesse verbessern

### Schweregrade

| Grad | Beschreibung | Reaktionszeit |
|------|-------------|---------------|
| Kritisch | Datenverlust, Breach, System komplett ausgefallen | < 1 Stunde |
| Hoch | Teilausfall, potenzielle Gefaehrdung | < 4 Stunden |
| Mittel | Degradierte Performance, nicht-kritischer Bug | < 24 Stunden |
| Niedrig | Kosmetisch, keine Auswirkung auf Sicherheit | Naechster Sprint |

---

## Compliance

### Schweizer Datenschutzgesetz (DSG)

- Datensparsamkeit: nur notwendige Daten erheben
- Transparenz: klare Datenschutzerklaerung
- Auskunftsrecht: Nutzer koennen ihre Daten jederzeit exportieren
- Loeschrecht: vollstaendige Datenloesch-Funktion implementieren
- Datenbearbeitungsverzeichnis fuehren
- Datenschutz-Folgenabschaetzung bei kritischen Verarbeitungen

### DSGVO / GDPR

- Gilt fuer EU-Nutzer und bei Verarbeitung von EU-Daten
- Rechtsgrundlage fuer jede Verarbeitung dokumentiert
- Data Processing Agreements mit Drittanbietern (Google, Anthropic, Hetzner)
- Privacy by Design und Privacy by Default
- Recht auf Datenportabilitaet (JSON/CSV-Export)

### AI-spezifische Compliance

- Transparenz ueber AI-Nutzung gegenueber Endnutzern
- Keine vollautomatisierten Entscheidungen ohne menschliche Kontrolle
- AI-Outputs klar als solche gekennzeichnet
- Logging aller AI-Interaktionen fuer Nachvollziehbarkeit

---

## Sicherheits-Checkliste fuer PRs

Jeder Pull Request sollte folgende Punkte pruefen:

- [ ] Keine Secrets im Code oder in der Konfiguration
- [ ] Input-Validierung fuer alle neuen Endpunkte
- [ ] Tenant-Isolation beruecksichtigt (alle Queries mit `tenant_id`)
- [ ] Autorisierung auf neuen Routen konfiguriert
- [ ] Keine SQL-Raw-Queries ohne Parameterisierung
- [ ] Keine sensiblen Daten in Logs
- [ ] Dependencies auf bekannte Schwachstellen geprueft
- [ ] CORS-Konfiguration nicht gelockert
- [ ] Rate Limiting fuer neue Endpunkte definiert
- [ ] Error-Responses leaken keine internen Details
- [ ] Tests fuer Sicherheits-relevante Logik vorhanden

---

## Responsible Disclosure

Wir nehmen Sicherheit ernst und schaetzen die Arbeit von Security Researchers.

### Meldung von Schwachstellen

Wenn Sie eine Sicherheitsluecke in alpine-career finden, melden Sie diese bitte vertraulich:

- **E-Mail:** security@alpine-career.ch *(Platzhalter — wird eingerichtet)*
- **Verschluesselung:** PGP-Key wird bereitgestellt
- **Antwortzeit:** Wir bestaetigen den Eingang innerhalb von 48 Stunden

### Ablauf

1. Senden Sie eine detaillierte Beschreibung der Schwachstelle
2. Wir bestaetigen den Eingang und beginnen die Analyse
3. Wir halten Sie ueber den Fortschritt informiert
4. Nach der Behebung veroeffentlichen wir ein Advisory
5. Wir nennen Sie (mit Ihrem Einverstaendnis) als Entdecker

### Richtlinien

- Greifen Sie nicht auf Daten anderer Nutzer zu
- Fuehren Sie keine destruktiven Tests durch
- Veroeffentlichen Sie die Schwachstelle nicht vor der Behebung

---

## Status und naechste Schritte

### Aktueller Stand (Phase 0)

- [x] Sicherheitsrichtlinien dokumentiert
- [x] Architekturentscheidungen fuer Sicherheit getroffen
- [ ] Secret-Management-Infrastruktur einrichten
- [ ] Pre-Commit-Hooks fuer Secret-Scanning

### Phase 1 — Core Infrastructure

- [ ] Google OAuth 2.0 implementieren
- [ ] JWT-Token-System aufsetzen
- [ ] RBAC-Middleware implementieren
- [ ] Rate Limiting mit Redis
- [ ] TLS-Konfiguration via Traefik

### Phase 2-3 — Career Agent

- [ ] Tenant-Isolation testen und auditieren
- [ ] API-Input-Validierung fuer alle Endpunkte
- [ ] OAuth-Token-Verschluesselung implementieren
- [ ] Dependency-Scanning in CI integrieren

### Phase 4 — Production

- [ ] Penetration Testing durchfuehren
- [ ] Incident-Response-Plan finalisieren
- [ ] Compliance-Dokumentation vervollstaendigen
- [ ] Security-Monitoring und Alerting einrichten
- [ ] Datenschutz-Folgenabschaetzung durchfuehren
