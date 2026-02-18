# Airflow DAG Documentation

DAG ID: infrapulse_etl

Schedule: Daily (@daily)

Tasks:

1. ingest_files (BashOperator)
   - Moves raw files to staging

2. run_etl (PythonOperator)
   - Extract
   - Transform
   - Validate
   - Load

3. archive_files (BashOperator)
   - Moves processed files to archive

Retries: 2
