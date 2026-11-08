"""Quick look: run a prototype on a few seeds of some bench functions with
only 2 worker processes. Usage: python smoke.py module.Class SEEDS func..."""
import os
import sys
from multiprocessing import Pool

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1] / "improve"))
import lab  # noqa: E402
import numpy as np  # noqa: E402


def job(args):
    key, run, variant = args
    return lab.one((key, run, variant, {}))


if __name__ == "__main__":
    variant, seeds = sys.argv[1], int(sys.argv[2])
    funcs = sys.argv[3:]
    tasks = [(f, r, variant) for f in funcs for r in range(seeds)]
    with Pool(2) as pool:
        values = pool.map(job, tasks, chunksize=1)
    for i, f in enumerate(funcs):
        e = values[i * seeds:(i + 1) * seeds]
        print(f"{f:4s} mean {np.mean(e):9.4g} median {np.median(e):9.4g}  "
              f"{np.round(e, 2).tolist()}")
