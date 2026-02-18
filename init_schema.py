#!/usr/bin/env python3
"""
Initialize Railway PostgreSQL Schema
This script reads warehouse/schema.sql and executes it
"""

import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables from .env.prod
load_dotenv('.env.prod')

def init_schema():
    """Initialize the database schema"""
    
    config = {
        "host": os.getenv("POSTGRES_HOST"),
        "port": int(os.getenv("POSTGRES_PORT", 5432)),
        "database": os.getenv("POSTGRES_DB"),
        "user": os.getenv("POSTGRES_USER"),
        "password": os.getenv("POSTGRES_PASSWORD"),
        "sslmode": os.getenv("POSTGRES_SSL_MODE", "require"),
    }
    
    print("=" * 60)
    print("🚀 Initializing Railway PostgreSQL Schema")
    print("=" * 60)
    
    try:
        print("\n📍 Connection Details:")
        print(f"   Host: {config['host']}")
        print(f"   Port: {config['port']}")
        print(f"   Database: {config['database']}")
        
        print("\n⏳ Connecting to Railway...")
        conn = psycopg2.connect(**config)
        cur = conn.cursor()
        
        print("✅ Connected!")
        
        # Read schema file
        print("\n📄 Reading schema.sql...")
        with open('warehouse/schema.sql', 'r') as f:
            schema = f.read()
        
        print(f"   ✅ Schema file loaded ({len(schema)} bytes)")
        
        # Execute schema
        print("\n⚙️  Executing schema...")
        cur.execute(schema)
        conn.commit()
        
        print("✅ Schema executed successfully!")
        
        # Verify tables were created
        print("\n📋 Verifying tables...")
        cur.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cur.fetchall()
        
        print(f"\n✅ Created {len(tables)} tables:")
        for table in tables:
            cur.execute(f"SELECT COUNT(*) FROM {table[0]};")
            count = cur.fetchone()[0]
            print(f"   • {table[0]:<30} ({count} rows)")
        
        # Check indexes
        print("\n🔍 Verifying indexes...")
        cur.execute("""
            SELECT indexname FROM pg_indexes 
            WHERE tablename = 'fact_service_failure'
            ORDER BY indexname;
        """)
        indexes = cur.fetchall()
        
        if indexes:
            print(f"   ✅ Found {len(indexes)} indexes on fact_service_failure:")
            for idx in indexes:
                print(f"      • {idx[0]}")
        
        print("\n" + "=" * 60)
        print("✅ Schema initialization complete!")
        print("=" * 60)
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = init_schema()
    exit(0 if success else 1)
