# 🚀 Railway PostgreSQL - Quick Reference Card

Print this or keep it open while deploying!

---

## **5-Minute Quick Start**

```bash
# STEP 1: Install Railway CLI
npm install -g @railway/cli

# STEP 2: Login to Railway
railway login

# STEP 3: Create .env.prod with your credentials
cp .env.railway.example .env.prod
# Edit .env.prod and fill in:
#   POSTGRES_HOST (from Railway dashboard)
#   POSTGRES_PASSWORD (from Railway dashboard)

# STEP 4: Initialize your database schema
railway run psql $DATABASE_URL -f warehouse/schema.sql

# STEP 5: Test connection
python test_railway_connection.py

# ✅ Done! Your database is ready to use
```

---

## **Railway Dashboard Navigation**

| Action | Path |
|--------|------|
| Get HOST | PostgreSQL → Connect → Copy Host |
| Get PASSWORD | PostgreSQL → Connect → Copy from Connection String |
| Get DATABASE | PostgreSQL → Settings (usually `railway`) |
| View Logs | PostgreSQL → Logs tab |
| Check Status | PostgreSQL → Overview →Status section |

---

## **Connection Details Format**

```
postgresql://postgres:PASSWORD@HOST:5432/DATABASE
```

Example:
```
postgresql://postgres:abc123@railway.app:5432/railway
```

---

## **Useful Commands**

### List all tables
```bash
railway run psql $DATABASE_URL -c "\dt"
```

### Count records in a table
```bash
railway run psql $DATABASE_URL -c "SELECT COUNT(*) FROM fact_service_failure;"
```

### View table structure
```bash
railway run psql $DATABASE_URL -c "\d dim_asset"
```

### Connect interactively
```bash
railway run psql $DATABASE_URL
```

### Create backup
```bash
pg_dump $DATABASE_URL > backup.sql
```

### Restore from backup
```bash
psql $DATABASE_URL < backup.sql
```

---

## **Checklist**

- [ ] Railway account created
- [ ] PostgreSQL database created
- [ ] `.env.prod` created and configured
- [ ] `python test_railway_connection.py` passes ✅
- [ ] Schema initialized: `railway run psql $DATABASE_URL -f warehouse/schema.sql`
- [ ] All 4 tables exist (verify with `\dt` command)
- [ ] Ready for Airflow deployment

---

## **Troubleshooting**

| Problem | Solution |
|---------|----------|
| `Connection refused` | Check HOST in .env.prod matches Railway dashboard |
| `password authentication failed` | Copy PASSWORD directly from Connection String in Railway |
| `psql: command not found` | Use `railway run psql` instead of `psql` |
| `Table does not exist` | Re-run: `railway run psql $DATABASE_URL -f warehouse/schema.sql` |
| `SSL connection error` | Ensure `POSTGRES_SSL_MODE=require` in .env.prod |

---

## **File References**

- Full guide: [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md)
- Environment template: [.env.railway.example](.env.railway.example)
- Test script: [test_railway_connection.py](test_railway_connection.py)

---

## **Support**

- Railway Docs: https://docs.railway.app/
- PostgreSQL Docs: https://www.postgresql.org/docs/
- Issues? Check logs: Railway dashboard → PostgreSQL → Logs
