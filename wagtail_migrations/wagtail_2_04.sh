#!/bin/bash

PROJ=/usr/local/apps/ocean_portal
ENV=$PROJ/wag_env;
PIP=$ENV/bin/pip;

# 2_04
$PIP uninstall wagtail -y
$PIP uninstall draftjs-exporter -y
$PIP install "draftjs-exporter==2.1.7"
$PIP install "wagtail==2.4"

PYTHON=$ENV/bin/python3;
DJ=$PROJ/marco/manage.py;

$PYTHON $DJ migrate wagtailcore
# $PYTHON $DJ migrate wagtailadmin
$PYTHON $DJ migrate wagtaildocs
$PYTHON $DJ migrate wagtailembeds
# $PYTHON $DJ migrate wagtailforms
# $PYTHON $DJ migrate wagtailimages
# $PYTHON $DJ migrate wagtailredirects
$PYTHON $DJ migrate wagtailsearch
$PYTHON $DJ migrate wagtailusers
