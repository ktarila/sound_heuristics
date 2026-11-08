"""Where do failing runs go wrong? Runs version 3 on new instances of a CEC
2022 form and records every group search: when it started and ended, why it
ended, and its best error.

Usage: python trace.py FORM RUNS [INSTANCES]
"""
import sys
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1] / "next"))
import forms  # noqa: E402
from sound_heuristic.solution import SoundSearch  # noqa: E402

V3 = dict(pop_size=180, final_size=4, kappa_start=0.0, kappa=8.0, refine=0.1)


class Traced(SoundSearch):
    def sound_phase(self, budget, patience=None):
        start = self.evaluations
        population, fitness = super().sound_phase(budget, patience)
        self.groups.append((start, self.evaluations, float(fitness.min()),
                            float(np.ptp(fitness)), len(population)))
        return population, fitness


def one(task):
    form, inst, run = task
    func = forms.make(form, inst)
    s = Traced(func, -100 * np.ones(10), 100 * np.ones(10),
               rng=np.random.default_rng([form, inst, run]), **V3)
    s.groups = []
    r = s.run(evaluations=200_000)
    return inst, run, r.best_fitness, s.groups


if __name__ == "__main__":
    form, runs = int(sys.argv[1]), int(sys.argv[2])
    insts = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    tasks = [(form, i, r) for i in range(insts) for r in range(runs)]
    with Pool(8) as pool:
        out = pool.map(one, tasks, chunksize=1)
    for inst, run, best, groups in out:
        g = " | ".join(f"{a/1000:.0f}-{b/1000:.0f}k e={f:.3g} n={n}"
                       for a, b, f, _, n in groups)
        print(f"inst {inst} run {run:2d} final {best:9.4g}  groups: {g}")
    finals = np.array([o[2] for o in out])
    print("mean", finals.mean(), "median", np.median(finals))
