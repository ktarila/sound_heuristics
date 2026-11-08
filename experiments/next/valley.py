"""Valley Hopper: a new search, not a sound search (prototype).

Idea: judge a place by the bottom of its valley, not by where you landed.
Every new point first takes a few short downhill steps ("settles"), so
points are compared valley floor against valley floor. New points come
from hops: towards a nearby better point plus the gap between two other
points (gaps between valley floors are about whole valley spacings). A
settled newcomer competes with the nearest member of the group, so several
valleys stay alive. The group shrinks to ``final_size``; the last
``refine`` share of the budget polishes the best point as version 3 does.

Settings (environment):
  SETTLE  downhill steps per new point (default 2 x coordinates; 0: off)
  FLO, FHI  hop size range (default 0.4, 1.0)
  NEAR    1 (default): head for a better point picked with chance
          1 / distance^2; 0: any better point, equally likely
  CROWD   1 (default): newcomer competes with its nearest member;
          0: with its parent
  SIGMA0  first settling step, as a share of the range (default 0.02)
"""
import os
import sys

import numpy as np

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))
from sound_heuristic.solution import Result, SoundSearch  # noqa: E402

SETTLE = os.environ.get("SETTLE")  # None: 2 x coordinates
FLO = float(os.environ.get("FLO", "0.4"))
FHI = float(os.environ.get("FHI", "1.0"))
NEAR = int(os.environ.get("NEAR", "1"))
CROWD = int(os.environ.get("CROWD", "1"))
SIGMA0 = float(os.environ.get("SIGMA0", "0.02"))

GROW, SHRINK = 1.5, 1.5 ** -0.25  # step change on success / failure


class ValleyHopper(SoundSearch):
    """Settle, hop, keep apart, shrink, polish. Takes the same settings
    as SoundSearch and uses ``pop_size``, ``final_size`` and ``refine``."""

    def settle_steps(self):
        """Downhill steps per new point."""
        return 2 * self.dim if SETTLE is None else int(SETTLE)

    def settle(self, x, f, sigma, steps):
        """Take ``steps`` random steps from each row of ``x``, keeping a
        step when it goes downhill. Each point's step size grows after a
        kept step and shrinks otherwise. All points move together, one
        batch of values per step."""
        span = float(np.max(self.upper - self.lower))
        for _ in range(steps):
            y = x + sigma[:, None] * self.rng.standard_normal(x.shape)
            y = self.fix_boundary(y, x)
            fy = self._evaluate(y)
            ok = fy < f
            x = np.where(ok[:, None], y, x)
            f = np.where(ok, fy, f)
            sigma = np.clip(np.where(ok, sigma * GROW, sigma * SHRINK),
                            1e-12 * span, span)
        return x, f, sigma

    def hops(self, x, f):
        """One new point per member: towards a better member, plus the gap
        between two other members."""
        n = len(x)
        diff = x[:, None, :] - x[None, :, :]
        dist2 = np.einsum("ijk,ijk->ij", diff, diff)
        better = f[None, :] < f[:, None]
        if NEAR:
            weight = np.where(better, 1.0 / np.maximum(dist2, 1e-300), 0.0)
        else:
            weight = better.astype(float)
        total = weight.sum(axis=1)
        none = total == 0  # the best member heads nowhere
        weight[none, np.flatnonzero(none)] = 1.0
        cum = np.cumsum(weight / weight.sum(axis=1, keepdims=True), axis=1)
        target = np.minimum((cum < self.rng.random((n, 1))).sum(axis=1),
                            n - 1)

        # two other members, different from each other and from i
        i = np.arange(n)
        r1 = self.rng.integers(0, n - 1, n)
        r1 += r1 >= i
        lo, hi = np.minimum(i, r1), np.maximum(i, r1)
        r2 = self.rng.integers(0, n - 2, n)
        r2 += r2 >= lo
        r2 += r2 >= hi

        scale = self.rng.uniform(FLO, FHI, (n, 1))
        v = x + scale * (x[target] - x) + scale * (x[r1] - x[r2])
        return self.fix_boundary(v, x)

    def keep(self, x, f, sigma, parents, u, fu, su):
        """Each newcomer replaces the member nearest to it (or its parent)
        if it is better."""
        for j in range(len(u)):
            if CROWD:
                k = int(np.argmin(np.sum((x - u[j]) ** 2, axis=1)))
            else:
                k = int(parents[j])
            if fu[j] < f[k]:
                x[k], f[k], sigma[k] = u[j], fu[j], su[j]
        return x, f, sigma

    def run(self, iterations=1000, evaluations=None):
        """Run with exactly ``evaluations`` evaluations (or
        ``pop_size * (iterations + 1)``)."""
        if evaluations is not None:
            iterations = -(-evaluations // self.pop_size) - 1
        total = evaluations or self.pop_size * (iterations + 1)
        self.evaluations = 0
        self._history = []
        hop_budget = max(self.pop_size, int(round(total * (1 - self.refine))))
        steps = self.settle_steps()
        span = float(np.mean(self.upper - self.lower))

        # start: spread out, then settle
        x = self.init_population()
        f = self._evaluate(x)
        sigma = np.full(len(x), SIGMA0 * span)
        room = (hop_budget - self.evaluations) // max(1, len(x))
        x, f, sigma = self.settle(x, f, sigma, min(steps, max(0, room)))
        self._record(float(f.min()))

        while True:
            left = hop_budget - self.evaluations
            n_new = min(len(x), left // (1 + steps))
            if n_new < 1 or len(x) < 4:
                break
            pick = (np.arange(len(x)) if n_new == len(x)
                    else self.rng.choice(len(x), n_new, replace=False))
            v = self.hops(x, f)[pick]
            fv = self._evaluate(v)
            u, fu, su = self.settle(v, fv, sigma[pick].copy(), steps)
            x, f, sigma = self.keep(x, f, sigma, pick, u, fu, su)
            self._record(float(f.min()))

            # shrink evenly from pop_size to final_size, dropping the worst
            share = min(1.0, self.evaluations / hop_budget)
            size = int(round(self.pop_size
                             - (self.pop_size - self.final_size) * share))
            size = max(self.final_size, size)
            if size < len(x):
                order = np.argsort(f, kind="stable")[:size]
                x, f, sigma = x[order], f[order], sigma[order]

        best = int(np.argmin(f))
        best_x, best_f = x[best].copy(), float(f[best])
        if self.evaluations < total:
            spread = float(np.sqrt(np.mean(x.var(axis=0))))
            best_x, best_f = self.refine_best(
                best_x, best_f, max(spread, 1e-8 * span), total)

        used = np.array([e for e, _ in self._history])
        best_so_far = np.minimum.accumulate([v for _, v in self._history])
        checkpoints = self.pop_size * (np.arange(iterations) + 2)
        index = np.searchsorted(used, checkpoints, side="right") - 1
        curve = best_so_far[np.clip(index, 0, None)]
        sign = 1 if self.minimisation else -1
        return Result(best_x, sign * best_f, self.evaluations, sign * curve)
