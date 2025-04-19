make clean
python compile.py --import-json config/gemm.json
./run.sh time --runs 3 --env-range OMP_NUM_THREADS 1 1 1
mv ./build/run.csv ./build/scratchpad/run.csv
mv ./build/compile_gemm.csv ./build/scratchpad/compile_gemm.csv
make clean
python compile.py --import-json config/gemm.openmp.json
./run.sh time --runs 3 --env-range OMP_NUM_THREADS 1 64 2
python combine.py --compile-info build/scratchpad/compile_gemm.csv build/compile_gemm.openmp.csv --run-info build/scratchpad/run.csv build/run.csv
python evaluate.py