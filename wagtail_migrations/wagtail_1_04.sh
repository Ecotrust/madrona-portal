#!/bin/bash

PROJ=/usr/local/apps/ocean_portal
ENV=$PROJ/wag_env;
PIP=$ENV/bin/pip;

# 1_04
$PIP uninstall wagtail -y
$PIP uninstall Willow -y
$PIP install "Willow==0.3.1"
$PIP install "wagtail==1.4.6"

PYTHON=$ENV/bin/python3;
DJ=$PROJ/marco/manage.py;

$PYTHON $DJ migrate wagtailcore
# $PYTHON $DJ migrate wagtailadmin
$PYTHON $DJ migrate wagtaildocs
# $PYTHON $DJ migrate wagtailembeds
# $PYTHON $DJ migrate wagtailforms
$PYTHON $DJ migrate wagtailimages
# $PYTHON $DJ migrate wagtailredirects
# $PYTHON $DJ migrate wagtailsearch
# $PYTHON $DJ migrate wagtailusers
