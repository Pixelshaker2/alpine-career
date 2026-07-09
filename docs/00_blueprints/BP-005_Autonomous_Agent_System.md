# Blueprint 005
# Autonomous Agent System

Projekt: Alpine Career
Version: 1.1
Status: Draft

---

# Ziel

Dieses Dokument definiert alle autonomen Agenten, welche Alpine Career serverseitig 24/7 ausführen.

Der Nutzer startet diese Agenten nicht manuell. Sie arbeiten kontinuierlich im Hintergrund.

Alpine Career ist Automation First und Telegram First.

---

# Grundprinzip

Der Nutzer richtet Alpine Career einmal ein.

Danach arbeitet das System autonom.

Der Nutzer wird nur dann einbezogen, wenn eine Entscheidung nötig ist.

Keine Bewerbung wird ohne ausdrückliche Freigabe versendet.

---

# Architektur

Jeder Agent besitzt:

- eine klar definierte Aufgabe
- eigene Ein- und Ausgaben
- Protokollierung
- Fehlerbehandlung
- Wiederholungslogik
- klare Grenzen zu anderen Agenten

Alle Agenten kommunizieren über den zentralen Alpine Career Core.

---

# Agent 01 – Job Discovery Agent

Aufgabe:
Durchsucht aktivierte Stellenquellen.

Verantwortung:
- neue Stellen erkennen
- Dubletten entfernen
- Stellen normalisieren
- Quelle speichern
- Inserat archivieren

Output:
Normalisierte Job-Datensätze.

---

# Agent 02 – Match Agent

Aufgabe:
Berechnet den persönlichen Match Score zwischen Nutzerprofil und Stelle.

Berücksichtigt:

- Profil
- Skills
- Erfahrung
- Region
- Lohn
- Pensum
- Präferenzen
- No-Gos
- Dokumente
- Bewerbungsziele

Output:
Match Analyse mit Score, Begründung, Risiken und Empfehlung.

---

# Agent 03 – Application Workspace Agent

Aufgabe:
Erstellt für jede passende Stelle einen isolierten Bewerbungs-Workspace.

Dieser Agent ist zentral, weil hier die komplette Bewerbung vorbereitet wird, bevor irgendetwas versendet wird.

Er erstellt:

- eindeutige Application ID
- Bewerbungsordner
- Mail-Entwurf als Systemobjekt
- Motivationsschreiben
- passende CV-Version
- Liste der Anhänge
- Vorschau für Telegram
- vollständiges Log

Wichtig:
Die Bewerbung wird zuerst im System vorbereitet, nicht direkt in Gmail.

Beispiel Application ID:

APP-2026-000245

Diese ID verbindet:

- Job
- Firma
- Bewerbung
- Mail
- Anhänge
- Google Drive
- Telegram-Freigabe
- Versand
- Antwort
- Interview
- RAV-Eintrag

---

# Agent 04 – Application Agent

Aufgabe:
Erstellt die inhaltlichen Bewerbungsunterlagen.

Erzeugt:

- E-Mail-Text
- Betreff
- Motivationsschreiben
- CV-Auswahl
- Dokumentenempfehlung
- kurze Begründung für den Nutzer

Output:
Fertiges Bewerbungspaket im Application Workspace.

---

# Agent 05 – Drive Agent

Aufgabe:
Organisiert automatisch Google Drive.

Erstellt pro Bewerbung:

/Bewerbungen
    /YYYY-MM-DD_Firma_Stellentitel
        /01_Inserat
        /02_Bewerbung
        /03_Kommunikation
        /04_Interview
        /05_Vertrag
        /99_Log

Speichert:

- Inserat
- Mailtext
- Motivationsschreiben
- CV
- Zeugnisse
- Diplome
- Versandnachweis
- Antworten
- Interviewnotizen
- Log-Datei

---

# Agent 06 – Gmail Agent

Aufgabe:
Erstellt und versendet E-Mails über Gmail API.

Der Gmail Agent darf erst aktiv senden, wenn eine explizite Freigabe vorhanden ist.

Ablauf:

1. Application Workspace vollständig prüfen
2. Empfänger prüfen
3. Betreff prüfen
4. Mailtext prüfen
5. Anhänge prüfen
6. Freigabe prüfen
7. Mail über Gmail API senden
8. Versandstatus speichern
9. gesendete Mail im Drive archivieren

Wichtig:
Gmail ist Versandkanal, nicht primärer Arbeitsort.

Die Bewerbung entsteht im Application Workspace.

---

# Agent 07 – Telegram Agent

Aufgabe:
Kommunikation mit dem Nutzer.

Telegram ist das Hauptinterface.

Sendet:

- neue Stellen
- fertige Bewerbungen
- Freigaben
- Erinnerungen
- Interviewinfos
- Monatsziele
- Fehlerhinweise

Empfängt:

- Freigeben
- Bearbeiten
- Ablehnen
- Später erinnern
- Status abfragen

Beispiel:

Neue Bewerbung bereit

Firma: Muster AG
Rolle: Marketing Manager 60–80 %
Match: 94 %

Die Bewerbung ist vollständig vorbereitet.

Anhänge:
- CV_Marketing.pdf
- Motivationsschreiben.pdf
- Arbeitszeugnisse.pdf

[Freigeben]
[Bearbeiten]
[Ablehnen]

---

# Agent 08 – Calendar Agent

Aufgabe:
Verwaltet automatisch Termine.

Erstellt:

- Interviewtermine
- Erinnerungen
- Follow-up-Aufgaben
- Vorbereitungsslots

---

# Agent 09 – Interview Agent

Aufgabe:
Bereitet Bewerbungsgespräche vor.

Erstellt:

- Firmenanalyse
- Interviewfragen
- Antwortideen
- Confidence Mode
- Checkliste
- Nachbereitungsfragen
- Danke-Mail-Entwurf

---

# Agent 10 – RAV Agent

Optional.

Aufgaben:

- Arbeitsbemühungen zählen
- Monatsziel überwachen
- Bewerbung dokumentieren
- Export vorbereiten
- Nachweise verlinken

Wichtig:
Der RAV Agent dokumentiert nur. Er gibt keine Rechtsberatung.

---

# Agent 11 – AI Memory Agent

Lernt kontinuierlich.

Merkt sich:

- Präferenzen
- Firmen
- Absagen
- Zusagen
- Interviewerfahrungen
- Bewerbungsverhalten
- erfolgreiche Formulierungen
- abgelehnte Branchen oder Firmen

Verbessert zukünftige Empfehlungen.

---

# Agent 12 – Response Monitoring Agent

Aufgabe:
Überwacht eingehende Antworten im Gmail-Konto.

Erkennt:

- Eingangsbestätigungen
- Absagen
- Intervieweinladungen
- Rückfragen
- Zusagen

Aktualisiert:

- Bewerbungsstatus
- Dashboard
- Drive-Archiv
- RAV-Nachweis
- Telegram-Benachrichtigung

---

# Hauptprozess Bewerbung

1. Job Discovery Agent findet Stelle
2. Match Agent bewertet Stelle
3. Application Workspace Agent erstellt Workspace
4. Application Agent erstellt Bewerbung
5. Drive Agent erstellt Ordnerstruktur
6. Telegram Agent sendet Freigabe
7. Nutzer entscheidet
8. Gmail Agent versendet bei Freigabe
9. Response Monitoring Agent überwacht Antworten
10. Calendar Agent erstellt Termine bei Interview
11. Interview Agent bereitet Gespräch vor
12. RAV Agent dokumentiert Bewerbung

---

# Business Rules

- Kein Agent versendet Bewerbungen ohne Freigabe.
- Jeder Agent schreibt Logs.
- Jeder Agent kann einzeln deaktiviert werden.
- Fehler eines Agenten dürfen andere Agenten nicht stoppen.
- Jede Bewerbung erhält eine eindeutige Application ID.
- Jede Bewerbung erhält einen eigenen Workspace.
- Jede gesendete Bewerbung wird archiviert.
- Anhänge müssen vor dem Versand validiert werden.
- Empfängeradresse muss vor dem Versand validiert werden.
- Der Nutzer kann jede Bewerbung ablehnen.
- Der Nutzer kann jede Bewerbung bearbeiten lassen.

---

# Definition of Done

Das autonome Agentensystem ist MVP-fähig, wenn:

- passende Stellen automatisch erkannt werden
- Bewerbungen vollständig vorbereitet werden
- ein Application Workspace pro Bewerbung entsteht
- Telegram-Freigabe funktioniert
- Gmail erst nach Freigabe sendet
- Google Drive automatisch archiviert
- Antworten erkannt und zugeordnet werden
- Interviews vorbereitet und im Kalender erfasst werden
- RAV-Daten dokumentiert werden können

---

# Nicht Bestandteil dieses Blueprints

- UI-Design
- Datenbank-Schema
- Zahlungsmodell
- Recruiting-Funktionen
- Arbeitgeberportal
