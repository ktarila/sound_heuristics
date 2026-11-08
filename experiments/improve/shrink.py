"""Prototype: the group shrinks during the run, dropping its worst agents
(Tanabe & Fukunaga 2014, as in L-SHADE and jSO). Size falls in a straight line
from START x pop_size to MIN agents over the sound part of the budget."""
import os
import sys
import numpy as np
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))
from sound_heuristic.solution import SoundSearch, SuccessMemory, GAIN, STUCK, Result

START = float(os.environ.get("SHRINK_START", "1.0"))  # first size, times pop_size
MIN = 4


class Shrink(SoundSearch):

    def _size(self):
        share = min(1.0, self.evaluations / self._sound_budget)
        return max(MIN, int(round(self._first + (MIN - self._first) * share)))

    def init_population(self):
        self.pop_size = self._size()
        return super().init_population()

    def sound_phase(self, budget, patience=None):
        start = self.evaluations
        population = self.init_population()
        fitness = self._evaluate(population)
        memory = SuccessMemory(self.memory_size)
        echoes = np.empty((0, self.dim))
        self._record(fitness.min())
        best, last_gain = fitness.min(), self.evaluations
        while self.evaluations < budget:
            progress = (self.evaluations - start) / (budget - start)
            kappa = self.kappa_start + (self.kappa - self.kappa_start) * progress
            n = len(population)
            self.pop_size = n
            step, hearing = memory.sample(n, self.rng)
            move = self.compute_move(population, fitness, echoes, step, kappa)
            candidate = np.where(self.hearing_mask(hearing), population + move, population)
            candidate = self.fix_boundary(candidate, population)
            count = min(n, budget - self.evaluations)
            candidate_fitness = np.full(n, np.inf)
            candidate_fitness[:count] = self._evaluate(candidate[:count])
            improved = candidate_fitness < fitness
            memory.update(step[improved], hearing[improved],
                          fitness[improved] - candidate_fitness[improved])
            echoes = np.vstack([echoes, population[improved]])
            population[improved] = candidate[improved]
            fitness[improved] = candidate_fitness[improved]
            # drop the worst agents down to the planned size
            size = self._size()
            if size < n:
                keep = np.argsort(fitness, kind="stable")[:size]
                population, fitness = population[keep], fitness[keep]
            capacity = int(round(self.archive * len(population)))
            if len(echoes) > capacity:
                echoes = echoes[self.rng.permutation(len(echoes))[:capacity]]
            self._record(fitness.min())
            if patience:
                spread = np.ptp(fitness)
                if best - fitness.min() > GAIN * spread:
                    best, last_gain = fitness.min(), self.evaluations
                if self.evaluations - last_gain >= patience or spread <= STUCK * abs(best):
                    break
        return population, fitness

    def run(self, iterations):
        base = self.pop_size
        total = base * (iterations + 1)
        self._first = int(round(START * base))
        self._sound_budget = max(base, int(round(total * (1 - self.refine))))
        self.evaluations, self._history = 0, []
        patience = int(self.stall * total)
        best_f = np.inf
        while self.evaluations < self._sound_budget:
            population, fitness = self.sound_phase(self._sound_budget, patience)
            i = fitness.argmin()
            if fitness[i] < best_f:
                best_x, best_f = population[i].copy(), fitness[i]
                spread = float(np.sqrt(np.mean(population.var(axis=0))))
            if self._sound_budget - self.evaluations < 2 * self._size():
                break
        self.pop_size = base
        if self.evaluations < total:
            floor = 1e-8 * float(np.mean(self.upper - self.lower))
            best_x, best_f = self.refine_best(best_x, best_f, max(spread, floor), total)
        used = np.array([e for e, _ in self._history])
        best_so_far = np.minimum.accumulate([f for _, f in self._history])
        checkpoints = base * (np.arange(iterations) + 2)
        index = np.searchsorted(used, checkpoints, side="right") - 1
        curve = best_so_far[np.clip(index, 0, None)]
        return Result(best_x, best_f, self.evaluations, curve)
