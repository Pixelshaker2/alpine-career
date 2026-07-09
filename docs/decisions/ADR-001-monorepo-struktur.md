# ADR-001: Monorepo-Struktur

- **Status:** Akzeptiert
- **Datum:** 2026-07-02
- **Beteiligte:** David Gabriel

## Kontext

alpine-career ist als Multi-Agent-Plattform konzipiert. Mehrere Agenten (Career Agent, zukuenftig weitere) teilen sich gemeinsame Infrastruktur: Authentifizierung, Datenbank-Zugriff, Event-System, Konfiguration und Deployment. Gleichzeitig soll jeder Agent als eigenstaendiges Modul entwickelt werden koennen.

Die Frage ist, wie der Code organisiert wird: ein Repository fuer alles, mehrere Repositories pro Komponente, oder ein Hybrid-Ansatz.

Zu beruecksichtigen sind:

- Das Team ist klein (anfangs 1 Entwickler)
- Gemeinsame Abhaengigkeiten aendern sich haeufig in der Fruehphase
- CI/CD-Komplexitaet soll minimal bleiben
- Spaetere Extraktion einzelner Module muss moeglich sein

## Entscheidung

Wir verwenden ein **Monorepo** mit klaren Modul-Grenzen. Alle Komponenten — Agenten, Core-Services, Infrastruktur, Tests und Dokumentation — leben in einem einzigen Git-Repository.

Die Verzeichnisstruktur folgt einer festen Konvention:

```
alpine-career/
  src/
    core/          # Gemeinsame Infrastruktur
    agents/        # Agent-Module (career/, finance/, ...)
    shared/        # Geteilte Models, Schemas, Utils
    api/           # API-Versionen und Routing
  tests/           # Unit, Integration, E2E
  infrastructure/  # Docker, Terraform, Scripts
  docs/            # Dokumentation
  config/          # Umgebungskonfigurationen
```

## Begruendung

### Atomare Commits

Aenderungen, die mehrere Module betreffen (z.B. ein neues Feld im User-Modell, das sowohl Core als auch Career Agent betrifft), koennen in einem einzigen Commit und Pull Request umgesetzt werden. Es gibt keine Repository-uebergreifenden Abhaengigkeitsprobleme.

### Gemeinsames Tooling

Linting, Formatting, Testing und CI/CD muessen nur einmal konfiguriert werden. Alle Module profitieren sofort von Verbesserungen an der Toolchain.

### Einfache CI/CD-Pipeline

Eine Pipeline fuer alle Komponenten. Kein Orchestrieren von Builds ueber mehrere Repositories hinweg. Bei Bedarf kann die Pipeline spaeter mit Path-Filtern optimiert werden (nur betroffene Module bauen).

### Einfaches Refactoring

Module koennen einfach verschoben, umbenannt oder zusammengefuehrt werden. IDE-gestuetztes Refactoring funktioniert ueber Modulgrenzen hinweg.

### Teamgroesse

Fuer ein kleines Team ist ein Monorepo der pragmatischste Ansatz. Der Overhead von Multi-Repo-Workflows (Dependency-Management, Repository-Synchronisation) lohnt sich erst ab einer gewissen Teamgroesse.

## Konsequenzen

### Positiv

- Einfache Einrichtung und Wartung
- Konsistente Code-Standards ueber alle Module
- Schnelle Iteration ohne Repository-Wechsel
- Vollstaendige Uebersicht ueber den gesamten Code

### Negativ

- **Disziplin bei Modul-Grenzen noetig:** Ohne klare Grenzen droht ein "Big Ball of Mud". Imports zwischen Modulen muessen kontrolliert werden (z.B. via Linting-Regeln oder archunit-aehnlichen Tests).
- **Geteilte Dependencies:** Ein Upgrade einer Bibliothek betrifft alle Module gleichzeitig. Das kann Vorteil oder Nachteil sein, erfordert aber bewussten Umgang.
- **Repository-Groesse:** Langfristig koennte das Repository gross werden. Git-Performance ist bei Monorepos ab einer gewissen Groesse ein Thema — fuer alpine-career aber auf absehbare Zeit unkritisch.
- **Zugriffsrechte:** Alle Entwickler haben Zugriff auf den gesamten Code. Fuer ein kleines Team ist das unproblematisch, bei groesseren Teams muesste man mit CODEOWNERS arbeiten.

## Alternativen

### Polyrepo (ein Repository pro Service/Agent)

- **Vorteile:** Klare Trennung, unabhaengige Deployments, granulare Zugriffsrechte
- **Nachteile:** Cross-Repo-Aenderungen sind komplex, Dependency-Management aufwaendig, CI/CD-Orchestrierung noetig
- **Verworfen:** Zu viel Overhead fuer ein kleines Team in einer fruehen Projektphase

### Multi-Repo mit Git Submodules

- **Vorteile:** Technische Trennung mit der Moeglichkeit, alles zusammenzufuehren
- **Nachteile:** Git Submodules sind fehleranfaellig, verwirrend fuer neue Entwickler und erhoehen die Komplexitaet des Workflows erheblich
- **Verworfen:** Submodules loesen ein Problem, das wir (noch) nicht haben, und schaffen dafuer neue Probleme
