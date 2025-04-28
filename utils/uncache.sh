#!/bin/bash

if [[ -n "$(ls -A bin 2>/dev/null)" || -n "$(ls -A aux 2>/dev/null)" ]]; then
    mkdir -p tmp
    filename="cached_$(date +%d%m%Y_%H%M%S)"
    tar -cf $filename aux bin
    mv $filename tmp
    rm aux/* bin/* 2>/dev/null

fi

# Get most recent file matching pattern
latest_file=$(ls -1t ./cache/cached_* 2>/dev/null | head -n 1)

# Check if one was found
if [[ -n "$latest_file" ]]; then

    tar -xf $latest_file
    if [[ -n "$(ls -A tmp 2>/dev/null)" ]]; then
        mv tmp/* cache
        rm -r tmp
        exit 0
    else
       exit 0
    fi
else
  exit 0
fi