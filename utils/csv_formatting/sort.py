# import pandas as pd
# import argparse
# import os


# def process_csv(file_path, dep_vars, drop_cols, sort_cols):
#     df = pd.read_csv(file_path)

#     # Drop specified columns
#     df = df.drop(columns=drop_cols, errors="ignore")

#     # Sort by specified columns (ascending)
#     df = df.sort_values(by=sort_cols, ascending=True)

#     # Independent variables are remaining columns not in dep_vars
#     indep_vars = [col for col in df.columns if col not in dep_vars]

#     # Display only independent and dependent variables
#     selected_cols = indep_vars + dep_vars
#     print(",".join(selected_cols))
#     for _, row in df.iterrows():
#         values = [
#             str(row[col]) if not pd.isna(row[col]) else "" for col in selected_cols
#         ]
#         print(",".join(values))


# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(
#         description="Process and display selected columns from a CSV."
#     )
#     parser.add_argument("csv_file", help="Path to the CSV file")
#     parser.add_argument(
#         "--dep_vars", nargs="+", required=True, help="Dependent variable columns"
#     )
#     parser.add_argument("--drop_cols", nargs="*", default=[], help="Columns to drop")
#     parser.add_argument(
#         "--sort_cols", nargs="+", required=True, help="Columns to sort by"
#     )

#     args = parser.parse_args()

#     process_csv(args.csv_file, args.dep_vars, args.drop_cols, args.sort_cols)


import pandas as pd
import argparse
import os
from tabulate import tabulate


def print_csv_as_table(df):

    # Convert DataFrame to a list of lists (for tabulate)
    # table_data = df.values.tolist()

    # # Get column headers
    # headers = df.columns.tolist()

    # # Print the table using tabulate
    # print(tabulate(table_data, headers=headers, tablefmt="grid"))
    for column in df.columns:
        if df[column].dtype in ['float64', 'int64']:  # Check if the column is numeric
            # Format: up to 4 decimal places, with commas
            # df[column] = df[column].apply(lambda x: f"{x:,.4f}" if pd.notna(x) else "")
            df[column] = df[column].apply(lambda x: f"{x:,.4f}" if pd.notna(x) else x)
    # Convert DataFrame to a list of lists (for tabulate)
    table_data = df.values.tolist()

    # Get column headers
    headers = df.columns.tolist()

    # Print the table using tabulate with grid format
    print(tabulate(table_data, headers=headers, tablefmt="simple_grid", numalign="right"))


def process_csv(file_path, drop_cols, sort_cols):
    df = pd.read_csv(file_path)

    # Drop specified columns
    df = df.drop(columns=drop_cols, errors="ignore")

    # Ensure specific columns remain integers
    # Example: columns that should remain integers
    int_columns = ["threads", "n"]  # Specify here if needed
    for col in int_columns:
        if col in df.columns:
            df[col] = df[col].astype("Int64")  # Use 'Int64' for nullable integer type

    # Sort by specified columns (ascending)
    df = df.sort_values(by=sort_cols, ascending=True)

    # Save to new CSV
    base, ext = os.path.splitext(file_path)
    out_path = f"{base}_processed{ext}"
    df.to_csv(out_path, index=False)
    print(f"Processed file written to {out_path}")
    print_csv_as_table(df)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Drop and sort columns from a CSV, then save."
    )
    parser.add_argument("csv_file", help="Path to the CSV file")
    parser.add_argument("--drop_cols", nargs="*", default=[], help="Columns to drop")
    parser.add_argument(
        "--sort_cols", nargs="+", required=True, help="Columns to sort by (names)"
    )

    args = parser.parse_args()

    process_csv(args.csv_file, args.drop_cols, args.sort_cols)
