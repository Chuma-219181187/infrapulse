import pandas as pd
from elt_logger import log_info, log_error, log_warning

def extract_failures(path):
    """Extract failure records from CSV file"""
    try:
        log_info(f"📂 Reading CSV file: {path}")
        df = pd.read_csv(path)
        log_info(f"✅ Extracted {len(df)} records from {path}")
        log_info(f"📊 Columns: {', '.join(df.columns.tolist())}")
        return df
    except FileNotFoundError:
        log_error(f"❌ File not found: {path}")
        raise
    except Exception as e:
        log_error(f"❌ Error reading CSV: {str(e)}")
        raise
