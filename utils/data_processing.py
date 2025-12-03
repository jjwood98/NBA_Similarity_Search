from sklearn.preprocessing import StandardScaler
import numpy as np
import pandas as pd

def normalise_stats(df):
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    scaler = StandardScaler()
    df_scaled = df.copy()
    df_scaled[numeric_cols] = scaler.fit_transform(df_scaled[numeric_cols])
    return df_scaled

def weighted_player_averages(group, decay = 0.8):
    group = group.sort_values(by=["Season"], ascending=False)
    numeric_cols = group.select_dtypes(include=np.number).columns.tolist()
    weights = pd.Series([decay**i for i in range(len(group))], index= group.index)
    weighted = (group[numeric_cols].T * weights).T.sum() / weights.sum()
    return weighted


def merge_df(df1, df2):
    shared = df1.columns.intersection(df2.columns)
    df = df1.merge(df2, on=list(shared))

    return df

def combine_team_rows(df, playtypes):
    id_cols = ["PLAYER_NAME", "Season"]
    agg_frames = []

    for pt in playtypes:
        pt_cols = [c for c in df.columns if c.startswith(pt + "_")]
        if not pt_cols:
            continue

        sub = df[id_cols + pt_cols].copy()

        # Identify sums vs weighted averages
        count_cols = [c for c in pt_cols if any(x in c for x in
                      ["GP", "POSS", "PTS", "FGM", "FGA", "FGMX"])]
        rate_cols = [c for c in pt_cols if c not in count_cols]

        poss_col = next((c for c in count_cols if c.endswith("_POSS")), None)

        def agg(player_df):
            out = {}
            # Count stats → sum
            for c in count_cols:
                out[c] = player_df[c].sum()

            # Rate stats → weighted
            for c in rate_cols:
                if poss_col is None:
                    out[c] = None
                else:
                    weights = player_df[poss_col].fillna(0)
                    if weights.sum() == 0:
                        out[c] = None
                    else:
                        out[c] = (player_df[c] * weights).sum() / weights.sum()
            return pd.Series(out)

        agg_df = sub.groupby(id_cols).apply(agg).reset_index()
        agg_frames.append(agg_df)

    # Merge all playtypes wide
    final = agg_frames[0]
    for f in agg_frames[1:]:
        final = final.merge(f, on=id_cols, how="outer")

    return final



def combine_multi_team_rows(df):
    #Combine multiple rows for the same player into a single row.

    # Weighting rules:
    #   - GP: sum across teams
    #   - Per-game metrics (PTS, FGM, FGA, POSS, etc.): weighted by GP
    #   - Efficiency/per-possession metrics (PPP, TOV_POSS_PCT, SF_POSS_PCT, PLUSONE_POSS_PCT, SCORE_POSS_PCT): weighted by POSS
    #   - Percentages (FG_PCT, EFG_PCT): weighted by FGA
    #   - PERCENTILE: optional weighted by GP or leave as first value

    # Identify columns
    gp_col = [c for c in df.columns if "GP" in c][0]
    poss_col = [c for c in df.columns if "POSS" in c and "FREQ" not in c][0]  # total possessions
    fga_col = [c for c in df.columns if "FGA" in c][0]

    # Everything else
    columns = df.columns.tolist()
    weighted_cols = [c for c in columns if c not in ["PLAYER_NAME", "Season", gp_col]]

    def aggregate_player(group):
        weighted = {}
        total_gp = group[gp_col].sum()
        total_poss = (group[poss_col] * group[gp_col]).sum()  # total season possessions

        weighted[gp_col] = total_gp

        for c in weighted_cols:
            if c in ["PPP", "TOV_POSS_PCT", "SF_POSS_PCT", "PLUSONE_POSS_PCT", "SCORE_POSS_PCT"]:
                # Weighted by possessions
                weighted[c] = ((group[c] * group[poss_col] * group[gp_col]).sum()) / total_poss if total_poss > 0 else 0
            elif c in ["FG_PCT", "EFG_PCT"]:
                # Weighted by FGA
                total_fga = (group[fga_col] * group[gp_col]).sum()
                weighted[c] = ((group[c] * group[fga_col] * group[gp_col]).sum()) / total_fga if total_fga > 0 else 0
            elif c == "PERCENTILE":
                # Optional: take first non-null
                weighted[c] = group[c].iloc[0]
            else:
                # Weighted by GP (default for per-game metrics)
                weighted[c] = ((group[c] * group[gp_col]).sum()) / total_gp if total_gp > 0 else 0

        return pd.Series(weighted)

    combined_df = df.groupby(['PLAYER_NAME', 'Season']).apply(aggregate_player).reset_index()
    return combined_df

def clean_data_features(df, measure_type = None):
    cols_to_drop = ["AGE", "GP", "MIN", "W", "L","W_PCT", "POSS", "Season", ]
    if measure_type is None:
        cols_to_drop = [
            'PLAYER_ID', 'NICKNAME', 'TEAM_ID', 'TEAM_ABBREVIATION',
            'W', 'L', 'W_PCT', 'NBA_FANTASY_PTS', 'WNBA_FANTASY_PTS',
            'GP_RANK', 'W_RANK', 'L_RANK', 'W_PCT_RANK', 'MIN_RANK',
            'FGM_RANK', 'FGA_RANK', 'FG_PCT_RANK', 'FG3M_RANK', 'FG3A_RANK',
            'FG3_PCT_RANK', 'FTM_RANK', 'FTA_RANK', 'FT_PCT_RANK', 'OREB_RANK',
            'DREB_RANK', 'REB_RANK', 'AST_RANK', 'TOV_RANK', 'STL_RANK', 'BLK_RANK',
            'BLKA_RANK', 'PF_RANK', 'PFD_RANK', 'PTS_RANK', 'PLUS_MINUS_RANK',
            'NBA_FANTASY_PTS_RANK', 'DD2_RANK', 'TD3_RANK', 'WNBA_FANTASY_PTS_RANK', 'TEAM_COUNT',
        "AGE", "GP", "MIN", "W", "L","W_PCT"]

    else:
        cols_to_drop = [
            "GP_RANK", "W_RANK", 'NICKNAME', 'TEAM_ID', 'TEAM_ABBREVIATION', "L_RANK", 'PLAYER_ID',
            'E_OFF_RATING', 'sp_work_PACE', 'E_TOV_PCT',
            'sp_work_OFF_RATING', 'E_DEF_RATING', 'sp_work_DEF_RATING', 'E_NET_RATING',
            'sp_work_NET_RATING', 'E_USG_PCT', 'E_PACE',
            "W_PCT_RANK", "MIN_RANK", "E_OFF_RATING_RANK", "OFF_RATING_RANK", "sp_work_OFF_RATING_RANK",
            "E_DEF_RATING_RANK", "DEF_RATING_RANK", "sp_work_DEF_RATING_RANK",
            "E_NET_RATING_RANK", "NET_RATING_RANK", "sp_work_NET_RATING_RANK", "AST_PCT_RANK",
            "AST_TO_RANK", "AST_RATIO_RANK", "OREB_PCT_RANK", "DREB_PCT_RANK",
            "REB_PCT_RANK", "TM_TOV_PCT_RANK", "E_TOV_PCT_RANK", "EFG_PCT_RANK", "TS_PCT_RANK",
            "USG_PCT_RANK", "E_USG_PCT_RANK", "E_PACE_RANK",
            "PACE_RANK", "sp_work_PACE_RANK", "PIE_RANK", "FGM_RANK", "FGA_RANK", "FGM_PG_RANK",
            "FGA_PG_RANK", "FG_PCT_RANK", "TEAM_COUNT", 'AGE', 'GP', 'MIN', 'FGM', 'FGA', 'FG_PCT', 'POSS', 'W', 'L', 'OFF_RATING', 'DEF_RATING', 'PACE', 'PACE_PER40']

    df = df.drop(columns= cols_to_drop)
    return df
