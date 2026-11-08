#!/bin/bash
# Round 7 bench: 31 runs, same seeds as experiments/v5/base2.json. Starts at once
# and shares the machine with the 30-coordinate run (experiments/queue_d30.sh).
cd "$(dirname "$0")"
FUNCS="c5 c8 p0 p1 p2 c22 c24 c10 c7 c21 c12 c17"
python lab.py base-c17 sound c17 --runs 31 > ../v5/v7_base-c17.log 2>&1
MODE=infra python lab.py infra leks.Leks $FUNCS --runs 31 > ../v5/v7_infra.log 2>&1
MODE=leks MERGE=1.0 python lab.py walled leks.Leks $FUNCS --runs 31 > ../v5/v7_walled.log 2>&1
TURN=0.5 python lab.py turn0.5 turn.Turn $FUNCS --runs 31 > ../v5/v7_turn0.5.log 2>&1
echo "round 7 bench done" > ../v5/v7_done.txt
