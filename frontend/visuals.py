import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import plotly.graph_objs as go
import math

class streamlit_visuals():
    def __init__(self, df_results, num_top_feats):
        self.df_results = df_results.copy()
        self.num_top_feats = num_top_feats


    def heatmap_plot(self):
        df_results = self.df_results
        num_top_feats = self.num_top_feats

        heatmap_data = pd.DataFrame()

        # Extract numeric contributions
        for i in range(1, num_top_feats + 1):
            col_name = f"Top Feature {i} (Contribution)"
            heatmap_data[col_name] = (
                df_results[col_name]
                .str.extract(r"\(([\d\.]+)%\)")[0]
                .astype(float)
            )

        heatmap_data.index = df_results['PLAYER_NAME']

        # Need the feature names for hover labels
        feature_names = pd.DataFrame()
        for i in range(1, num_top_feats + 1):
            col_name = f"Top Feature {i} (Contribution)"
            feature_names[col_name] = df_results[col_name].str.extract(r"^(.*?)\s*\(")[0]

        fig = go.Figure(
            data=go.Heatmap(
                z=heatmap_data.values,
                x=heatmap_data.columns,
                y=heatmap_data.index,
                colorscale="YlGnBu",
                text=feature_names.values,
                hovertemplate=(
                    "Player: %{y}<br>"
                    "Feature Slot: %{x}<br>"
                    "Feature Name: %{text}<br>"
                    "Contribution: %{z:.1f}%<extra></extra>"
                )
            )
        )

        fig.update_layout(
            title="Top Feature Contributions (%) for Similar Players",
            width=1200,
            height=800,
            margin=dict(l=80, r=80, t=80, b=80)
        )

        st.plotly_chart(fig, width='content')

    def radar_plot(self):
        df_results = self.df_results
        num_top_feats = self.num_top_feats


        # 3 Radar plots per row uses the space better
        columns_per_row = 3
        num_players = len(df_results)
        num_rows = math.ceil(num_players / columns_per_row)

        player_idx = 0

        for row in range(num_rows):
            cols = st.columns(columns_per_row)

            for col in cols:
                if player_idx >= num_players:
                    break

                player_row = df_results.iloc[player_idx]
                categories = []
                values = []

                for i in range(1, num_top_feats + 1):
                    feat_str = player_row[f"Top Feature {i} (Contribution)"]
                    name, pct = feat_str.split("(")
                    pct = pct.replace("%", "").replace(")", "").strip()
                    pct = float(pct)

                    categories.append(name.strip())
                    values.append(pct)

                categories += categories[:1]
                values += values[:1]

                fig = go.Figure(
                    data=[
                        go.Scatterpolar(
                            r=values,
                            theta=categories,
                            fill='toself',
                            name=player_row['PLAYER_NAME']
                        )
                    ],
                    layout=go.Layout(
                        polar=dict(
                            radialaxis=dict(
                                visible=True,
                                range=[0, max(values) + 10]
                            )
                        ),
                        showlegend=False,  # hide legend to save space
                        title=player_row['PLAYER_NAME']
                    )
                )

                col.plotly_chart(fig, use_container_width=True)
                player_idx += 1
