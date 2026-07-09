# Blueprint 006
# Workflow Engine

Projekt: Alpine Career
Version: 1.0
Status: Draft

---

# Ziel

Dieses Dokument definiert sämtliche automatisierten Abläufe (Workflows) von Alpine Career.
Jeder Workflow wird serverseitig ausgeführt und durch Ereignisse (Events) ausgelöst.

---

# Workflow 01 – Onboarding

Trigger:
- Neuer Benutzer

Ablauf:
1. Konto erstellen
2. Google verbinden
3. Telegram verbinden
4. Dokumente hochladen
5. Profil analysieren
6. AI Memory initialisieren
7. Stellensuche aktivieren

Ergebnis:
System arbeitet autonom.

---

# Workflow 02 – Stellensuche

Trigger:
- Zeitplan (z. B. alle 2 Stunden)

Ablauf:
1. Stellenplattformen durchsuchen
2. Dubletten entfernen
3. Match berechnen
4. Passende Stellen auswählen
5. Application Workspace vorbereiten

Ergebnis:
Bewerbung bereit zur Freigabe.

---

# Workflow 03 – Freigabe

Trigger:
- Bewerbung fertig

Telegram:
- Freigeben
- Bearbeiten
- Ablehnen
- Später erinnern

Bei Freigabe:
- Gmail Agent versendet
- Drive archiviert
- Status aktualisieren

---

# Workflow 04 – Antwortüberwachung

Trigger:
- Neue Gmail-Nachricht

Erkennung:
- Eingangsbestätigung
- Rückfrage
- Interview
- Absage
- Zusage

Aktionen:
- Status aktualisieren
- Telegram informieren
- Drive archivieren

---

# Workflow 05 – Interview

Trigger:
- Interview erkannt

Ablauf:
1. Kalender aktualisieren
2. Firmenanalyse erstellen
3. Interviewfragen generieren
4. Vorbereitung an Telegram senden
5. Nachbereitung vorbereiten

---

# Workflow 06 – RAV

Trigger:
- Neue Bewerbung

Aktionen:
- Arbeitsbemühung erfassen
- Monatsziel aktualisieren
- Export vorbereiten

---

# Workflow 07 – Täglicher Digest

Jeden Morgen:

Telegram sendet:
- Neue Jobs
- Offene Aufgaben
- Interviews
- Bewerbungsziel
- Empfehlungen

---

# Workflow 08 – Fehlerbehandlung

Bei Fehler:
- Log schreiben
- Automatisch erneut versuchen
- Nutzer nur informieren, wenn Eingriff nötig

---

# Workflow-Regeln

- Jeder Workflow ist unabhängig.
- Jeder Schritt wird protokolliert.
- Kein Versand ohne Freigabe.
- Jeder Workflow kann neu gestartet werden.
- Jeder Workflow besitzt eine eindeutige ID.

---

# Definition of Done

Alle Workflows laufen autonom auf dem Server, sind fehlertolerant und benötigen den Nutzer nur bei Entscheidungen.
