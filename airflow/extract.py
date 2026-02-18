import pandas as pd

def extract_failures(path):
    return pd.read_csv(path)
