"""Prototype: stop the hearing rate collapsing to one coordinate.

HEARING_FIX (env):
  recover  - a memory slot that reached 0 can come back (no sticky 0)
  floor    - hearing at least 0.7 in the first quarter of the budget and
             0.6 in the first half (as jSO, Brest et al. 2017); sticky 0 kept
  both     - floor and recover
  late     - hearing at least LATE_FLOOR once LATE_START of the budget is
             used (default 0.5 from 0.1), slots can recover
  latesticky - like late, but a slot that reached 0 stays at 0
  explore  - slots can recover, and each iteration a share EXPLORE
             (default 0.2) of the agents tries a hearing rate drawn at
             random from [0, 1]; all successes update the memory as usual
  share    - like late, but only a share WIDE (default 0.5) of the agents,
             picked at random each iteration, hear widely (at least
             LATE_FLOOR); the rest use the learned hearing rate
HEARING_INIT (env): starting hearing rate (default 0.5)
"""
import os
import sys
import numpy as np
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))
from sound_heuristic import solution
from sound_heuristic.solution import SoundSearch

FIX = os.environ.get("HEARING_FIX", "both")
INIT = float(os.environ.get("HEARING_INIT", "0.5"))
LATE_FLOOR = float(os.environ.get("LATE_FLOOR", "0.5"))
LATE_START = float(os.environ.get("LATE_START", "0.1"))
WIDE = float(os.environ.get("WIDE", "0.5"))
EXPLORE = float(os.environ.get("EXPLORE", "0.2"))
PROGRESS = [0.0]  # share of the whole budget used; one search per process

_Base = solution.SuccessMemory


class Memory(_Base):
    def __init__(self, size=5, step=0.5, hearing=None):
        super().__init__(size, step, INIT if hearing is None else hearing)

    def sample(self, n, rng):
        step, hearing = super().sample(n, rng)
        if FIX in ("floor", "both"):
            p = PROGRESS[0]
            floor = 0.7 if p < 0.25 else 0.6 if p < 0.5 else 0.0
            hearing = np.maximum(hearing, floor)
        if FIX in ("late", "latesticky") and PROGRESS[0] >= LATE_START:
            hearing = np.maximum(hearing, LATE_FLOOR)
        if FIX == "explore":
            trying = rng.random(n) < EXPLORE
            hearing = np.where(trying, rng.random(n), hearing)
        if FIX == "share" and PROGRESS[0] >= LATE_START:
            wide = rng.random(n) < WIDE
            hearing = np.where(wide, np.maximum(hearing, LATE_FLOOR), hearing)
        return step, hearing

    def update(self, step, hearing, gain):
        if (FIX in ("recover", "both", "late", "share", "explore") and step.size
                and np.sum(gain) > 0):
            weight = gain / np.sum(gain)
            self.step[self.slot] = (np.sum(weight * step ** 2)
                                    / np.sum(weight * step))
            if np.max(hearing) == 0:
                self.hearing[self.slot] = 0.0
            else:
                self.hearing[self.slot] = (np.sum(weight * hearing ** 2)
                                           / np.sum(weight * hearing))
            self.slot = (self.slot + 1) % self.step.size
            return
        super().update(step, hearing, gain)


solution.SuccessMemory = Memory  # sound_phase looks the name up at run time


class Hearing(SoundSearch):
    def run(self, iterations=1000, evaluations=None):
        self._total = evaluations or self.pop_size * (iterations + 1)
        return super().run(iterations, evaluations)

    def _record(self, best_f):
        PROGRESS[0] = self.evaluations / self._total
        super()._record(best_f)
