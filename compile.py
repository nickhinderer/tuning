import os
import subprocess
import itertools

# import csv
import secrets
import string
import argparse
import re
from pathlib import Path 
print('hello')


# === Global Configuration === #

# to try without, use '' as a member of a group
FLAG_GROUPS = [
    [
        "O3",
    ],
    ['fopenmp']
]

VARIABLE_FLAGS = {"DN": [16, 256, 512, 1024]}

SOURCE_FILE = "gemm.openmp"
COMPILER = "gcc"
PRELUDE = "-fopt-info-vec-missed -DNI=N -DNJ=N -DNK=N -I polybench-c-4.2.1-beta/utilities -I polybench-c-4.2.1-beta/linear-algebra/blas/gemm polybench-c-4.2.1-beta/utilities/polybench.c polybench-c-4.2.1-beta/linear-algebra/blas/gemm/gemm.openmp.c -DPOLYBENCH_TIME"

PRINT_IN_COLOR = False
COLOR = (
    {
        "red": "\033[031m",
        "gre": "\033[032m",
        "ylo": "\033[033m",
        "blu": "\033[034m",
        "pur": "\033[035m",
        "clr": "\033[0m",
    }
    if PRINT_IN_COLOR
    else {"red": "", "gre": "", "ylo": "", "blu": "", "pur": "", "clr": ""}
)


# === Global Variables === #


# === Helper Functions === #


def generate_filename(prefix=SOURCE_FILE, length=16):
    """Generate a random temporary filename."""
    chars = string.ascii_lowercase + string.digits
    suffix = "".join(secrets.choice(chars) for _ in range(length))
    return prefix + suffix


def update_environment_from_file(filename):
    """Read and parse environment variables from a file into a dict."""
    env_vars = {}
    with open(filename, "r") as file:
        for line in file:
            if "=" in line:
                key, val = line.strip().split("=", 1)
                val = val.strip('"')  # Remove quotes if present
                env_vars[key] = val
                os.environ[key] = val  # Update the actual environment
    # because of formatting complications that arise when trying to put some of these variables in a csv
    # instead this information will be written once to a file since these will remain the same for one
    # the duration of this program
    with open(f"aux/compile_env_{SOURCE_FILE}.txt", "w") as f:
        for variable, value in os.environ.items():
            f.write(f"{variable}={value}\n")
            print(f"{variable}={value}")
    return env_vars


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
    var_parts = [f"-{k}={v}" for k, v in variables.items()]
    return " ".join(flag_parts + var_parts)


def build_csv_row(active_flags, all_flags, variable_values, temp_filename):
    """Convert flag presence and variable values into a CSV row with temp filename."""
    flag_bits = [1 if flag in active_flags else 0 for flag in all_flags]
    return [temp_filename, SOURCE_FILE] + flag_bits + list(variable_values)


def yield_flag_csv_entries():
    """
    Yield CSV row strings and corresponding compiler flag strings.

    Returns:
        Yields tuples of (csv_row_string, compiler_flag_string)
    """
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
            compiler_cmd += f" -o bin/{temp_filename} "
            compiler_cmd += build_compiler_flag_string(flag_combo, variables)

            # Row to write to CSV
            row = build_csv_row(active_flags, all_flags, var_values, temp_filename)
            csv_row_string = ",".join(map(str, row))

            yield csv_row_string, compiler_cmd


def run_compile_and_report(cmd, report=False, verbose=False):
    """Runs a compile command, and optionally reports missed optimization lines with source context."""

    def log(msg):
        if verbose:
            print(msg)
        wf.write(msg + "\n")
        return

    try:
        # print(cmd)
        result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
        output = result.stdout + result.stderr

        if report:
            with open(f"aux/compiler_report_{SOURCE_FILE}.txt", "a") as wf:
                # Match lines like: path/file.c:123:3: ...
                pattern = re.compile(r'([^\s:]+\.c):(\d+):\d?')
                # pattern = re.compile(r'([^\s:]+\.c):(\d+)(?::\d+)?')
                # pattern = re.compile(r"\b([^\s:]+\.c):(\d+)(?::\d+)?")
                # matches = pattern.findall(output)
                matches = []
                for line in output.splitlines():
                    match = pattern.search(line)
                    if match:
                        filename, lineno = match.groups()
                        matches.append((filename, int(lineno), line.strip()))

                seen = set()
                for filename, lineno, full_msg in matches:
                    key = (filename, lineno)
                    if key in seen:
                        continue
                    seen.add(key)

                    lineno = int(lineno)
                    log(f"\n[!] {filename}:{lineno}\n")
                    log(f"   > {full_msg}")

                    # Try to resolve full path
                    path = Path(filename)
                    if not path.exists():
                        print(f"    File not found: {filename}")
                        continue

                    try:
                        with open(path, "r") as rf:
                            lines = rf.readlines()

                        start = max(0, lineno - 7)
                        end = min(len(lines), lineno + 6)

                        for i in range(start, end):
                            prefix = (
                                f">> {COLOR['blu']}"
                                if i + 1 == lineno
                                else f"   {COLOR['ylo']}"
                            )
                            log(f"{prefix}{i+1:4}: {lines[i].rstrip()}{COLOR['clr']}")

                    except Exception as e:
                        print(f"    Error reading {filename}: {e}")

        return result.returncode == 0

    except Exception as e:
        print(f"[ERROR] Failed to run command: {e}")
        return False


def init():
    """Create required directories and parse arguments."""
    os.makedirs("bin", exist_ok=True)
    os.makedirs("aux", exist_ok=True)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--env-file", type=str, help="Path to environment variable file"
    )
    parser.add_argument("--report", action="store_true", help="")
    args = parser.parse_args()

    return args


# === Entry Point === #

if __name__ == "__main__":

    args = init()

    env_vars = {}
    if args.env_file:
        env_vars = update_environment_from_file(args.env_file)

    with open(f"aux/compile_data_{SOURCE_FILE}.csv", "w") as f:
        for csv_row, compiler_cmd in yield_flag_csv_entries():
            f.write(csv_row + "\n")
            if (
                compiler_cmd
            ):  # to avoid the first iteration which yeilds header and no command
                run_compile_and_report(compiler_cmd, report=False, verbose=True)
