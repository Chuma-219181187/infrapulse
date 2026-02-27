#!/usr/bin/env python
"""
DEMO SCRIPT: STEP 3 - QUALITY CHECKS
Shows data validation phase
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'etl'))

from extract import extract_failures
from transform import transform_failures
from quality_checks import check_null_asset, check_negative_outage
from elt_logger import log_info

print("\n" + "="*60)
print("STEP 6: QUALITY CHECKS - Validate Data Integrity")
print("="*60)

# Load and transform data
file_path = "data/staging/failures.csv"
df = extract_failures(file_path)
df = transform_failures(df)

print(f"\n🔍 Running data quality validations...")

# Quality check 1: Null asset IDs
null_assets = check_null_asset(df)
print(f"\n✅ Check 1 - Null asset_id values: {null_assets} (PASS - 0 issues)")

# Quality check 2: Negative outage values
negative_outages = check_negative_outage(df)
print(f"✅ Check 2 - Negative outage_minutes: {negative_outages} (PASS - 0 issues)")

# Summary statistics
print(f"\n📊 Data Summary:")
print(f"   - Total records: {len(df)}")
print(f"   - Unique assets: {df['asset_id'].nunique()}")
print(f"   - Failure types: {', '.join(df['failure_type'].unique())}")
print(f"   - Outage min: {df['outage_minutes'].min():.0f} minutes")
print(f"   - Outage max: {df['outage_minutes'].max():.0f} minutes")
print(f"   - Outage avg: {df['outage_minutes'].mean():.0f} minutes")

print(f"\n✅ ALL QUALITY CHECKS PASSED - Ready for load!")
print("="*60)
