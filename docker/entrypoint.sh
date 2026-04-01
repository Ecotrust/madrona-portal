#!/bin/sh
# Madrona Portal — Docker entrypoint
# Waits for the database, runs migrations, seeds a fresh DB, then starts the server.

set -e

# ---------------------------------------------------------------------------
# 1. Wait for the database to accept connections
# ---------------------------------------------------------------------------
python - <<'PY'
import os, socket, time, sys

# Accept both DB_HOST (preferred) and legacy SQL_HOST
host = os.environ.get("DB_HOST") or os.environ.get("SQL_HOST", "db")
port = int(os.environ.get("DB_PORT") or os.environ.get("SQL_PORT", "5432"))
timeout = int(os.environ.get("DB_WAIT_TIMEOUT", "90"))

print(f"Waiting for database at {host}:{port} (timeout {timeout}s)...", flush=True)
start = time.time()
while True:
    try:
        with socket.create_connection((host, port), timeout=2):
            break
    except OSError:
        if time.time() - start > timeout:
            sys.exit(f"Timed out waiting for database at {host}:{port}")
        time.sleep(1)

print("Database is up.", flush=True)
PY

# ---------------------------------------------------------------------------
# 2. Migrate and collect static files
# ---------------------------------------------------------------------------
python marco/manage.py migrate --noinput
python marco/manage.py collectstatic --noinput
python marco/manage.py compress --force

# ---------------------------------------------------------------------------
# 3. Seed a fresh database with initial fixture data
#
# A brand-new PostGIS install contains exactly one Wagtail Page row (the
# Wagtail root page, depth=1).  We count pages at depth > 1 — if none exist,
# this is a fresh database and we load the initial fixture.
#
# IMPORTANT: We never wipe content on an existing database.  That would
# destroy real data.  Set FORCE_RELOAD_FIXTURES=1 only in CI or dev reset
# scenarios where wiping the database is intentional.
# ---------------------------------------------------------------------------
CONTENT_PAGES=$(python - 2>/dev/null <<'PY' || echo "unknown"
import sys, os
sys.path.insert(0, 'marco')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marco.settings')
import django
django.setup()
from wagtail.models import Page
print(Page.objects.filter(depth__gt=1).count())
PY
)

echo "Content pages in database: ${CONTENT_PAGES}"

if [ "${CONTENT_PAGES:-0}" -lt "5" ] || [ "${FORCE_RELOAD_FIXTURES:-0}" = "1" ]; then
    echo "Fresh database detected — loading initial fixtures..."

    # Clear rows created by migrations that would conflict with fixture data.
    python - <<'PY'
import sys, os
sys.path.insert(0, 'marco')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marco.settings')
import django
django.setup()

# The sites migration creates a default site and initial_data migration
# creates placeholder pages — both conflict with fixture data.
from django.contrib.sites.models import Site
Site.objects.all().delete()

from wagtail.models import Page
Page.objects.filter(depth__gt=1).delete()

try:
    from portal.base.models import PortalRendition
    PortalRendition.objects.all().delete()
except Exception:
    pass
PY

    python marco/manage.py loaddata initial_data_prod.json
    # Load per-app reference fixtures that aren't included in the main fixture.
    # Use absolute paths so only this specific file is loaded (not other apps'
    # initial_data.json files that happen to share the same name).
    python marco/manage.py loaddata \
        apps/madrona-scenarios/scenarios/fixtures/initial_data.json
    echo "Initial fixtures loaded."
else
    echo "Existing database — skipping fixture load."
fi

# ---------------------------------------------------------------------------
# 4. Create superuser (only when DJANGO_SUPERUSER_PASSWORD is set and the
#    username does not already exist — safe to run on every restart)
# ---------------------------------------------------------------------------
if [ -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]; then
    python - <<PY
import os, sys
sys.path.insert(0, 'marco')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marco.settings')
import django
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email    = os.environ.get('DJANGO_SUPERUSER_EMAIL',    'admin@example.com')
password = os.environ['DJANGO_SUPERUSER_PASSWORD']
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f'Superuser "{username}" created.', flush=True)
else:
    print(f'Superuser "{username}" already exists — skipping.', flush=True)
PY
fi

# ---------------------------------------------------------------------------
# 5. Start the application server
#
# DEBUG=True  → Django's runserver (auto-reload, no gunicorn needed)
# DEBUG=False → gunicorn (multi-worker, production-safe)
#
# Override with DJANGO_ENV=production to force gunicorn regardless of DEBUG.
# ---------------------------------------------------------------------------
DJANGO_DEBUG=$(python - <<'PY'
import sys, os
sys.path.insert(0, 'marco')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marco.settings')
import django
django.setup()
from django.conf import settings
print("true" if settings.DEBUG else "false")
PY
)

if [ "${DJANGO_ENV:-}" = "production" ] || [ "${DJANGO_DEBUG}" = "false" ]; then
    echo "Starting gunicorn (production mode)..."
    exec gunicorn marco.wsgi:application \
        --bind 0.0.0.0:8000 \
        --workers "${GUNICORN_WORKERS:-3}" \
        --timeout "${GUNICORN_TIMEOUT:-120}" \
        --chdir marco \
        --access-logfile - \
        --error-logfile -
else
    echo "Starting Django development server..."
    exec python marco/manage.py runserver 0.0.0.0:8000
fi
