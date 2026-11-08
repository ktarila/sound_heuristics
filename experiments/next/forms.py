"""New instances of the CEC 2022 function forms, for designing version 4.

The competition's own instances (its shift, rotation and shuffle files) are
the test set and are not used here. Each instance takes the formula of one
CEC 2022 function and draws its own random shift (within -80..80), rotation
and coordinate order, so a method tuned on these has not seen the test set's
data. The formulas come from sound_heuristic/cec2022.py.

make(index, seed, dim=10) -> func mapping (n, dim) points to errors.
"""
import sys

import numpy as np

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))
from sound_heuristic import cec2022 as c  # noqa: E402

BASIC_NAME = {1: "zakharov", 2: "rosenbrock", 4: "rastrigin", 5: "levy"}


def _rotation(rng, dim):
    q, r = np.linalg.qr(rng.normal(size=(dim, dim)))
    return q * np.sign(np.diag(r))


def make(index, seed, dim=10):
    rng = np.random.default_rng(90_000 + 1000 * index + seed)
    if index <= 5:
        shift = rng.uniform(-80, 80, dim)
        matrix = _rotation(rng, dim)

        def func(x):
            x = np.atleast_2d(np.asarray(x, float))
            if index == 3:  # shifted, not turned, as in the official code
                return c._schaffer_f7(x - shift)
            f, rate = c._BASIC[BASIC_NAME[index]]
            return f(c._shift_rotate(x, shift, matrix, rate))
        return func
    if index <= 8:
        parts = c._HYBRID[index]
        shift = rng.uniform(-80, 80, dim)
        matrix = _rotation(rng, dim)
        order = rng.permutation(dim)
        sizes = [int(np.ceil(share * dim)) for share, _ in parts[:-1]]
        sizes.append(dim - sum(sizes))

        def func(x):
            x = np.atleast_2d(np.asarray(x, float))
            y = c._shift_rotate(x, shift, matrix, 1.0)[:, order]
            total, start = 0.0, 0
            for size, (_, name) in zip(sizes, parts):
                if name == "schaffer_f7":
                    total = total + c._schaffer_f7(y[:, :size])
                else:
                    f, rate = c._BASIC[name]
                    total = total + f(y[:, start:start + size] * rate)
                start += size
            return total
        return func
    parts = c._COMPOSITION[index]
    shifts = rng.uniform(-80, 80, (len(parts), dim))
    matrices = [_rotation(rng, dim) for _ in parts]

    def func(x):
        x = np.atleast_2d(np.asarray(x, float))
        values, weights = [], []
        for k, (name, factor, rotated, sigma, bias) in enumerate(parts):
            f, rate = c._BASIC[name]
            z = c._shift_rotate(x, shifts[k], matrices[k], rate, rotated)
            values.append(f(z) * factor + bias)
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
    return func


if __name__ == "__main__":
    # check: error 0 at the instance's best point for the basic and hybrid
    # forms (the composition's best point is its first shift)
    for i in range(1, 13):
        f = make(i, 0)
        rng = np.random.default_rng(90_000 + 1000 * i)
        shift = rng.uniform(-80, 80, (len(c._COMPOSITION[i]), 10))[0] if i >= 9 \
            else rng.uniform(-80, 80, 10)
        print(i, float(f(shift)[0]))
