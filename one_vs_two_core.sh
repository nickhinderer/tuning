make clean
python compile.py --import-json config/gemm-single-core.json
# ./run.sh time --runs 20
# mv ./build/run.csv ./build/scratchpad/run.csv
# mv ./build/compile_gemm.single.core.csv ./build/scratchpad/compile_gemm.single.core.csv
# make clean
# python compile.py --import-json config/gemm-two-core.json
./run.sh time --runs 40 --env-set GOMP_CPU_AFFINITY 0-1,1 --env-set OMP_NUM_THREADS 2
python combine.py --compile-info build/compile_gemm-singe-core.csv --run-info build/run.csv
python evaluate\ copy.py