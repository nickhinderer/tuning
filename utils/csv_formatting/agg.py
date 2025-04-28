# import pandas as pd
# import sys
# import os


# def aggregate_csv(file_path, dep_vars):
#     # Load CSV
#     df = pd.read_csv(file_path)

#     # Independent variables are all others
#     indep_vars = [col for col in df.columns if col not in dep_vars]

#     # Group by independent variables and aggregate dependent variables by mean
#     grouped = df.groupby(indep_vars, as_index=False)[dep_vars].mean()

#     # Print min, max, average for each dependent variable
#     for col in dep_vars:
#         print(
#             f"{col}: min={grouped[col].min()}, max={grouped[col].max()}, avg={grouped[col].mean()}"
#         )

#     # Save to new file
#     base, ext = os.path.splitext(file_path)
#     out_path = f"{base}_agg{ext}"
#     grouped.to_csv(out_path, index=False)
#     print(f"Aggregated file written to {out_path}")


# if __name__ == "__main__":
#     if len(sys.argv) < 3:
#         print("Usage: python agg.py <csv_file> <dep_var1> [<dep_var2> ...]")
#         sys.exit(1)

#     file_name = sys.argv[1]
#     dependent_vars = sys.argv[2:]
#     aggregate_csv(file_name, dependent_vars)


# import pandas as pd
# import sys
# import os


# def aggregate_csv(file_path, dep_vars):
#     df = pd.read_csv(file_path)

#     indep_vars = [col for col in df.columns if col not in dep_vars]

#     grouped = df.groupby(indep_vars, as_index=False)[dep_vars].mean()

#     # For each row, compute min, max, avg across the dependent variables
#     for idx, row in grouped.iterrows():
#         values = row[dep_vars]
#         row_min = values.min()
#         row_max = values.max()
#         row_avg = values.mean()
#         print(f"Row {idx}: min={row_min}, max={row_max}, avg={row_avg}")

#     # Save to new file
#     base, ext = os.path.splitext(file_path)
#     out_path = f"{base}_agg{ext}"
#     grouped.to_csv(out_path, index=False)
#     print(f"Aggregated file written to {out_path}")


# if __name__ == "__main__":
#     if len(sys.argv) < 3:
#         print("Usage: python script.py <csv_file> <dep_var1> [<dep_var2> ...]")
#         sys.exit(1)

#     file_name = sys.argv[1]
#     dependent_vars = sys.argv[2:]
#     aggregate_csv(file_name, dependent_vars)


import pandas as pd
import sys
import os


def aggregate_csv(file_path, dep_vars):
    df = pd.read_csv(file_path)

    indep_vars = [col for col in df.columns if col not in dep_vars]

    grouped = df.groupby(indep_vars, as_index=False)[dep_vars].mean()

    # Prepare header
    header = indep_vars + ["row_min", "row_max", "row_avg"]
    print(",".join(header))

    # For each row, compute min, max, avg across dependent variables and print
    for _, row in grouped.iterrows():
        indep_values = [str(row[col]) for col in indep_vars]
        dep_values = row[dep_vars]
        row_min = dep_values.min()
        row_max = dep_values.max()
        row_avg = dep_values.mean()
        stats = [f"{row_min:.6f}", f"{row_max:.6f}", f"{row_avg:.6f}"]
        print(",".join(indep_values + stats))

    # Save to new file
    base, ext = os.path.splitext(file_path)
    out_path = f"{base}_agg{ext}"
    grouped.to_csv(out_path, index=False)
    print(f"\nAggregated file written to {out_path}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python script.py <csv_file> <dep_var1> [<dep_var2> ...]")
        sys.exit(1)

    file_name = sys.argv[1]
    dependent_vars = sys.argv[2:]
    aggregate_csv(file_name, dependent_vars)
