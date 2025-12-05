import sys
import os

# Add project root directory to Python path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

FAISS_PATH = os.path.join(ROOT_DIR, "data/faiss/faiss_index.bin")
DF_PATH = os.path.join(ROOT_DIR, "data/faiss/df_original.parquet")

import streamlit as st
import pickle
import numpy as np
import pandas as pd
from utils.faiss_index import load_faiss_index, query_faiss
from frontend.feature_names import get_feature_names
from frontend.visuals import streamlit_visuals
from frontend.search_workflow import search_workflow

st.set_page_config(page_title="NBA Player Similarity", layout="wide")
st.title("🏀 NBA Player Similarity (FAISS)")

# Load FAISS + metadata once
@st.cache_resource
def load_index():
    index, metadata = load_faiss_index(FAISS_PATH)
    player_names = metadata["PLAYER_NAME"].tolist()
    embeddings = np.stack(metadata["embeddings"].values).astype("float32")
    df_original = pd.read_parquet(DF_PATH)
    return index, embeddings, player_names, df_original

index, embeddings, player_names, df_original = load_index()

# --- User Inputs ---
player_name = st.selectbox("Select Player", sorted(player_names))
k = st.slider("Top-k", 1, 20, 5)

if st.button("Search"):
    workflow = search_workflow(index, embeddings, player_names, df_original)
    df_results, num_top_feats = workflow.run(player_name, k)

    if df_results is not None:
        vs = streamlit_visuals(df_results, num_top_feats)
        vs.heatmap_plot()
        vs.radar_plot()
