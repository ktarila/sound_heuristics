cd "$(dirname "$0")"
until [ -s ../v5_t-late08.log ]; do sleep 10; done
ALL="c5 c8 p0 p1 p2 c22 c24 c10 c7"
for w in 0.5 0.25; do
  HEARING_FIX=share LATE_FLOOR=0.8 WIDE=$w python lab.py share$w hearing.Hearing $ALL --runs 31 > ../v5_share$w.log 2>&1
done
echo done
