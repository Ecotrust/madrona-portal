#!/bin/bash

PROJ=/usr/local/apps/ocean_portal
ENV=$PROJ/wag_env;
while getopts e:v: flag
do
  case "${flag}" in
    e) ENV=${OPTARG};;
    v) PYVER=${OPTARG};;
  esac
done
PIP=$ENV/bin/pip;
PYTHON=$ENV/bin/python3;
DJ=$PROJ/marco/manage.py;

# 1_08
$PIP uninstall wagtail -y
$PIP uninstall django -y
$PIP install "django==1.10.8"
$PIP install "wagtail==1.8.2"

cp $PROJ/wagtail_migrations/libgeos_1_10.py $ENV'/lib/python'$PYVER'/site-packages/django/contrib/gis/geos/libgeos.py'

$PYTHON $DJ migrate wagtailcore
# $PYTHON $DJ migrate wagtailadmin
# $PYTHON $DJ migrate wagtaildocs
# $PYTHON $DJ migrate wagtailembeds
# $PYTHON $DJ migrate wagtailforms
$PYTHON $DJ migrate wagtailimages
# $PYTHON $DJ migrate wagtailredirects
# $PYTHON $DJ migrate wagtailsearch
# $PYTHON $DJ migrate wagtailusers
