import pandas as pd

from utils.nba_api_wrapper import DataCollection
from utils.data_processing import normalise_stats,merge_df, weighted_player_averages
from utils.k_nearest import compute_similarity,top_k_similar_players
from utils.umap import compute_umap_similarity
from utils.faiss_index import build_faiss_index, save_faiss_index
import pickle
import numpy as np

def build_faiss_pipeline():
    print("Updating Data...")
    dc = DataCollection("data/nba_stats.db")
    layer1_df = dc.get_last_n_years_stats(per_mode="PerGame")
    layer1_df = layer1_df.groupby('PLAYER_NAME', group_keys=True).apply(weighted_player_averages,
                                                                        include_groups=False).reset_index()
    layer2_df = dc.get_last_n_years_stats(per_mode="PerGame", measure_type = "Advanced")
    layer3_df = dc.get_player_playtpes()
    def_stats = dc.get_def_stats()
    df = merge_df(layer1_df, layer2_df)
    df = merge_df(df, layer3_df)
    df = merge_df(df, def_stats)

    print("Normalising Data...")
    df = df.groupby('PLAYER_NAME',group_keys = True).apply(weighted_player_averages, include_groups=False).reset_index()
    df_normalised = normalise_stats(df)
    sim_matrix = compute_similarity(df_normalised)
    sim_matrix_umap, embedding_umap, embeddings, umap_model = compute_umap_similarity(df_normalised)

    print("Building Faiss index...")
    index = build_faiss_index(embeddings)

    print("Saving FAISS + metadata...")
    metadata = pd.DataFrame({
        "PLAYER_NAME": df_normalised["PLAYER_NAME"].tolist(),
        "embeddings": [emb.tolist() for emb in embeddings],
    })

    save_faiss_index(index, "faiss_index.bin", metadata)
    metadata.to_parquet("faiss_index_metadata.parquet")
    df.to_parquet("df_original.parquet")

    with open("umap_model.pkl", "wb") as f:
        pickle.dump(umap_model, f)

    print("FAISS index built and saved successfully!")


if __name__ == "__main__":
    build_faiss_pipeline()