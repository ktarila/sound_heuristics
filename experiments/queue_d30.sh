#!/bin/bash
# CEC 2017 at 30 coordinates, 10 runs: Echo (v2) and Encore after step 9 (step2);
# Encore itself (v3-noisy) was run first. Results in experiments/v6/.
cd "$(dirname "$0")/.." || exit 1
until [ -s experiments/v6/c17_d30_v3-noisy.txt ]; do sleep 30; done
python benchmark.py --suite cec2017 --dim 30 --runs 10 --pop 50 --final-pop 50 --stall 0 --kappa-start 1 --kappa 4 --refine 0.3 --noisy-after 1 --name v2-d30 --save experiments/v6/c17_d30_v2.json > experiments/v6/c17_d30_v2.txt
python benchmark.py --suite cec2017 --dim 30 --runs 10 --kappa-start 1 --kappa 4 --refine 0.3 --noisy-after 1 --name step2-d30 --save experiments/v6/c17_d30_step2.json > experiments/v6/c17_d30_step2.txt
echo done
