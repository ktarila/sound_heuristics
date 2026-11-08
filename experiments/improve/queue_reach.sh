cd "$(dirname "$0")"
ALL="c5 c8 p0 p1 p2 c22 c24 c10 c7 c21 c12"
run(){ name=$1; shift; env "$@" python lab.py $name reach.Reach $ALL --runs 31 > ../v5_$name.log 2>&1; }
run base2 DECAY_START=1.0
run reach30w0 DECAY_START=0.3 W_END=0.0
run reach50w0 DECAY_START=0.5 W_END=0.0
run reach30w05 DECAY_START=0.3 W_END=0.5
echo done
