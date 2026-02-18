#!/bin/bash

DATE=$(date +%F)
BACKUP_DIR=backups
mkdir -p $BACKUP_DIR

docker exec infrapulse_postgres pg_dump -U postgres infrapulse > $BACKUP_DIR/infrapulse_$DATE.sql

echo "Backup completed"
