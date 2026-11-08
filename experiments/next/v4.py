"""Prototypes for version 4.

Version 3 spends its last 10% on a (1+1)-CMA-ES: one point that tries one
random step at a time. Here the endgame is a population CMA-ES
(the (mu/mu_w, lambda)-CMA-ES of Hansen, as in his tutorial "The CMA
Evolution Strategy"), started from the best point the sound search found,
with step size from that group's spread. When it converges and budget is
left, it starts again from the best point with a larger population and step
(the IPOP restart rule of Auger and Hansen, 2005).

Env settings:
  ENDGAME   "cma" (default) or "one" (version 3's (1+1)-CMA-ES)
  IPOP      1 (default): restarts double the population; 0: same population
  GROW      factor on the step size at each restart (default 2)
  FINISH    share of the budget for a CMA-ES finish after every group search
            except the last (default 0: off)
"""
import os
import sys

import numpy as np

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))
from sound_heuristic.solution import SoundSearch  # noqa: E402

ENDGAME = os.environ.get("ENDGAME", "cma")
IPOP = int(os.environ.get("IPOP", "1"))
GROW = float(os.environ.get("GROW", "2"))
FINISH = float(os.environ.get("FINISH", "0"))


def cma_es(evaluate, x0, f0, sigma, lower, upper, budget, rng, lam=None):
    """One (mu/mu_w, lambda)-CMA-ES run from ``x0``. ``evaluate`` maps (n, d)
    points to values and counts them. Stops when out of ``budget``
    evaluations or converged. Returns best point, its value, evaluations
    used."""
    n = len(x0)
    lam = lam or 4 + int(3 * np.log(n))
    mu = lam // 2
    w = np.log(mu + 0.5) - np.log(np.arange(1, mu + 1))
    w /= w.sum()
    mueff = 1.0 / np.sum(w ** 2)
    cc = (4 + mueff / n) / (n + 4 + 2 * mueff / n)
    cs = (mueff + 2) / (n + mueff + 5)
    c1 = 2 / ((n + 1.3) ** 2 + mueff)
    cmu = min(1 - c1, 2 * (mueff - 2 + 1 / mueff) / ((n + 2) ** 2 + mueff))
    damps = 1 + 2 * max(0.0, np.sqrt((mueff - 1) / (n + 1)) - 1) + cs
    chi_n = np.sqrt(n) * (1 - 1 / (4 * n) + 1 / (21 * n ** 2))
    span = float(np.max(upper - lower))

    mean = x0.copy()
    pc, ps = np.zeros(n), np.zeros(n)
    basis, scale = np.eye(n), np.ones(n)
    cov = np.eye(n)
    best_x, best_f = x0.copy(), f0
    used, gen, last_eigen = 0, 0, 0
    history = []
    while used + lam <= budget:
        z = rng.standard_normal((lam, n))
        steps = (z * scale) @ basis.T
        x = np.clip(mean + sigma * steps, lower, upper)
        f = evaluate(x)
        used += lam
        gen += 1
        order = np.argsort(f)
        if f[order[0]] < best_f:
            best_x, best_f = x[order[0]].copy(), float(f[order[0]])
        history.append(float(f[order[0]]))

        old = mean
        chosen = x[order[:mu]]
        mean = w @ chosen
        y = (chosen - old) / sigma
        y_mean = w @ y
        inv_sqrt = basis @ np.diag(1 / scale) @ basis.T
        ps = (1 - cs) * ps + np.sqrt(cs * (2 - cs) * mueff) * inv_sqrt @ y_mean
        hsig = (np.linalg.norm(ps) / np.sqrt(1 - (1 - cs) ** (2 * gen)) / chi_n
                < 1.4 + 2 / (n + 1))
        pc = (1 - cc) * pc + hsig * np.sqrt(cc * (2 - cc) * mueff) * y_mean
        cov = ((1 - c1 - cmu) * cov
               + c1 * (np.outer(pc, pc) + (1 - hsig) * cc * (2 - cc) * cov)
               + cmu * (y.T * w) @ y)
        sigma *= np.exp((cs / damps) * (np.linalg.norm(ps) / chi_n - 1))
        sigma = min(sigma, span)

        if used - last_eigen > lam / (c1 + cmu) / n / 10:
            last_eigen = used
            cov = np.triu(cov) + np.triu(cov, 1).T
            values, basis = np.linalg.eigh(cov)
            if not np.all(np.isfinite(values)) or values.min() <= 0:
                break
            scale = np.sqrt(values)
            if scale.max() / scale.min() > 1e7:
                break
        # converged: steps far below the range, or no change in the best
        if sigma * scale.max() < 1e-12 * span:
            break
        if (len(history) > 10 + int(30 * n / lam)
                and np.ptp(history[-(10 + int(30 * n / lam)):])
                <= 1e-12 * max(1.0, abs(best_f))):
            break
    return best_x, best_f, used


class V4(SoundSearch):
    """Version 3 with a population CMA-ES endgame (and optional finishes)."""

    def refine_best(self, x, fx, sigma, budget):
        if ENDGAME == "one":
            return super().refine_best(x, fx, sigma, budget)
        lam, step, start_sigma = None, 1.0, sigma
        # stop once the next (doubled) group no longer fits in what is left;
        # otherwise the loop can spin without using any evaluations
        while (budget - self.evaluations
               >= (lam or 4 + int(3 * np.log(self.dim)))):
            x_new, f_new, _ = cma_es(
                self._evaluate, x, fx, start_sigma * step, self.lower,
                self.upper, budget - self.evaluations, self.rng, lam)
            if f_new < fx:
                x, fx = x_new, f_new
            self._record(fx)
            # start again from the best point, wider and with more agents
            lam = (lam or 4 + int(3 * np.log(self.dim))) * (2 if IPOP else 1)
            step *= GROW
        return x, fx

    def sound_phase(self, budget, patience=None):
        population, fitness = super().sound_phase(budget, patience)
        left = budget - self.evaluations
        if FINISH > 0 and left > 2 * self.group_size(budget):
            # finish this group's basin quickly, then let the run start again
            best = int(fitness.argmin())
            spread = float(np.sqrt(np.mean(population.var(axis=0))))
            spread = max(spread, 1e-8 * float(np.mean(self.upper - self.lower)))
            cap = min(int(FINISH * self.total), left - 2 * self.group_size(budget))
            x, f, _ = cma_es(self._evaluate, population[best].copy(),
                             float(fitness[best]), spread, self.lower,
                             self.upper, cap, self.rng)
            population[best], fitness[best] = x, f
            self._record(float(fitness.min()))
        return population, fitness

    def run(self, iterations=1000, evaluations=None):
        self.total = evaluations or self.pop_size * (iterations + 1)
        return super().run(iterations, evaluations)
