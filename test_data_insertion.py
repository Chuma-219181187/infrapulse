#!/usr/bin/env python3
"""
Test Data Insertion and Query
Demonstrates how to insert and retrieve data from Railway
"""

import psycopg2
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv('.env.prod')

def insert_test_data():
    """Insert and query test data"""
    
    config = {
        "host": os.getenv("POSTGRES_HOST"),
        "port": int(os.getenv("POSTGRES_PORT", 5432)),
        "database": os.getenv("POSTGRES_DB"),
        "user": os.getenv("POSTGRES_USER"),
        "password": os.getenv("POSTGRES_PASSWORD"),
        "sslmode": os.getenv("POSTGRES_SSL_MODE", "require"),
    }
    
    print("=" * 60)
    print("🧪 Testing Data Insertion & Query")
    print("=" * 60)
    
    try:
        conn = psycopg2.connect(**config)
        cur = conn.cursor()
        
        # Step 1: Insert into dim_asset
        print("\n1️⃣  Inserting into dim_asset...")
        cur.execute("""
            INSERT INTO dim_asset (asset_id, asset_type, service_type, location)
            VALUES (%s, %s, %s, %s)
            RETURNING asset_key;
        """, ('ASSET-001', 'Server', 'Web Service', 'DataCenter-1'))
        
        asset_key = cur.fetchone()[0]
        print(f"   ✅ Inserted asset with key: {asset_key}")
        
        # Step 2: Insert into dim_date
        print("\n2️⃣  Inserting into dim_date...")
        cur.execute("""
            INSERT INTO dim_date (date_key, full_date)
            VALUES (%s, %s);
        """, (20260217, datetime(2026, 2, 17).date()))
        
        print(f"   ✅ Inserted date: 2026-02-17")
        
        # Step 3: Insert into fact_service_failure
        print("\n3️⃣  Inserting into fact_service_failure...")
        cur.execute("""
            INSERT INTO fact_service_failure (asset_key, date_key, failure_type, outage_minutes, resolved)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING failure_id;
        """, (asset_key, 20260217, 'Network Outage', 45, True))
        
        failure_id = cur.fetchone()[0]
        print(f"   ✅ Inserted failure with ID: {failure_id}")
        
        # Step 4: Record in etl_metadata
        print("\n4️⃣  Recording ETL metadata...")
        cur.execute("""
            INSERT INTO etl_metadata (records_loaded, status)
            VALUES (%s, %s)
            RETURNING run_id;
        """, (3, 'success'))
        
        run_id = cur.fetchone()[0]
        print(f"   ✅ Recorded ETL run: {run_id}")
        
        conn.commit()
        
        # Step 5: Query the data back
        print("\n" + "=" * 60)
        print("📊 Querying Data Back")
        print("=" * 60)
        
        # Query fact_service_failure with joins
        print("\n🔍 Fact Service Failure with Asset Info:")
        cur.execute("""
            SELECT 
                f.failure_id,
                a.asset_id,
                a.asset_type,
                d.full_date,
                f.failure_type,
                f.outage_minutes,
                f.resolved
            FROM fact_service_failure f
            JOIN dim_asset a ON f.asset_key = a.asset_key
            JOIN dim_date d ON f.date_key = d.date_key;
        """)
        
        rows = cur.fetchall()
        for row in rows:
            print(f"   Failure ID: {row[0]}")
            print(f"   Asset: {row[1]} ({row[2]})")
            print(f"   Date: {row[3]}")
            print(f"   Type: {row[4]} | Outage: {row[5]} minutes | Resolved: {row[6]}")
        
        # Query counts
        print("\n📈 Table Counts:")
        for table in ['dim_asset', 'dim_date', 'fact_service_failure', 'etl_metadata']:
            cur.execute(f"SELECT COUNT(*) FROM {table};")
            count = cur.fetchone()[0]
            print(f"   {table:<30} {count} rows")
        
        print("\n" + "=" * 60)
        print("✅ Data insertion and retrieval successful!")
        print("=" * 60)
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = insert_test_data()
    exit(0 if success else 1)
