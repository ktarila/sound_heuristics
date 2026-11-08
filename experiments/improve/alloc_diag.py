"""Run the allocation chooser on a few seeds and show how the evaluations
were shared: weights of lek A (neighbour hearing) and lek B (infrasound)
after the last check, and the final error."""
import sys
import numpy as np
import lab
import leks

key, seeds = sys.argv[1], int(sys.argv[2])
leks.MODE = "alloc"
func, lower, upper, optimum, budget = lab.problem(key)
for seed in range(seeds):
    s = leks.Leks(func, lower, upper, rng=np.random.default_rng(seed),
                  pop_size=180, final_size=4, kappa_start=0.0, kappa=8.0,
                  refine=0.1)
    r = s.run(evaluations=budget)
    last = s.allocation[-1] if s.allocation else None
    print(f"{key} seed {seed}: final error {max(0.0, r.best_fitness - optimum):.2f}; "
          f"weights A/B after {len(s.allocation)} checks: "
          f"{'-' if last is None else f'{last[1]:.2f} / {last[2]:.2f}'}", flush=True)
