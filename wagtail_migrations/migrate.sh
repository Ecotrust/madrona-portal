#!/bin/bash

while getopts i: flag
do
  case "${flag}" in
    i) infile=${OPTARG};;
  esac
done

PROJ=/usr/local/apps/ocean_portal
ENV=$PROJ/wag_env;
PIP=$ENV/bin/pip;
PYTHON=$ENV/bin/python3;
DJ='$PYTHON $PROJ/marco/manage.py';

echo "Input SQL file: $infile";

# Prep and load the DB
sudo -u postgres dropdb ocean_portal;
sudo -u postgres createdb -O postgres ocean_portal;
sudo -u postgres psql -c "CREATE EXTENSION postgis; CREATE EXTENSION postgis_topology;" ocean_portal;
sudo -u postgres psql ocean_portal < $infile;

# Install requirements to standalone virtualenv
python3 -m virtualenv $ENV;
$PIP install -r $PROJ/wagtail_migrations/requirements_wagtail_1.3.1.txt
cp $PROJ/wagtail_migrations/libgeos_1_9.py $ENV/lib/python3.6/site-packages/django/contrib/gis/geos/libgeos.py
$DJ migrate wagtail
