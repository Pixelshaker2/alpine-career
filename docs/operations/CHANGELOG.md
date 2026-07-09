# Changelog

Alle relevanten Aenderungen an Alpine Career werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/),
und dieses Projekt haelt sich an [Semantic Versioning](https://semver.org/lang/de/).

## Richtlinien

### Wann wird ein Eintrag erstellt?

- Bei jedem Merge in `main`, der fuer Nutzer oder Entwickler relevant ist
- Nicht fuer rein interne Refactorings ohne sichtbare Auswirkung
- Nicht fuer Tippfehler-Korrekturen in Kommentaren

### Kategorien

| Kategorie | Beschreibung |
|---|---|
| **Added** | Neue Features oder Funktionen |
| **Changed** | Aenderungen an bestehenden Features |
| **Deprecated** | Features, die bald entfernt werden |
| **Removed** | Entfernte Features oder Funktionen |
| **Fixed** | Fehlerbehebungen |
| **Security** | Sicherheitsrelevante Aenderungen |

### Format fuer Eintraege

Jeder Eintrag ist eine Aufzaehlung mit kurzer, klarer Beschreibung:

```markdown
- Job-Matching-Algorithmus implementiert, der Stelleninserate mit Nutzerprofil abgleicht
- Tenant-Isolation fuer alle Datenbankabfragen im Career Agent sichergestellt
```

Verweise auf Issues oder PRs werden in Klammern angehaengt:

```markdown
- Race Condition beim gleichzeitigen Zugriff auf Nutzerprofile behoben (#42)
```

---

## [Unreleased]

### Added

- Projektstruktur als modularer Monolith aufgesetzt mit Verzeichnissen fuer `core/`, `agents/`, und `shared/`
- Career Agent als Referenzimplementierung angelegt mit Unterverzeichnissen fuer API, Domain, Services, Integrationen und Templates
- Kerndokumentation erstellt: README.md, CLAUDE.md, AGENTS.md, CONTRIBUTING.md, CHANGELOG.md
- Entwicklungsregeln fuer KI-Assistenten in CLAUDE.md definiert (Code Style, Architektur, Sicherheit)
- Agenten-Architektur und -Lebenszyklus in AGENTS.md beschrieben
- Beitragsrichtlinien mit Branch-Konventionen, PR-Prozess und Code-Review-Checkliste in CONTRIBUTING.md festgehalten
- Schweizer Rechtschreibung (kein Eszett) als Dokumentationsstandard festgelegt

### Changed

- Noch keine Aenderungen -- Projekt befindet sich in der Foundation Phase

### Security

- Sicherheitsregeln dokumentiert: Keine Secrets im Code, keine Tenant-Datenvermischung, keine personenbezogenen Daten in Logs, parametrisierte Queries als Pflicht
- Regel etabliert, dass der Career Agent niemals automatisch E-Mails oder Bewerbungen versenden darf
