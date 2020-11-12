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

# 2_10
$PIP uninstall wagtail -y
$PIP uninstall Willow -y
$PIP uninstall djangorestframework -y
$PIP install "djangorestframework==3.12.2"
$PIP install "Willow==1.4"
$PIP install "django-filter==2.4.0"
$PIP install "wagtail==2.10"

PYTHON=$ENV/bin/python3;
DJ=$PROJ/marco/manage.py;

$PYTHON $DJ migrate wagtailcore
# $PYTHON $DJ migrate wagtailadmin
# $PYTHON $DJ migrate wagtaildocs
# $PYTHON $DJ migrate wagtailembeds
# $PYTHON $DJ migrate wagtailforms
# $PYTHON $DJ migrate wagtailimages
# $PYTHON $DJ migrate wagtailredirects
# $PYTHON $DJ migrate wagtailsearch
# $PYTHON $DJ migrate wagtailusers
