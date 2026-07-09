# Produkt -- alpine-career

> Status: Entwurf | Letzte Aktualisierung: 2026-07-02

## 1. Produktvision

alpine-career macht KI-Agenten fuer alle zugaenglich -- beginnend mit dem Schweizer Arbeitsmarkt. Die Plattform bietet spezialisierte Agenten, die Menschen bei komplexen, wiederkehrenden Aufgaben unterstuetzen. Der erste Agent, der Career Agent, begleitet Stellensuchende in der Schweiz durch den gesamten Bewerbungsprozess.

**Langfristige Vision:** Eine Plattform, auf der verschiedene KI-Agenten fuer unterschiedliche Lebensbereiche bereitstehen -- Karriere, Finanzen, Gesundheit, Bildung. Jeder Agent ist Experte in seinem Bereich und arbeitet im Auftrag des Nutzers.

## 2. Zielgruppe

**Primaere Zielgruppe: Stellensuchende in der Schweiz**

- Berufstaetige, die eine neue Stelle suchen (aktiv oder passiv)
- Berufseinsteiger nach Studium oder Lehre
- Personen in beruflicher Neuorientierung
- Fachkraefte, die aus dem Ausland in die Schweiz wechseln

**Merkmale:**
- Mehrsprachig (Deutsch, Franzoesisch, Italienisch, Englisch)
- Vertraut mit digitalen Tools, aber nicht zwingend technikaffin
- Erwarten Datenschutz und Transparenz (Schweizer Sensibilitaet)
- Bewerbungsprozesse sind zeitaufwendig und emotional belastend
- Schweizer Arbeitsmarkt hat eigene Konventionen (Foto im CV, handschriftliche Unterschrift digital, Referenzen)

## 3. Kern-Wertversprechen

**"Dein persoenlicher Karriere-Assistent, der fuer dich arbeitet -- nicht ueber dich entscheidet."**

Der Career Agent spart Stellensuchenden 10+ Stunden pro Woche, indem er:
- Repetitive Aufgaben automatisiert (Stellensuche, Anpassung von CVs)
- Qualitaet erhoeht (professionelle Anschreiben, optimierte CVs)
- Ueberblick schafft (Bewerbungsstatus, Fristen, Follow-ups)
- Immer verfuegbar ist (24/7 via Telegram)

Der Nutzer behaelt dabei stets die volle Kontrolle. Nichts wird ohne ausdrueckliche Freigabe versendet.

## 4. User Journey

```
1. Onboarding         Profil erstellen, Praeferenzen festlegen
       |
2. Profilerstellung   CV hochladen oder manuell erfassen
       |
3. Stellensuche       Agent sucht passende Stellen
       |
4. Bewerbung          CV optimieren, Anschreiben generieren
       |
5. Versand            Nutzer prueft und gibt Versand frei
       |
6. Tracking           Bewerbungsstatus verfolgen
       |
7. Interview          Vorbereitung auf Gespraeche
       |
8. Follow-up          Nachfassen, Absagen verarbeiten
```

Der Agent kommuniziert primaer ueber Telegram. Der Nutzer erhaelt proaktive Vorschlaege und kann jederzeit Anweisungen geben.

## 5. Feature-Bereiche des Career Agents

### 5.1 Profilerstellung
- Upload und Parsing bestehender CVs (PDF, DOCX)
- Strukturierte Erfassung von Berufserfahrung, Ausbildung, Skills
- Erkennung von Luecken und Verbesserungsvorschlaegen
- Mehrsprachige Profile (ein Profil, verschiedene Sprachversionen)

### 5.2 Stellensuche
- Automatische Suche auf Schweizer Jobportalen (jobs.ch, LinkedIn, Indeed CH)
- Matching basierend auf Profil, Praeferenzen und Standort
- Taeglich neue Vorschlaege mit Relevanz-Score
- Filter nach Branche, Pensum, Region, Sprachanforderungen
- Merkliste und Ausschlusskriterien

### 5.3 CV-Optimierung
- Anpassung des CVs an spezifische Stellenausschreibungen
- Keyword-Optimierung fuer ATS-Systeme (Applicant Tracking Systems)
- Schweizer CV-Konventionen (Format, Foto, Struktur)
- Generierung in verschiedenen Formaten (PDF, DOCX)
- Speicherung aller Versionen in Google Drive

### 5.4 Anschreiben-Generierung
- Individuelles Anschreiben pro Stelle
- Bezug auf Stellenausschreibung und Unternehmen
- Anpassbarer Ton (formell, modern, branchenspezifisch)
- Mehrsprachig (DE, FR, EN)
- Nutzer kann Entwurf bearbeiten vor Versand

### 5.5 Bewerbungsmanagement
- Dashboard mit allen laufenden Bewerbungen
- Status-Tracking (Entwurf, gesendet, Einladung, Absage, Angebot)
- Erinnerungen bei ausstehenden Antworten
- Statistiken (Bewerbungen pro Woche, Antwortrate, Durchlaufzeit)

### 5.6 Interview-Vorbereitung
- Recherche zum Unternehmen (Groesse, Kultur, aktuelle News)
- Branchenspezifische Interviewfragen mit Antwortvorschlaegen
- STAR-Methode fuer verhaltensbasierte Fragen
- Technische Fragen je nach Rolle
- Checkliste fuer den Interview-Tag

### 5.7 Follow-up-Tracking
- Automatische Erinnerung, wenn keine Antwort nach X Tagen
- Vorschlag fuer Follow-up-E-Mail
- Verwaltung von Absagen (Feedback-Anfrage, Netzwerk aufbauen)
- Nachverfolgung von Zusagen (Vertragsdetails, Startdatum)

## 6. Produktprinzipien

### Nutzerkontrolle
Der Agent schlaegt vor, der Nutzer entscheidet. Keine automatischen E-Mails, keine Bewerbungen ohne Freigabe. Der Nutzer kann jede Aktion rueckgaengig machen oder anpassen.

### Transparenz
Der Nutzer versteht immer, was der Agent tut und warum. Keine Black Box. Entscheidungen des Agenten werden erklaert. Datennutzung ist nachvollziehbar.

### Datenisolation
Daten eines Nutzers sind strikt von anderen getrennt. Kein Cross-Tenant-Lernen. Keine Weitergabe an Dritte. DSGVO- und DSG-konform (Schweizer Datenschutzgesetz).

### Kein Auto-Send
E-Mails und Bewerbungen werden immer als Entwurf erstellt. Versand erfolgt ausschliesslich nach expliziter Freigabe durch den Nutzer. Dies ist nicht konfigurierbar -- es ist ein Grundsatz.

### Schweizer Kontext
Der Agent versteht den Schweizer Arbeitsmarkt: regionale Unterschiede, Sprachanforderungen, kulturelle Normen, uebliche Gehaelter, Arbeitsbewilligungen.

### Einfachheit
Features werden nur gebaut, wenn sie einen klaren Nutzen fuer Stellensuchende haben. Komplexitaet wird im System gehalten, nicht zum Nutzer durchgereicht.

## 7. Erfolgsmetriken

> Placeholder -- wird nach MVP-Launch mit echten Daten befuellt

**Nutzermetriken:**
- Registrierungen pro Monat
- Aktive Nutzer (woechentlich)
- Retentionsrate nach 30/60/90 Tagen
- Net Promoter Score (NPS)

**Agentenmetriken:**
- Anzahl generierter CVs und Anschreiben
- Stellenvorschlaege pro Nutzer und Tag
- Akzeptanzrate der Vorschlaege
- Zeit von Stellenvorschlag bis Bewerbungsversand

**Geschaeftsmetriken:**
- Conversion Rate (kostenlos zu bezahlt)
- Monthly Recurring Revenue (MRR)
- Customer Acquisition Cost (CAC)
- Customer Lifetime Value (CLV)

## 8. Zukuenftige Agenten (Ideen)

> Placeholder -- diese Liste dient der Inspiration und ist nicht priorisiert

- **Finance Agent:** Persoenliches Budgetmanagement, Steueroptimierung (CH)
- **Learning Agent:** Weiterbildungsempfehlungen basierend auf Karrierezielen
- **Freelance Agent:** Projektakquise, Offerten, Rechnungsstellung fuer Freelancer
- **Immigration Agent:** Unterstuetzung bei Arbeitsbewilligungen und Umzug in die Schweiz
- **Networking Agent:** LinkedIn-Optimierung, Kontaktpflege, Event-Empfehlungen

Jeder neue Agent nutzt die gemeinsame Plattform-Infrastruktur (Auth, Multi-Tenancy, Integrationen, Event-System) und bringt eigene Domain-Logik mit.

## Naechste Schritte

- [ ] User Research mit 5-10 Stellensuchenden durchfuehren
- [ ] MVP-Scope definieren (minimaler Feature-Set fuer Launch)
- [ ] Preismodell entwerfen
- [ ] Onboarding-Flow detaillieren
- [ ] Telegram-Bot-Konversationsdesign erstellen
