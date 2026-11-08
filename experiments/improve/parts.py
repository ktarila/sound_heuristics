"""Split the final error on an F8 stand-in into its five parts."""
import sys
import numpy as np
import lab
from sound_heuristic import cec2022
from sound_heuristic.solution import SoundSearch

key = int(sys.argv[1]); seeds = range(int(sys.argv[2]))
func, shift = lab.proxy8(key)
rng0 = np.random.default_rng(5000 + key)
rng0.uniform(-80, 80, 10)
q, r = np.linalg.qr(rng0.normal(size=(10, 10))); matrix = q * np.sign(np.diag(r))
order = rng0.permutation(10)
parts = lab.PARTS
sizes = [int(np.ceil(s * 10)) for s, _ in parts[:-1]]; sizes.append(10 - sum(sizes))
print("parts:", [(n, s) for (_, n), s in zip(parts, sizes)])
for seed in seeds:
    s = SoundSearch(func, np.full(10, -100.0), np.full(10, 100.0), pop_size=180, final_size=4,
                    kappa_start=0.0, kappa=8.0, refine=0.1, rng=np.random.default_rng(seed))
    res = s.run(evaluations=200_000)
    y = cec2022._shift_rotate(res.best_x[None], shift, matrix, 1.0)[:, order]
    vals, start = [], 0
    for size, (_, name) in zip(sizes, parts):
        f, rate = cec2022._BASIC[name]
        vals.append(float(f(y[:, start:start + size] * rate)[0])); start += size
    print(f"seed {seed}: total {res.best_fitness:7.3f}  parts " + "  ".join(f"{v:7.3f}" for v in vals))
