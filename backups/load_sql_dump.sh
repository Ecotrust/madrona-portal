#!/bin/bash
# Import a PostgreSQL SQL dump into the running Docker database service.
#
# Usage (run from madrona-portal/):
#   ./backups/load_sql_dump.sh /path/to/your_dump.sql
#
# The db container must already be running:
#   docker compose --env-file docker/.env.dev -f docker/docker-compose.yml up -d db

set -euo pipefail

DUMP_FILE="${1:-}"

if [ -z "$DUMP_FILE" ] || [ ! -f "$DUMP_FILE" ]; then
    echo "Usage: $0 <path-to-sql-dump>"
    echo "  Example: $0 ~/wcoa_prod.sql"
    exit 1
fi

# Load credentials from the Docker env file (same directory as docker-compose.yml)
set -a
# shellcheck source=/dev/null
source "$(dirname "$0")/../docker/.env.dev"
set +a

echo "Importing $(basename "$DUMP_FILE") into database '$SQL_DATABASE' ..."

docker compose --env-file docker/.env.dev -f docker/docker-compose.yml exec -T db \
    psql -U "$SQL_USER" -d "$SQL_DATABASE" < "$DUMP_FILE"

echo ""
echo "Import complete."
echo ""
echo "Next: restart the app to run Django migrations on top of the imported data:"
echo "  docker compose --env-file docker/.env.dev -f docker/docker-compose.yml restart app"
