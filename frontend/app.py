import sys
import os

# Add project root directory to Python path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from utils.data_processing import normalise_stats
from utils.nba_api_wrapper import DataCollection
from utils.k_nearest import top_k_similar_players, compute_similarity
from utils.data_processing import weighted_player_averages


# ------------------------
# Streamlit App
# ------------------------
st.set_page_config(page_title="NBA Player Similarity", layout="wide")
st.title("🏀 NBA Player Similarity Search - Layer 1")
st.markdown(
    """
    Enter a player name to find the top-k most similar players based on basic per-game stats.
    Older seasons are weighted less in the similarity calculation.
    """
)

# --- User Inputs ---
player_name = st.text_input("Player Name", "Ja Morant")
k = st.slider("Top-k similar players", min_value=1, max_value=20, value=5)

# --- Search ---
if st.button("Find Similar Players"):
    try:
        dc = DataCollection("data/nba_stats.db")
        layer1_df = dc.get_last_n_years_stats(per_mode="PerGame")
        dc.save_to_sql(layer1_df, table_name="layer1_basic_stats")
        layer1_df = layer1_df.groupby('PLAYER_NAME').apply(weighted_player_averages, include_groups=False).reset_index()

        df_normalised = normalise_stats(layer1_df)
        sim_matrix = compute_similarity(df_normalised)
        top5 = top_k_similar_players("Ja Morant", layer1_df, sim_matrix, k=5)
        top_players = top_k_similar_players(player_name, layer1_df, sim_matrix, k)

        st.success(f"Top {k} players similar to {player_name}")
        st.dataframe(top_players, width='stretch')

        # Optional: Radar chart comparing stats
        stats_columns = layer1_df.select_dtypes(include=np.number).columns.tolist()
        player_stats = layer1_df[layer1_df['PLAYER_NAME'] == player_name][stats_columns].mean()

        # Create radar chart for top player comparison
        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        categories = stats_columns
        N = len(categories)

        # Player values
        values = player_stats.values
        values = list(values) + [values[0]]  # Close the loop

        angles = [n / float(N) * 2 * 3.14159 for n in range(N)]
        angles += [angles[0]]

        ax.plot(angles, values, linewidth=2, linestyle='solid', label=player_name)
        ax.fill(angles, values, alpha=0.25)

        # Top similar players (first one for illustration)
        if not top_players.empty:
            top1_name = top_players.iloc[0]['PLAYER_NAME']
            top1_stats = layer1_df[layer1_df['PLAYER_NAME'] == top1_name][stats_columns].mean()
            top1_values = list(top1_stats.values) + [top1_stats.values[0]]
            ax.plot(angles, top1_values, linewidth=2, linestyle='dashed', label=top1_name)
            ax.fill(angles, top1_values, alpha=0.25)

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=8)
        ax.set_title("Player Stats Radar Chart", size=14, y=1.1)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))

        st.pyplot(fig)

    except Exception as e:
        st.error(f"Error: {e}")
        st.stop()
