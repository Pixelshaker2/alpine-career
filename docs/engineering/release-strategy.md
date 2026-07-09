# Release-Strategie

> Letzte Aktualisierung: 2026-07-02

## Uebersicht

alpine-career verwendet Semantic Versioning (SemVer) fuer alle Releases. Diese Dokumentation beschreibt den Release-Prozess von der Versionierung bis zur Kommunikation.

## Semantic Versioning (SemVer)

Versionen folgen dem Schema `MAJOR.MINOR.PATCH`:

```
v1.4.2
│ │ └── PATCH: Bugfixes, keine neuen Features
│ └──── MINOR: Neue Features, rueckwaertskompatibel
└────── MAJOR: Breaking Changes, API-Aenderungen
```

### Regeln

| Aenderungstyp                              | Version-Inkrement |
|--------------------------------------------|-------------------|
| Bugfix, Security Patch                     | PATCH (1.4.2 → 1.4.3) |
| Neues Feature, rueckwaertskompatibel       | MINOR (1.4.2 → 1.5.0) |
| Breaking Change an der API                 | MAJOR (1.4.2 → 2.0.0) |
| Dokumentation, Refactoring, Tests          | Kein Release noetig     |

Das Projekt startet bei `v0.1.0`. Waehrend der `v0.x`-Phase koennen Minor-Releases Breaking Changes enthalten.

## Release-Prozess

### 1. Release vorbereiten

```bash
# Aktuellen main-Branch auschecken
git checkout main
git pull origin main

# Version pruefen
cat pyproject.toml | grep version
```

### 2. Version aktualisieren

```bash
# Version in pyproject.toml anpassen
# z.B. version = "1.5.0"

# Changelog aktualisieren (siehe unten)
```

### 3. Release-Commit erstellen

```bash
git add pyproject.toml CHANGELOG.md
git commit -m "chore(release): v1.5.0"
git push origin main
```

### 4. Tag erstellen und pushen

```bash
git tag -a v1.5.0 -m "Release v1.5.0: Agent Scheduling und Performance-Verbesserungen"
git push origin v1.5.0
```

### 5. GitHub Release erstellen

- Der Tag loest automatisch den GitHub Actions Workflow aus
- Ein GitHub Release wird mit den Changelog-Eintraegen erstellt
- Das Docker-Image wird gebaut und auf GHCR gepusht
- Deployment auf Staging wird automatisch gestartet

## Changelog-Verwaltung

Der Changelog wird in `CHANGELOG.md` im Root-Verzeichnis gefuehrt und folgt dem [Keep a Changelog](https://keepachangelog.com/) Format:

```markdown
# Changelog

## [Unreleased]

### Added
- Agent-Scheduling fuer wiederkehrende Ausfuehrungen (#45)

### Fixed
- Token-Refresh-Race-Condition im Auth-Modul (#42)

### Changed
- API-Antwortformat fuer Agent-Endpoints paginiert (#38)

## [1.4.2] - 2026-06-28

### Fixed
- Datenbank-Connection-Pool-Leak bei hoher Last (#41)
- Fehlerhafte Validierung bei leeren Agent-Konfigurationen (#40)
```

### Kategorien

| Kategorie    | Beschreibung                                     |
|--------------|--------------------------------------------------|
| Added        | Neue Features                                    |
| Changed      | Aenderungen an bestehendem Verhalten             |
| Deprecated   | Features, die in Zukunft entfernt werden         |
| Removed      | Entfernte Features                               |
| Fixed        | Fehlerbehebungen                                 |
| Security     | Sicherheitsrelevante Aenderungen                |

Jeder Eintrag referenziert die zugehoerige Issue- oder PR-Nummer.

## Version Bumping

Die Version wird an folgenden Stellen aktualisiert:

1. **`pyproject.toml`**: Hauptquelle der Version
2. **`CHANGELOG.md`**: Unreleased-Eintraege werden zum neuen Release verschoben
3. **Docker Image Tag**: Wird automatisch aus dem Git-Tag abgeleitet

```toml
# pyproject.toml
[project]
name = "alpine-career"
version = "1.5.0"
```

Die Version ist programmatisch ueber `importlib.metadata` verfuegbar:

```python
from importlib.metadata import version
APP_VERSION = version("alpine-career")
```

## Release-Checkliste

Vor jedem Release muessen folgende Punkte abgehakt werden:

```markdown
- [ ] Alle geplanten Issues fuer dieses Release sind abgeschlossen
- [ ] Alle Tests bestehen auf main (CI gruen)
- [ ] CHANGELOG.md ist aktualisiert
- [ ] Version in pyproject.toml ist korrekt
- [ ] Breaking Changes sind dokumentiert (falls vorhanden)
- [ ] Datenbankmigrationen sind getestet (up und down)
- [ ] Staging-Deployment ist erfolgreich
- [ ] Smoke Tests auf Staging bestanden
- [ ] Release-Notizen sind vorbereitet
- [ ] Team ist ueber den Release informiert
```

## Hotfix-Prozess

Hotfixes sind dringende Korrekturen, die ausserhalb des normalen Release-Zyklus erfolgen:

```
main ─────●────●──── hotfix-commit ────●──── (v1.4.3)
                  \                   /
                   hotfix/fix-critical
```

### Vorgehen

1. Branch `hotfix/<beschreibung>` von `main` erstellen
2. Fix implementieren und testen
3. PR oeffnen mit Label `hotfix`
4. Review (kann beschleunigt werden bei Critical)
5. Merge in `main`
6. PATCH-Version erhoehen und Tag erstellen
7. Sofort auf Produktion deployen

### Wann ist ein Hotfix gerechtfertigt?

- Security-Schwachstelle (aktiv ausgenutzt oder kritisch)
- Datenkorruption oder Datenverlust
- Applikation ist fuer alle Nutzer nicht nutzbar
- Kritischer Business-Prozess ist blockiert

Alle anderen Fehler werden im naechsten regulaeren Release behoben.

## Pre-Release-Versionen

Fuer groessere Aenderungen koennen Pre-Release-Versionen erstellt werden:

| Phase  | Format           | Zweck                              |
|--------|------------------|------------------------------------|
| Alpha  | `v2.0.0-alpha.1` | Fruehe Entwicklungsphase, instabil |
| Beta   | `v2.0.0-beta.1`  | Feature-complete, noch Bugs moeglich |
| RC     | `v2.0.0-rc.1`    | Release Candidate, finale Tests    |

```bash
# Pre-Release Tag
git tag -a v2.0.0-beta.1 -m "Release v2.0.0-beta.1"
git push origin v2.0.0-beta.1
```

Pre-Releases werden nur auf Staging deployed und sind nicht fuer Endnutzer bestimmt.

## Release-Kommunikation

### Intern (Team)

- Slack-Nachricht im Projekt-Channel mit Release-Highlights
- Link zum GitHub Release mit vollstaendigem Changelog

### Extern (Nutzer)

- Release-Notizen im Product-Blog (bei groesseren Releases)
- In-App-Benachrichtigung bei neuen Features (zukuenftig)
- E-Mail-Benachrichtigung bei Breaking Changes der API

### Vorlage fuer Release-Notizen

```markdown
## Was ist neu in v1.5.0?

### Neue Features
- **Agent Scheduling**: Agenten koennen jetzt zeitgesteuert ausgefuehrt werden.

### Verbesserungen
- API-Antwortzeiten um 30% reduziert.

### Fehlerbehebungen
- Connection-Pool-Leak bei hoher Last behoben.

### Upgrade-Hinweise
- Keine Breaking Changes in diesem Release.
- Datenbankmigration wird automatisch ausgefuehrt.
```
