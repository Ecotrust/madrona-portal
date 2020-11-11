#!/bin/bash
ENV=/usr/local/apps/wag_env;
PYVER='3.6'
PYGDAL='<2.2.4'
DBNAME='ocean_portal'
DBUSER='postgres'
infile='/usr/local/apps/ocean_portal/data/marco_portal_prod_12.sql'
# Let's hold off on password for a bit
DBPASS=''
PROMPT_VERSION=true

while getopts i:u:p:n:e:v:s:g: flag
do
  case "${flag}" in
    i) infile=${OPTARG};;           # (i)nput .SQL file to import
    u) DBUSER=${OPTARG};;           # Database (u)ser
    p) DBPASS=${OPTARG};;           # Database User's (p)assword
    n) DBNAME=${OPTARG};;           # Database (n)ame
    e) ENV=${OPTARG};;              # (e)nvironment directory location
    v) PYVER=${OPTARG};;            # Python (v)ersion
    s) PROMPT_VERSION=${OPTARG};;   # (s)top and prompt before each version upgrade
    g) PYGDAL=${OPTARG};;           # Py(g)DAL version installed
  esac
done

PROJ=/usr/local/apps/ocean_portal;
PIP=$ENV/bin/pip;
PYTHON=$ENV/bin/python3;
DJ=$PROJ/marco/manage.py;

$PROJ/wagtail_migrations/migrate.sh -e $ENV -i $infile -u $DBUSER -p $DBPASS -n $DBNAME -v $PYVER -s $PROMPT_VERSION -g $PYGDAL
