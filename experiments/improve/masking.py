"""Prototype: when the group shrinks, the agent that leaves is the one most
drowned out ("masked") by a fitter agent nearby, not simply the worst.

Masking of agent i: the loudest sound i hears from a fitter agent,
max_j P_j^kappa / (4 pi r_ij^2) over agents j better than i. An agent at
the same point as a fitter (or equal, earlier) agent is fully masked.
The best agent is never masked.

MASK_POOL (env): "all" - any agent can leave; "half" - only the worse half.
"""
import os
import sys
import numpy as np
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))
from sound_heuristic import solution
from sound_heuristic.solution import (SoundSearch, SuccessMemory, GAIN, STUCK,
                                      compute_intensity, pairwise_sq_distances)

POOL = os.environ.get("MASK_POOL", "all")


def masking(population, fitness, kappa):
    n = len(population)
    heard = compute_intensity(population, fitness, kappa)  # row i hears col j
    order = np.argsort(fitness, kind="stable")
    rank = np.empty(n, dtype=int)
    rank[order] = np.arange(n)
    fitter = rank[None, :] < rank[:, None]  # j ranks above i
    score = np.where(fitter, heard, 0.0).max(axis=1)
    same = (pairwise_sq_distances(population) == 0) & fitter
    score[same.any(axis=1)] = np.inf
    return score


class Masking(SoundSearch):

    def survivors(self, population, fitness, size, kappa):
        n = len(population)
        score = masking(population, fitness, kappa)
        if POOL == "half":
            order = np.argsort(fitness, kind="stable")
            score[order[: n // 2]] = -1.0  # better half stays
        leave = np.argsort(-score, kind="stable")[: n - size]
        keep = np.setdiff1d(np.arange(n), leave)
        return keep

    def sound_phase(self, budget, patience=None):
        start = self.evaluations
        population = self.init_population(self.group_size(budget))
        fitness = self._evaluate(population)
        memory = solution.SuccessMemory(self.memory_size)
        echoes = np.empty((0, self.dim))
        self._record(fitness.min())
        best, last_gain = fitness.min(), self.evaluations

        while self.evaluations < budget:
            progress = (self.evaluations - start) / (budget - start)
            kappa = self.kappa_start + (self.kappa - self.kappa_start) * progress
            size = len(population)
            step, hearing = memory.sample(size, self.rng)
            move = self.compute_move(population, fitness, echoes, step, kappa)
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
            population[improved] = candidate[improved]
            fitness[improved] = candidate_fitness[improved]

            size = self.group_size(budget)
            if size < len(population):
                keep = self.survivors(population, fitness, size, kappa)
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
