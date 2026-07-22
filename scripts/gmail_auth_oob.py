#!/usr/bin/env python3
"""Gmail OAuth2 — OOB-Flow fuer Remote-Autorisierung.

Generiert einen Auth-Link den Marco oeffnet.
Marco bekommt einen Code, den Dave hier eingibt.
Token wird als gmail_token.pickle gespeichert.
"""

import pickle
import sys
from pathlib import Path

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import Flow
except ImportError:
    print("Fehler: google-auth-oauthlib nicht installiert.")
    print("  pip install google-auth-oauthlib")
    sys.exit(1)


SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
CREDENTIALS_FILE = Path("credentials.json")
OUTPUT_FILE = Path("gmail_token.pickle")


def main() -> None:
    """Run OOB OAuth2 flow for remote authorization."""
    if not CREDENTIALS_FILE.exists():
        print(f"Fehler: {CREDENTIALS_FILE} nicht gefunden.")
        print("Bitte credentials.json ins aktuelle Verzeichnis legen.")
        sys.exit(1)

    flow = Flow.from_client_secrets_file(
        str(CREDENTIALS_FILE),
        scopes=SCOPES,
        redirect_uri="urn:ietf:wg:oauth:2.0:oob",
    )

    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )

    print("\n" + "=" * 60)
    print("DIESEN LINK AN MARCO SCHICKEN:")
    print("=" * 60)
    print(auth_url)
    print("=" * 60)
    print("\nMarco oeffnet den Link, meldet sich an,")
    print("klickt 'Erweitert' → 'Zu Alpine Career Bot' → 'Zulassen'")
    print("und schickt dir den Code.\n")

    code = input("Code von Marco eingeben: ").strip()

    if not code:
        print("Kein Code eingegeben. Abbruch.")
        sys.exit(1)

    flow.fetch_token(code=code)
    creds = flow.credentials

    with open(OUTPUT_FILE, "wb") as f:
        pickle.dump(creds, f)

    print(f"\nToken gespeichert: {OUTPUT_FILE}")
    print(f"Refresh Token vorhanden: {bool(creds.refresh_token)}")
    print()
    print("Naechste Schritte:")
    print(f"  scp {OUTPUT_FILE} root@46.224.126.55:/tmp/")
    print("  ssh root@46.224.126.55")
    print("  docker cp /tmp/gmail_token.pickle alpine-career-app:/app/data/gmail_token.pickle")
    print("  rm /tmp/gmail_token.pickle")


if __name__ == "__main__":
    main()
