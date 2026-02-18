import pandas as pd
from elt_logger import log_info, log_error, log_warning

def transform_failures(df):
    """Transform failure data (clean, enrich, prepare for warehouse)"""
    try:
        log_info(f"🔄 Starting transformation on {len(df)} records")
        
        # Remove duplicates
        initial_count = len(df)
        df = df.drop_duplicates()
        duplicates_removed = initial_count - len(df)
        if duplicates_removed > 0:
            log_warning(f"⚠️ Removed {duplicates_removed} duplicate records")
        
        # Parse timestamps
        df["start_time"] = pd.to_datetime(df["start_time"])
        df["end_time"] = pd.to_datetime(df["end_time"])
        log_info(f"✅ Parsed timestamps")
        
        # Calculate outage duration
        df["outage_minutes"] = (
            df["end_time"] - df["start_time"]
        ).dt.total_seconds() / 60
        min_outage = df["outage_minutes"].min()
        max_outage = df["outage_minutes"].max()
        avg_outage = df["outage_minutes"].mean()
        log_info(f"✅ Calculated outage_minutes (min: {min_outage:.0f}, max: {max_outage:.0f}, avg: {avg_outage:.0f})")
        
        # Create date key
        df["date_key"] = df["start_time"].dt.strftime("%Y%m%d").astype(int)
        date_range = f"{df['start_time'].min().date()} to {df['start_time'].max().date()}"
        log_info(f"✅ Created date key (range: {date_range})")
        
        log_info(f"✅ Transformation complete: {len(df)} records ready for load")
        return df
    except Exception as e:
        log_error(f"❌ Transformation failed: {str(e)}")
        raise
