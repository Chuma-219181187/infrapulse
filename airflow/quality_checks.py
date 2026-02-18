def check_null_asset(df):
    return df["asset_id"].isnull().sum()

def check_negative_outage(df):
    return (df["outage_minutes"] < 0).sum()
