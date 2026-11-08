"""Prototype: agents hear like people.

Each agent has an age (in iterations) and its own ears.
  EARS  (env, default 0): spread of ear quality. Agent i's kappa is
        kappa(t) * exp(EARS * N(0,1)), fixed for its life: a good ear tells
        a good source from a merely close one.
  AGING (env, default 0): hearing loss with age. The sound i hears fades by
        exp(-AGING * age_i / LIFE * r / typical distance), so elders hear
        only nearby agents.
  KIDS  (env, default 0): share of the lifespan an agent is a stubborn kid:
        it ignores the others and moves only by the ambient push.
  LIFE  (env, default 100): lifespan in iterations. At the end of it the
        agent is replaced by its child at the same spot: age 0, new ears.
  CHILDHOOD (env, default 0): share of each group search at the start
        when nobody listens; everyone moves only by the ambient push.
Starting ages are spread evenly over the lifespan, so the group always has
kids, adults and elders.
"""
import os
import sys
import numpy as np
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))
from sound_heuristic import solution
from sound_heuristic.solution import (SoundSearch, GAIN, STUCK, sound_power,
                                      pairwise_sq_distances)

EARS = float(os.environ.get("EARS", "0"))
AGING = float(os.environ.get("AGING", "0"))
KIDS = float(os.environ.get("KIDS", "0"))
LIFE = int(os.environ.get("LIFE", "100"))
# share of each group search at the start when nobody listens (childhood)
CHILDHOOD = float(os.environ.get("CHILDHOOD", "0"))


class Humans(SoundSearch):

    def _ears(self, n):
        if EARS == 0:
            return np.ones(n)
        return np.exp(EARS * self.rng.standard_normal(n))

    def _traits(self, n):
        return self.rng.integers(0, LIFE, n), self._ears(n)

    def loudest_source(self, population, fitness, kappa):
        if EARS == 0 and AGING == 0:
            return super().loudest_source(population, fitness, kappa)
        sq = pairwise_sq_distances(population)
        power = sound_power(fitness)
        with np.errstate(divide="ignore", invalid="ignore"):
            log_power = np.log(power)  # the worst agent is silent: -inf
            score = ((kappa * self._ear)[:, None] * log_power[None, :]
                     - np.log(4 * np.pi * sq))
            if AGING:
                r = np.sqrt(sq)
                scale = r[r > 0].mean() if np.any(r > 0) else 1.0
                loss = AGING * self._age / LIFE
                score = score - loss[:, None] * r / scale
        score[(sq == 0) | np.isnan(score)] = -np.inf
        return score.argmax(axis=1)

    def compute_move(self, population, fitness, echoes, step, kappa):
        n = len(population)
        rng = self.rng
        source = self.loudest_source(population, fitness, kappa)
        direction = self.direction(fitness, source)
        towards = direction[:, None] * (population[source] - population)
        if KIDS:
            towards[self._age < KIDS * LIFE] = 0.0  # stubborn kids
        if CHILDHOOD and self._progress < CHILDHOOD:
            towards[:] = 0.0  # the whole group is still young
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

    def sound_phase(self, budget, patience=None):
        start = self.evaluations
        population = self.init_population(self.group_size(budget))
        fitness = self._evaluate(population)
        self._age, self._ear = self._traits(len(population))
        memory = solution.SuccessMemory(self.memory_size)
        echoes = np.empty((0, self.dim))
        self._record(fitness.min())
        best, last_gain = fitness.min(), self.evaluations

        while self.evaluations < budget:
            progress = (self.evaluations - start) / (budget - start)
            kappa = self.kappa_start + (self.kappa - self.kappa_start) * progress
            self._progress = progress
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

            # a year passes; agents at the end of their life are replaced by
            # their child at the same spot
            self._age += 1
            born = self._age >= LIFE
            if born.any():
                self._age[born] = 0
                self._ear[born] = self._ears(born.sum())

            size = self.group_size(budget)
            if size < len(population):
                keep = np.argsort(fitness, kind="stable")[:size]
                population, fitness = population[keep], fitness[keep]
                self._age, self._ear = self._age[keep], self._ear[keep]
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
