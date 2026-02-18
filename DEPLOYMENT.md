# InfraPulse Cloud Deployment Guide

This guide walks you through deploying the InfraPulse ETL pipeline to the cloud using Astronomer for Airflow and Render/Railway for PostgreSQL.

---

## **Step 1: Prepare Local Environment**

### **1.1 Create `.env` files**

- Local development: `.env` (already created)
- Production: Create `.env.prod` with secure credentials

```bash
cp .env.example .env.prod
# Edit .env.prod with production credentials
```

### **1.2 Build and Test Locally**

```bash
docker-compose --env-file .env up -d
docker-compose logs -f airflow
```

---

## **Step 2: Deploy PostgreSQL to Cloud**

### **Option A: Render.com**

1. **Create Render account** at https://render.com/

2. **Create PostgreSQL Database**:
   - Click "New +" → "PostgreSQL"
   - Name: `infrapulse-db`
   - Region: Choose closest to your users
   - PostgreSQL Version: 14
   - Plan: Standard tier (for production)

3. **Note these credentials** (save securely):
   - `POSTGRES_HOST` (external database URL)
   - `POSTGRES_USER`
   - `POSTGRES_PASSWORD`
   - `POSTGRES_DB` = `infrapulse`

4. **Initialize Schema**:
   ```bash
   psql -h <POSTGRES_HOST> -U <POSTGRES_USER> -d infrapulse -f warehouse/schema.sql
   ```

### **Option B: Railway.app**

1. **Create Railway account** at https://railway.app/

2. **Create PostgreSQL Database**:
   - Click "Create New" → "Database" → "PostgreSQL"
   - Region: Select closest region
   - Version: 14

3. **Get connection string** from Railway dashboard

4. **Initialize Schema**:
   ```bash
   psql <YOUR_DATABASE_URL> -f warehouse/schema.sql
   ```

---

## **Step 3: Update ETL Code for Cloud**

### **3.1 Modify `etl/load.py` for cloud database**

Replace hardcoded localhost connection with environment variables:

```python
import psycopg2
import os
from elt_logger import log_info, log_error

def load_failures(df):
    """Load failures to PostgreSQL warehouse (cloud-ready)"""
    
    # Use environment variables for cloud deployment
    conn_params = {
        "host": os.getenv("POSTGRES_HOST", "postgres"),  # localhost for local, cloud URL for production
        "database": os.getenv("POSTGRES_DB", "infrapulse"),
        "user": os.getenv("POSTGRES_USER"),
        "password": os.getenv("POSTGRES_PASSWORD"),
    }
    
    # Add SSL for cloud deployments
    if os.getenv("POSTGRES_SSL_MODE"):
        conn_params["sslmode"] = os.getenv("POSTGRES_SSL_MODE", "require")
    
    try:
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()
        
        # ... rest of the load logic remains the same
        
    except Exception as e:
        log_error(f"Connection failed: {str(e)}")
        raise
```

### **3.2 Modify `airflow/dags/infrapulse_etl_dag.py` for cloud**

Update the `verify_data()` function to use environment variables:

```python
def verify_data():
    """Verify data loaded into PostgreSQL (cloud-ready)"""
    
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "postgres"),
            database=os.getenv("POSTGRES_DB", "infrapulse"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
        )
        # ... rest of verification logic
```

---

## **Step 4: Deploy Airflow to Cloud**

### **Option A: Astronomer (Recommended)**

1. **Install Astronomer CLI**:
   ```bash
   brew install astro
   # or for Windows: download from https://www.astronomer.io/downloads/
   ```

2. **Login to Astronomer**:
   ```bash
   astro login
   ```

3. **Create Deployment**:
   ```bash
   astro deployment create --stack-version 6.0.0
   ```

4. **Configure Environment Variables**:
   ```bash
   astro deployment variable set POSTGRES_HOST="your-render-db.example.com"
   astro deployment variable set POSTGRES_USER="your_username"
   astro deployment variable set POSTGRES_PASSWORD="your_secure_password"
   astro deployment variable set POSTGRES_DB="infrapulse"
   ```

5. **Deploy DAGs**:
   ```bash
   astro deploy
   ```

6. **Access Airflow UI**:
   - Get URL from Astronomer dashboard
   - Login with credentials from `.env.prod`

### **Option B: Self-Hosted on Cloud VM**

**Using Docker Compose on AWS EC2/Azure VM:**

1. **Create cloud VM** (Ubuntu 22.04 recommended)

2. **Install Docker and Docker Compose**:
   ```bash
   sudo apt-get update
   sudo apt-get install docker.io docker-compose
   sudo usermod -aG docker $USER
   ```

3. **Clone repository**:
   ```bash
   git clone <your-repo>
   cd infrapulse
   ```

4. **Create production `.env` file**:
   ```bash
   cat > .env.prod << EOF
   POSTGRES_HOST=your-render-db.example.com
   POSTGRES_USER=your_username
   POSTGRES_PASSWORD=your_secure_password
   AIRFLOW_USERNAME=airflow_user
   AIRFLOW_PASSWORD=strong_airflow_password
   AIRFLOW_EMAIL=airflow@example.com
   EOF
   ```

5. **Start containers**:
   ```bash
   docker-compose --env-file .env.prod -d up
   ```

6. **Access Airflow UI**:
   - `http://<your-vm-ip>:8080`

---

## **Step 5: Configure Secrets & Environment Variables**

### **For Astronomer:**

```bash
# Set variables securely
astro deployment variable set POSTGRES_PASSWORD="$(cat secret.txt)"

# List all variables
astro deployment variable list
```

### **For Self-Hosted Cloud VM:**

Use AWS Secrets Manager or Azure Key Vault:

```bash
# Fetch secrets and create .env at runtime
aws secretsmanager get-secret-value --secret-id infrapulse-secrets --query SecretString --output text > .env.prod
docker-compose --env-file .env.prod up -d
```

---

## **Step 6: Verify Cloud Deployment**

### **Test Airflow Connection**:

1. **Access Airflow UI** at `http://<your-airflow-url>:8080`
2. **Trigger DAG manually**: Click your DAG → Trigger DAG
3. **Check logs**: Verify in Task Logs that data is loading to cloud database

### **Verify Database Connection**:

```bash
# Test connection to cloud PostgreSQL
psql -h <POSTGRES_HOST> -U <POSTGRES_USER> -d infrapulse -c "SELECT COUNT(*) FROM fact_service_failure;"
```

---

## **Step 7: CI/CD Pipeline (Optional)**

### **GitHub Actions Example**:

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Astronomer

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Deploy to Astronomer
        run: |
          astro login --token ${{ secrets.ASTRONOMER_TOKEN }}
          astro deploy --deployment-id ${{ secrets.ASTRONOMER_DEPLOYMENT_ID }}
        env:
          POSTGRES_HOST: ${{ secrets.POSTGRES_HOST }}
          POSTGRES_PASSWORD: ${{ secrets.POSTGRES_PASSWORD }}
```

---

## **Troubleshooting**

### **Connection Issues**:
```bash
# Test connection locally
docker exec infrapulse_db psql -U $POSTGRES_USER -d infrapulse -c "SELECT 1"

# Test from local machine to cloud DB
psql -h <POSTGRES_HOST> -U <POSTGRES_USER> -d infrapulse -c "SELECT 1"
```

### **Airflow DAG Not Running**:
- Check environment variables are set
- View logs: `astro logs --follow`
- Verify scheduler is running: `airflow scheduler logs`

### **PostgreSQL Connection Timeouts**:
- Check firewall rules allow inbound on port 5432
- Verify database is in same region as Airflow (or close by)
- Add SSL certificate if required by cloud provider

---

## **Security Best Practices**

✅ **DO:**
- Use `.env.example` to show required variables (no secrets)
- Store actual credentials in `.env.prod` (git-ignored)
- Use cloud provider secrets manager (AWS Secrets, Azure Key Vault)
- Rotate passwords regularly
- Use SSL/TLS for database connections

❌ **DON'T:**
- Commit `.env` or `.env.prod` to version control
- Hardcode passwords in code
- Use weak passwords in production
- Send credentials via email

---

## **Next Steps**

1. ✅ Deploy PostgreSQL to Render/Railway
2. ✅ Deploy Airflow to Astronomer or self-hosted
3. ✅ Configure environment variables
4. ✅ Test end-to-end pipeline
5. ✅ Set up monitoring/alerts (optional)
6. ✅ Document data lineage and SLAs

For questions, refer to:
- Astronomer Docs: https://docs.astronomer.io/
- Render Docs: https://render.com/docs/databases
- Railway Docs: https://docs.railway.app/
