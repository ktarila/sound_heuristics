"""Prototype: flat hearing late in the run. After FLAT_START of the group
search, an agent picks evenly (not weighted by loudness) among the sources
that sound at least BAND times as loud as the loudest one it hears; like the
DE rule's uniform pick among the best few, but chosen by what is heard.
Before FLAT_START it is version 3 exactly. Env: FLAT_START (0.5), BAND (0.3)."""
import os
import sys
import numpy as np
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))
from sound_heuristic.solution import SoundSearch, compute_intensity

FLAT_START = float(os.environ.get("FLAT_START", "0.5"))
BAND = float(os.environ.get("BAND", "0.3"))


class Flat(SoundSearch):

    def loudest_source(self, population, fitness, kappa, noisy=False):
        span = self.kappa - self.kappa_start
        progress = (kappa - self.kappa_start) / span if span else 1.0
        if progress < FLAT_START:
            return super().loudest_source(population, fitness, kappa, noisy)
        heard = compute_intensity(population, fitness, kappa)
        source = heard.argmax(axis=1)
        top = heard[np.arange(len(heard)), source][:, None]
        with np.errstate(invalid="ignore", divide="ignore"):
            weight = np.where(top > 0, (heard >= BAND * top).astype(float), 0.0)
        total = weight.sum(axis=1)
        some = total > 0
        cum = np.cumsum(weight[some], axis=1) / total[some, None]
        draw = self.rng.random(some.sum())[:, None]
        source[some] = np.minimum((cum < draw).sum(axis=1), len(heard) - 1)
        return source
