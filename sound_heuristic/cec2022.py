"""CEC 2022 test functions F1-F12 (Kumar et al., 2021), 10 or 20 coordinates.

Written from the competition definitions, following the organisers'
Python code and its known quirks (marked "as in the official code").
Checked side by side with the organisers' C code (cec22_test_func.cpp) on
1,800-4,500 points per function at 10 and 20 coordinates: all 12 agree to
about one part in 10^12. The values where runs get stuck also agree with
the competition entries' published results to 5-8 digits. The data
files (shifts, rotations, shuffles) are downloaded from the organisers'
GitHub on first use and are not included here: that repository has no
license.

Each function takes one point ``(dim,)`` or many points ``(n, dim)``.
The best value of F``k`` is ``BEST[k]``; results are usually reported as
the error ``f(x) - BEST[k]``.
"""
import io
import os
import re
import urllib.request
import zipfile
from collections import namedtuple
from functools import lru_cache
from pathlib import Path

import numpy as np

DATA_URL = ("https://raw.githubusercontent.com/P-N-Suganthan/2022-SO-BO/"
            "main/Python-CEC2022.zip")
DATA_DIR = Path(os.environ.get(
    "CEC2022_DATA", Path(__file__).resolve().parent.parent / "cec2022_data"))
BEST = {1: 300.0, 2: 400.0, 3: 600.0, 4: 800.0, 5: 900.0, 6: 1800.0,
        7: 2000.0, 8: 2200.0, 9: 2300.0, 10: 2400.0, 11: 2600.0,
        12: 2700.0}
DIMS = (10, 20)
BUDGET = {10: 200_000, 20: 1_000_000}  # evaluations per run
LIMIT = 100.0  # every coordinate lies in [-100, 100]
_DATA_FILE = re.compile(r"^(M_\d+_D\d+|shift_data_\d+|shuffle_data_\d+_D\d+)"
                        r"\.txt$")

Problem = namedtuple("Problem", "index func lower upper optimum")


# -- data ------------------------------------------------------------

def download(data_dir=None):
    """Fetch the official data files into ``data_dir``."""
    data_dir = Path(data_dir or DATA_DIR)
    data_dir.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(DATA_URL, timeout=60) as response:
        archive = zipfile.ZipFile(io.BytesIO(response.read()))
    for member in archive.namelist():
        name = os.path.basename(member)
        if "input_data/" in member and _DATA_FILE.match(name):
            (data_dir / name).write_bytes(archive.read(member))


@lru_cache(maxsize=None)
def _load(name):
    path = DATA_DIR / name
    if not path.exists():
        download()
    return np.loadtxt(path)


# -- published results of the competition entries --------------------

RESULTS_URL = ("https://raw.githubusercontent.com/P-N-Suganthan/2022-SO-BO/"
               "main/2022-Full-Download.zip")
# entries with full result files: file prefix -> name. The first four are
# in their official order (1st to 4th); the rest are in no order.
ENTRIES = {
    "EA4eigN100_10": "EA4eig", "NL-SHADE-LBC": "NL-SHADE-LBC",
    "NL-SHADE-RSP-MID": "NL-SHADE-RSP-MID", "S_LSHADE_DP": "S-LSHADE-DP",
    "jSObinexpEig": "jSObinexpEig", "MTT_SHADE": "MTT-SHADE",
    "IMPML-SHADE": "IMPML-SHADE", "SPHH_Ensemble": "SPHH-Ensemble",
    "Co-PPSO": "Co-PPSO", "OMCSOMA": "OMCSOMA", "NLSOMACLP": "NLSOMACLP",
    "ZOCMAES": "ZOCMAES"}
_RESULT_FILE = re.compile(r"Results_and_Ranking/.*/(" + "|".join(
    map(re.escape, ENTRIES)) + r")_\d+_(10|20)\.txt$")


def download_results(data_dir=None):
    """Fetch the entries' result files (from a 15 MB archive; only the
    result files are kept) into ``data_dir/entries``."""
    folder = Path(data_dir or DATA_DIR) / "entries"
    folder.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(RESULTS_URL, timeout=300) as response:
        archive = zipfile.ZipFile(io.BytesIO(response.read()))
    for member in archive.namelist():
        if _RESULT_FILE.search(member):
            (folder / os.path.basename(member)).write_bytes(
                archive.read(member))


def published(dim=10):
    """Final errors of the competition entries: {name: {F: 30 errors}}.

    Each result file has 17 rows of 30 runs: errors at 16 points during
    the run (the last at the end of the budget), then the evaluations
    used.
    """
    folder = DATA_DIR / "entries"
    if not folder.exists():
        download_results()
    results = {}
    for prefix, name in ENTRIES.items():
        results[name] = {}
        for index in range(1, 13):
            text = (folder / f"{prefix}_{index}_{dim}.txt").read_text()
            table = np.array([[float(v) for v in re.split(r"[\s,]+",
                                                         line.strip())]
                              for line in text.splitlines() if line.strip()])
            if table.shape != (17, 30):
                raise ValueError(f"{prefix} F{index}: shape {table.shape}")
            results[name][index] = table[15]
    return results


# -- building blocks -------------------------------------------------

def _shift_rotate(x, shift, matrix, rate, rotate=True):
    """``matrix @ ((x - shift) * rate)`` for every row of ``x``."""
    y = (x - shift) * rate
    return y @ matrix.T if rotate else y


def _zakharov(z):
    half_i = 0.5 * np.arange(1, z.shape[1] + 1)
    s = np.sum(half_i * z, axis=1)
    return np.sum(z ** 2, axis=1) + s ** 2 + s ** 4


def _rosenbrock(z):
    z = z + 1.0
    head, tail = z[:, :-1], z[:, 1:]
    return np.sum(100.0 * (head ** 2 - tail) ** 2 + (head - 1.0) ** 2,
                  axis=1)


def _schaffer_f7(y):
    s = np.sqrt(y[:, :-1] ** 2 + y[:, 1:] ** 2)
    total = np.sum(np.sqrt(s) * (1 + np.sin(50.0 * s ** 0.2) ** 2), axis=1)
    return total ** 2 / (y.shape[1] - 1) ** 2


def _rastrigin(z):
    return np.sum(z ** 2 - 10.0 * np.cos(2 * np.pi * z) + 10.0, axis=1)


def _levy(z):
    w = 1.0 + z / 4.0
    first = np.sin(np.pi * w[:, 0]) ** 2
    last = (w[:, -1] - 1) ** 2 * (1 + np.sin(2 * np.pi * w[:, -1]) ** 2)
    middle = np.sum((w[:, :-1] - 1) ** 2
                    * (1 + 10 * np.sin(np.pi * w[:, :-1] + 1) ** 2), axis=1)
    return first + middle + last


def _bent_cigar(z):
    return z[:, 0] ** 2 + 1e6 * np.sum(z[:, 1:] ** 2, axis=1)


def _hgbat(z):
    z = z - 1.0
    r2, s = np.sum(z ** 2, axis=1), np.sum(z, axis=1)
    return (np.abs(r2 ** 2 - s ** 2) ** 0.5 + (0.5 * r2 + s) / z.shape[1]
            + 0.5)


def _happycat(z):
    z = z - 1.0
    dim = z.shape[1]
    r2, s = np.sum(z ** 2, axis=1), np.sum(z, axis=1)
    return np.abs(r2 - dim) ** 0.25 + (0.5 * r2 + s) / dim + 0.5


def _katsuura(z):
    dim = z.shape[1]
    powers = 2.0 ** np.arange(1, 33)
    t = z[:, :, None] * powers
    inner = np.sum(np.abs(t - np.floor(t + 0.5)) / powers, axis=2)
    factors = (1 + np.arange(1, dim + 1) * inner) ** (10.0 / dim ** 1.2)
    scale = 10.0 / dim ** 2
    return np.prod(factors, axis=1) * scale - scale


def _ackley(z):
    dim = z.shape[1]
    return (np.e - 20.0 * np.exp(-0.2 * np.sqrt(np.sum(z ** 2, axis=1) / dim))
            - np.exp(np.sum(np.cos(2 * np.pi * z), axis=1) / dim) + 20.0)


def _schwefel(z):
    dim = z.shape[1]
    z = z + 4.209687462275036e+002
    rest = np.fmod(np.abs(z), 500.0)
    high = -(500.0 - rest) * np.sin(np.sqrt(500.0 - rest)) \
        + ((z - 500.0) / 100) ** 2 / dim
    low = -(-500.0 + rest) * np.sin(np.sqrt(500.0 - rest)) \
        + ((z + 500.0) / 100) ** 2 / dim
    middle = -z * np.sin(np.sqrt(np.abs(z)))
    terms = np.where(z > 500, high, np.where(z < -500, low, middle))
    return np.sum(terms, axis=1) + 4.189828872724338e+002 * dim


def _griewank_rosenbrock(z):
    z = z + 1.0
    nxt = np.roll(z, -1, axis=1)  # pairs (z_i, z_i+1), last pair wraps
    t = 100.0 * (z ** 2 - nxt) ** 2 + (z - 1.0) ** 2
    return np.sum(t ** 2 / 4000.0 - np.cos(t) + 1.0, axis=1)


def _griewank(z):
    i = np.arange(1, z.shape[1] + 1)
    return (1.0 + np.sum(z ** 2, axis=1) / 4000.0
            - np.prod(np.cos(z / np.sqrt(i)), axis=1))


def _ellipsoid(z):
    dim = z.shape[1]
    return np.sum(10.0 ** (6.0 * np.arange(dim) / (dim - 1)) * z ** 2, axis=1)


def _discus(z):
    return 1e6 * z[:, 0] ** 2 + np.sum(z[:, 1:] ** 2, axis=1)


def _expanded_schaffer_f6(z):
    t = z ** 2 + np.roll(z, -1, axis=1) ** 2
    return np.sum(0.5 + (np.sin(np.sqrt(t)) ** 2 - 0.5)
                  / (1.0 + 0.001 * t) ** 2, axis=1)


# function, scaling of the input ("rate") in the official code
_BASIC = {
    "zakharov": (_zakharov, 1.0), "rosenbrock": (_rosenbrock, 0.02048),
    "rastrigin": (_rastrigin, 0.0512), "levy": (_levy, 1.0),
    "bent_cigar": (_bent_cigar, 1.0), "hgbat": (_hgbat, 0.05),
    "happycat": (_happycat, 0.05), "katsuura": (_katsuura, 0.05),
    "ackley": (_ackley, 1.0), "schwefel": (_schwefel, 10.0),
    "griewank_rosenbrock": (_griewank_rosenbrock, 0.05),
    "griewank": (_griewank, 6.0), "ellipsoid": (_ellipsoid, 1.0),
    "discus": (_discus, 1.0), "schaffer_f6": (_expanded_schaffer_f6, 1.0),
}

# hybrid functions: (share of coordinates, part); the last part takes the rest
_HYBRID = {
    6: [(0.4, "bent_cigar"), (0.4, "hgbat"), (0.2, "rastrigin")],
    7: [(0.1, "hgbat"), (0.2, "katsuura"), (0.2, "ackley"),
        (0.2, "rastrigin"), (0.1, "schwefel"), (0.2, "schaffer_f7")],
    8: [(0.3, "katsuura"), (0.2, "happycat"), (0.2, "griewank_rosenbrock"),
        (0.1, "schwefel"), (0.2, "ackley")],
}

# composition functions: (part, value factor, rotated, sigma, bias)
_COMPOSITION = {
    9: [("rosenbrock", 1.0, True, 10, 0), ("ellipsoid", 1e-6, True, 20, 200),
        ("bent_cigar", 1e-26, True, 30, 300),
        ("discus", 1e-6, True, 40, 100), ("ellipsoid", 1e-6, False, 50, 400)],
    10: [("schwefel", 1.0, False, 20, 0), ("rastrigin", 1.0, True, 10, 200),
         ("hgbat", 1.0, True, 10, 100)],
    11: [("schaffer_f6", 5e-4, True, 20, 0), ("schwefel", 1.0, True, 20, 200),
         ("griewank", 10.0, True, 30, 300),
         ("rosenbrock", 1.0, True, 30, 400),
         ("rastrigin", 10.0, True, 20, 200)],
    12: [("hgbat", 10.0, True, 10, 0), ("rastrigin", 10.0, True, 20, 300),
         ("schwefel", 2.5, True, 30, 500),
         ("bent_cigar", 1e-26, True, 40, 100),
         ("ellipsoid", 1e-6, True, 50, 400),
         ("schaffer_f6", 5e-4, True, 60, 200)],
}


def _hybrid(x, index):
    dim = x.shape[1]
    parts = _HYBRID[index]
    shift = _load(f"shift_data_{index}.txt")[:dim]
    matrix = _load(f"M_{index}_D{dim}.txt")
    order = _load(f"shuffle_data_{index}_D{dim}.txt").astype(int) - 1
    sizes = [int(np.ceil(share * dim)) for share, _ in parts[:-1]]
    sizes.append(dim - sum(sizes))
    y = _shift_rotate(x, shift, matrix, 1.0)[:, order]
    total, start = 0.0, 0
    for size, (_, name) in zip(sizes, parts):
        if name == "schaffer_f7":
            # as in the official code: reads the first coordinates of y,
            # not its own group
            total = total + _schaffer_f7(y[:, :size])
        else:
            func, rate = _BASIC[name]
            total = total + func(y[:, start:start + size] * rate)
        start += size
    return total


def _composition(x, index):
    dim = x.shape[1]
    parts = _COMPOSITION[index]
    shifts = _load(f"shift_data_{index}.txt")[:, :dim]
    matrices = _load(f"M_{index}_D{dim}.txt")
    values, weights = [], []
    for k, (name, factor, rotated, sigma, bias) in enumerate(parts):
        func, rate = _BASIC[name]
        matrix = matrices[k * dim:(k + 1) * dim]
        z = _shift_rotate(x, shifts[k], matrix, rate, rotated)
        values.append(func(z) * factor + bias)
        d2 = np.sum((x - shifts[k]) ** 2, axis=1)
        with np.errstate(divide="ignore"):
            w = np.where(d2 != 0,
                         np.sqrt(1.0 / np.where(d2 != 0, d2, 1.0))
                         * np.exp(-d2 / 2.0 / dim / sigma ** 2), 1.0e99)
        weights.append(w)
    values, weights = np.array(values), np.array(weights)
    flat = np.max(weights, axis=0) == 0
    weights[:, flat] = 1.0
    return np.sum(weights * values, axis=0) / np.sum(weights, axis=0)


def evaluate(x, index):
    """Value of CEC 2022 function F``index`` at point(s) ``x``."""
    x = np.asarray(x, dtype=float)
    single = x.ndim == 1
    x = np.atleast_2d(x)
    dim = x.shape[1]
    if index not in BEST:
        raise ValueError("CEC 2022 function index should be between 1 and 12")
    if dim not in DIMS:
        raise ValueError("CEC 2022 functions are defined for 10 or 20 "
                         "coordinates here")
    if index <= 5:
        shift = _load(f"shift_data_{index}.txt")[:dim]
        matrix = _load(f"M_{index}_D{dim}.txt")
        if index == 3:
            # as in the official code: Schaffer F7 is shifted, not rotated
            value = _schaffer_f7(x - shift)
        else:
            # F4's "non-continuous" step has no effect in the official code
            name = {1: "zakharov", 2: "rosenbrock", 4: "rastrigin",
                    5: "levy"}[index]
            func, rate = _BASIC[name]
            value = func(_shift_rotate(x, shift, matrix, rate))
    elif index <= 8:
        value = _hybrid(x, index)
    else:
        value = _composition(x, index)
    value = value + BEST[index]
    return value[0] if single else value


def get_problem(index, dim=10):
    """CEC 2022 function ``index`` (1 - 12) as a ``Problem``."""
    if index not in BEST:
        raise ValueError("CEC 2022 function index should be between 1 and 12")

    def func(x, _index=index):
        return evaluate(x, _index)
    return Problem(index, func, np.full(dim, -LIMIT), np.full(dim, LIMIT),
                   BEST[index])
