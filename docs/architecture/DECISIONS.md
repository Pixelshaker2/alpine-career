# Architecture Decision Records (ADRs) — alpine-career

## Was sind ADRs?

Architecture Decision Records dokumentieren wichtige Architektur- und Technologieentscheidungen im Projekt. Sie halten fest, **warum** eine Entscheidung getroffen wurde — nicht nur **was** entschieden wurde. So koennen zukuenftige Entwicklerinnen und Entwickler Entscheidungen nachvollziehen, ohne die urspruenglichen Diskussionen miterlebt zu haben.

Jedes ADR ist unveraenderlich in seinem Kern: Statt ein ADR zu aendern, wird ein neues ADR erstellt, das das alte ersetzt oder ergaenzt.

## Wie erstelle ich ein neues ADR?

1. Kopiere die Vorlage aus `../decisions/TEMPLATE.md` (oder ein bestehendes ADR als Basis)
2. Benenne die Datei nach dem Schema: `ADR-NNN-kurzbeschreibung.md`
3. Fulle alle Abschnitte aus: Kontext, Entscheidung, Begruendung, Konsequenzen, Alternativen
4. Setze den Status auf `Vorgeschlagen`
5. Erstelle einen Pull Request und hole Reviews ein
6. Nach Annahme: Status auf `Akzeptiert` setzen und hier verlinken

### Status-Werte

| Status | Bedeutung |
|--------|-----------|
| `Vorgeschlagen` | ADR ist im Review |
| `Akzeptiert` | Entscheidung wurde angenommen und gilt |
| `Abgeloest` | Durch ein neueres ADR ersetzt (Verweis angeben) |
| `Verworfen` | Vorschlag wurde abgelehnt |

### Vorlage

```markdown
# ADR-NNN: Titel

- **Status:** Vorgeschlagen
- **Datum:** YYYY-MM-DD
- **Beteiligte:** Namen

## Kontext

Welches Problem loesen wir? Warum muessen wir eine Entscheidung treffen?

## Entscheidung

Was haben wir entschieden?

## Begruendung

Warum diese Entscheidung? Welche Kriterien waren ausschlaggebend?

## Konsequenzen

Was folgt aus dieser Entscheidung? Positiv und negativ.

## Alternativen

Welche Optionen wurden betrachtet und warum verworfen?
```

---

## Verzeichnis aller ADRs

| Nr. | Titel | Status | Datum |
|-----|-------|--------|-------|
| [ADR-001](../decisions/ADR-001-monorepo-struktur.md) | Monorepo-Struktur | Akzeptiert | 2026-07-02 |
| [ADR-002](../decisions/ADR-002-python-fastapi.md) | Python und FastAPI als Technologie-Stack | Akzeptiert | 2026-07-02 |
| [ADR-003](../decisions/ADR-003-modular-monolith.md) | Modularer Monolith als Architekturstil | Akzeptiert | 2026-07-02 |
| [ADR-004](../decisions/ADR-004-traefik-reverse-proxy.md) | Traefik als Reverse Proxy | Akzeptiert | 2026-07-02 |
| [ADR-005](../decisions/ADR-005-row-level-multi-tenancy.md) | Row-Level Multi-Tenancy | Akzeptiert | 2026-07-02 |
