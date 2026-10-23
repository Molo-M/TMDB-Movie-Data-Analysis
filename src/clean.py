"""
clean.py
Step 2: Clean and preprocess the raw movie data.
Each function does one cleaning step. clean_data() runs all of them in order.
"""

import numpy as np
import pandas as pd

from src.config import COLUMNS_TO_DROP, NAME_LIST_COLUMNS, FINAL_COLUMN_ORDER, CLEAN_DATA_PATH


# ----------------------------------------------------------------------
# Helper functions (used with .apply on a single value)
# ----------------------------------------------------------------------

def clean_names(column):
    """Join the "name" of each dictionary in a list with "|"."""
    if isinstance(column, list):
        names = []
        for name in column:
            names.append(name["name"])
        return "|".join(names)
    else:
        return None


def clean_cast(cast):
    """Join the names of all cast members with "|"."""
    names = []
    for member in cast:
        names.append(member["name"])
    return "|".join(names)


def clean_crew(crew):
    """Join the names of the directors in the crew with "|"."""
    names = []
    for member in crew:
        if member["job"] == "Director":
            names.append(member["name"])
    return "|".join(names)


def get_collection_name(collection):
    """Return the collection name, or None if the movie isn't in a collection."""
    if isinstance(collection, dict):
        return collection["name"]
    else:
        return None


# ----------------------------------------------------------------------
# Cleaning steps (each takes a DataFrame and returns a DataFrame)
# ----------------------------------------------------------------------

def drop_irrelevant_columns(df):
    """Drop the columns we don't need."""
    return df.drop(columns=COLUMNS_TO_DROP, errors="ignore")


def extract_collection(df):
    """Replace the belongs_to_collection dictionary with just the collection name."""
    df["belongs_to_collection"] = df["belongs_to_collection"].apply(get_collection_name)
    return df


def extract_credits(df):
    """Split the credits column into cast, cast_size, director and crew_size."""
    # Extract the dictionary keys into a temporary dataframe
    credits_df = df["credits"].apply(pd.Series)

    # Count the cast and crew before turning them into strings
    df["cast_size"] = credits_df["cast"].apply(len)
    df["crew_size"] = credits_df["crew"].apply(len)

    # Keep only the names
    df["cast"] = credits_df["cast"].apply(clean_cast)
    df["director"] = credits_df["crew"].apply(clean_crew)

    # Drop the uncleaned column now that the new clean columns have been added
    return df.drop(columns=["credits"])


def extract_names(df):
    """Clean genres, spoken languages, production countries and companies."""
    for col in NAME_LIST_COLUMNS:
        df[col] = df[col].apply(clean_names)
    return df


def convert_types(df):
    """Convert columns to the right data types (invalid values become NaN)."""
    for col in ["budget", "id", "popularity"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
    return df


def replace_unrealistic_values(df):
    """Replace values that don't make sense with NaN."""
    # A budget, revenue or runtime of 0 means the value is unknown
    for col in ["budget", "revenue", "runtime"]:
        df[col] = df[col].replace(0, np.nan)

    # A movie with no votes can't have a meaningful rating
    df.loc[df["vote_count"] == 0, "vote_average"] = np.nan

    # Replace placeholder text with NaN
    for col in ["overview", "tagline"]:
        df[col] = df[col].replace(["No Data", ""], np.nan)

    return df


def convert_to_millions(df):
    """Convert budget and revenue to million USD and rename the columns."""
    df["budget_musd"] = round(df["budget"] / 1_000_000, 2)
    df["revenue_musd"] = round(df["revenue"] / 1_000_000, 2)
    return df.drop(columns=["budget", "revenue"])


def remove_bad_rows(df):
    """Remove duplicates, rows without id/title, and rows with too much missing data."""
    df = df.drop_duplicates(subset=["id"])
    df = df.dropna(subset=["id", "title"])
    # Keep only rows where at least 10 columns have non-NaN values
    df = df.dropna(thresh=10)
    return df


def filter_released(df):
    """Keep only movies that have been released, then drop the status column."""
    df = df[df["status"] == "Released"]
    return df.drop(columns=["status"])


def reorder_columns(df):
    """Put the columns in the final order and reset the index."""
    # Selecting the columns this way raises an error if a column name doesn't exist,
    # instead of silently creating an empty column
    df = df[FINAL_COLUMN_ORDER]
    return df.reset_index(drop=True)


# ----------------------------------------------------------------------
# Run every step
# ----------------------------------------------------------------------

def clean_data(raw_df):
    """Run all the cleaning steps in order and return the clean DataFrame."""
    df = raw_df.copy()
    df = drop_irrelevant_columns(df)
    df = extract_collection(df)
    df = extract_credits(df)
    df = extract_names(df)
    df = convert_types(df)
    df = replace_unrealistic_values(df)
    df = convert_to_millions(df)
    df = remove_bad_rows(df)
    df = filter_released(df)
    df = reorder_columns(df)
    return df


def compare_before_after(raw_df, clean_df):
    """Build a small table comparing the raw data and the clean data."""
    rows = [
        {"Metric": "Rows",
         "Before": raw_df.shape[0], "After": clean_df.shape[0]},
        {"Metric": "Columns",
         "Before": raw_df.shape[1], "After": clean_df.shape[1]},
        {"Metric": "Missing values (total)",
         "Before": raw_df.isna().sum().sum(), "After": clean_df.isna().sum().sum()},
        {"Metric": "Duplicate ids",
         "Before": raw_df["id"].duplicated().sum(), "After": clean_df["id"].duplicated().sum()},
    ]
    return pd.DataFrame(rows)


def missing_values(df):
    """Count the missing values in each column (only columns with at least one)."""
    counts = df.isna().sum()
    return counts[counts > 0]


def save_clean_data(df, path=CLEAN_DATA_PATH):
    """Save the clean DataFrame to a CSV file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    print(f"Saved clean data to {path}")