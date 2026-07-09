"""Seed data for Marco von Burg — first MVP user.

E-Mail bewusst auf Gmail gesetzt (nicht GMX aus dem CV).
Alle Daten aus dem Original-CV extrahiert + Setup-Daten ergaenzt.
"""

MARCO_USER = {
    "telegram_username": "Dorender",
    "name": "Marco von Burg",
    "email": "m.vonburg94@gmail.com",
}

MARCO_CV_TEXT = """Marco von Burg
IT-Systemadministrator — Cloud & Modern Workplace

geb. 08.05.1994 · Berlin (Umzug geplant) · +41 79 876 38 81 · m.vonburg94@gmail.com ·
linkedin.com/in/marcovonburg

Systemadministrator mit ueber 6 Jahren Praxis in Microsoft-365-Verwaltung, Windows-
Infrastruktur und IT-Field-Support bei einem Swisscom-Tochterunternehmen. Naechster Schritt:
Cloud-Administration mit Microsoft Azure und Modern Workplace — belegt durch die laufende
AZ-104-Zertifizierung. Strukturiert, loesungs- und kundenorientiert, zweisprachig (DE/EN).

BERUFSERFAHRUNG

Servicetechniker & Digital-Signage-Spezialist | 07/2020 – heute
JLS Digital AG (Swisscom-Gruppe) · Luzern
- Administration und Betrieb von Microsoft 365 und CMS-Plattformen; Remote-Monitoring \
einer verteilten Display- und Geraete-Infrastruktur ueber mehrere Standorte.
- Verwaltung von Benutzern, Endgeraeten und Berechtigungen; Installation, Konfiguration \
und Wartung netzwerkbasierter Systeme.
- Eigenstaendiges Troubleshooting auf Netzwerk- und Hardware-Ebene sowie IT-Field-Support \
unter Einhaltung definierter Service-Level (SLA).
- Schnittstelle zwischen Kunden und internen Teams; Koordination von Rollouts und \
Serviceeinsaetzen.

AV-Techniker | 06/2019 – 06/2020
Auviso Audio Visual Solutions AG · Emmenbruecke
- Installation, Wartung und Support netzwerkbasierter AV- und Signal-Routing-Systeme \
inkl. Audio-over-IP (Dante); Fehlerdiagnose vor Ort und remote.

Technische Temporaereinsaetze | 2017 – 2019
u. a. Seven-Air Gebr. Meyer AG (Monteur), Wirth & Co AG, Buholzer Batterien AG
- Technisches Grundhandwerk, Belastbarkeit und Zuverlaessigkeit in wechselnden \
Einsatzumgebungen; ergaenzt durch eine internationale Reisephase.

AUSBILDUNG

Fachmann Betriebsunterhalt EFZ | 2012 – 2015
Einwohnergemeinde Eschenbach · Fachrichtung Werkdienst
- Eidg. Berufsabschluss (vergleichbar mit anerkannter dualer Ausbildung in Deutschland).

ZERTIFIZIERUNGEN
In Vorbereitung 2026: Azure Administrator Associate (AZ-104), Azure Fundamentals (AZ-900), \
ITIL 4 Foundation
Abgeschlossen: Dante Certification Level 1 (L2 in Vorbereitung)

SPRACHEN
Deutsch: Muttersprache
Englisch: verhandlungssicher

INTERESSEN
Musikproduktion & DJing (Techno), Audiotechnik, Reisen
"""

MARCO_SKILLS = {
    "core": [
        "Microsoft 365",
        "Microsoft Azure",
        "Entra ID / AD",
        "Windows Server & Client",
        "Netzwerk (LAN/WAN, TCP/IP)",
        "IT-Field-Support",
    ],
    "additional": [
        "CMS-Administration",
        "Remote-Monitoring",
        "ITIL 4",
        "Hardware-Diagnose",
        "Strukturierte Verkabelung",
        "Audio-over-IP (Dante)",
    ],
    "certifications_in_progress": [
        "Azure Administrator Associate (AZ-104)",
        "Azure Fundamentals (AZ-900)",
        "ITIL 4 Foundation",
    ],
    "certifications_completed": [
        "Dante Certification Level 1",
    ],
    "languages": {
        "Deutsch": "Muttersprache",
        "Englisch": "verhandlungssicher",
    },
}

MARCO_TARGET_ROLES = {
    "titles_de": [
        "IT-Systemadministrator",
        "Cloud Administrator",
        "Microsoft 365 Administrator",
        "Azure Administrator",
        "Modern Workplace Engineer",
        "Workplace Engineer",
        "IT-Administrator",
        "IT-Support Specialist",
        "Technical Support Specialist",
    ],
    "titles_en": [
        "System Administrator",
        "Cloud Engineer",
        "M365 Admin",
        "Azure Admin",
        "IT Operations Engineer",
    ],
}

MARCO_TARGET_LOCATIONS = {
    "primary": {
        "city": "Berlin",
        "country": "DE",
        "priority": "hoch",
    },
    "secondary": [
        {"city": "Zuerich", "country": "CH"},
        {"city": "Luzern", "country": "CH"},
        {"city": "Bern", "country": "CH"},
        {"city": "Basel", "country": "CH"},
    ],
}

MARCO_SALARY = {
    "berlin": {
        "min": 48000,
        "max": 58000,
        "target": 52000,
        "currency": "EUR",
        "period": "brutto/Jahr",
    },
    "schweiz": {
        "min": 78000,
        "max": 88000,
        "target": 82000,
        "currency": "CHF",
        "period": "brutto/Jahr",
    },
}

MARCO_PREFERENCES = {
    "remote": "full_remote",
    "availability": "2026-10-01",
    "industries_preferred": [
        "IT-Dienstleister",
        "Telekommunikation",
        "Finanzwesen",
        "Gesundheitswesen",
        "Oeffentliche Verwaltung",
    ],
    "industries_excluded": [
        "Abfall / Entsorgung",
    ],
    "priority": "Berlin bevorzugt, Schweiz als Alternative",
}
