"""Sound intensity search: a group search for the lowest value of a function.

Every agent makes a sound; the better the agent, the louder it is. The
intensity agent ``i`` hears from agent ``j`` falls with the square of
their distance,

    I_ij = P_j^kappa / (4 pi r_ij^2)

and every agent listens to the source it hears loudest. It moves towards
that source if the source is fitter and away from it otherwise, plus an
"ambient" term: the difference between a random agent and an echo (a
random current or past position). Only some coordinates of the move are
heard; the rest stay put. A move is kept only if it improves the agent.

``kappa`` grows during the run, so agents first hear mostly their
neighbours and later hear the best agents from far away. After a while
their hearing turns less exact: instead of always the loudest source, an
agent turns towards a source with a chance that grows with its loudness. The group can
start large and shrink, dropping its worst agents. At the end the best
agent refines its point alone. See README.
"""
from collections import namedtuple

import numpy as np

from sound_heuristic import config as cfg

Result = namedtuple("Result", "best_x best_fitness evaluations curve")
GAIN = 0.01  # share of the group's spread of values that counts as a gain
STUCK = 1e-12  # values closer than this (relative) count as all the same


def pairwise_sq_distances(population):
    """Squared distance between every pair of agents (exactly 0 for
    agents at the same point)."""
    diff = population[:, None, :] - population[None, :, :]
    return np.einsum("ijk,ijk->ij", diff, diff)


def sound_power(fitness):
    """Loudness of each agent, adding up to 1 (lower value is better).

    Falls in equal steps from best (loudest) to worst (silent); equal
    values sound equally loud. Only the order matters, not the values.
    """
    fitness = np.asarray(fitness, dtype=float)
    n = fitness.size
    if n == 1:
        return np.ones(1)
    ordered = np.sort(fitness)
    # place in the sorted list; tied agents share the middle of their places
    low = np.searchsorted(ordered, fitness, side="left")
    high = np.searchsorted(ordered, fitness, side="right") - 1
    power = (n - 1 - (low + high) / 2) / (n - 1)
    return power / power.sum()


def compute_intensity(population, fitness, kappa=1.0):
    """Row ``i``: how loud each agent sounds to agent ``i``.

    An agent does not hear itself or an agent at exactly its point.
    """
    sq_dist = pairwise_sq_distances(population)
    area = 4 * np.pi * sq_dist
    inv_area = np.divide(1.0, area, out=np.zeros_like(area), where=area > 0)
    # loudness belongs to the agent making the sound, so it scales columns
    return inv_area * sound_power(fitness)[None, :] ** kappa


class SuccessMemory:
    """Step sizes and hearing rates that recently led to improvements.

    Hearing rate: the chance each coordinate takes part in a move. Each
    agent draws its values near a random slot; after each iteration one
    slot takes the average of the values that worked (Tanabe & Fukunaga,
    2013, 2014). A slot whose successes all used one coordinate stays at 0
    (stored as NaN).
    """

    def __init__(self, size=cfg.MEMORY_SIZE, step=cfg.STEP_INIT,
                 hearing=cfg.HEARING_INIT):
        self.step = np.full(size, float(step))
        self.hearing = np.full(size, float(hearing))
        self.slot = 0  # the slot that will be replaced next

    def sample(self, n, rng):
        """Step sizes in (0, 1] and hearing rates in [0, 1] for n agents."""
        pick = rng.integers(0, self.step.size, n)
        step = np.empty(n)
        redo = np.ones(n, dtype=bool)
        while redo.any():  # draw again until every step size is positive
            step[redo] = (self.step[pick[redo]]
                          + 0.1 * rng.standard_cauchy(redo.sum()))
            redo = step <= 0
        step = np.minimum(step, 1.0)
        centre = self.hearing[pick]
        hearing = np.clip(centre + 0.1 * rng.standard_normal(n), 0, 1)
        hearing[np.isnan(centre)] = 0.0
        return step, hearing

    def update(self, step, hearing, gain):
        """Average the values that worked into the next slot, weighted
        by improvement ``gain``, leaning towards larger values."""
        if step.size == 0 or np.sum(gain) <= 0:
            return
        weight = gain / np.sum(gain)
        self.step[self.slot] = (np.sum(weight * step ** 2)
                                / np.sum(weight * step))
        if np.isnan(self.hearing[self.slot]) or np.max(hearing) == 0:
            self.hearing[self.slot] = np.nan
        else:
            self.hearing[self.slot] = (np.sum(weight * hearing ** 2)
                                       / np.sum(weight * hearing))
        self.slot = (self.slot + 1) % self.step.size


class SoundSearch:  # pylint: disable=too-many-instance-attributes
    """Sound intensity search inside lower and upper limits per coordinate."""

    # pylint: disable=too-many-arguments
    def __init__(self, fitness_function, lower, upper, *,
                 pop_size=cfg.POP_SIZE, kappa=cfg.KAPPA,
                 kappa_start=cfg.KAPPA_START, refine=cfg.REFINE,
                 archive=cfg.ARCHIVE, stall=cfg.STALL,
                 final_size=cfg.FINAL_SIZE, noisy_after=cfg.NOISY_AFTER,
                 focus=cfg.FOCUS, memory_size=cfg.MEMORY_SIZE,
                 minimisation=cfg.MINIMISATION, rng=None):
        """``fitness_function`` maps an ``(agents, coordinates)`` array to
        one value per agent. ``lower``/``upper``: one number or one per
        coordinate. ``kappa_start``/``kappa``: how much loudness counts at
        the start/end. ``refine``: share of evaluations for refinement.
        ``archive``: echoes kept, as a multiple of ``pop_size``.
        ``stall``: start the group again when its best value has not
        really improved for this share of all evaluations (0: never).
        ``final_size``: agents left when the group search ends; the group
        shrinks evenly from ``pop_size``, dropping its worst agents
        (None: no shrinking). ``noisy_after``: share of each group search
        after which agents no longer always turn to the loudest source but
        pick one at random, with chance proportional to its loudness to
        the power ``focus`` (1: never).
        """
        self.lower = np.atleast_1d(np.asarray(lower, dtype=float))
        self.upper = np.atleast_1d(np.asarray(upper, dtype=float))
        if self.lower.shape != self.upper.shape:
            raise ValueError("lower and upper must have the same shape")
        if np.any(self.lower >= self.upper):
            raise ValueError("every lower bound must be below its upper bound")
        if pop_size < 4:
            raise ValueError("pop_size must be at least 4")
        if not 0 <= refine < 1:
            raise ValueError("refine must be in [0, 1)")
        if not 0 <= stall <= 1:
            raise ValueError("stall must be in [0, 1]")
        if not 0 <= noisy_after <= 1:
            raise ValueError("noisy_after must be in [0, 1]")
        if focus <= 0:
            raise ValueError("focus must be positive")
        final_size = pop_size if final_size is None else final_size
        if not 4 <= final_size <= pop_size:
            raise ValueError("final_size must be in [4, pop_size]")
        self.fitness_function = fitness_function
        self.minimisation = minimisation
        self.pop_size = pop_size
        self.kappa = kappa
        self.kappa_start = kappa_start
        self.refine = refine
        self.archive = archive
        self.stall = stall
        self.final_size = final_size
        self.noisy_after = noisy_after
        self.focus = focus
        self.memory_size = memory_size
        self.rng = rng if rng is not None else np.random.default_rng()
        self.evaluations = 0
        self._history = []

    @property
    def dim(self):
        """Number of coordinates."""
        return self.lower.size

    def _evaluate(self, population):
        """Function values; negated when maximising, so lower is better."""
        self.evaluations += len(population)
        values = np.asarray(self.fitness_function(population), dtype=float)
        return values if self.minimisation else -values

    def _record(self, best_f):
        """Note the best value so far."""
        self._history.append((self.evaluations, best_f))

    def init_population(self, size=None):
        """``size`` agents (default ``pop_size``) placed at random within
        the limits."""
        size = self.pop_size if size is None else size
        return self.rng.uniform(self.lower, self.upper, (size, self.dim))

    def group_size(self, budget):
        """Planned number of agents once ``self.evaluations`` of the
        ``budget`` for the group search are used: falls in a straight line
        from ``pop_size`` to ``final_size``."""
        used = min(1.0, self.evaluations / budget)
        return int(round(self.pop_size
                         + (self.final_size - self.pop_size) * used))

    # -- sound phase -------------------------------------------------

    def loudest_source(self, population, fitness, kappa, noisy=False):
        """For each agent, the agent it hears loudest; or, if ``noisy``, an
        agent picked at random with chance proportional to how loud it
        sounds to the power ``focus``."""
        heard = compute_intensity(population, fitness, kappa)
        source = heard.argmax(axis=1)
        if not noisy:
            return source
        top = heard[np.arange(len(heard)), source][:, None]
        with np.errstate(invalid="ignore", divide="ignore"):
            weight = np.where(top > 0, heard / top, 0.0) ** self.focus
        total = weight.sum(axis=1)
        some = total > 0  # an agent that hears nothing keeps the argmax
        cumulative = np.cumsum(weight[some], axis=1) / total[some, None]
        draw = self.rng.random(some.sum())[:, None]
        source[some] = np.minimum((cumulative < draw).sum(axis=1),
                                  len(heard) - 1)
        return source

    @staticmethod
    def direction(fitness, source):
        """+1 (towards) if the agent heard is better, -1 (away) if not."""
        return np.where(fitness[source] < fitness, 1.0, -1.0)

    def compute_move(self, population, fitness, echoes, step, kappa,
                     noisy=False):
        """Each agent's move: towards (or away from) the agent it hears
        loudest (see ``loudest_source`` for ``noisy``), plus a random push,
        times its step size."""
        n = len(population)
        rng = self.rng
        source = self.loudest_source(population, fitness, kappa, noisy)
        direction = self.direction(fitness, source)
        towards = direction[:, None] * (population[source] - population)

        # random push: gap between another agent and another agent or an
        # echo (a place an agent recently left)
        agents = np.arange(n)
        first = rng.integers(0, n - 1, n)
        first += first >= agents
        pool = np.vstack([population, echoes])
        second = rng.integers(0, len(pool), n)
        clash = (second == agents) | (second == first)
        while clash.any():
            second[clash] = rng.integers(0, len(pool), clash.sum())
            clash = (second == agents) | (second == first)
        ambient = population[first] - pool[second]
        return step[:, None] * (towards + ambient)

    def hearing_mask(self, hearing):
        """Coordinates that change: each with chance ``hearing``, at least
        one."""
        n = hearing.size
        mask = self.rng.random((n, self.dim)) < hearing[:, None]
        mask[np.arange(n), self.rng.integers(0, self.dim, n)] = True
        return mask

    def fix_boundary(self, candidate, previous):
        """Put a coordinate that crossed a limit halfway between its old
        value and that limit."""
        repaired = np.where(candidate < self.lower,
                            (previous + self.lower) / 2, candidate)
        return np.where(candidate > self.upper,
                        (previous + self.upper) / 2, repaired)

    def sound_phase(self, budget, patience=None):
        """Group search from a fresh start until ``budget`` evaluations are
        used, or until it is stuck: every agent equally good, or no real
        gain in the best value for ``patience`` evaluations (a real gain
        is at least 1% of the spread of the group's values)."""
        start = self.evaluations
        population = self.init_population(self.group_size(budget))
        fitness = self._evaluate(population)
        memory = SuccessMemory(self.memory_size)
        echoes = np.empty((0, self.dim))
        self._record(fitness.min())
        best, last_gain = fitness.min(), self.evaluations

        while self.evaluations < budget:
            # loudness counts more and more as the phase goes on
            progress = (self.evaluations - start) / (budget - start)
            kappa = self.kappa_start + (self.kappa - self.kappa_start) * progress
            size = len(population)
            step, hearing = memory.sample(size, self.rng)
            noisy = progress >= self.noisy_after
            move = self.compute_move(population, fitness, echoes, step,
                                     kappa, noisy)
            candidate = np.where(self.hearing_mask(hearing),
                                 population + move, population)
            candidate = self.fix_boundary(candidate, population)

            # never go over the budget: points not evaluated are not kept
            count = min(size, budget - self.evaluations)
            candidate_fitness = np.full(size, np.inf)
            candidate_fitness[:count] = self._evaluate(candidate[:count])

            # keep improving moves; the place left behind becomes an echo
            improved = candidate_fitness < fitness
            memory.update(step[improved], hearing[improved],
                          fitness[improved] - candidate_fitness[improved])
            echoes = np.vstack([echoes, population[improved]])
            population[improved] = candidate[improved]
            fitness[improved] = candidate_fitness[improved]

            # the group shrinks: the worst agents leave
            size = self.group_size(budget)
            if size < len(population):
                keep = np.argsort(fitness, kind="stable")[:size]
                population, fitness = population[keep], fitness[keep]
            capacity = int(round(self.archive * len(population)))
            if len(echoes) > capacity:  # forget random echoes when full
                keep = self.rng.permutation(len(echoes))[:capacity]
                echoes = echoes[keep]
            self._record(fitness.min())

            if patience:
                # a real gain: at least GAIN of the spread of values
                spread = np.ptp(fitness)
                if best - fitness.min() > GAIN * spread:
                    best, last_gain = fitness.min(), self.evaluations
                if (self.evaluations - last_gain >= patience
                        or spread <= STUCK * abs(best)):
                    break
        return population, fitness

    # -- refinement --------------------------------------------------

    def refine_best(self, x, fx, sigma, budget):
        """Improve ``x`` alone until ``budget`` evaluations are used.

        Tries one random step at a time and keeps it if no worse. Steps
        grow when more than about 1 in 5 work and shrink otherwise, and
        stretch along the direction of recent successes. Method of Igel,
        Suttorp & Hansen (2006), the "(1+1)-CMA-ES".
        """
        n = self.dim
        damping = 1 + n / 2  # how slowly the step size reacts
        # target success rate, its running estimate, update weight
        target, success, smoothing = 2 / 11, 2 / 11, 1 / 12
        c_path = 2 / (n + 2)  # how fast the path forgets old steps
        c_cov = 2 / (n ** 2 + 6)  # how fast the step shape learns
        threshold = 0.44  # above this success rate, stop growing the path
        sigma_max = float(np.max(self.upper - self.lower))
        factor, path = np.eye(n), np.zeros(n)

        while self.evaluations < budget:
            z = factor @ self.rng.standard_normal(n)
            y = np.clip(x + sigma * z, self.lower, self.upper)
            fy = self._evaluate(y[None])[0]
            ok = fy <= fx and not np.array_equal(y, x)
            success = (1 - smoothing) * success + smoothing * ok
            sigma = min(sigma * np.exp((success - target)
                                       / (damping * (1 - target))),
                        sigma_max)
            if ok:
                x, fx = y, fy
                if success < threshold:
                    path = (1 - c_path) * path + np.sqrt(
                        c_path * (2 - c_path)) * z
                    alpha = 1 - c_cov
                else:
                    path = (1 - c_path) * path
                    alpha = 1 - c_cov + c_cov * c_path * (2 - c_path)
                factor = self._update_factor(factor, path, alpha, c_cov)
            self._record(fx)
        return x, fx

    @staticmethod
    def _update_factor(factor, path, alpha, c_cov):
        """Stretch the step shape along ``path``; reset if it breaks."""
        n = len(path)
        try:
            w = np.linalg.solve(factor, path)
        except np.linalg.LinAlgError:
            return np.eye(n)
        ww = w @ w
        if not (np.isfinite(ww) and ww > 1e-12):
            return factor
        updated = np.sqrt(alpha) * factor + (
            np.sqrt(alpha) / ww * (np.sqrt(1 + c_cov * ww / alpha) - 1)
            * np.outer(path, w))
        return updated if np.all(np.isfinite(updated)) else np.eye(n)

    # -- whole run ---------------------------------------------------

    def run(self, iterations=cfg.ITERATIONS, evaluations=None):
        """Run with ``pop_size * (iterations + 1)`` evaluations, or exactly
        ``evaluations`` if given.

        ``curve[t]`` is the best value after ``pop_size * (t + 2)``
        evaluations (the end of iteration ``t`` for a group that does not
        shrink).
        """
        if evaluations is not None:
            iterations = -(-evaluations // self.pop_size) - 1
        total = evaluations or self.pop_size * (iterations + 1)
        self.evaluations = 0
        self._history = []
        sound_budget = max(self.pop_size,
                           int(round(total * (1 - self.refine))))
        patience = int(self.stall * total)

        # the group starts again whenever it gets stuck; keep the best
        best_f = np.inf
        while self.evaluations < sound_budget:
            population, fitness = self.sound_phase(sound_budget, patience)
            best = fitness.argmin()
            if fitness[best] < best_f or best_f == np.inf:
                best_x, best_f = population[best].copy(), fitness[best]
                # first refinement step about as wide as that group's spread
                spread = float(np.sqrt(np.mean(population.var(axis=0))))
            if (sound_budget - self.evaluations
                    < 2 * self.group_size(sound_budget)):
                break  # too little left for a new start

        if self.evaluations < total:
            floor = 1e-8 * float(np.mean(self.upper - self.lower))
            best_x, best_f = self.refine_best(best_x, best_f,
                                              max(spread, floor), total)

        # best value so far at the end of each iteration
        used = np.array([e for e, _ in self._history])
        best_so_far = np.minimum.accumulate([f for _, f in self._history])
        checkpoints = self.pop_size * (np.arange(iterations) + 2)
        index = np.searchsorted(used, checkpoints, side="right") - 1
        curve = best_so_far[np.clip(index, 0, None)]

        sign = 1 if self.minimisation else -1
        return Result(best_x, sign * best_f, self.evaluations, sign * curve)


def sample_parameters(rng, size):
    """Random settings to try when tuning: kappa, refine, archive."""
    return np.column_stack([
        2 ** rng.uniform(0, 4, size),
        rng.uniform(0.1, 0.5, size),
        rng.uniform(0, 3, size),
    ])
