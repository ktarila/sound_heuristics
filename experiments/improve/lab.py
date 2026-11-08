"""Test bench for F4/F8 work. Runs one variant on stand-in functions and
saves results in benchmark.py's format (for compare.py).

Functions (key: what it is, budget):
  c5, c8   CEC 2017 F5 / F8: rotated Rastrigin (stand-ins for CEC 2022 F4)
  c7, c17, c22, c24  CEC 2017 guards (Lunacek, hybrid, two blends)
  q<F>x<k> new instance k of the CEC 2022 form F (experiments/next/forms.py), 200k
  p0..p4   new instances of the CEC 2022 F8 mix (Katsuura 30%, HappyCat
           20%, Griewank-Rosenbrock 20%, Schwefel 10%, Ackley 20%) with
           their own random shift, rotation and coordinate order; 200,000
           evaluations as in CEC 2022. The real F8 instance is not used.

Usage: python lab.py NAME VARIANT FUNCS... [--runs N] [KEY=VALUE ...]
VARIANT: "sound" (built-in) or a prototype class "module.Class".
KEY=VALUE pairs are passed to the search (numbers parsed).
"""
import importlib
import json
import os
import sys
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "next"))
from sound_heuristic import cec2017, cec2022  # noqa: E402
from sound_heuristic.solution import SoundSearch  # noqa: E402

DIM = 10
OUT = os.path.join(os.path.dirname(HERE), "v5")
PARTS = cec2022._HYBRID[8]


def proxy8(seed, dim=DIM):
    """A new instance of the CEC 2022 F8 mix."""
    rng = np.random.default_rng(5000 + seed)
    shift = rng.uniform(-80, 80, dim)
    q, r = np.linalg.qr(rng.normal(size=(dim, dim)))
    matrix = q * np.sign(np.diag(r))
    order = rng.permutation(dim)
    sizes = [int(np.ceil(share * dim)) for share, _ in PARTS[:-1]]
    sizes.append(dim - sum(sizes))

    def func(x):
        x = np.atleast_2d(np.asarray(x, dtype=float))
        y = cec2022._shift_rotate(x, shift, matrix, 1.0)[:, order]
        total, start = 0.0, 0
        for size, (_, name) in zip(sizes, PARTS):
            f, rate = cec2022._BASIC[name]
            total = total + f(y[:, start:start + size] * rate)
            start += size
        return total
    return func, shift


def problem(key):
    """(func, lower, upper, optimum, budget)."""
    if key.startswith("c"):
        p = cec2017.get_problem(int(key[1:]), DIM)
        return p.func, p.lower, p.upper, p.optimum, cec2017.budget(DIM)
    if key.startswith("q"):  # new instance of a CEC 2022 form: q<form>x<instance>
        sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1] / "next"))
        import forms
        form, inst = key[1:].split("x")
        return (forms.make(int(form), int(inst)), np.full(DIM, -100.0),
                np.full(DIM, 100.0), 0.0, 200_000)
    func, _ = proxy8(int(key[1:]))
    return func, np.full(DIM, -100.0), np.full(DIM, 100.0), 0.0, 200_000


def make_class(variant):
    if variant == "sound":
        return SoundSearch
    module, cls = variant.rsplit(".", 1)
    return getattr(importlib.import_module(module), cls)


def one(task):
    key, run, variant, kwargs = task
    func, lower, upper, optimum, budget = problem(key)
    seed = np.random.SeedSequence([7, sum(map(ord, key)), run])
    settings = dict(pop_size=18 * DIM, final_size=4, kappa_start=0.0,
                    kappa=8.0, refine=0.1)
    settings.update(kwargs)
    search = make_class(variant)(func, lower, upper,
                                 rng=np.random.default_rng(seed), **settings)
    value = search.run(evaluations=budget).best_fitness - optimum
    return max(0.0, float(value)) if value > 1e-8 else 0.0


def parse(value):
    try:
        return float(value) if "." in value or "e" in value else int(value)
    except ValueError:
        return value


def main():
    args = sys.argv[1:]
    runs = 51
    if "--runs" in args:
        i = args.index("--runs")
        runs = int(args[i + 1])
        del args[i:i + 2]
    name, variant = args[0], args[1]
    funcs = [a for a in args[2:] if "=" not in a]
    kwargs = dict(a.split("=", 1) for a in args[2:] if "=" in a)
    kwargs = {k: parse(v) for k, v in kwargs.items()}
    tasks = [(f, r, variant, kwargs) for f in funcs for r in range(runs)]
    with Pool(os.cpu_count()) as pool:
        values = pool.map(one, tasks, chunksize=1)
    errors = {f: values[i * runs:(i + 1) * runs] for i, f in enumerate(funcs)}
    os.makedirs(OUT, exist_ok=True)
    record = {"name": name, "suite": "lab", "dim": DIM, "runs": runs,
              "evaluations": "100k (c) / 200k (p)",
              "variant": variant, "settings": kwargs, "errors": errors}
    with open(os.path.join(OUT, f"{name}.json"), "w") as handle:
        json.dump(record, handle, indent=1)
    for f, e in errors.items():
        print(f"{f:4s} mean {np.mean(e):9.4g}  median {np.median(e):9.4g}")


if __name__ == "__main__":
    main()
