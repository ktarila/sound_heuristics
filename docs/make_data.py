"""Build the data for the web page.

Three groups of functions: CEC 2022 (12), CEC 2017 (29, the design set of
version 3) and the 23 classic functions (Yao et al., 1999). For each
function this writes ``docs/data/<group>_<number>.js`` with:

* a surface: the function with two of its coordinates free and the others
  held at the best point, on an 81 x 81 grid;
* recorded runs of versions 1, 2 and 3 on that two-coordinate problem:
  where every agent is at 61 moments of the run, and the best error so far;
* recorded runs of the three versions on the real function (10 coordinates
  for the CEC groups, the usual dimension for the classic ones), with the
  settings and random seeds of the first runs of the benchmark.

``docs/tables.js`` holds the 30-run averages shown in the tables, read
from the saved benchmark files in ``results/``.

Run from the repository root:  python docs/make_data.py
(about 30 minutes on 8 cores). Settings, as environment variables:
FUNCTION_GROUPS (default "cec2022,cec2017,classic"), RUNS (recorded runs per
version, default 3), ONLY_TABLE=1 (redo just tables.js).
The CEC data files must be in cec2022_data/ and cec2017_data/ (see README).
"""
import json
import os
import subprocess
import sys
import types
from collections import namedtuple
from functools import lru_cache
from multiprocessing import Pool

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import benchmark  # noqa: E402
from sound_heuristic import cec2017, cec2022, fitness, stats  # noqa: E402
from sound_heuristic.solution import SoundSearch  # noqa: E402

DOCS = os.path.join(ROOT, "docs")
DATA_DIR = os.path.join(DOCS, "data")
V1_COMMIT = "b703cac"  # the last commit before version 2
GRID = 81
BUDGET = 5_000  # evaluations per run on the two-coordinate problem
FRAMES = 60
RUNS = int(os.environ.get("RUNS", "3"))
POINTS = 120  # moments recorded on the real function
GROUPS = os.environ.get("FUNCTION_GROUPS", "cec2022,cec2017,classic").split(",")
SIZES = {"cec2022": list(range(1, 13)), "cec2017": list(cec2017.FUNCS),
         "classic": list(range(1, 24))}
RESULTS = os.path.join(ROOT, "results")

# ``func`` gives errors; ``raw`` gives the function's own values (``offset`` is
# the best possible value). The real runs search ``raw``, as ``benchmark.py``
# does, so that they are bit for bit the runs of the saved benchmark.
Problem = namedtuple("Problem", "func lower upper best optimum raw offset")


# -- the problems -----------------------------------------------------------

# best points of the classic functions (zero where not listed); for the CEC
# functions they are read from the data files
CLASSIC_BEST = {
    5: 1.0, 6: -0.5, 8: 420.9687, 12: -1.0, 13: 1.0,
    14: [-32, -32], 15: [0.19283, 0.19083, 0.12299, 0.13576],
    16: [0.08984, -0.71266], 17: [np.pi, 2.275], 18: [0, -1],
    19: [0.114614, 0.555649, 0.852547],
    20: [0.20169, 0.150011, 0.476874, 0.275332, 0.311652, 0.6573],
    21: [4, 4, 4, 4], 22: [4, 4, 4, 4], 23: [4, 4, 4, 4],
}


@lru_cache(maxsize=None)
def search_best_point(group, index):
    """Best point found by version 3 (when it is not known in closed form)."""
    problem = load_problem(group, index, find=False)
    best_x, best_f = None, np.inf
    for seed in range(3):
        search = SoundSearch(problem.func, problem.lower, problem.upper,
                             pop_size=180, final_size=4, kappa_start=0.0,
                             kappa=8.0, refine=0.1,
                             rng=np.random.default_rng(seed))
        result = search.run(evaluations=100_000)
        if result.best_fitness < best_f:
            best_x, best_f = result.best_x, result.best_fitness
    return tuple(best_x)


def load_problem(group, index, find=True):
    """``Problem``: ``func`` maps (n, dim) points to errors (value minus the
    best possible value)."""
    if group == "cec2022":
        p = cec2022.get_problem(index, 10)
        shift = np.asarray(cec2022._load(f"shift_data_{index}.txt"), float)
        best = (shift[0] if shift.ndim == 2 else shift)[:10].copy()
        return Problem(lambda x: p.func(x) - p.optimum, p.lower, p.upper,
                       best, 0.0, p.func, p.optimum)
    if group == "cec2017":
        p = cec2017.get_problem(index, 10)

        def func(x):
            return p.func(x) - p.optimum
        shift = np.asarray(cec2017._data(index, 10)[0], float)
        best = (shift[0] if shift.ndim == 2 else shift)[:10].copy()
        if find and abs(func(best)) > 1e-6:  # e.g. Levy: not at the shift
            best = np.array(search_best_point(group, index))
        return Problem(func, p.lower, p.upper, best, 0.0, p.func, p.optimum)
    p = fitness.get_problem(index)
    known = CLASSIC_BEST.get(index, 0.0)
    best = (np.array(known, dtype=float) if np.ndim(known)
            else np.full(len(p.lower), known))
    return Problem(lambda x: p.func(x) - p.optimum, p.lower, p.upper, best,
                   p.optimum, p.func, p.optimum)


def log_height(error):
    """The height drawn on the page: log10(1 + error)."""
    return np.log10(1.0 + np.maximum(error, 0.0))


def slice_problem(problem):
    """Two coordinates free, the rest at the best point: maps (n, 2) points
    to errors."""
    def func(points):
        points = np.atleast_2d(points)
        full = np.tile(problem.best, (len(points), 1))
        full[:, :2] = points
        return problem.func(full)
    return func, np.asarray(problem.lower)[:2], np.asarray(problem.upper)[:2]


# -- the three versions -----------------------------------------------------

def load_version1():
    """Version 1 of the search, read from the commit that still has it."""
    def show(path):
        return subprocess.run(["git", "show", f"{V1_COMMIT}:{path}"],
                              cwd=ROOT, capture_output=True, text=True,
                              check=True).stdout
    config = types.ModuleType("v1_config")
    exec(show("sound_heuristic/config.py"), config.__dict__)
    source = show("sound_heuristic/solution.py").replace(
        "from sound_heuristic import config as cfg", "")
    module = types.ModuleType("v1_solution")
    module.cfg = config
    exec(source, module.__dict__)
    return module.SoundSearch


@lru_cache(maxsize=None)
def version1_class():
    return load_version1()


def settings(group, version, ten):
    """(agents at the start, keyword settings) for one version. ``ten``: the
    real function, not the two-coordinate slice."""
    long_pop = {"cec2022": 50, "cec2017": 50, "classic": 30}[group]
    if version == 1:
        return (long_pop if ten else 30), {}
    if version == 2:
        pop = long_pop if ten else 30
        return pop, dict(final_size=pop, kappa_start=1.0, kappa=4.0,
                         refine=0.3, stall=0.0, noisy_after=1.0)
    if group == "classic":  # the classic settings are the defaults
        return 30, dict(final_size=None, kappa_start=1.0, kappa=4.0,
                        refine=0.3)
    return (180 if ten else 36), dict(final_size=4, kappa_start=0.0,
                                      kappa=8.0, refine=0.1)


def make_search(version, func, lower, upper, rng, group, ten):
    pop, extra = settings(group, version, ten)
    if version == 1:
        return version1_class()(func, lower, upper, pop_size=pop, rng=rng)
    return SoundSearch(func, lower, upper, pop_size=pop, rng=rng, **extra)


def decimals(span):
    return 3 if span < 5 else 2 if span < 30 else 1


# -- one recorded run on two coordinates --------------------------------------

def record_two(task):
    """Positions of the group and best error so far at ``FRAMES`` moments."""
    group, index, version, run = task
    problem = load_problem(group, index)
    func, lower, upper = slice_problem(problem)
    seed = 1000 * index + run
    if group == "classic":
        fitness.seed_noise(seed)
    pop, _ = settings(group, version, False)
    search = make_search(version, func, lower, upper,
                         np.random.default_rng(seed), group, False)
    snapshots, seen, best = [], [], [np.inf, None]
    original_evaluate, original_fix = search._evaluate, search.fix_boundary

    def evaluate(points):
        values = original_evaluate(points)
        i = int(np.argmin(values))
        if values[i] < best[0]:
            best[0], best[1] = float(values[i]), np.array(points[i])
        seen.append((search.evaluations, best[0]))
        if len(points) == 1:  # refinement: show the one agent at work
            snapshots.append((search.evaluations, best[1][None].copy()))
        return values

    def fix(candidate, previous, *rest):
        snapshots.append((search.evaluations, previous.copy()))
        return original_fix(candidate, previous, *rest)

    search._evaluate, search.fix_boundary = evaluate, fix
    if version == 1:
        search.run(iterations=max(BUDGET // pop - 1, 1))
    else:
        search.run(evaluations=BUDGET)

    used = np.array([e for e, _ in snapshots])
    moments = np.round(BUDGET * (np.arange(FRAMES + 1) / FRAMES) ** 1.5)
    dx, dy = decimals(upper[0] - lower[0]), decimals(upper[1] - lower[1])
    frames = []
    for t in moments:
        k = max(int(np.searchsorted(used, t, side="right")) - 1, 0)
        points = snapshots[k][1]
        frames.append({"x": np.round(points[:, 0], dx).tolist(),
                       "y": np.round(points[:, 1], dy).tolist(),
                       "z": np.round(log_height(func(points)), 2).tolist()})
    seen_used = np.array([e for e, _ in seen])
    seen_best = np.array([b for _, b in seen])
    index_at = np.clip(np.searchsorted(seen_used, moments, side="right") - 1,
                       0, None)
    seen_best = np.where(seen_best <= tolerance(group, index), 0.0, seen_best)
    return {"frames": frames, "evals": [int(t) for t in moments],
            "curve": [float(f"{seen_best[i]:.3g}") for i in index_at],
            "final": float(f"{best[0]:.4g}")}


# -- one recorded run on the real function ------------------------------------

def ten_budget(group):
    if group == "cec2022":
        return cec2022.BUDGET[10]
    if group == "cec2017":
        return cec2017.budget(10)
    return 30 * 501


def run_ten(task):
    """Best error so far at ``POINTS`` moments. Seeds as in
    ``benchmark.py``."""
    group, index, version, run = task
    problem = load_problem(group, index)
    noise_seed, search_seed = np.random.SeedSequence([0, index, run]).spawn(2)
    if group == "classic":
        fitness.seed_noise(noise_seed)
    evaluations = ten_budget(group)
    pop, _ = settings(group, version, True)
    search = make_search(version, problem.raw, problem.lower, problem.upper,
                         np.random.default_rng(search_seed), group, True)
    seen, original = [], search._evaluate

    def evaluate(points):
        values = original(points)
        seen.append((search.evaluations, float(values.min() - problem.offset)))
        return values
    search._evaluate = evaluate
    if version == 1:
        search.run(iterations=500 if group == "classic"
                   else evaluations // pop - 1)
    else:
        search.run(evaluations=evaluations)
    used = np.array([e for e, _ in seen])
    best = np.minimum.accumulate([v for _, v in seen])
    best = np.where(np.abs(best) <= tolerance(group, index), 0.0,
                    np.maximum(best, 0.0))
    moments = np.unique(np.round(np.geomspace(max(pop, 100), evaluations,
                                              POINTS)))
    index_at = np.clip(np.searchsorted(used, moments, side="right") - 1, 0,
                       None)
    return {"evals": [int(t) for t in moments],
            "curve": [float(f"{best[i]:.3g}") for i in index_at],
            "final": float(f"{best[-1]:.4g}")}


# -- the surface --------------------------------------------------------------

def make_surface(task):
    group, index = task
    problem = load_problem(group, index)
    func, lower, upper = slice_problem(problem)
    if group == "classic":
        fitness.seed_noise(0)
    ax = np.linspace(lower[0], upper[0], GRID)
    ay = np.linspace(lower[1], upper[1], GRID)
    xx, yy = np.meshgrid(ax, ay)
    error = func(np.column_stack([xx.ravel(), yy.ravel()]))
    return {"axes": [[float(lower[0]), float(upper[0])],
                     [float(lower[1]), float(upper[1])]],
            "optimum": [float(f"{problem.best[0]:.5g}"),
                        float(f"{problem.best[1]:.5g}")],
            "z": np.round(log_height(error).reshape(GRID, GRID), 3).tolist(),
            "max_error": float(f"{np.max(error):.3g}")}


# -- tables -------------------------------------------------------------------

def load_errors(name):
    with open(os.path.join(RESULTS, name), encoding="utf-8") as handle:
        return json.load(handle)["errors"]


def tolerance(group, index):
    """Errors up to this count as zero. 1e-8 as in the CEC competitions; the
    classic functions' best values are only printed to about 6 digits in the
    literature, so smaller errors are rounding of the printed best value."""
    if group != "classic":
        return 1e-8
    return 2e-5 * max(1.0, abs(fitness.get_problem(index).optimum))


def snap(values, tol=1e-8):
    values = np.asarray(values, float)
    return np.where(values <= tol, 0.0, values)


def spread(runs, tol=1e-8):
    runs = snap(runs, tol)
    return {"zero_runs": int((runs == 0).sum()), "runs": len(runs),
            "best": float(f"{runs.min():.4g}"),
            "median": float(f"{np.median(runs):.4g}"),
            "worst": float(f"{runs.max():.4g}")}


def verdict(a, b, tol=1e-8):
    """Is ``a`` significantly better (+), worse (-) or no different (=)."""
    def rounded(values):  # 6 significant figures, as compare.py does
        return np.array([float(f"{v:.6g}") for v in snap(values, tol)])
    test = stats.rank_sum(rounded(a), rounded(b))
    return {"a": "+", "b": "-", "=": "="}[test.winner]


def table_rows(group):
    """Per function: 30-run averages and comparisons, from ``results/``."""
    rows = {}
    if group == "cec2022":
        v2 = load_errors("cec2022_D10_sound.json")
        v3 = load_errors("cec2022_D10_v3-noisy.json")
        entries = cec2022.published(10)
        for i in SIZES[group]:
            k = str(i)
            scores = {n: float(snap(e[i]).mean()) for n, e in entries.items()}
            best = min(scores, key=scores.get)
            rounded = {n: float(f"{s:.4g}") for n, s in scores.items()}
            mean3 = float(snap(v3[k]).mean())
            place = 1 + sum(s < float(f"{mean3:.4g}") for s in rounded.values())
            tied = sum(s == rounded[best] for s in rounded.values())
            rows[i] = {"v2": float(snap(v2[k]).mean()), "v3": mean3,
                       "v3_runs": spread(v3[k]), "vs_v2": verdict(v3[k], v2[k]),
                       "compare": scores[best],
                       "compare_label": (f"{tied} entries tie" if tied > 1
                                         else best),
                       "place": place, "place_of": 13}
    elif group == "cec2017":
        v2 = load_errors("cec2017_D10_v2.json")
        v3 = load_errors("cec2017_D10_v3-noisy.json")
        de = load_errors("cec2017_D10_de-rule-0.11.json")
        for i in SIZES[group]:
            k = str(i)
            rows[i] = {"v2": float(snap(v2[k]).mean()),
                       "v3": float(snap(v3[k]).mean()),
                       "v3_runs": spread(v3[k]), "vs_v2": verdict(v3[k], v2[k]),
                       "compare": float(snap(de[k]).mean()),
                       "compare_label": "DE rule",
                       "vs_compare": verdict(v3[k], de[k])}
    else:
        v1 = load_errors("classic_v1.json")
        v2 = load_errors("classic_v2.json")
        v3 = load_errors("classic_v3.json")
        for i in SIZES[group]:
            k = str(i)
            optimum = fitness.get_problem(i).optimum
            raw = {n: benchmark.PUBLISHED[n][i - 1] for n in ("GWO", "PSO", "GSA")}
            error = {n: float(snap(abs(raw[n] - optimum), tolerance(group, i)))
                     for n in raw}
            best = min(error, key=error.get)
            tol = tolerance(group, i)
            mean3 = float(snap(v3[k], tol).mean())
            ours = float(f"{optimum + mean3:.4g}")
            place = 1 + sum(float(f"{value:.4g}") < ours for value in raw.values())
            rows[i] = {"v1": float(snap(v1[k], tol).mean()),
                       "v2": float(snap(v2[k], tol).mean()),
                       "v3": mean3, "v3_runs": spread(v3[k], tol),
                       "vs_v2": verdict(v3[k], v2[k], tol),
                       "compare": error[best], "compare_label": best,
                       "published": error, "place": place, "place_of": 4}
    return rows


def classic_v1_one(task):
    index, run = task
    problem = fitness.get_problem(index)
    noise_seed, search_seed = np.random.SeedSequence([0, index, run]).spawn(2)
    fitness.seed_noise(noise_seed)
    search = version1_class()(problem.func, problem.lower, problem.upper,
                              pop_size=30,
                              rng=np.random.default_rng(search_seed))
    result = search.run(iterations=500)
    return float(abs(result.best_fitness - problem.optimum))


def make_classic_v1_results():
    """Run version 1 on the classic functions as ``benchmark.py`` would and
    save the errors (30 runs, seed 0), unless they are already saved."""
    path = os.path.join(RESULTS, "classic_v1.json")
    if os.path.exists(path):
        return
    tasks = [(i, r) for i in SIZES["classic"] for r in range(30)]
    with Pool(min(os.cpu_count(), 8)) as pool:
        finals = pool.map(classic_v1_one, tasks, chunksize=1)
    errors = {}
    for (i, _), value in zip(tasks, finals):
        errors.setdefault(str(i), []).append(value)
    record = {"name": "classic-v1", "suite": "classic", "seed": 0, "runs": 30,
              "pop": 30, "evaluations": 15030,
              "settings": {"version": "1, commit " + V1_COMMIT},
              "errors": errors}
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(record, handle, indent=1)


# -- writing ------------------------------------------------------------------

def write_js(path, name, payload):
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(name + " = ")
        json.dump(payload, handle, separators=(",", ":"))
        handle.write(";\n")


def d20_rows():
    """CEC 2022 at 20 coordinates, version 3 against the 12 entries: per
    function, the mean, the best entry, the place by mean, and how many
    entries are significantly better and worse (Wilcoxon, 5% level)."""
    v3 = load_errors("cec2022_D20_v3.json")
    entries = cec2022.published(20)
    rows = {}
    for i in SIZES["cec2022"]:
        k = str(i)
        scores = {n: float(snap(e[i]).mean()) for n, e in entries.items()}
        best = min(scores, key=scores.get)
        rounded = {n: float(f"{s:.4g}") for n, s in scores.items()}
        mean3 = float(snap(v3[k]).mean())
        tied = sum(s == rounded[best] for s in rounded.values())
        marks = [verdict(v3[k], e[i]) for e in entries.values()]
        rows[i] = {"v3": mean3, "v3_runs": spread(v3[k]),
                   "compare": scores[best],
                   "compare_label": (f"{tied} entries tie" if tied > 1
                                     else best),
                   "place": 1 + sum(s < float(f"{mean3:.4g}")
                                    for s in rounded.values()),
                   "place_of": 13,
                   "entries_better": marks.count("-"),
                   "entries_worse": marks.count("+")}
    return rows


def write_tables():
    tables = {g: table_rows(g) for g in SIZES}
    tables["cec2022_d20"] = d20_rows()
    write_js(os.path.join(DOCS, "tables.js"), "window.SOUND_TABLE", tables)


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    make_classic_v1_results()
    if os.environ.get("ONLY_TABLE"):
        write_tables()
        return
    with Pool(min(os.cpu_count(), 8)) as pool:
        for group in GROUPS:
            indices = SIZES[group]
            surfaces = dict(zip(indices, pool.map(
                make_surface, [(group, i) for i in indices], chunksize=1)))
            tasks = [(group, i, v, r) for i in indices for v in (1, 2, 3)
                     for r in range(RUNS)]
            two = dict(zip(tasks, pool.map(record_two, tasks, chunksize=1)))
            ten = dict(zip(tasks, pool.map(run_ten, tasks, chunksize=1)))
            for i in indices:
                entry = surfaces[i]
                entry["runs"] = {str(v): [two[(group, i, v, r)]
                                          for r in range(RUNS)]
                                 for v in (1, 2, 3)}
                entry["ten_runs"] = {str(v): [ten[(group, i, v, r)]
                                              for r in range(RUNS)]
                                     for v in (1, 2, 3)}
                entry["ten_dim"] = len(load_problem(group, i).lower)
                entry["ten_evals"] = ten_budget(group)
                write_js(os.path.join(DATA_DIR, f"{group}_{i}.js"),
                         f'(window.SOUND_FN = window.SOUND_FN || {{}})'
                         f'["{group}_{i}"]', entry)
                print(group, i, "two:",
                      {v: [f"{r['final']:.3g}" for r in entry["runs"][v]]
                       for v in entry["runs"]},
                      "real:", {v: [r["final"] for r in entry["ten_runs"][v]]
                                for v in entry["ten_runs"]}, flush=True)
    write_tables()
    print("done")


if __name__ == "__main__":
    main()
