import sqlite3
import pandas as pd
from utils.nba_api_wrapper import DataCollection
from utils.data_processing import normalise_stats,merge_df, weighted_player_averages
from utils.k_nearest import compute_similarity,top_k_similar_players, top_k_similar_players_improved, compute_similarity_pca, top_k_similar_players_pca
from nba_api.stats.endpoints import LeagueDashPlayerStats, SynergyPlayTypes, LeagueDashPtDefend
from utils.logger import logging
import pprint
from utils.umap import compute_umap_similarity
from scipy.stats import spearmanr

# dc = DataCollection()
# test = dc.get_def_stats()
# for cols in test.columns:
#     print(cols)
# #dc.save_to_sql(test, table_name="playtype_stats")



dc = DataCollection("data/nba_stats.db")
layer1_df = dc.get_last_n_years_stats(per_mode="PerGame")

layer1_df = layer1_df.groupby('PLAYER_NAME',group_keys = True).apply(weighted_player_averages, include_groups=False).reset_index()
df_normalised = normalise_stats(layer1_df)
sim_matrix = compute_similarity(df_normalised)
top5_layer1 = top_k_similar_players_improved("Rudy Gobert", layer1_df, sim_matrix, k=5)


layer2_df = dc.get_last_n_years_stats(per_mode="PerGame", measure_type = "Advanced")
df = merge_df(layer1_df, layer2_df)
df = df.groupby('PLAYER_NAME',group_keys = True).apply(weighted_player_averages, include_groups=False).reset_index()
df_normalised = normalise_stats(df)
sim_matrix = compute_similarity(df_normalised)
top5_layer2 = top_k_similar_players_improved("Rudy Gobert", df, sim_matrix, k=5)

layer3_df = dc.get_player_playtpes()

df = merge_df(df, layer3_df)

def_stats = dc.get_def_stats()
df = merge_df(df, def_stats)
for cols in df.columns:
    print(cols)
dc.save_to_sql(df, table_name="complete_combined_table")


df = df.groupby('PLAYER_NAME',group_keys = True).apply(weighted_player_averages, include_groups=False).reset_index()
df_normalised = normalise_stats(df)
sim_matrix = compute_similarity(df_normalised)
sim_matrix3, pca, X_pca, numeric_cols = compute_similarity_pca(layer3_df, n_components=20)
top5_layer3 = top_k_similar_players_improved("Rudy Gobert", df, sim_matrix, k=5)

sim_matrix_umap, embedding_umap = compute_umap_similarity(df_normalised)
top5_layer3_umap = top_k_similar_players_improved("Rudy Gobert", df, sim_matrix_umap, k=5)

set(top5_layer3['PLAYER_NAME']) & set(top5_layer3_umap['PLAYER_NAME'])
spearmanr(top5_layer3['SIMILARITY'], top5_layer3_umap['SIMILARITY'])

with pd.option_context(
    'display.max_rows', None,        # Show all rows
    'display.max_columns', None,     # Show all columns
    'display.width', 200,            # Max line width
    'display.max_colwidth', None     # Do not truncate column content
):
    logging.info("Layer 1 Top 5:\n%s", top5_layer1.to_string(index=False))
    logging.info("Layer 2 Top 5:\n%s", top5_layer2.to_string(index=False))
    logging.info("Layer 3 Top 5:\n%s", top5_layer3.to_string(index=False))
    logging.info("Layer 3 (UMAP) Top 5:\n%s", top5_layer3_umap.to_string(index=False))

