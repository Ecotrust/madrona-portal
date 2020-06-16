#!/bin/bash

PROJ=/usr/local/apps/ocean_portal
ENV=$PROJ/wag_env;
PIP=$ENV/bin/pip;

# 1_13
$PIP uninstall wagtail -y
$PIP uninstall Willow -y

$PIP install "Willow==1.0"
$PIP install "wagtail==1.13.4"

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

$PYTHON $DJ migrate accounts 0006
$PYTHON $DJ migrate auth 0008
$PYTHON $DJ migrate data_manager 0033
$PYTHON $DJ migrate drawing 0005
$PYTHON $DJ migrate grid_pages 0005
$PYTHON $DJ migrate mapgroups 0006
$PYTHON $DJ migrate news 0004
# $PYTHON $DJ migrate ocean_stories 0017
$PYTHON $DJ migrate scenarios 0001 --fake-initial
$PYTHON $DJ migrate visualize 0006
