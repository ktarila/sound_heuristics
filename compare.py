"""Compare saved benchmark results with statistical tests.

    python compare.py results/cec2022_D10_*.json --control sound

Prints, for every function, each algorithm's mean error, and whether the
control is significantly better (+), worse (-) or not different (=) from
it (Wilcoxon rank-sum test, 5% level). Then the Friedman test on the mean
errors across functions, and Holm's comparison of the control with each
other algorithm. Errors below 1e-8 count as 0.
"""
import argparse
import json

import numpy as np

from sound_heuristic import stats


def load(paths):
    """Saved results, checked to cover the same functions and runs."""
    records = [json.load(open(path, encoding="utf-8")) for path in paths]
    funcs = list(records[0]["errors"])
    for record in records:
        if list(record["errors"]) != funcs:
            raise ValueError(f"{record['name']} covers different functions")
        if (record["suite"], record.get("dim")) != (
                records[0]["suite"], records[0].get("dim")):
            raise ValueError(f"{record['name']} is from a different suite")
    names = [record["name"] for record in records]
    if len(set(names)) != len(names):
        raise ValueError("every result file needs a different name")
    errors = {record["name"]: {f: np.array(record["errors"][f])
                               for f in funcs} for record in records}
    return names, funcs, errors, records[0]


def main():
    """Print the comparison tables."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("files", nargs="+")
    parser.add_argument("--control", default=None,
                        help="name of the algorithm to compare the others "
                             "with (default: the first file)")
    parser.add_argument("--alpha", type=float, default=0.05)
    args = parser.parse_args()
    names, funcs, errors, first = load(args.files)
    control = args.control or names[0]
    if control not in names:
        raise SystemExit(f"--control must be one of {names}")
    others = [n for n in names if n != control]

    label = first["suite"] + (f", {first['dim']} coordinates"
                              if "dim" in first else "")
    print(f"{label}; {first['runs']} runs; {first['evaluations']} "
          f"evaluations per run")
    print(f"Mean error; +/-/= : {control} significantly better / worse / "
          f"no different (Wilcoxon rank-sum, {args.alpha:.0%} level)\n")
    width = max(12, *(len(n) + 2 for n in names))
    print("F".ljust(5) + "".join(n.rjust(width) for n in names))
    tally = {n: [0, 0, 0] for n in others}
    for f in funcs:
        cells = []
        for name in names:
            mean = np.mean(np.where(errors[name][f] < stats.TOLERANCE, 0,
                                    errors[name][f]))
            mark = ""
            if name != control:
                test = stats.rank_sum(errors[control][f], errors[name][f],
                                      args.alpha)
                mark = {"a": "+", "b": "-", "=": "="}[test.winner]
                tally[name]["+-=".index(mark)] += 1
            cells.append(f"{mean:.3g} {mark}".rstrip().rjust(width))
        print(f"F{f:<4}" + "".join(cells))
    print("\n+/-/= totals: " + "; ".join(
        f"vs {n}: {t[0]}/{t[1]}/{t[2]}" for n, t in tally.items()))

    table = np.array([[np.mean(errors[n][f]) for n in names] for f in funcs])
    result = stats.friedman(table)
    print("\nFriedman test on mean errors (average rank, 1 = best):")
    for name, rank in sorted(zip(names, result.average_ranks),
                             key=lambda pair: pair[1]):
        print(f"  {name:{width}} {rank:.2f}")
    print(f"  statistic {result.statistic:.2f}, p-value {result.p_value:.3g}")

    print(f"\nHolm's comparison with {control} "
          "(adjusted p-value below the level means a real difference):")
    for row in stats.holm(result.average_ranks, names, len(funcs), control):
        side = ("worse than" if row.z > 0 else "better than" if row.z < 0
                else "the same as")
        print(f"  {row.name:{width}} ranks {side} {control}; "
              f"p = {row.p_value:.3g}, adjusted p = {row.adjusted_p_value:.3g}")


if __name__ == "__main__":
    main()
