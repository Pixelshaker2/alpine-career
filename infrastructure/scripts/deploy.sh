#!/bin/bash
# Alpine Career — Deploy-Script fuer Hetzner VPS
# Nutzung: ./deploy.sh [server-ip]
#
# Voraussetzungen auf dem Server:
#   - Docker + Docker Compose installiert
#   - SSH-Key hinterlegt
#   - .env Datei auf dem Server unter /opt/alpine-career/.env

set -euo pipefail

SERVER="${1:?Bitte Server-IP angeben: ./deploy.sh 1.2.3.4}"
DEPLOY_DIR="/opt/alpine-career"
REPO_URL="git@github.com:GITHUB_USER/alpine-career.git"

echo "=== Alpine Career Deploy ==="
echo "Server: $SERVER"
echo "Verzeichnis: $DEPLOY_DIR"
echo ""

ssh "root@$SERVER" bash <<EOF
set -euo pipefail

# Repo klonen oder aktualisieren
if [ -d "$DEPLOY_DIR" ]; then
    echo ">> Repository aktualisieren..."
    cd $DEPLOY_DIR
    git pull origin main
else
    echo ">> Repository klonen..."
    git clone $REPO_URL $DEPLOY_DIR
    cd $DEPLOY_DIR
fi

# .env pruefen
if [ ! -f .env ]; then
    echo "FEHLER: .env Datei fehlt unter $DEPLOY_DIR/.env"
    echo "Kopiere .env.example nach .env und trage die Werte ein."
    exit 1
fi

# Docker Compose starten
echo ">> Container bauen und starten..."
docker compose down --remove-orphans 2>/dev/null || true
docker compose build --no-cache
docker compose up -d

# Migrationen ausfuehren
echo ">> Datenbank-Migrationen..."
docker compose exec -T app python -m alembic upgrade head

echo ""
echo "=== Deploy abgeschlossen ==="
docker compose ps
EOF
