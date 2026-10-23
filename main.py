"""
main.py
Runs the whole pipeline from start to finish:
fetch -> clean -> analyse -> visualise.

Usage:
    python main.py            # uses the saved raw data if it exists
    python main.py --refresh  # fetches fresh data from the API
"""

import sys
import pandas as pd

from src import fetch, clean, analysis, visualize
from src.config import FIGURES_DIR


def print_section(title):
    """Print a title so the output is easy to read."""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def main():
    # Show all columns when printing tables in the terminal
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", None)

    refresh = "--refresh" in sys.argv

    # Step 1: Fetch the data
    print_section("Step 1: Fetching data")
    raw_df = fetch.load_or_fetch(refresh=refresh)

    # Step 2: Clean the data
    print_section("Step 2: Cleaning data")
    df = clean.clean_data(raw_df)
    clean.save_clean_data(df)
    print("\nBefore vs. after cleaning:")
    print(clean.compare_before_after(raw_df, df).to_string(index=False))
    print("\nMissing values per column after cleaning:")
    print(clean.missing_values(df))
    print("\nSummary statistics of the clean data:")
    print(df.describe().round(2))

    # Step 3: KPIs and analysis
    df = analysis.add_profit_and_roi(df)

    print_section("Step 3: Best / Worst Performing Movies")
    budget_10m = analysis.filter_min_budget(df)
    votes_10 = analysis.filter_min_votes(df)

    rankings = [
        ("Highest Revenue", df, "revenue_musd", False),
        ("Highest Budget", df, "budget_musd", False),
        ("Highest Profit", df, "profit_musd", False),
        ("Lowest Profit", df, "profit_musd", True),
        ("Highest ROI (budget >= 10M)", budget_10m, "roi", False),
        ("Lowest ROI (budget >= 10M)", budget_10m, "roi", True),
        ("Most Voted", df, "vote_count", False),
        ("Highest Rated (>= 10 votes)", votes_10, "vote_average", False),
        ("Lowest Rated (>= 10 votes)", votes_10, "vote_average", True),
        ("Most Popular", df, "popularity", False),
    ]
    for title, data, column, ascending in rankings:
        print(f"\n{title}:")
        print(analysis.rank_movies(data, column, ascending=ascending, top_n=5).to_string(index=False))

    print_section("Search Queries")
    print("\nSci-Fi Action movies starring Bruce Willis:")
    print(analysis.search_bruce_willis(df)[["title", "vote_average"]])
    print("\nUma Thurman movies directed by Quentin Tarantino:")
    print(analysis.search_uma_thurman_tarantino(df)[["title", "runtime"]])

    print_section("Franchise vs. Standalone")
    print(analysis.franchise_vs_standalone(df).to_string(index=False))

    print_section("Most Successful Franchises")
    print(analysis.franchise_summary(df))

    print_section("Most Successful Directors")
    print(analysis.director_summary(df))

    # Step 4: Visualizations (saved to reports/figures, not shown)
    print_section("Step 4: Saving charts")
    visualize.plot_distributions(df, FIGURES_DIR / "distributions.png", show=False)
    visualize.plot_genre_counts(df, FIGURES_DIR / "genre_counts.png", show=False)
    visualize.plot_correlations(df, FIGURES_DIR / "correlations.png", show=False)
    visualize.plot_revenue_vs_budget(df, FIGURES_DIR / "revenue_vs_budget.png", show=False)
    visualize.plot_roi_by_genre(df, FIGURES_DIR / "roi_by_genre.png", show=False)
    visualize.plot_popularity_vs_rating(df, FIGURES_DIR / "popularity_vs_rating.png", show=False)
    visualize.plot_yearly_revenue(df, FIGURES_DIR / "yearly_revenue.png", show=False)
    visualize.plot_franchise_vs_standalone(df, FIGURES_DIR / "franchise_vs_standalone.png", show=False)

    print("\nDone!")


if __name__ == "__main__":
    main()