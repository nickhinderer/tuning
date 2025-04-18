python compile.py --import-json gemm.json
python compile.py --import-json gemm.openmp.json
./run.sh time --runs 10 --env-range OMP_NUM_THREADS 1 32 1
python combine.py
python evaluate.py