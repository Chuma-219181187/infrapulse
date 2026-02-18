# ETL Pipeline Flow

1. Raw data dropped in data/raw/YYYY-MM-DD
2. Shell script ingests to staging
3. Airflow DAG triggered
4. Extract module reads CSV
5. Transform module:
   - Cleans duplicates
   - Calculates outage_minutes
   - Generates date_key
6. Quality checks run
7. Load module inserts into:
   - dim_asset
   - dim_date
   - fact_service_failure
8. Metadata table updated
9. Files archived
