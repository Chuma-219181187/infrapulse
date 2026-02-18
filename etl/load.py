import psycopg2
import os
from elt_logger import log_info, log_error, log_warning

def load_failures(df):
    """Load failures to PostgreSQL warehouse (cloud-ready)"""

    # Use environment variables for cloud deployment
    conn_params = {
        "host": os.getenv("POSTGRES_HOST", "postgres"),
        "port": int(os.getenv("POSTGRES_PORT", 5432)),
        "database": os.getenv("POSTGRES_DB", "railway"),
        "user": os.getenv("POSTGRES_USER"),
        "password": os.getenv("POSTGRES_PASSWORD"),
        "sslmode": os.getenv("POSTGRES_SSL_MODE", "require"),  # Required for Railway
    }

    try:
        # Mask password for logging
        safe_host = f"{conn_params['host']}:{conn_params['port']}"
        log_info(f"🔗 Connecting to PostgreSQL: {safe_host}")
        
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()
        
        log_info(f"✅ Connected to database: {conn_params['database']}")

        records_loaded = 0
        assets_inserted = 0
        dates_inserted = 0

        log_info(f"📝 Loading {len(df)} records to warehouse...")

        for idx, (_, row) in enumerate(df.iterrows(), 1):

            cur.execute("""
                INSERT INTO dim_asset (asset_id)
                VALUES (%s)
                ON CONFLICT (asset_id) DO NOTHING
            """, (row["asset_id"],))
            
            if cur.rowcount > 0:
                assets_inserted += 1

            cur.execute("""
                INSERT INTO dim_date (date_key, full_date)
                VALUES (%s, %s)
                ON CONFLICT (date_key) DO NOTHING
            """, (row["date_key"], row["start_time"].date()))
            
            if cur.rowcount > 0:
                dates_inserted += 1

            cur.execute("""
                SELECT asset_key FROM dim_asset WHERE asset_id=%s
            """, (row["asset_id"],))

            asset_key = cur.fetchone()[0]

            cur.execute("""
                INSERT INTO fact_service_failure
                (asset_key, date_key, failure_type, outage_minutes, resolved)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                asset_key,
                row["date_key"],
                row["failure_type"],
                int(row["outage_minutes"]),
                row["resolved"]
            ))

            records_loaded += 1
            
            # Log progress every 50 records
            if idx % 50 == 0:
                log_info(f"  📊 Progress: {idx}/{len(df)} records processed...")

        # Record ETL metadata
        cur.execute("""
            INSERT INTO etl_metadata (records_loaded, status)
            VALUES (%s, %s)
        """, (records_loaded, "SUCCESS"))

        conn.commit()
        cur.close()
        conn.close()

        log_info(f"✅ Load complete!")
        log_info(f"  📊 Total records loaded: {records_loaded}")
        log_info(f"  🏷️  New assets inserted: {assets_inserted}")
        log_info(f"  📅 New dates inserted: {dates_inserted}")
        log_info(f"  🏭 Fact records: {records_loaded}")

    except Exception as e:
        log_error(f"❌ Failed to load data: {str(e)}")
        raise

