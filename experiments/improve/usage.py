import sys, pathlib; here = pathlib.Path(__file__).resolve().parent; sys.path.insert(0, str(here)); sys.path.insert(0, str(here.parents[1]))
import numpy as np, hyper3
from multiprocessing import Pool
from sound_heuristic import cec2017 as C
def one(task):
    f, run, stall = task
    p = C.get_problem(f, 10)
    s = hyper3.EpisodeHyper(p.func, p.lower, p.upper, pop_size=50, stall=stall, rng=np.random.default_rng(run))
    s.run(1999)
    return f, stall, s.usage
if __name__ == '__main__':
  tasks = [(f, r, st) for st in (0.1, 0.05) for f in (5, 10, 12, 14, 16, 22, 24, 26, 30) for r in range(4)]
  with Pool(8) as pool:
      out = pool.map(one, tasks)
  from collections import defaultdict
  agg = defaultdict(lambda: defaultdict(int))
  for f, st, u in out:
      for k, v in u.items(): agg[(st, f)][k] += v
  for key in sorted(agg):
      print(key, dict(agg[key]), 'groups per run', sum(agg[key].values())/4)
