# TMDB Movie Data Analysis using Pandas and APIs

A data analysis pipeline that fetches data for 18 blockbuster movies from the [TMDB API](https://developer.themoviedb.org/docs), cleans it with Pandas, and analyzes which movies, franchises and directors performed best financially and with audiences.

### Project Links

| Deliverable          | Link                                                      |
| -------------------- | --------------------------------------------------------- |
| **Project Instructions** | [View Instructions](instructions.md)  |
| **Jupyter Notebook** | [View Notebook](notebooks/Movie-Analysis-Notebook.ipynb)  |
| **Report**           | [View Report](reports/Report.pdf)                         |

---

## Repository Structure

```text
TMDB-Movie-Data-Analysis/
├── data/
│   ├── raw/                  # movies_raw.json (saved API response, not committed)
│   └── processed/            # movies_clean.csv
├── notebooks/
│   └── Movie-Analysis-Notebook.ipynb   # step-by-step walkthrough of the analysis
├── src/
│   ├── __init__.py
│   ├── config.py             # movie IDs, API settings, file paths, column lists
│   ├── fetch.py              # Step 1: API extraction (with timeout and retries)
│   ├── clean.py              # Step 2: cleaning, preprocessing and before/after summary
│   ├── analysis.py           # Step 3: KPIs, searches, franchise/director stats
│   └── visualize.py          # EDA and Step 4 charts
├── reports/
│   ├── Report.pdf
│   └── figures/              # charts saved by main.py
├── main.py                   # runs the full pipeline end to end
├── requirements.txt
├── instructions.md           # Project description and instructions
├── .env.example              # template for the API token
├── .gitignore
└── README.md
```

---

## How to Run

1. Clone the repository and move into the project folder.
2. Create an environment and install the dependencies:
   - **pip:** `python -m venv venv`, activate it, then `pip install -r requirements.txt`
   - **Anaconda:** `conda create -n tmdb python=3.11`, `conda activate tmdb`, then `pip install -r requirements.txt`
3. Copy `.env.example`, rename the copy to `.env`, and add your TMDB API Read Access Token.
4. Run the full pipeline: `python main.py` (add `--refresh` to re-fetch data from the API).
   This prints all the results and saves the charts to `reports/figures/`.
5. To explore the analysis step by step, open `notebooks/Movie-Analysis-Notebook.ipynb` in Jupyter (`jupyter notebook`) or any editor that supports notebooks.

---

## Methodology

**1. Data extraction (`fetch.py`)**
Each movie is requested from the TMDB `/movie/{id}` endpoint together with its credits. Requests have a 10-second timeout, and temporary failures (network errors, rate limits, server errors) are retried up to 3 times. Invalid IDs, such as `0`, are reported and skipped. The raw response is saved to `data/raw/` so the analysis can be rerun without calling the API again.

**2. Cleaning and preprocessing (`clean.py`)**
Irrelevant columns are dropped. The nested JSON columns (collection, genres, languages, countries, companies, credits) are flattened into readable `|`-separated names, and cast size, crew size and director(s) are extracted from the credits. Data types are converted, and unrealistic values (zero budget/revenue/runtime, ratings with no votes, placeholder text) are replaced with `NaN`. Budget and revenue are converted to million USD. Duplicates, rows missing an id or title, rows with fewer than 10 non-missing values, and unreleased movies are removed. A before/after summary shows what the cleaning changed.

**3. Exploratory data analysis (`Movie-Analysis-Notebook.ipynb` and `visualize.py`)**
Summary statistics, distributions of budget, revenue, rating and runtime, genre counts, release years, and correlations between the numeric columns.

**4. KPIs and analysis (`analysis.py`)**
Profit (revenue − budget) and ROI (revenue ÷ budget) are calculated. Movies are ranked on revenue, budget, profit, ROI (budget ≥ \$10M only), votes, rating (≥ 10 votes only) and popularity, using a single ranking function. The analysis also includes two cast/director search queries, a franchise vs. standalone comparison, and summary tables for franchises and directors.

**5. Visualization (`visualize.py`)**
Revenue vs. budget, ROI by genre, popularity vs. rating, yearly box office trends, and franchise vs. standalone revenue over time.

---

## Key Findings

- **All 18 movies are major blockbusters.** Revenues range from \$1.24B to \$2.94B, and even the least profitable movie (*Star Wars: The Last Jedi*) made over \$1B in profit. Results therefore describe top-grossing movies, not movies in general.
- **Avengers: Endgame earned the most revenue (\$2.94B), but Avatar was the better investment.** *Avatar* has the highest profit (\$2.69B) and the highest ROI, earning 12.3 times its budget.
- **The Avengers Collection is the most successful franchise.** Its 4 movies earned \$7.9B in total, with a mean rating of 7.96. Avengers movies also lead in vote count and popularity.
- **Franchise vs. standalone results are not conclusive.** Franchise movies had bigger budgets (\$218M vs. \$180M on average) and higher popularity. The 2 standalone movies (*Titanic* and *Beauty and the Beast*) had slightly higher mean revenue and ROI, but 2 movies is too small a sample to compare fairly.
- **James Cameron is the top director by revenue** (\$5.19B from *Avatar* and *Titanic*). Anthony and Joe Russo have the highest mean rating (8.25) for *Avengers: Infinity War* and *Endgame*.
- **Neither search query returned results.** No movie in the dataset stars Bruce Willis, or stars Uma Thurman under Quentin Tarantino's direction.

See the [notebook](notebooks/Movie-Analysis-Notebook.ipynb) for the full analysis and charts, and the [report](reports/Report.pdf) for a summary of insights and conclusions.

---

## Tools

Python, Pandas, NumPy, Matplotlib, Seaborn, Requests, python-dotenv, Jupyter.