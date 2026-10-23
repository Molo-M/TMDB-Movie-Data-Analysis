"""
analysis.py
Step 3: KPIs and analysis.
Ranking movies, searching for movies, and comparing franchises and directors.
"""

import pandas as pd


def add_profit_and_roi(df):
    """Add a profit column (revenue - budget) and an ROI column (revenue / budget)."""
    df = df.copy()
    df["profit_musd"] = df["revenue_musd"] - df["budget_musd"]
    df["roi"] = df["revenue_musd"] / df["budget_musd"]
    return df


# ----------------------------------------------------------------------
# Best / worst performing movies
# ----------------------------------------------------------------------

def rank_movies(df, column_title, ascending=False, top_n=None):
    """Return the title and the chosen column, sorted by that column.
    ascending=False gives the highest first, ascending=True gives the lowest first."""
    ranked = df[["title", column_title]].sort_values(by=column_title, ascending=ascending)
    if top_n is not None:
        ranked = ranked.head(top_n)
    return ranked


def filter_min_budget(df, min_budget=10):
    """Keep only movies with a budget of at least min_budget million USD (used for ROI)."""
    return df[df["budget_musd"] >= min_budget]


def filter_min_votes(df, min_votes=10):
    """Keep only movies with at least min_votes votes (used for ratings)."""
    return df[df["vote_count"] >= min_votes]


# ----------------------------------------------------------------------
# Search queries
# ----------------------------------------------------------------------

def search_bruce_willis(df):
    """Search 1: Science Fiction Action movies starring Bruce Willis, best rated first."""
    mask = (
        df["cast"].str.contains("Bruce Willis", na=False)
        & df["genres"].str.contains("Science Fiction", na=False)
        & df["genres"].str.contains("Action", na=False)
    )
    return df[mask].sort_values(by="vote_average", ascending=False)


def search_uma_thurman_tarantino(df):
    """Search 2: movies starring Uma Thurman directed by Quentin Tarantino, shortest first."""
    mask = (
        df["cast"].str.contains("Uma Thurman", na=False)
        & df["director"].str.contains("Quentin Tarantino", na=False)
    )
    return df[mask].sort_values(by="runtime", ascending=True)


# ----------------------------------------------------------------------
# Franchise vs. standalone
# ----------------------------------------------------------------------

def calculate_statistics(df, column, statistic):
    """Calculate a statistic (e.g. "mean", "median") for franchise and standalone movies.
    Returns the two values: (franchise_value, standalone_value)."""
    # Separate data into those that belong to a movie collection and those that don't
    belongs_collection = df[df["belongs_to_collection"].notna()]
    not_belongs_collection = df[df["belongs_to_collection"].isna()]

    # Calculate the requested statistic
    franchise_value = getattr(belongs_collection[column], statistic)()
    standalone_value = getattr(not_belongs_collection[column], statistic)()

    return franchise_value, standalone_value


def franchise_vs_standalone(df):
    """Build a table comparing franchise and standalone movies on every metric."""
    metrics = [
        ("Mean Revenue (M USD)", "revenue_musd", "mean"),
        ("Median ROI", "roi", "median"),
        ("Mean Budget (M USD)", "budget_musd", "mean"),
        ("Mean Popularity", "popularity", "mean"),
        ("Mean Rating", "vote_average", "mean"),
    ]

    rows = []
    for label, column, statistic in metrics:
        franchise_value, standalone_value = calculate_statistics(df, column, statistic)
        rows.append({"Metric": label, "Franchise": franchise_value, "Standalone": standalone_value})

    return pd.DataFrame(rows)


# ----------------------------------------------------------------------
# Most successful franchises and directors
# ----------------------------------------------------------------------

def franchise_summary(df):
    """Summarise each franchise: number of movies, budget, revenue and rating."""
    summary = df.groupby("belongs_to_collection").agg(
        movie_count=("id", "count"),
        total_budget_musd=("budget_musd", "sum"),
        mean_budget_musd=("budget_musd", "mean"),
        total_revenue_musd=("revenue_musd", "sum"),
        mean_revenue_musd=("revenue_musd", "mean"),
        mean_rating=("vote_average", "mean"),
    )
    return summary.sort_values(by="total_revenue_musd", ascending=False)


def director_summary(df):
    """Summarise each director: number of movies, total revenue and mean rating."""
    # Create a new dataframe where movies with several directors are split into one row each
    director_df = df.assign(director_split=df["director"].str.split("|")).explode("director_split")

    summary = director_df.groupby("director_split").agg(
        movie_count=("id", "count"),
        total_revenue_musd=("revenue_musd", "sum"),
        mean_rating=("vote_average", "mean"),
    )
    return summary.sort_values(by="total_revenue_musd", ascending=False)