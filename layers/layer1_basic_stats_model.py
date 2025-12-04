from utils.nba_api_wrapper import DataCollection
from utils.data_processing import normalise_stats
from utils.k_nearest import compute_similarity,top_k_similar_players

dc = DataCollection("../data/nba_stats.db")
layer1_df = dc.get_last_n_years_stats(per_mode="PerGame", measure_type= "Basic")
dc.save_to_sql(layer1_df, table_name="layer1_basic_stats")

print(layer1_df.head())


df_normalised = normalise_stats(layer1_df)
sim_matrix = compute_similarity(df_normalised)
top5 = top_k_similar_players("Ja Morant", layer1_df, sim_matrix, k=5)