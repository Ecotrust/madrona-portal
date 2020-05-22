#!/bin/bash

PROJ=/usr/local/apps/ocean_portal
ENV=$PROJ/wag_env;
PIP=$ENV/bin/pip;

# 1_10
$PIP uninstall wagtail -y
$PIP install "wagtail==1.10.1"

PYTHON=$ENV/bin/python3;
DJ=$PROJ/marco/manage.py;

$PYTHON $DJ migrate wagtailcore
# $PYTHON $DJ migrate wagtailadmin
# $PYTHON $DJ migrate wagtaildocs
# $PYTHON $DJ migrate wagtailembeds
# $PYTHON $DJ migrate wagtailforms

# Thanks for the 'auto yes' help, Dhanushka Amarakoon
#   https://stackoverflow.com/a/40231886/706797
yes yes | $PYTHON $DJ migrate wagtailimages
# $PYTHON $DJ migrate wagtailredirects
# $PYTHON $DJ migrate wagtailsearch
$PYTHON $DJ migrate wagtailusers
