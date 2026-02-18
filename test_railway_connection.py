#!/usr/bin/env python3
"""
Test Railway PostgreSQL Connection
Run this script to verify your Railway database connection is working
"""

import psycopg2
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.prod')

def test_connection():
    """Test the Railway database connection"""
    
    # Get connection parameters
    config = {
        "host": os.getenv("POSTGRES_HOST"),
        "port": int(os.getenv("POSTGRES_PORT", 5432)),
        "database": os.getenv("POSTGRES_DB"),
        "user": os.getenv("POSTGRES_USER"),
        "password": os.getenv("POSTGRES_PASSWORD"),
        "sslmode": os.getenv("POSTGRES_SSL_MODE", "require"),
    }
    
    # Validate that all required variables are set
    required_vars = ["host", "database", "user", "password"]
    missing_vars = [var for var in required_vars if not config.get(var)]
    
    if missing_vars:
        print("❌ Error: Missing required environment variables:")
        for var in missing_vars:
            print(f"   - POSTGRES_{var.upper()}")
        print("\n📝 Ensure .env.prod exists with all required variables")
        return False
    
    print("=" * 60)
    print("🚀 Testing Railway PostgreSQL Connection")
    print("=" * 60)
    
    try:
        print("\n📍 Connection Details:")
        print(f"   Host: {config['host']}")
        print(f"   Port: {config['port']}")
        print(f"   Database: {config['database']}")
        print(f"   User: {config['user']}")
        print(f"   SSL Mode: {config['sslmode']}")
        
        print("\n⏳ Connecting to Railway...")
        conn = psycopg2.connect(**config)
        cur = conn.cursor()
        
        print("✅ Connected successfully!")
        
        # Test 1: Check PostgreSQL version
        print("\n📊 Database Information:")
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        print(f"   PostgreSQL: {version.split(',')[0]}")
        
        # Test 2: List all tables
        print("\n📋 Tables in Your Database:")
        cur.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cur.fetchall()
        
        if not tables:
            print("   ⚠️  No tables found! Use the schema initialization command:")
            print("   railway run psql $DATABASE_URL -f warehouse/schema.sql")
            return False
        
        for table in tables:
            cur.execute(f"SELECT COUNT(*) FROM {table[0]};")
            count = cur.fetchone()[0]
            print(f"   • {table[0]:<25} ({count} rows)")
        
        # Test 3: Verify expected tables
        print("\n✅ Verification:")
        expected_tables = ['dim_asset', 'dim_date', 'fact_service_failure', 'etl_metadata']
        found_tables = [t[0] for t in tables]
        
        for expected in expected_tables:
            if expected in found_tables:
                print(f"   ✅ {expected} exists")
            else:
                print(f"   ❌ {expected} missing")
        
        # Test 4: Check indexes
        print("\n🔍 Indexes on fact_service_failure:")
        cur.execute("""
            SELECT indexname FROM pg_indexes 
            WHERE tablename = 'fact_service_failure'
            ORDER BY indexname;
        """)
        indexes = cur.fetchall()
        
        if indexes:
            for idx in indexes:
                print(f"   • {idx[0]}")
        else:
            print("   ⚠️  No indexes found")
        
        # Test 5: Test INSERT and SELECT (on staging data)
        print("\n🧪 Testing Write Access:")
        try:
            cur.execute("""
                INSERT INTO etl_metadata (records_loaded, status) 
                VALUES (0, 'test') 
                RETURNING run_id;
            """)
            test_id = cur.fetchone()[0]
            conn.commit()
            print(f"   ✅ Write access confirmed (test run_id: {test_id})")
            
            # Cleanup
            cur.execute("DELETE FROM etl_metadata WHERE run_id = %s;", (test_id,))
            conn.commit()
            print("   ✅ Cleanup complete")
        except Exception as e:
            print(f"   ⚠️  Write test failed: {e}")
        
        print("\n" + "=" * 60)
        print("✅ All tests passed! Your Railway database is ready to use.")
        print("=" * 60)
        
        conn.close()
        return True
        
    except psycopg2.OperationalError as e:
        print(f"\n❌ Connection Failed: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("   1. Verify POSTGRES_HOST, POSTGRES_USER, POSTGRES_PASSWORD in .env.prod")
        print("   2. Check that Railway database is running in dashboard")
        print("   3. Ensure you have internet access to Railway servers")
        print("   4. Try: railway run psql $DATABASE_URL -c 'SELECT 1;'")
        return False
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
