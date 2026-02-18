# 🎯 Monitoring Quick Reference

**Print this or bookmark it for daily use.**

---

## 🔴 **If Something's Wrong**

| Problem | Where to Check | How to Fix |
|---------|---|---|
| DAG didn't run | Astronomer UI → Calendar | Check if deployment is "Running" |
| Task failed | DAG → Tree View → Task → Logs | See error in logs tab |
| No data loaded | Run `test_railway_connection.py` | Check ETL task logs |
| Connection error | DAG logs → verify_data task | Check POSTGRES_* environment variables |

---

## 📊 **Daily Monitoring (1 minute)**

```
1. Astronomer UI → infrapulse_etl DAG
2. Look for green checkmark in Calendar (today)
3. Green = Success ✅
4. Red = Failed ❌
5. No symbol = Not run yet ⏳
```

---

## 📈 **Weekly Deep Dive (5 minutes)**

```
1. Calendar View → Count green checks (should be 7/7)
2. Tree View → Check average runtime (should be <10 sec)
3. Railway Dashboard → Check storage usage (should be <100 MB)
4. Run test: python test_railway_connection.py
```

---

## 🔍 **Access Task Logs**

**In Astronomer UI:**
1. Click `infrapulse_etl` DAG name
2. Click "Tree View" (top menu)
3. Click any colored square (task)
4. Click "Logs" tab
5. See detailed execution output

**Example log output (with new logging):**
```
📖 Reading CSV file: /opt/airflow/data/staging/failures.csv
✅ Extracted 150 records from /opt/airflow/data/staging/failures.csv
📊 Columns: asset_id, start_time, end_time, failure_type, resolved

🔄 Starting transformation on 150 records
✅ Parsed timestamps
✅ Calculated outage_minutes (min: 5, max: 480, avg: 125)
✅ Created date key (range: 2026-02-15 to 2026-02-18)
✅ Transformation complete: 150 records ready for load

🔗 Connecting to PostgreSQL: crossover.proxy.rlwy.net:27399
✅ Connected to database: railway
📝 Loading 150 records to warehouse...
  📊 Progress: 50/150 records processed...
  📊 Progress: 100/150 records processed...
✅ Load complete!
  📊 Total records loaded: 150
  🏷️  New assets inserted: 3
  📅 New dates inserted: 2
  🏭 Fact records: 150
```

---

## 💾 **Database Query: Check Loads**

```bash
# SSH into Railway or use query tool
psql -h crossover.proxy.rlwy.net -U postgres -d railway
```

```sql
-- View last 10 ETL runs
SELECT etl_run_id, status, records_loaded, start_time, end_time 
FROM etl_metadata 
ORDER BY start_time DESC LIMIT 10;

-- View record growth by date
SELECT full_date, COUNT(*) as daily_records 
FROM fact_service_failure 
JOIN dim_date USING (date_key)
GROUP BY full_date 
ORDER BY full_date DESC;

-- Find problematic assets
SELECT asset_id, COUNT(*) as failure_count 
FROM fact_service_failure 
JOIN dim_asset USING (asset_key)
GROUP BY asset_id 
ORDER BY failure_count DESC;
```

---

## 📱 **Set Up Email Alerts**

**In Astronomer UI:**
1. Click your Deployment name
2. Go to **Alerts** section (left menu)
3. Click **"+ New Alert"**
4. Select **"DAG Failed"**
5. Choose **"infrapulse_etl"**
6. Set notification to **Email**
7. Add your email
8. Save

**You'll get alerts when:**
- 🔴 DAG fails to run
- 🔴 Any task fails
- 🔴 DAG takes >10 minutes

---

## 🆘 **Emergency Contacts**

| Issue | Resource |
|-------|----------|
| Airflow Questions | [Astronomer Docs](https://docs.astronomer.io/) |
| PostgreSQL Questions | [Railway Docs](https://docs.railway.app/) |
| ETL Logic | Check [MONITORING_SETUP.md](MONITORING_SETUP.md) |
| Code Issues | Check task logs in Airflow UI |

---

## ✅ **Pre-Flight Checklist Runs**

Before deploying code changes:

```
[ ] All 4 tasks have green checkmarks
[ ] Latest run completed within 24 hours
[ ] No red ❌ errors in calendar
[ ] Database record count increased
[ ] No NULL values in fact_service_failure
[ ] Outage minutes range is reasonable (5-480)
```

---

## 🔔 **Performance Targets**

| Metric | Target | Status |
|--------|--------|--------|
| DAG Success Rate | >95% | ✅ |
| Average Runtime | <10 seconds | ✅ |
| Data Freshness | <24 hours old | ✅ |
| Zero Failures | Per week | ✅ |

---

**For full details, see:** [MONITORING_SETUP.md](MONITORING_SETUP.md)
