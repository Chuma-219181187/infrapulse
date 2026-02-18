# Railway PostgreSQL: Visual Step-by-Step Walkthrough

Follow these exact steps with screenshots (you'll click through each one)

---

## **Step 1: Create Railway Account**

1. Go to https://railway.app/
2. Click **"Get Started"** or **"Sign in"**
3. Choose authentication method (GitHub recommended - easier)
4. Authorize Railway on GitHub
5. Accept terms and complete signup

✅ **You now have a Railway account**

---

## **Step 2: Create PostgreSQL Database**

### Option A: From Scratch (New Project)
1. On Railway dashboard, click **"Create New Project"**
2. Select **"Provision PostgreSQL"**
3. Wait for PostgreSQL to initialize (30 seconds)
4. When complete, you'll see PostgreSQL in your project

### Option B: Add to Existing Project
1. Click **"Create New"** → **"Database"** → **"PostgreSQL"**
2. Select region closest to your location
3. Wait for initialization

✅ **PostgreSQL is now created and running**

---

## **Step 3: Get Connection Credentials**

This is critical - you'll need these values!

1. In your Railway project, click **"PostgreSQL"**
2. Click the **"Connect"** tab
3. You'll see different connection options:

### Copy These Values:

**Option 1: Full Connection String (Easiest)**
```
Click "Copy" next to the full PostgreSQL URI
Example: postgresql://postgres:password@hostname.railway.app:5432/railway
```

**Option 2: Individual Values (if needed)**
- **Host**: `hostname.railway.app`
- **Port**: `5432`
- **Database**: `railway` (or your chosen name)
- **User**: `postgres`
- **Password**: Visible in the Connection String

4. **Save these somewhere safe** (password manager, encrypted file, etc.)

✅ **You have all connection credentials**

---

## **Step 4: Create .env.prod File**

1. In your project directory, create a new file: `.env.prod`

2. Copy and paste this template:

```bash
# Railway PostgreSQL Configuration
POSTGRES_HOST=hostname.railway.app
POSTGRES_PORT=5432
POSTGRES_DB=railway
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password_from_step3
DATABASE_URL=postgresql://postgres:your_password@hostname.railway.app:5432/railway
POSTGRES_SSL_MODE=require
```

3. Replace the values with your actual Railway credentials from Step 3

4. **Save the file** (⚠️ Never commit to git!)

✅ **Your environment variables are configured**

---

## **Step 5: Verify .gitignore Protection**

Make sure `.env.prod` is never committed to Git:

1. Open `.gitignore` in your project root
2. Verify it contains: `.env.prod`
3. If not, add it

```bash
# .gitignore should have this line:
.env.prod
```

✅ **Your credentials are protected**

---

## **Step 6: Install Required Tools**

These are one-time installations:

### Option A: Using Railway CLI (Recommended)

```bash
npm install -g @railway/cli
railway login
```

### Option B: Using psql (if you have PostgreSQL installed)

```bash
# macOS
brew install postgresql

# Windows (use PostgreSQL installer or Scoop)
scoop install postgresql

# Linux
sudo apt-get install postgresql-client
```

✅ **Required tools are installed**

---

## **Step 7: Test Connection**

Run the Python test script I created for you:

```bash
# First, install the test dependencies (one time)
pip install psycopg2-binary python-dotenv

# Run the test
python test_railway_connection.py
```

**Expected Output:**
```
============================================================
🚀 Testing Railway PostgreSQL Connection
============================================================

📍 Connection Details:
   Host: hostname.railway.app
   Port: 5432
   Database: railway
   User: postgres
   SSL Mode: require

⏳ Connecting to Railway...
✅ Connected successfully!

📊 Database Information:
   PostgreSQL: PostgreSQL 14.x

📋 Tables in Your Database:
   ⚠️  No tables found! Use the schema initialization command...
```

⚠️ **If this fails**, check:
- Is `POSTGRES_HOST` correct? (Copy-paste from Railway dashboard)
- Is `POSTGRES_PASSWORD` correct? (Copy exactly from connection string)
- Do you have internet? (Railway runs in cloud, needs connection)

✅ **Connection is working!**

---

## **Step 8: Initialize Your Database Schema**

This creates all your tables (dim_asset, dim_date, fact_service_failure, etl_metadata)

### Using Railway CLI (Easiest)

```bash
# Make sure you're in the project directory
cd /path/to/infrapulse

# Initialize the schema
railway run psql $DATABASE_URL -f warehouse/schema.sql
```

### Using Direct psql (Alternative)

```bash
psql postgresql://postgres:password@hostname.railway.app:5432/railway -f warehouse/schema.sql
```

Replace `password` and `hostname` with your actual values.

**Expected Output:**
```
CREATE TABLE
CREATE TABLE
CREATE TABLE
CREATE TABLE
CREATE INDEX
CREATE INDEX
```

✅ **Schema is now initialized**

---

## **Step 9: Verify All Tables Exist**

```bash
# Using Railway CLI
railway run psql $DATABASE_URL -c "\dt"
```

**Expected Output:**
```
          List of relations
 Schema |       Name          | Type  
--------+---------------------+-------
 public | dim_asset           | table
 public | dim_date            | table
 public | etl_metadata        | table
 public | fact_service_failure| table
(4 rows)
```

✅ **All 4 tables are created**

---

## **Step 10: Test Writing Data**

Make sure you can insert data:

```bash
railway run psql $DATABASE_URL -c "INSERT INTO dim_asset (asset_id, asset_type, service_type, location) VALUES ('TEST-001', 'Server', 'Web', 'DataCenter-1');"
```

**Expected Output:**
```
INSERT 0 1
```

Then verify it was inserted:

```bash
railway run psql $DATABASE_URL -c "SELECT * FROM dim_asset WHERE asset_id='TEST-001';"
```

✅ **Read and write access confirmed**

---

## **Step 11: Update Your ETL Code**

Now that Railway is set up, update your Python ETL code to use these environment variables.

### Update `etl/load.py`

Make sure it uses environment variables with SSL:

```python
import psycopg2
import os

def load_failures(df):
    conn_params = {
        "host": os.getenv("POSTGRES_HOST"),
        "port": int(os.getenv("POSTGRES_PORT", 5432)),
        "database": os.getenv("POSTGRES_DB"),
        "user": os.getenv("POSTGRES_USER"),
        "password": os.getenv("POSTGRES_PASSWORD"),
        "sslmode": os.getenv("POSTGRES_SSL_MODE", "require"),
    }
    
    conn = psycopg2.connect(**conn_params)
    # ... rest of your code
```

### Update `airflow/dags/infrapulse_etl_dag.py`

Same pattern for Airflow connections:

```python
def verify_data():
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=int(os.getenv("POSTGRES_PORT", 5432)),
        database=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        sslmode=os.getenv("POSTGRES_SSL_MODE", "require"),
    )
    # ... rest of your code
```

✅ **Code is updated for Railway**

---

## **Step 12: Final Verification**

Run your complete test again:

```bash
python test_railway_connection.py
```

**Expected Output:**
```
============================================================
✅ All tests passed! Your Railway database is ready to use.
============================================================
```

✅ **Everything is working!**

---

## **Troubleshooting Guide**

### ❌ Problem: `Connection refused`
**Solution:**
- Check `POSTGRES_HOST` in `.env.prod`
- Go to Railway dashboard → PostgreSQL → Connect tab
- Copy the HOST value exactly (including domain)
- Re-test with `python test_railway_connection.py`

### ❌ Problem: `FATAL: password authentication failed`
**Solution:**
- Your password is wrong
- Go to Railway dashboard → PostgreSQL → Connect
- Find the full Connection String
- Extract the password from: `postgresql://postgres:PASSWORD@host...`
- Copy the PASSWORD part exactly (including special characters)
- Update `.env.prod`

### ❌ Problem: `psql: command not found`
**Solution:**
- Use Railway CLI instead: `railway run psql` or `npm install -g @railway/cli`
- OR install PostgreSQL client tools locally

### ❌ Problem: `relation "dim_asset" does not exist`
**Solution:**
- Your schema wasn't initialized
- Run: `railway run psql $DATABASE_URL -f warehouse/schema.sql`
- Verify with: `railway run psql $DATABASE_URL -c "\dt"`

### ❌ Problem: `Network error: Connection timeout`
**Solution:**
- Check your internet connection
- Railway service might be down (check status.railway.app)
- Try again in a few minutes
- Check if your firewall blocks outbound connections to Railway

---

## **Quick Command Reference**

```bash
# List all tables
railway run psql $DATABASE_URL -c "\dt"

# Count records in a table
railway run psql $DATABASE_URL -c "SELECT COUNT(*) FROM fact_service_failure;"

# View one row
railway run psql $DATABASE_URL -c "SELECT * FROM dim_asset LIMIT 1;"

# Delete test data
railway run psql $DATABASE_URL -c "DELETE FROM dim_asset WHERE asset_id='TEST-001';"

# View all fields/indexes of a table
railway run psql $DATABASE_URL -c "\d fact_service_failure"

# Check database size
railway run psql $DATABASE_URL -c "SELECT pg_size_pretty(pg_database_size('railway'));"

# Connect interactively (for multiple commands)
railway run psql $DATABASE_URL
# Then type SQL commands
# Type \q to exit
```

---

## **Success Checklist**

- [ ] Railway account created
- [ ] PostgreSQL database created
- [ ] Connection credentials copied
- [ ] `.env.prod` file created
- [ ] `.env.prod` protected in `.gitignore`
- [ ] `python test_railway_connection.py` passes ✅
- [ ] Schema initialized (all 4 tables exist)
- [ ] Can insert test data
- [ ] Can query data
- [ ] ETL code updated with env variables
- [ ] Ready for next step (Airflow deployment)

---

## **Next Steps**

Once the database is working:
1. Deploy Airflow (see [DEPLOYMENT.md](./DEPLOYMENT.md))
2. Load real production data
3. Set up monitoring
4. Schedule automated runs

**Congratulations! Your Railway PostgreSQL database is ready! 🎉**

---

## **Getting Help**

- 📖 Full Guide: [RAILWAY_DEPLOYMENT.md](./RAILWAY_DEPLOYMENT.md)
- ⚡ Quick Ref: [RAILWAY_QUICK_REFERENCE.md](./RAILWAY_QUICK_REFERENCE.md)
- 🏗️ Architecture: [RAILWAY_ARCHITECTURE.md](./RAILWAY_ARCHITECTURE.md)
- 📋 Checklist: [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md)
- 🌐 Railway Support: https://docs.railway.app/
