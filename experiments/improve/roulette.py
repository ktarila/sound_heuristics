"""Prototype: noisy perception. Each agent turns towards a source with
chance proportional to how loud it sounds (intensity ** SHARP), instead of
always the loudest. SHARP (env, default 1): higher means closer to always
picking the loudest. SWITCH (env, default 0): share of each group search
during which agents still pick the loudest; noisy after that."""
import os
import sys
import numpy as np
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))
from sound_heuristic.solution import SoundSearch, compute_intensity

SHARP = float(os.environ.get("SHARP", "1"))
# share of each group search after which perception turns noisy; before
# it every agent picks the loudest (0: noisy from the start)
SWITCH = float(os.environ.get("SWITCH", "0"))


class Roulette(SoundSearch):

    def loudest_source(self, population, fitness, kappa):
        if SWITCH > 0:
            # kappa rises in a straight line, so it tells how far along we are
            span = self.kappa - self.kappa_start
            progress = (kappa - self.kappa_start) / span if span else 1.0
            if progress < SWITCH:
                return super().loudest_source(population, fitness, kappa)
        heard = compute_intensity(population, fitness, kappa)
        n = len(population)
        top = heard.max(axis=1, keepdims=True)
        with np.errstate(invalid="ignore", divide="ignore"):
            weight = np.where(top > 0, heard / top, 0.0) ** SHARP
        total = weight.sum(axis=1)
        source = heard.argmax(axis=1)  # fallback: nothing heard
        ok = total > 0
        cum = np.cumsum(weight[ok], axis=1) / total[ok, None]
        draw = self.rng.random(ok.sum())[:, None]
        source[ok] = np.minimum((cum < draw).sum(axis=1), n - 1)
        return source
