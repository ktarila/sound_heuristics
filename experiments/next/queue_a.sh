#!/bin/bash
# v4 candidate A: population CMA-ES endgame (IPOP restarts), 10% share, vs version 3.
cd "$(dirname "$0")"
Q="q2x0 q2x1 q4x0 q4x1 q6x0 q6x1 q7x0 q7x1 q8x0 q10x0 q10x1"
C="c22 c24 c5 c10 c7 c12 c17 c21"
ENDGAME=cma python lab.py v4-cma v4.V4 $Q $C --runs 15 > ../v5/v4-cma.log 2>&1
python lab.py v4-base sound $Q --runs 15 > ../v5/v4-base.log 2>&1
echo done > ../v5/v4_a_done.txt
