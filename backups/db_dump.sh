#!/bin/bash

DBNAME=dbname
DBOWNER=dbowner
DBPASSWORD=password
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
OUTFILE=$DBNAME'_dump.sql'
OUTDIR=$DIR

while getopts n:o:p:d:f: flag
do
  case "${flag}" in
    n) DBNAME=${OPTARG};;           # (n)ame of the database
    o) DBOWNER=${OPTARG};;          # Database (o)wner
    p) DBPASSWORD=${OPTARG};;       # Database owner's (p)assword
    d) OUTDIR=${OPTARG};;           # Output dump file (d)irectory
    f) OUTFILE=${OPTARG};;          # Output dump (f)ilename
  esac
done

PGPASSWORD=$DBPASSWORD /usr/bin/pg_dump -b -c -n public -O --quote-all-identifiers --no-acl -w -U $DBOWNER -f $OUTDIR/$OUTFILE $DBNAME
