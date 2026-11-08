"""Prototype: echolocation, judging a move before making it.

Version 3 remembers where agents used to be (echoes) but not how good those
places were, and every move is a blind try. Here every point ever evaluated
(the most recent STORE_PER_DIM x coordinates of them, plus the whole group)
is remembered together with its value. Each agent drafts ECHO_K moves, all
from its own hearing (own step size and hearing rate, each with its own
random source and push). Each draft is rated from the 3 nearest remembered
points (their values, weighted by 1 / distance), and only the draft with the
best rating is evaluated. No extra evaluations are spent.

Env: ECHO_K (drafts per agent, default 3; 1 reproduces version 3 exactly),
     ECHO_START (share of the group search before drafting starts, 0.1),
     STORE_PER_DIM (default 50), NEAR (points used to rate, default 3).
After a run, ``search.success`` holds (progress, share of moves that
improved) per iteration.
"""
import os
import sys
import numpy as np
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))
from sound_heuristic.solution import SoundSearch, SuccessMemory, GAIN, STUCK

ECHO_K = int(os.environ.get("ECHO_K", "3"))
ECHO_START = float(os.environ.get("ECHO_START", "0.1"))
STORE_PER_DIM = int(os.environ.get("STORE_PER_DIM", "50"))
NEAR = int(os.environ.get("NEAR", "3"))


def rate(points, known_x, known_f, near=NEAR):
    """Rating of each point: the values of the ``near`` closest known
    points, weighted by 1 / distance (lower is better)."""
    sq = (np.einsum("ij,ij->i", points, points)[:, None]
          + np.einsum("ij,ij->i", known_x, known_x)[None, :]
          - 2.0 * points @ known_x.T)
    np.maximum(sq, 0.0, out=sq)
    near = min(near, known_x.shape[0])
    close = np.argpartition(sq, near - 1, axis=1)[:, :near]
    distance = np.sqrt(np.take_along_axis(sq, close, axis=1))
    weight = 1.0 / (distance + 1e-12)
    return (weight * known_f[close]).sum(axis=1) / weight.sum(axis=1)


class Echo(SoundSearch):

    def sound_phase(self, budget, patience=None):
        start = self.evaluations
        population = self.init_population(self.group_size(budget))
        fitness = self._evaluate(population)
        memory = SuccessMemory(self.memory_size)
        echoes = np.empty((0, self.dim))
        self._record(fitness.min())
        best, last_gain = fitness.min(), self.evaluations
        cap = STORE_PER_DIM * self.dim
        seen_x, seen_f = population.copy(), fitness.copy()
        self.success = []

        while self.evaluations < budget:
            progress = (self.evaluations - start) / (budget - start)
            kappa = self.kappa_start + (self.kappa - self.kappa_start) * progress
            size = len(population)
            step, hearing = memory.sample(size, self.rng)
            noisy = progress >= self.noisy_after

            drafts = ECHO_K if progress >= ECHO_START else 1
            options = []
            for _ in range(drafts):
                move = self.compute_move(population, fitness, echoes, step,
                                         kappa, noisy)
                draft = np.where(self.hearing_mask(hearing),
                                 population + move, population)
                options.append(self.fix_boundary(draft, population))
            if drafts == 1:
                candidate = options[0]
            else:
                known_x = np.vstack([seen_x, population])
                known_f = np.concatenate([seen_f, fitness])
                scores = np.column_stack([rate(o, known_x, known_f)
                                          for o in options])
                pick = scores.argmin(axis=1)
                candidate = np.stack(options)[pick, np.arange(size)]

            count = min(size, budget - self.evaluations)
            candidate_fitness = np.full(size, np.inf)
            candidate_fitness[:count] = self._evaluate(candidate[:count])
            seen_x = np.vstack([seen_x, candidate[:count]])[-cap:]
            seen_f = np.concatenate([seen_f, candidate_fitness[:count]])[-cap:]

            improved = candidate_fitness < fitness
            self.success.append((progress, float(improved.mean())))
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
