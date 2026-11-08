"""Prototype: every iteration each agent picks a listening rule; rules that
gave bigger improvements get picked more (adaptive choice, Burke et al. 2013)."""
import sys
import numpy as np
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))
from sound_heuristic.solution import (SoundSearch, SuccessMemory, GAIN, STUCK,
                                      pairwise_sq_distances, sound_power)

# listening rules: kappa = factor * the usual rising kappa
RULES = (("loudest", 1.0), ("nearest", 0.0), ("far", 2.0))
P_MIN = 0.1    # every rule keeps at least this chance
LEARN = 0.1    # how fast the scores follow new results


class AgentHyper(SoundSearch):
    rules = RULES

    def _choose(self, n):
        k = len(self.rules)
        p = P_MIN + (1 - k * P_MIN) * self._score
        return self.rng.choice(k, size=n, p=p / p.sum())

    def compute_move(self, population, fitness, echoes, step, kappa):
        self._rule = self._choose(len(population))
        factor = np.array([r[1] for r in self.rules])[self._rule]
        self._kappa_agent = factor * kappa
        return super().compute_move(population, fitness, echoes, step, kappa)

    def loudest_source(self, population, fitness, kappa):
        sq = pairwise_sq_distances(population)
        area = 4 * np.pi * sq
        inv = np.divide(1.0, area, out=np.zeros_like(area), where=area > 0)
        power = sound_power(fitness)
        loud = power[None, :] ** self._kappa_agent[:, None]
        return (inv * loud).argmax(axis=1)

    def _credit(self, gain):
        """gain: improvement of each agent this iteration (0 if none)."""
        k = len(self.rules)
        mean = np.array([gain[self._rule == r].mean() if np.any(self._rule == r) else 0.0
                         for r in range(k)])
        self.usage += np.bincount(self._rule, minlength=k)
        if mean.sum() > 0:
            self._score = (1 - LEARN) * self._score + LEARN * mean / mean.sum()

    def sound_phase(self, budget, patience=None):
        start = self.evaluations
        population = self.init_population()
        fitness = self._evaluate(population)
        memory = SuccessMemory(self.memory_size)
        echoes = np.empty((0, self.dim))
        capacity = int(round(self.archive * self.pop_size))
        self._record(fitness.min())
        best, last_gain = fitness.min(), self.evaluations
        while self.evaluations < budget:
            progress = (self.evaluations - start) / (budget - start)
            kappa = self.kappa_start + (self.kappa - self.kappa_start) * progress
            step, hearing = memory.sample(self.pop_size, self.rng)
            move = self.compute_move(population, fitness, echoes, step, kappa)
            candidate = np.where(self.hearing_mask(hearing), population + move, population)
            candidate = self.fix_boundary(candidate, population)
            count = min(self.pop_size, budget - self.evaluations)
            candidate_fitness = np.full(self.pop_size, np.inf)
            candidate_fitness[:count] = self._evaluate(candidate[:count])
            improved = candidate_fitness < fitness
            gain = np.where(improved, fitness - candidate_fitness, 0.0)
            self._credit(gain)
            memory.update(step[improved], hearing[improved], gain[improved])
            echoes = np.vstack([echoes, population[improved]])
            if len(echoes) > capacity:
                echoes = echoes[self.rng.permutation(len(echoes))[:capacity]]
            population[improved] = candidate[improved]
            fitness[improved] = candidate_fitness[improved]
            self._record(fitness.min())
            if patience:
                spread = np.ptp(fitness)
                if best - fitness.min() > GAIN * spread:
                    best, last_gain = fitness.min(), self.evaluations
                if self.evaluations - last_gain >= patience or spread <= STUCK * abs(best):
                    break
        return population, fitness

    def run(self, iterations):
        k = len(self.rules)
        self._score = np.full(k, 1 / k)
        self.usage = np.zeros(k, dtype=int)
        return super().run(iterations)
