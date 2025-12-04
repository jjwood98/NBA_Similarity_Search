import streamlit as st
import pickle
import numpy as np
import pandas as pd
from utils.faiss_index import load_faiss_index, query_faiss
from frontend.feature_names import get_feature_names

class search_workflow:
    def __init__(self,index, embeddings, player_names, df_original):
        self.index = index
        self.embeddings = embeddings
        self.player_names = player_names
        self.df_original = df_original

    def run(self, player_name, k):
        index = self.index
        embeddings = self.embeddings
        player_names = self.player_names
        df_original = self.df_original

        # --- Find player embedding index ---
        player_idx = player_names.index(player_name)
        query_emb = embeddings[player_idx].reshape(1, -1).astype("float32")

        # --- Query FAISS index ---
        distances, indices = query_faiss(index, query_emb, k + 1)  # include possible self
        distances = distances[0]
        indices = indices[0]

        # --- Remove query player itself ---
        mask = indices != player_idx
        indices = indices[mask][:k]
        distances = distances[mask][:k]

        numeric_cols = df_original.select_dtypes(include=np.number).columns.tolist()
        player_vec = df_original.loc[player_idx, numeric_cols].values
        player_norm = np.linalg.norm(player_vec)

        # --- Prepare results DataFrame ---
        output_rows = []
        num_top_feats = 15
        feature_names = get_feature_names()

        for idx, dist in zip(indices, distances):
            other_vec = df_original.loc[idx, numeric_cols].values
            other_norm = np.linalg.norm(other_vec)

            contrib = (player_vec * other_vec) / (player_norm * other_norm)
            total_sim = 1 - dist  # if using L2 distance, convert to similarity

            # Skip zero similarity
            if total_sim == 0:
                continue

            contribution_percent = contrib / contrib.sum()
            contrib_df = pd.DataFrame({"feature": numeric_cols, "pct": contribution_percent})
            top_feats = contrib_df.sort_values("pct", ascending=False).head(num_top_feats)

            row = {
                "PLAYER_NAME": player_names[idx],
                "SIMILARITY": round(float(total_sim) * 100, 2)
            }

            # Add top feature contributions as readable strings
            for i, (_, r) in enumerate(top_feats.iterrows(), start=1):
                feat = r["feature"]
                readable_feat = feature_names.get(feat, feat)
                pct = r["pct"] * 100
                row[f"Top Feature {i} (Contribution)"] = f"{readable_feat} ({pct:.1f}%)"

            output_rows.append(row)

        df_results = pd.DataFrame(output_rows)
        df_results.index = df_results['PLAYER_NAME']

        # --- Display results table ---
        st.dataframe(df_results)

        return df_results, num_top_feats