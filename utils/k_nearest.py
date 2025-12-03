import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

def top_k_similar_players(player_name, df, sim_matrix, k=5):
    player_idx = df.index[df['PLAYER_NAME'] == player_name][0]
    similarity_scores = sim_matrix[player_idx]

    top_idx = np.argsort(similarity_scores)[::-1]  # descending order
    top_idx = top_idx[top_idx != player_idx][:k]

    return df.iloc[top_idx][['PLAYER_NAME'] + list(df.columns[2:])]

def top_k_similar_players_improved(player_name, df, sim_matrix, k=5, top_features=15):
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()

    player_idx = df.index[df['PLAYER_NAME'] == player_name][0]
    player_vec = df.loc[player_idx, numeric_cols].values
    player_norm = np.linalg.norm(player_vec)
    similarity_scores = sim_matrix[player_idx]

    top_idx = np.argsort(similarity_scores)[::-1]  # descending order
    top_idx = top_idx[top_idx != player_idx][:k]

    output_rows=[]

    for idx in top_idx:
        other_vec = df.loc[idx, numeric_cols].values
        other_norm = np.linalg.norm(other_vec)

        # Per-feature raw contributions
        contrib = (player_vec * other_vec) / (player_norm * other_norm)
        total_sim = similarity_scores[idx]

        # Avoid division issues
        if total_sim == 0:
            continue

        # Convert to percentage of similarity
        contribution_percent = contrib / contrib.sum()

        contrib_df = (
            pd.DataFrame({"feature": numeric_cols, "pct": contribution_percent})
            .sort_values("pct", ascending=False)
        )

        # Top N contributing features
        top_feats = contrib_df.head(top_features)

        row = {
            "PLAYER_NAME": df.loc[idx, "PLAYER_NAME"],
            "SIMILARITY": round(float(total_sim), 4)
        }

        # Add readable "STAT (20%)" columns
        for i, (_, r) in enumerate(top_feats.iterrows(), start=1):
            feat = r["feature"]
            pct = r["pct"] * 100
            row[f"top_{i}"] = f"{feat} ({pct:.1f}%)"

        output_rows.append(row)

    return pd.DataFrame(output_rows)


def compute_similarity(df):
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    X = df[numeric_cols].values
    sim_matrix = cosine_similarity(X)  # similarity between every pair of players
    return sim_matrix


def compute_similarity_pca(df, n_components=20):
    """
    Computes cosine similarity after PCA dimensionality reduction.

    Parameters:
        df (pd.DataFrame): DataFrame with numeric features
        n_components (int): Number of PCA components to keep

    Returns:
        sim_matrix (np.ndarray): Cosine similarity matrix
        pca (PCA object): Fitted PCA, for mapping back to original features
        X_pca (np.ndarray): PCA-transformed feature matrix
        numeric_cols (list): Names of numeric columns used
    """
    # Select numeric columns
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    df[numeric_cols] = df[numeric_cols].fillna(0)

    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df[numeric_cols])

    # Apply PCA
    pca = PCA(n_components=n_components)
    X_pca = pca.fit_transform(X_scaled)

    # Cosine similarity in PCA space
    sim_matrix = cosine_similarity(X_pca)

    return sim_matrix, pca, X_pca, numeric_cols


def top_k_similar_players_pca(player_name, df, sim_matrix, pca, X_pca, numeric_cols, k=5):
    """
    Returns top-k similar players with top feature contributions (from PCA mapping).

    Parameters:
        player_name (str)
        df (pd.DataFrame)
        sim_matrix (np.ndarray)
        pca (PCA object)
        X_pca (np.ndarray)
        numeric_cols (list)
        k (int)

    Returns:
        pd.DataFrame: Player, similarity, top-5 feature contributions
    """

    df = df.drop(columns = ["Season"])
    # Find player index
    player_idx = df.index[df['PLAYER_NAME'] == player_name][0]

    # Similarity scores
    similarity_scores = sim_matrix[player_idx]

    # Top-k indices excluding self
    top_idx = np.argsort(similarity_scores)[::-1]
    top_idx = top_idx[top_idx != player_idx][:k]

    # Prepare results
    results = []
    for idx in top_idx:
        player_sim = similarity_scores[idx]

        # Compute per-feature contributions
        # Approximate by projecting difference in PCA space back to original features
        diff_pca = X_pca[idx] - X_pca[player_idx]
        contrib_orig = np.abs(diff_pca @ pca.components_)  # absolute contribution per original feature
        contrib_orig_pct = 100 * contrib_orig / contrib_orig.sum()

        # Pick top 5 contributing features
        top_feats_idx = np.argsort(contrib_orig_pct)[::-1][:5]
        top_feats = [f"{numeric_cols[i]} ({contrib_orig_pct[i]:.1f}%)" for i in top_feats_idx]

        results.append({
            'PLAYER_NAME': df.iloc[idx]['PLAYER_NAME'],
            'SIMILARITY': round(player_sim, 4),
            'top_1': top_feats[0],
            'top_2': top_feats[1],
            'top_3': top_feats[2],
            'top_4': top_feats[3],
            'top_5': top_feats[4]
        })

    return pd.DataFrame(results)