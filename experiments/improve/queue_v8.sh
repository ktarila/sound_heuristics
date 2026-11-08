#!/bin/bash
# Allocation chooser bench: 31 runs, same seeds as experiments/v5/base2.json. Waits
# for the round 7 bench (queue_v7.sh) so the two do not compete.
cd "$(dirname "$0")"
while [ ! -f ../v5/v7_done.txt ]; do sleep 60; done
FUNCS="c5 c8 p0 p1 p2 c22 c24 c10 c7 c21 c12 c17"
MODE=alloc python lab.py alloc leks.Leks $FUNCS --runs 31 > ../v5/v8_alloc.log 2>&1
echo "alloc bench done" > ../v5/v8_done.txt
