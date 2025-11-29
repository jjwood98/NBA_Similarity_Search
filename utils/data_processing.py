from sklearn.preprocessing import StandardScaler
import numpy as np

def normalise_stats(df):
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    scaler = StandardScaler()
    df_scaled = df.copy()
    df_scaled[numeric_cols] = scaler.fit_transform(df_scaled[numeric_cols])
    return df_scaled

