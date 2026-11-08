"""Share of moves that improved, per tenth of the group search, for
different numbers of drafts (ECHO_K set by the caller via argv)."""
import sys
import numpy as np
import lab
import echo

key = sys.argv[1]
func, lower, upper, optimum, budget = lab.problem(key)
for k in (1, 3):
    echo.ECHO_K = k
    rows = []
    finals = []
    for seed in range(2):
        s = echo.Echo(func, lower, upper, rng=np.random.default_rng(seed),
                      pop_size=180, final_size=4, kappa_start=0.0, kappa=8.0,
                      refine=0.1)
        r = s.run(evaluations=budget)
        finals.append(max(0.0, r.best_fitness - optimum))
        p = np.array(s.success)
        rows.append([p[(p[:, 0] >= a) & (p[:, 0] < a + 0.1), 1].mean()
                     if ((p[:, 0] >= a) & (p[:, 0] < a + 0.1)).any() else np.nan
                     for a in np.arange(0, 1, 0.1)])
    print(f"{key} K={k}: errors {np.round(finals, 2).tolist()}  success by tenth:",
          np.round(np.nanmean(rows, axis=0), 3).tolist())
