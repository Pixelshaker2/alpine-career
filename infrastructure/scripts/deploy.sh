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
REPO_URL="https://github.com/Pixelshaker2/alpine-career.git"

echo "=== Alpine Career Deploy ==="
echo "Server: $SERVER"
echo "Verzeichnis: $DEPLOY_DIR"
echo ""

ssh "root@$SERVER" bash <<EOF
set -euo pipefail

# Repo klonen oder aktualisieren
if [ -d "$DEPLOY_DIR/.git" ]; then
    echo ">> Repository aktualisieren..."
    cd $DEPLOY_DIR
    git pull origin main
else
    echo ">> Repository klonen..."
    # .env sichern falls vorhanden
    if [ -f "$DEPLOY_DIR/.env" ]; then
        cp $DEPLOY_DIR/.env /tmp/.env.deploy.bak
    fi
    rm -rf $DEPLOY_DIR
    git clone $REPO_URL $DEPLOY_DIR
    cd $DEPLOY_DIR
    # .env wiederherstellen
    if [ -f /tmp/.env.deploy.bak ]; then
        mv /tmp/.env.deploy.bak $DEPLOY_DIR/.env
    fi
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
