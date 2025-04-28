#!/bin/bash
make clean
.venv/bin/python machine_profiler.py > output.txt
# python3.11 compile.py 
./run.sh --bin-folder bin --env-file env.txt --output-vars exec_time --runs 2 --range OMP_NUM_THREADS 1 11 2
.venv/bin/python evaluate.py >> output.txt