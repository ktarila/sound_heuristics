"""Where does the group go on a composition function? At checkpoints,
count agents nearest to each component's centre and the best value
there. Usage: python trap.py FUNC SEEDS"""
import sys
import numpy as np
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))
from sound_heuristic import cec2017
from sound_heuristic.solution import SoundSearch

FUNC = int(sys.argv[1])
SEEDS = [int(s) for s in sys.argv[2].split(",")]
DIM = 10
TOTAL = cec2017.budget(DIM)
p = cec2017.get_problem(FUNC, DIM)
centres = cec2017._data(FUNC, DIM)[0][:, :DIM] if np.ndim(cec2017._data(FUNC, DIM)[0]) == 2 else None
k = len(cec2017._COMPOSITION[FUNC])
centres = np.asarray(cec2017._data(FUNC, DIM)[0]).reshape(-1, DIM)[:k] if centres is None else centres[:k]


class Watch(SoundSearch):
    marks = None

    def _record(self, best_f):
        super()._record(best_f)
        pop = getattr(self, "_pop", None)


def main():
    for seed in SEEDS:
        s = SoundSearch(p.func, p.lower, p.upper, pop_size=18 * DIM,
                        final_size=4, rng=np.random.default_rng(seed))
        marks = [0.002, 0.01, 0.03, 0.06, 0.1, 0.2, 0.4, 0.7]
        rows = []
        orig = s.compute_move

        def move(population, fitness, echoes, step, kappa, s=s):
            if marks and s.evaluations >= marks[0] * TOTAL:
                marks.pop(0)
                d = np.linalg.norm(population[:, None, :] - centres[None],
                                   axis=2)
                near = d.argmin(axis=1)
                counts = np.bincount(near, minlength=k)
                bests = [fitness[near == c].min() - p.optimum
                         if (near == c).any() else np.nan for c in range(k)]
                dbest = d[fitness.argmin()]
                rows.append((s.evaluations / TOTAL, len(population), counts,
                             bests, dbest))
            return orig(population, fitness, echoes, step, kappa)
        s.compute_move = move
        r = s.run(evaluations=TOTAL)
        print(f"F{FUNC} seed {seed}: final {r.best_fitness - p.optimum:.2f}")
        for share, n, counts, bests, dbest in rows:
            b = " ".join(f"{v:8.1f}" for v in bests)
            dd = " ".join(f"{v:6.1f}" for v in dbest)
            print(f"  {share:5.3f} n={n:3d} agents per valley {counts} "
                  f"best per valley {b} | best agent's distance {dd}")


if __name__ == "__main__":
    main()
