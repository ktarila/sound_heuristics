#!/bin/bash
# Switch bench: version 3 hearing until SWITCH, then infrasound, one group
# (no split of the evaluations). 31 runs, same seeds as experiments/v5/base2.json.
cd "$(dirname "$0")"
FUNCS="c5 c8 p0 p1 p2 c22 c24 c10 c7 c21 c12 c17"
for s in 0.2 0.1; do
  MODE=switch SWITCH=$s python lab.py switch$s leks.Leks $FUNCS --runs 31 > ../v5/v9_switch$s.log 2>&1
done
echo "switch bench done" > ../v5/v9_done.txt
