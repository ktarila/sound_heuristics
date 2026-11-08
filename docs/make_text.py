"""Write docs/meta.js: names, groups and building blocks of the CEC 2017 and
classic functions, read from the code so that the web page cannot drift from
it. The prose (history, properties) is written by hand in docs/functions.js.

Run from the repository root:  python docs/make_text.py
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from sound_heuristic import cec2017, fitness  # noqa: E402

NAMES = {
    "ellips": "Ellipsoid", "bent_cigar": "Bent cigar", "discus": "Discus",
    "zakharov": "Zakharov", "levy": "Levy", "rosenbrock": "Rosenbrock",
    "schaffer_f7": "Schaffer F7", "ackley": "Ackley",
    "weierstrass": "Weierstrass", "griewank": "Griewank",
    "rastrigin": "Rastrigin", "schwefel": "Schwefel", "katsuura": "Katsuura",
    "bi_rastrigin": "Bi-Rastrigin", "grie_rosen": "Griewank-Rosenbrock",
    "escaffer6": "Schaffer F6", "happycat": "HappyCat", "hgbat": "HGBat",
}
SINGLE_NAMES = {1: "Bent cigar", 3: "Zakharov", 4: "Rosenbrock",
                5: "Rastrigin", 6: "Schaffer F7", 7: "Lunacek bi-Rastrigin",
                8: "Non-continuous Rastrigin", 9: "Levy", 10: "Schwefel"}
# the same function in CEC 2022 (checked against the two code files)
ALSO_2022 = {3: "F1", 4: "F2", 5: "F4", 6: "F3", 8: "F4", 9: "F5"}
CLASSIC_NAMES = {
    1: "Sphere", 2: "Schwefel 2.22", 3: "Schwefel 1.2", 4: "Schwefel 2.21",
    5: "Rosenbrock", 6: "Step", 7: "Quartic with noise",
    8: "Schwefel 2.26", 9: "Rastrigin", 10: "Ackley", 11: "Griewank",
    12: "Penalized 1", 13: "Penalized 2", 14: "Shekel's foxholes",
    15: "Kowalik", 16: "Six-hump camel", 17: "Branin",
    18: "Goldstein-Price", 19: "Hartman 3", 20: "Hartman 6",
    21: "Shekel 5", 22: "Shekel 7", 23: "Shekel 10",
}


def cec2017_meta():
    meta = {}
    for i in cec2017.FUNCS:
        entry = {"bias": 100 * i, "also2022": ALSO_2022.get(i)}
        if i in cec2017._SINGLE:
            entry["name"] = SINGLE_NAMES[i]
            entry["group"] = "Unimodal" if i in (1, 3) else "Simple multimodal"
            part = cec2017._SINGLE[i]
            entry["parts"] = [[NAMES[part], "all coordinates"]]
        elif i <= 20:
            shares, names = cec2017._HYBRID[i]
            entry["name"] = f"Hybrid {i - 10}"
            entry["group"] = "Hybrid"
            entry["parts"] = [[NAMES[n], f"{round(s * 100)}% of the coordinates"]
                              for s, n in zip(shares, names)]
        else:
            entry["name"] = f"Composition {i - 20}"
            entry["group"] = "Composition"
            entry["parts"] = []
            for part, _, _, sigma, bias in cec2017._COMPOSITION[i]:
                label = (f"Hybrid {part - 10} (F{part})" if isinstance(part, int)
                         else NAMES[part])
                entry["parts"].append([label, f"sigma {sigma}, bias {bias}"])
        meta[i] = entry
    return meta


def classic_meta():
    meta = {}
    for i in range(1, 24):
        p = fitness.get_problem(i)
        group = ("Unimodal" if i <= 7 else "Multimodal, many local minima"
                 if i <= 13 else "Multimodal, few local minima")
        meta[i] = {"name": CLASSIC_NAMES[i], "group": group,
                   "dim": len(p.lower),
                   "lower": [float(v) for v in p.lower],
                   "upper": [float(v) for v in p.upper],
                   "optimum": float(p.optimum)}
    return meta


def main():
    meta = {"cec2017": cec2017_meta(), "classic": classic_meta()}
    path = os.path.join(ROOT, "docs", "meta.js")
    with open(path, "w", encoding="utf-8") as handle:
        handle.write("window.SOUND_META = ")
        json.dump(meta, handle, separators=(",", ":"))
        handle.write(";\n")
    print("wrote", path)


if __name__ == "__main__":
    main()
