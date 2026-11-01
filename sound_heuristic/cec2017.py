"""CEC 2017 test functions (Awad et al., 2016): F1 and F3-F30 at 10, 30,
50 or 100 coordinates. The organisers withdrew F2.

A port of the organisers' C code (cec17_test_func.cpp). That code keeps
two shared work arrays, ``y`` and ``z``, and some functions read what an
earlier step left in them. Those quirks are copied (marked "as in the C
code") so that results can be compared with published ones. The data
files (shifts, rotations, shuffles) are downloaded from the organisers'
GitHub on first use and are not included here: that repository has no
license.

Each function takes one point ``(dim,)`` or many points ``(n, dim)``.
The best value of F``k`` is ``100 * k``; results are usually reported as
the error ``f(x) - 100 * k``.
"""
import io
import math
import os
import re
import urllib.request
import zipfile
from collections import namedtuple
from functools import lru_cache
from pathlib import Path

import numpy as np

DATA_URL = ("https://raw.githubusercontent.com/P-N-Suganthan/"
            "CEC2017-BoundContrained/master/CEC17_fast_pow-C++.zip")
DATA_DIR = Path(os.environ.get(
    "CEC2017_DATA", Path(__file__).resolve().parent.parent / "cec2017_data"))
FUNCS = (1,) + tuple(range(3, 31))
DIMS = (10, 30, 50, 100)
LIMIT = 100.0  # every coordinate lies in [-100, 100]
_DATA_FILE = re.compile(r"^(M_\d+_D\d+|shift_data_\d+|shuffle_data_\d+_D\d+)"
                        r"\.txt$")

Problem = namedtuple("Problem", "index func lower upper optimum")


def budget(dim):
    """Evaluations per run under the competition rules."""
    return 10_000 * dim


# -- data ------------------------------------------------------------

def download(data_dir=None):
    """Fetch the official data files into ``data_dir``."""
    data_dir = Path(data_dir or DATA_DIR)
    data_dir.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(DATA_URL, timeout=120) as response:
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


@lru_cache(maxsize=None)
def _data(index, dim):
    """Shift, rotation and shuffle of F``index``, read as the C code does.

    F1-F20: one shift (the first ``dim`` numbers) and one rotation.
    F21-F30: one shift (first ``dim`` numbers of each line) and one
    rotation per component. Shuffles are made 0-based.
    """
    matrices = _load(f"M_{index}_D{dim}.txt").reshape(-1, dim, dim)
    shifts = np.atleast_2d(_load(f"shift_data_{index}.txt"))[:, :dim]
    shuffle = None
    if 11 <= index <= 20:
        shuffle = _load(f"shuffle_data_{index}_D{dim}.txt").astype(int)
        shuffle = shuffle.ravel()[:dim] - 1
    elif index >= 29:
        shuffle = _load(f"shuffle_data_{index}_D{dim}.txt").astype(int)
        shuffle = shuffle.ravel()[:10 * dim].reshape(10, dim) - 1
    if index <= 20:
        return shifts[0], matrices[0], shuffle
    return shifts, matrices, shuffle


# -- building blocks -------------------------------------------------

class _Work:
    """The C code's shared work arrays ``y`` and ``z``, a row per point."""

    def __init__(self, n, dim):
        self.y = np.zeros((n, dim))
        self.z = np.zeros((n, dim))


def _sr(w, x, nx, shift, matrix, rate, s_flag, r_flag):
    """sr_func: shift (if s_flag), scale by ``rate``, rotate (if r_flag);
    the result goes into ``z``. Shifting and rotating goes through ``y``."""
    if s_flag and r_flag:
        w.y[:, :nx] = (x - shift[:nx]) * rate
        w.z[:, :nx] = w.y[:, :nx] @ matrix.T
    elif s_flag:
        w.z[:, :nx] = (x - shift[:nx]) * rate
    elif r_flag:
        w.y[:, :nx] = x * rate
        w.z[:, :nx] = w.y[:, :nx] @ matrix.T
    else:
        w.z[:, :nx] = x * rate
    return w.z[:, :nx]


def _ellips(w, x, nx, shift, matrix, s, r):
    z = _sr(w, x, nx, shift, matrix, 1.0, s, r)
    return np.sum(10.0 ** (6.0 * np.arange(nx) / (nx - 1)) * z * z, axis=1)


def _bent_cigar(w, x, nx, shift, matrix, s, r):
    z = _sr(w, x, nx, shift, matrix, 1.0, s, r)
    return z[:, 0] ** 2 + 1e6 * np.sum(z[:, 1:] ** 2, axis=1)


def _discus(w, x, nx, shift, matrix, s, r):
    z = _sr(w, x, nx, shift, matrix, 1.0, s, r)
    return 1e6 * z[:, 0] ** 2 + np.sum(z[:, 1:] ** 2, axis=1)


def _zakharov(w, x, nx, shift, matrix, s, r):
    z = _sr(w, x, nx, shift, matrix, 1.0, s, r)
    sum2 = np.sum(0.5 * np.arange(1, nx + 1) * z, axis=1)
    return np.sum(z * z, axis=1) + sum2 ** 2 + sum2 ** 4


def _levy(w, x, nx, shift, matrix, s, r):
    z = _sr(w, x, nx, shift, matrix, 1.0, s, r)
    v = 1.0 + (z - 1.0) / 4.0  # best point at z = 1, not at the shift
    first = np.sin(np.pi * v[:, 0]) ** 2
    last = (v[:, -1] - 1) ** 2 * (1 + np.sin(2 * np.pi * v[:, -1]) ** 2)
    middle = (v[:, :-1] - 1) ** 2 * (1 + 10 * np.sin(np.pi * v[:, :-1] + 1) ** 2)
    return first + np.sum(middle, axis=1) + last


def _rosenbrock(w, x, nx, shift, matrix, s, r):
    z = _sr(w, x, nx, shift, matrix, 2.048 / 100.0, s, r)
    z += 1.0  # changes the shared z, as in the C code
    return np.sum(100.0 * (z[:, :-1] ** 2 - z[:, 1:]) ** 2
                  + (z[:, :-1] - 1.0) ** 2, axis=1)


def _schaffer_f7(w, x, nx, shift, matrix, s, r):
    _sr(w, x, nx, shift, matrix, 1.0, s, r)
    # as in the C code: reads y, not z. On its own (F6) y is the shifted,
    # unrotated point; inside a hybrid it is the first nx coordinates of
    # the shuffled point, not this component's own share.
    y = w.y[:, :nx]
    zi = np.sqrt(y[:, :-1] ** 2 + y[:, 1:] ** 2)
    w.z[:, :nx - 1] = zi
    total = np.sum(zi ** 0.5 + zi ** 0.5 * np.sin(50.0 * zi ** 0.2) ** 2,
                   axis=1)
    return total * total / (nx - 1) / (nx - 1)


def _ackley(w, x, nx, shift, matrix, s, r):
    z = _sr(w, x, nx, shift, matrix, 1.0, s, r)
    sum1 = -0.2 * np.sqrt(np.sum(z * z, axis=1) / nx)
    sum2 = np.sum(np.cos(2.0 * np.pi * z), axis=1) / nx
    return np.e - 20.0 * np.exp(sum1) - np.exp(sum2) + 20.0


def _weierstrass(w, x, nx, shift, matrix, s, r):
    z = _sr(w, x, nx, shift, matrix, 0.5 / 100.0, s, r)
    a, b = 0.5 ** np.arange(21), 3.0 ** np.arange(21)
    total = np.sum(a * np.cos(2.0 * np.pi * b * (z[:, :, None] + 0.5)),
                   axis=(1, 2))
    return total - nx * np.sum(a * np.cos(2.0 * np.pi * b * 0.5))


def _griewank(w, x, nx, shift, matrix, s, r):
    z = _sr(w, x, nx, shift, matrix, 600.0 / 100.0, s, r)
    prod = np.prod(np.cos(z / np.sqrt(1.0 + np.arange(nx))), axis=1)
    return 1.0 + np.sum(z * z, axis=1) / 4000.0 - prod


def _rastrigin(w, x, nx, shift, matrix, s, r):
    z = _sr(w, x, nx, shift, matrix, 5.12 / 100.0, s, r)
    return np.sum(z * z - 10.0 * np.cos(2.0 * np.pi * z) + 10.0, axis=1)


def _schwefel(w, x, nx, shift, matrix, s, r):
    z = _sr(w, x, nx, shift, matrix, 1000.0 / 100.0, s, r)
    z += 4.209687462275036e+002
    high, low = z > 500, z < -500
    fold = np.fmod(np.abs(z), 500)
    with np.errstate(invalid="ignore"):
        inside = z * np.sin(np.sqrt(np.abs(z)))
    above = (500.0 - fold) * np.sin(np.sqrt(500.0 - fold))
    below = (-500.0 + fold) * np.sin(np.sqrt(500.0 - fold))
    term = np.where(high, above, np.where(low, below, inside))
    penalty = np.where(high, ((z - 500.0) / 100) ** 2 / nx,
                       np.where(low, ((z + 500.0) / 100) ** 2 / nx, 0.0))
    return (np.sum(penalty - term, axis=1)
            + 4.189828872724338e+002 * nx)


def _katsuura(w, x, nx, shift, matrix, s, r):
    z = _sr(w, x, nx, shift, matrix, 5.0 / 100.0, s, r)
    powers = 2.0 ** np.arange(1, 33)
    t = powers * z[:, :, None]
    temp = np.sum(np.abs(t - np.floor(t + 0.5)) / powers, axis=2)
    f = np.prod((1.0 + np.arange(1, nx + 1) * temp)
                ** (10.0 / (1.0 * nx) ** 1.2), axis=1)
    scale = 10.0 / nx / nx
    return f * scale - scale


def _bi_rastrigin(w, x, nx, shift, matrix, s, r):
    mu0, d = 2.5, 1.0
    sv = 1.0 - 1.0 / (2.0 * (nx + 20.0) ** 0.5 - 8.2)
    mu1 = -((mu0 * mu0 - d) / sv) ** 0.5
    w.y[:, :nx] = (x - shift[:nx]) if s else x.copy()
    w.y[:, :nx] *= 10.0 / 100.0
    tmpx = 2 * w.y[:, :nx]
    # as in the C code: signs follow the shift, even inside a hybrid
    tmpx = np.where(shift[:nx] < 0.0, -tmpx, tmpx)
    w.z[:, :nx] = tmpx
    tmpx = tmpx + mu0
    tmp1 = np.sum((tmpx - mu0) ** 2, axis=1)
    tmp2 = np.sum((tmpx - mu1) ** 2, axis=1) * sv + d * nx
    if r:
        w.y[:, :nx] = w.z[:, :nx] @ matrix.T
        cosines = np.sum(np.cos(2.0 * np.pi * w.y[:, :nx]), axis=1)
    else:
        cosines = np.sum(np.cos(2.0 * np.pi * w.z[:, :nx]), axis=1)
    return np.where(tmp1 < tmp2, tmp1, tmp2) + 10.0 * (nx - cosines)


def _grie_rosen(w, x, nx, shift, matrix, s, r):
    z = _sr(w, x, nx, shift, matrix, 5.0 / 100.0, s, r)
    z += 1.0
    nxt = np.roll(z, -1, axis=1)  # the last coordinate wraps to the first
    temp = 100.0 * (z * z - nxt) ** 2 + (z - 1.0) ** 2
    return np.sum(temp * temp / 4000.0 - np.cos(temp) + 1.0, axis=1)


def _escaffer6(w, x, nx, shift, matrix, s, r):
    z = _sr(w, x, nx, shift, matrix, 1.0, s, r)
    sq = z * z + np.roll(z, -1, axis=1) ** 2
    return np.sum(0.5 + (np.sin(np.sqrt(sq)) ** 2 - 0.5)
                  / (1.0 + 0.001 * sq) ** 2, axis=1)


def _happycat(w, x, nx, shift, matrix, s, r):
    z = _sr(w, x, nx, shift, matrix, 5.0 / 100.0, s, r)
    z -= 1.0
    r2, sum_z = np.sum(z * z, axis=1), np.sum(z, axis=1)
    return np.abs(r2 - nx) ** (2 * 0.125) + (0.5 * r2 + sum_z) / nx + 0.5


def _hgbat(w, x, nx, shift, matrix, s, r):
    z = _sr(w, x, nx, shift, matrix, 5.0 / 100.0, s, r)
    z -= 1.0
    r2, sum_z = np.sum(z * z, axis=1), np.sum(z, axis=1)
    return (np.abs(r2 ** 2.0 - sum_z ** 2.0) ** (2 * 0.25)
            + (0.5 * r2 + sum_z) / nx + 0.5)


_BASIC = {
    "ellips": _ellips, "bent_cigar": _bent_cigar, "discus": _discus,
    "zakharov": _zakharov, "levy": _levy, "rosenbrock": _rosenbrock,
    "schaffer_f7": _schaffer_f7, "ackley": _ackley,
    "weierstrass": _weierstrass, "griewank": _griewank,
    "rastrigin": _rastrigin, "schwefel": _schwefel, "katsuura": _katsuura,
    "bi_rastrigin": _bi_rastrigin, "grie_rosen": _grie_rosen,
    "escaffer6": _escaffer6, "happycat": _happycat, "hgbat": _hgbat,
}

# F1-F10. F8 is "non-continuous Rastrigin", but in the C code the step
# changes values that are overwritten straight after, so it is Rastrigin.
_SINGLE = {1: "bent_cigar", 3: "zakharov", 4: "rosenbrock", 5: "rastrigin",
           6: "schaffer_f7", 7: "bi_rastrigin", 8: "rastrigin", 9: "levy",
           10: "schwefel"}

# F11-F20: share of the coordinates for each component, and components
_HYBRID = {
    11: ((0.2, 0.4, 0.4), ("zakharov", "rosenbrock", "rastrigin")),
    12: ((0.3, 0.3, 0.4), ("ellips", "schwefel", "bent_cigar")),
    13: ((0.3, 0.3, 0.4), ("bent_cigar", "rosenbrock", "bi_rastrigin")),
    14: ((0.2, 0.2, 0.2, 0.4),
         ("ellips", "ackley", "schaffer_f7", "rastrigin")),
    15: ((0.2, 0.2, 0.3, 0.3),
         ("bent_cigar", "hgbat", "rastrigin", "rosenbrock")),
    16: ((0.2, 0.2, 0.3, 0.3),
         ("escaffer6", "hgbat", "rosenbrock", "schwefel")),
    17: ((0.1, 0.2, 0.2, 0.2, 0.3),
         ("katsuura", "ackley", "grie_rosen", "schwefel", "rastrigin")),
    18: ((0.2,) * 5, ("ellips", "ackley", "rastrigin", "hgbat", "discus")),
    19: ((0.2,) * 5, ("bent_cigar", "rastrigin", "grie_rosen",
                      "weierstrass", "escaffer6")),
    20: ((0.1, 0.1, 0.2, 0.2, 0.2, 0.2),
         ("hgbat", "katsuura", "ackley", "rastrigin", "schwefel",
          "schaffer_f7")),
}

# F21-F30: (component, scale numerator, scale denominator, sigma, bias).
# An integer component is a hybrid function above.
_COMPOSITION = {
    21: [("rosenbrock", 1, 1, 10, 0), ("ellips", 10000, 1e10, 20, 100),
         ("rastrigin", 1, 1, 30, 200)],
    22: [("rastrigin", 1, 1, 10, 0), ("griewank", 1000, 100, 20, 100),
         ("schwefel", 1, 1, 30, 200)],
    23: [("rosenbrock", 1, 1, 10, 0), ("ackley", 1000, 100, 20, 100),
         ("schwefel", 1, 1, 30, 200), ("rastrigin", 1, 1, 40, 300)],
    24: [("ackley", 1000, 100, 10, 0), ("ellips", 10000, 1e10, 20, 100),
         ("griewank", 1000, 100, 30, 200), ("rastrigin", 1, 1, 40, 300)],
    25: [("rastrigin", 10000, 1e3, 10, 0), ("happycat", 1000, 1e3, 20, 100),
         ("ackley", 1000, 100, 30, 200), ("discus", 10000, 1e10, 40, 300),
         ("rosenbrock", 1, 1, 50, 400)],
    26: [("escaffer6", 10000, 2e7, 10, 0), ("schwefel", 1, 1, 20, 100),
         ("griewank", 1000, 100, 20, 200), ("rosenbrock", 1, 1, 30, 300),
         ("rastrigin", 10000, 1e3, 40, 400)],
    27: [("hgbat", 10000, 1000, 10, 0), ("rastrigin", 10000, 1e3, 20, 100),
         ("schwefel", 10000, 4e3, 30, 200),
         ("bent_cigar", 10000, 1e30, 40, 300),
         ("ellips", 10000, 1e10, 50, 400),
         ("escaffer6", 10000, 2e7, 60, 500)],
    28: [("ackley", 1000, 100, 10, 0), ("griewank", 1000, 100, 20, 100),
         ("discus", 10000, 1e10, 30, 200), ("rosenbrock", 1, 1, 40, 300),
         ("happycat", 1000, 1e3, 50, 400),
         ("escaffer6", 10000, 2e7, 60, 500)],
    29: [(15, 1, 1, 10, 0), (16, 1, 1, 30, 100), (17, 1, 1, 50, 200)],
    30: [(15, 1, 1, 10, 0), (18, 1, 1, 30, 100), (19, 1, 1, 50, 200)],
}


def _sizes(shares, nx):
    """Coordinates per component: shares rounded up, as in the C code,
    and the last component takes the rest."""
    sizes = [math.ceil(share * nx) for share in shares[:-1]]
    return sizes + [nx - sum(sizes)]


def _hybrid(w, x, nx, shift, matrix, shuffle, s, r, index):
    shares, names = _HYBRID[index]
    z = _sr(w, x, nx, shift, matrix, 1.0, s, r)
    w.y[:, :nx] = z[:, shuffle]
    total, start = 0.0, 0
    for size, name in zip(_sizes(shares, nx), names):
        total = total + _BASIC[name](w, w.y[:, start:start + size], size,
                                     shift, matrix, 0, 0)
        start += size
    return total


def _composition(w, x, nx, shifts, matrices, shuffles, index):
    table = _COMPOSITION[index]
    fits, weights = [], []
    for i, (part, num, den, sigma, bias) in enumerate(table):
        if isinstance(part, int):
            fit = _hybrid(w, x, nx, shifts[i], matrices[i], shuffles[i],
                          1, 1, part)
        else:
            fit = _BASIC[part](w, x, nx, shifts[i], matrices[i], 1, 1)
        if (num, den) != (1, 1):
            fit = num * fit / den
        fits.append(fit + bias)
        dist = np.sum((x - shifts[i]) ** 2, axis=1)
        with np.errstate(divide="ignore"):
            weight = ((1.0 / dist) ** 0.5
                      * np.exp(-dist / 2.0 / nx / float(sigma) ** 2.0))
        weights.append(np.where(dist != 0, weight, 1e99))
    weights = np.array(weights)
    none = weights.max(axis=0) == 0  # no component near: equal weights
    weights[:, none] = 1.0
    total, f = 0.0, 0.0
    for weight in weights:
        total = total + weight
    for weight, fit in zip(weights, fits):
        f = f + weight / total * fit
    return f


def evaluate(x, index):
    """Value of F``index`` at one point ``(dim,)`` or many ``(n, dim)``."""
    if index not in FUNCS:
        raise ValueError(f"no function F{index} (F2 was withdrawn)")
    x = np.asarray(x, dtype=float)
    single = x.ndim == 1
    x = np.atleast_2d(x)
    n, dim = x.shape
    shift, matrix, shuffle = _data(index, dim)
    w = _Work(n, dim)
    if index <= 10:
        f = _BASIC[_SINGLE[index]](w, x, dim, shift, matrix, 1, 1)
    elif index <= 20:
        f = _hybrid(w, x, dim, shift, matrix, shuffle, 1, 1, index)
    else:
        f = _composition(w, x, dim, shift, matrix, shuffle, index)
    f = f + 100.0 * index
    return f[0] if single else f


def get_problem(index, dim=10):
    """F``index`` with ``dim`` coordinates, as ``Problem``."""
    if dim not in DIMS:
        raise ValueError(f"dim must be one of {DIMS}")

    def func(x, _index=index):
        return evaluate(x, _index)

    limit = np.full(dim, LIMIT)
    return Problem(index, func, -limit, limit, 100.0 * index)
