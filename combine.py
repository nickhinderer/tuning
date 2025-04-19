# import pandas as pd
# from tabulate import tabulate
# import argparse
# import matplotlib
# from dotenv import load_dotenv
# import os
# from pathlib import Path


# load_dotenv()
# FILE = os.path.join(os.getenv("DATA_PATH"), os.getenv("DATA_FILE"))
# parser = argparse.ArgumentParser()
# parser.add_argument("--compile-info", nargs="+")
# parser.add_argument("--run-info", nargs="+")
# args = parser.parse_args()

# # === Global Configuration === #

# COLUMN_RENAME = {
#     "id": "id",
#     "DN=": "n",
#     "OMP_NUM_THREADS": "threads",
#     "fopenmp": "OpenMP",
#     "time": "time",
# }

# # === ANSI Colors ===


# # TODO specify these somewhere more convenient
# def correct_erroneous_column_values(df):
#     df.loc[df["openMP"] == 0, "threads"] = 1
#     return


# # or alternatively:


# def drop_erroneous_rows_matching_values(df, criteria):
#     """Criteria of the form:
#     {
#         'column1' : [value1],
#         'column2' : [value2, value3]
#     }
#     """
#     mask = pd.Series([True] * len(df), index=df.index)
#     for col, vals in criteria.items():
#         vals = vals if isinstance(vals, (list, set, tuple)) else [vals]
#         mask &= ~df[col].isin(vals)
#     return df[mask].copy()

#     return


# def remove_outliers(threshold=None, number=0):
#     """Either remove by a given acceptable deviation or the top and bottom number specified"""
#     return


# def merge_csv_inner_join(compiler_data, run_data):
#     """Intended to be used to link the compiler variables with runtime variables based on executable name"""
#     # df1 = pd.read_csv(compiler_data)  # has unique ids
#     # df2 = pd.read_csv(run_data)  # has duplicates

#     # Merge on 'id', duplicating df1 rows as needed
#     return pd.merge(
#         run_data, compiler_data, on="id", how="inner"
#     )  # or 'inner' if you only want matching ids


# def concatenate_csv_fill_mutex_zeros(compiler_data1, compiler_data2):
#     """Intended to be used to concatenate two csv files generated from compilation"""
#     df1 = compiler_data1  # has unique ids
#     df2 = pd.read_csv(compiler_data2)
#     fill_value = 0

#     # Get union of all column names
#     all_columns = df1.columns.union(df2.columns)
#     print(all_columns)
#     # Reindex each DataFrame to have all columns, fill missing with fill_value
#     df1_filled = df1.reindex(columns=all_columns, fill_value=fill_value)
#     df2_filled = df2.reindex(columns=all_columns, fill_value=fill_value)

#     # Concatenate the two vertically
#     return pd.concat([df1_filled, df2_filled], ignore_index=True)


# if __name__ == "__main__":

#     compile_df = None
#     if type(args.compile_info) == list:
#         compile_df = pd.read_csv(args.compile_info[0])
#         for csv in args.compile_info[1:]:
#             compile_df = concatenate_csv_fill_mutex_zeros(compile_df, csv)
#     else:
#         compile_df = pd.read_csv(args.compile_info)

#     run_df = None
#     if type(args.run_info) == list:
#         run_df = pd.read_csv(args.run_info[0])
#         for csv in args.run_info[1:]:

#             run_df = concatenate_csv_fill_mutex_zeros(run_df, csv)
#     else:
#         run_df = pd.read_csv(args.run_info)
#     # print(tabulate(compile_df))
#     # print(tabulate(run_df))


#     df = merge_csv_inner_join(compile_df, run_df)
#     df = df.rename(columns=COLUMN_RENAME)

#     df.to_csv(FILE, index=False)
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
