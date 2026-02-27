#!/usr/bin/env python
"""
DEMO SCRIPT: STEP 2 - TRANSFORM
Shows data cleaning and enrichment phase
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'etl'))

from extract import extract_failures
from transform import transform_failures
from elt_logger import log_info

print("\n" + "="*60)
print("STEP 5: TRANSFORM - Clean & Enrich Data")
print("="*60)

# Load raw data
file_path = "data/staging/failures.csv"
df = extract_failures(file_path)

print(f"\n📊 Raw data columns: {list(df.columns)}")
print(f"📊 Raw data shape: {df.shape}")

# Transform the data
df_transformed = transform_failures(df)

print(f"\n✅ TRANSFORMATION COMPLETE\n")
print(f"📊 Transformed columns: {list(df_transformed.columns)}")
print(f"📊 Transformed shape: {df_transformed.shape}")

print("\nTransformed data:")
print(df_transformed.to_string())
print("\n" + "="*60)
