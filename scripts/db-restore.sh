#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# db-restore.sh — Restore a PostgreSQL dump into the Dockerized dev database.
#
# Usage:
#   ./scripts/db-restore.sh <dump.sql>
#   ./scripts/db-restore.sh --drop <dump.sql>          # drop & recreate DB first
#   ./scripts/db-restore.sh --env-file <path> <dump.sql>
#
# Run from anywhere — this script always operates relative to madrona-portal/.
#
# Prerequisites:
#   1. Docker Compose stack is running from madrona-portal/docker:
#        docker compose up
#   2. madrona-portal/docker/.env exists and contains DB_NAME, DB_USER, DB_PASSWORD.
#
# Options:
#   --drop              Terminate all active connections, drop, and recreate the
#                       target database before restoring. Required for a clean
#                       import from prod. Without this flag the dump is applied
#                       on top of existing data.
#   --env-file <path>   Path to the .env file (default: ./docker/.env).
#
# Notes:
#   - The dump is streamed directly into the container — no temp files on disk.
#   - psql warnings (e.g. "already exists") are normal when importing a dump
#     produced on a different Postgres version (12 → 16) and are not fatal.
#   - After a --drop restore, run migrations to pick up any schema drift:
#       docker compose exec app python marco/manage.py migrate
# -----------------------------------------------------------------------------
set -euo pipefail

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
die()  { echo "[db-restore] ERROR: $*" >&2; exit 1; }
info() { echo "[db-restore] $*"; }

# ---------------------------------------------------------------------------
# Parse arguments
# ---------------------------------------------------------------------------
DROP_FIRST=false
DUMP_FILE=""
ENV_FILE="$(dirname "${BASH_SOURCE[0]}")/../docker/.env"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --drop)     DROP_FIRST=true; shift ;;
    --env-file) [[ -n "${2:-}" ]] || die "--env-file requires a path argument"
                ENV_FILE="$2"; shift 2 ;;
    -*)         die "Unknown option: '$1'. Usage: $0 [--drop] [--env-file <path>] <dump.sql>" ;;
    *)          [[ -z "$DUMP_FILE" ]] || die "Unexpected argument: '$1'"
                DUMP_FILE="$1"; shift ;;
  esac
done

[[ -n "$DUMP_FILE" ]] || die "Usage: $0 [--drop] [--env-file <path>] <dump.sql>"

# Resolve dump path before we cd away.
DUMP_ABS="$(cd "$(dirname "$DUMP_FILE")" && pwd)/$(basename "$DUMP_FILE")"
[[ -f "$DUMP_ABS" ]] || die "Dump file not found: $DUMP_FILE"

# Resolve ENV_FILE to an absolute path before we cd away.
ENV_FILE_ABS="$(cd "$(dirname "$ENV_FILE")" && pwd)/$(basename "$ENV_FILE")"
[[ -f "$ENV_FILE_ABS" ]] || die "Env file not found: $ENV_FILE"

# ---------------------------------------------------------------------------
# Always operate from madrona-portal/ regardless of where the script is called
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

# ---------------------------------------------------------------------------
# Load .env for DB credentials
# ---------------------------------------------------------------------------
set -a
# shellcheck source=/dev/null
source "$ENV_FILE_ABS"
set +a

DB_NAME="${DB_NAME:-wcoa_docker_db}"
DB_USER="${DB_USER:-postgres}"
DB_PASSWORD="${DB_PASSWORD:?DB_PASSWORD must be set in .env}"

COMPOSE="docker compose -f docker/docker-compose.yml --env-file $ENV_FILE_ABS"
PSQL="$COMPOSE exec -T -e PGPASSWORD=$DB_PASSWORD db psql -U $DB_USER"

# ---------------------------------------------------------------------------
# Verify the db container is healthy before doing anything
# ---------------------------------------------------------------------------
info "Checking db service health..."
$COMPOSE ps db | grep -q "healthy" \
  || die "db container is not healthy. Is the stack running? Try: $COMPOSE up -d"

# ---------------------------------------------------------------------------
# Optional: terminate connections, drop, and recreate the database
# ---------------------------------------------------------------------------
if [[ "$DROP_FIRST" == true ]]; then
  info "Terminating active connections to '$DB_NAME'..."
  $PSQL -d postgres -c \
    "SELECT pg_terminate_backend(pid)
     FROM pg_stat_activity
     WHERE datname = '$DB_NAME' AND pid <> pg_backend_pid();" \
    > /dev/null

  info "Dropping database '$DB_NAME'..."
  $PSQL -d postgres -c "DROP DATABASE IF EXISTS \"$DB_NAME\";"

  info "Creating database '$DB_NAME'..."
  $PSQL -d postgres -c "CREATE DATABASE \"$DB_NAME\";"

  info "Enabling PostGIS extension..."
  $PSQL -d "$DB_NAME" -c "CREATE EXTENSION IF NOT EXISTS postgis;"
fi

# ---------------------------------------------------------------------------
# Stream the dump into the database
# ---------------------------------------------------------------------------
DUMP_SIZE="$(du -sh "$DUMP_ABS" | cut -f1)"
info "Restoring '$DUMP_FILE' (${DUMP_SIZE}) → '$DB_NAME'..."
info "psql warnings about existing objects are expected and non-fatal."

$PSQL -d "$DB_NAME" \
  --set ON_ERROR_STOP=off \
  < "$DUMP_ABS"

info "Restore complete."
info ""
info "Next steps:"
info "  Apply any pending migrations:"
info "    docker compose exec app python marco/manage.py migrate"
