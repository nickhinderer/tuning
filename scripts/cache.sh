#!/bin/bash
filename="cached_$(date +%d%m%Y_%H%M%S)"
tar -cf $filename data
mv $filename misc/cache
rm -rf data
mkdir -p data/bin data/csv/compile data/csv/run