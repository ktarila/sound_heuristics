"""Test functions f1 - f23 (Yao et al. 1999, as used by Mirjalili).

Each takes one point ``(dim,)`` and returns a number, or many points
``(n, dim)`` and returns ``n`` numbers.
"""
from collections import namedtuple

import numpy as np

# Random numbers for f7's noise; fix them with ``seed_noise`` to repeat
# an experiment exactly.
_NOISE_RNG = np.random.default_rng()


def seed_noise(seed):
    """Fix the random noise of f7 so results can be repeated."""
    global _NOISE_RNG  # pylint: disable=global-statement
    _NOISE_RNG = np.random.default_rng(seed)


def _check_dim(x, dim, name):
    if x.shape[-1] != dim:
        raise ValueError(f"Dimension of {name} must be equal to {dim}")


def f1(x):
    """Sphere: sum x_i^2. Domain [-100, 100]^n, min 0."""
    x = np.asarray(x)
    return np.sum(x ** 2, axis=-1)


def f2(x):
    """Schwefel 2.22: sum |x_i| + prod |x_i|."""
    x = np.abs(np.asarray(x))
    return np.sum(x, axis=-1) + np.prod(x, axis=-1)


def f3(x):
    """Schwefel 1.2: sum_i (sum_{j<=i} x_j)^2."""
    x = np.asarray(x)
    return np.sum(np.cumsum(x, axis=-1) ** 2, axis=-1)


def f4(x):
    """Schwefel 2.21: max |x_i|."""
    return np.max(np.abs(np.asarray(x)), axis=-1)


def f5(x):
    """Rosenbrock: sum 100 (x_{i+1} - x_i^2)^2 + (x_i - 1)^2."""
    x = np.asarray(x)
    head, tail = x[..., :-1], x[..., 1:]
    return np.sum(100 * (tail - head ** 2) ** 2 + (head - 1) ** 2, axis=-1)


def f6(x):
    """Step function as in Mirjalili's code: sum (x_i + 0.5)^2.

    Yao et al. round down, sum floor(x_i + 0.5)^2; say which version
    you use when comparing with published results.
    """
    x = np.asarray(x)
    return np.sum((x + 0.5) ** 2, axis=-1)


def f7(x):
    """Quartic with noise: sum i * x_i^4 + a random number in [0, 1),
    new on every call."""
    x = np.asarray(x)
    ind = np.arange(1, x.shape[-1] + 1)
    return np.sum(ind * x ** 4, axis=-1) + _NOISE_RNG.random(x.shape[:-1])


def f8(x):
    """Schwefel 2.26: sum -x_i sin(sqrt|x_i|). Min -418.9829 n."""
    x = np.asarray(x)
    return np.sum(-x * np.sin(np.sqrt(np.abs(x))), axis=-1)


def f9(x):
    """Rastrigin: sum x_i^2 - 10 cos(2 pi x_i) + 10."""
    x = np.asarray(x)
    return np.sum(x ** 2 - 10 * np.cos(2 * np.pi * x) + 10, axis=-1)


def f10(x):
    """Ackley."""
    x = np.asarray(x)
    term_one = -20 * np.exp(-0.2 * np.sqrt(np.mean(x ** 2, axis=-1)))
    term_two = np.exp(np.mean(np.cos(2 * np.pi * x), axis=-1))
    return term_one - term_two + 20 + np.e


def f11(x):
    """Griewank: sum x_i^2 / 4000 - prod cos(x_i / sqrt(i)) + 1."""
    x = np.asarray(x)
    ind = np.arange(1, x.shape[-1] + 1)
    return (np.sum(x ** 2, axis=-1) / 4000
            - np.prod(np.cos(x / np.sqrt(ind)), axis=-1) + 1)


def u_sum(x, a, k, m):
    """Penalty term for f12 and f13: sum_i u(x_i, a, k, m) where

       u = k (x - a)^m    if x > a
           0              if -a <= x <= a
           k (-x - a)^m   if x < -a
    """
    x = np.asarray(x)
    penalty = np.where(x > a, k * (x - a) ** m, 0.0)
    penalty = np.where(x < -a, k * (-x - a) ** m, penalty)
    return np.sum(penalty, axis=-1)


def f12(x):
    """Penalised function 1 (best point: every x_i = -1)."""
    x = np.asarray(x)
    n = x.shape[-1]
    y = 1 + (x + 1) / 4
    first = 10 * np.sin(np.pi * y[..., 0]) ** 2
    middle = np.sum((y[..., :-1] - 1) ** 2
                    * (1 + 10 * np.sin(np.pi * y[..., 1:]) ** 2), axis=-1)
    last = (y[..., -1] - 1) ** 2
    return (np.pi / n) * (first + middle + last) + u_sum(x, 10, 100, 4)


def f13(x):
    """Penalised function 2 (best point: every x_i = 1)."""
    x = np.asarray(x)
    first = np.sin(3 * np.pi * x[..., 0]) ** 2
    middle = np.sum((x[..., :-1] - 1) ** 2
                    * (1 + np.sin(3 * np.pi * x[..., 1:]) ** 2), axis=-1)
    last = (x[..., -1] - 1) ** 2 * (1 + np.sin(2 * np.pi * x[..., -1]) ** 2)
    return 0.1 * (first + middle + last) + u_sum(x, 5, 100, 4)


_F14_A = np.array([
    [-32.0, -16, 0, 16, 32] * 5,
    [v for v in (-32.0, -16, 0, 16, 32) for _ in range(5)],
])


def f14(x):
    """Shekel's foxholes, dim = 2."""
    x = np.asarray(x)
    _check_dim(x, 2, "f14")
    # distance to each of the 25 holes, per coordinate
    bottom = np.sum((x[..., :, None] - _F14_A) ** 6, axis=-2)
    j = np.arange(1, _F14_A.shape[1] + 1)
    return 1 / (1 / 500 + np.sum(1 / (j + bottom), axis=-1))


_F15_A = np.array([0.1957, 0.1947, 0.1735, 0.16, 0.0844, 0.0627,
                   0.0456, 0.0342, 0.0323, 0.0235, 0.0246])
_F15_B = 1 / np.array([0.25, 0.5, 1, 2, 4, 6, 8, 10, 12, 14, 16])


def f15(x):
    """Kowalik, dim = 4."""
    x = np.asarray(x)
    _check_dim(x, 4, "f15")
    b = _F15_B
    x0, x1, x2, x3 = (x[..., i, None] for i in range(4))
    model = x0 * (b ** 2 + b * x1) / (b ** 2 + b * x2 + x3)
    return np.sum((_F15_A - model) ** 2, axis=-1)


def f16(x):
    """Six-hump camel back, dim = 2."""
    x = np.asarray(x)
    _check_dim(x, 2, "f16")
    x0, x1 = x[..., 0], x[..., 1]
    return (4 * x0 ** 2 - 2.1 * x0 ** 4 + x0 ** 6 / 3
            + x0 * x1 - 4 * x1 ** 2 + 4 * x1 ** 4)


def f17(x):
    """Branin, dim = 2. Domain x1 in [-5, 10], x2 in [0, 15]."""
    x = np.asarray(x)
    _check_dim(x, 2, "f17")
    x0, x1 = x[..., 0], x[..., 1]
    first = (x1 - 5.1 / (4 * np.pi ** 2) * x0 ** 2 + 5 / np.pi * x0 - 6) ** 2
    second = 10 * (1 - 1 / (8 * np.pi)) * np.cos(x0)
    return first + second + 10


def f18(x):
    """Goldstein-Price, dim = 2."""
    x = np.asarray(x)
    _check_dim(x, 2, "f18")
    x0, x1 = x[..., 0], x[..., 1]
    first = 1 + (x0 + x1 + 1) ** 2 * (
        19 - 14 * x0 + 3 * x0 ** 2 - 14 * x1 + 6 * x0 * x1 + 3 * x1 ** 2)
    second = 30 + (2 * x0 - 3 * x1) ** 2 * (
        18 - 32 * x0 + 12 * x0 ** 2 + 48 * x1 - 36 * x0 * x1 + 27 * x1 ** 2)
    return first * second


_HARTMAN_C = np.array([1, 1.2, 3, 3.2])
_F19_A = np.array([[3, 10, 30], [0.1, 10, 35], [3, 10, 30], [0.1, 10, 35]])
_F19_P = np.array([[0.3689, 0.117, 0.2673],
                   [0.4699, 0.4387, 0.747],
                   [0.1091, 0.8732, 0.5547],
                   [0.03815, 0.5743, 0.8828]])
_F20_A = np.array([[10, 3, 17, 3.5, 1.7, 8],
                   [0.05, 10, 17, 0.1, 8, 14],
                   [3, 3.5, 1.7, 10, 17, 8],
                   [17, 8, 0.05, 10, 0.1, 14]])
_F20_P = np.array([[0.1312, 0.1696, 0.5569, 0.0124, 0.8283, 0.5886],
                   [0.2329, 0.4135, 0.8307, 0.3736, 0.1004, 0.9991],
                   [0.2348, 0.1415, 0.3522, 0.2883, 0.3047, 0.6650],
                   [0.4047, 0.8828, 0.8732, 0.5743, 0.1091, 0.0381]])


def _hartman(x, array_a, array_p):
    inner = np.sum(array_a * (x[..., None, :] - array_p) ** 2, axis=-1)
    return -np.sum(_HARTMAN_C * np.exp(-inner), axis=-1)


def f19(x):
    """Hartman 3, dim = 3."""
    x = np.asarray(x)
    _check_dim(x, 3, "f19")
    return _hartman(x, _F19_A, _F19_P)


def f20(x):
    """Hartman 6, dim = 6."""
    x = np.asarray(x)
    _check_dim(x, 6, "f20")
    return _hartman(x, _F20_A, _F20_P)


_SHEKEL_A = np.array([[4, 4, 4, 4],
                      [1, 1, 1, 1],
                      [8, 8, 8, 8],
                      [6, 6, 6, 6],
                      [3, 7, 3, 7],
                      [2, 9, 2, 9],
                      [5, 5, 3, 3],
                      [8, 1, 8, 1],
                      [6, 2, 6, 2],
                      [7, 3.6, 7, 3.6]])
_SHEKEL_C = np.array([0.1, 0.2, 0.2, 0.4, 0.4, 0.6, 0.3, 0.7, 0.5, 0.5])


def f21_23(x, last):
    """Shekel family; f21, f22, f23 use the first 5, 7, 10 terms."""
    x = np.asarray(x)
    sq_dist = np.sum((x[..., None, :] - _SHEKEL_A[:last]) ** 2, axis=-1)
    return -np.sum(1 / (sq_dist + _SHEKEL_C[:last]), axis=-1)


def f21(x):
    """Shekel 5, dim = 4."""
    _check_dim(np.asarray(x), 4, "f21")
    return f21_23(x, 5)


def f22(x):
    """Shekel 7, dim = 4."""
    _check_dim(np.asarray(x), 4, "f22")
    return f21_23(x, 7)


def f23(x):
    """Shekel 10, dim = 4."""
    _check_dim(np.asarray(x), 4, "f23")
    return f21_23(x, 10)


Problem = namedtuple("Problem", "index func lower upper optimum")


# index: (lower limit, upper limit, coordinates, function, best value)
# limits are one number for all coordinates or one per coordinate
_BENCHMARKS = {
    1: (-100, 100, 30, f1, 0.0),
    2: (-10, 10, 30, f2, 0.0),
    3: (-100, 100, 30, f3, 0.0),
    4: (-100, 100, 30, f4, 0.0),
    5: (-30, 30, 30, f5, 0.0),
    6: (-100, 100, 30, f6, 0.0),
    7: (-1.28, 1.28, 30, f7, 0.0),
    8: (-500, 500, 30, f8, -418.9829 * 30),
    9: (-5.12, 5.12, 30, f9, 0.0),
    10: (-32, 32, 30, f10, 0.0),
    11: (-600, 600, 30, f11, 0.0),
    12: (-50, 50, 30, f12, 0.0),
    13: (-50, 50, 30, f13, 0.0),
    14: (-65.536, 65.536, 2, f14, 0.998004),
    15: (-5, 5, 4, f15, 0.0003075),
    16: (-5, 5, 2, f16, -1.0316285),
    17: ([-5, 0], [10, 15], 2, f17, 0.397887),
    18: (-2, 2, 2, f18, 3.0),
    19: (0, 1, 3, f19, -3.86278),
    20: (0, 1, 6, f20, -3.32237),
    21: (0, 10, 4, f21, -10.1532),
    22: (0, 10, 4, f22, -10.4029),
    23: (0, 10, 4, f23, -10.5364),
}


def get_problem(index):
    """Test function ``index`` (1 - 23), with one limit per coordinate."""
    if index not in _BENCHMARKS:
        raise ValueError("Function index should be between 1 and 23")
    lower, upper, dim, func, optimum = _BENCHMARKS[index]
    lower = np.broadcast_to(np.asarray(lower, dtype=float), (dim,)).copy()
    upper = np.broadcast_to(np.asarray(upper, dtype=float), (dim,)).copy()
    return Problem(index, func, lower, upper, optimum)
