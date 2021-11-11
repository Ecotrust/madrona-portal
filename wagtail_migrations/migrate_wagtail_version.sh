#!/bin/bash

VERSION=$1
PROJ=/usr/local/apps/ocean_portal
ENV=$PROJ/wag_env;
PYTHON=$ENV/bin/python3;
DJ=$PROJ/marco/manage.py;

if [[ $VERSION -eq 1 ]]
then
  $PYTHON $DJ migrate wagtailcore
  $PYTHON $DJ migrate wagtailadmin
  $PYTHON $DJ migrate wagtaildocs
  $PYTHON $DJ migrate wagtailembeds
  $PYTHON $DJ migrate wagtailforms
  $PYTHON $DJ migrate wagtailimages
  $PYTHON $DJ migrate wagtailredirects
  $PYTHON $DJ migrate wagtailsearch
  $PYTHON $DJ migrate wagtailusers
else
  $PYTHON $DJ migrate wagtail
fi
