import argparse
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

# === Load Environment === #
load_dotenv()
DATA_PATH = os.getenv("DATA_PATH")
DATA_FILE = os.getenv("DATA_FILE")
OUTPUT_FILE = os.path.join(DATA_PATH, DATA_FILE)

# === CLI === #
parser = argparse.ArgumentParser()
parser.add_argument("--compile-info", nargs="+", required=True)
parser.add_argument("--run-info", nargs="+", required=True)
args = parser.parse_args()

# === Constants === #
COLUMN_RENAME = {
    "id": "id",
    "DN=": "n",
    "OMP_NUM_THREADS": "threads",
    "fopenmp": "OpenMP",
    "time": "time",
}


# === Utility Functions === #
# def load_and_concatenate(csv_paths):
#     """Load multiple CSVs and concatenate, filling missing columns with 0."""
#     dfs = [pd.read_csv(csv) for csv in csv_paths]
#     # all_columns = pd.Index([]).union_many([df.columns for df in dfs])
#     all_columns = pd.Index([]).union(*[df.columns for df in dfs])
#     return pd.concat(
#         [df.reindex(columns=all_columns, fill_value=0) for df in dfs], ignore_index=True
#     )
def load_and_concatenate(csv_paths):
    """Load multiple CSVs and concatenate, filling missing columns with 0."""
    dfs = [pd.read_csv(csv) for csv in csv_paths]

    # Get the union of all columns across all dataframes
    all_columns = pd.Index([])

    # Append columns from each dataframe into all_columns
    for df in dfs:
        all_columns = all_columns.union(df.columns)

    # Reindex each dataframe to have all columns, filling missing columns with 0
    return pd.concat(
        [df.reindex(columns=all_columns, fill_value=0) for df in dfs], ignore_index=True
    )


def merge_on_id(df1, df2):
    """Inner join on 'id' column."""
    return pd.merge(df2, df1, on="id", how="inner")


def drop_rows_with_values(df, criteria):
    """Remove rows with specific values per column."""
    mask = pd.Series(True, index=df.index)
    for col, vals in criteria.items():
        mask &= ~df[col].isin(vals if isinstance(vals, (list, set, tuple)) else [vals])
    return df[mask].copy()


# === Main Execution === #
if __name__ == "__main__":
    compile_df = load_and_concatenate(args.compile_info)
    run_df = load_and_concatenate(args.run_info)

    merged_df = merge_on_id(compile_df, run_df)
    renamed_df = merged_df.rename(columns=COLUMN_RENAME)

    renamed_df.to_csv(OUTPUT_FILE, index=False)
