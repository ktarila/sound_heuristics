"""Prototype: each new group (restart) picks its type by score, with tabu (Burke et al. 2003)."""
import sys
import numpy as np
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))
from sound_heuristic.solution import SoundSearch, Result

# (name, agents as a multiple of pop_size, fixed kappa or None for the usual rise)
TYPES = (("loudest", 1, None), ("nearest", 1, 0.0), ("big", 4, None))
TENURE = 1


class EpisodeHyper(SoundSearch):
    types = TYPES

    def loudest_source(self, population, fitness, kappa):
        if getattr(self, "_kappa_fixed", None) is not None:
            kappa = self._kappa_fixed
        return super().loudest_source(population, fitness, kappa)

    def run(self, iterations):
        base = self.pop_size
        total = base * (iterations + 1)
        self.evaluations, self._history = 0, []
        sound_budget = max(base, int(round(total * (1 - self.refine))))
        patience = int(self.stall * total)
        score = {t[0]: 0 for t in self.types}
        tabu = {t[0]: 0 for t in self.types}
        self.usage = {t[0]: 0 for t in self.types}
        best_f, best_x, spread = np.inf, None, None
        first = True
        while self.evaluations < sound_budget:
            if first:
                kind = self.types[0]
                first = False
            else:
                free = [t for t in self.types if tabu[t[0]] == 0] or list(self.types)
                top = max(score[t[0]] for t in free)
                choices = [t for t in free if score[t[0]] == top]
                kind = choices[self.rng.integers(len(choices))]
            name, mult, kfix = kind
            self.usage[name] += 1
            self.pop_size = base * mult
            self._kappa_fixed = kfix
            if sound_budget - self.evaluations < 2 * self.pop_size:
                self.pop_size = base
                self._kappa_fixed = None
                break
            before = best_f
            population, fitness = self.sound_phase(sound_budget, patience)
            i = fitness.argmin()
            if fitness[i] < best_f:
                best_x, best_f = population[i].copy(), fitness[i]
                spread = float(np.sqrt(np.mean(population.var(axis=0))))
            for t in tabu:
                tabu[t] = max(0, tabu[t] - 1)
            if best_f < before:
                score[name] = min(score[name] + 1, 3)
            else:
                score[name] = max(score[name] - 1, -3)
                tabu[name] = TENURE
        self.pop_size = base
        self._kappa_fixed = None
        floor = 1e-8 * float(np.mean(self.upper - self.lower))
        if self.evaluations < total:
            best_x, best_f = self.refine_best(best_x, best_f, max(spread, floor), total)
        used = np.array([e for e, _ in self._history])
        best_so_far = np.minimum.accumulate([f for _, f in self._history])
        checkpoints = base * (np.arange(iterations) + 2)
        index = np.searchsorted(used, checkpoints, side="right") - 1
        curve = best_so_far[np.clip(index, 0, None)]
        return Result(best_x, best_f, self.evaluations, curve)
