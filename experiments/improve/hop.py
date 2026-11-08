"""Prototype: whole hops. The ambient push (another agent minus another
agent or an echo) is added in full, not scaled by the step size, for a
share HOP (env, default 0.3) of the agents each iteration. On a regular
grid of valleys the gap between two agents is a whole number of grid
steps, so a whole hop lands in another valley instead of on a ridge."""
import os
import sys
import numpy as np
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))
from sound_heuristic.solution import SoundSearch
from waves import ambient

HOP = float(os.environ.get("HOP", "0.3"))


class Hop(SoundSearch):

    def compute_move(self, population, fitness, echoes, step, kappa,
                     noisy=False):
        source = self.loudest_source(population, fitness, kappa, noisy)
        direction = self.direction(fitness, source)
        towards = direction[:, None] * (population[source] - population)
        push = ambient(self, population, echoes)
        hop = self.rng.random(len(population)) < HOP
        scale = np.where(hop, 1.0, step)
        return step[:, None] * towards + scale[:, None] * push
