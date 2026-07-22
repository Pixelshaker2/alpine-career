# Gmail Setup — Anleitung fuer Marco

Hallo Marco, damit der Bot Bewerbungen ueber dein Gmail versenden kann, musst du einmalig einen Zugang einrichten. Dauert ca. 10 Minuten.

---

## Schritt 1: Google Cloud Console oeffnen

1. Oeffne https://console.cloud.google.com
2. Melde dich mit m.vonburg94@gmail.com an
3. Oben in der Leiste auf das Projekt-Dropdown klicken → "Neues Projekt"
4. Projektname: Alpine Career Bot
5. Auf "Erstellen" klicken
6. Warten bis erstellt, dann oben auf das Projekt wechseln

---

## Schritt 2: Gmail API aktivieren

1. Links oben auf das Hamburger-Menu (die drei Striche ≡)
2. "APIs & Dienste" → "Bibliothek"
3. In der Suche "Gmail API" eintippen
4. Auf "Gmail API" klicken
5. Den blauen Button "Aktivieren" klicken

---

## Schritt 3: App einrichten (Branding)

1. Links oben auf das Hamburger-Menu (≡)
2. "Google Auth Platform" suchen und aufklappen
3. Auf "Branding" klicken
4. Ausfuellen:
   - App-Name: Alpine Career Bot
   - Support-E-Mail: m.vonburg94@gmail.com
   - Kontakt-E-Mail Entwickler: m.vonburg94@gmail.com
5. Speichern

---

## Schritt 4: Testnutzer hinzufuegen (Audience)

1. Im gleichen Menu "Google Auth Platform" auf "Audience" (oder "Zielgruppe") klicken
2. Typ auf "External" setzen (falls gefragt)
3. Bei "Test users" auf "Add user" klicken
4. E-Mail eingeben: m.vonburg94@gmail.com
5. Hinzufuegen und speichern

---

## Schritt 5: Zugangsdaten erstellen (Clients)

1. Im Menu "Google Auth Platform" auf "Clients" klicken
2. Auf "Create OAuth client" klicken (oder "+ Erstellen")
3. Anwendungstyp: Desktop app (oder Desktopanwendung)
4. Name: Alpine Career CLI
5. Auf "Erstellen" klicken
6. Es erscheint ein Dialog — dort auf "JSON herunterladen" klicken
7. Die Datei speichern (heisst z.B. client_secret_xxx.json)

---

## Schritt 6: Datei an Dave schicken

Schick die heruntergeladene JSON-Datei an Dave per Telegram oder WhatsApp.

Keine Sorge: Die Datei enthaelt keine Passwoerter. Sie ist nur die "Visitenkarte" der App. Im naechsten Schritt wirst du nochmal gefragt, ob du dem Bot Zugriff erlauben willst.

---

## Schritt 7: Zugriff erlauben (macht Dave mit dir zusammen)

Dave fuehrt ein Script aus. Dabei oeffnet sich ein Browser-Fenster:

1. Mit m.vonburg94@gmail.com anmelden
2. Google warnt: "Diese App wurde nicht von Google verifiziert"
   → Auf "Erweitert" klicken → "Zu Alpine Career Bot (unsicher)"
3. "Alpine Career Bot moechte Zugriff auf: Gmail-Nachrichten senden"
   → Auf "Zulassen" klicken
4. Fertig! Fenster schliessen.

---

## Was das bedeutet

- Der Bot kann NUR E-Mails senden, nicht lesen
- Du musst im Bot jedes Mal mit /senden bestaetigen
- Keine Bewerbung wird ohne deine Freigabe verschickt
- Du kannst den Zugriff jederzeit unter https://myaccount.google.com/permissions widerrufen
