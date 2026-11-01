"""Statistical tests for comparing optimisers. Needs only NumPy.

- ``rank_sum``: on one function, are one algorithm's results better than
  another's more often than chance would give? (Wilcoxon rank-sum, also
  called Mann-Whitney U.)
- ``friedman``: across many functions, do the algorithms' average ranks
  differ more than chance would give?
- ``holm``: compare one algorithm with each of the others, adjusting
  the p-values because several comparisons are made at once.

Pass errors (how far above the best possible value a result is); lower
is better. Errors up to ``TOLERANCE`` count as 0, as in the CEC
competitions (some entries write a solved run as exactly 1e-8).
"""
import math
from collections import namedtuple

import numpy as np

TOLERANCE = 1e-8

RankSum = namedtuple("RankSum", "p_value winner")
Friedman = namedtuple("Friedman", "average_ranks statistic p_value")
Holm = namedtuple("Holm", "name z p_value adjusted_p_value")


def _ranks(values):
    """Ranks from 1 (smallest); tied values share the average rank."""
    values = np.asarray(values, dtype=float)
    ordered = np.sort(values)
    low = np.searchsorted(ordered, values, side="left")
    high = np.searchsorted(ordered, values, side="right")
    return (low + high + 1) / 2


def snap(values):
    """Errors up to TOLERANCE become 0."""
    values = np.asarray(values, dtype=float)
    return np.where(np.abs(values) <= TOLERANCE, 0.0, values)


def normal_sf(z):
    """Chance that a standard normal value is above ``z``."""
    return 0.5 * math.erfc(z / math.sqrt(2))


def chi2_sf(x, df):
    """Chance that a chi-squared value with ``df`` degrees of freedom is
    above ``x`` (upper regularised incomplete gamma function)."""
    if x <= 0:
        return 1.0
    a, x = df / 2.0, x / 2.0
    log_front = a * math.log(x) - x - math.lgamma(a)
    if x < a + 1:  # series for the lower part, then 1 minus it
        term = total = 1.0 / a
        n = a
        for _ in range(10_000):
            n += 1
            term *= x / n
            total += term
            if abs(term) < abs(total) * 1e-15:
                break
        return max(0.0, 1.0 - math.exp(log_front) * total)
    # continued fraction for the upper part (modified Lentz)
    tiny = 1e-300
    b = x + 1 - a
    c, d = 1 / tiny, 1 / b
    h = d
    for i in range(1, 10_000):
        an = -i * (i - a)
        b += 2
        d = an * d + b
        d = tiny if abs(d) < tiny else d
        c = b + an / c
        c = tiny if abs(c) < tiny else c
        d = 1 / d
        h *= d * c
        if abs(d * c - 1) < 1e-15:
            break
    return math.exp(log_front) * h


def rank_sum(a, b, alpha=0.05):
    """Two-sided Wilcoxon rank-sum test between samples ``a`` and ``b``.

    Uses the normal approximation with tie and continuity corrections,
    which is accurate for samples of about 10 or more. ``winner`` is
    "a" or "b" if that sample is significantly lower at level ``alpha``,
    otherwise "=".
    """
    a, b = snap(a), snap(b)
    n1, n2 = a.size, b.size
    ranks = _ranks(np.concatenate([a, b]))
    u = ranks[:n1].sum() - n1 * (n1 + 1) / 2
    mean = n1 * n2 / 2
    n = n1 + n2
    _, counts = np.unique(np.concatenate([a, b]), return_counts=True)
    tie = np.sum(counts ** 3 - counts) / (n * (n - 1))
    sd = math.sqrt(n1 * n2 / 12 * ((n + 1) - tie))
    if sd == 0:
        return RankSum(1.0, "=")
    z = (abs(u - mean) - 0.5) / sd
    p = min(1.0, 2 * normal_sf(max(z, 0.0)))
    winner = "="
    if p < alpha:
        winner = "a" if u < mean else "b"
    return RankSum(p, winner)


def friedman(table):
    """Friedman test on ``table[problem, algorithm]`` (lower is better).

    Returns the average rank of each algorithm (1 = best), the test
    statistic, and its p-value (with the usual correction for ties).
    """
    table = snap(table)
    n_problems, k = table.shape
    ranks = np.array([_ranks(row) for row in table])
    average = ranks.mean(axis=0)
    statistic = 12 * n_problems / (k * (k + 1)) * (
        np.sum(average ** 2) - k * (k + 1) ** 2 / 4)
    ties = sum(np.sum(c ** 3 - c) for c in
               (np.unique(row, return_counts=True)[1] for row in table))
    correction = 1 - ties / (n_problems * k * (k * k - 1))
    if correction <= 0:
        return Friedman(average, 0.0, 1.0)
    statistic /= correction
    return Friedman(average, statistic, chi2_sf(statistic, k - 1))


def holm(average_ranks, names, n_problems, control):
    """Compare algorithm ``control`` with each other one (Holm's method).

    Uses the average ranks from ``friedman``. Returns one ``Holm`` row per
    other algorithm, most different first. A positive ``z`` means the
    other algorithm ranks worse than the control.
    """
    average_ranks = np.asarray(average_ranks, dtype=float)
    k = len(names)
    c = names.index(control)
    se = math.sqrt(k * (k + 1) / (6 * n_problems))
    rows = []
    for i, name in enumerate(names):
        if i != c:
            z = (average_ranks[i] - average_ranks[c]) / se
            rows.append((name, z, min(1.0, 2 * normal_sf(abs(z)))))
    rows.sort(key=lambda row: row[2])
    m, running, out = len(rows), 0.0, []
    for j, (name, z, p) in enumerate(rows):
        running = max(running, min(1.0, (m - j) * p))
        out.append(Holm(name, z, p, running))
    return out
