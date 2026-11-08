"""Prototype: ears that turn with the group.

Version 3 decides which coordinates of a move are heard one problem axis at
a time. On turned functions the valleys do not run along the axes, so a
one-axis move cuts across them. Here a share TURN of the agents (picked at
random each iteration) hear along the main directions of the better half of
the group instead: the move is turned into those directions, each direction
is heard with the agent's hearing rate (at least one), and the result is
turned back. The move itself (towards/away plus the ambient push) is not
changed. Agents that do not turn hear along the axes as before.

Env: TURN (share of agents, default 0.5; 0 reproduces version 3 exactly),
     FRAME_SHARE (share of the group used to find directions, default 0.5),
     TURN_START (share of the group search before turning starts, default 0).
"""
import os
import sys
import numpy as np
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))
from sound_heuristic.solution import SoundSearch, SuccessMemory, GAIN, STUCK

TURN = float(os.environ.get("TURN", "0.5"))
FRAME_SHARE = float(os.environ.get("FRAME_SHARE", "0.5"))
TURN_START = float(os.environ.get("TURN_START", "0.0"))


class Turn(SoundSearch):

    def find_frame(self, population, fitness, frame):
        """Main directions of the better part of the group (columns). Keeps
        the old frame when too few agents are left to tell directions."""
        n = len(population)
        count = max(int(round(FRAME_SHARE * n)), 0)
        if count < self.dim + 1:
            count = min(n, self.dim + 1) if n >= self.dim + 1 else 0
        if count < self.dim + 1:
            return frame
        best = np.argsort(fitness, kind="stable")[:count]
        spread = np.cov(population[best].T)
        if not np.all(np.isfinite(spread)):
            return frame
        _, vectors = np.linalg.eigh(spread)
        return vectors

    def turned_candidate(self, population, move, hearing, frame, turn):
        """Candidate points: agents in ``turn`` hear along ``frame``, the
        others along the axes."""
        mask = self.hearing_mask(hearing)
        candidate = np.where(mask, population + move, population)
        if turn.any():
            rows = np.flatnonzero(turn)
            inside = (move[rows] @ frame) * mask[rows]
            candidate[rows] = population[rows] + inside @ frame.T
        return candidate

    def sound_phase(self, budget, patience=None):
        start = self.evaluations
        population = self.init_population(self.group_size(budget))
        fitness = self._evaluate(population)
        memory = SuccessMemory(self.memory_size)
        echoes = np.empty((0, self.dim))
        self._record(fitness.min())
        best, last_gain = fitness.min(), self.evaluations
        frame = None

        while self.evaluations < budget:
            progress = (self.evaluations - start) / (budget - start)
            kappa = self.kappa_start + (self.kappa - self.kappa_start) * progress
            size = len(population)
            step, hearing = memory.sample(size, self.rng)
            noisy = progress >= self.noisy_after
            move = self.compute_move(population, fitness, echoes, step,
                                     kappa, noisy)
            if TURN > 0 and progress >= TURN_START:
                frame = self.find_frame(population, fitness, frame)
            if TURN > 0 and frame is not None and progress >= TURN_START:
                turn = self.rng.random(size) < TURN
                candidate = self.turned_candidate(population, move, hearing,
                                                  frame, turn)
            else:
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
