"""Off-switch check: a prototype with its setting off must give exactly the
same result as the built-in search, seed for seed.

Usage: python offcheck.py module.Class [evaluations] [func ...]
(set the prototype's env variable to its "off" value before calling)
"""
import importlib
import sys
import time
import numpy as np

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1] / "improve"))
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))
from sound_heuristic import cec2017  # noqa: E402
from sound_heuristic.solution import SoundSearch  # noqa: E402

DIM = 10
module, cls = sys.argv[1].rsplit(".", 1)
budget = int(sys.argv[2]) if len(sys.argv) > 2 else 20000
funcs = [int(f) for f in sys.argv[3:]] or [5, 22]
Proto = getattr(importlib.import_module(module), cls)
settings = dict(pop_size=18 * DIM, final_size=4, kappa_start=0.0, kappa=8.0,
                refine=0.1)

ok = True
for f in funcs:
    p = cec2017.get_problem(f, DIM)
    for seed in range(3):
        out = []
        for klass in (SoundSearch, Proto):
            t = time.time()
            s = klass(p.func, p.lower, p.upper,
                      rng=np.random.default_rng(seed), **settings)
            r = s.run(evaluations=budget)
            out.append((r.best_fitness, r.evaluations, time.time() - t))
        same = out[0][0] == out[1][0] and out[0][1] == out[1][1]
        ok &= same
        print(f"F{f} seed {seed}: built-in {out[0][0]:.6g} ({out[0][2]:.1f}s) "
              f"prototype {out[1][0]:.6g} ({out[1][2]:.1f}s) "
              f"{'SAME' if same else 'DIFFERENT'}")
print("ALL SAME" if ok else "MISMATCH")
