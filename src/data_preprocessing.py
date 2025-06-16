import pandas as pd

def load_and_preprocess(filepath):
    df = pd.read_csv(filepath)
    df = pd.get_dummies(df, drop_first=True)
    return df
