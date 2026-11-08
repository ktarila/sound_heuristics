cd "$(dirname "$0")"
ALL="c5 c8 p0 p1 p2 c22 c24 c10 c7"
for e in 0.2 0.1; do
  HEARING_FIX=explore EXPLORE=$e python lab.py explore$e hearing.Hearing $ALL --runs 31 > ../v5_explore$e.log 2>&1
done
HEARING_FIX=recover python lab.py recover hearing.Hearing $ALL --runs 31 > ../v5_recover.log 2>&1
echo done
