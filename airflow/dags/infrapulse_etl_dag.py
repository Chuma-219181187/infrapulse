from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime
import sys
import os
import psycopg2

# Add parent directory to path so we can import ETL modules
# ETL modules are in /opt/airflow/ (same level as dags/)
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from extract import extract_failures
from transform import transform_failures
from quality_checks import check_null_asset, check_negative_outage
from load import load_failures
from elt_logger import log_info, log_error

def run_etl():
    # Use flexible path that works in both local and Astronomer environments
    base_dir = os.getenv("AIRFLOW_DATA_DIR", "/opt/airflow/data")
    file_path = os.path.join(base_dir, "staging", "failures.csv")
    
    # Log the path being used
    log_info(f"Using data file: {file_path}")

    # Skip ETL if file doesn't exist (useful for Astronomer deployments without data volume)
    if not os.path.exists(file_path):
        log_info(f"Data file not found at {file_path}. Skipping ETL (normal for test deployments).")
        return

    df = extract_failures(file_path)
    df = transform_failures(df)

    if check_null_asset(df) > 0:
        raise ValueError("Null asset IDs found")

    if check_negative_outage(df) > 0:
        raise ValueError("Negative outage values found")

    load_failures(df)

def verify_data():
    """Verify data loaded into PostgreSQL (cloud-ready)"""
    
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "postgres"),
            port=int(os.getenv("POSTGRES_PORT", 5432)),
            database=os.getenv("POSTGRES_DB", "railway"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            sslmode=os.getenv("POSTGRES_SSL_MODE", "require"),  # Required for Railway
        )
        cur = conn.cursor()
        
        # Check 1: Count records
        cur.execute("SELECT COUNT(*) FROM fact_service_failure;")
        record_count = cur.fetchone()[0]
        log_info(f"Total records in fact_service_failure: {record_count}")
        if record_count == 0:
            raise ValueError("No records found in fact_service_failure table")
        
        # Check 2: Check for null asset_key
        cur.execute("SELECT COUNT(*) FROM fact_service_failure WHERE asset_key IS NULL;")
        null_assets = cur.fetchone()[0]
        log_info(f"Null asset_key count: {null_assets}")
        if null_assets > 0:
            raise ValueError(f"Found {null_assets} records with null asset_key")
        
        # Check 3: Check for negative outage_minutes
        cur.execute("SELECT COUNT(*) FROM fact_service_failure WHERE outage_minutes < 0;")
        negative_outages = cur.fetchone()[0]
        log_info(f"Negative outage_minutes count: {negative_outages}")
        if negative_outages > 0:
            raise ValueError(f"Found {negative_outages} records with negative outage_minutes")
        
        # Check 4: Verify assets exist in dim_asset
        cur.execute("""
            SELECT COUNT(*) FROM fact_service_failure f 
            WHERE f.asset_key NOT IN (SELECT asset_key FROM dim_asset)
        """)
        orphaned = cur.fetchone()[0]
        log_info(f"Orphaned fact records (no asset): {orphaned}")
        if orphaned > 0:
            raise ValueError(f"Found {orphaned} orphaned fact records")
        
        # Check 5: Get sample data
        cur.execute("""
            SELECT 
              fa.asset_id,
              dd.full_date,
              fd.failure_type,
              fd.outage_minutes
            FROM fact_service_failure fd
            JOIN dim_asset fa ON fd.asset_key = fa.asset_key
            JOIN dim_date dd ON fd.date_key = dd.date_key
            LIMIT 3
        """)
        samples = cur.fetchall()
        log_info("Sample data:")
        for row in samples:
            log_info(f"  Asset: {row[0]}, Date: {row[1]}, Type: {row[2]}, Outage: {row[3]} min")
        
        # Check 6: ETL metadata status
        cur.execute("""
            SELECT COUNT(*), SUM(records_loaded), MAX(status) 
            FROM etl_metadata 
            WHERE status = 'SUCCESS'
        """)
        result = cur.fetchone()
        log_info(f"Successful ETL runs: {result[0]}, Total records loaded: {result[1]}")
        
        conn.close()
        log_info("✓ All data verification checks passed!")
        
    except Exception as e:
        log_error(f"Data verification failed: {str(e)}")
        raise

default_args = {
    "owner": "data_engineer",
    "start_date": datetime(2026, 1, 1),
    "retries": 2
}

with DAG(
    dag_id="infrapulse_etl",
    schedule_interval="@daily",
    catchup=False,
    default_args=default_args
) as dag:

    ingest = BashOperator(
        task_id="ingest_files",
        bash_command="""
        set +e
        BASE_DIR="${AIRFLOW_DATA_DIR:-/opt/airflow/data}"
        STAGING_DIR="$BASE_DIR/staging"
        RAW_DIR="$BASE_DIR/raw"
        
        # Try to create directories, but don't fail if we can't
        mkdir -p "$STAGING_DIR" "$BASE_DIR/archive" 2>/dev/null
        
        # Check if raw directory exists and has files
        if [ -d "$RAW_DIR" ] && [ "$(ls -A "$RAW_DIR" 2>/dev/null)" ]; then
            echo "📂 Found raw data directory: $RAW_DIR"
            # Copy all files from raw subdirectories to staging
            find "$RAW_DIR" -maxdepth 2 -type f -name "*.csv" -exec cp {} "$STAGING_DIR/" \\; 2>/dev/null || true
            if [ "$(ls -A "$STAGING_DIR" 2>/dev/null)" ]; then
                FILE_COUNT=$(ls "$STAGING_DIR" | wc -l)
                echo "✅ Files ingested successfully: $FILE_COUNT files"
            else
                echo "ℹ️  No CSV files found in raw directory"
            fi
        else
            echo "ℹ️  No raw data directory found at: $RAW_DIR"
            echo "ℹ️  This is normal for Astronomer deployments without persistent data volumes"
        fi
        exit 0
        """,
        do_xcom_push=False
    )

    etl = PythonOperator(
        task_id="run_etl",
        python_callable=run_etl
    )

    archive = BashOperator(
        task_id="archive_files",
        bash_command="""
        BASE_DIR="${AIRFLOW_DATA_DIR:-/opt/airflow/data}"
        ARCHIVE_SUBDIR="$BASE_DIR/archive/$(date +%F)"
        mkdir -p "$ARCHIVE_SUBDIR"
        mv "$BASE_DIR/staging"/* "$ARCHIVE_SUBDIR/" 2>/dev/null || echo "No staging files to archive"
        """,
        do_xcom_push=False
    )

    verify = PythonOperator(
        task_id="verify_data",
        python_callable=verify_data
    )

    ingest >> etl >> archive >> verify
