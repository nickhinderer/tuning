import pandas as pd
from tabulate import tabulate
import argparse
# from modules.files import create_file_with_timestamp
import matplotlib

# === Global Configuration === #

combine_compiler_generated_tables = True
# compiler_file = "aux/compile_data_gemm.csv"
compiler_file = "build/compile_gemm.csv"
compiler_file2 = "build/compile_gemm.openmp.csv"
run_file = "build/run.csv"


COLUMN_RENAME = {
    "id": "id",
    "DN": "n",
    "OMP_NUM_THREADS": "threads",
    "fopenmp": "OpenMP",
    "time": "time",
}

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


def split_table_by_column(df, column):
    return {val: df[df[column] == val].copy() for val in df[column].unique()}


def find_best_combination(df, metric, preferred):
    """
    Return the best performing row with respect to a given dependent variable (column) and
    whether high or low value is preferred

    """
    if preferred == "max":
        return df.loc[df[metric].idxmax()]
    elif preferred == "min":
        return df.loc[df[metric].idxmin()]
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


def sort_table_by_order(df, order):
    """
    e.g.
        order: ['n', 'threads', 'opt']
    """
    return df.sort_values(by=order)
    # return df.sort_values(by=["n", "openMP", "threads", "id"])
    # pd.DataFrame().
    return


def map_numeric_to_category(df, column, map_values, new_column="category"):
    """
    Convert numeric values (any number) to categorical
    e.g.
        df:
        A B C
        0 1 1
        2 1 4
        column: A
        map: {
            0 : x
            1 : y
            2 : z
        }
        new column: D
        returns:
        B C D
        1 1 x
        1 4 z
    """
    df[new_column] = df[column].map(map_values)
    return df.drop(columns=[column])  # Optionally drop original column


def one_hot_to_category(df, one_hot_columns, new_column_name):
    """
    e.g.
        one hot columns: O1, O2, O3
        new column: opt
        merges the three columns with the categorical names as a value instead
    """
    return df.assign(**{new_column_name: df[one_hot_columns].idxmax(axis=1)}).drop(
        columns=one_hot_columns
    )


def display_group_metrics(name_map):

    # for old, new in name_map.items():

    return


# def color_dataframe(df, group_col):
#     groups = df[group_col].unique()
#     if len(groups) > len(COLORS):
#         raise ValueError("Too many groups for available colors.")
#     color_map = dict(zip(groups, COLORS))

#     return [
#         [f"{color_map[row[group_col]]}{val}{RESET}" for val in row]
#         for _, row in df.iterrows()
#     ]


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
    # if len(unique_indices) > len(COLORS):
    # raise ValueError("Too many unique indices for available colors.")
    # color_map = dict(zip(unique_indices, COLORS))
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

    # Format and color index
    formatted_index = [
        f"{color_map[idx]}{format_value(idx)}{RESET}" for idx in df.index
    ]
    colored_df.index = formatted_index

    return colored_df


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-s", "--save", action="store_true")
    args = parser.parse_args()

    run_df = pd.read_csv(run_file)
    compile_df = (
        concatenate_csv_fill_mutex_zeros(compiler_file, compiler_file2)
        if combine_compiler_generated_tables
        else pd.read_csv(compiler_file)
    )
    df = merge_csv_inner_join(compile_df, run_df)
    df = df.rename(columns=COLUMN_RENAME)
    # df.to_csv('new_csv.csv', index=False)
    # df = pd.read_csv('new_csv.csv')
    # PROBLEM 1
    # df = df.sort_values(by=["threads", "id"])
    df = df.sort_values(by=["n", "threads", "id"])
    result = None
    for val, table in split_table_by_column(df, "threads").items():
        result = table.groupby("threads")["time"].agg(["min", "max", "mean"])
        print(result)
    # results
    df = df.sort_values(by=["n", "OpenMP"])
    for n, n_table in split_table_by_column(df, "n").items():
        print(f"------n={n}------\n")
        for omp, omp_table in split_table_by_column(n_table, "OpenMP").items():
            agg = omp_table["time"].agg(["min", "max", "mean"])
            print(f"{'using' if omp else 'without'} OpenMP")
            print(agg.to_string(header=False))
            print()
            print(type(agg.values))
            print(omp)
            if omp:
                result = []
                for thread, thread_table in split_table_by_column(
                    omp_table, "threads"
                ).items():

                    agg = thread_table.groupby("threads")["time"].agg(
                        ["min", "max", "mean"]
                    )
                    result.append(agg)
                result = pd.concat(result)
                result = result.sort_index()
                print(result, "\n")
                # print(color_dataframe_by_index(result), "\n")
                print(
                    tabulate(
                        color_dataframe_by_index(result),
                        ["threads", *result.columns],
                        tablefmt="simple_grid",
                    ),
                    "\n",
                )

    # if args.save:
    #     filename = create_file_with_timestamp("data", "csv", "scratchpad")
    #     with open(filename, "w") as f:
    #         f.write(df["time"].agg(["min", "max", "mean"]).to_string())

    # result = []
    # print(f"{'without' if v1 else 'using'} OpenMP")
    # for val, table in split_table_by_column(t1, 'threads').items():
    #     agg = table.groupby("threads")["time"].agg(["min", "max", "mean"])
    #     result.append(agg)
    # result = pd.concat(result)
    # result = result.sort_index()
    # print(result)

    # Combine all into a single DataFrame
    # result = pd.concat(result)
    # result = result.sort_index()

    # print(result, '\n')

    # group_cols = [col for col in df.columns if col != "time"]
    # aggregated = df.groupby(group_cols, as_index=False)["time"].mean()
    # print(tabulate(aggregated.values, aggregated.columns, tablefmt="psql"))
    # for
    # summary = df.groupby("id")["time"].agg(["min", "max", "mean"])
    # print(summary)

    # group_cols = [col for col in df.columns if col != "time"]
    # aggregated = df.groupby(group_cols, as_index=False)["time"].mean()

    # # print(tabulate(aggregated.values, aggregated.columns, tablefmt="psql"))
    # correct_erroneous_column_values(df)
    # aggregated = df.groupby(group_cols, as_index=False)["time"].mean()
    # df = aggregated.sort_values(by=["n", "openMP", "threads", "id"])
    # # df = color_dataframe_by_group_column(df, "openMP")
    # # print(tabulate(df.values, df.columns, tablefmt="psql"))
    # # print(find_best_combination(df, 'time', 'min'))
    # for v1, t1 in split_table_by_column(df, 'n').items():
    #     for val, table in split_table_by_column(t1, 'openMP').items():
    #         print(f'\n\nthreads = {val}')
    #         colored = color_dataframe_by_group_column(table, "threads")
    #         print(tabulate(colored.values, colored.columns, tablefmt="psql"))
    #         print(find_best_combination(table, 'time', 'min'))
    #         print()
    #         summary = table.groupby("id")["time"].agg(["min", "max", "mean"])
    #         print(summary)
    #         # summary = table.groupby("id")["time"].agg(["min", "max", "mean"])

    # # merged.to_csv("aux/compiler_output_combined.csv", index=False)
    # # merged.to_csv("aux/final_result.csv", index=False)
    # # df = pd.read_csv("aux/final_result.csv")

    # #

    # # df.to_csv("aux/final_sorted.csv", index=False)

    # # pd.set_option("display.width", 100)  # Set display width
    # # pd.set_option("display.max_columns", None)  # Show all columns
    # # print(df_sorted)
    # # df_sorted = df_sorted.drop(columns=['id'])
    # # print(tabulate(df_sorted.values, df_sorted.columns, tablefmt='psql'))

    # #

    # #

    # # # Group by independent variables, average the output
    # #

    # # print(aggregated)
    # # # df = df.drop(columns=['id'])
    # # df = aggregated[["id", "DN", "fopenmp", "OMP_NUM_THREADS", "source", "time"]]
    # # df = df.sort_values(by=["DN", "fopenmp", "OMP_NUM_THREADS", "id"])
    # # # df = df.sort_index('DN')
    # # # df['exec_time'] = df['exec_time'].map('{:.10f}'.format)
    # # # df['exec_time'] = df['exec_time'].apply(lambda x: f"{x:.6f}")
    # # print(tabulate(df.values, df.columns, tablefmt="psql"))
    # # # Tabulate
    # # # print(tabulate(df.astype(str), headers='keys', tablefmt='psql'))
    # # # formatted_data = df.applymap(lambda x: f"{x:.6f}" if isinstance(x, float) else str(x))

    # # # Step 2: Convert to list of lists, pass headers explicitly
    # # # print(tabulate(formatted_data.values.tolist(), headers=formatted_data.columns, tablefmt='psql'))

    # # # ANSI color codes

    # # # Apply coloring row-by-row based on score
    # # def color_row(row):
    # #     if row["fopenmp"] == 0:
    # #         return [f"{RED}{x}{RESET}" for x in row]
    # #     else:
    # #         return [f"{BLUE}{x}{RESET}" for x in row]
    # #     return [str(x) for x in row]

    # # return [str(x) for x in row]

    # # # Step 1: Filter rows with fopenmp == 0
    # # avg_time = df[df["fopenmp"] == 0]["time"].mean()

    # # # Replace rows where fopenmp == 0 with the average time
    # # df = df.groupby(
    # #     ["id", "DN", "fopenmp", "OMP_NUM_THREADS", "source"], as_index=False
    # # ).agg({"time": "mean"})

    # # df = df.rename(columns={"OMP_NUM_THREADS": "threads", "DN": "n", "time": "time"})

    # # df = df.sort_values(by=["n", "fopenmp", "threads", "id"])
    # # colored_rows = df.apply(color_row, axis=1).tolist()
    # # # Print with tabulate

    # # print(tabulate(colored_rows, headers=df.columns, tablefmt="psql"))

    # # TODO for each group display min max avg, the best point, and have feature to split table (after having possibly grouped already) and compare based off that partiotion
    # # you can either compare within the table, or compare between partition within a table, or across tables (either average or best value from either)
