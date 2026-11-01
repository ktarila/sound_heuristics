"""Heuristic search algorithms based on sound/light

Examples:
    python entry.py -i 1 -n 1000                  # 30 runs on f1
    python entry.py -i 9 -n 1000 --seed 0 --rho 40
    python entry.py --tune 1 5 9 10 -n 500 --samples 40 --runs 5 --seed 0
"""
import argparse

import numpy as np

from sound_heuristic import config as cfg
from sound_heuristic import fitness
from sound_heuristic.solution import SoundSearch, sample_parameters


def run_many(problem, runs, iterations, seed=None, progress=False, **params):
    """Independent runs, each with its own child seed of ``seed``."""
    fitness.seed_noise(seed)
    results = []
    for child in np.random.SeedSequence(seed).spawn(runs):
        if progress:
            print('.', end='', flush=True)
        search = SoundSearch(problem.func, problem.lower, problem.upper,
                             rng=np.random.default_rng(child), **params)
        results.append(search.run(iterations))
    if progress:
        print()
    return results


def summarise(results, minimisation=cfg.MINIMISATION):
    """Statistics over the best fitness of each run."""
    values = np.array([r.best_fitness for r in results])
    return {
        "Mean": np.mean(values),
        "Std": np.std(values, ddof=1) if len(values) > 1 else 0.0,
        "Median": np.median(values),
        "Best": np.min(values) if minimisation else np.max(values),
        "Worst": np.max(values) if minimisation else np.min(values),
        "Evaluations/run": results[0].evaluations,
    }


def error_score(problem, results):
    """Median log10 distance to the known optimum (lower is better)."""
    errors = np.abs(np.array([r.best_fitness for r in results])
                    - problem.optimum)
    return np.median(np.log10(errors + 1e-16))


def tune(indices, samples, runs, iterations, seed=None):
    """Random search over (rho, momentum, exploration, pull).

    Every candidate sees the same seeds (common random numbers), so
    differences come from the parameters, not luck. Tune on functions
    other than the ones you report, to avoid selection bias.
    """
    problems = [fitness.get_problem(i) for i in indices]
    rng = np.random.default_rng(seed)
    defaults = [[cfg.RHO, cfg.MOMENTUM, cfg.EXPLORATION, cfg.PULL]]
    candidates = np.vstack([defaults, sample_parameters(rng, samples)])
    print(f"Tuning on f{indices}: {len(candidates)} candidates x "
          f"{runs} runs x {iterations} iterations")

    best_score, best_params = np.inf, None
    for k, (rho, momentum, exploration, pull) in enumerate(candidates):
        params = {"rho": rho, "momentum": momentum,
                  "exploration": exploration, "pull": pull}
        score = np.mean([
            error_score(p, run_many(p, runs, iterations, seed, **params))
            for p in problems])
        marker = ""
        if score < best_score:
            best_score, best_params, marker = score, params, "  <- best"
        print(f"{k:3d} rho={rho:7.3f} momentum={momentum:.3f} "
              f"exploration={exploration:.4f} pull={pull:.3f} "
              f"score={score:8.3f}{marker}")

    print("-------Best-----------")
    print(best_params, f"score={best_score:.3f}")
    return best_params


def parse_args():
    """Read program arguments."""
    parser = argparse.ArgumentParser(description=cfg.NAME)
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument('-i', type=int, metavar="INDEX",
                        help="index of fitness function, 1 - 23")
    target.add_argument('--tune', type=int, nargs='+', metavar="INDEX",
                        help="tune parameters on these function indices")
    parser.add_argument('-n', type=int, default=cfg.ITERATIONS,
                        help="iterations per run")
    parser.add_argument('--runs', type=int, default=None,
                        help=f"independent runs (default {cfg.RUNS}, "
                             "or 5 when tuning)")
    parser.add_argument('--pop', type=int, default=cfg.POP_SIZE,
                        help="population size")
    parser.add_argument('--seed', type=int, default=cfg.SEED,
                        help="random seed for reproducible results")
    parser.add_argument('--rho', type=float, default=cfg.RHO)
    parser.add_argument('--momentum', type=float, default=cfg.MOMENTUM)
    parser.add_argument('--exploration', type=float,
                        default=cfg.EXPLORATION)
    parser.add_argument('--pull', type=float, default=cfg.PULL)
    parser.add_argument('--samples', type=int, default=40,
                        help="random candidates to try when tuning")
    return parser.parse_args()


def main():
    """Main entry of program"""
    args = parse_args()
    print(cfg.NAME)
    if args.tune:
        tune(args.tune, args.samples, args.runs or 5, args.n, args.seed)
        return

    problem = fitness.get_problem(args.i)
    results = run_many(problem, args.runs or cfg.RUNS, args.n, args.seed,
                       progress=True, pop_size=args.pop, rho=args.rho,
                       momentum=args.momentum, exploration=args.exploration,
                       pull=args.pull)
    print(f"f{args.i} (dim {problem.lower.size}, "
          f"known optimum {problem.optimum:g})")
    for key, value in summarise(results).items():
        print(f"{key:>16}: {value:g}")


if __name__ == '__main__':
    main()
