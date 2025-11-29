import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def top_k_similar_players(player_name, df, sim_matrix, k=5):
    player_idx = df.index[df['PLAYER_NAME'] == player_name][0]
    similarity_scores = sim_matrix[player_idx]

    top_idx = np.argsort(similarity_scores)[::-1]  # descending order
    top_idx = top_idx[top_idx != player_idx][:k]

    return df.iloc[top_idx][['PLAYER_NAME'] + list(df.columns[2:])]


def compute_similarity(df):
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    X = df[numeric_cols].values
    sim_matrix = cosine_similarity(X)  # similarity between every pair of players
    return sim_matrix


