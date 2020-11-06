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

# 2_03
# No migrations, what's the point of installing?
# $PIP uninstall wagtail -y
# taggit 0.24 worked great for wagtail 2.0-2.2. Maybe we'll just upgrade to 0.23.0 at 2.0 instead?
# $PIP uninstall django-taggit -y
# $PIP install "django-taggit==0.23.0"
# $PIP install "wagtail==2.3"

PYTHON=$ENV/bin/python3;
DJ=$PROJ/marco/manage.py;

# $PYTHON $DJ migrate wagtailcore
# $PYTHON $DJ migrate wagtailadmin
# $PYTHON $DJ migrate wagtaildocs
# $PYTHON $DJ migrate wagtailembeds
# $PYTHON $DJ migrate wagtailforms
# $PYTHON $DJ migrate wagtailimages
# $PYTHON $DJ migrate wagtailredirects
# $PYTHON $DJ migrate wagtailsearch
# $PYTHON $DJ migrate wagtailusers
