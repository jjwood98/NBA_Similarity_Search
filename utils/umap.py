import numpy as np
import umap
from sklearn.metrics.pairwise import cosine_similarity
from utils.faiss_index import build_faiss_index


def compute_umap_similarity(
        df_normalised,
        n_neighbors=40,
        min_dist=0.1,
        n_components=12,
        metric='cosine',
        random_state=42
):

    df_numeric = df_normalised.select_dtypes(include=np.number)
    umap_model = umap.UMAP(
        n_neighbors=n_neighbors,
        min_dist=min_dist,
        n_components=n_components,
        metric=metric,
        random_state=random_state
    )

    embedding = umap_model.fit_transform(df_numeric.values)
    embedding = embedding.astype('float32')

    build_faiss_index(embedding)
    embedding_norm = embedding / np.linalg.norm(embedding, axis=1, keepdims=True)
    sim_matrix = cosine_similarity(embedding_norm)

    return sim_matrix, embedding_norm, embedding, umap_model
