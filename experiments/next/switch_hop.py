"""Version 3 early, then the all-coordinates hop (prototype).

Each group search moves by sound (version 3, unchanged) until SWITCH of it
has passed. After that every agent hops instead: towards a better agent
plus the gap between two others, all coordinates at once (Valley Hopper's
hop, ``valley.ValleyHopper.hops``). As before, a move is kept only if it
beats the agent's own place. Restarts, shrinking and the endgame are
version 3's.

Settings (environment):
  SWITCH  share of each group search moved by sound (default 0.1;
          1: never hop, which is version 3 exactly)
  FLO, FHI, NEAR  as in valley.py
"""
import os
import sys

import numpy as np

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sound_heuristic.solution import (  # noqa: E402
    GAIN, STUCK, SoundSearch, SuccessMemory)
from valley import ValleyHopper  # noqa: E402

SWITCH = float(os.environ.get("SWITCH", "0.1"))


class SwitchHop(SoundSearch):
    """Version 3 with the hop after SWITCH of each group search."""

    hops = ValleyHopper.hops

    def sound_phase(self, budget, patience=None):
        """As SoundSearch.sound_phase, but moves are hops once SWITCH of
        the group search has passed."""
        start = self.evaluations
        population = self.init_population(self.group_size(budget))
        fitness = self._evaluate(population)
        memory = SuccessMemory(self.memory_size)
        echoes = np.empty((0, self.dim))
        self._record(fitness.min())
        best, last_gain = fitness.min(), self.evaluations

        while self.evaluations < budget:
            progress = (self.evaluations - start) / (budget - start)
            size = len(population)
            hop = progress >= SWITCH
            if hop:
                candidate = self.hops(population, fitness)
            else:
                kappa = (self.kappa_start
                         + (self.kappa - self.kappa_start) * progress)
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
            if not hop:
                memory.update(step[improved], hearing[improved],
                              fitness[improved] - candidate_fitness[improved])
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
