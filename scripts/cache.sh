#!/bin/bash
mkdir -p build/cache
filename="cached_$(date +%d%m%Y_%H%M%S)"
tar -cf $filename bin/* build/*.csv
mv $filename build/cache
rm bin/* build/*.csv