cd "$(dirname "$0")"
ALL="c5 c8 p0 p1 p2 c22 c24 c10 c7"
for w in 0.25 0.5; do
  WIDE=$w python lab.py wide$w wide.Wide $ALL --runs 31 > ../v5_wide$w.log 2>&1
done
echo done
