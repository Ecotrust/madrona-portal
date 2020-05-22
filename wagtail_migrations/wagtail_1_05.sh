#!/bin/bash

PROJ=/usr/local/apps/ocean_portal
ENV=$PROJ/wag_env;
PIP=$ENV/bin/pip;

# 1_05
$PIP uninstall wagtail -y
$PIP uninstall django-modelcluster -y
$PIP install "django-modelcluster==2.0"
$PIP install "wagtail==1.5.3"

PYTHON=$ENV/bin/python3;
DJ=$PROJ/marco/manage.py;

$PYTHON $DJ migrate wagtailcore
$PYTHON $DJ migrate wagtailadmin
$PYTHON $DJ migrate wagtaildocs
$PYTHON $DJ migrate wagtailembeds
$PYTHON $DJ migrate wagtailforms
$PYTHON $DJ migrate wagtailimages
$PYTHON $DJ migrate wagtailredirects
$PYTHON $DJ migrate wagtailsearch
$PYTHON $DJ migrate wagtailusers
