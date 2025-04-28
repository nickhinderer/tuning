import pandas as pd
from tabulate import tabulate
import matplotlib
import os


# === Global Configuration === #
# === ANSI Colors ===
RED = "\033[91m"
GREEN = "\033[92m"
ORANGE = "\033[93m"
BLUE = "\033[94m"
PURPLE = "\033[95m"
CYAN = "\033[96m"
WHITE = "\033[97m"
RESET = "\033[0m"
COLORS = [RED, BLUE, ORANGE, GREEN, PURPLE, CYAN, WHITE, RESET]
COLORS = [RED, BLUE, ORANGE, GREEN]


def drop_erroneous_rows_matching_values(df, criteria):
    mask = pd.Series([True] * len(df), index=df.index)
    for col, vals in criteria.items():
        vals = vals if isinstance(vals, (list, set, tuple)) else [vals]
        mask &= ~df[col].isin(vals)
    return df[mask].copy()


def split_table_by_column(df, column):
    return {val: df[df[column] == val].copy() for val in df[column].unique()}


def find_best_combination(df, metric, preferred):
    if preferred == "max":
        return df.loc[df[metric].idxmax()]
    elif preferred == "min":
        return df.loc[df[metric].idxmin()]
    return


def color_dataframe_by_group_column(df, group_col):
    groups = df[group_col].unique()
    if len(groups) > len(COLORS):
        raise ValueError("Too many groups for available colors.")
        # color_map = dict(zip(groups, COLORS))
    color_map = {group: COLORS[i % len(COLORS)] for i, group in enumerate(groups)}

    def color_row(row):
        color = color_map[row[group_col]]
        return row.map(lambda val: f"{color}{val}{RESET}")

    return df.apply(color_row, axis=1)


def color_dataframe_by_index(df, float_precision=6):
    unique_indices = df.index.unique()
    color_map = {
        group: COLORS[i % len(COLORS)] for i, group in enumerate(unique_indices)
    }

    def format_value(val):
        if isinstance(val, float):
            return f"{val:.{float_precision}f}"
        return str(val)

    def color_row(row):
        color = color_map[row.name]
        formatted = row.map(format_value)
        return formatted.map(lambda val: f"{color}{val}{RESET}")

    colored_df = df.apply(color_row, axis=1)
    formatted_index = [
        f"{color_map[idx]}{format_value(idx)}{RESET}" for idx in df.index
    ]
    colored_df.index = formatted_index
    return colored_df


if __name__ == "__main__":
    df = pd.read_csv("nick")
    result = None
    for val, table in split_table_by_column(df, "GOMP_CPU_AFFINITY").items():
        print(f"{'one core two threads' if val == 1 else 'two cores two threads'}")
        result = table["time"].agg(["min", "max", "mean"])
        print(result.to_string(), "\n")
