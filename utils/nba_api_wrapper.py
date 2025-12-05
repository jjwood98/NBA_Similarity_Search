from datetime import datetime
from nba_api.stats.endpoints import LeagueDashPlayerStats, SynergyPlayTypes, LeagueDashPlayerStats, LeagueDashPtDefend
import pandas as pd
import sqlite3
import time
from utils.data_processing import combine_multi_team_rows, clean_data_features


class DataCollection:
    def __init__(self, db_path="data/nba_stats.db"):
        """
        db_path: path to SQLite database file
        """
        self.db_path = db_path

    def get_last_n_years_stats(self, per_mode, measure_type = None, n_years=5):
        """
        Pulls NBA player stats for the last `n_years` seasons.
        Returns a single DataFrame with all seasons concatenated.
        """
        current_year = datetime.today().year
        current_month = datetime.today().month

        # Determine the current season start year
        if current_month >= 10:
            season_start = current_year
        else:
            season_start = current_year - 1

        # Generate season strings, e.g., "2020-21"
        seasons = [f"{y}-{str(y + 1)[-2:]}" for y in range(season_start - n_years + 1, season_start + 1)]

        all_stats = []
        print(f"Pulling {measure_type } Stats")
        for season in seasons:
            try:
                if measure_type is None:
                    df = LeagueDashPlayerStats(
                        season=season,
                        season_type_all_star="Regular Season",
                        per_mode_detailed=per_mode,
                    ).get_data_frames()[0]
                    df['Season'] = season  # add season column

                    cols_to_drop = [
                        'PLAYER_ID', 'NICKNAME', 'TEAM_ID', 'TEAM_ABBREVIATION',
                        'W', 'L', 'W_PCT', 'NBA_FANTASY_PTS', 'WNBA_FANTASY_PTS',
                        'GP_RANK', 'W_RANK', 'L_RANK', 'W_PCT_RANK', 'MIN_RANK',
                        'FGM_RANK', 'FGA_RANK', 'FG_PCT_RANK', 'FG3M_RANK', 'FG3A_RANK',
                        'FG3_PCT_RANK', 'FTM_RANK', 'FTA_RANK', 'FT_PCT_RANK', 'OREB_RANK',
                        'DREB_RANK', 'REB_RANK', 'AST_RANK', 'TOV_RANK', 'STL_RANK', 'BLK_RANK',
                        'BLKA_RANK', 'PF_RANK', 'PFD_RANK', 'PTS_RANK', 'PLUS_MINUS_RANK',
                        'NBA_FANTASY_PTS_RANK', 'DD2_RANK', 'TD3_RANK', 'WNBA_FANTASY_PTS_RANK', 'TEAM_COUNT', 'NET_RATING', 'W_PCT'
                    ]

                else:

                    df = LeagueDashPlayerStats(
                        season=season,
                        season_type_all_star="Regular Season",
                        per_mode_detailed = per_mode,
                        measure_type_detailed_defense = measure_type,
                    ).get_data_frames()[0]
                    df['Season'] = season  # add season column

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
                        "FGA_PG_RANK", "FG_PCT_RANK", "TEAM_COUNT", 'AGE', 'GP', 'MIN', 'FGM', 'FGA', 'FG_PCT']

                #df = df.drop(columns=cols_to_drop)
                df = clean_data_features(df, measure_type= measure_type)

                all_stats.append(df)
            except Exception as e:
                print(f"Failed to pull {season}: {e}")

        final_df = pd.concat(all_stats, ignore_index=True)
        return final_df


    def get_player_playtpes(self, n_years=5):
        current_year = datetime.today().year
        current_month = datetime.today().month

        # Determine the current season start year
        if current_month >= 10:
            season_start = current_year
        else:
            season_start = current_year - 1

        # Generate season strings, e.g., "2020-21"
        seasons = [f"{y}-{str(y + 1)[-2:]}" for y in range(season_start - n_years + 1, season_start + 1)]

        playtpes = [
            "Transition", "Isolation", "PRBallHandler", "PRRollman", "Postup",
            "Spotup", "Handoff", "Cut", "OffScreen", "OffRebound", "Misc"]

        all_stats = []
        print("Pulling Playtype Stats")
        for season in seasons:
            season_frames = []
            try:
                for playtype in playtpes:
                    try:
                        df = SynergyPlayTypes(
                            per_mode_simple="PerGame",
                            season_type_all_star="Regular Season",
                            play_type_nullable=playtype,
                            season=season,
                            type_grouping_nullable="Offensive",
                            player_or_team_abbreviation="P"
                        ).get_data_frames()[0]
                        time.sleep(1.5)
                        cols_to_drop = ['SEASON_ID', 'TEAM_ID', 'TEAM_ABBREVIATION', 'PLAY_TYPE', 'PLAYER_ID', 'TEAM_NAME', 'TYPE_GROUPING']
                        df = df.drop(columns=cols_to_drop, errors='ignore')
                        df.rename(columns={'POSS_PCT': 'FREQ'}, inplace=True)

                        id_cols = ["PLAYER_NAME"]
                        stat_cols = [c for c in df.columns if c not in id_cols]

                        df_stats = df[stat_cols].add_prefix(f"{playtype}_")
                        df = pd.concat([df[id_cols], df_stats], axis=1)
                        df['Season'] = season  # add season column
                        df = combine_multi_team_rows(df)
                        season_frames.append(df)

                    except Exception as e:
                        print(f"  Failed play type {playtype} for {season}: {e}")
                        print(e)
                        continue

                season_df = season_frames[0]
                for f in season_frames[1:]:
                    season_df = season_df.merge(f, on=["PLAYER_NAME", "Season"], how="outer")

                patterns = ["_PERCENTILE", "_GP"]
                pattern_cols_to_drop = [col for col in season_df.columns if any(col.endswith(p) for p in patterns)]
                season_df = season_df.drop(columns=pattern_cols_to_drop, errors='ignore')
                all_stats.append(season_df)

            except Exception as e:
                print(f"Failed to pull {season}: {e}")


        final_df = pd.concat(all_stats, ignore_index=True)
        return final_df

    def get_def_stats(self, n_years=5):
        current_year = datetime.today().year
        current_month = datetime.today().month

        # Determine the current season start year
        if current_month >= 10:
            season_start = current_year
        else:
            season_start = current_year - 1

        # Generate season strings, e.g., "2020-21"
        seasons = [f"{y}-{str(y + 1)[-2:]}" for y in range(season_start - n_years + 1, season_start + 1)]

        #DefenseCategory
        deftypes = [
                "3 Pointers","2 Pointers","Less Than 6Ft","Less Than 10Ft","Greater Than 15Ft"]

        all_stats = []
        print(f"Pulling Defensive Stats")
        for season in seasons:
            season_frames = []
            try:
                for deftype in deftypes:
                    try:
                        df = LeagueDashPtDefend(
                            per_mode_simple="PerGame",
                            season_type_all_star="Regular Season",
                            defense_category = deftype,
                            season=season,
                        ).get_data_frames()[0]
                        time.sleep(1.5)
                        cols_to_drop = ['PLAYER_LAST_TEAM_ABBREVIATION', 'CLOSE_DEF_PERSON_ID', 'PLAYER_LAST_TEAM_ID', 'PLAYER_POSITION', 'AGE',
                                        'GP', 'G']
                        df = df.drop(columns=cols_to_drop, errors='ignore')

                        id_cols = ["PLAYER_NAME"]
                        stat_cols = [c for c in df.columns if c not in id_cols]

                        df_stats = df[stat_cols].add_prefix(f"{deftype}_")
                        df = pd.concat([df[id_cols], df_stats], axis=1)
                        df['Season'] = season  # add season column
                        season_frames.append(df)

                    except Exception as e:
                        print(f"  Failed play type {deftype} for {season}: {e}")
                        print(e)
                        continue

                season_df = season_frames[0]
                for f in season_frames[1:]:
                    season_df = season_df.merge(f, on=["PLAYER_NAME", "Season"], how="outer")

                all_stats.append(season_df)

            except Exception as e:
                print(f"Failed to pull {season}: {e}")

        final_df = pd.concat(all_stats, ignore_index=True)
        return final_df


    def save_to_sql(self, df, table_name="player_stats"):
        """
        Saves a DataFrame to SQLite. Replaces existing table by default.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                df.to_sql(table_name, conn, if_exists='replace', index=False)
            print(f"Data saved to {self.db_path}, table: {table_name}")
        except Exception as e:
            print(f"Failed to save data to SQL: {e}")

