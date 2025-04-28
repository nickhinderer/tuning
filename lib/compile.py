import subprocess
import itertools

import secrets
import string
import argparse
import json


# === Global Configuration === #


ID = "gemm"
SOURCE = "gemm"
COMPILER = "gcc"
PRELUDE = "-fopt-info-vec-missed -DNI=N -DNJ=N -DNK=N -I ../polybench-c-4.2.1-beta/utilities -I ../polybench-c-4.2.1-beta/linear-algebra/blas/gemm ../polybench-c-4.2.1-beta/utilities/polybench.c ../polybench-c-4.2.1-beta/linear-algebra/blas/gemm/gemm.c -DPOLYBENCH_TIME "
VARIABLE_FLAGS = {"DN=": [16, 256, 512, 1024]}
FLAG_GROUPS = [
    # to try without, use '' as a member of a group
    [
        "O3",
    ],
    ["fopenmp"],
]

parser = argparse.ArgumentParser()
parser.add_argument(
    "--import-json",
    nargs="?",
    default=None,  # None means not used at all
)
args = parser.parse_args()

if args.import_json:
    with open(f"{args.import_json}", "r") as f:
        config = json.load(f)
        ID, data = next(iter(config.items()))
        SOURCE = data.get("source")
        COMPILER = data.get("compiler")
        PRELUDE = data.get("prelude")
        flags = data.get("flags")
        if flags:
            VARIABLE_FLAGS = flags.get("variable")
            FLAG_GROUPS = flags.get("group")
        else:
            VARIABLE_FLAGS = dict()
            FLAG_GROUPS = list()

# === Helper Functions === #


def generate_filename(prefix=ID, length=16):
    """Generate a random temporary filename."""
    chars = string.ascii_lowercase + string.digits
    suffix = "".join(secrets.choice(chars) for _ in range(length))
    return prefix + suffix


def generate_flag_combinations(flag_groups):
    """Generate all combinations of compiler flags."""
    return list(itertools.product(*flag_groups))


def generate_variable_combinations(variable_flags):
    """Generate all combinations of variable flags."""
    return list(itertools.product(*variable_flags.values()))


def collect_unique_flags(flag_groups):
    """Extract all unique flags (excluding empty string) for CSV columns."""
    flags = set()
    for group in flag_groups:
        for flag in group:
            if flag:
                flags.add(flag)
    return sorted(flags)


def build_compiler_flag_string(flags, variables):
    """Create a valid compiler flag string with dashes and variable assignments."""
    flag_parts = [f"-{flag}" for flag in flags if flag]
    var_parts = [f"-{k}{v}" for k, v in variables.items()]
    return " ".join(flag_parts + var_parts)


def build_csv_row(active_flags, all_flags, variable_values, temp_filename):
    """Convert flag presence and variable values into a CSV row with temp filename."""
    flag_bits = [1 if flag in active_flags else 0 for flag in all_flags]
    return [temp_filename, SOURCE] + flag_bits + list(variable_values)


def yield_flag_csv_entries():

    all_flags = collect_unique_flags(FLAG_GROUPS)
    flag_combos = generate_flag_combinations(FLAG_GROUPS)
    var_combos = generate_variable_combinations(VARIABLE_FLAGS)
    header = ["id"] + ["source"] + all_flags + list(VARIABLE_FLAGS.keys())

    yield ",".join(header), None  # yield header as first row

    for flag_combo in flag_combos:
        active_flags = [f for f in flag_combo if f]
        for var_values in var_combos:
            variables = dict(zip(VARIABLE_FLAGS.keys(), var_values))
            temp_filename = generate_filename()

            # Compiler flags including output redirection
            compiler_cmd = " ".join((COMPILER, PRELUDE))
            compiler_cmd += f" -o data/bin/{temp_filename} "
            compiler_cmd += build_compiler_flag_string(flag_combo, variables)

            # Row to write to CSV
            row = build_csv_row(active_flags, all_flags, var_values, temp_filename)
            csv_row_string = ",".join(map(str, row))

            yield csv_row_string, compiler_cmd


def run_compile_and_report(cmd):
    try:
        print(cmd)
        result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
        print(result.stderr)
        return result.returncode == 0

    except Exception as e:
        print(f"[ERROR] Failed to run command: {e}")
        return False


# === Entry Point === #

if __name__ == "__main__":
    with open(f"data/csv/compile/compile_{ID}.csv", "w") as f:
        for csv_row, compiler_cmd in yield_flag_csv_entries():
            f.write(csv_row + "\n")
            if (
                compiler_cmd
            ):  # to avoid the first iteration which yeilds header and no command
                print(compiler_cmd)
                run_compile_and_report(compiler_cmd)
