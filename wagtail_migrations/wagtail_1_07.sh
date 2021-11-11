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

# 1_07
$PIP uninstall wagtail -y
$PIP uninstall Willow -y
$PIP install "Willow<0.5"
$PIP install "wagtail==1.7"

PYTHON=$ENV/bin/python3;
DJ=$PROJ/marco/manage.py;

$PYTHON $DJ migrate wagtailcore
# $PYTHON $DJ migrate wagtailadmin
# $PYTHON $DJ migrate wagtaildocs
# $PYTHON $DJ migrate wagtailembeds
# $PYTHON $DJ migrate wagtailforms
$PYTHON $DJ migrate wagtailimages
# $PYTHON $DJ migrate wagtailredirects
# $PYTHON $DJ migrate wagtailsearch
$PYTHON $DJ migrate wagtailusers

cp $PROJ/wagtail_migrations/0002_auto_20200526_2354.py $PROJ/marco/portal/base/migrations/
cp $PROJ/wagtail_migrations/0003_auto_20200526_2357.py $PROJ/marco/portal/base/migrations/
$PYTHON $DJ migrate base 0003
