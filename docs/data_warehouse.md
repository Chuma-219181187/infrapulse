# InfraPulse Data Warehouse Documentation

## Overview
InfraPulse warehouse supports infrastructure reliability analytics including failure tracking, outage duration analysis, and asset performance monitoring.

---

## Dimension Tables

### dim_asset
| Column | Type | Description |
|--------|------|-------------|
| asset_key | SERIAL PK | Surrogate key |
| asset_id | VARCHAR | Business identifier |
| asset_type | VARCHAR | Type of infrastructure |
| service_type | VARCHAR | Electricity / Water |
| location | VARCHAR | District |

---

### dim_date
| Column | Type | Description |
|--------|------|-------------|
| date_key | INT | YYYYMMDD format |
| full_date | DATE | Calendar date |

---

## Fact Tables

### fact_service_failure
| Column | Type | Description |
|--------|------|-------------|
| failure_id | SERIAL PK | Unique failure |
| asset_key | FK | Linked asset |
| date_key | FK | Failure date |
| failure_type | VARCHAR | Type of issue |
| outage_minutes | INT | Downtime |
| resolved | BOOLEAN | Resolved flag |

---

## Metadata

### etl_metadata
Tracks ETL run performance.
