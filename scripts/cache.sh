#!/bin/bash
mkdir -p cache
filename="cached_$(date +%d%m%Y_%H%M%S)"
tar -cf $filename aux bin
mv $filename cache
rm aux/* bin/*