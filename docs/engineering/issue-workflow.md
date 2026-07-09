# Issue-Workflow

> Letzte Aktualisierung: 2026-07-02

## Uebersicht

Diese Dokumentation beschreibt den Issue-Workflow fuer alpine-career. Issues werden in GitHub Issues verwaltet und folgen einem standardisierten Lebenszyklus von der Erfassung bis zum Abschluss.

## Issue-Typen

| Typ       | Label      | Beschreibung                                           | Beispiel                              |
|-----------|------------|--------------------------------------------------------|---------------------------------------|
| Bug       | `bug`      | Fehlerhaftes Verhalten der Applikation                 | Login schlaegt mit 500 fehl           |
| Feature   | `feature`  | Neue Funktionalitaet oder Erweiterung                  | Agent-Scheduling einfuehren           |
| Task      | `task`     | Technische Aufgabe ohne direkte Nutzerwirkung          | Dependency-Update, Refactoring        |
| Epic      | `epic`     | Uebergeordnetes Ziel, das mehrere Issues umfasst       | Multi-Agent-Support                   |

### Bug-Issues enthalten

- Schritte zur Reproduktion
- Erwartetes Verhalten
- Tatsaechliches Verhalten
- Umgebung (Browser, OS, API-Version)
- Screenshots oder Logs (falls relevant)

### Feature-Issues enthalten

- User Story im Format "Als [Rolle] moechte ich [Aktion], damit [Nutzen]"
- Akzeptanzkriterien
- Technische Notizen (falls vorhanden)
- Abhaengigkeiten zu anderen Issues

## Issue-Lebenszyklus

```
┌──────────┐    ┌─────────────┐    ┌───────────┐    ┌──────────┐
│   Open   │───→│ In Progress │───→│ In Review │───→│   Done   │
└──────────┘    └─────────────┘    └───────────┘    └──────────┘
      │                │                                  ▲
      │                └──────── Blocked ─────────────────┘
      │                                                   │
      └──────────── Won't Fix / Duplicate ────────────────┘
```

### Status-Beschreibung

| Status        | Beschreibung                                             |
|---------------|----------------------------------------------------------|
| Open          | Issue ist erfasst und im Backlog                          |
| In Progress   | Jemand arbeitet aktiv daran                               |
| In Review     | PR ist erstellt und wartet auf Code Review                |
| Done          | PR ist gemerged und Issue ist abgeschlossen               |
| Blocked       | Arbeit ist blockiert durch eine Abhaengigkeit             |
| Won't Fix     | Issue wird bewusst nicht umgesetzt                        |
| Duplicate     | Issue existiert bereits unter einer anderen Nummer        |

## Issue-Templates

### Bug Report Template

```markdown
---
name: Bug Report
about: Einen Fehler melden
labels: bug
---

## Beschreibung
Kurze Beschreibung des Fehlers.

## Schritte zur Reproduktion
1. Gehe zu ...
2. Klicke auf ...
3. Beobachte ...

## Erwartetes Verhalten
Was haette passieren sollen.

## Tatsaechliches Verhalten
Was stattdessen passiert ist.

## Umgebung
- API-Version: v1.x
- Browser: Chrome 126
- OS: macOS 15

## Screenshots / Logs
Falls zutreffend.
```

### Feature Request Template

```markdown
---
name: Feature Request
about: Ein neues Feature vorschlagen
labels: feature
---

## User Story
Als [Rolle] moechte ich [Aktion], damit [Nutzen].

## Akzeptanzkriterien
- [ ] Kriterium 1
- [ ] Kriterium 2
- [ ] Kriterium 3

## Technische Notizen
Technische Ueberlegungen oder Einschraenkungen.

## Abhaengigkeiten
Verwandte Issues: #xx, #yy
```

## Labels und Prioritaeten

### Prioritaets-Labels

| Label         | Bedeutung                                      | Reaktionszeit     |
|---------------|-------------------------------------------------|-------------------|
| `priority: critical` | Produktionsproblem, sofortige Aktion     | Sofort            |
| `priority: high`     | Wichtig, naechster Sprint                | < 1 Woche         |
| `priority: medium`   | Normal, geplant                          | < 2 Wochen        |
| `priority: low`      | Nice-to-have, Backlog                    | Kein Zeitdruck    |

### Kategorien-Labels

| Label          | Beschreibung                          |
|----------------|---------------------------------------|
| `api`          | API-Endpoints betroffen               |
| `auth`         | Authentifizierung/Autorisierung       |
| `agents`       | Agent-System betroffen                |
| `database`     | Datenbank/Migrationen                 |
| `infrastructure` | CI/CD, Docker, Hosting             |
| `documentation`| Dokumentation                         |
| `security`     | Sicherheitsrelevant                   |
| `performance`  | Performance-Optimierung               |

### Groessen-Labels

| Label     | Aufwand           |
|-----------|-------------------|
| `size: xs` | < 1 Stunde       |
| `size: s`  | 1-4 Stunden      |
| `size: m`  | 0.5-1 Tag        |
| `size: l`  | 1-3 Tage         |
| `size: xl` | > 3 Tage         |

## Sprint-Planung

alpine-career arbeitet in **einwoechigen Sprints** (Montag bis Freitag):

### Sprint-Ablauf

1. **Montag**: Sprint Planning (30 Min)
   - Review des Backlogs
   - Auswahl der Issues fuer den Sprint
   - Kapazitaetsplanung
2. **Montag-Freitag**: Umsetzung
3. **Freitag**: Sprint Review (15 Min)
   - Was wurde erreicht?
   - Was bleibt offen?
   - Blocker identifizieren

### Sprint-Kapazitaet

- Pro Entwickler: ca. 4 Tage produktive Arbeit (1 Tag fuer Reviews, Meetings, Admin)
- Sprint wird nicht ueberladen: Maximal 80% der Kapazitaet einplanen
- Unerledigtes wird in den naechsten Sprint uebernommen und priorisiert

## Definition of Ready

Ein Issue ist bereit fuer die Umsetzung, wenn:

- [ ] Die Beschreibung ist klar und verstaendlich
- [ ] Akzeptanzkriterien sind definiert (bei Features)
- [ ] Abhaengigkeiten sind identifiziert und aufgeloest
- [ ] Ein Groessen-Label ist zugewiesen
- [ ] Ein Prioritaets-Label ist zugewiesen
- [ ] Technische Fragen sind geklaert

## Definition of Done

Ein Issue gilt als abgeschlossen, wenn:

- [ ] Der Code ist implementiert und folgt den Coding-Standards
- [ ] Unit Tests sind geschrieben (Coverage >= 80%)
- [ ] Integration Tests sind geschrieben (falls relevant)
- [ ] Der Code wurde reviewed und approved
- [ ] Die CI-Pipeline ist gruen
- [ ] Die Dokumentation ist aktualisiert (falls relevant)
- [ ] Der PR ist in `main` gemerged
- [ ] Die Aenderung ist auf Staging verifiziert
- [ ] Das Issue ist geschlossen mit Referenz auf den PR

## Schaetzungs-Ansatz

alpine-career verwendet **T-Shirt-Groessen** fuer die Aufwandsschaetzung:

| Groesse | Aufwand     | Beschreibung                                        |
|---------|-------------|-----------------------------------------------------|
| XS      | < 1 Stunde  | Einfache Aenderung, klarer Scope                     |
| S       | 1-4 Stunden | Ueberschaubares Feature oder Bugfix                  |
| M       | 0.5-1 Tag   | Feature mit mehreren Komponenten                     |
| L       | 1-3 Tage    | Komplexes Feature, mehrere Module betroffen          |
| XL      | > 3 Tage    | Sollte in kleinere Issues aufgeteilt werden          |

Issues der Groesse XL werden vor der Umsetzung in kleinere, umsetzbare Teile aufgeteilt. Die Aufteilung erfolgt im Sprint Planning.
