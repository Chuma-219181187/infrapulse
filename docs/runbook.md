# InfraPulse Operations Runbook

## Starting the System

docker-compose up -d

## Access Airflow

http://localhost:8080
Username: admin
Password: admin

## Trigger ETL

Enable DAG → Click Trigger

## Backup Database

bash scripts/backup.sh

## Troubleshooting

1. Check Airflow logs
2. Check logs/etl.log
3. Verify database connection
4. Restart containers if needed:
   docker-compose restart
