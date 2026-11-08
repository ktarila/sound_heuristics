"""Prototype: some agents hear widely, without changing what the group
learns. After WIDE_START of the budget, each iteration a share WIDE of the
agents (picked at random) hears at least WIDE_FLOOR of the coordinates.
Only the other agents' successes update the memory of step sizes and
hearing rates, so the learned hearing rate stays what suits the function.

WIDE (default 0.25), WIDE_FLOOR (0.8), WIDE_START (0.1), all env.
"""
import os
import sys
import numpy as np
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))
from sound_heuristic.solution import SoundSearch, SuccessMemory, GAIN, STUCK

WIDE = float(os.environ.get("WIDE", "0.25"))
WIDE_FLOOR = float(os.environ.get("WIDE_FLOOR", "0.8"))
WIDE_START = float(os.environ.get("WIDE_START", "0.1"))


class Wide(SoundSearch):

    def run(self, iterations=1000, evaluations=None):
        self._total = evaluations or self.pop_size * (iterations + 1)
        return super().run(iterations, evaluations)

    def sound_phase(self, budget, patience=None):
        start = self.evaluations
        population = self.init_population(self.group_size(budget))
        fitness = self._evaluate(population)
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
            if WIDE > 0 and self.evaluations >= WIDE_START * self._total:
                wide = self.rng.random(size) < WIDE
                heard = np.where(wide, np.maximum(hearing, WIDE_FLOOR),
                                 hearing)
            else:
                wide = np.zeros(size, dtype=bool)
                heard = hearing
            candidate = np.where(self.hearing_mask(heard),
                                 population + move, population)
            candidate = self.fix_boundary(candidate, population)
            count = min(size, budget - self.evaluations)
            candidate_fitness = np.full(size, np.inf)
            candidate_fitness[:count] = self._evaluate(candidate[:count])
            improved = candidate_fitness < fitness
            learn = improved & ~wide  # wide hearers do not teach the memory
            memory.update(step[learn], hearing[learn],
                          fitness[learn] - candidate_fitness[learn])
            echoes = np.vstack([echoes, population[improved]])
            population[improved] = candidate[improved]
            fitness[improved] = candidate_fitness[improved]

            size = self.group_size(budget)
            if size < len(population):
                keep = np.argsort(fitness, kind="stable")[:size]
                population, fitness = population[keep], fitness[keep]
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
