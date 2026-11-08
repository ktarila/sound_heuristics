"""The DE rule in place of listening: each agent moves towards a random one
of the best p share of the group (at least 2 agents), always towards, as in
"current-to-pbest" (Zhang & Sanderson 2009; Tanabe & Fukunaga 2014).
Everything else is version 3 unchanged.

PBEST (env): a number (fixed share, L-SHADE uses 0.11) or "jso" (0.25
falling to 0.125 over the group search, as in jSO, Brest et al. 2017).
"""
import os
import sys
import numpy as np
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))
from sound_heuristic.solution import SoundSearch

PBEST = os.environ.get("PBEST", "0.11")


class PBest(SoundSearch):

    def _share(self, kappa):
        if PBEST != "jso":
            return float(PBEST)
        span = self.kappa - self.kappa_start
        progress = (kappa - self.kappa_start) / span if span else 1.0
        return 0.25 - 0.125 * progress

    def loudest_source(self, population, fitness, kappa, noisy=False):
        n = len(population)
        top = max(2, int(round(self._share(kappa) * n)))
        best = np.argsort(fitness, kind="stable")[:top]
        return best[self.rng.integers(0, top, n)]

    @staticmethod
    def direction(fitness, source):
        return np.ones(len(fitness))
