# Railway Deployment Architecture

## **Before & After Deployment**

### **Local Development (Before)**
```
┌─────────────────────────────────────────┐
│         Your Local Machine              │
├─────────────────────────────────────────┤
│  Docker Containers:                     │
│  ├─ PostgreSQL Database (localhost)     │
│  ├─ Apache Airflow (localhost:8080)     │
│  └─ Jupyter/Development Tools           │
│                                         │
│  Data Flow:                             │
│  CSV → ETL Extraction → Transform       │
│       → Load into PostgreSQL            │
│       → Airflow Scheduler monitors      │
└─────────────────────────────────────────┘
```

### **Cloud Deployment (After)**
```
┌─────────────────────────────────────────────────────────┐
│                    Railway.app Cloud                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  PostgreSQL Database (Managed by Railway):            │
│  ├─ dim_asset table                                   │
│  ├─ dim_date table                                    │
│  ├─ fact_service_failure table (YOUR DATA)            │
│  └─ etl_metadata table                                │
│                                                         │
│  Connection String:                                    │
│  postgresql://user:pass@rail.railway.app:5432/db     │
│                                                         │
└─────────────────────────────────────────────────────────┘
         ↑                              
         │ (Secure SSL Connection)      
         │                              
┌─────────────────────────────────────────┐
│         Your Airflow (Astronomer)       │
│         or Docker Host                  │
├─────────────────────────────────────────┤
│  ETL Pipeline:                          │
│  1. Extract: Read CSV files             │
│  2. Transform: Process & enrich data    │
│  3. Load: Write to Railway PostgreSQL   │
│  4. Verify: Check data quality          │
│                                         │
│  Data → Airflow → Railway DB            │
└─────────────────────────────────────────┘
```

---

## **Deployment Steps Flow**

```
1. Create Railway Account
   └─→ 2. Create PostgreSQL Database
       └─→ 3. Get Connection Details (HOST, USER, PASS)
           └─→ 4. Create .env.prod with credentials
               └─→ 5. Test connection (test_railway_connection.py)
                   └─→ 6. Initialize schema (warehouse/schema.sql)
                       └─→ 7. Verify tables exist
                           └─→ 8. Update ETL code (load.py)
                               └─→ 9. Deploy Airflow
                                   └─→ ✅ Ready for production!
```

---

## **Database Schema Overview**

Your schema has **4 tables** with relationships:

```
┌─────────────────────┐
│   dim_asset         │
├─────────────────────┤
│ asset_key (PK)      │
│ asset_id            │
│ asset_type          │
│ service_type        │
│ location            │
└──────────┬──────────┘
           │ (1:N)
           │
           └──────────┐
                      │
                      ├─────────────────────────────┐
                      │                             │
            ┌─────────────────────────┐   ┌─────────────────────────┐
            │ fact_service_failure    │   │   dim_date              │
            ├─────────────────────────┤   ├─────────────────────────┤
            │ failure_id (PK)         │   │ date_key (PK)           │
            │ asset_key (FK)──────┐   │   │ full_date               │
            │ date_key (FK)───────┼──────→ │                         │
            │ failure_type        │   │   │                         │
            │ outage_minutes      │   │   │                         │
            │ resolved            │   │   │                         │
            │ (Indexes on asset_key)  │   │                         │
            └─────────────────────────┘   └─────────────────────────┘
                      │
                      │
            ┌─────────────────────────┐
            │   etl_metadata          │
            ├─────────────────────────┤
            │ run_id (PK)             │
            │ run_time (TIMESTAMP)    │
            │ records_loaded          │
            │ status                  │
            └─────────────────────────┘
```

---

## **Data Flow Example**

```
Raw Data (CSV)
    │
    ↓
┌─────────────────────────────────┐
│ ETL Extract Phase               │
│ - Read failures.csv             │
│ - Parse columns                 │
└─────────────────────────────────┘
    │
    ↓
┌─────────────────────────────────┐
│ ETL Transform Phase             │
│ - Clean data                    │
│ - Validate quality              │
│ - Map to dimensions             │
│ - Create fact records           │
└─────────────────────────────────┘
    │
    ↓
┌──────────────────────────────────────────┐
│ ETL Load Phase (via Railway)             │
│ - Insert into dim_asset                  │
│ - Insert into dim_date                   │
│ - Insert into fact_service_failure       │
│ - Record metadata in etl_metadata        │
│                                          │
│ Connection:                              │
│ postgresql://user:pass@host:5432/db     │
│ (SSL required)                           │
└──────────────────────────────────────────┘
    │
    ↓
┌─────────────────────────────────┐
│ Railway PostgreSQL Database      │
│ (Secure, Managed, Cloud-backed)  │
└─────────────────────────────────┘
```

---

## **Connection Security Flow**

```
Your Code (.env.prod)
    │
    ├─ POSTGRES_HOST: hostname.railway.app
    ├─ POSTGRES_PORT: 5432
    ├─ POSTGRES_DB: railway
    ├─ POSTGRES_USER: postgres
    ├─ POSTGRES_PASSWORD: ★★★★★★★★
    └─ POSTGRES_SSL_MODE: require (IMPORTANT!)
            │
            ↓
┌──────────────────────────────┐
│ SSL/TLS Encryption Tunnel    │
└──────────────────────────────┘
            │
            ↓
┌──────────────────────────────────┐
│ Railway PostgreSQL Server        │
│ (Encrypted Connection)           │
└──────────────────────────────────┘
```

---

## **File Structure After Deployment**

```
infrapulse/
├── RAILWAY_DEPLOYMENT.md ⭐ (New - Full guide)
├── RAILWAY_QUICK_REFERENCE.md ⭐ (New - Quick reference)
├── test_railway_connection.py ⭐ (New - Verification script)
├── .env.railway.example ⭐ (New - Template)
├── .env.prod (NEW - Create this from template)
│
├── warehouse/
│   └── schema.sql (Your 4 tables + indexes)
│
├── etl/
│   ├── load.py (Update: Use env vars + SSL)
│   ├── extract.py
│   ├── transform.py
│   └── quality_checks.py
│
├── airflow/
│   └── dags/
│       └── infrapulse_etl_dag.py (Update: Use env vars + SSL)
│
├── data/
│   ├── raw/
│   └── staging/
│
└── docs/
    └── ... (existing docs)
```

---

## **Environment Variables Mapping**

| Your Code | Railway Dashboard | Example |
|-----------|------------------|---------|
| `POSTGRES_HOST` | PostgreSQL → Connect → Host | `xyz.railway.app` |
| `POSTGRES_PORT` | (Fixed) | `5432` |
| `POSTGRES_DB` | PostgreSQL → Settings | `railway` |
| `POSTGRES_USER` | (Usually) | `postgres` |
| `POSTGRES_PASSWORD` | Copy from Connection String | `Secure_Pass_123!` |
| `POSTGRES_SSL_MODE` | (Required for Railway) | `require` |

---

## **Quality Assurance Checks**

After deployment, verify:

```bash
# ✅ Can connect to Railway database?
python test_railway_connection.py

# ✅ Are all 4 tables created?
railway run psql $DATABASE_URL -c "\dt"

# ✅ Can insert data?
railway run psql $DATABASE_URL -c "INSERT INTO dim_asset VALUES (1, 'A1', 'Type1', 'Service1', 'Location1');"

# ✅ Can query data?
railway run psql $DATABASE_URL -c "SELECT COUNT(*) FROM dim_asset;"

# ✅ Are indexes in place?
railway run psql $DATABASE_URL -c "\d fact_service_failure"

# ✅ Can read from CSV and load?
python etl/extract.py && python etl/load.py
```

---

## **Security Checklist**

```
✅ Environment variables in .env.prod (not committed to git)
✅ SSL mode enabled (POSTGRES_SSL_MODE=require)
✅ Strong password (16+ chars, mixed case, numbers, symbols)
✅ .gitignore includes .env.prod
✅ Connection string not visible in logs
✅ Password file permissions restricted (chmod 600 .env.prod)
✅ Regular password rotation documented
✅ Only necessary users have database access
```

---

## **Migration Path**

```
┌─────────────────────┐
│ Local Development   │        ┌─────────────────────┐
│ (Docker)            │───────→│ Railway PostgreSQL  │
│ PostgreSQL          │        │ (Production)        │
└─────────────────────┘        └─────────────────────┘
        ↓                               ↓
   .env (local)                   .env.prod (secret)
   Full Docker setup              Managed database
   Easy to reset/delete           Automated backups
                                 HA/redundancy
```

---

## **Next Steps After Railway Setup**

1. ✅ Database created and tested
2. → Deploy Airflow (see [DEPLOYMENT.md](DEPLOYMENT.md))
3. → Load production data via ETL
4. → Set up monitoring and alerts
5. → Configure automated backups
6. → Document connection handoff to ops team

---

## **Support & Links**

- 📖 Full guide: [RAILWAY_DEPLOYMENT.md](./RAILWAY_DEPLOYMENT.md)
- ⚡ Quick ref: [RAILWAY_QUICK_REFERENCE.md](./RAILWAY_QUICK_REFERENCE.md)
- 🔧 Test script: [test_railway_connection.py](./test_railway_connection.py)
- 📋 Template: [.env.railway.example](./.env.railway.example)
- 🌐 Railway Docs: https://docs.railway.app/
- 🐘 PostgreSQL Docs: https://www.postgresql.org/docs/
