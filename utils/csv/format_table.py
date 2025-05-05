import pandas as pd

pd.options.display.float_format = "{:,.4f}".format
from tabulate import tabulate
import sys


def aggregate_csv(input_csv, dep_vars):
    # Load the CSV file into a DataFrame
    df = pd.read_csv(input_csv)

    # Drop the 'id' and 'source' columns
    df = df.drop(columns=["source"])

    # Split dependent variables from input string
    dep_vars_list = dep_vars.split(",")

    # Determine independent variables (those that are not in the dependent vars list)
    independent_vars = [col for col in df.columns if col not in dep_vars_list]

    # Aggregate the data by calculating the mean of the dependent variables
    aggregated_df = df.groupby(independent_vars, as_index=False).agg(
        {var: "mean" for var in dep_vars_list}
    )
    aggregated_df = aggregated_df.applymap(
        lambda x: "{:,.4f}".format(x) if isinstance(x, (int, float)) else x
    )

    # Print the aggregated DataFrame as a simple grid
    print(tabulate(aggregated_df, headers="keys", tablefmt="simple_grid", showindex=False))
    aggregated_df.to_csv(sys.argv[1]+".agg.csv", index=False)
    # print(
    #     tabulate(
    #         aggregated_df[:5],
    #         headers="keys",
    #         tablefmt="grid",
    #         numalign="right",
    #         stralign="center",
    #     )
    # )
    # print("\n" + "-" * 40 + "\n")  # Optional separator between the two halves
    # print(
    #     tabulate(
    #         aggregated_df[5:],
    #         headers="keys",
    #         tablefmt="grid",
    #         numalign="right",
    #         stralign="center",
    #     )
    # )


# Example usage:
input_csv = sys.argv[1]  # Replace with the path to your CSV file
dep_vars = "instr,cyc,stall_cyc,l1d_miss,l2d_acc,l2d_miss,l3_acc,dtlb_m,itlb_m,vec_sp,vec_dp,sp_op,dp_op,fp_scl_sin,fp_scl_dbl,lst_instr"  # Replace with the dependent variables you want to average
aggregate_csv(input_csv, dep_vars)


# import pandas as pd
# from tabulate import tabulate
# import sys


# def aggregate_csv(input_csv, dep_vars):
#     # Load the CSV file into a DataFrame
#     df = pd.read_csv(input_csv)

#     # Drop the 'id' and 'source' columns
#     df = df.drop(columns=["id", "source"])

#     # Select dependent variables
#     dep_vars_list = dep_vars.split(",")

#     # Aggregate the data by calculating the mean of the dependent variables
#     aggregated_df = (
#         df.groupby(list(df.columns.difference(dep_vars_list)))
#         .agg({var: "mean" for var in dep_vars_list})
#         .reset_index()
#     )

#     # Print the aggregated DataFrame as a simple grid
#     print(tabulate(aggregated_df, headers="keys", tablefmt="grid", showindex=False))
