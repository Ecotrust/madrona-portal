#!/bin/bash
ENV=/tmp/wag_env;
PYVER='3.6'
DBNAME='ocean_portal'
DBUSER='postgres'
# Let's hold off on password for a bit
DBPASS=''

while getopts i:u:p:n:e:v: flag
do
  case "${flag}" in
    i) infile=${OPTARG};;
    u) DBUSER=${OPTARG};;
    p) DBPASS=${OPTARG};;
    n) DBNAME=${OPTARG};;
    e) ENV=${OPTARG};;
    v) PYVER=${OPTARG};;
  esac
done

PROJ=/usr/local/apps/ocean_portal;
PIP=$ENV/bin/pip;
PYTHON=$ENV/bin/python3;
DJ=$PROJ/marco/manage.py;
# MIGRATE=$PROJ/wagtail_migrations/migrate_wagtail_version.sh -e $ENV -v $PYVER;

if [[ ! -f $infile ]] ; then
  echo 'File "$infile" DOES NOT EXIST. Please provide a valid input file with the "-i" flag';
  exit;
fi

echo "Input SQL file: $infile";

echo "Checking out Wagtail 1.x compatible code-base..."
git checkout wagtail-1x

# Prep and load the DB
sudo -u postgres dropdb $DBNAME;
sudo -u postgres createdb -O $DBUSER $DBNAME;
sudo -u postgres psql -c "CREATE EXTENSION postgis; CREATE EXTENSION postgis_topology;" $DBNAME;
sudo -u postgres psql $DBNAME < $infile;

# Install requirements to standalone virtualenv
sudo rm -r $ENV
if [ $? -eq 0 ]; then
    echo "Delete old env succeeded."
else
    sudo rm -r $ENV
fi
python3 -m virtualenv $ENV;
$PIP install -r $PROJ'/wagtail_migrations/'$PYVER'_requirements_wagtail_1.3.1.txt'
cp $PROJ/wagtail_migrations/libgeos_1_9.py $ENV'/lib/python'$PYVER'/site-packages/django/contrib/gis/geos/libgeos.py'
if [ $? -eq 0 ]; then
    echo "Custom libgeos_1_9 inserted"
else
    # 20.04 Focal Fossa has py 3.8, not Bionic's 3.6
    PYVER='3.8'
    cp $PROJ/wagtail_migrations/libgeos_1_9.py $ENV'/lib/python'$PYVER'/site-packages/django/contrib/gis/geos/libgeos.py'
fi
cp $PROJ/wagtail_migrations/wagtailimportexport/wagtail_hooks_py2.py $ENV'/lib/python'$PYVER'/site-packages/wagtailimportexport/wagtail_hooks.py'
cp $PROJ/wagtail_migrations/wagtailimportexport/views_py2.py $ENV'/lib/python'$PYVER'/site-packages/wagtailimportexport/views.py'
# mv $PROJ/marco/portal/base/migrations/0002_portalimage_collection.py $PROJ/wagtail_migrations/
mv $PROJ/marco/portal/base/migrations/0002_auto_20200526_2354.py $PROJ/wagtail_migrations/
mv $PROJ/marco/portal/base/migrations/0003_auto_20200526_2357.py $PROJ/wagtail_migrations/
mv $PROJ/marco/portal/base/migrations/0004_auto_20200613_0023.py $PROJ/wagtail_migrations/
mv $PROJ/marco/portal/base/migrations/0005_portalimage_file_hash.py $PROJ/wagtail_migrations/
# $MIGRATE 1

$PYTHON $DJ migrate data_manager 0023
$PYTHON $DJ migrate ocean_stories 0017

for VER in '1_04' '1_05' '1_06' '1_07' '1_08' '1_09' '1_10' '1_11' '1_12' '1_13'
do
  echo '************************************'
  echo '************************************'
  echo '****           '$VER'            *****'
  echo '************************************'
  echo '************************************'
  # rm -r $ENV/lib/python3.6/site-packages/~*

  $PROJ/wagtail_migrations/wagtail_$VER.sh -e $ENV -v $PYVER

  # $MIGRATE 1
done

echo "Checking out Wagtail 2.x compatible code-base..."
git checkout wagtail-migration

for VER in '2_00' '2_01' '2_02' '2_03' '2_04' '2_05' '2_06' '2_07' '2_08' '2_09'
do
  echo '************************************'
  echo '************************************'
  echo '****           '$VER'            *****'
  echo '************************************'
  echo '************************************'
  $PROJ/wagtail_migrations/wagtail_$VER.sh -e $ENV -v $PYVER
done
