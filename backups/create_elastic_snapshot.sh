#!/bin/bash

REPOSITORY=""

while getopts "r:" opt; do
  case $opt in
    r) REPOSITORY="$OPTARG" ;;
    *) echo "Usage: $0 -r <repository>"; exit 1 ;;
  esac
done

if [[ -z "$REPOSITORY" ]]; then
  echo "Error: -r <repository> is required"
  exit 1
fi

DATETIME_VAR=$(date +%Y%m%d_%H%M)
/usr/bin/curl -X PUT "localhost:9200/_snapshot/${REPOSITORY}/snapshot_${DATETIME_VAR}" -H 'Content-Type: application/json' -d '{"indices": "metadata_v1", "ignore_unavailable": true, "include_global_state": false}'
