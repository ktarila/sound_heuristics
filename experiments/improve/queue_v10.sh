#!/bin/bash
# Mixed switch bench: version 3 hearing for 10%, then each agent hears
# infrasound with probability SHARE each round, the rest keep version 3
# hearing. 31 runs, same seeds as experiments/v5/base2.json.
cd "$(dirname "$0")"
FUNCS="c5 c8 p0 p1 p2 c22 c24 c10 c7 c21 c12 c17"
for s in 0.5 0.25; do
  MODE=switch SWITCH=0.1 SHARE=$s python lab.py mix$s leks.Leks $FUNCS --runs 31 > ../v5/v10_mix$s.log 2>&1
done
echo "mix bench done" > ../v5/v10_done.txt
