#!/bin/sh

#set -e
python marco/manage.py collectstatic --noinput
python marco/manage.py migrate --noinput

uwsgi --socket :8000 --master --enable-threads --module marco.wsgi
#exec "$@"
