#!/bin/sh

# Exit on errors
set -e

# Wait for the database service before running migrations.
python - <<'PY'
import os
import socket
import time

host = os.environ.get("SQL_HOST", "db")
port = int(os.environ.get("DB_INTERNAL_PORT", "5432"))
timeout_seconds = int(os.environ.get("DB_WAIT_TIMEOUT", "90"))

start = time.time()
while True:
	try:
		with socket.create_connection((host, port), timeout=2):
			break
	except OSError:
		if time.time() - start > timeout_seconds:
			raise SystemExit(f"Timed out waiting for database at {host}:{port}")
		time.sleep(1)
PY

# if [ -n "$SQL_HOST" ]; then
# 	echo "Waiting for database at ${SQL_HOST}:${DB_INTERNAL_PORT:-5432}..."
# 	# pg_isready is available after installing postgresql-client in the image
# 	until pg_isready -h "$SQL_HOST" -p "${DB_INTERNAL_PORT:-5432}" >/dev/null 2>&1; do
# 		echo "Postgres is unavailable - sleeping"
# 		sleep 1
# 	done
# 	echo "Postgres is up"
# fi

python marco/manage.py collectstatic --noinput
python marco/manage.py migrate --noinput

# On a fresh database (no real Wagtail content pages yet), load the initial
# fixture data so the site starts with working navigation and content.
# The check is skipped safely if Django fails to import for any reason.
PAGE_COUNT=$(python - 2>/dev/null <<'PY' || echo "unknown"
import sys, os
sys.path.insert(0, 'marco')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marco.settings')
import django
django.setup()
from wagtail.models import Page
print(Page.objects.filter(depth__gt=1).count())
PY
)
if [ "$PAGE_COUNT" = "0" ]; then
    echo "Fresh database — loading initial fixtures..."
    python marco/manage.py loaddata wcoa_init wcoa_init_layers wagtail_menus
    echo "Initial fixtures loaded."
fi

python marco/manage.py runserver 0:8000
#uwsgi --socket :8000 --master --enable-threads --module marco.marco.wsgi
#exec "$@"
