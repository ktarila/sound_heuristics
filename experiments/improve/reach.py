"""Prototype: sound that carries further as the run goes on.

Intensity heard: P_j^kappa / (4 pi r^(2 w)). Version 3 has w = 1 (sound
falls with the square of distance). Here w falls in a straight line from 1
to W_END over the group search, starting at DECAY_START (share of the
search). With w near 0 distance hardly matters, so every agent hears the
loudest agents from anywhere (like the DE rule's pull towards the best
few), while early on neighbours still drown out far agents (keeps groups
apart, avoids traps).
Env: DECAY_START (default 0.3), W_END (default 0.0).
"""
import os
import sys
import numpy as np
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))
from sound_heuristic.solution import SoundSearch, sound_power, pairwise_sq_distances

DECAY_START = float(os.environ.get("DECAY_START", "0.3"))
W_END = float(os.environ.get("W_END", "0.0"))


class Reach(SoundSearch):

    def _exponent(self, kappa):
        span = self.kappa - self.kappa_start
        progress = (kappa - self.kappa_start) / span if span else 1.0
        if progress <= DECAY_START:
            return 1.0
        t = (progress - DECAY_START) / (1.0 - DECAY_START)
        return 1.0 + (W_END - 1.0) * t

    def loudest_source(self, population, fitness, kappa, noisy=False):
        w = self._exponent(kappa)
        sq = pairwise_sq_distances(population)
        with np.errstate(divide="ignore", invalid="ignore"):
            area = 4 * np.pi * sq ** w
            inv = np.divide(1.0, area, out=np.zeros_like(area), where=sq > 0)
        heard = inv * sound_power(fitness)[None, :] ** kappa
        source = heard.argmax(axis=1)
        if not noisy:
            return source
        top = heard[np.arange(len(heard)), source][:, None]
        with np.errstate(invalid="ignore", divide="ignore"):
            weight = np.where(top > 0, heard / top, 0.0) ** self.focus
        total = weight.sum(axis=1)
        some = total > 0
        cum = np.cumsum(weight[some], axis=1) / total[some, None]
        draw = self.rng.random(some.sum())[:, None]
        source[some] = np.minimum((cum < draw).sum(axis=1), len(heard) - 1)
        return source
