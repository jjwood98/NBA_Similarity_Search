import sqlite3
import pandas as pd
from nba_api.stats.endpoints import leaguedashplayerstats
from datetime import datetime

# Determine current NBA season
today = datetime.today()
year = today.year
month = today.month

# NBA season starts around October
if month >= 10:
    current_season_start = year
else:
    current_season_start = year - 1

# Generate last 5 seasons
seasons = []
for i in range(5):
    start = current_season_start - i
    end = start + 1
    season_str = f"{start}-{str(end)[-2:]}"
    seasons.append(season_str)

print("Fetching stats for seasons:", seasons)

# Connect to SQLite
conn = sqlite3.connect("data/nba_player_stats.db")

for season in seasons:
    print(f"Fetching {season} stats...")
    stats = leaguedashplayerstats.LeagueDashPlayerStats(
        season=season,
        season_type_all_star='Regular Season',
        per_mode_detailed='PerGame',
    )
    df = stats.get_data_frames()[0]
    df['Season'] = season  # Add season column

    # Append to SQLite
    df.to_sql("player_stats", conn, if_exists="append", index=False)

conn.close()
print("Done fetching and storing stats.")
