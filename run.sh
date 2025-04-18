#!/bin/bash

set -euo pipefail

# Default CSV filename
CSV_FILE="aux/run_data.csv"

# Argument parsing
BIN_FOLDER=""
ENV_FILE=""
PRINT_ENV=0
RUNS=1
declare -A RANGE_VARS
declare -A SET_VARS
OUTPUT_VARS=()

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --bin-folder)
      BIN_FOLDER="$2"; shift 2 ;;
    --env-file)
      ENV_FILE="$2"; shift 2 ;;
    --range)
      VAR="$2"; MIN="$3"; MAX="$4"; STRIDE="$5"
      RANGE_VARS["$VAR"]="$MIN:$MAX:$STRIDE"
      shift 5 ;;
    --set)
      VAR="$2"; VALUES="$3"
      SET_VARS["$VAR"]="$VALUES"
      shift 3 ;;
    --runs)
      RUNS="$2"; shift 2 ;;
    --output-vars)
      shift
      while [[ $# -gt 0 && "$1" != --* ]]; do
        OUTPUT_VARS+=("$1")
        shift
      done ;;
    --print-env)
      PRINT_ENV=1; shift ;;
    --csv)
      CSV_FILE="$2"; shift 2 ;;
    *)
      echo "Unknown argument: $1" >&2; exit 1 ;;
  esac
done

# ls -l "$BIN_FOLDER"

# Check required args
[[ -z "$BIN_FOLDER" || -z "$ENV_FILE" ]] && {
  echo "Usage: $0 --bin-folder <folder> --env-file <file> ..." >&2
  exit 1
}

# Load default environment variables
source "$ENV_FILE"

# Create list of binaries
BINARIES=()
while IFS= read -r -d '' bin; do
  [[ -x "$bin" ]] && BINARIES+=("$bin")
done < <(find "$BIN_FOLDER" -maxdepth 1 -type f -executable -print0)


# Generate env variable combinations
COMBINATIONS=("")
for VAR in "${!RANGE_VARS[@]}"; do
  IFS=":" read -r MIN MAX STRIDE <<< "${RANGE_VARS[$VAR]}"
  VALUES=()
  for ((v=MIN; v<=MAX; v+=STRIDE)); do VALUES+=("$v"); done
  NEW_COMBOS=()
  for combo in "${COMBINATIONS[@]}"; do
    for val in "${VALUES[@]}"; do
      NEW_COMBOS+=("$combo $VAR=$val")
    done
  done
  COMBINATIONS=("${NEW_COMBOS[@]}")
done

for VAR in "${!SET_VARS[@]}"; do
  IFS=',' read -ra VALUES <<< "${SET_VARS[$VAR]}"
  NEW_COMBOS=()
  for combo in "${COMBINATIONS[@]}"; do
    for val in "${VALUES[@]}"; do
      NEW_COMBOS+=("$combo $VAR=$val")
    done
  done
  COMBINATIONS=("${NEW_COMBOS[@]}")
done

# Print environment if requested
if [[ "$PRINT_ENV" -eq 1 ]]; then
  echo "---- Effective Environment ----"
  printenv | sort
  echo "-------------------------------"
fi

# Write CSV header
{
  printf "id"
  for VAR in "${!RANGE_VARS[@]}"; do printf ",%s" "$VAR"; done
  for VAR in "${!SET_VARS[@]}"; do printf ",%s" "$VAR"; done
  for OUT in "${OUTPUT_VARS[@]}"; do printf ",%s" "$OUT"; done
  echo
} > "$CSV_FILE"

# Run binaries
for bin in "${BINARIES[@]}"; do
  BIN_NAME=$(basename "$bin")
  for combo in "${COMBINATIONS[@]}"; do
    # Export env vars
    eval "export $combo >> /dev/null"
    for ((i=0; i<RUNS; i++)); do
      # OUTPUT =$("$bin") || { echo "Error: binary '$BIN_NAME' failed on run $i"; exit 1; }
      # env | grep "GOMP_CPU_AFFINITY"
      OUTPUT=$("$bin") || { echo "Error: binary '$BIN_NAME' failed on run $i"; exit 1; }

      # Handle escaped \n in the output (if needed)
      # Only do this if your binary outputs things like 'line1\nline2'
      if [[ "$OUTPUT" == *\\n* ]]; then
        OUTPUT=$(printf "%b" "$OUTPUT")
      fi

      # Split into lines
      OUT_LINES=()
      while IFS= read -r line; do
        OUT_LINES+=("$line")
      done <<< "$OUTPUT"

      # Debug output
      # echo "Split output lines:"
      for line in "${OUT_LINES[@]}"; do
        echo ">> $line"
      done

      # Check number of outputs
      if [[ "${#OUT_LINES[@]}" -ne "${#OUTPUT_VARS[@]}" ]]; then
        echo "Error: expected ${#OUTPUT_VARS[@]} output lines from '$BIN_NAME', got ${#OUT_LINES[@]}" >&2
        exit 1
      fi
      
      {
        printf "%s" "$BIN_NAME"
        for VAR in "${!RANGE_VARS[@]}"; do
          val=$(echo "$combo" | grep -oP "$VAR=\K\S+" || echo "")
          printf ",%s" "$val"
        done
        for VAR in "${!SET_VARS[@]}"; do
          val=$(echo "$combo" | grep -oP "$VAR=\K\S+" || echo "")
          printf ",%s" "$val"
        done
        for val in "${OUT_LINES[@]}"; do
          printf ",%s" "$val"
        done
        echo
      } >> "$CSV_FILE"
    done
  done
done