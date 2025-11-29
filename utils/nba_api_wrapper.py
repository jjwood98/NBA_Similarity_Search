from datetime import datetime
from nba_api.stats.endpoints import LeagueDashPlayerStats
import pandas as pd
import sqlite3


class DataCollection:
    def __init__(self, db_path="nba_stats.db"):
        """
        db_path: path to SQLite database file
        """
        self.db_path = db_path

    def get_last_n_years_stats(self, n_years=5, per_mode="PerGame"):
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
        for season in seasons:
            print(f"Pulling stats for {season}...")
            try:
                df = LeagueDashPlayerStats(
                    season=season,
                    season_type_all_star="Regular Season",
                    per_mode_detailed =per_mode
                ).get_data_frames()[0]
                df['Season'] = season  # add season column
                all_stats.append(df)
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
