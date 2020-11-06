#!/bin/bash
ENV=/tmp/wag_env;
PYVER='3.8'
DBNAME='ocean_portal'
DBUSER='postgres'
infile='/usr/local/apps/ocean_portal/data/marco_portal_prod_12.sql'
# Let's hold off on password for a bit
DBPASS=''

while getopts i:u:p:n:e:v: flag
do
  case "${flag}" in
    i) infile=${OPTARG};;
    u) DBUSER=${OPTARG};;
    p) DBPASS=${OPTARG};;
    n) DBNAME=${OPTARG};;
    e) ENV=${OPTARG};;
    v) PYVER=${OPTARG};;
  esac
done

PROJ=/usr/local/apps/ocean_portal;
PIP=$ENV/bin/pip;
PYTHON=$ENV/bin/python3;
DJ=$PROJ/marco/manage.py;

sudo migrate.sh -e $ENV -i $infile -u $DBUSER -p $DBPASS -n $DBNAME -v $PYVER
