"""Sound intensity heuristic search.

Each agent emits sound with a power proportional to its (normalised)
fitness. The intensity agent ``i`` hears from agent ``j`` is

    I_ij = P_j / (4 pi r_ij^2)

Every agent picks the source it hears loudest and moves towards it if
that source is fitter, away from it otherwise. Added to that are
momentum, a random exploration term that decays over the run, and a pull
towards the global best that grows over the run. All random coefficients
are drawn per dimension. A move is kept only if it improves the agent
(greedy acceptance), so the population never loses its best solution.
"""
from collections import namedtuple

import numpy as np

from sound_heuristic import config as cfg

Result = namedtuple("Result", "best_x best_fitness evaluations curve")


def pairwise_sq_distances(population):
    """Squared Euclidean distance between every pair of agents.

    Uses explicit differences (not the |a|^2 + |b|^2 - 2ab identity) so
    identical agents get exactly 0.
    """
    diff = population[:, None, :] - population[None, :, :]
    return np.einsum("ijk,ijk->ij", diff, diff)


def normalised_power(fitness):
    """Map fitness (minimisation) to power in [0, 1], summing to 1.

    Best agent gets the largest power, worst agent gets 0. If all agents
    are equally fit, every agent gets the same power.
    """
    best, worst = np.min(fitness), np.max(fitness)
    spread = worst - best
    if spread <= 0 or not np.isfinite(spread):
        small_p = np.ones_like(fitness, dtype=float)
    else:
        small_p = (worst - fitness) / spread
    return small_p / np.sum(small_p)


def compute_intensity(population, fitness):
    """Intensity matrix: row i holds what agent i hears from every j."""
    sq_dist = pairwise_sq_distances(population)
    area = 4 * np.pi * sq_dist
    inv_area = np.divide(1.0, area, out=np.zeros_like(area), where=area > 0)
    # power belongs to the source j -> scale columns
    return inv_area * normalised_power(fitness)[None, :]


class SoundSearch:  # pylint: disable=too-many-instance-attributes
    """Sound intensity optimiser over a box-constrained domain."""

    # pylint: disable=too-many-arguments
    def __init__(self, fitness_function, lower, upper, *,
                 pop_size=cfg.POP_SIZE, rho=cfg.RHO, momentum=cfg.MOMENTUM,
                 exploration=cfg.EXPLORATION,
                 exploration_prob=cfg.EXPLORATION_PROB, pull=cfg.PULL,
                 minimisation=cfg.MINIMISATION, rng=None):
        """``fitness_function`` must accept a population ``(n, dim)``
        and return ``(n,)`` values. ``lower``/``upper`` are scalars or
        per-dimension arrays.
        """
        self.lower = np.atleast_1d(np.asarray(lower, dtype=float))
        self.upper = np.atleast_1d(np.asarray(upper, dtype=float))
        if self.lower.shape != self.upper.shape:
            raise ValueError("lower and upper must have the same shape")
        if np.any(self.lower >= self.upper):
            raise ValueError("every lower bound must be below its upper bound")
        self.fitness_function = fitness_function
        self.minimisation = minimisation
        self.pop_size = pop_size
        self.rho = rho
        self.momentum = momentum
        self.exploration = exploration
        self.exploration_prob = exploration_prob
        self.pull = pull
        self.rng = rng if rng is not None else np.random.default_rng()
        self.evaluations = 0

    @property
    def dim(self):
        """Problem dimension."""
        return self.lower.size

    def _evaluate(self, population):
        """Evaluate a population, internally always as minimisation."""
        self.evaluations += len(population)
        values = np.asarray(self.fitness_function(population), dtype=float)
        return values if self.minimisation else -values

    def init_population(self):
        """Uniform random population inside the bounds."""
        return self.rng.uniform(self.lower, self.upper,
                                (self.pop_size, self.dim))

    def compute_step(self, population, fitness):
        """Move towards the loudest source if it is fitter, else away.

        The random factor is drawn per dimension, so moves are not
        restricted to the line between agent and neighbour.
        """
        intensity = compute_intensity(population, fitness)
        neighbours = intensity.argmax(axis=1)
        direction = np.where(fitness[neighbours] < fitness, 1.0, -1.0)
        scale = self.rho / 100 * (1 + self.rng.random(population.shape))
        return direction[:, None] * scale * (
            population[neighbours] - population)

    def compute_pull(self, population, best_x, progress):
        """Attraction to the global best, growing with progress^2."""
        return (self.pull * progress ** 2
                * self.rng.random(population.shape) * (best_x - population))

    def compute_exploration(self, progress):
        """Gaussian kick for a random subset of agents, decaying to 0."""
        sigma = self.exploration * (1 - progress) ** 3 * (
            self.upper - self.lower)
        kick = self.rng.normal(0, 1, (self.pop_size, self.dim)) * sigma
        chosen = self.rng.random((self.pop_size, 1)) < self.exploration_prob
        return kick * chosen

    def fix_boundary(self, candidate, previous, velocity):
        """Repair out-of-bounds coordinates of ``candidate``.

        A coordinate that crossed a bound is placed halfway between its
        previous value and that bound (as in L-SHADE), which keeps the
        agent's progress instead of resetting it. Momentum is cleared for
        repaired coordinates.
        """
        below = candidate < self.lower
        above = candidate > self.upper
        repaired = np.where(below, (previous + self.lower) / 2, candidate)
        repaired = np.where(above, (previous + self.upper) / 2, repaired)
        velocity = np.where(below | above, 0.0, velocity)
        return repaired, velocity

    def run(self, iterations=cfg.ITERATIONS):
        """Run the search and return a ``Result``.

        ``evaluations`` counts fitness evaluations (pop_size per
        iteration, plus the initial population). ``curve`` holds the best
        fitness after each iteration.
        """
        self.evaluations = 0
        population = self.init_population()
        velocity = np.zeros_like(population)
        fitness = self._evaluate(population)
        best_idx = np.argmin(fitness)
        best_x, best_f = population[best_idx].copy(), fitness[best_idx]
        curve = np.empty(iterations)

        for iteration in range(iterations):
            progress = iteration / iterations
            step = self.compute_step(population, fitness)
            step += self.compute_exploration(progress)
            step += self.compute_pull(population, best_x, progress)
            carry = self.rng.uniform(0, self.momentum, (self.pop_size, 1))
            new_velocity = carry * velocity + step
            candidate, new_velocity = self.fix_boundary(
                population + new_velocity, population, new_velocity)
            candidate_fitness = self._evaluate(candidate)

            # greedy acceptance: keep a move only if it improves the agent
            improved = candidate_fitness < fitness
            population[improved] = candidate[improved]
            fitness[improved] = candidate_fitness[improved]
            velocity = np.where(improved[:, None], new_velocity, 0.0)

            best_idx = np.argmin(fitness)
            if fitness[best_idx] < best_f:
                best_x, best_f = population[best_idx].copy(), fitness[best_idx]
            curve[iteration] = best_f

        sign = 1 if self.minimisation else -1
        return Result(best_x, sign * best_f, self.evaluations, sign * curve)


def sample_parameters(rng, size):
    """Random candidates for tuning.

    Columns: rho, momentum, exploration, pull.
    """
    return np.column_stack([
        rng.uniform(5, 95, size),
        rng.uniform(0, 1, size),
        10 ** rng.uniform(-2, -0.5, size),
        10 ** rng.uniform(-0.5, 0.7, size),
    ])
