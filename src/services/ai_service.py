"""AI service — Claude API for CV optimization and cover letter generation.

Uses Anthropic Claude API to:
1. Tailor a CV to a specific job posting
2. Generate a cover letter matching the job requirements

All prompts produce German output (Schweizer Schreibweise, kein Eszett).
"""

import logging
from dataclasses import dataclass

import anthropic

from src.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class GeneratedCV:
    """Result of CV optimization."""

    summary: str
    experience: str
    skills: str
    certifications: str
    full_text: str


@dataclass
class GeneratedCoverLetter:
    """Result of cover letter generation."""

    subject: str
    body: str
    full_text: str


CV_SYSTEM_PROMPT = """\
Du bist ein erfahrener Karriereberater und CV-Spezialist fuer den \
deutschsprachigen IT-Arbeitsmarkt. Du optimierst Lebenslaeufe so, \
dass sie perfekt auf eine bestimmte Stellenausschreibung zugeschnitten sind.

Regeln:
- Schweizer Schreibweise: Kein Eszett (ss). Immer «ss» statt «ss».
- Keine Luegen oder Uebertreibungen — nur vorhandene Erfahrung umformulieren.
- Relevante Skills und Erfahrungen an den Anfang stellen.
- Keywords aus der Stellenausschreibung natuerlich einbauen.
- Professioneller, praegnanter Stil.
- Ergebnis als strukturierter Text mit klaren Abschnitten.
"""

CV_USER_PROMPT = """\
Optimiere den folgenden Lebenslauf fuer diese Stelle.

## STELLENAUSSCHREIBUNG

Titel: {job_title}
Firma: {job_company}
Standort: {job_location}
Beschreibung:
{job_description}

## ORIGINALER LEBENSLAUF

{cv_text}

## PROFIL-DATEN

Skills: {skills}
Zielrollen: {target_roles}
Verfuegbarkeit: {availability}

## AUFGABE

Erstelle einen optimierten Lebenslauf mit folgenden Abschnitten:

1. ZUSAMMENFASSUNG (3-4 Saetze, zugeschnitten auf die Stelle)
2. BERUFSERFAHRUNG (relevante Taetigkeiten hervorheben, Keywords einbauen)
3. SKILLS (nach Relevanz fuer die Stelle sortiert)
4. ZERTIFIZIERUNGEN (inkl. laufende, wenn relevant)

Formatiere jeden Abschnitt mit dem Abschnittstitel in Grossbuchstaben, \
gefolgt vom Inhalt. Trenne Abschnitte mit einer Leerzeile.
"""

COVER_LETTER_SYSTEM_PROMPT = """\
Du bist ein erfahrener Karriereberater, der Bewerbungsanschreiben \
fuer den deutschsprachigen IT-Arbeitsmarkt verfasst. Dein Ziel: \
Das Anschreiben soll klingen, als haette es ein Mensch geschrieben — \
nicht eine KI.

Stil-Regeln:
- Schweizer Schreibweise: Kein Eszett (ss). Immer «ss» statt «ss».
- Formelles «Sie», aber natuerlicher, warmer Ton — wie ein Brief, \
  den ein selbstbewusster Fachmann tatsaechlich schreiben wuerde.
- Maximal eine Seite (ca. 250-350 Woerter). Lieber kuerzer und praegnant.
- VERBOTEN: «hiermit bewerbe ich mich», «mit grossem Interesse», \
  «ich bin ueberzeugt», «ich freue mich auf», «in Ihrem Unternehmen», \
  «spannende Herausforderung», «wertvoller Beitrag», «dynamisches Team», \
  «gewinnbringend einbringen». Diese Floskeln verraten sofort KI-Texte.
- Stattdessen: Konkreter Einstieg — warum genau diese Stelle, was der \
  Bewerber dort konkret besser machen kann als andere.
- Satzlaenge variieren: Kurze Saetze neben laengeren. Nicht jeder Satz \
  gleich lang. Mal ein Einwortsatz. Mal ein Nebensatz.
- Persoenliche Note: Ein konkretes Detail, eine kleine Anekdote, oder \
  ein Bezug zur eigenen Erfahrung — etwas, das nur ein Mensch schreiben wuerde.
- Keine Aufzaehlungslisten im Anschreiben. Fliesstext.
- Nicht alles positiv formulieren. Ein ehrlicher Satz wie «Das Thema X \
  ist fuer mich Neuland, aber...» wirkt authentischer als Perfektion.
- Verfuegbarkeit und Gehaltsvorstellung nur erwaehnen wenn explizit verlangt.
"""

COVER_LETTER_USER_PROMPT = """\
Erstelle ein Bewerbungsanschreiben fuer diese Stelle.

## STELLENAUSSCHREIBUNG

Titel: {job_title}
Firma: {job_company}
Standort: {job_location}
Beschreibung:
{job_description}

## BEWERBER

Name: {name}
Aktuelle Rolle: IT-Systemadministrator — Cloud & Modern Workplace
Erfahrung: 6+ Jahre (Swisscom-Tochter JLS Digital AG)
Kernkompetenzen: {skills}
Zertifizierungen in Arbeit: {certs_in_progress}

## OPTIMIERTER LEBENSLAUF (ZUSAMMENFASSUNG)

{cv_summary}

## AUFGABE

Schreibe ein professionelles Bewerbungsanschreiben mit:

1. BETREFF (eine praegnante Betreffzeile fuer die E-Mail)
2. ANSCHREIBEN (der vollstaendige Brieftext)

Formatiere so:
BETREFF: [Betreffzeile]

ANSCHREIBEN:
[Vollstaendiger Text]
"""


def _get_client() -> anthropic.Anthropic:
    """Create Anthropic client."""
    if not settings.anthropic_api_key:
        raise RuntimeError("ANTHROPIC_API_KEY ist nicht konfiguriert")
    return anthropic.Anthropic(api_key=settings.anthropic_api_key)


async def optimize_cv(
    cv_text: str,
    skills: list[str],
    target_roles: list[str],
    availability: str,
    job_title: str,
    job_company: str,
    job_location: str,
    job_description: str,
) -> GeneratedCV:
    """Optimize a CV for a specific job posting using Claude API.

    Args:
        cv_text: Raw CV text.
        skills: List of core skills.
        target_roles: List of target job titles.
        availability: Start date.
        job_title: Target job title.
        job_company: Target company name.
        job_location: Target job location.
        job_description: Full job description text.

    Returns:
        GeneratedCV with optimized sections.
    """
    import asyncio

    client = _get_client()

    user_prompt = CV_USER_PROMPT.format(
        job_title=job_title,
        job_company=job_company,
        job_location=job_location,
        job_description=job_description[:3000],
        cv_text=cv_text,
        skills=", ".join(skills),
        target_roles=", ".join(target_roles),
        availability=availability or "Nach Vereinbarung",
    )

    # Claude API ist synchron — in Thread ausfuehren
    response = await asyncio.to_thread(
        client.messages.create,
        model=settings.anthropic_model,
        max_tokens=settings.anthropic_max_tokens,
        system=CV_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    full_text = response.content[0].text
    logger.info(
        "CV optimized",
        extra={
            "job_title": job_title,
            "tokens_in": response.usage.input_tokens,
            "tokens_out": response.usage.output_tokens,
        },
    )

    # Abschnitte parsen
    sections = _parse_cv_sections(full_text)

    return GeneratedCV(
        summary=sections.get("zusammenfassung", ""),
        experience=sections.get("berufserfahrung", ""),
        skills=sections.get("skills", ""),
        certifications=sections.get("zertifizierungen", ""),
        full_text=full_text,
    )


async def generate_cover_letter(
    name: str,
    skills: list[str],
    certs_in_progress: list[str],
    cv_summary: str,
    job_title: str,
    job_company: str,
    job_location: str,
    job_description: str,
) -> GeneratedCoverLetter:
    """Generate a cover letter for a specific job posting using Claude API.

    Args:
        name: Applicant's name.
        skills: List of core skills.
        certs_in_progress: Certifications being worked on.
        cv_summary: Summary from optimized CV.
        job_title: Target job title.
        job_company: Target company name.
        job_location: Target job location.
        job_description: Full job description text.

    Returns:
        GeneratedCoverLetter with subject and body.
    """
    import asyncio

    client = _get_client()

    user_prompt = COVER_LETTER_USER_PROMPT.format(
        job_title=job_title,
        job_company=job_company,
        job_location=job_location,
        job_description=job_description[:3000],
        name=name,
        skills=", ".join(skills),
        certs_in_progress=", ".join(certs_in_progress) or "Keine",
        cv_summary=cv_summary[:1000],
    )

    response = await asyncio.to_thread(
        client.messages.create,
        model=settings.anthropic_model,
        max_tokens=settings.anthropic_max_tokens,
        system=COVER_LETTER_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    full_text = response.content[0].text
    logger.info(
        "Cover letter generated",
        extra={
            "job_title": job_title,
            "tokens_in": response.usage.input_tokens,
            "tokens_out": response.usage.output_tokens,
        },
    )

    # Betreff und Text parsen
    subject, body = _parse_cover_letter(full_text)

    # Humanizer-Pass: Text natuerlicher machen
    body = await humanize_text(body)

    return GeneratedCoverLetter(
        subject=subject,
        body=body,
        full_text=f"BETREFF: {subject}\n\nANSCHREIBEN:\n{body}",
    )


HUMANIZER_SYSTEM_PROMPT = """\
Du bist ein Lektor, der KI-generierte Bewerbungsanschreiben so ueberarbeitet, \
dass sie nicht mehr als KI-Text erkennbar sind. Du aenderst den INHALT nicht — \
nur den Stil.

Deine Eingriffe:
1. FLOSKELN ERSETZEN: Ersetze generische Formulierungen durch konkretere. \
   «Ich bringe umfangreiche Erfahrung mit» → «In 6 Jahren bei JLS Digital \
   habe ich...». Jeder Satz muss eine konkrete Information transportieren.
2. SATZRHYTHMUS BRECHEN: KI schreibt gleichmaessig lange Saetze. Brich das \
   auf. Kurz. Dann wieder laenger mit einem Nebensatz, der den Gedanken weiter \
   ausfuehrt. Variation ist menschlich.
3. UEBERGAENGE VARIIEREN: Nicht jeder Absatz beginnt mit «Ich». Manchmal \
   mit dem Unternehmen, manchmal mit einer Beobachtung, manchmal direkt \
   mit der Sache.
4. EINE ECKE LASSEN: Perfekte Texte sind verdaechtig. Lass eine leicht \
   unkonventionelle Formulierung stehen oder baue eine ein — etwas, das \
   ein Mensch so formulieren wuerde, eine KI aber nicht.
5. REDUNDANZ ENTFERNEN: KI wiederholt sich gerne in anderen Worten. \
   Streiche Saetze die dasselbe nochmal sagen.

Regeln:
- Schweizer Schreibweise: Kein Eszett (ss). Immer «ss» statt «ss».
- Laenge NICHT erhoehen — eher etwas kuerzen.
- Keine neuen Fakten erfinden.
- Ausgabe: NUR der ueberarbeitete Text, keine Kommentare.
"""


async def humanize_text(text: str) -> str:
    """Run a second Claude pass to humanize AI-generated text.

    Takes a cover letter or similar text and rewrites it to sound
    more naturally human-written while preserving the content.

    Args:
        text: The AI-generated text to humanize.

    Returns:
        Humanized version of the text.
    """
    import asyncio

    client = _get_client()

    response = await asyncio.to_thread(
        client.messages.create,
        model=settings.anthropic_model,
        max_tokens=settings.anthropic_max_tokens,
        system=HUMANIZER_SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": (
                "Ueberarbeite dieses Bewerbungsanschreiben, damit es "
                "natuerlicher und menschlicher klingt:\n\n"
                f"{text}"
            ),
        }],
    )

    result = response.content[0].text
    logger.info(
        "Text humanized",
        extra={
            "tokens_in": response.usage.input_tokens,
            "tokens_out": response.usage.output_tokens,
            "original_len": len(text),
            "humanized_len": len(result),
        },
    )
    return result


def _parse_cv_sections(text: str) -> dict[str, str]:
    """Parse CV text into sections by uppercase headers."""
    sections: dict[str, str] = {}
    current_key = ""
    current_lines: list[str] = []

    for line in text.split("\n"):
        stripped = line.strip()
        # Erkennung: Zeile besteht nur aus Grossbuchstaben (+ Leerzeichen)
        clean = stripped.replace("*", "").replace("#", "").strip()
        if clean and clean.upper() == clean and len(clean) > 3 and clean.isalpha():
            if current_key:
                sections[current_key] = "\n".join(current_lines).strip()
            current_key = clean.lower()
            current_lines = []
        else:
            current_lines.append(line)

    if current_key:
        sections[current_key] = "\n".join(current_lines).strip()

    return sections


def _parse_cover_letter(text: str) -> tuple[str, str]:
    """Parse cover letter into subject line and body text."""
    subject = ""
    body = text

    for line in text.split("\n"):
        stripped = line.strip()
        upper = stripped.upper()
        if upper.startswith("BETREFF:") or upper.startswith("BETREFF :"):
            subject = stripped.split(":", 1)[1].strip()
            # Body ist alles nach der ANSCHREIBEN-Markierung
            continue

    # Anschreiben-Text extrahieren
    markers = ["ANSCHREIBEN:", "ANSCHREIBEN :", "---"]
    for marker in markers:
        if marker in text.upper():
            idx = text.upper().index(marker)
            body = text[idx + len(marker):].strip()
            break

    if not subject:
        subject = f"Bewerbung als {body.split()[0] if body else 'Fachkraft'}"

    return subject, body
