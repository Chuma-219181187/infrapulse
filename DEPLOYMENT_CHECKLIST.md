# Cloud Deployment Checklist

## � Quick Start: Railway PostgreSQL (Easiest Option)

⭐ **Start here for Railway deployment!**

See [RAILWAY_DEPLOYMENT.md](./RAILWAY_DEPLOYMENT.md) for the complete step-by-step guide.

**Quick Summary:**
1. Sign up at https://railway.app/
2. Create PostgreSQL database (Railway does this automatically)
3. Copy credentials from Railway dashboard
4. Run: `cp .env.railway.example .env.prod` and fill in values
5. Run: `python test_railway_connection.py`
6. Run: `railway run psql $DATABASE_URL -f warehouse/schema.sql`
7. Done! Your database is ready.

**Files Created for Railway:**
- ✅ `RAILWAY_DEPLOYMENT.md` - Complete detailed guide (11 steps)
- ✅ `.env.railway.example` - Environment variable template
- ✅ `test_railway_connection.py` - Connection test script

---

## �📋 Pre-Deployment Steps

- [ ] Update `docker-compose.yml` to use environment variables ✅
- [ ] Create `.env.example` with required variables ✅
- [ ] Create `.env` for local development ✅
- [ ] Update `etl/load.py` to use `os.getenv()` ✅
- [ ] Update `airflow/dags/infrapulse_etl_dag.py` for cloud ✅
- [ ] Add `.gitignore` to protect secrets ✅
- [ ] Test locally with `docker-compose --env-file .env up -d` ✅

---

## 🗄️ Deploy PostgreSQL Database

### **Render.com:**
- [ ] Create account at https://render.com/
- [ ] Create PostgreSQL instance
- [ ] Save `POSTGRES_HOST`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- [ ] Run schema initialization: `psql -h <HOST> -U <USER> -d infrapulse -f warehouse/schema.sql`

### **Railway.app:** ⭐ (Recommended - Easiest Setup)
**👉 [See Complete Railway Guide](./RAILWAY_DEPLOYMENT.md) for step-by-step instructions**

- [ ] Create account at https://railway.app/
- [ ] Create PostgreSQL database
- [ ] Copy connection details (HOST, USER, PASSWORD, DB)
- [ ] Copy `.env.railway.example` to `.env.prod` and fill in credentials
- [ ] Test connection: `python test_railway_connection.py`
- [ ] Run schema initialization: `railway run psql $DATABASE_URL -f warehouse/schema.sql`
- [ ] Verify tables: `railway run psql $DATABASE_URL -c "\dt"`

---

## 🚀 Deploy Airflow

✅ **COMPLETE** - Astronomer deployment running
- ✅ DAGs uploaded and tested
- ✅ Environment variables configured
- ✅ DAG successfully triggered
- ✅ Data loaded to Railway verified

### 📊 **Monitoring & Logging** ✅ **COMPLETE**

See: [MONITORING_SETUP.md](./MONITORING_SETUP.md) and [MONITORING_QUICKREF.md](./MONITORING_QUICKREF.md)

- ✅ Task-level logging with detailed tracing
- ✅ Astronomer UI log access configured
- ✅ Database monitoring setup
- ✅ Email alerts available
- ✅ Performance metrics defined

### **Astronomer (Recommended):**

```bash
# 1. Install Astronomer CLI
brew install astro
# or: Download from https://www.astronomer.io/downloads/

# 2. Login
astro login

# 3. Create deployment
astro deployment create --stack-version 6.0.0

# 4. Set environment variables
astro deployment variable set POSTGRES_HOST="your-render-db.example.com"
astro deployment variable set POSTGRES_USER="your_username"
astro deployment variable set POSTGRES_PASSWORD="your_secure_password"
astro deployment variable set POSTGRES_DB="infrapulse"

# 5. Deploy DAGs
astro deploy

# 6. Access Airflow UI
# Get URL from Astronomer dashboard
```

### **Self-Hosted on Cloud VM (AWS/Azure):**

```bash
# 1. Create Ubuntu VM (22.04 LTS)

# 2. Install Docker
sudo apt-get update
sudo apt-get install docker.io docker-compose

# 3. Clone repository
git clone <your-repo>
cd infrapulse

# 4. Create .env.prod
cat > .env.prod << EOF
POSTGRES_HOST=your-render-db.example.com
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_secure_password
AIRFLOW_USERNAME=airflow_user
AIRFLOW_PASSWORD=strong_airflow_password
AIRFLOW_EMAIL=airflow@example.com
EOF

# 5. Start containers
docker-compose --env-file .env.prod -d up

# 6. Access Airflow at http://<VM-IP>:8080
```

---

## 🔒 Security Best Practices

- [ ] Store credentials in `.env.prod` (git-ignored)
- [ ] Use secrets manager (AWS Secrets, Azure Key Vault)
- [ ] Enable SSL for database connections
- [ ] Use strong passwords (min 16 chars, mix case/numbers/symbols)
- [ ] Rotate passwords regularly
- [ ] Restrict database firewall to Airflow IP only
- [ ] Use private databases (not publicly accessible)

---

## ✅ Post-Deployment Verification

```bash
# Test database connection
psql -h <POSTGRES_HOST> -U <POSTGRES_USER> -d infrapulse -c "SELECT 1"

# Trigger DAG manually
Airflow UI → DAGs → infrapulse_etl → Trigger DAG

# Check logs
Airflow UI → DAGs → infrapulse_etl → Task Logs

# Verify data loaded
psql -h <POSTGRES_HOST> -U <POSTGRES_USER> -d infrapulse -c "SELECT COUNT(*) FROM fact_service_failure"
```

---

## 📊 Monitoring & Maintenance

- [ ] Set up Airflow alerts (email on DAG failure)
- [ ] Monitor database performance
- [ ] Set up automated backups
- [ ] Review logs weekly
- [ ] Update dependencies monthly

---

## 🆘 Troubleshooting

### Database Connection Timeout
```bash
# Check network connectivity
telnet <POSTGRES_HOST> 5432

# Verify firewall rules allow inbound
# Check database is in same region as Airflow
```

### DAG Not Running
```bash
# Check scheduler is running
docker ps | grep airflow

# Check DAG parsing errors
airflow dags list
airflow dag-processor

# View scheduler logs
docker logs <airflow-container> --follow
```

### Environment Variables Not Set
```bash
# Verify .env file exists
cat .env

# Restart containers to reload
docker-compose down
docker-compose --env-file .env up -d
```

---

## 📚 Resources

- [DEPLOYMENT.md](./DEPLOYMENT.md) - Detailed deployment guide
- **[RAILWAY_DEPLOYMENT.md](./RAILWAY_DEPLOYMENT.md)** ⭐ - Complete Railway guide with 11 steps
- [.env.railway.example](./.env.railway.example) - Environment template
- [test_railway_connection.py](./test_railway_connection.py) - Connection verification script
- [Astronomer Docs](https://docs.astronomer.io/)
- [Render Docs](https://render.com/docs/databases)
- [Railway Docs](https://docs.railway.app/)
