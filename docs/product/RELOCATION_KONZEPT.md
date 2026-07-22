# Konzept: Alpine Career als Relocation-Plattform DE/AT → CH

> Status: Entwurf | Datum: 2026-07-15
> Erstellt von: Dave
> Umsetzung: Noch nicht gestartet — Marco-MVP zuerst abschliessen

---

## Vision

Alpine Career wird zur **Full-Service-Plattform fuer deutschsprachige Fachkraefte aus Deutschland und Oesterreich**, die in die Schweiz wechseln moechten. Der AI-Agent begleitet den gesamten Prozess — von der Jobsuche ueber die Bewerbung bis zur Relocation.

## Markt und Chance

### Fachkraeftemangel Schweiz

Die Schweiz braucht bis 2033 rund **128'600 zusaetzliche ICT-Spezialisten**. Selbst nach Beruecksichtigung von Absolventen und Zuwanderung bleibt ein Engpass von ca. 54'400 Personen. Die Branche "Planung, Beratung, Informatik" ist der groesste Arbeitgeber fuer auslaendische Fachkraefte.

### Gehaltssprung als Motivator

IT-Fachkraefte verdienen in der Schweiz **30–50% mehr** als in Deutschland. Konkret:

| Rolle | Deutschland (ca.) | Schweiz (ca.) | Faktor |
|---|---|---|---|
| Sysadmin / Cloud Admin | 45'000–55'000 EUR | 85'000–100'000 CHF | ~1.7x |
| Software Engineer (Mid) | 55'000–70'000 EUR | 100'000–120'000 CHF | ~1.7x |
| DevOps / Cloud Engineer | 60'000–75'000 EUR | 110'000–130'000 CHF | ~1.7x |
| Senior / Lead | 75'000–95'000 EUR | 130'000–160'000 CHF | ~1.6x |

### Zielgruppe

- **Primaer:** Deutsche und oesterreichische IT-Fachkraefte (25–45 Jahre), die in die Schweiz wechseln wollen
- **Sekundaer:** Andere deutschsprachige Berufe mit Fachkraeftemangel (Gesundheit, Ingenieurwesen, Finanzen)
- **Gemeinsam:** Alle sind EU-Buerger und profitieren vom Freizuegigkeitsabkommen

---

## Was der Full-Service Agent kann

### 1. Jobsuche (bereits gebaut fuer Marco)

- Schweizer Jobportale durchsuchen (jobs.ch, SwissDevJobs, etc.)
- AI-Matching: Profil vs. Stelle
- Standortfilter: Zuerich, Bern, Basel, Luzern, etc.
- Gehaltseinschaetzung fuer CH-Markt

### 2. Bewerbung (bereits gebaut fuer Marco)

- CV auf Schweizer Standards anpassen (Foto, Handschrift, Referenzen)
- Anschreiben generieren
- PDF-Generierung
- Bewerbung per Gmail versenden
- Tracking aller Bewerbungen

### 3. Gehaltsvergleich (NEU)

- Aktuelles DE/AT-Gehalt eingeben
- Umrechnung mit branchenspezifischem Faktor
- Kaufkraftvergleich (Miete, Krankenkasse, Steuern, Lebenshaltung)
- Netto-Vergleich: "Was bleibt am Ende mehr?"
- Kantonale Unterschiede (Steuern variieren stark)

### 4. Bewilligungscheck (NEU)

- Automatische Bestimmung des richtigen Ausweistyps:
  - **Ausweis L** — Kurzaufenthalt (unter 12 Monate, an Kanton gebunden)
  - **Ausweis B** — Aufenthalt (ab 12 Monate, 5 Jahre gueltig, Familiennachzug moeglich)
  - **Ausweis G** — Grenzgaenger (wohnt in DE/AT, arbeitet in CH)
  - **Meldeverfahren** — unter 90 Tage, keine Bewilligung noetig
- Checkliste: Was braucht man fuer den Antrag?
- Zeitplan: Wann was erledigen?

### 5. Relocation-Guide (NEU)

Interaktive Checkliste mit Zeitstrahl:

**3 Monate vorher:**
- Arbeitsvertrag unterschreiben
- Wohnung in der Schweiz suchen
- Kuendigung aktuelle Wohnung DE/AT

**1 Monat vorher:**
- Abmeldung beim Einwohnermeldeamt DE/AT
- Umzugsunternehmen beauftragen
- Zollformular 18.44 vorbereiten (Uebersiedlungsgut)
- Inventarliste erstellen

**Nach Ankunft (innerhalb 14 Tage):**
- Anmeldung bei der Einwohnerkontrolle der Gemeinde
- Aufenthaltsbewilligung beantragen (Arbeitsvertrag + Pass)

**Innerhalb 3 Monate:**
- Schweizer Krankenversicherung abschliessen (obligatorisch)
- Bankkonto eroeffnen
- AHV-Nummer erhalten
- Steuererklarung vorbereiten

**Dokumente-Checkliste:**
- Gultiger Reisepass oder Personalausweis
- Arbeitsvertrag (Original)
- Abmeldebescheinigung aus DE/AT
- Mietvertrag CH
- Passfotos
- Zollformular 18.44 + Inventarliste (3x, original unterschrieben)

---

## Geschaeftsmodell (Ideen)

| Modell | Beschreibung | Preis |
|---|---|---|
| Freemium | Jobsuche + 3 Bewerbungen gratis | Kostenlos |
| Pro | Unbegrenzte Bewerbungen + CV-Optimierung | CHF 29/Monat |
| Relocation | Pro + Gehaltsrechner + Bewilligungscheck + Checkliste | CHF 49/Monat |
| Concierge | Alles + persoenliche Beratung (spaeter) | CHF 149 einmalig |

---

## Technische Erweiterungen

### Was schon da ist (Marco-MVP)

- Telegram Bot mit Jobsuche, CV, Anschreiben, Gmail, Tracking
- PostgreSQL, Redis, Docker auf Hetzner
- Claude AI fuer Textgenerierung

### Was dazukommt

| Feature | Aufwand | Prioritaet |
|---|---|---|
| Multi-User (Telegram-basiert) | Mittel | Hoch — sofort nach Marco |
| Gehaltsrechner-Modul | Klein | Hoch — hoher Mehrwert |
| Bewilligungscheck-Modul | Klein | Hoch — Alleinstellung |
| Relocation-Checkliste (interaktiv) | Mittel | Mittel |
| Schweizer CV-Anpassung (Foto, Referenzen) | Klein | Hoch |
| Web-Interface (Landing Page + Dashboard) | Gross | Spaeter |
| Payment Integration (Stripe) | Mittel | Spaeter |
| Onboarding-Flow fuer neue Nutzer | Mittel | Hoch |

### Datenquellen fuer Relocation-Infos

- Staatssekretariat fuer Migration (SEM): sem.admin.ch
- ch.ch (offizielle Schweizer Behoerden-Plattform)
- Kantonale Steuerrechner (z.B. Zuerich, Bern)
- Krankenkassenvergleich (comparis.ch, priminfo.admin.ch)
- Mietpreise (homegate.ch, comparis.ch)

---

## Abgrenzung zu Wettbewerbern

| Anbieter | Was sie bieten | Was Alpine Career besser macht |
|---|---|---|
| einwandern-schweiz.ch | Infoportal, Beratung | AI-Agent automatisiert den Prozess |
| Grenzgaengerdienst | Steuer/Versicherungsberatung | Wir decken den ganzen Weg ab |
| Recruiting-Agenturen | Jobvermittlung | Nutzer behaelt Kontrolle, keine Provision |
| LinkedIn / jobs.ch | Jobportale | Plus Bewerbung + Relocation in einem |

**Alleinstellung:** Kein anderer Dienst verbindet AI-gestuetzte Jobsuche, automatische Bewerbung UND Relocation-Begleitung in einem Tool.

---

## Naechste Schritte

1. ✅ Marco-MVP abschliessen (Gmail OAuth fertig machen)
2. Konzept reviewen und verfeinern
3. Multi-User-Faehigkeit einbauen
4. Gehaltsrechner als erstes Relocation-Feature
5. Landing Page fuer fruehe Nutzerakquise
6. Beta mit 5–10 Testnutzern aus DE/AT

---

## Quellen

- [Arbeitsbewilligung Schweiz 2026](https://einwandern-schweiz.ch/arbeiten-in-der-schweiz/arbeitsbewilligung/)
- [EU/EFTA-Buerger in der Schweiz (SEM)](https://www.sem.admin.ch/sem/en/home/themen/fza_schweiz-eu-efta/eu-efta_buerger_schweiz.html)
- [IT-Loehne Schweiz 2026 (Robert Half)](https://www.roberthalf.com/ch/de/insights/gehaltsuebersicht/it-bereich)
- [IT Gehaelter Schweiz (ITBoard)](https://www.itboard.ch/salaries)
- [Gehaltsvergleich DE-CH (CIO)](https://www.cio.de/article/4103134/it-branche-der-grosse-gehaltsvergleich-2025-2026.html)
- [Fachkraeftemangel Schweiz (UZH)](https://www.stellenmarktmonitor.uzh.ch/de/indices/fachkraeftemangel.html)
- [ICT-Fachkraeftebedarf 2026 (digitalswitzerland)](https://digitalswitzerland.com/wp-content/uploads/2021/02/IWSB_ICT-Bildungsbedarf_2026.pdf)
- [Umzug Schweiz Checkliste](https://einwandern-schweiz.ch/umzug-schweiz-checkliste/)
- [Aufenthaltsbewilligungen B und L](https://einwandern-schweiz.ch/aufenthaltsbewilligung-schweiz/)
- [Aufenthaltsbewilligung Ausweis B (SEM)](https://www.sem.admin.ch/sem/en/home/themen/aufenthalt/eu_efta/ausweis_b_eu_efta.html)
