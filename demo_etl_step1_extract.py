#!/usr/bin/env python
"""
DEMO SCRIPT: STEP 1 - EXTRACT
Shows the extraction phase of the ETL pipeline
"""

import sys
import os

# Add etl directory to path so imports work correctly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'etl'))

from extract import extract_failures
from elt_logger import log_info

print("\n" + "="*60)
print("STEP 4: EXTRACT - Reading Raw CSV Data")
print("="*60)

file_path = "data/staging/failures.csv"
df = extract_failures(file_path)

print(f"\n✅ EXTRACTED {len(df)} records from CSV\n")
print("Columns:", list(df.columns))
print("\nData preview:")
print(df.to_string())
print("\n" + "="*60)
