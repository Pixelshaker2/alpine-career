# Monitoring-Strategie

> Letzte Aktualisierung: 2026-07-02

## Uebersicht

alpine-career setzt auf proaktives Monitoring, um Probleme zu erkennen, bevor sie Nutzer beeintraechtigen. Die Strategie basiert auf den vier goldenen Signalen: Latenz, Fehlerrate, Durchsatz und Saettigung.

## Monitoring-Philosophie

- **Beobachtbarkeit vor Reaktion**: Das System soll so instrumentiert sein, dass Probleme erkannt werden, bevor Nutzer sie melden.
- **Wenige, aussagekraeftige Alerts**: Lieber wenige Alerts, die immer eine Aktion erfordern, als viele, die ignoriert werden.
- **Daten statt Vermutungen**: Entscheidungen zur Optimierung basieren auf Metriken, nicht auf Annahmen.
- **Einfachheit**: Monitoring-Stack so schlank wie moeglich halten, passend zur aktuellen Teamgroesse.

## Health Endpoints

Die Applikation stellt drei Health-Endpoints bereit:

```python
# GET /health - Liveness Check
# Schneller Check, ob die Applikation laeuft
@router.get("/health")
async def liveness():
    return {"status": "ok"}

# GET /health/ready - Readiness Check
# Prueft Verbindung zu allen Abhaengigkeiten
@router.get("/health/ready")
async def readiness(db: AsyncSession, redis: Redis):
    db_ok = await check_db_connection(db)
    redis_ok = await check_redis_connection(redis)
    status = "ok" if (db_ok and redis_ok) else "degraded"
    return {
        "status": status,
        "checks": {
            "database": "ok" if db_ok else "error",
            "redis": "ok" if redis_ok else "error",
        }
    }

# GET /health/detailed - Detaillierter Status (intern)
# Nur ueber internes Netzwerk erreichbar
@router.get("/health/detailed")
async def detailed_health():
    return {
        "status": "ok",
        "version": settings.APP_VERSION,
        "uptime_seconds": get_uptime(),
        "database_pool": get_pool_stats(),
        "redis_info": get_redis_info(),
        "memory_usage_mb": get_memory_usage(),
    }
```

## Metriken-Erfassung (Prometheus)

Metriken werden mit `prometheus-client` fuer Python erfasst und ueber `/metrics` bereitgestellt:

```python
from prometheus_client import Counter, Histogram, Gauge

# Request-Metriken
http_requests_total = Counter(
    "http_requests_total",
    "Gesamtzahl HTTP-Requests",
    ["method", "endpoint", "status_code"]
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "Dauer der HTTP-Requests in Sekunden",
    ["method", "endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)

# Business-Metriken
active_agents = Gauge(
    "active_agents_total",
    "Anzahl aktuell laufender Agents"
)

agent_executions_total = Counter(
    "agent_executions_total",
    "Gesamtzahl Agent-Ausfuehrungen",
    ["agent_type", "status"]
)
```

## Dashboards (Grafana)

Grafana wird fuer die Visualisierung aller Metriken verwendet. Folgende Dashboards sind eingerichtet:

### System-Dashboard
- CPU- und Memory-Auslastung pro Container
- Disk-I/O und Netzwerk-Traffic
- Container-Status und Restarts

### Applikations-Dashboard
- Request-Rate (Requests/Sekunde)
- Antwortzeiten (P50, P95, P99)
- Fehlerrate (4xx, 5xx)
- Aktive Datenbankverbindungen
- Redis-Memory und Hit-Rate

### Business-Dashboard
- Aktive Nutzer (taeglich, woechentlich)
- Agent-Ausfuehrungen pro Stunde
- Erfolgsrate der Agent-Ausfuehrungen
- API-Nutzung nach Endpoint

## Alerting-Strategie

Alerts werden in drei Stufen eingeteilt:

| Stufe    | Reaktionszeit | Benachrichtigung        | Beispiel                            |
|----------|---------------|-------------------------|-------------------------------------|
| Critical | Sofort        | Slack + E-Mail + Telefon | Applikation nicht erreichbar        |
| Warning  | < 1 Stunde    | Slack + E-Mail          | Fehlerrate > 5%                     |
| Info     | Naechster Tag | Slack                   | Disk-Nutzung > 70%                  |

### Alert-Regeln

```yaml
# Beispiele fuer Alerting-Regeln (Prometheus Alertmanager)
groups:
  - name: alpine-career-alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status_code=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Fehlerrate ueber 5% in den letzten 5 Minuten"

      - alert: AppDown
        expr: up{job="alpine-career"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "alpine-career Applikation ist nicht erreichbar"

      - alert: HighLatency
        expr: histogram_quantile(0.95, http_request_duration_seconds_bucket) > 2
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "P95 Latenz ueber 2 Sekunden"
```

## Die vier goldenen Signale

### Latenz
- **Metrik**: `http_request_duration_seconds`
- **Ziel**: P95 < 500ms fuer API-Endpoints, P95 < 5s fuer Agent-Ausfuehrungen
- **Alert**: Warning bei P95 > 2s ueber 10 Minuten

### Fehlerrate
- **Metrik**: `http_requests_total` mit Label `status_code=~"5.."`
- **Ziel**: < 1% Server-Fehler
- **Alert**: Warning bei > 5%, Critical bei > 10%

### Durchsatz
- **Metrik**: `http_requests_total` (Rate)
- **Ziel**: Baseline je nach Tageszeit, Anomalie-Erkennung
- **Alert**: Warning bei ploetzlichem Einbruch > 50%

### Saettigung
- **Metriken**: CPU, Memory, DB-Connections, Redis-Memory
- **Ziel**: Keine Ressource dauerhaft ueber 80%
- **Alert**: Warning bei > 80%, Critical bei > 95%

## Applikations-Metriken

Zusaetzlich zu den HTTP-Metriken werden geschaeftsspezifische Metriken erfasst:

- **Agent-Laufzeit**: Dauer der Agent-Ausfuehrungen nach Typ
- **Queue-Laenge**: Anzahl wartender Tasks in der Redis-Queue
- **Cache-Hit-Rate**: Anteil der Requests, die aus dem Cache bedient werden
- **DB-Query-Dauer**: Langsame Queries (> 100ms) werden separat gezaehlt

## Infrastruktur-Metriken

Infrastruktur-Metriken werden mit `node_exporter` auf dem Hetzner VPS erfasst:

- CPU-Auslastung (User, System, I/O Wait)
- Memory (Used, Available, Swap)
- Disk (Usage, I/O, IOPS)
- Netzwerk (Bandwidth, Connections, Errors)
- Docker-Container-Metriken (via cAdvisor)

## SLA-Ziele (Platzhalter)

| Metrik             | Ziel        | Messperiode |
|--------------------|-------------|-------------|
| Verfuegbarkeit     | 99.5%       | Monatlich   |
| API-Antwortzeit    | P95 < 500ms | Woechentlich|
| Fehlerrate         | < 1%        | Woechentlich|
| Geplante Wartung   | < 4h/Monat  | Monatlich   |

Diese Ziele werden nach der ersten Betriebsphase basierend auf realen Daten angepasst.

## Incident Management

Bei einem Incident wird folgendes Vorgehen angewandt:

1. **Erkennung**: Alert wird ausgeloest oder manuell gemeldet
2. **Triage**: Schweregrad bestimmen (Critical, Warning, Info)
3. **Kommunikation**: Team via Slack benachrichtigen
4. **Behebung**: Root Cause identifizieren und beheben
5. **Wiederherstellung**: System-Normalzustand verifizieren
6. **Post-Mortem**: Blameless Post-Mortem dokumentieren mit Action Items

Post-Mortems werden unter `docs/decisions/` als ADR abgelegt, wenn sie zu architektonischen Aenderungen fuehren.
