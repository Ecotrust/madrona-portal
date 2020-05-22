#!/bin/bash

PROJ=/usr/local/apps/ocean_portal
ENV=$PROJ/wag_env;
PIP=$ENV/bin/pip;

# 2_00
$PIP uninstall rpc4django -y
$PIP uninstall wagtail -y
$PIP uninstall djangorestframework -y
$PIP uninstall Willow -y
$PIP uninstall django-modelcluster -y
$PIP uninstall django-taggit -y
$PIP uninstall django-treebeard -y
$PIP uninstall Django -y
$PIP install "Django==2.0.13"
$PIP install "django-treebeard==4.3.1"
$PIP install "django-taggit==0.23.0"
$PIP install "django-modelcluster==4.4.1"
$PIP install "Willow==1.1"
$PIP install "djangorestframework==3.11.0"
$PIP install "wagtail==2.0.2"
$PIP install "rpc4django==0.6.3"
$PIP uninstall madrona-manipulators -y
$PIP install -e git+https://github.com/MidAtlanticPortal/madrona-manipulators.git@dj2#egg=madrona_manipulators

PYTHON=$ENV/bin/python3;
DJ=$PROJ/marco/manage.py;

$PYTHON $DJ migrate auth 0009

# $PYTHON $DJ migrate wagtailcore
# $PYTHON $DJ migrate wagtailadmin
# $PYTHON $DJ migrate wagtaildocs
# $PYTHON $DJ migrate wagtailembeds
# $PYTHON $DJ migrate wagtailforms
# $PYTHON $DJ migrate wagtailimages
# $PYTHON $DJ migrate wagtailredirects
# $PYTHON $DJ migrate wagtailsearch
# $PYTHON $DJ migrate wagtailusers
