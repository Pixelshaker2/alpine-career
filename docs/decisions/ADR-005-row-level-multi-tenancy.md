# ADR-005: Row-Level Multi-Tenancy

- **Status:** Akzeptiert
- **Datum:** 2026-07-02
- **Beteiligte:** David Gabriel

## Kontext

alpine-career ist eine SaaS-Plattform, die mehrere Tenants (Organisationen oder Einzelnutzer) auf derselben Infrastruktur bedient. Tenant-Isolation ist eine zentrale Sicherheitsanforderung: Kein Nutzer darf jemals Daten eines anderen Tenants sehen, veraendern oder loeschen.

Es gibt drei gaengige Multi-Tenancy-Strategien in Datenbanksystemen:

1. **Database-per-Tenant:** Jeder Tenant hat eine eigene Datenbank-Instanz
2. **Schema-per-Tenant:** Jeder Tenant hat ein eigenes Schema innerhalb derselben Datenbank
3. **Row-Level Isolation:** Alle Tenants teilen sich dieselben Tabellen, Zeilen werden ueber eine `tenant_id`-Spalte getrennt

Die Wahl beeinflusst Kosten, Komplexitaet, Performance, Sicherheit und die Faehigkeit zur Skalierung.

Zu beruecksichtigen sind:

- Erwartete Tenant-Anzahl: 10–100 in den ersten 12 Monaten, spaeter potenziell Tausende
- Datenvolumen pro Tenant: moderat (Profile, Bewerbungen, Dokument-Metadaten)
- Budget: ein einzelner PostgreSQL-Server auf Hetzner Cloud zu Beginn
- Team: klein, operationeller Aufwand muss minimal sein
- Compliance: Schweizer DSG und DSGVO verlangen Datentrennung, nicht zwingend physische Trennung

## Entscheidung

Wir verwenden **Row-Level Isolation** mit einer `tenant_id`-Spalte auf allen mandantenrelevanten Tabellen. Die Isolation wird auf drei Ebenen durchgesetzt:

### 1. Datenbank-Ebene

- Jede mandantenrelevante Tabelle hat eine `tenant_id`-Spalte (UUID, NOT NULL, Foreign Key auf `tenants`)
- Composite Index auf `(tenant_id, id)` fuer performante Abfragen
- PostgreSQL Row-Level Security (RLS) als zusaetzliche Absicherung

### 2. Middleware-Ebene

- Eine FastAPI-Middleware extrahiert die `tenant_id` aus dem JWT-Token
- Die `tenant_id` wird in den Request-Kontext injiziert
- Alle Repository-Methoden nutzen automatisch den Tenant-Filter

### 3. Anwendungs-Ebene

- SQLAlchemy-Query-Filter wird automatisch angewendet (z.B. via Event-Listener oder Mixin)
- Kein manuelles Hinzufuegen von `WHERE tenant_id = ?` in jedem Query
- Tests validieren, dass kein Query ohne Tenant-Filter ausgefuehrt wird

```python
# Beispiel: Automatischer Tenant-Filter via SQLAlchemy
class TenantMixin:
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tenants.id"),
        nullable=False,
        index=True,
    )

class JobApplication(Base, TenantMixin):
    __tablename__ = "job_applications"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    position: Mapped[str]
    status: Mapped[str]
```

## Begruendung

### Einfache Operationen

Eine einzige Datenbank bedeutet:

- Ein Backup-Job, ein Restore-Prozess
- Ein Migrations-Lauf fuer alle Tenants gleichzeitig
- Ein Connection Pool, eine Monitoring-Instanz
- Kein Tenant-spezifisches Datenbankmanagement

### Kosteneffizienz

Fuer einen kleinen SaaS mit 10–100 Tenants ist eine einzige PostgreSQL-Instanz auf Hetzner (z.B. CX31: ~10 EUR/Monat) voellig ausreichend. Database-per-Tenant wuerde bei 100 Tenants 100 separate Datenbank-Instanzen erfordern — operationell und finanziell nicht tragbar.

### Skalierungspfad

Row-Level Isolation schliesst spaetere Skalierung nicht aus:

- **Vertikale Skalierung:** Groesserer Server bei wachsender Last
- **Read Replicas:** Leseintensive Queries auf Replicas verteilen
- **Sharding:** Bei extremem Wachstum koennen Tenants auf verschiedene Datenbanken verteilt werden (die `tenant_id` dient als natuerlicher Shard-Key)
- **Hybrid:** Grosse Enterprise-Tenants koennten spaeter in eine eigene Datenbank migriert werden

### PostgreSQL Row-Level Security

PostgreSQL bietet mit Row-Level Security (RLS) eine datenbanknatige Absicherung. Selbst wenn die Anwendungsebene fehlerhaft ist, verhindert RLS den Cross-Tenant-Zugriff auf Datenbankebene. Das ist eine zusaetzliche Defense-in-Depth-Schicht.

```sql
-- Beispiel: RLS Policy
ALTER TABLE job_applications ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON job_applications
    USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
```

## Konsequenzen

### Positiv

- Minimaler operationeller Aufwand (eine Datenbank, ein Backup)
- Kosteneffizient fuer kleine und mittlere Tenant-Zahlen
- Einfache Queries und Reports ueber alle Tenants (fuer Plattform-Admins)
- Schema-Aenderungen gelten sofort fuer alle Tenants
- Einfache lokale Entwicklung und Tests

### Negativ

- **Query-Disziplin erforderlich:** Jeder Query muss den Tenant-Filter enthalten. Ein vergessener Filter ist ein Sicherheits-Incident. Mitigationen: automatischer Filter via Middleware, Code-Reviews, spezifische Tests.
- **Kein vollstaendiges noisy-neighbor-Schutz:** Ein Tenant mit hohem Datenvolumen oder aufwaendigen Queries kann die Performance fuer alle anderen beeinflussen. Mitigation: Query-Timeouts, Connection-Pool-Limits pro Tenant, Monitoring.
- **Compliance-Diskussionen:** Manche Enterprise-Kunden oder Regulatoren koennten physische Datentrennung verlangen. Fuer die aktuelle Zielgruppe (Schweizer Stellensuchende, B2C) ist Row-Level Isolation ausreichend.
- **Datenbank-Groesse:** Eine Tabelle mit Daten aller Tenants kann sehr gross werden. Mitigation: Partitionierung nach `tenant_id`, regelmaessige Archivierung alter Daten.
- **Datenmigration bei Tenant-Austritt:** Loeschen aller Daten eines Tenants erfordert DELETE-Queries ueber alle Tabellen. Fuer DSGVO-Compliance muss dies vollstaendig und nachpruefbar implementiert werden.

## Alternativen

### Schema-per-Tenant

- **Vorteile:** Bessere logische Trennung, einfachere Tenant-Datenloesch (DROP SCHEMA), Tenant-spezifische Indizes moeglich
- **Nachteile:** Schema-Migrationen muessen fuer jeden Tenant einzeln ausgefuehrt werden (bei 1000 Tenants: 1000 Migrationen), Connection-Pool-Management wird komplexer, PostgreSQL hat Grenzen bei der Schema-Anzahl
- **Verworfen:** Der Migrationsaufwand skaliert linear mit der Tenant-Anzahl und wird schnell unhandlich

### Database-per-Tenant

- **Vorteile:** Maximale Isolation, einfache Tenant-Datenloesch (DROP DATABASE), unabhaengige Backups und Restores, kein noisy-neighbor-Problem
- **Nachteile:** Enormer operationeller Aufwand (Provisioning, Migrationen, Monitoring pro Tenant), hohe Kosten, Cross-Tenant-Queries unmoeglich
- **Verworfen:** Fuer ein B2C-SaaS mit potenziell tausenden Tenants operationell und finanziell nicht tragbar
