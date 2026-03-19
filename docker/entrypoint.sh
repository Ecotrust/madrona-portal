#!/bin/sh

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
