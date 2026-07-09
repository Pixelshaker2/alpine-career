# MVP-Plan — Alpine Career Telegram Bot

> Status: Entwurf | Datum: 2026-07-09
> Ziel: Lauffaehiges Produkt fuer einen Nutzer (Marco von Burg)
> Interface: Telegram Bot
> Timeline: 3–4 Wochen

---

## Was der MVP kann

Marco schreibt dem Telegram Bot. Der Bot kann:

1. **Profil verwalten** — CV ist hinterlegt, Marco kann Skills/Praeferenzen anpassen
2. **Stellen suchen** — Bot durchsucht Jobportale in Berlin und der Schweiz, liefert passende Treffer
3. **CV optimieren** — Generiert eine auf die Stelle angepasste CV-Variante
4. **Anschreiben erstellen** — Generiert ein Anschreiben pro Stelle
5. **Bewerbung senden** — CV + Anschreiben per Gmail versenden (nur nach expliziter Freigabe durch Marco)
6. **Bewerbungen tracken** — Status pro Bewerbung (offen, beworben, Einladung, Absage)

Was der MVP **nicht** kann: automatisch bewerben ohne Freigabe, Multi-User, Web-Dashboard.

---

## Was wir streichen (gegenueber der vollen Architektur)

| Feature | Volle Architektur | MVP |
|---|---|---|
| Multi-Tenancy | Row-Level mit tenant_id | Einzelnutzer, kein Tenant-System |
| Auth | Google OAuth + JWT | Telegram Chat-ID als Identifikation |
| Event-System | Domain Events + Redis Pub/Sub | Direkte Funktionsaufrufe |
| API Gateway | FastAPI REST API | Telegram Bot Handler direkt |
| Gmail Integration | Gmail API fuer E-Mail-Versand | Gmail API — Bewerbungen direkt versenden (mit Freigabe) |
| Google Drive | Drive API fuer Dokumentenspeicherung | Lokale Dateien, Bot sendet als PDF |
| Frontend | TBD (React/Next.js) | Telegram ist das Interface |
| RBAC | Rollenbasierte Zugriffskontrolle | Nicht noetig (1 User) |
| CI/CD | GitHub Actions + Auto-Deploy | Manuelles Deploy via SSH |

---

## Tech Stack MVP

| Komponente | Technologie |
|---|---|
| Runtime | Python 3.12 |
| Bot Framework | python-telegram-bot v21 |
| API Layer | FastAPI (intern, fuer spaetere Erweiterung) |
| Datenbank | PostgreSQL 16 (via Docker) |
| ORM | SQLAlchemy 2.0 (async) |
| Migrationen | Alembic |
| AI | Claude API (Anthropic) |
| Job-Suche | Web Scraping (jobs.ch, StepStone, LinkedIn) |
| PDF-Generierung | WeasyPrint oder ReportLab |
| E-Mail | Gmail API (google-api-python-client, OAuth2) |
| Cache | Redis (Job-Ergebnisse cachen) |
| Deployment | Docker Compose auf Hetzner VPS |

---

## Marcos Profil

### Persoenliche Daten

- **Name:** Marco von Burg
- **Telegram:** @Dorender
- **Gmail:** m.vonburg94@gmail.com
- **Startdatum:** 01.10.2026
- **Standort:** Berlin (Umzug geplant), sucht in Berlin UND Schweiz
- **Prioritaet:** Berlin (Praeferenz), Schweiz als Alternative
- **Remote:** Full Remote moeglich

### Berufsprofil (aus CV)

- **Rolle:** IT-Systemadministrator — Cloud & Modern Workplace
- **Erfahrung:** 6+ Jahre (Swisscom-Tochter JLS Digital AG)
- **Kernkompetenzen:** Microsoft 365, Azure, Entra ID/AD, Windows Server, Netzwerk, ITIL 4
- **Zertifizierungspfad:** AZ-900 → ITIL 4 Foundation → AZ-104 → Security+ → AZ-500
- **Sprachen:** Deutsch (Muttersprache), Englisch (verhandlungssicher)
- **Zielrichtung:** Cloud-Administration, Modern Workplace

### Gehaltsvorstellungen

- **Berlin:** 48.000–58.000 EUR brutto/Jahr (Ziel ca. 52.000 EUR)
- **Schweiz:** CHF 78'000–88'000 brutto/Jahr (Ziel ca. CHF 82'000)

### Suchprofil

**Jobtitel (DE):** IT-Systemadministrator, Cloud Administrator, Microsoft 365 Administrator, Azure Administrator, Modern Workplace Engineer, Workplace Engineer, IT-Administrator, IT-Support Specialist, Technical Support Specialist

**Jobtitel (EN):** System Administrator, Cloud Engineer, M365 Admin, Azure Admin, IT Operations Engineer

**Standorte:** Berlin (DE), Zuerich (CH), Luzern (CH), Bern (CH), Basel (CH)

**Branchen:** IT-Dienstleister, Telekommunikation, Finanzwesen, Gesundheitswesen, oeffentliche Verwaltung

**Branchen-No-Gos:** Abfall / Entsorgung

---

## Sprint-Plan

### Sprint 1 — Skeleton (Woche 1)

Ziel: Bot antwortet, Datenbank laeuft, Deployment funktioniert.

| Task | Beschreibung | Schaetzung |
|---|---|---|
| S1.1 | Git Repo auf GitHub erstellen, Foundation pushen | 1h |
| S1.2 | Python-Packages: pyproject.toml mit echten Dependencies | 2h |
| S1.3 | Docker Compose: PostgreSQL + Redis funktionsfaehig | 2h |
| S1.4 | Datenbank-Schema: User, Profile, JobSearch, Application | 3h |
| S1.5 | Alembic Setup + erste Migration | 2h |
| S1.6 | Telegram Bot Grundgeruest: /start, /help, /status | 3h |
| S1.7 | Config-Modul: pydantic-settings, .env laden | 2h |
| S1.8 | Hetzner VPS aufsetzen, Docker installieren, Bot deployen | 3h |
| S1.9 | Bot laeuft auf Hetzner und antwortet auf /start | 1h |

**Ergebnis:** Bot ist live auf Hetzner, antwortet auf Befehle, DB ist verbunden.

### Sprint 2 — Profil & Jobsuche (Woche 2)

Ziel: Marco kann sein Profil sehen und bekommt Stellenvorschlaege.

| Task | Beschreibung | Schaetzung |
|---|---|---|
| S2.1 | Marcos Profil in DB einpflegen (aus CV-Daten) | 2h |
| S2.2 | /profil Befehl: Profil anzeigen und bearbeiten | 3h |
| S2.3 | Job-Scraper: jobs.ch Integration | 4h |
| S2.4 | Job-Scraper: StepStone/Indeed DE Integration | 4h |
| S2.5 | Job-Matching: Abgleich Profil vs. Stellenanzeige (Claude API) | 4h |
| S2.6 | /suche Befehl: Stellen suchen, Ergebnisse als Liste | 3h |
| S2.7 | /detail [id] Befehl: Stellendetails anzeigen | 2h |
| S2.8 | Redis-Caching fuer Job-Ergebnisse (TTL 6h) | 2h |

**Ergebnis:** Marco tippt /suche und kriegt passende Stellen in Berlin und der Schweiz.

### Sprint 3 — CV & Anschreiben (Woche 3)

Ziel: Marco kann pro Stelle ein angepasstes CV und Anschreiben generieren.

| Task | Beschreibung | Schaetzung |
|---|---|---|
| S3.1 | Claude API Integration: Prompt-Templates fuer CV-Optimierung | 4h |
| S3.2 | Claude API Integration: Prompt-Templates fuer Anschreiben | 4h |
| S3.3 | PDF-Generierung: CV als PDF rendern | 4h |
| S3.4 | PDF-Generierung: Anschreiben als PDF rendern | 3h |
| S3.5 | /vorschau [id] Befehl: PDFs im Chat anzeigen vor Freigabe | 2h |
| S3.6 | Generierte Dokumente in DB speichern | 2h |
| S3.7 | Gmail API Setup: OAuth2 fuer m.vonburg94@gmail.com, Token-Handling | 4h |
| S3.8 | /senden [id] Befehl: Bewerbung per E-Mail versenden (nach Freigabe) | 3h |
| S3.9 | E-Mail-Template: Professionelle Bewerbungsmail mit PDF-Anhaengen | 2h |

**Ergebnis:** Marco waehlt eine Stelle, prueft CV + Anschreiben, gibt frei, Bot sendet per Gmail.

### Sprint 4 — Tracking & Polish (Woche 4)

Ziel: Marco kann Bewerbungen tracken, System ist stabil.

| Task | Beschreibung | Schaetzung |
|---|---|---|
| S4.1 | Bewerbungs-Tracking: Status-Modell (offen/beworben/einladung/absage) | 3h |
| S4.2 | /bewerbungen Befehl: Alle Bewerbungen mit Status auflisten | 2h |
| S4.3 | /status [id] [status] Befehl: Status aktualisieren | 2h |
| S4.4 | Gmail-Eingangscheck: Antworten auf Bewerbungen erkennen und benachrichtigen | 4h |
| S4.5 | Taeglich automatische Stellensuche (Scheduled Task) | 3h |
| S4.6 | Benachrichtigung: "5 neue Stellen gefunden" push an Marco | 2h |
| S4.7 | Error Handling und Logging haerten | 3h |
| S4.8 | Backup-Strategie: PostgreSQL Dump Cronjob | 2h |
| S4.9 | Dokumentation: Bot-Befehle, Deployment-Anleitung | 2h |

**Ergebnis:** Vollstaendiger MVP. Marco sucht, generiert, bewirbt sich per Gmail, trackt Antworten — alles ueber Telegram.

---

## Bot-Befehle Uebersicht

```
/start          — Begruessung und Einrichtung
/help           — Alle Befehle auflisten
/profil         — Profil anzeigen/bearbeiten
/suche          — Neue Stellensuche starten
/suche berlin   — Suche auf Berlin einschraenken
/suche schweiz  — Suche auf Schweiz einschraenken
/detail [id]    — Stellendetails anzeigen
/bewerben [id]  — CV + Anschreiben fuer Stelle generieren
/vorschau [id]  — Generierte PDFs anzeigen
/senden [id]    — Bewerbung per Gmail versenden (mit Bestaetigung)
/bewerbungen    — Alle Bewerbungen auflisten
/status [id] [s]— Bewerbungsstatus aktualisieren
/stats          — Statistik (Bewerbungen, Einladungen, Quote)
```

---

## Datenbank-Schema (Entwurf)

```
users
  id              UUID PK
  telegram_chat_id BIGINT UNIQUE
  name            VARCHAR
  email           VARCHAR          -- m.vonburg94@gmail.com
  gmail_token     JSONB            -- OAuth2 Refresh Token (verschluesselt)
  created_at      TIMESTAMP

profiles
  id              UUID PK
  user_id         UUID FK -> users
  raw_cv_text     TEXT
  skills          JSONB
  target_roles    JSONB
  target_locations JSONB
  preferences     JSONB
  updated_at      TIMESTAMP

jobs
  id              UUID PK
  external_id     VARCHAR UNIQUE
  source          VARCHAR (jobs_ch, stepstone, indeed)
  title           VARCHAR
  company         VARCHAR
  location        VARCHAR
  description     TEXT
  url             VARCHAR
  salary_range    VARCHAR
  match_score     FLOAT
  scraped_at      TIMESTAMP

applications
  id              UUID PK
  user_id         UUID FK -> users
  job_id          UUID FK -> jobs
  status          VARCHAR (found, cv_generated, review, sent, interview, rejected, offer)
  cv_pdf          BYTEA
  cover_letter_pdf BYTEA
  email_subject   VARCHAR
  email_body      TEXT
  email_to        VARCHAR          -- Empfaenger-Adresse
  gmail_message_id VARCHAR         -- Gmail Message-ID fuer Tracking
  sent_at         TIMESTAMP
  notes           TEXT
  created_at      TIMESTAMP
  updated_at      TIMESTAMP
```

---

## Deployment

```
Hetzner VPS (CX22: 2 vCPU, 4 GB RAM, 40 GB SSD) — ca. 6 EUR/Monat

Docker Compose:
  - app (Python + Telegram Bot + FastAPI)
  - postgres (PostgreSQL 16)
  - redis (Redis 7)

Domain: optional (Bot braucht keine Domain, nur Token)
SSL: nicht noetig fuer Telegram Polling-Modus
```

---

## Risiken MVP

| Risiko | Auswirkung | Mitigation |
|---|---|---|
| Job-Portale blocken Scraping | Keine Stellenergebnisse | APIs nutzen wo verfuegbar, Scraping-Rate limitieren, User-Agent rotieren |
| Claude API Kosten | Hohe Kosten bei vielen Generierungen | Token-Budget pro Tag, Caching von Ergebnissen |
| PDF-Qualitaet | Unprofessionelle CVs | Professionelle Templates investieren, Testlaeufe mit Marco |
| Datenverlust | Bewerbungsdaten weg | Taegliches PostgreSQL-Backup |

---

## Uebergang MVP → Plattform

Der MVP ist so gebaut, dass er spaeter in die volle Alpine Career Architektur uebergeht:

- Datenbank-Schema wird via Alembic migriert → bleibt erhalten
- Bot-Handler werden zu Service-Layer-Aufrufen → API kommt spaeter dazu
- Profil/Job/Application-Modelle werden zu Domain-Entitaeten
- Multi-Tenancy kommt durch tenant_id-Spalte → Alembic-Migration
- Web-Frontend kommt spaeter als zusaetzliches Interface

Nichts wird weggeworfen. Der MVP waechst in die Plattform hinein.
