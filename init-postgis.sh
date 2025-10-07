#!/bin/bash
set -euo pipefail

# This script runs in a lightweight init container to restore a PostGIS database
# from a local backup file mounted at /backup. It waits for the main db service,
# ensures PostGIS extension, then restores using pg_restore (archive) or psql (plain SQL).

BACKUP_FILE=${BACKUP_FILE:-/backup/wastd_prod.pgdump}
DB_HOST=${DB_HOST:-db}
DB_PORT=${DB_PORT:-5432}
DB_NAME=${POSTGRES_DB:-wastd}
DB_USER=${POSTGRES_USER:-postgres}
DB_PASSWORD=${POSTGRES_PASSWORD:-postgres}

echo "[postgis-init] backup file: $BACKUP_FILE"
if [[ ! -f "$BACKUP_FILE" ]]; then
  echo "[postgis-init] WARNING: backup file not found, skipping restore." >&2
  exit 0
fi

echo "[postgis-init] waiting for db $DB_HOST:$DB_PORT ..."
until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" >/dev/null 2>&1; do sleep 1; done

export PGPASSWORD="$DB_PASSWORD"
echo "[postgis-init] ensuring PostGIS extension..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -v ON_ERROR_STOP=1 -c "CREATE EXTENSION IF NOT EXISTS postgis;" >/dev/null

echo "[postgis-init] detecting backup format..."
if pg_restore -l "$BACKUP_FILE" >/dev/null 2>&1; then
  echo "[postgis-init] restoring archive with pg_restore"
  pg_restore -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -O -x -v "$BACKUP_FILE"
else
  echo "[postgis-init] restoring plain SQL with psql"
  psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -v ON_ERROR_STOP=1 -f "$BACKUP_FILE"
fi

echo "[postgis-init] restore done."


