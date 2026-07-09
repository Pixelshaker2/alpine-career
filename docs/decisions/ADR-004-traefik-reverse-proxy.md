# ADR-004: Traefik als Reverse Proxy

- **Status:** Akzeptiert
- **Datum:** 2026-07-02
- **Beteiligte:** David Gabriel

## Kontext

alpine-career benoetigt einen Reverse Proxy, der folgende Aufgaben uebernimmt:

- **SSL/TLS-Terminierung:** Automatische Zertifikatsverwaltung fuer HTTPS
- **Request-Routing:** Weiterleitung an den richtigen Backend-Service (aktuell einer, spaeter mehrere)
- **Load Balancing:** Verteilung der Last auf mehrere Instanzen
- **Middleware:** Headers, Rate Limiting, Kompression, CORS
- **Docker-Integration:** Automatische Erkennung neuer Services ohne manuelle Konfiguration

Die Anwendung laeuft in Docker-Containern auf Hetzner Cloud. Der Reverse Proxy muss sowohl in der lokalen Entwicklungsumgebung als auch in der Produktion funktionieren, idealerweise mit minimaler Konfigurationsanpassung.

## Entscheidung

Wir verwenden **Traefik v3** als Reverse Proxy und Ingress-Controller.

Traefik wird als Docker-Container deployt und konfiguriert sich ueberwiegend dynamisch ueber Docker Labels an den Backend-Containern.

### Konfigurationsbeispiel

```yaml
# docker-compose.yml (vereinfacht)
services:
  traefik:
    image: traefik:v3.0
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./infrastructure/traefik:/etc/traefik

  api:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.api.rule=Host(`api.alpine-career.ch`)"
      - "traefik.http.routers.api.tls.certresolver=letsencrypt"
```

## Begruendung

### Docker-Native Service Discovery

Traefik erkennt automatisch neue Docker-Container und deren Routing-Regeln ueber Labels. Wenn ein neuer Service gestartet wird, ist er sofort ueber Traefik erreichbar — ohne Konfigurationsdateien zu bearbeiten und ohne Neustarts. Das ist entscheidend fuer eine Plattform, die spaeter mehrere Agenten als eigenstaendige Services betreiben koennte.

### Automatische SSL-Zertifikate

Traefik integriert Let's Encrypt nativ. Zertifikate werden automatisch angefordert, validiert und erneuert. Es ist keine separate Certbot-Konfiguration noetig, kein Cron-Job fuer die Erneuerung, und kein manuelles Eingreifen.

### Dynamische Konfiguration

Die Routing-Konfiguration lebt direkt bei den Services (als Docker Labels). Das bedeutet:

- Kein zentrales Konfigurations-File, das bei jeder Service-Aenderung angefasst werden muss
- Jedes Team/Modul definiert sein eigenes Routing
- Aenderungen am Routing sind Teil des Service-Deployments

### Integriertes Dashboard

Traefik bietet ein Web-Dashboard zur Echtzeit-Ueberwachung aller Routen, Services, Middleware und Zertifikate. Das erleichtert das Debugging von Routing-Problemen erheblich.

### Middleware-Oekoystem

Traefik bringt zahlreiche Middleware out of the box mit:

- Rate Limiting
- IP-Whitelisting
- Basic Auth (fuer interne Tools)
- Header-Manipulation
- Request-Kompression
- Retry-Logik
- Circuit Breaker

Diese Middleware kann per Docker Label an einzelne Services gehaengt werden — ohne Code-Aenderungen.

## Konsequenzen

### Positiv

- Zero-Config SSL mit Let's Encrypt
- Services werden automatisch erkannt und geroutet
- Routing-Regeln leben bei den Services (Dezentralisierung)
- Einfache lokale Entwicklung mit selbstsignierten Zertifikaten
- Dashboard fuer Debugging und Monitoring
- Zukunftssicher: Traefik unterstuetzt auch Kubernetes als Provider

### Negativ

- **Kleinere Community als Nginx:** Bei sehr spezifischen Problemen gibt es weniger Stack-Overflow-Antworten und Blog-Posts. Die offizielle Dokumentation ist allerdings umfassend.
- **Docker-Socket-Zugriff:** Traefik benoetigt Zugriff auf den Docker Socket, was ein Sicherheitsrisiko darstellt. Mitigation: Read-Only-Zugriff (`/var/run/docker.sock:ro`) und ggf. Docker Socket Proxy.
- **Lernkurve:** Entwickler, die Nginx gewohnt sind, muessen sich auf das Label-basierte Konfigurationsmodell umstellen.
- **Weniger Kontrolle bei Spezialfaellen:** Fuer sehr spezifische Routing-Anforderungen (z.B. komplexes URL-Rewriting) kann Nginx flexibler sein.

## Alternativen

### Nginx

- **Vorteile:** Industriestandard, riesige Community, extrem performant, hervorragende Dokumentation, jahrelang erprobt
- **Nachteile:** Statische Konfiguration (Reload bei Aenderungen noetig), SSL-Zertifikatsverwaltung erfordert separaten Certbot, Docker-Integration nur ueber Drittanbieter-Tools (nginx-proxy, nginx-proxy-manager), keine native Service Discovery
- **Verworfen:** Der manuelle Konfigurationsaufwand steht im Widerspruch zu unserem Ziel der Automatisierung. Fuer ein Docker-basiertes Setup ist Traefik die natuerlichere Wahl.

### Caddy

- **Vorteile:** Automatische HTTPS, einfache Konfiguration (Caddyfile), gute Performance, Go-basiert
- **Nachteile:** Weniger Middleware-Optionen als Traefik, Docker-Integration nicht so ausgereift, kleineres Oekosystem fuer Plugins
- **Verworfen:** Caddy ist eine gute Alternative, aber Traefik bietet die bessere Docker-Integration und mehr konfigurierbare Middleware.

### HAProxy

- **Vorteile:** Extrem performant fuer Load Balancing, Battle-tested in grossen Deployments, tiefe TCP/HTTP-Kontrolle
- **Nachteile:** Komplexere Konfiguration, keine native SSL-Zertifikatsverwaltung, Docker-Integration erfordert zusaetzliche Tools, Overhead fuer ein kleines Projekt
- **Verworfen:** HAProxy ist fuer grosse Infrastrukturen konzipiert. Fuer alpine-career ist es ueberdimensioniert.
