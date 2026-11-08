"""Print best errors for a few seeded runs. MODE=proto uses the prototype
(main tree + roulette.py), MODE=new the code in the current directory."""
import os, sys
import numpy as np
mode = os.environ["MODE"]
if mode == "proto":
    sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    os.environ["SHARP"], os.environ["SWITCH"] = "2", "0.1"
    import roulette
    make = lambda p, seed: roulette.Roulette(p.func, p.lower, p.upper, pop_size=180, final_size=4, kappa_start=0, kappa=8, refine=0.1, rng=np.random.default_rng(seed))
else:
    sys.path.insert(0, os.getcwd())
    from sound_heuristic.solution import SoundSearch
    make = lambda p, seed: SoundSearch(p.func, p.lower, p.upper, pop_size=180, final_size=4, rng=np.random.default_rng(seed))
from sound_heuristic import cec2017
import sound_heuristic
print("code from", os.path.dirname(sound_heuristic.__file__))
for f in (5, 7, 22):
    p = cec2017.get_problem(f, 10)
    for seed in range(2):
        r = make(p, seed).run(evaluations=30000)
        print(f, seed, repr(r.best_fitness))
