# #!/bin/bash
# set -e

# print_usage() {
#     echo "Usage:"
#     echo "  $0 replace <source_file> <destination_file>"
#     echo "  $0 restore <destination_file>"
# }

# MODE="$1"

# if [[ "$MODE" == "replace" ]]; then
#     SRC="$2"
#     DST="$3"

#     if [[ -z "$SRC" || -z "$DST" ]]; then
#         echo "Error: Missing arguments for replace."
#         print_usage
#         exit 1
#     fi

#     if [[ ! -f "$SRC" ]]; then
#         echo "Error: Source file does not exist: $SRC"
#         exit 1
#     fi

#     if [[ ! -f "$DST" ]]; then
#         echo "Error: Destination file does not exist: $DST"
#         exit 1
#     fi

#     cp "$DST" "${DST}_tmp"
#     cp "$SRC" "$DST"

# elif [[ "$MODE" == "restore" ]]; then
#     DST="$2"

#     if [[ -z "$DST" ]]; then
#         echo "Error: Missing destination file for restore."
#         print_usage
#         exit 1
#     fi

#     if [[ ! -f "${DST}_tmp" ]]; then
#         echo "Error: Backup file does not exist: ${DST}_tmp"
#         exit 1
#     fi

#     mv "${DST}_tmp" "$DST"

# else
#     echo "Error: Invalid mode."
#     print_usage
#     exit 1
# fi


#!/bin/bash
set -e

print_usage() {
    echo "Usage:"
    echo "  $0 replace <source_file> <destination_file>"
    echo "  $0 restore <destination_file>"
}

MODE="$1"

if [[ "$MODE" == "replace" ]]; then
    SRC="$2"
    DST="$3"

    if [[ -z "$SRC" || -z "$DST" ]]; then
        echo "Error: Missing arguments for replace."
        print_usage
        exit 1
    fi

    if [[ ! -f "$SRC" ]]; then
        echo "Error: Source file does not exist: $SRC"
        exit 1
    fi

    if [[ ! -f "$DST" ]]; then
        echo "Error: Destination file does not exist: $DST"
        exit 1
    fi

    DIRNAME=$(dirname "$DST")
    BASENAME=$(basename "$DST")
    TMPFILE="$DIRNAME/tmp_$BASENAME"

    cp "$DST" "$TMPFILE"
    cp "$SRC" "$DST"

elif [[ "$MODE" == "restore" ]]; then
    DST="$2"

    if [[ -z "$DST" ]]; then
        echo "Error: Missing destination file for restore."
        print_usage
        exit 1
    fi

    DIRNAME=$(dirname "$DST")
    BASENAME=$(basename "$DST")
    TMPFILE="$DIRNAME/tmp_$BASENAME"

    if [[ ! -f "$TMPFILE" ]]; then
        echo "Error: Backup file does not exist: $TMPFILE"
        exit 1
    fi

    mv "$TMPFILE" "$DST"

else
    echo "Error: Invalid mode."
    print_usage
    exit 1
fi
