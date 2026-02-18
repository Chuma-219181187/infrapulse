# 📊 Monitoring & Logging Setup Guide

Your Astronomer Airflow + Railway PostgreSQL infrastructure is now running. This guide shows you how to monitor pipeline health, access logs, and set up alerts.

---

## 🚀 **Quick Start: Access Logs (2 minutes)**

### 1. **View DAG Execution in Astronomer UI**

1. Open your **Astronomer Webserver URL**
2. Click **"infrapulse_etl"** DAG
3. You'll see:
   - **Graph View**: Visual task pipeline
   - **Tree View**: All past executions
   - **Calendar**: Color-coded execution history (green=success, red=failed)

### 2. **View Task Logs**

**For a specific task:**
1. Click **"infrapulse_etl"** DAG
2. Click **"Tree View"** (top menu)
3. Click any **task instance** (appears as a square)
4. Click **"Logs"** tab
5. See full execution output and any errors

**Example task log output:**
```
[2026-02-18 10:30:15,123] {extract.py:25} INFO - Reading CSV: /opt/airflow/data/staging/failures.csv
[2026-02-18 10:30:16,456] {transform.py:42} INFO - Transformed 150 records
[2026-02-18 10:30:17,789] {load.py:58} INFO - Loaded 150 records to fact_service_failure
[2026-02-18 10:30:19,234] {quality_checks.py:31} INFO - ✓ All data verification checks passed!
```

---

## 📋 **Monitoring Checklist**

### Daily Checks (1 minute)

```bash
# Check latest DAG run status
# In Astronomer UI:
# 1. Open Dashboard (top left)
# 2. Look for "infrapulse_etl" in Recent Runs
# 3. Green checkmark = Success ✅
# 4. Red X = Failed ❌
# 5. Blue circle = Running 🔄
```

### Weekly Health Review (5 minutes)

| Metric | Where to Check | Target |
|--------|---|---|
| Success Rate | Calendar view (green percentage) | >95% |
| Avg Runtime | Tree View (check timestamps) | <5 min |
| Failed Tasks | Red in Calendar | 0 failures |
| Latest Run | Tree View (top row) | Within 24 hrs |

---

## 🔍 **Detailed Logging Access**

### **Level 1: DAG-Level Logs**

Shows high-level execution flow:

1. Astronomer UI → **infrapulse_etl** DAG
2. Click **"Logs"** tab
3. See when DAG started/stopped, which tasks ran

**Example output:**
```
[2026-02-18 10:30:10] DAG scheduled
[2026-02-18 10:30:10] Executing ingest_files task
[2026-02-18 10:30:12] ingest_files completed: 150 files ingested
[2026-02-18 10:30:12] Executing run_etl task
[2026-02-18 10:30:17] run_etl completed: 150 records transformed
[2026-02-18 10:30:17] Executing verify_data task
[2026-02-18 10:30:19] verify_data completed: All checks passed
[2026-02-18 10:30:19] DAG execution completed successfully
```

### **Level 2: Task-Level Logs** (More detailed)

Shows what each Python function did:

1. DAG → **Tree View**
2. Click task square (e.g., `run_etl`)
3. Click **"Logs"**
4. See ETL module execution:

```
[02-18 10:30:12,123] Reading CSV: failures.csv
[02-18 10:30:12,456] - Loaded 150 rows from CSV
[02-18 10:30:13,789] Transforming data
[02-18 10:30:14,234] - Cleaned asset IDs (null count: 0)
[02-18 10:30:14,567] - Calculated outage_minutes (range: 5-480)
[02-18 10:30:15,890] Connecting to Railway PostgreSQL
[02-18 10:30:16,123] Inserting records
[02-18 10:30:16,456] - Inserted 150 records into fact_service_failure
[02-18 10:30:17,789] ✓ All data verification checks passed!
```

### **Level 3: Raw Container Logs** (Astronomer Advanced)

See everything the container did (includes system messages):

1. Astronomer Dashboard → **Deployment Settings**
2. Scroll to **"Logs"** section
3. See: Python output, scheduler, webserver, triggerer logs

---

## 🛡️ **Monitoring Your Data Pipeline**

### **Check 1: Is Data Fresh?** (Run weekly)

```bash
cd "c:\Users\iceik\Desktop\CAPACITY__X__PROJECT Y\infrapulse\infrapulse"
python test_railway_connection.py
```

**Expected output:**
```
fact_service_failure: ### rows  ← Should increase after each DAG run
etl_metadata: SUCCESS runs    ← Should increment
dim_asset: Asset count         ← Should be consistent
dim_date: Date range           ← Should expand
```

### **Check 2: Data Quality** (Built into DAG)

The `verify_data` task automatically checks:

| Check | What it verifies | Pass condition |
|-------|---|---|
| **Record Count** | Data was loaded | >0 records |
| **Null Assets** | No empty asset IDs | 0 nulls ✅ |
| **Negative Outages** | No invalid durations | 0 negatives ✅ |
| **Orphaned Records** | All records have assets | 0 orphans ✅ |
| **Sample Data** | Data structure correct | Sample retrieved ✅ |

See results in task logs: `verify_data` task → **Logs** tab

### **Check 3: ETL Metadata** (Database-level tracking)

Your `etl_metadata` table tracks every run:

```sql
-- Query in Railway dashboard or psql
SELECT 
  etl_run_id,
  status,
  records_loaded,
  start_time,
  end_time,
  (EXTRACT(EPOCH FROM end_time - start_time))::int AS duration_seconds
FROM etl_metadata
ORDER BY start_time DESC
LIMIT 10;
```

Expected output:
```
etl_run_id | status  | records_loaded | start_time | end_time | duration
-----------|---------|----------------|-----------|----------|----------
10         | SUCCESS | 150            | 10:30:10  | 10:30:19 | 9
 9         | SUCCESS | 150            | daily     | ✅       | 8
 8         | SUCCESS | 150            | ✅        | ✅       | 9
```

---

## ⚠️ **Alert Setup** (Email on Failures)

### **Option 1: Astronomer Built-in Alerts** (Recommended)

1. Astronomer Dashboard → **Alerts** (left menu)
2. Click **"+ New Alert"**
3. Configure:
   - **Alert Type**: DAG failure
   - **DAG**: infrapulse_etl
   - **Notification**: Email
   - **Recipients**: your-email@example.com
4. Click **"Create"**

**You'll get emails when:**
- DAG fails to run
- A task fails
- DAG execution takes >10 minutes

### **Option 2: Manual Airflow Alerts** (Advanced)

Already configured in [airflow/dags/infrapulse_etl_dag.py](airflow/dags/infrapulse_etl_dag.py):

```python
default_args = {
    "owner": "data_engineer",
    "retries": 2,  # Retry failed tasks 2x
    "email_on_failure": True,  
    "email": ["your-email@example.com"]
}
```

**To enable:**
1. Edit `airflow/dags/infrapulse_etl_dag.py`
2. Add your email to `"email"` list
3. Commit and redeploy to Astronomer

---

## 📈 **Performance Monitoring**

### **View DAG Performance Metrics**

In Astronomer UI:

1. **infrapulse_etl** DAG → **Statistics** tab
2. See:
   - Total Runs: X
   - Success Rate: X%
   - Avg Duration: X sec
   - Latest Status: ✅/❌

### **Monitor Each Task**

1. **infrapulse_etl** DAG → **Graph View**
2. Hover over each task sphere
3. See: Status, duration, retries

**Expected timings:**
- `ingest_files`: <1 sec
- `run_etl`: 2-5 sec
- `verify_data`: 1-2 sec
- `archive_files`: <1 sec
- **Total**: 5-10 sec

---

## 🗄️ **Railway PostgreSQL Monitoring**

### **Check Database Performance**

1. Log into **Railway Dashboard**: https://railway.app
2. Click your **PostgreSQL** database
3. Under **"Monitoring"** tab, see:
   - **Connections**: Active database connections
   - **Storage**: Disk usage
   - **CPU/Memory**: Resource utilization

### **Query Database Directly**

```bash
# Connect from your local machine
psql -h crossover.proxy.rlwy.net -p 27399 -U postgres -d railway
```

**Useful monitoring queries:**

```sql
-- Check latest ETL run
SELECT * FROM etl_metadata ORDER BY start_time DESC LIMIT 1;

-- Count records by date
SELECT full_date, COUNT(*) FROM fact_service_failure 
JOIN dim_date USING (date_key)
GROUP BY full_date ORDER BY full_date DESC LIMIT 10;

-- Find problematic assets
SELECT asset_id, COUNT(*) FROM fact_service_failure 
JOIN dim_asset USING (asset_key)
GROUP BY asset_id ORDER BY COUNT(*) DESC;

-- Check for data anomalies
SELECT 
  'Min Outage (min)' as metric, MIN(outage_minutes)::text as value
  FROM fact_service_failure
UNION ALL
SELECT 'Max Outage (min)', MAX(outage_minutes)::text FROM fact_service_failure
UNION ALL
SELECT 'Avg Outage (min)', ROUND(AVG(outage_minutes), 2)::text FROM fact_service_failure;
```

---

## 👁️ **Dashboard - At-a-Glance Status**

Create this visual check in your browser bookmarks:

**Your Monitoring Dashboard URLs:**

| Metric | URL | Check |
|--------|-----|-------|
| Airflow UI | `https://infrapulse-xxxxx.airflow.astronomer.run` | DAG status, logs |
| Railway DB | `https://railway.app` | Database health, storage |
| This Guide | Keep this file handy | Reference |

---

## 🚨 **Troubleshooting Guide**

### **Scenario 1: DAG Didn't Run at Scheduled Time**

**Location:** Astronomer UI → Calendar
**Action:**
1. Check if deployment is "Running" (green status)
2. Check scheduler logs: Deployment → "Logs" → filter "scheduler"
3. Manually trigger DAG to verify (should work even if scheduler stopped)

### **Scenario 2: Task Failed** (Red in Calendar)

**Location:** DAG → Tree View → Click failed task → "Logs"
**Common causes:**
```
"Connection refused" 
  → Check POSTGRES_HOST, PORT in Variables
  → Verify Railway DB is running
  
"SSL error"
  → Ensure POSTGRES_SSL_MODE=require in Variables
  → Check Railway requires SSL

"No such file or directory"
  → Data file doesn't exist (normal if first run)
  → DAG handles this gracefully, should not fail
  
"NULL asset IDs found"
  → Data quality issue
  → Check CSV file for empty asset columns
```

### **Scenario 3: Data Not Loaded**

**Verification:**
```bash
cd "c:\Users\iceik\Desktop\CAPACITY__X__PROJECT Y\infrapulse\infrapulse"
python test_railway_connection.py
# Check if record counts increased
```

**Fix:** Manual trigger
1. Astronomer UI → infrapulse_etl → ▶ Trigger DAG
2. Wait 2-3 minutes for execution
3. Check logs in Task view

---

## 📝 **Weekly Maintenance Checklist**

```
[ ] Check DAG success rate (target: >95%)
[ ] Review log files for warnings
[ ] Verify record counts increased
[ ] Check Railway storage usage
[ ] Confirm latest run within 24 hours
[ ] Review any email alerts received
[ ] Test manually triggering DAG
[ ] Query etl_metadata for anomalies
```

---

## 🔗 **Reference: Log File Locations**

In Astronomer (managed), logs are stored in:
- **Scheduler logs**: Deployment settings → Logs
- **Webserver logs**: Deployment settings → Logs  
- **Task logs**: Airflow UI → DAG → Tree View → Task → Logs
- **Database logs**: Railway Dashboard → PostgreSQL → Monitoring

Local backup (if using Docker):
- `logs/dag_id=*/run_id=*/task_id=*/`

---

## ✅ **You're Monitoring-Ready!**

Your pipeline now has:
- ✅ Real-time task status in Astronomer UI
- ✅ Detailed logs at 3 levels (DAG, Task, Container)
- ✅ Automated data quality checks
- ✅ Database performance visibility
- ✅ Optional email alerts on failures

**Next steps:** Set up the email alerts, then monitor your first scheduled run! 🎉
