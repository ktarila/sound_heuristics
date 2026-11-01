"""Reproduce the README results.

    python benchmark.py                      # f1-f23, ranked against GWO/PSO/GSA
    python benchmark.py --suite shifted      # f1-f13 (not f8), best point moved
    python benchmark.py --suite rotated      # ... moved and turned
    python benchmark.py --ablate random      # listen to a random agent instead
    python benchmark.py --ablate towards     # never move away from an agent
    python benchmark.py --refine 0 --kappa 1 # switch parts off

Same effort as the Grey Wolf Optimizer paper: 30 agents x 500 iterations
(15,030 evaluations) per run, 30 runs per function.
"""
import argparse
import os
from multiprocessing import Pool

import numpy as np

from sound_heuristic import config as cfg
from sound_heuristic import fitness
from sound_heuristic.solution import SoundSearch

# Average results published by Mirjalili et al. (2014), Grey Wolf
# Optimizer, Advances in Engineering Software 69, 46-61.
PUBLISHED = {
    "GWO": [6.59e-28, 7.18e-17, 3.29e-6, 5.61e-7, 26.81258, 0.816579,
            0.002213, -6123.1, 0.310521, 1.06e-13, 0.004485, 0.053438,
            0.654464, 4.042493, 0.000337, -1.03163, 0.397889, 3.000028,
            -3.86263, -3.28654, -10.1514, -10.4015, -10.5343],
    "PSO": [0.000136, 0.042144, 70.12562, 1.086481, 96.71832, 0.000102,
            0.122854, -4841.29, 46.70423, 0.276015, 0.009215, 0.006917,
            0.006675, 3.627168, 0.000577, -1.03163, 0.397887, 3.0,
            -3.86278, -3.26634, -6.8651, -8.45653, -9.95291],
    "GSA": [2.53e-16, 0.055655, 896.5347, 7.35487, 67.54309, 2.5e-16,
            0.089441, -2821.07, 25.96841, 0.062087, 27.70154, 1.799617,
            8.899084, 5.859838, 0.003673, -1.03163, 0.397887, 3.0,
            -3.86278, -3.31778, -5.95512, -9.68447, -10.5364],
}

# Functions whose best point can be moved and stay inside the limits.
# f8's best point is near a limit; f14-f23's are already off-centre.
TRANSFORMABLE = [1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13]


class RandomSource(SoundSearch):
    """Test version: listens to a random agent instead of the loudest."""

    def loudest_source(self, population, fitness, kappa):
        n = len(population)
        pick = self.rng.integers(0, n - 1, n)
        return pick + (pick >= np.arange(n))


class NearestSource(SoundSearch):
    """Test version: listens to the nearest agent, ignoring loudness."""

    def loudest_source(self, population, fitness, kappa):
        return super().loudest_source(population, np.zeros(len(fitness)), 1)


class TowardsOnly(SoundSearch):
    """Test version: always moves towards the agent heard, never away."""

    @staticmethod
    def direction(fitness, source):
        return np.ones(len(fitness))


ALGORITHMS = {"none": SoundSearch, "random": RandomSource,
              "nearest": NearestSource, "towards": TowardsOnly}


def transformed(index, suite):
    """``(func, lower, upper, best value)`` of a function in a suite.

    "shifted" moves the best point to a fixed random place (within 60% of
    the range around the centre); "rotated" also turns the function by a
    fixed random angle, so coordinates no longer act independently.
    """
    problem = fitness.get_problem(index)
    if suite == "classic":
        return problem.func, problem.lower, problem.upper, problem.optimum
    rng = np.random.default_rng(1000 + index)
    half = (problem.upper - problem.lower) / 2
    centre = (problem.upper + problem.lower) / 2
    shift = centre + rng.uniform(-0.6, 0.6, problem.lower.size) * half
    rotation = np.eye(problem.lower.size)
    if suite == "rotated":
        gauss = np.random.default_rng(2000 + index).normal(
            size=(problem.lower.size,) * 2)
        q, r = np.linalg.qr(gauss)
        rotation = q * np.sign(np.diag(r))

    def func(x, base=problem.func):
        return base((np.asarray(x) - shift) @ rotation.T)
    return func, problem.lower, problem.upper, problem.optimum


def one_run(task):
    """Best value found in one run."""
    index, run, args = task
    func, lower, upper, _ = transformed(index, args.suite)
    noise_seed, search_seed = np.random.SeedSequence(
        [args.seed, index, run]).spawn(2)
    fitness.seed_noise(noise_seed)
    search = ALGORITHMS[args.ablate](
        func, lower, upper, pop_size=args.pop, kappa=args.kappa,
        kappa_start=args.kappa_start, refine=args.refine,
        archive=args.archive, rng=np.random.default_rng(search_seed))
    return search.run(args.iterations).best_fitness


def ranks(means):
    """Place of each algorithm on each function (1 = best); results equal
    to 4 significant figures share the better place."""
    names = ["Sound"] + list(PUBLISHED)
    table = {name: [] for name in names}
    for i, mean in enumerate(means):
        rounded = {"Sound": float(f"{mean:.4g}")}
        rounded.update({name: float(f"{PUBLISHED[name][i]:.4g}")
                        for name in PUBLISHED})
        for name in names:
            table[name].append(
                1 + sum(rounded[other] < rounded[name] for other in names))
    return table


def report_ranks(means):
    """Print average places, wins, and one-to-one records."""
    table = ranks(means)
    groups = {"all": slice(0, 23), "f1-f7": slice(0, 7),
              "f8-f13": slice(7, 13), "f14-f23": slice(13, 23)}
    print("\nMean rank (lower is better):")
    print(f"{'':6}" + "".join(f"{g:>9}" for g in groups) + "  best on")
    for name, row in table.items():
        cells = "".join(f"{np.mean(row[s]):9.2f}" for s in groups.values())
        print(f"{name:6}{cells}  {row.count(1)}")
    for other in PUBLISHED:
        pairs = list(zip(table["Sound"], table[other]))
        win = sum(a < b for a, b in pairs)
        tie = sum(a == b for a, b in pairs)
        print(f"Sound vs {other} (win/tie/loss): "
              f"{win}/{tie}/{len(pairs) - win - tie}")
    print("Sound rank per function:", table["Sound"])


def parse_args():
    """Read program arguments."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--suite", default="classic",
                        choices=["classic", "shifted", "rotated"])
    parser.add_argument("--funcs", type=int, nargs="+", default=None)
    parser.add_argument("--runs", type=int, default=30)
    parser.add_argument("--iterations", type=int, default=500)
    parser.add_argument("--pop", type=int, default=30)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--jobs", type=int, default=os.cpu_count())
    parser.add_argument("--kappa", type=float, default=cfg.KAPPA)
    parser.add_argument("--kappa-start", type=float, default=cfg.KAPPA_START)
    parser.add_argument("--refine", type=float, default=cfg.REFINE)
    parser.add_argument("--archive", type=float, default=cfg.ARCHIVE)
    parser.add_argument("--ablate", default="none", choices=list(ALGORITHMS),
                        help="replace loudest-source listening")
    return parser.parse_args()


def main():
    """Run every function in the suite and print a summary."""
    args = parse_args()
    funcs = args.funcs or (list(range(1, 24)) if args.suite == "classic"
                           else TRANSFORMABLE)
    tasks = [(i, run, args) for i in funcs for run in range(args.runs)]
    with Pool(args.jobs) as pool:
        values = np.array(pool.map(one_run, tasks, chunksize=1))
    values = values.reshape(len(funcs), args.runs)

    print(f"suite={args.suite} runs={args.runs} pop={args.pop} "
          f"iterations={args.iterations} kappa={args.kappa} "
          f"refine={args.refine} archive={args.archive} "
          f"ablate={args.ablate}")
    print(f"{'f':>4} {'mean':>11} {'std':>10} {'median':>11} "
          f"{'log10 err':>9}")
    log_errors = []
    for index, row in zip(funcs, values):
        optimum = transformed(index, args.suite)[3]
        log_error = np.median(np.log10(np.abs(row - optimum) + 1e-300))
        log_errors.append(log_error)
        print(f"f{index:<3} {row.mean():11.4g} {row.std(ddof=1):10.3g} "
              f"{np.median(row):11.4g} {log_error:9.2f}")
    print(f"mean of median log10 error: {np.mean(log_errors):.3f}")
    if args.suite == "classic" and funcs == list(range(1, 24)):
        report_ranks(values.mean(axis=1))


if __name__ == "__main__":
    main()
