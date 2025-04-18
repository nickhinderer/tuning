import pandas as pd
from tabulate import tabulate
import argparse
import matplotlib
from dotenv import load_dotenv
import os
from pathlib import Path


load_dotenv()
# === Global Configuration === #

combine_compiler_generated_tables = True
# compiler_file = "aux/compile_data_gemm.csv"
compiler_file = "build/compile_gemm.csv"
compiler_file2 = "build/compile_gemm.openmp.csv"
run_file = "build/run.csv"

DATA_PATH = os.getenv("DATA_PATH")
DATA_FILE = os.getenv("DATA_FILE")
FILE = os.path.join(DATA_PATH, DATA_FILE)

COLUMN_RENAME = {
    "id": "id",
    "DN=": "n",
    "OMP_NUM_THREADS": "threads",
    "fopenmp": "OpenMP",
    "time": "time",
}

# === ANSI Colors ===


# TODO specify these somewhere more convenient
def correct_erroneous_column_values(df):
    df.loc[df["openMP"] == 0, "threads"] = 1
    return


# or alternatively:


def drop_erroneous_rows_matching_values(df, criteria):
    """Criteria of the form:
    {
        'column1' : [value1],
        'column2' : [value2, value3]
    }
    """
    mask = pd.Series([True] * len(df), index=df.index)
    for col, vals in criteria.items():
        vals = vals if isinstance(vals, (list, set, tuple)) else [vals]
        mask &= ~df[col].isin(vals)
    return df[mask].copy()

    return


def remove_outliers(threshold=None, number=0):
    """Either remove by a given acceptable deviation or the top and bottom number specified"""
    return


def merge_csv_inner_join(compiler_data, run_data):
    """Intended to be used to link the compiler variables with runtime variables based on executable name"""
    # df1 = pd.read_csv(compiler_data)  # has unique ids
    # df2 = pd.read_csv(run_data)  # has duplicates

    # Merge on 'id', duplicating df1 rows as needed
    return pd.merge(
        run_data, compiler_data, on="id", how="inner"
    )  # or 'inner' if you only want matching ids


def concatenate_csv_fill_mutex_zeros(compiler_data1, compiler_data2):
    """Intended to be used to concatenate two csv files generated from compilation"""
    df1 = pd.read_csv(compiler_data1)  # has unique ids
    df2 = pd.read_csv(compiler_data2)
    fill_value = 0

    # Get union of all column names
    all_columns = df1.columns.union(df2.columns)

    # Reindex each DataFrame to have all columns, fill missing with fill_value
    df1_filled = df1.reindex(columns=all_columns, fill_value=fill_value)
    df2_filled = df2.reindex(columns=all_columns, fill_value=fill_value)

    # Concatenate the two vertically
    return pd.concat([df1_filled, df2_filled], ignore_index=True)


if __name__ == "__main__":


    run_df = pd.read_csv(run_file)
    compile_df = (
        concatenate_csv_fill_mutex_zeros(compiler_file, compiler_file2)
        if combine_compiler_generated_tables
        else pd.read_csv(compiler_file)
    )
    df = merge_csv_inner_join(compile_df, run_df)
    df = df.rename(columns=COLUMN_RENAME)
    
    df.to_csv(FILE, index=False)
    