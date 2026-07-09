# Logging-Strategie

> Letzte Aktualisierung: 2026-07-02

## Uebersicht

alpine-career verwendet strukturiertes Logging im JSON-Format mit `structlog`. Ziel ist es, alle relevanten Ereignisse maschinenlesbar und konsistent zu erfassen, um Debugging, Monitoring und Auditing zu ermoeglichen.

## Strukturiertes Logging (JSON-Format)

Alle Log-Eintraege werden als JSON ausgegeben. Dies erleichtert die maschinelle Verarbeitung und die Integration mit Log-Aggregations-Tools.

```json
{
  "timestamp": "2026-07-02T14:23:45.123Z",
  "level": "info",
  "event": "user_login_successful",
  "correlation_id": "req-a1b2c3d4",
  "user_id": "usr-5678",
  "ip_address": "192.168.1.x",
  "duration_ms": 142,
  "module": "src.core.auth.service"
}
```

Jeder Log-Eintrag enthaelt mindestens: `timestamp`, `level`, `event`, `correlation_id` und `module`.

## Log Levels

| Level    | Verwendung                                                         | Beispiel                                       |
|----------|--------------------------------------------------------------------|-------------------------------------------------|
| DEBUG    | Detaillierte Informationen fuer Entwicklung                        | SQL-Queries, Cache-Hits/Misses                  |
| INFO     | Normale Geschaeftsereignisse                                       | Benutzer eingeloggt, Agent gestartet            |
| WARNING  | Unerwartete Situation, die keine sofortige Aktion erfordert        | Deprecated API verwendet, Rate-Limit nah        |
| ERROR    | Fehler, der eine Operation verhindert                              | Datenbank-Verbindung fehlgeschlagen             |
| CRITICAL | Systemkritischer Fehler, der sofortige Aufmerksamkeit erfordert    | Datenkorruption, Security-Breach erkannt        |

### Richtlinien

- **DEBUG** ist nur in der lokalen Umgebung aktiviert
- **INFO** ist das Standard-Level fuer Staging und Produktion
- **WARNING** und hoeher loesen Alerts aus (siehe Monitoring-Strategie)
- **CRITICAL** loest sofortige Benachrichtigung an das Team aus

## Correlation IDs fuer Request Tracing

Jeder eingehende HTTP-Request erhaelt eine eindeutige Correlation ID:

```python
# Middleware fuer Correlation IDs
@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    correlation_id = request.headers.get(
        "X-Correlation-ID",
        f"req-{uuid4().hex[:8]}"
    )
    structlog.contextvars.bind_contextvars(correlation_id=correlation_id)
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    return response
```

Die Correlation ID wird durch alle Schichten der Applikation propagiert:

- HTTP-Request → Service-Layer → Repository → Externe API-Aufrufe
- Asynchrone Tasks (Celery/Redis) uebernehmen die Correlation ID des ausloesenden Requests
- Die Correlation ID wird im Response-Header `X-Correlation-ID` zurueckgegeben

## Sensitive Daten maskieren

Folgende Daten werden in Logs **niemals** im Klartext ausgegeben:

- Passwoerter und Tokens
- E-Mail-Adressen (maskiert: `d***@example.com`)
- API-Schluessel (maskiert: `sk-...abc`)
- Persoenliche Identifikationsdaten

```python
# structlog Processor fuer Datenmaskierung
def mask_sensitive_data(logger, method_name, event_dict):
    sensitive_keys = {"password", "token", "api_key", "secret", "authorization"}
    for key in sensitive_keys:
        if key in event_dict:
            event_dict[key] = "***MASKED***"

    if "email" in event_dict and event_dict["email"]:
        email = event_dict["email"]
        local, domain = email.split("@", 1)
        event_dict["email"] = f"{local[0]}***@{domain}"

    return event_dict
```

## Log-Speicherung und -Rotation

| Umgebung    | Speicherort              | Rotation          | Aufbewahrung |
|-------------|--------------------------|-------------------|--------------|
| Local       | stdout (Konsole)         | Keine             | Session      |
| Staging     | /var/log/alpine-career/      | Taeglich, 100 MB  | 14 Tage      |
| Production  | /var/log/alpine-career/      | Taeglich, 100 MB  | 30 Tage      |

In Produktion werden Logs zusaetzlich an einen zentralen Log-Collector gestreamt (zukuenftig: Loki oder vergleichbar).

## Python Logging Setup (structlog)

```python
# src/core/logging/config.py
import structlog
import logging

def setup_logging(log_level: str = "INFO"):
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            mask_sensitive_data,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, log_level.upper()),
    )
```

Verwendung im Code:

```python
import structlog

logger = structlog.get_logger()

async def create_agent(agent_data: AgentCreate) -> Agent:
    logger.info("agent_creation_started", agent_name=agent_data.name)
    # ... Logik ...
    logger.info("agent_creation_completed", agent_id=str(agent.id))
    return agent
```

## Request/Response Logging

Jeder HTTP-Request und -Response wird automatisch geloggt:

```python
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    start_time = time.monotonic()

    logger.info(
        "http_request_received",
        method=request.method,
        path=request.url.path,
        client_ip=request.client.host,
    )

    response = await call_next(request)
    duration_ms = (time.monotonic() - start_time) * 1000

    logger.info(
        "http_response_sent",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=round(duration_ms, 2),
    )
    return response
```

Request-Bodies werden **nicht** geloggt (Datenschutz). Bei Bedarf koennen einzelne Endpoints gezielt Body-Logging aktivieren.

## Error Logging

Fehler werden mit vollstaendigem Kontext geloggt:

```python
try:
    result = await external_api.call(payload)
except ExternalAPIError as e:
    logger.error(
        "external_api_call_failed",
        service="openai",
        endpoint=e.endpoint,
        status_code=e.status_code,
        error_message=str(e),
        retry_count=attempt,
        exc_info=True,
    )
    raise
```

- Exceptions enthalten immer `exc_info=True` fuer den vollstaendigen Stacktrace
- Fehler werden kategorisiert: `client_error`, `server_error`, `external_error`, `validation_error`
- Wiederholte identische Fehler werden nicht einzeln geloggt (Rate-Limiting fuer Error-Logs)

## Audit Logging

Sicherheitsrelevante und geschaeftskritische Aktionen werden separat als Audit-Logs erfasst:

```python
audit_logger = structlog.get_logger("audit")

async def delete_agent(user_id: UUID, agent_id: UUID):
    audit_logger.info(
        "agent_deleted",
        actor_id=str(user_id),
        resource_type="agent",
        resource_id=str(agent_id),
        action="delete",
    )
```

Audit-Logs umfassen:

- Benutzer-Anmeldungen und -Abmeldungen
- Aenderungen an Berechtigungen
- Erstellen, Aendern und Loeschen von Ressourcen
- Administrative Aktionen
- Fehlgeschlagene Authentifizierungsversuche

Audit-Logs haben eine laengere Aufbewahrungsfrist (90 Tage) und werden separat gespeichert.
