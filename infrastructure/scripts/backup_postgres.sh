#!/bin/bash
# =============================================================================
# PostgreSQL Backup Script — Alpine Career
# =============================================================================
# Erstellt taeglich einen pg_dump, rotiert nach 7 Tagen.
#
# Einrichtung auf Hetzner:
#   1. chmod +x /opt/alpine-career/infrastructure/scripts/backup_postgres.sh
#   2. crontab -e
#   3. 0 3 * * * /opt/alpine-career/infrastructure/scripts/backup_postgres.sh
#
# Das Script laeuft um 03:00 UTC (04:00 CET).
# =============================================================================

set -euo pipefail

# Konfiguration
BACKUP_DIR="/opt/alpine-career/backups"
CONTAINER_NAME="alpine-career-postgres"
DB_NAME="alpine_career"
DB_USER="alpine_career"
RETENTION_DAYS=7
DATE=$(date +%Y-%m-%d_%H-%M)
BACKUP_FILE="${BACKUP_DIR}/alpine_career_${DATE}.sql.gz"

# Backup-Verzeichnis erstellen
mkdir -p "${BACKUP_DIR}"

# pg_dump im Container ausfuehren und komprimieren
docker exec "${CONTAINER_NAME}" \
    pg_dump -U "${DB_USER}" "${DB_NAME}" \
    | gzip > "${BACKUP_FILE}"

# Groesse pruefen
BACKUP_SIZE=$(du -h "${BACKUP_FILE}" | cut -f1)
echo "[$(date -Iseconds)] Backup erstellt: ${BACKUP_FILE} (${BACKUP_SIZE})"

# Alte Backups loeschen (aelter als RETENTION_DAYS Tage)
find "${BACKUP_DIR}" -name "alpine_career_*.sql.gz" -mtime +${RETENTION_DAYS} -delete
REMAINING=$(ls -1 "${BACKUP_DIR}"/alpine_career_*.sql.gz 2>/dev/null | wc -l)
echo "[$(date -Iseconds)] Backups vorhanden: ${REMAINING} (Rotation: ${RETENTION_DAYS} Tage)"
