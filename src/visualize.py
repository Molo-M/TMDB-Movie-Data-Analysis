"""
visualize.py
Step 4: Data visualization.
One function per chart. Each function can show the chart, save it, or both.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def finish_plot(save_path=None, show=True):
    """Save the current chart (if a path is given) and/or show it."""
    if save_path is not None:
        save_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, bbox_inches="tight")
        print(f"Saved figure to {save_path}")
    if show:
        plt.show()
    plt.close()


# ----------------------------------------------------------------------
# Exploratory Data Analysis (EDA) charts
# ----------------------------------------------------------------------

def plot_distributions(df, save_path=None, show=True):
    """Histograms of budget, revenue, rating and runtime side by side."""
    columns = ["budget_musd", "revenue_musd", "vote_average", "runtime"]
    titles = ["Budget (million USD)", "Revenue (million USD)", "Rating", "Runtime (minutes)"]

    fig, axes = plt.subplots(1, 4, figsize=(16, 4))
    for ax, column, title in zip(axes, columns, titles):
        ax.hist(df[column].dropna(), bins=8, color="skyblue", edgecolor="black")
        ax.set_title(title)
        ax.set_ylabel("Number of movies")
    plt.suptitle("Distributions of Key Numeric Columns")
    plt.tight_layout()
    finish_plot(save_path, show)


def plot_genre_counts(df, save_path=None, show=True):
    """Horizontal bar chart of how many movies belong to each genre."""
    # Split movies with several genres into one row per genre
    genre_counts = df["genres"].str.split("|").explode().value_counts().sort_values()

    plt.figure()
    plt.barh(genre_counts.index, genre_counts.values, color="skyblue", edgecolor="black")
    plt.title("Number of Movies per Genre")
    plt.xlabel("Number of movies")
    plt.ylabel("Genre")
    finish_plot(save_path, show)


def plot_correlations(df, save_path=None, show=True):
    """Heatmap of the correlations between the numeric columns."""
    numeric_columns = ["budget_musd", "revenue_musd", "vote_count", "vote_average",
                       "popularity", "runtime"]
    correlations = df[numeric_columns].corr()

    plt.figure(figsize=(7, 5))
    sns.heatmap(correlations, annot=True, fmt=".2f", cmap="coolwarm", vmin=-1, vmax=1)
    plt.title("Correlation Between Numeric Columns")
    finish_plot(save_path, show)


# ----------------------------------------------------------------------
# Step 4 charts
# ----------------------------------------------------------------------

def plot_revenue_vs_budget(df, save_path=None, show=True):
    """Scatter plot of revenue against budget with a trend line."""
    plt.figure()
    sns.regplot(x=df["budget_musd"], y=df["revenue_musd"], ci=None,
                line_kws={"color": "red", "linestyle": "--"})
    plt.title("Revenue vs. Budget Trend")
    plt.xlabel("Budget (million USD)")
    plt.ylabel("Revenue (million USD)")
    finish_plot(save_path, show)


def plot_roi_by_genre(df, save_path=None, show=True):
    """Horizontal bar chart of the average ROI for each genre."""
    # Split movies with several genres into one row per genre
    genre_df = df.assign(genre_split=df["genres"].str.split("|")).explode("genre_split")
    genre_roi = genre_df.groupby("genre_split")["roi"].mean().sort_values(ascending=True)

    plt.figure()
    plt.barh(genre_roi.index, genre_roi.values, color="skyblue", edgecolor="black")
    plt.title("ROI Distribution by Genre")
    plt.xlabel("Average ROI")
    plt.ylabel("Genre")
    finish_plot(save_path, show)


def plot_popularity_vs_rating(df, save_path=None, show=True):
    """Scatter plot of rating against popularity with a trend line."""
    plt.figure()
    sns.regplot(x=df["popularity"], y=df["vote_average"], ci=None,
                line_kws={"color": "purple", "linestyle": "--"})
    plt.title("Popularity vs. Rating")
    plt.xlabel("Popularity")
    plt.ylabel("Vote Average (Rating)")
    finish_plot(save_path, show)


def plot_yearly_revenue(df, save_path=None, show=True):
    """Line chart of total revenue per release year."""
    year_df = df.copy()
    year_df["release_year"] = year_df["release_date"].dt.year
    year_revenue = year_df.groupby("release_year")["revenue_musd"].sum()

    plt.figure()
    plt.plot(year_revenue.index, year_revenue.values, marker="o")
    plt.title("Yearly Trends in Box Office Performance")
    plt.xlabel("Release Year")
    plt.ylabel("Revenue (million USD)")
    finish_plot(save_path, show)


def plot_franchise_vs_standalone(df, save_path=None, show=True):
    """Line chart of revenue over the years, split into franchise and standalone movies."""
    franchise_df = df.copy()
    franchise_df["release_year"] = franchise_df["release_date"].dt.year
    franchise_df["franchise"] = np.where(franchise_df["belongs_to_collection"].isna(),
                                         "Standalone", "Franchise")

    plt.figure()
    sns.lineplot(data=franchise_df, x="release_year", y="revenue_musd",
                 hue="franchise", marker="o")
    plt.title("Franchise vs. Standalone Success")
    plt.xlabel("Release Year")
    plt.ylabel("Revenue (million USD)")
    finish_plot(save_path, show)