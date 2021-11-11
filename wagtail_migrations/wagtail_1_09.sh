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

# 1_09
$PIP uninstall wagtail -y
$PIP uninstall django-modelcluster -y
$PIP uninstall django-taggit -y
$PIP install "django-taggit==0.20.0"
$PIP install "django-modelcluster==3.1"
$PIP install "wagtail==1.9.1"

PYTHON=$ENV/bin/python3;
DJ=$PROJ/marco/manage.py;

# $PYTHON $DJ migrate wagtailcore
# $PYTHON $DJ migrate wagtailadmin
# $PYTHON $DJ migrate wagtaildocs
# $PYTHON $DJ migrate wagtailembeds
# $PYTHON $DJ migrate wagtailforms
$PYTHON $DJ migrate wagtailimages
# $PYTHON $DJ migrate wagtailredirects
# $PYTHON $DJ migrate wagtailsearch
# $PYTHON $DJ migrate wagtailusers

cp $PROJ/wagtail_migrations/0004_auto_20200613_0023.py $PROJ/marco/portal/base/migrations/
$PYTHON $DJ migrate base 0004
