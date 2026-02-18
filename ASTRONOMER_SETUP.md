# Astronomer Deployment Configuration Guide

## **Deployment Overview**

Your InfraPulse ETL pipeline will run on Astronomer's managed Airflow infrastructure with your Railway PostgreSQL database.

---

## **Architecture**

```
Your Local Machine (this computer)
        ↓
  DAGs & Dependencies (Dockerfile)
        ↓
   Git Repository (or manual upload)
        ↓
   Astronomer Platform (Cloud)
        ↓
  Airflow Webserver & Scheduler
        ↓
   Railway PostgreSQL Database
   (crossover.proxy.rlwy.net:27399)
```

---

## **Prerequisites Checklist**

✅ Railway PostgreSQL database created
✅ `.env.prod` file with Railway credentials
✅ DAGs in `airflow/dags/` directory
✅ ETL modules in `etl/` directory
✅ `requirements.txt` with dependencies
✅ `Dockerfile` configured
✅ `.astronomerignore` file created

---

## **Part 1: Create Astronomer Account**

1. Go to: https://www.astronomer.io/
2. Click **"Start Free"** or **"Sign Up"**
3. Use GitHub or email signup (GitHub recommended)
4. Complete verification
5. You'll land on Astronomer Dashboard

✅ **You now have an Astronomer account**

---

## **Part 2: Create Workspace**

A workspace is a container for your deployments.

1. On Astronomer Dashboard, click **"Create New Workspace"**
2. Enter: `infrapulse`
3. Click **"Create"**
4. Wait for workspace to be ready (usually instant)

✅ **Workspace "infrapulse" is created**

---

## **Part 3: Create Deployment**

A deployment is your Airflow instance.

1. Inside your "infrapulse" workspace, click **"Create Deployment"**
2. Fill in these details:
   - **Deployment Name:** `infrapulse-prod`
   - **Region:** Choose closest to your data (e.g., `us-east-1` for Eastern US)
   - **Executor Type:** `Celery` (recommended for production)
   - **Stack Version:** `6.0.0` or latest
   - **Environment:** Select your namespace

3. Click **"Create Deployment"**
4. **Wait 2-3 minutes** for deployment to initialize

You'll see:
```
✅ Deployment Status: Running
🌐 Webserver URL: https://something.astronomer.run
🔐 API Token: (you'll need to set this up next)
```

✅ **Deployment created and running**

---

## **Part 4: Get Deployment Connection Details**

Once deployment is running:

1. Click on your deployment ("infrapulse-prod")
2. Click the **"Settings"** tab
3. Note these values:
   - **Deployment ID**: `abc123...` (copy this)
   - **Webserver URL**: `https://...astronomer.run` (save this)

4. Click **"API Token"** section
5. Click **"Generate API Token"**
6. A token will appear (looks like: `abcdef123456...`)
7. **Copy and save this token** - you'll use it to deploy DAGs

✅ **You have deployment credentials**

---

## **Part 5: Set Environment Variables in Astronomer**

This connects Astronomer's Airflow to your Railway database.

1. In deployment settings, scroll to **"Environment Variables"**
2. Click **"Add Environment Variable"**
3. Add these variables one by one:

| Variable Name | Value |
|---------------|-------|
| `POSTGRES_HOST` | `crossover.proxy.rlwy.net` |
| `POSTGRES_PORT` | `27399` |
| `POSTGRES_DB` | `railway` |
| `POSTGRES_USER` | `postgres` |
| `POSTGRES_PASSWORD` | `CTlwdjWtjhzRkWmYCMxssBkgcDEMrOpN` |
| `POSTGRES_SSL_MODE` | `require` |

⚠️ **Mark `POSTGRES_PASSWORD` as "Secret" so it's encrypted**

For each variable:
1. Enter **Variable Name** (e.g., `POSTGRES_HOST`)
2. Enter **Value** 
3. If it's a password, check **"Secret"** checkbox
4. Click **"Add"**

Repeat for all 6 variables.

✅ **Environment variables configured**

---

## **Part 6: Deploy Your DAGs**

### **Option A: Using Git Repository (Recommended)**

1. Push your code to GitHub:
   ```bash
   git init
   git remote add origin https://github.com/YOUR_USERNAME/infrapulse.git
   git add .
   git commit -m "Initial Astronomer deployment"
   git push -u origin main
   ```

2. In Astronomer Deployment Settings:
   - Click **"DAG Deployment"** tab
   - Select **"Repository"** option
   - Connect your GitHub repository
   - Astronomer will auto-sync DAGs

### **Option B: Using Command Line (If CLI works)**

```bash
astro login
astro deployment list
astro deploy --deployment-id=YOUR_DEPLOYMENT_ID
```

### **Option C: Manual Upload via Web UI**

1. On your deployment, click **"File Manager"**
2. Drag-and-drop your `airflow/dags/` files
3. Upload your ETL modules to `plugins/` folder

✅ **DAGs deployed to Astronomer**

---

## **Part 7: Verify Deployment**

1. Visit your **Webserver URL**: `https://...astronomer.run`
2. You should see Airflow UI
3. Login with the credentials you set in Astronomer setup
4. You should see your DAGs listed:
   - `infrapulse_etl_dag`

5. Click on your DAG to view details
6. Look for:
   - DAG Status: ✅ Green (Running normally)
   - Latest Run: Shows recent runs
   - No errors in Logs

---

## **Part 8: Trigger Your First DAG Manual Run**

1. In Airflow UI, find your DAG: `infrapulse_etl_dag`
2. Click the DAG name
3. Click **"Trigger DAG"** button
4. Optional: Add configuration/notes
5. Click **"Trigger"**

You'll see:
```
✅ DAG triggered
📊 Run started at: 2026-02-17 10:30:00
```

Monitor the run:
1. Click on the dag run (shown as a row)
2. Watch the tasks progress: extract → transform → load → verify
3. ✅ All tasks should complete with green checkmarks
4. ✅ Data should be in your Railway database

---

## **Part 9: Set Up DAG Schedule (Optional)**

To run your DAG on a schedule:

1. In your Airflow UI, click your DAG
2. Click **"Unpause"** to enable scheduling
3. Your DAG will run on its schedule (check `infrapulse_etl_dag.py` for cron expression)

Default: Runs daily at midnight UTC

---

## **Troubleshooting**

### DAG Not Showing in Airflow

**Problem:** You don't see `infrapulse_etl_dag` in the DAGs list

**Solutions:**
1. Refresh the page (F5)
2. Check DAG parsing errors:
   - Click **"Admin"** → **"DAGs"**
   - Look for red warnings
3. Check file permissions on DAGs folder
4. Ensure DAG file is in correct location: `airflow/dags/infrapulse_etl_dag.py`

### DAG Fails to Run

**Problem:** DAG starts but tasks fail

**Solutions:**
1. Check environment variables are set correctly:
   - Click deployment → Settings → Environment Variables
   - Verify all POSTGRES_* variables are present
2. Check task logs:
   - Click failing task
   - View logs from all attempts
3. Verify Railway database is accessible:
   - Run: `python test_railway_connection.py` locally
4. Check connection string:
   - Ensure POSTGRES_PASSWORD is correct (copy from Railway dashboard again if needed)

### Connection Timeout

**Problem:** `timeout: the server did not respond`

**Solution:**
- Railway database might be sleeping or unreachable
- Check Railway dashboard: PostgreSQL should show "Running"
- Verify POSTGRES_HOST is correct
- Check SSL MODE is set to `require`

### No Data in Database After Pipeline Runs

**Problem:** DAG runs successfully but no data in Railway

**Solutions:**
1. Check that your CSV files exist in the correct location
2. Verify extract phase is reading files: Check logs
3. Verify load phase is writing: Check logs for "Loaded X records"
4. Manually query database: `python test_railway_connection.py`

---

## **Next Steps**

After successful deployment:

1. **Monitor Airflow:** Check for failed runs in Airflow UI
2. **Setup Alerts:** Configure email alerts for DAG failures
3. **Schedule Runs:** Set DAG schedule (daily, hourly, etc.)
4. **Monitor Database:** Check Railway dashboard for performance
5. **Setup Backups:** Enable automatic backups in Railway

---

## **Quick Commands for Local Testing**

Before deploying to Astronomer, test locally:

```bash
# Test Railway connection
python test_railway_connection.py

# Test ETL pipeline
python -c "
import sys
sys.path.insert(0, 'etl')
from extract import extract_failures
from transform import transform_failures  
from load import load_failures

df = extract_failures('data/raw/2026-02-15/failures.csv')
df = transform_failures(df)
load_failures(df)
print('✅ Pipeline successful')
"

# Start Airflow locally with Railway
docker-compose --env-file .env.prod up -d
# Then access at http://localhost:8080
```

---

## **Support Resources**

- **Astronomer Docs:** https://docs.astronomer.io/
- **Airflow Docs:** https://airflow.apache.org/docs/
- **Railway Docs:** https://docs.railway.app/
- **Your Files:**
  - `.env.prod` - Your Railway credentials
  - `airflow/dags/infrapulse_etl_dag.py` - Your DAG
  - `Dockerfile` - Custom build
  - `.astronomerignore` - Files to exclude

---

## **Checklist Summary**

- [ ] Astronomer account created
- [ ] Workspace "infrapulse" created
- [ ] Deployment "infrapulse-prod" created and running
- [ ] All 6 environment variables set in Astronomer
- [ ] DAGs deployed (via Git, CLI, or Web UI)
- [ ] Airflow UI accessible
- [ ] DAG visible in Airflow UI
- [ ] First manual run completed successfully
- [ ] Data appears in Railway database
- [ ] Schedule configured (if desired)

---

**You're ready to deploy to Astronomer! 🚀**
