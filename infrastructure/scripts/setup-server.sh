#!/bin/bash
# Alpine Career — Ersteinrichtung Hetzner VPS (Ubuntu 22.04)
# Nutzung: ssh root@SERVER < setup-server.sh

set -euo pipefail

echo "=== Hetzner VPS Setup ==="

# System aktualisieren
apt-get update && apt-get upgrade -y

# Docker installieren
curl -fsSL https://get.docker.com | sh
systemctl enable docker
systemctl start docker

# Docker Compose Plugin (in Docker enthalten seit 2023)
docker compose version

# Verzeichnis anlegen
mkdir -p /opt/alpine-career/data

# Firewall (UFW)
apt-get install -y ufw
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw --force enable

# Swap (4 GB fuer CX22 mit 4 GB RAM)
if [ ! -f /swapfile ]; then
    fallocate -l 4G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi

# Automatische Updates
apt-get install -y unattended-upgrades
dpkg-reconfigure -plow unattended-upgrades

echo ""
echo "=== Setup abgeschlossen ==="
echo "Naechste Schritte:"
echo "  1. .env Datei nach /opt/alpine-career/.env kopieren"
echo "  2. SSH-Key fuer GitHub hinterlegen"
echo "  3. ./deploy.sh [SERVER-IP] ausfuehren"
