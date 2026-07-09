# Git-Strategie

> Letzte Aktualisierung: 2026-07-02

## Uebersicht

alpine-career verwendet GitHub Flow als Branch-Modell. Dieses Modell ist schlank, verstaendlich und eignet sich gut fuer ein kleines Team mit Continuous Deployment.

## Branch-Modell: GitHub Flow

```
main ─────●────●────●────●────●────●──── (immer deploybar)
            \      /  \      /
             feat-1    feat-2
```

- **`main`**: Der einzige langlebige Branch. Immer deploybar, immer stabil.
- **Feature Branches**: Kurzlebige Branches fuer einzelne Features, Bugfixes oder Aufgaben.
- **Kein `develop`-Branch**: Kein Zwischenbranch noetig. `main` ist die einzige Quelle der Wahrheit.

## Branch-Benennung

Branches folgen dem Schema `<typ>/<kurzbeschreibung>`:

| Praefix     | Verwendung                                      | Beispiel                         |
|-------------|--------------------------------------------------|----------------------------------|
| `feature/`  | Neues Feature oder Erweiterung                   | `feature/agent-scheduling`       |
| `bugfix/`   | Fehlerbehebung                                   | `bugfix/login-token-expiry`      |
| `hotfix/`   | Dringende Korrektur auf Produktion                | `hotfix/fix-db-connection-leak`  |
| `docs/`     | Dokumentationsaenderungen                         | `docs/update-api-docs`           |
| `refactor/` | Code-Umstrukturierung ohne Funktionsaenderung    | `refactor/extract-auth-service`  |
| `chore/`    | Wartungsarbeiten (Dependencies, CI, Config)       | `chore/update-dependencies`      |

### Regeln

- Kleinbuchstaben, Woerter mit Bindestrichen getrennt
- Maximal 50 Zeichen nach dem Praefix
- Keine Issue-Nummern im Branch-Namen (werden im PR referenziert)

## Commit Messages: Conventional Commits

Commits folgen der [Conventional Commits](https://www.conventionalcommits.org/) Spezifikation:

```
<typ>(<scope>): <beschreibung>

[optionaler body]

[optionaler footer]
```

### Typen

| Typ        | Beschreibung                                 |
|------------|----------------------------------------------|
| `feat`     | Neues Feature                                |
| `fix`      | Fehlerbehebung                               |
| `docs`     | Dokumentation                                |
| `style`    | Formatierung (kein Codeaenderung)            |
| `refactor` | Code-Umstrukturierung                        |
| `test`     | Tests hinzufuegen oder aendern               |
| `chore`    | Wartung (Build, CI, Dependencies)            |
| `perf`     | Performance-Verbesserung                     |

### Beispiele

```
feat(agents): add scheduling capability for career agents

fix(auth): resolve token refresh race condition

docs(api): update OpenAPI schema for v1 endpoints

refactor(core): extract database connection pool into separate module

chore(deps): update FastAPI to 0.115.0

feat(api)!: change response format for agent endpoints

BREAKING CHANGE: Agent list endpoint now returns paginated response.
```

### Regeln

- Betreffzeile maximal 72 Zeichen
- Imperativ verwenden ("add" statt "added")
- Kein Punkt am Ende der Betreffzeile
- Body erklaert das *Warum*, nicht das *Was*
- Breaking Changes mit `!` nach dem Scope markieren

## Pull-Request-Workflow

1. **Branch erstellen** vom aktuellen `main`
2. **Aenderungen committen** mit Conventional Commits
3. **PR oeffnen** mit aussagekraeftigem Titel und Beschreibung
4. **CI abwarten**: Alle Tests und Checks muessen bestehen
5. **Code Review**: Mindestens ein Approval erforderlich
6. **Merge**: Squash Merge in `main`
7. **Branch loeschen**: Automatisch nach dem Merge

### PR-Beschreibung

Jeder PR enthaelt:

```markdown
## Was wurde geaendert?
Kurze Beschreibung der Aenderung.

## Warum?
Kontext und Motivation.

## Wie getestet?
- [ ] Unit Tests geschrieben
- [ ] Integration Tests geschrieben
- [ ] Manuell getestet

## Screenshots (falls relevant)

## Verwandte Issues
Closes #123
```

## Merge-Strategie: Squash Merge

alpine-career verwendet **Squash Merge** fuer alle PRs:

- Alle Commits eines PR werden zu einem einzigen Commit zusammengefasst
- Der Merge-Commit verwendet den PR-Titel als Commit-Message
- Ergibt eine saubere, lineare Historie auf `main`
- Einzelne Entwicklungs-Commits (WIP, Fixups) verschwinden aus der Haupthistorie

```
# Statt vieler kleiner Commits:
main: feat(agents): add scheduling capability (#42)

# Anstatt:
main: WIP scheduling
main: fix tests
main: review feedback
main: more fixes
```

## Protected Branches

Der `main`-Branch ist geschuetzt mit folgenden Regeln:

- **Kein direkter Push**: Alle Aenderungen muessen ueber PRs erfolgen
- **Required Reviews**: Mindestens 1 Approval
- **Status Checks**: CI muss erfolgreich durchlaufen
- **Up-to-date**: Branch muss aktuell mit `main` sein vor dem Merge
- **No force push**: Force-Push auf `main` ist blockiert
- **Signed Commits**: Empfohlen, aber nicht erzwungen (zukuenftig)

## Code-Review-Anforderungen

### Fuer den Reviewer

- **Fokus**: Architektur, Logik, Sicherheit, Testabdeckung
- **Feedback**: Konstruktiv, konkret, mit Vorschlaegen
- **Zeitrahmen**: Reviews innerhalb von 24 Stunden
- **Approve**: Nur wenn alle wesentlichen Punkte geklaert sind

### Fuer den Autor

- PRs klein halten (< 400 Zeilen geaenderter Code)
- Selbst-Review vor dem Einreichen
- Auf Review-Feedback zeitnah reagieren
- Komplexe Aenderungen im PR-Body erklaeren

## Release Tagging

Releases werden mit Git-Tags auf `main` markiert:

```bash
# Tag erstellen
git tag -a v1.2.0 -m "Release v1.2.0: Agent Scheduling"
git push origin v1.2.0
```

- Tags folgen Semantic Versioning: `v<major>.<minor>.<patch>`
- Tags werden nur auf `main` erstellt
- Jeder Tag loest automatisch den Release-Workflow aus (siehe Release-Strategie)
