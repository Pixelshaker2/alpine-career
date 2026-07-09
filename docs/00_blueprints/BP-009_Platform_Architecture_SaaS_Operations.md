# Blueprint 009
# Platform Architecture & SaaS Operations

Projekt: Alpine Career
Version: 1.0
Status: Draft
Owner: Product Team

---

# Ziel

Dieses Dokument definiert, wie Alpine Career als skalierbare SaaS-Plattform betrieben wird.

Alpine Career ist nicht nur eine persönliche Automatisierung.
Alpine Career ist ein mandantenfähiges Produkt, das mehrere Kunden sicher, stabil und kontrolliert bedienen kann.

---

# 1. Grundprinzip

Die Plattform muss folgende Anforderungen erfüllen:

- mehrere Kunden parallel
- vollständige Datentrennung
- 24/7 Betrieb
- stabile Agenten
- klare Kostenkontrolle
- sichere Integrationen
- nachvollziehbare Aktionen
- einfache Skalierung

---

# 2. Multi-Tenant Architektur

Jeder Kunde ist ein eigener Tenant.

Ein Tenant enthält:

- Benutzerkonto
- Karriereprofil
- Dokumente
- Gmail-Verbindung
- Google Drive-Verbindung
- Kalender-Verbindung
- Telegram-Verbindung
- AI Memory
- Bewerbungen
- Logs
- Abonnement

Regel:
Daten verschiedener Tenants dürfen niemals vermischt werden.

---

# 3. Tenant Status

Ein Tenant kann folgende Status haben:

- Trial
- Active
- Suspended
- Cancelled
- Expired

Nur aktive Tenants führen Agenten aus.

---

# 4. Subscription Engine

Die Subscription Engine verwaltet:

- Plan
- Laufzeit
- Zahlungsstatus
- Limits
- Feature-Zugriff
- Kündigung
- Pausierung

---

# 5. Billing

Zahlungslogik:

1. Kunde wählt Plan
2. Zahlung wird verarbeitet
3. Webhook bestätigt Zahlung
4. Tenant wird aktiviert
5. Rechnung wird gespeichert

Mögliche Anbieter:

- Stripe
- später TWINT
- später Rechnung für B2B

---

# 6. Feature Flags

Jede Funktion kann pro Plan aktiviert oder deaktiviert werden.

Beispiele:

Starter:
- Telegram
- Gmail
- Basis-Matching

Pro:
- Interview Manager
- RAV Mode
- Calendar Manager

Premium:
- AI Memory
- Erweiterte Analysen
- Priorisierte Agentenläufe

---

# 7. Admin Dashboard

Das Admin Dashboard ist nur für den Betreiber.

Es zeigt:

- aktive Kunden
- MRR
- Churn
- neue Registrierungen
- Fehler
- Agentenstatus
- API-Kosten
- Anzahl Bewerbungen
- Anzahl Interviews
- offene Supportfälle

---

# 8. Agent Health Monitoring

Jeder Agent besitzt einen Status:

- Healthy
- Warning
- Failed
- Disabled

Beispiele:

Job Discovery Agent: Healthy
Gmail Agent: Healthy
Drive Agent: Warning
Telegram Agent: Failed

Fehler werden automatisch protokolliert.

---

# 9. Audit Log

Jede wichtige Aktion wird gespeichert.

Beispiele:

- Job gefunden
- Match berechnet
- Bewerbung erstellt
- Telegram gesendet
- Nutzer hat freigegeben
- Gmail hat versendet
- Antwort erkannt
- Interview erstellt
- RAV-Eintrag erzeugt

Audit Logs sind unveränderbar.

---

# 10. AI Cost Control

Jeder AI-Aufruf wird gemessen.

Pro Tenant wird gespeichert:

- Anzahl AI Requests
- Token-Verbrauch
- geschätzte Kosten
- Monatslimit
- Warnschwelle

Wenn ein Limit erreicht wird:

1. Agenten reduzieren Frequenz
2. Betreiber wird informiert
3. Kunde erhält je nach Plan Hinweis

---

# 11. Event Bus

Alle Agenten kommunizieren über Events.

Agenten rufen sich nicht direkt auf.

Beispiele:

JOB_FOUND
MATCH_COMPLETED
APPLICATION_WORKSPACE_CREATED
APPLICATION_READY_FOR_APPROVAL
APPLICATION_APPROVED
APPLICATION_SENT
EMAIL_RESPONSE_RECEIVED
INTERVIEW_DETECTED
CALENDAR_EVENT_CREATED
RAV_ENTRY_CREATED

Vorteile:

- bessere Skalierbarkeit
- weniger Abhängigkeiten
- einfacheres Debugging
- Agenten können einzeln ersetzt werden

---

# 12. Plugin-System

Externe Quellen werden über Plugins angebunden.

Beispiele:

- jobs.ch Plugin
- jobup.ch Plugin
- LinkedIn Plugin
- Indeed Plugin
- Firmenwebseiten Plugin

Regel:
Ein neues Plugin darf den Core nicht verändern.

---

# 13. Onboarding für neue Kunden

Ablauf:

1. Registrierung
2. Plan wählen
3. Google verbinden
4. Telegram verbinden
5. CV hochladen
6. Profil vervollständigen
7. Suchziele definieren
8. Testlauf
9. Agenten aktivieren

Ziel:
Ein Kunde soll in maximal 10–15 Minuten startklar sein.

---

# 14. Sicherheit

Pflichtregeln:

- OAuth verwenden
- keine Passwörter speichern
- Tokens verschlüsseln
- Tenant-Isolation erzwingen
- Logs ohne sensible Inhalte
- Zugriff jederzeit widerrufbar
- Daten exportierbar
- Daten löschbar

---

# 15. Support & Betrieb

Supportfälle müssen über das Admin Dashboard nachvollziehbar sein.

Der Betreiber sieht:

- welcher Agent Fehler hatte
- welche Bewerbung betroffen ist
- welche Integration betroffen ist
- wann der Fehler auftrat
- ob ein Retry erfolgreich war

---

# 16. Plattform-Limits

Pro Plan können Limits definiert werden:

- maximale Bewerbungen pro Monat
- maximale AI-Kosten
- maximale aktive Suchprofile
- maximale Dokumente
- maximale Telegram-Benachrichtigungen
- maximale Agentenläufe pro Tag

---

# 17. Definition of Done

Die Plattformarchitektur ist MVP-fähig, wenn:

- mehrere Tenants getrennt betrieben werden können
- Agenten nur für aktive Tenants laufen
- Audit Logs existieren
- AI-Kosten pro Tenant sichtbar sind
- Feature Flags funktionieren
- Billing vorbereitet ist
- Admin Dashboard den Systemzustand zeigt
- Integrationen tenant-spezifisch gespeichert sind

---

# 18. Nicht Bestandteil von Version 1

- White Label
- Team Accounts
- Arbeitgeberportal
- Partner API
- Mobile App
- Mehrsprachiges Admin Panel
- Enterprise SSO

---

# 19. Kernaussage

Alpine Career muss von Anfang an wie eine Plattform gedacht werden.

Nicht als einzelner Bot.

Nicht als n8n-Automation.

Nicht als Dashboard.

Sondern als autonomes, mandantenfähiges Career-Management-System.
