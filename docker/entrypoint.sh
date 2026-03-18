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

python marco/manage.py runserver 0:8000
#uwsgi --socket :8000 --master --enable-threads --module marco.marco.wsgi
#exec "$@"
