from utils.nba_api_wrapper import DataCollection
from utils.data_processing import normalise_stats,merge_df, weighted_player_averages
from utils.k_nearest import compute_similarity,top_k_similar_players

dc = DataCollection("data/nba_stats.db")
layer1_df = dc.get_last_n_years_stats(per_mode="Per100Possessions", measure_type= "Advanced")
layer2_df = dc.get_last_n_years_stats(per_mode="Per100Possessions", measure_type = "Advanced")
dc.save_to_sql(layer1_df, table_name="layer1_basic_stats")

df = merge_df(layer1_df, layer2_df)

df = df.groupby('PLAYER_NAME', group_keys = True).apply(weighted_player_averages, include_groups=False).reset_index()
df_normalised = normalise_stats(df)
sim_matrix = compute_similarity(df_normalised)
top5 = top_k_similar_players("Ja Morant", df, sim_matrix, k=5)

print(top5)