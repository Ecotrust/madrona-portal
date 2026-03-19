#!/bin/sh

# Exit on errors
set -e

# If a SQL_HOST is provided, wait for Postgres to become available before running
# migrations. This prevents race conditions when using docker-compose where the
# web container starts before the DB is ready.
if [ -n "$SQL_HOST" ]; then
	echo "Waiting for database at ${SQL_HOST}:${SQL_PORT:-5432}..."
	# pg_isready is available after installing postgresql-client in the image
	until pg_isready -h "$SQL_HOST" -p "${SQL_PORT:-5432}" >/dev/null 2>&1; do
		echo "Postgres is unavailable - sleeping"
		sleep 1
	done
	echo "Postgres is up"
fi


echo "Collecting static files..."
python manage.py collectstatic --noinput
echo "Applying database migrations..."
python manage.py migrate --noinput

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
