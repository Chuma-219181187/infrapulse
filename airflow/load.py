import psycopg2
import os
from elt_logger import log_info, log_error

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
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()

        records_loaded = 0

        for _, row in df.iterrows():

            cur.execute("""
                INSERT INTO dim_asset (asset_id)
                VALUES (%s)
                ON CONFLICT (asset_id) DO NOTHING
            """, (row["asset_id"],))

            cur.execute("""
                INSERT INTO dim_date (date_key, full_date)
                VALUES (%s, %s)
                ON CONFLICT (date_key) DO NOTHING
            """, (row["date_key"], row["start_time"].date()))

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

        cur.execute("""
            INSERT INTO etl_metadata (records_loaded, status)
            VALUES (%s, %s)
        """, (records_loaded, "SUCCESS"))

        conn.commit()
        cur.close()
        conn.close()

        log_info(f"Loaded {records_loaded} records")

    except Exception as e:
        log_error(f"Failed to load data: {str(e)}")
        raise

