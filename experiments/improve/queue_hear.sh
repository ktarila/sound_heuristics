cd "$(dirname "$0")"
until [ -s ../v5_hop1.0.log ]; do sleep 10; done
F="c5 c8 p0 p1 p2"
HEARING_FIX=both python lab.py hear-both hearing.Hearing $F --runs 31 > ../v5_hear-both.log 2>&1
HEARING_FIX=late LATE_FLOOR=0.5 python lab.py late05 hearing.Hearing $F --runs 31 > ../v5_late05.log 2>&1
HEARING_FIX=late LATE_FLOOR=0.3 python lab.py late03 hearing.Hearing $F --runs 31 > ../v5_late03.log 2>&1
HEARING_FIX=late LATE_FLOOR=0.8 python lab.py late08 hearing.Hearing $F --runs 31 > ../v5_late08.log 2>&1
echo done
