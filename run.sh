#!/bin/bash

set -e

set -a
source .env
set +a

# -------------------------
# Helper function: join with delimiter
join_by() {
    local IFS="$1"
    shift
    echo "$*"
}

# -------------------------
# Initialization
exec_dir=""
output_vars=()
csv_file="build/run.csv"
runs=1
declare -A arg_sets
declare -A env_sets
declare -A arg_ranges
declare -A env_ranges
env_file=""
print_env_after_set=false
print_env_before_run=false

# -------------------------
# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --csv)
            csv_file="$2"
            shift 2
            ;;
        --out-vars)
            IFS=',' read -r -a output_vars <<< "$2"
            shift 2
            ;;
        --arg-set)
            key="$2"
            IFS=',' read -r -a values <<< "$3"
            arg_sets["$key"]="${values[@]}"
            shift 3
            ;;
        --arg-range)
            key="$2"
            min="$3"
            max="$4"
            stride="$5"
            values=()
            for ((v=min; v<=max; v+=stride)); do
                values+=("$v")
            done
            arg_sets["$key"]="${values[@]}"
            shift 5
            ;;
        --env-set)
            key="$2"
            IFS=',' read -r -a values <<< "$3"
            env_sets["$key"]="${values[@]}"
            shift 3
            ;;
        --env-range)
            key="$2"
            min="$3"
            max="$4"
            stride="$5"
            values=()
            for ((v=min; v<=max; v+=stride)); do
                values+=("$v")
            done
            env_sets["$key"]="${values[@]}"
            shift 5
            ;;
        --runs)
            runs="$2"
            shift 2
            ;;
        --env-file)
            env_file="$2"
            shift 2
            ;;
        --print-env-after-set)
            print_env_after_set=true
            shift
            ;;
        --print-env-before-run)
            print_env_before_run=true
            shift
            ;;
        *)
            if [[ -z "$exec_dir" ]]; then
                exec_dir="$1"
                shift
            elif [[ ${#output_vars[@]} -eq 0 ]]; then
                IFS=',' read -r -a output_vars <<< "$1"
                shift
            else
                echo "Unknown or malformed argument: $1"
                exit 1
            fi
            ;;
    esac
done

# -------------------------
# Validate required fields
if [[ -z "$exec_dir" || ${#output_vars[@]} -eq 0 ]]; then
    echo "Usage: $0 <exec_dir> <output_vars> [options]"
    exit 1
fi

# -------------------------
# Source env file if given
if [[ -n "$env_file" ]]; then
    source "$env_file"
    $print_env_after_set && env
fi

# -------------------------
# Generate argument/env variable combinations (Cartesian product)
arg_keys=("${!arg_sets[@]}")
env_keys=("${!env_sets[@]}")

arg_combinations=("")
for key in "${arg_keys[@]}"; do
    new_combinations=()
    IFS=' ' read -r -a values <<< "${arg_sets[$key]}"
    for combo in "${arg_combinations[@]}"; do
        for val in "${values[@]}"; do
            new_combinations+=("$combo $key=$val")
        done
    done
    arg_combinations=("${new_combinations[@]}")
done

env_combinations=("")
for key in "${env_keys[@]}"; do
    new_combinations=()
    IFS=' ' read -r -a values <<< "${env_sets[$key]}"
    for combo in "${env_combinations[@]}"; do
        for val in "${values[@]}"; do
            new_combinations+=("$combo $key=$val")
        done
    done
    env_combinations=("${new_combinations[@]}")
done

# -------------------------
# Write CSV header
header="binary"
for k in "${arg_keys[@]}"; do header+=",$k"; done
for k in "${env_keys[@]}"; do header+=",$k"; done
for o in "${output_vars[@]}"; do header+=",$o"; done
echo "$header" > "$csv_file"

# -------------------------
# Run each combination
for bin in "$exec_dir"/*; do
    [[ -x "$bin" && -f "$bin" ]] || continue
    bin_name=$(basename "$bin")

    for arg_combo in "${arg_combinations[@]}"; do
        declare -A arg_vals
        for pair in $arg_combo; do
            k="${pair%%=*}"
            v="${pair#*=}"
            arg_vals["$k"]="$v"
        done
        arg_args=()
        for k in "${arg_keys[@]}"; do
            arg_args+=("${arg_vals[$k]}")
        done

        for env_combo in "${env_combinations[@]}"; do
            declare -A env_vals
            for pair in $env_combo; do
                k="${pair%%=*}"
                v="${pair#*=}"
                env_vals["$k"]="$v"
            done

            for ((i=0; i<runs; i++)); do
                # Set env vars temporarily
                env_cmd=""
                for k in "${env_keys[@]}"; do
                    env_cmd+=" $k=${env_vals[$k]}"
                done

                $print_env_before_run && echo "ENV: $env_cmd"

                # Run and capture output
                result=$(eval $env_cmd "$bin" "${arg_args[@]}")

                # Read outputs line by line
                # IFS=$'\n' read -d '' -r -a lines <<< "$result"
                IFS=$'\n' read -r -a lines <<< "$result"

                # Construct CSV row
                row="$bin_name"
                for k in "${arg_keys[@]}"; do row+=","${arg_vals[$k]}; done
                for k in "${env_keys[@]}"; do row+=","${env_vals[$k]}; done
                for l in "${lines[@]}"; do row+=",$l"; done

                echo "$row" >> "$csv_file"
            done
        done
    done
done
