#!/bin/sh
# Madrona Portal — Docker entrypoint
# Waits for the database, then starts the application server.
#
# By default steps 1 (DB wait), 2 (collectstatic + compress), and 6 (server start) run. Set DB_INIT=1 to also run steps 3-5 (migrate, fixtures, superuser).
# This is intentionally opt-in to protect existing databases.

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
# 2. Collect static files and compress assets (always runs)
# ---------------------------------------------------------------------------
# Ensure the bind-mounted static dir is writable by madrona_user regardless of how Docker created it on the host (often root:root on Linux).
chown madrona_user:madrona_user /vol/web/static 2>/dev/null || true

echo "Collecting static files..."
gosu madrona_user python marco/manage.py collectstatic --noinput
echo "Compressing assets..."
gosu madrona_user python marco/manage.py compress --force

# ---------------------------------------------------------------------------
# 3-5. Database initialisation (opt-in via DB_INIT=1)
# ---------------------------------------------------------------------------
if [ "${DB_INIT:-0}" != "1" ]; then
    echo "DB_INIT not set — skipping migrations, fixtures, and superuser creation."
else

# ---------------------------------------------------------------------------
# 3. Migrate
# ---------------------------------------------------------------------------
python marco/manage.py migrate --noinput

# ---------------------------------------------------------------------------
# 4. Seed a fresh database with initial fixture data
#
# A brand-new PostGIS install contains exactly one Wagtail Page row (the Wagtail root page, depth=1).  We count pages at depth > 1 — if none exist, this is a fresh database and we load the initial fixture.
#
# IMPORTANT: Be careful not to wipe content on an existing database. Set FORCE_RELOAD_FIXTURES=1 only in CI or dev reset scenarios where wiping the database is intentional.
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

    # Load fixtures in a single Python process so ContentTypes created here are guaranteed to be visible when loaddata deserializes FK natural keys.
    python - <<'PY'
import sys, os
sys.path.insert(0, 'marco')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marco.settings')
import django
django.setup()

# Step 1: ensure every installed app's ContentTypes exist before loading fixture data.  create_contenttypes is idempotent.
from django.apps import apps as django_apps
from django.contrib.contenttypes.management import create_contenttypes
from django.contrib.contenttypes.models import ContentType

for app_config in django_apps.get_app_configs():
    create_contenttypes(app_config, verbosity=0)

print('ContentTypes synchronized for all installed apps.', flush=True)

# Step 2: load fixtures — same process, same DB session.
from django.core.management import call_command
call_command(
    'loaddata',
    'apps/madrona-scenarios/scenarios/fixtures/initial_data.json',
    verbosity=1,
)
PY
    echo "Initial fixtures loaded."
else
    echo "Existing database — skipping fixture load."
fi

# ---------------------------------------------------------------------------
# 5. Create superuser (only when DJANGO_SUPERUSER_PASSWORD is set and the
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

fi  # end DB_INIT block

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
    exec gosu madrona_user gunicorn marco.wsgi:application \
        --bind 0.0.0.0:8008 \
        --workers "${GUNICORN_WORKERS:-3}" \
        --timeout "${GUNICORN_TIMEOUT:-120}" \
        --chdir marco \
        --access-logfile - \
        --error-logfile -
else
    echo "Starting Django development server..."
    exec gosu madrona_user python marco/manage.py runserver 0.0.0.0:8000
fi
