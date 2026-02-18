#!/bin/bash

RAW_DIR=/opt/airflow/data/raw/$(date +%F)
STAGING=/opt/airflow/data/staging

mkdir -p $STAGING

for file in $RAW_DIR/*; do
  if [[ -s "$file" ]]; then
    cp "$file" $STAGING
    echo "Moved $(basename $file) to staging"
  fi
done
