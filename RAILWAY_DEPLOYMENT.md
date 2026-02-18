# Railway PostgreSQL Deployment Guide

A step-by-step guide to deploy your InfraPulse PostgreSQL database to Railway.app

---

## 📋 Overview

Your database includes these tables:
- `dim_asset` - Asset dimension table
- `dim_date` - Date dimension table
- `fact_service_failure` - Facts table with foreign keys
- `etl_metadata` - ETL run tracking
- Plus indexes on `fact_service_failure`

---

## **STEP 1: Create Railway Account**

### 1.1 Sign Up
1. Go to https://railway.app/
2. Click **"Sign in"** or **"Get Started"**
3. Choose signup method (GitHub, Google, or email)
4. Verify your email
5. Create a new project:
   - Click **"Create New Project"**
   - Select **"Provision PostgreSQL"**

---

## **STEP 2: Create PostgreSQL Database on Railway**

### 2.1 Configure Database
1. Railroad will create a PostgreSQL instance automatically
2. Once created, click on **"PostgreSQL"** in your project
3. Go to the **"Settings"** tab
4. Note your database name (default: `railway`)

### 2.2 Obtain Connection Details

Click the **"Connect"** tab and copy these values:

| Variable | Copy from | Example |
|----------|-----------|---------|
| `DATABASE_URL` | "Connection String (URI)" | `postgresql://user:password@host:5432/railway` |
| `POSTGRES_HOST` | Host field | `hostname.railway.app` |
| `POSTGRES_PORT` | Click "Edit" to see port | `5432` |
| `POSTGRES_DB` | Database name | `railway` |
| `POSTGRES_USER` | Username | `postgres` |
| `POSTGRES_PASSWORD` | Password field | (hidden, copy from Connection String) |

**⚠️ Save these securely! You'll need them for environment variables later.**

---

## **STEP 3: Initialize Your Database Schema**

### 3.1 Using Railway CLI (Recommended)

**Install Railway CLI:**
```bash
npm install -g @railway/cli
```

**Login to Railway:**
```bash
railway login
```

**Run your schema:**
```bash
railway run psql $DATABASE_URL -f warehouse/schema.sql
```

### 3.2 Using Direct psql Connection (Alternative)

If you have `psql` installed locally:

```bash
psql postgresql://user:password@hostname.railway.app:5432/railway -f warehouse/schema.sql
```

Replace with your actual connection details.

### 3.3 Verify Schema Was Created

```bash
railway run psql $DATABASE_URL -c "\dt"
```

You should see:
```
           List of relations
 Schema |          Name          | Type  
--------+------------------------+-------
 public | dim_asset              | table
 public | dim_date               | table
 public | etl_metadata           | table
 public | fact_service_failure   | table
(4 rows)
```

---

## **STEP 4: Set Up Environment Variables**

### 4.1 Create `.env.prod` File

In your project root, create a new file `.env.prod`:

```bash
cat > .env.prod << 'EOF'
# Railway PostgreSQL Connection
POSTGRES_HOST=your-hostname.railway.app
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password_here
POSTGRES_DB=railway
DATABASE_URL=postgresql://postgres:your_password_here@your-hostname.railway.app:5432/railway

# Airflow Configuration (if using Airflow)
AIRFLOW_HOME=/home/airflow/gce
AIRFLOW__CORE__DAGS_FOLDER=/home/airflow/gce/dags
AIRFLOW__CORE__LOAD_EXAMPLES=False
AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql://postgres:your_password_here@your-hostname.railway.app:5432/railway

# SSL Configuration (Railway requires SSL)
POSTGRES_SSL_MODE=require
EOF
```

### 4.2 Add to `.gitignore` (if not already present)

```bash
echo ".env.prod" >> .gitignore
```

---

## **STEP 5: Test Connection Locally**

### 5.1 Test with Python

Create a test file `test_railway_connection.py`:

```python
import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables from .env.prod
load_dotenv('.env.prod')

try:
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        database=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        sslmode="require"  # Required for Railway
    )
    
    cur = conn.cursor()
    cur.execute("SELECT * FROM dim_asset LIMIT 1;")
    result = cur.fetchone()
    
    print("✅ Connection successful!")
    print(f"✅ Database: {cur.description}")
    
    cur.execute("SELECT COUNT(*) FROM dim_asset;")
    count = cur.fetchone()
    print(f"✅ dim_asset table exists with {count[0]} records")
    
    cur.execute("SELECT COUNT(*) FROM fact_service_failure;")
    count = cur.fetchone()
    print(f"✅ fact_service_failure table exists with {count[0]} records")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Connection failed: {e}")
    exit(1)
```

Run the test:
```bash
pip install python-dotenv psycopg2-binary
python test_railway_connection.py
```

### 5.2 Test with psql Command

```bash
psql postgresql://postgres:your_password@hostname.railway.app:5432/railway -c "SELECT COUNT(*) FROM dim_asset;"
```

---

## **STEP 6: Update Your Code for Railway**

### 6.1 Update `etl/load.py`

Ensure it uses environment variables with SSL support:

```python
import psycopg2
import os
from elt_logger import log_info, log_error

def load_failures(df):
    """Load failures to PostgreSQL warehouse"""
    
    conn_params = {
        "host": os.getenv("POSTGRES_HOST"),
        "port": int(os.getenv("POSTGRES_PORT", 5432)),
        "database": os.getenv("POSTGRES_DB"),
        "user": os.getenv("POSTGRES_USER"),
        "password": os.getenv("POSTGRES_PASSWORD"),
        "sslmode": os.getenv("POSTGRES_SSL_MODE", "require"),  # Required for Railway
    }
    
    try:
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()
        
        # Insert logic here
        for index, row in df.iterrows():
            cur.execute("""
                INSERT INTO fact_service_failure 
                (asset_key, date_key, failure_type, outage_minutes, resolved)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                row['asset_key'],
                row['date_key'],
                row['failure_type'],
                row['outage_minutes'],
                row['resolved']
            ))
        
        conn.commit()
        log_info(f"Loaded {len(df)} records to fact_service_failure")
        conn.close()
        
    except Exception as e:
        log_error(f"Load failed: {str(e)}")
        raise
```

### 6.2 Update `airflow/dags/infrapulse_etl_dag.py`

Add SSL support in your database connections:

```python
import psycopg2
import os

def verify_data():
    """Verify data loaded into PostgreSQL"""
    
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST"),
            port=int(os.getenv("POSTGRES_PORT", 5432)),
            database=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            sslmode=os.getenv("POSTGRES_SSL_MODE", "require"),  # Required for Railway
        )
        
        cur = conn.cursor()
        
        # Verify tables exist
        cur.execute("""
            SELECT COUNT(*) FROM fact_service_failure;
        """)
        
        count = cur.fetchone()[0]
        print(f"✅ Verified {count} records in fact_service_failure")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        raise
```

---

## **STEP 7: Database Interactions (Quick Reference)**

### Connect to Your Railway Database
```bash
psql railroad://postgres:password@hostname.railway.app:5432/railway
```

### Common Commands

**List all tables:**
```sql
\dt
```

**Check table structure:**
```sql
\d dim_asset;
\d fact_service_failure;
```

**Count records:**
```sql
SELECT COUNT(*) FROM fact_service_failure;
SELECT COUNT(*) FROM dim_asset;
```

**View last ETL run:**
```sql
SELECT * FROM etl_metadata ORDER BY run_id DESC LIMIT 5;
```

**Check indexes:**
```sql
\d fact_service_failure
```

---

## **STEP 8: Backup & Disaster Recovery**

### 8.1 Create a Local Backup
```bash
pg_dump postgresql://postgres:password@hostname.railway.app:5432/railway > backup.sql
```

### 8.2 Restore from Backup (if needed)
```bash
psql postgresql://postgres:password@hostname.railway.app:5432/railway < backup.sql
```

### 8.3 Enable Railway Backups
1. In Railway dashboard, go to PostgreSQL settings
2. Look for "Backups" tab
3. Enable automatic backups (if available on your plan)

---

## **STEP 9: Security Checklist**

- [ ] Never commit `.env.prod` to git (already in `.gitignore`)
- [ ] Use strong password (min 16 chars, mixed case, numbers, symbols)
- [ ] Enable SSL (`sslmode=require`) in all connections
- [ ] Restrict database access to known IPs if possible
- [ ] Rotate passwords every 90 days
- [ ] Monitor Railway logs for suspicious activity
- [ ] Use environment variables for all sensitive data
- [ ] Keep `.env.prod` file with restricted permissions:
  ```bash
  chmod 600 .env.prod
  ```

---

## **STEP 10: Monitor & Troubleshoot**

### Check Railway Logs
1. Go to Railway dashboard
2. Select your PostgreSQL database
3. Click **"Logs"** tab
4. View real-time connection and query logs

### Common Issues

**Issue: `FATAL: password authentication failed`**
- Verify POSTGRES_PASSWORD is correct
- Check spaces in password string
- Try copying password directly from Railway dashboard

**Issue: `SSL connection error`**
- Ensure `sslmode=require` in connection string
- Verify you're using Railway's hostname (not localhost)

**Issue: `Connection timeout`**
- Check Railway service status
- Verify your internet connection
- Try connecting from Railway CLI: `railway run psql $DATABASE_URL`

**Issue: `Table does not exist`**
- Verify schema was initialized: `railway run psql $DATABASE_URL -c "\dt"`
- Re-run schema if needed: `railway run psql $DATABASE_URL -f warehouse/schema.sql`

---

## **STEP 11: Next Steps**

After successful connection:

1. **Deploy Airflow** - Follow `DEPLOYMENT.md` for Airflow setup
2. **Load sample data** - Test ETL pipeline with actual data
3. **Monitor performance** - Check query logs and connection metrics
4. **Schedule DAGs** - Set up automatic ETL runs in Airflow
5. **Set up alerts** - Create alerts for failed connections or slow queries

---

## **Quick Summary**

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Select your project
railway link

# 4. Initialize schema
railway run psql $DATABASE_URL -f warehouse/schema.sql

# 5. Test connection
python test_railway_connection.py

# 6. You're done! 🎉
```

---

## **Contact & Support**

- Railway Docs: https://docs.railway.app/
- PostgreSQL Docs: https://www.postgresql.org/docs/
- Your schema file: `warehouse/schema.sql`
- Your ETL code: `etl/load.py`, `airflow/dags/infrapulse_etl_dag.py`

