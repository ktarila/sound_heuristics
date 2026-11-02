"""Compare saved benchmark results with statistical tests.

    python compare.py results/cec2022_D10_*.json --control v3-noisy
    python compare.py results/cec2022_D10_sound.json --published

Prints, for every function, each algorithm's mean error, and whether the
control is significantly better (+), worse (-) or not different (=) from
it (Wilcoxon rank-sum test, 5% level). Then the Friedman test on the mean
errors across functions, and Holm's comparison of the control with each
other algorithm. Errors up to 1e-8 count as 0, and all errors are
compared to 6 significant figures (some result files are written to only
6), so equal results are not mistaken for different ones.

``--published`` adds the CEC 2022 competition entries, from the
organisers' result files (downloaded on first use).
"""
import argparse
import json

import numpy as np

from sound_heuristic import cec2022, stats


def load(paths):
    """Saved results, one record per file."""
    return [json.load(open(path, encoding="utf-8")) for path in paths]


def entries(first, names):
    """Records for the CEC 2022 competition entries ``names`` (all if
    empty), matching the suite of record ``first``."""
    if first["suite"] != "cec2022":
        raise SystemExit("--published needs CEC 2022 results")
    dim = first["dim"]
    results = cec2022.published(dim)
    unknown = set(names) - set(results)
    if unknown:
        raise SystemExit(f"unknown entries {sorted(unknown)}; "
                         f"choose from {list(results)}")
    return [{"name": name, "suite": "cec2022", "dim": dim, "runs": 30,
             "evaluations": cec2022.BUDGET[dim],
             "errors": {str(f): list(errors[f]) for f in range(1, 13)}}
            for name, errors in results.items() if not names or name in names]


def check(records):
    """Names, functions and errors, checked to cover the same functions."""
    funcs = list(records[0]["errors"])
    for record in records:
        if list(record["errors"]) != funcs:
            raise ValueError(f"{record['name']} covers different functions")
        if (record["suite"], record.get("dim")) != (
                records[0]["suite"], records[0].get("dim")):
            raise ValueError(f"{record['name']} is from a different suite")
    names = [record["name"] for record in records]
    if len(set(names)) != len(names):
        raise ValueError("every result needs a different name")
    errors = {record["name"]: {f: _round(stats.snap(record["errors"][f]))
                               for f in funcs} for record in records}
    return names, funcs, errors


def _round(values, digits=6):
    """``values`` to ``digits`` significant figures."""
    return np.array([float(f"{v:.{digits}g}") for v in values])


def main():
    """Print the comparison tables."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("files", nargs="+")
    parser.add_argument("--control", default=None,
                        help="name of the algorithm to compare the others "
                             "with (default: the first file)")
    parser.add_argument("--published", nargs="*", default=None,
                        metavar="NAME",
                        help="add the CEC 2022 competition entries (all, "
                             "or the ones named)")
    parser.add_argument("--alpha", type=float, default=0.05)
    args = parser.parse_args()
    records = load(args.files)
    first = records[0]
    if args.published is not None:
        records += entries(first, args.published)
    names, funcs, errors = check(records)
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
            mark = ""
            if name != control:
                test = stats.rank_sum(errors[control][f], errors[name][f],
                                      args.alpha)
                mark = {"a": "+", "b": "-", "=": "="}[test.winner]
                tally[name]["+-=".index(mark)] += 1
            cells.append(f"{np.mean(errors[name][f]):.3g} {mark}"
                         .rstrip().rjust(width))
        print(f"F{f:<4}" + "".join(cells))
    print(f"\n{control} better / worse / no different:")
    for name, (better, worse, same) in tally.items():
        print(f"  vs {name:{width}} {better:2} / {worse:2} / {same:2}")

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
