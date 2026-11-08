"""Trace one run: best error, group size, step and hearing memory, spread,
at fixed shares of the budget. Usage: python trace.py FUNC [SEEDS]"""
import sys
import numpy as np
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))
from sound_heuristic import cec2017
from sound_heuristic import solution
from sound_heuristic.solution import SoundSearch

FUNC = int(sys.argv[1])
SEEDS = int(sys.argv[2]) if len(sys.argv) > 2 else 3
DIM = 10
TOTAL = cec2017.budget(DIM)

log = []
orig_update = solution.SuccessMemory.update


class Traced(SoundSearch):
    def sound_phase(self, budget, patience=None):
        log.append(("phase", self.evaluations))
        return super().sound_phase(budget, patience)

    def _record(self, best_f):
        super()._record(best_f)


def main():
    p = cec2017.get_problem(FUNC, DIM)
    for seed in range(SEEDS):
        log.clear()
        snaps = []
        s = Traced(p.func, p.lower, p.upper, pop_size=18 * DIM, final_size=4,
                   rng=np.random.default_rng(seed))
        # wrap memory.sample to snapshot the memory and the group
        orig_sample = solution.SuccessMemory.sample
        marks = list(np.linspace(0.05, 0.7, 14))

        def sample(mem, n, rng, s=s):
            if marks and s.evaluations >= marks[0] * TOTAL:
                marks.pop(0)
                best = min(f for _, f in s._history) - p.optimum
                snaps.append((s.evaluations / TOTAL, n, best,
                              np.mean(mem.step), np.nanmean(mem.hearing)))
            return orig_sample(mem, n, rng)
        solution.SuccessMemory.sample = sample
        r = s.run(evaluations=TOTAL)
        solution.SuccessMemory.sample = orig_sample
        phases = [round(e / TOTAL, 2) for k, e in log]
        print(f"F{FUNC} seed {seed}: final {r.best_fitness - p.optimum:.3f}"
              f" phases start at {phases}")
        for share, n, best, st, he in snaps:
            print(f"   {share:5.2f} n={n:4d} best={best:9.3f} step={st:.2f}"
                  f" hearing={he:.2f}")


if __name__ == "__main__":
    main()
