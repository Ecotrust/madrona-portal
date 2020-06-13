#!/bin/bash

while getopts i: flag
do
  case "${flag}" in
    i) infile=${OPTARG};;
  esac
done

PROJ=/usr/local/apps/ocean_portal;
ENV=$PROJ/wag_env;
PIP=$ENV/bin/pip;
PYTHON=$ENV/bin/python3;
DJ=$PROJ/marco/manage.py;
MIGRATE=$PROJ/wagtail_migrations/migrate_wagtail_version.sh;

if [[ ! -f $infile ]] ; then
  echo 'File "$infile" DOES NOT EXIST. Please provide a valid input file with the "-i" flag';
  exit;
fi

echo "Input SQL file: $infile";

# Prep and load the DB
sudo -u postgres dropdb ocean_portal;
sudo -u postgres createdb -O postgres ocean_portal;
sudo -u postgres psql -c "CREATE EXTENSION postgis; CREATE EXTENSION postgis_topology;" ocean_portal;
sudo -u postgres psql ocean_portal < $infile;

# Install requirements to standalone virtualenv
sudo rm -r $ENV
python3 -m virtualenv $ENV;
$PIP install -r $PROJ/wagtail_migrations/requirements_wagtail_1.3.1.txt
cp $PROJ/wagtail_migrations/libgeos_1_9.py $ENV/lib/python3.6/site-packages/django/contrib/gis/geos/libgeos.py
cp $PROJ/wagtail_migrations/wagtailimportexport/wagtail_hooks_py2.py $ENV/lib/python3.6/site-packages/wagtailimportexport/wagtail_hooks.py
cp $PROJ/wagtail_migrations/wagtailimportexport/views_py2.py $ENV/lib/python3.6/site-packages/wagtailimportexport/views.py
# mv $PROJ/marco/portal/base/migrations/0002_portalimage_collection.py $PROJ/wagtail_migrations/
mv $PROJ/marco/portal/base/migrations/0002_auto_20200526_2354.py $PROJ/wagtail_migrations/
mv $PROJ/marco/portal/base/migrations/0003_auto_20200526_2357.py $PROJ/wagtail_migrations/
mv $PROJ/marco/portal/base/migrations/0004_auto_20200613_0023.py $PROJ/wagtail_migrations/
# $MIGRATE 1

$PYTHON $DJ migrate data_manager 0023

for VER in '1_04' '1_05' '1_06' '1_07' '1_08' '1_09' '1_10' '1_11' '1_12' '1_13'
do
  echo '************************************'
  echo '************************************'
  echo '****           '$VER'            *****'
  echo '************************************'
  echo '************************************'
  # rm -r $ENV/lib/python3.6/site-packages/~*

  $PROJ/wagtail_migrations/wagtail_$VER.sh

  # $MIGRATE 1
done

for VER in '2_00' '2_01' '2_02' '2_03' '2_04' '2_05' '2_06' '2_07' '2_08' '2_09'
do
  echo '************************************'
  echo '************************************'
  echo '****           '$VER'            *****'
  echo '************************************'
  echo '************************************'
  $PROJ/wagtail_migrations/wagtail_$VER.sh
done
