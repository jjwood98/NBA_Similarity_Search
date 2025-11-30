from sklearn.preprocessing import StandardScaler
import numpy as np
import pandas as pd

def normalise_stats(df):
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    scaler = StandardScaler()
    df_scaled = df.copy()
    df_scaled[numeric_cols] = scaler.fit_transform(df_scaled[numeric_cols])
    return df_scaled

def weighted_player_averages(group, decay = 0.8):
    group = group.sort_values(by=["Season"], ascending=False)
    numeric_cols = group.select_dtypes(include=np.number).columns.tolist()
    weights = pd.Series([decay**i for i in range(len(group))], index= group.index)
    weighted = (group[numeric_cols].T * weights).T.sum() / weights.sum()
    return weighted


def merge_df(df1, df2):
    shared = df1.columns.intersection(df2.columns)
    print(shared)
    print(df1.shape)
    print(df2.shape)
    df = df1.merge(df2, on=list(shared))

    return df