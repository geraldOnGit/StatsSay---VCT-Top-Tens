import pandas as pd
from sklearn.preprocessing import MinMaxScaler




def get_top_players_by_year(year: int, data_folder: str = "data") -> dict:
    """
    Loads the VCT dataset for a given year and returns the top 10 players
    per tournament based on performance metrics.

    Args:
        year (int): Year to analyze (2021–2025)
        data_folder (str): Folder where yearly CSVs are stored

    Returns:
        dict: {tournament_name: top_10_players DataFrame}
    """
    # Load the CSV file for the year
    file_path = f"{data_folder}/{year}.csv"
    df = pd.read_csv(file_path)
    df['Year'] = year  # Add Year column if needed

    # Clean percentage columns
    percent_columns = ['Headshot %', 'Clutch Success %', 'Kill, Assist, Trade, Survive %']
    for col in percent_columns:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: str(x).rstrip('%') if isinstance(x, str) else x)
            df[col] = pd.to_numeric(df[col], errors='coerce') / 100

    # Recalculate K:D Ratio
    df['K:D Ratio'] = df['Kills'] / df['Deaths']

    # Metrics to include
    extended_metrics = [
        'Kill, Assist, Trade, Survive %',
        'Average Combat Score',
        'Clutch Success %',
        'Average Damage Per Round',
        'K:D Ratio',
        'Headshot %',
        'First Kills'
    ]

    top_10_by_tournament = {}

    for tournament in df['Tournament'].dropna().unique():
        tournament_df = df[df['Tournament'] == tournament].copy()

        # Filter players with at least 50 rounds
        tournament_df = tournament_df[tournament_df['Rounds Played'] >= 180]

        # Drop rows with missing values in key metrics
        tournament_df = tournament_df.dropna(subset=extended_metrics)

        if tournament_df.empty:
            continue

        # Group by player and average metrics
        grouped = tournament_df.groupby('Player')[extended_metrics].mean().reset_index()

        # Normalize
        scaler = MinMaxScaler()
        grouped_scaled = grouped.copy()
        grouped_scaled[extended_metrics] = scaler.fit_transform(grouped[extended_metrics])

        # Composite score
        grouped_scaled['Composite Score'] = grouped_scaled[extended_metrics].mean(axis=1)

        # Top 10
        top_10 = grouped_scaled.sort_values('Composite Score', ascending=False).head(10).reset_index(drop=True)
        top_10_by_tournament[tournament] = top_10

    return top_10_by_tournament
