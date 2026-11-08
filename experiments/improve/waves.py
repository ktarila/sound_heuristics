"""Prototypes of two more sound properties.

Superposition: sounds add up. After the switch to less exact hearing
(noisy_after), an agent moves along the sum of all the sounds it hears:
towards each fitter agent and away from each worse one, each weighted by
how loud it sounds to the power SUPER_FOCUS (env, default 2). Before the
switch it turns to the loudest, as in version 3.

Doppler: a moving source sounds different, so a listener can tell where it
is heading. Each agent remembers its last successful move; a listener aims
at where the source is heading, source + DOPPLER * (its last move)
(env DOPPLER, default 0.5).
"""
import os
import sys
import numpy as np
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))
from sound_heuristic.solution import (SoundSearch, SuccessMemory, GAIN, STUCK,
                                      compute_intensity)

SUPER_FOCUS = float(os.environ.get("SUPER_FOCUS", "2"))
DOPPLER = float(os.environ.get("DOPPLER", "0.5"))


def ambient(search, population, echoes):
    """Random push: another agent minus another agent or an echo."""
    n = len(population)
    rng = search.rng
    agents = np.arange(n)
    first = rng.integers(0, n - 1, n)
    first += first >= agents
    pool = np.vstack([population, echoes])
    second = rng.integers(0, len(pool), n)
    clash = (second == agents) | (second == first)
    while clash.any():
        second[clash] = rng.integers(0, len(pool), clash.sum())
        clash = (second == agents) | (second == first)
    return population[first] - pool[second]


class Superposition(SoundSearch):

    def compute_move(self, population, fitness, echoes, step, kappa,
                     noisy=False):
        if not noisy:
            return super().compute_move(population, fitness, echoes, step,
                                        kappa, noisy)
        heard = compute_intensity(population, fitness, kappa)
        top = heard.max(axis=1, keepdims=True)
        with np.errstate(invalid="ignore", divide="ignore"):
            weight = np.where(top > 0, heard / top, 0.0) ** SUPER_FOCUS
        total = weight.sum(axis=1, keepdims=True)
        weight = np.divide(weight, total, out=np.zeros_like(weight),
                           where=total > 0)
        sign = np.where(fitness[None, :] < fitness[:, None], 1.0, -1.0)
        diff = population[None, :, :] - population[:, None, :]
        towards = np.einsum("ij,ijk->ik", weight * sign, diff)
        return step[:, None] * (towards + ambient(self, population, echoes))


class Doppler(SoundSearch):

    def compute_move(self, population, fitness, echoes, step, kappa,
                     noisy=False):
        source = self.loudest_source(population, fitness, kappa, noisy)
        direction = self.direction(fitness, source)
        heading = population[source] + DOPPLER * self._velocity[source]
        towards = direction[:, None] * (heading - population)
        return step[:, None] * (towards + ambient(self, population, echoes))

    def sound_phase(self, budget, patience=None):
        start = self.evaluations
        population = self.init_population(self.group_size(budget))
        fitness = self._evaluate(population)
        self._velocity = np.zeros_like(population)
        memory = SuccessMemory(self.memory_size)
        echoes = np.empty((0, self.dim))
        self._record(fitness.min())
        best, last_gain = fitness.min(), self.evaluations

        while self.evaluations < budget:
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
            count = min(size, budget - self.evaluations)
            candidate_fitness = np.full(size, np.inf)
            candidate_fitness[:count] = self._evaluate(candidate[:count])
            improved = candidate_fitness < fitness
            memory.update(step[improved], hearing[improved],
                          fitness[improved] - candidate_fitness[improved])
            echoes = np.vstack([echoes, population[improved]])
            self._velocity[improved] = (candidate[improved]
                                        - population[improved])
            population[improved] = candidate[improved]
            fitness[improved] = candidate_fitness[improved]

            size = self.group_size(budget)
            if size < len(population):
                keep = np.argsort(fitness, kind="stable")[:size]
                population, fitness = population[keep], fitness[keep]
                self._velocity = self._velocity[keep]
            capacity = int(round(self.archive * len(population)))
            if len(echoes) > capacity:
                keep = self.rng.permutation(len(echoes))[:capacity]
                echoes = echoes[keep]
            self._record(fitness.min())

            if patience:
                spread = np.ptp(fitness)
                if best - fitness.min() > GAIN * spread:
                    best, last_gain = fitness.min(), self.evaluations
                if (self.evaluations - last_gain >= patience
                        or spread <= STUCK * abs(best)):
                    break
        return population, fitness
