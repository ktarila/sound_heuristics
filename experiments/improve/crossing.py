"""When does a run's best value first get below the decoy value (error 100)
on a trap function? Prints, per seed, the share of the evaluation budget at
which that happens (blank: never) and the final error."""
import sys
import numpy as np
import lab
import leks

key, mode, seeds = sys.argv[1], sys.argv[2], int(sys.argv[3])
leks.MODE = mode
func, lower, upper, optimum, budget = lab.problem(key)
rows = []
for seed in range(seeds):
    cls = leks.Leks
    s = cls(func, lower, upper, rng=np.random.default_rng(seed), pop_size=180,
            final_size=4, kappa_start=0.0, kappa=8.0, refine=0.1)
    r = s.run(evaluations=budget)
    used = np.array([e for e, _ in s._history])
    best = np.minimum.accumulate([f for _, f in s._history]) - optimum
    below = np.flatnonzero(best < 99.0)
    when = used[below[0]] / budget if below.size else None
    rows.append((seed, when, max(0.0, r.best_fitness - optimum)))
    print(f"{key} {mode:6s} seed {seed}: below 99 at "
          f"{'never' if when is None else f'{100*when:.0f}% of budget'}; "
          f"final error {rows[-1][2]:.1f}", flush=True)
