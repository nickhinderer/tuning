make clean
python compile.py --import-json env/gemm.json
./run.sh time --runs 5 --env-range OMP_NUM_THREADS 1 1 1
mv ./build/run.csv ./build/scratchpad/run.csv
mv ./build/compile_gemm.csv ./build/scratchpad/compile_gemm.csv
make clean
python compile.py --import-json env/gemm.openmp.json
./run.sh time --runs 5 --env-range OMP_NUM_THREADS 1 32 1
python combine.py --compile-info build/scratchpad/compile_gemm.csv build/compile_gemm.openmp.csv --run-info build/scratchpad/run.csv build/run.csv
python evaluate.py