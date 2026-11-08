cd "$(dirname "$0")"
ALL="c5 c8 p0 p1 p2 c22 c24 c10 c7 c21 c12"
run(){ name=$1; shift; env "$@" python lab.py $name flat.Flat $ALL --runs 31 > ../v5_$name.log 2>&1; }
run flat50b03 FLAT_START=0.5 BAND=0.3
run flat50b01 FLAT_START=0.5 BAND=0.1
run flat30b03 FLAT_START=0.3 BAND=0.3
echo done
