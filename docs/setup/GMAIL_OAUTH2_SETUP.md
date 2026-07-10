# Gmail OAuth2 Setup — Anleitung fuer Marco

Diese Anleitung erklaert Schritt fuer Schritt, wie du den Gmail-Zugang fuer den Alpine Career Bot einrichtest. Du brauchst dazu deinen Google-Account (m.vonburg94@gmail.com) und ca. 10 Minuten.

---

## Schritt 1: Google Cloud Console oeffnen

1. Oeffne https://console.cloud.google.com
2. Melde dich mit **m.vonburg94@gmail.com** an
3. Oben in der Leiste klicke auf das Projekt-Dropdown → **"Neues Projekt"**
4. Projektname: **Alpine Career Bot**
5. Klicke **"Erstellen"**
6. Warte bis das Projekt erstellt ist und wechsle darauf (oben in der Leiste)

---

## Schritt 2: Gmail API aktivieren

1. Im linken Menu: **"APIs & Dienste"** → **"Bibliothek"**
2. Suche nach **"Gmail API"**
3. Klicke auf das Ergebnis "Gmail API"
4. Klicke den blauen Button **"Aktivieren"**

---

## Schritt 3: OAuth-Zustimmungsbildschirm einrichten

1. Im linken Menu: **"APIs & Dienste"** → **"OAuth-Zustimmungsbildschirm"**
2. Waehle **"Extern"** → **"Erstellen"**
3. Fuelle aus:
   - **App-Name:** Alpine Career Bot
   - **E-Mail-Adresse des Nutzersupports:** m.vonburg94@gmail.com
   - **Kontaktdaten des Entwicklers:** m.vonburg94@gmail.com
4. Klicke **"Speichern und fortfahren"**
5. Seite "Bereiche" → einfach **"Speichern und fortfahren"** (nichts auswaehlen)
6. Seite "Testnutzer":
   - Klicke **"+ Nutzer hinzufuegen"**
   - Gib ein: **m.vonburg94@gmail.com**
   - Klicke **"Hinzufuegen"**
7. Klicke **"Speichern und fortfahren"**

---

## Schritt 4: OAuth-Anmeldedaten erstellen

1. Im linken Menu: **"APIs & Dienste"** → **"Anmeldedaten"**
2. Klicke oben **"+ Anmeldedaten erstellen"** → **"OAuth-Client-ID"**
3. Anwendungstyp: **"Desktopanwendung"**
4. Name: **Alpine Career CLI**
5. Klicke **"Erstellen"**
6. Ein Dialog erscheint mit Client-ID und Client-Secret
7. Klicke **"JSON herunterladen"** (wichtig!)
8. Die heruntergeladene Datei heisst z.B. `client_secret_...json`

---

## Schritt 5: Datei an Dave schicken

Schicke die heruntergeladene JSON-Datei an Dave (per Telegram, WhatsApp oder E-Mail).

**Wichtig:**
- Die Datei enthaelt KEINE Passwoerter oder Zugangsdaten zu deinem Gmail
- Sie enthaelt nur die "App-Identitaet", damit der Bot sich bei Google vorstellen kann
- Im naechsten Schritt wirst du nochmal gefragt, ob du dem Bot Zugriff erlauben willst

---

## Schritt 6: Zugriff erlauben (zusammen mit Dave)

Dave wird ein kleines Script ausfuehren. Dabei oeffnet sich ein Browser-Fenster:

1. Melde dich mit **m.vonburg94@gmail.com** an
2. Google warnt: "Diese App wurde nicht von Google verifiziert"
   → Klicke **"Erweitert"** → **"Zu Alpine Career Bot (unsicher)"**
3. Du siehst: "Alpine Career Bot moechte Zugriff auf: Gmail-Nachrichten senden"
   → Klicke **"Zulassen"**
4. Fertig! Das Fenster kann geschlossen werden.

---

## Was passiert danach?

- Der Bot kann jetzt E-Mails ueber dein Gmail-Konto senden
- Er kann **nur senden**, nicht lesen — das ist alles, was er darf
- Du musst im Bot trotzdem jedes Mal mit `/senden` bestaetigen
- Keine Bewerbung wird ohne deine explizite Freigabe verschickt

---

## Fragen?

Schreib Dave oder nutze den Bot mit `/hilfe`.
