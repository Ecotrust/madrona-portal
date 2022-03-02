#!/bin/sh

#set -e
python marco/manage.py collectstatic --noinput
python marco/manage.py migrate --noinput

python marco/manage.py runserver 0:8000
#uwsgi --socket :8000 --master --enable-threads --module marco.marco.wsgi
#exec "$@"
