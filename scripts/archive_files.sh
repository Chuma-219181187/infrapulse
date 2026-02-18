#!/bin/bash

ARCHIVE=/opt/airflow/data/archive/$(date +%F)
mkdir -p $ARCHIVE

mv /opt/airflow/data/staging/* $ARCHIVE 2>/dev/null
