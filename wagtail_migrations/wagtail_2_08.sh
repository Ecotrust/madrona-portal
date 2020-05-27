#!/bin/bash

PROJ=/usr/local/apps/ocean_portal
ENV=$PROJ/wag_env;
PIP=$ENV/bin/pip;

# 2_08
$PIP uninstall wagtail -y
$PIP uninstall Django -y
$PIP uninstall asgiref -y
$PIP install "asgiref==3.2.7"
$PIP install "Django<2.3"
$PIP install "wagtail==2.8.2"

PYTHON=$ENV/bin/python3;
DJ=$PROJ/marco/manage.py;

$PYTHON $DJ migrate wagtailcore
# $PYTHON $DJ migrate wagtailadmin
# $PYTHON $DJ migrate wagtaildocs
# $PYTHON $DJ migrate wagtailembeds
$PYTHON $DJ migrate wagtailforms
# $PYTHON $DJ migrate wagtailimages
# $PYTHON $DJ migrate wagtailredirects
# $PYTHON $DJ migrate wagtailsearch
# $PYTHON $DJ migrate wagtailusers


$PYTHON $DJ migrate auth 0011
$PYTHON $DJ migrate admin 0003
# cp $PROJ/wagtail_migrations/0002_portalimage_collection.py $PROJ/marco/portal/base/migrations/
# $PYTHON $DJ migrate base 0002
