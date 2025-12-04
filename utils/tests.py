import pandas as pd


def check_playtype_frequencies(df, freq_suffix='FREQ'):
    ##Checks that the sum of all playtype frequencies for each player is ~100.
    # Select all columns ending with the frequency suffix
    freq_cols = [col for col in df.columns if col.endswith(freq_suffix)]
    print(freq_cols)

    # Calculate the sum of frequencies for each row
    df['total_frequency'] = df[freq_cols].sum(axis=1)

    # Flag rows where total frequency is not ~100
    flagged = df[(df['total_frequency'] < 99) | (df['total_frequency'] > 101)]

    # Optionally, round total_frequency for easier reading
    flagged['total_frequency'] = flagged['total_frequency'].round(2)

    return flagged[['PLAYER_NAME', 'Season'] + freq_cols + ['total_frequency']]

# Example usage:
# flagged_players = check_playtype_frequencies(all_stats_df)
# print(flagged_players)
