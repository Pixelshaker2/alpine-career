#!/usr/bin/env python3
"""Gmail OAuth2 — lokales Autorisierungs-Script.

Dieses Script wird EINMALIG LOKAL ausgefuehrt, um den OAuth2-Token
fuer Marcos Gmail-Account (m.vonburg94@gmail.com) zu generieren.

Ablauf:
1. Google Cloud Console → Credentials → OAuth2 Client ID (Desktop App)
2. credentials.json herunterladen und hier ablegen
3. Dieses Script ausfuehren:
   python scripts/gmail_auth.py --credentials path/to/credentials.json
4. Browser oeffnet sich → mit m.vonburg94@gmail.com anmelden
5. gmail_token.pickle wird erstellt
6. Token auf den Server kopieren:
   scp gmail_token.pickle root@46.224.126.55:/tmp/
   ssh root@46.224.126.55
   docker cp /tmp/gmail_token.pickle alpine-career-app:/app/data/gmail_token.pickle
   rm /tmp/gmail_token.pickle

WICHTIG: credentials.json und gmail_token.pickle NIEMALS committen!
"""

import argparse
import pickle
import sys
from pathlib import Path

# Minimale Dependencies — nur google-auth-oauthlib noetig
try:
    from google_auth_oauthlib.flow import InstalledAppFlow
except ImportError:
    print("Fehler: google-auth-oauthlib nicht installiert.")
    print("  pip install google-auth-oauthlib")
    sys.exit(1)


SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
DEFAULT_OUTPUT = Path("gmail_token.pickle")


def main() -> None:
    """Run OAuth2 authorization flow and save token."""
    parser = argparse.ArgumentParser(
        description="Gmail OAuth2 Token generieren"
    )
    parser.add_argument(
        "--credentials",
        type=Path,
        required=True,
        help="Pfad zur credentials.json von Google Cloud Console",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Ausgabedatei fuer den Token (default: {DEFAULT_OUTPUT})",
    )
    args = parser.parse_args()

    if not args.credentials.exists():
        print(f"Fehler: {args.credentials} nicht gefunden.")
        sys.exit(1)

    print(f"Starte OAuth2-Flow mit {args.credentials}")
    print("Ein Browser-Fenster wird sich oeffnen...")
    print("Bitte mit m.vonburg94@gmail.com anmelden und Zugriff erlauben.\n")

    flow = InstalledAppFlow.from_client_secrets_file(
        str(args.credentials),
        SCOPES,
    )
    creds = flow.run_local_server(port=0)

    # Token speichern
    with open(args.output, "wb") as f:
        pickle.dump(creds, f)

    print(f"\nToken gespeichert: {args.output}")
    print(f"Token ist gueltig bis: {creds.expiry}")
    print(f"Refresh Token vorhanden: {bool(creds.refresh_token)}")
    print()
    print("Naechster Schritt — Token auf den Server kopieren:")
    print(f"  scp {args.output} root@46.224.126.55:/tmp/")
    print(f"  ssh root@46.224.126.55")
    print(f"  docker cp /tmp/gmail_token.pickle alpine-career-app:/app/data/gmail_token.pickle")
    print(f"  rm /tmp/gmail_token.pickle")


if __name__ == "__main__":
    main()
