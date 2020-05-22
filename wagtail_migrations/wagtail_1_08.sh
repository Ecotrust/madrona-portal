#!/bin/bash

PROJ=/usr/local/apps/ocean_portal
ENV=$PROJ/wag_env;
PIP=$ENV/bin/pip;
PYTHON=$ENV/bin/python3;
DJ=$PROJ/marco/manage.py;

# 1_08
$PIP uninstall wagtail -y
$PIP uninstall django -y
$PIP install "django==1.10.8"
$PIP install "wagtail==1.8.2"

cp $PROJ/wagtail_migrations/libgeos_1_10.py $ENV/lib/python3.6/site-packages/django/contrib/gis/geos/libgeos.py
# cp $PROJ/wagtail_migrations/0002_portalimage_collection.py $PROJ/marco/portal/base/migrations/
# $PYTHON $DJ migrate base 0002
