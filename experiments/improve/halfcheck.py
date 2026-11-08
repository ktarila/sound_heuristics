"""Is the neighbour-hearing lek's trap rate caused by half the agents, half
the evaluations, or both? Plain version 3 search on F22 / F24 with those
changes (same seeds as the bench). Usage: python halfcheck.py"""
import os
import sys
from multiprocessing import Pool
import numpy as np
import lab

CONFIGS = {  # name: (agents at start, share of the evaluations)
    "full (180 agents, 100%)": (180, 1.0),
    "half agents (90, 100%)": (90, 1.0),
    "half evaluations (180, 50%)": (180, 0.5),
    "both halves (90, 50%)": (90, 0.5),
}


def job(task):
    key, run, agents, share = task
    func, lower, upper, optimum, budget = lab.problem(key)
    seed = np.random.SeedSequence([7, sum(map(ord, key)), run])
    s = lab.SoundSearch(func, lower, upper, rng=np.random.default_rng(seed),
                        pop_size=agents, final_size=4, kappa_start=0.0,
                        kappa=8.0, refine=0.1)
    r = s.run(evaluations=int(budget * share))
    return max(0.0, r.best_fitness - optimum)


if __name__ == "__main__":
    keys = ["c22", "c24"]
    with Pool(os.cpu_count()) as pool:
        for name, (agents, share) in CONFIGS.items():
            tasks = [(k, r, agents, share) for k in keys for r in range(31)]
            values = np.array(pool.map(job, tasks, chunksize=1))
            c22, c24 = values[:31], values[31:]
            print(f"{name:30s} c22 mean {c22.mean():6.1f}, trapped {(c22 > 50).sum():2d}/31"
                  f" | c24 mean {c24.mean():6.1f}, at 100: {(abs(c24 - 100) < 1).sum():2d}/31",
                  flush=True)
