import pandas as pd

def transform_failures(df):
    df = df.drop_duplicates()

    df["start_time"] = pd.to_datetime(df["start_time"])
    df["end_time"] = pd.to_datetime(df["end_time"])

    df["outage_minutes"] = (
        df["end_time"] - df["start_time"]
    ).dt.total_seconds() / 60

    df["date_key"] = df["start_time"].dt.strftime("%Y%m%d").astype(int)

    return df
