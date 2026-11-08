"""Prototype: two leks that meet later.

Peafowl males display in groups (leks). Here the starting group is split in
two, walled apart: no sound, no ambient partner, no echo crosses between
them. Lek A hears as in version 3 (loudness counts more and more, loudest
source at first, less exact later). Lek B hears infrasound: its loudness
does not fade with distance, loudness counts fully (kappa at its end value)
and the choice among loud sources is less exact from the start. At MERGE
(share of the group search) the two leks become one group under the usual
rules, with the step-size memory of the lek whose best agent is better.

Why: hearing near neighbours protects against traps (CEC 2017 F22, F24),
hearing the best from anywhere suits Rastrigin and Schwefel. Mixing the two
inside one group lets far hearers drag everyone into one valley; walling
them apart for a while is the new part.

Env: MODE = leks (default) | infra (one group, infrasound all the way: the
control) | alloc (two walled leks that never merge, but
from ALLOC_START of the group search, every CHECK, the lek whose best agent
is worse keeps only LOSER_KEEPS of its planned size: its evaluations go to
the other lek, which is how a high-level chooser spends its trials) | switch (one group, version 3 hearing until SWITCH, then
infrasound) | single (one group, version 3 hearing: must reproduce version 3
exactly) | off (the built-in group search);
     MERGE (default 0.3), SWITCH (default 0.3), SPLIT (share of agents in lek A, default 0.5).
     SHARE (switch mode only, default 1): after the switch, each agent hears
     infrasound with this probability each round; the others keep version 3
     hearing. SHARE 1 reproduces the plain switch exactly.
"""
import os
import sys
import numpy as np
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))
from sound_heuristic.solution import (SoundSearch, SuccessMemory, GAIN, STUCK,
                                      sound_power)

MODE = os.environ.get("MODE", "leks")
MERGE = float(os.environ.get("MERGE", "0.3"))
SWITCH = float(os.environ.get("SWITCH", "0.3"))
CHECK = float(os.environ.get("CHECK", "0.05"))
ALLOC_START = float(os.environ.get("ALLOC_START", "0.15"))
LOSER_KEEPS = float(os.environ.get("LOSER_KEEPS", "0.7"))
SPLIT = float(os.environ.get("SPLIT", "0.5"))
SHARE = float(os.environ.get("SHARE", "1.0"))
MIN_LEK = 4


class Lek:
    """One walled-off group with its own memory and echoes."""

    def __init__(self, population, fitness, memory, echoes):
        self.population = population
        self.fitness = fitness
        self.memory = memory
        self.echoes = echoes


class Leks(SoundSearch):

    _infra = False
    _mixed = False

    # -- hearing -----------------------------------------------------

    def loudest_source(self, population, fitness, kappa, noisy=False):
        if not self._infra:
            return super().loudest_source(population, fitness, kappa, noisy)
        if self._mixed:
            # some agents hear infrasound (kappa at its end value, noisy),
            # the rest keep version 3 hearing
            far = self.rng.random(len(population)) < SHARE
            near_source = super().loudest_source(population, fitness, kappa,
                                                 noisy)
            self._mixed = False
            try:
                far_source = self.loudest_source(population, fitness,
                                                 self.kappa, True)
            finally:
                self._mixed = True
            return np.where(far, far_source, near_source)
        n = len(population)
        rows = np.arange(n)
        heard = np.tile(sound_power(fitness) ** kappa, (n, 1))
        heard[rows, rows] = 0.0  # nobody hears itself; distance is ignored
        source = heard.argmax(axis=1)
        if not noisy:
            return source
        top = heard[rows, source][:, None]
        with np.errstate(invalid="ignore", divide="ignore"):
            weight = np.where(top > 0, heard / top, 0.0) ** self.focus
        total = weight.sum(axis=1)
        some = total > 0
        cumulative = np.cumsum(weight[some], axis=1) / total[some, None]
        draw = self.rng.random(some.sum())[:, None]
        source[some] = np.minimum((cumulative < draw).sum(axis=1), n - 1)
        return source

    # -- one lek -----------------------------------------------------

    def new_lek(self, size):
        population = self.init_population(size)
        fitness = self._evaluate(population)
        return Lek(population, fitness, SuccessMemory(self.memory_size),
                   np.empty((0, self.dim)))

    def iterate(self, lek, kappa, noisy, infra, budget):
        """One round of moves for one lek."""
        size = len(lek.population)
        step, hearing = lek.memory.sample(size, self.rng)
        self._infra = infra
        self._mixed = infra and MODE == "switch" and SHARE < 1.0
        move = self.compute_move(lek.population, lek.fitness, lek.echoes,
                                 step, kappa, noisy)
        self._infra = False
        self._mixed = False
        candidate = np.where(self.hearing_mask(hearing),
                             lek.population + move, lek.population)
        candidate = self.fix_boundary(candidate, lek.population)

        count = min(size, budget - self.evaluations)
        candidate_fitness = np.full(size, np.inf)
        candidate_fitness[:count] = self._evaluate(candidate[:count])

        improved = candidate_fitness < lek.fitness
        lek.memory.update(step[improved], hearing[improved],
                          lek.fitness[improved] - candidate_fitness[improved])
        lek.echoes = np.vstack([lek.echoes, lek.population[improved]])
        lek.population[improved] = candidate[improved]
        lek.fitness[improved] = candidate_fitness[improved]

    def shrink(self, lek, size):
        """The worst agents leave until ``size`` are left; forget random
        echoes beyond the archive size."""
        if size < len(lek.population):
            keep = np.argsort(lek.fitness, kind="stable")[:size]
            lek.population, lek.fitness = (lek.population[keep],
                                           lek.fitness[keep])
        capacity = int(round(self.archive * len(lek.population)))
        if len(lek.echoes) > capacity:
            keep = self.rng.permutation(len(lek.echoes))[:capacity]
            lek.echoes = lek.echoes[keep]

    @staticmethod
    def merge(first, second):
        """One group; the memory of the lek with the better best agent."""
        lead = first if first.fitness.min() <= second.fitness.min() else second
        return Lek(np.vstack([first.population, second.population]),
                   np.concatenate([first.fitness, second.fitness]),
                   lead.memory, np.vstack([first.echoes, second.echoes]))

    # -- the group search --------------------------------------------

    def lek_sizes(self, total, count, weights=(1.0, 1.0)):
        if count == 1:
            return [total]
        first = max(MIN_LEK, int(round(SPLIT * total * weights[0])))
        second = max(MIN_LEK, int(round((total - round(SPLIT * total))
                                        * weights[1])))
        return [first, second]

    def sound_phase(self, budget, patience=None):
        if MODE == "off":
            return super().sound_phase(budget, patience)
        start = self.evaluations
        total = self.group_size(budget)
        two = MODE in ("leks", "alloc") and MERGE > 0
        infra_only = MODE == "infra"
        leks = [self.new_lek(s) for s in self.lek_sizes(total, 2 if two else 1)]
        self._record(min(lek.fitness.min() for lek in leks))
        best = min(lek.fitness.min() for lek in leks)
        last_gain = self.evaluations
        weights, next_check = [1.0, 1.0], ALLOC_START
        self.allocation = []  # (progress, weight of A, weight of B)

        while self.evaluations < budget:
            progress = (self.evaluations - start) / (budget - start)
            kappa = (self.kappa_start
                     + (self.kappa - self.kappa_start) * progress)
            noisy = progress >= self.noisy_after
            if MODE == "alloc" and len(leks) == 2 and progress >= next_check:
                next_check += CHECK
                a, b = leks[0].fitness.min(), leks[1].fitness.min()
                tied = abs(a - b) <= 1e-8 + 1e-12 * max(abs(a), abs(b))
                if not tied:
                    behind = 0 if a > b else 1
                    weights[behind] *= LOSER_KEEPS
                self.allocation.append((progress, *weights))
            if (len(leks) == 2 and progress >= MERGE
                    and MODE != "alloc"):
                leks = [self.merge(*leks)]
                best, last_gain = leks[0].fitness.min(), self.evaluations
            for index, lek in enumerate(leks):
                if self.evaluations >= budget:
                    break
                infra = (infra_only or (len(leks) == 2 and index == 1)
                         or (MODE == "switch" and progress >= SWITCH))
                mixed = infra and MODE == "switch" and SHARE < 1.0
                self.iterate(lek, kappa if mixed else
                             (self.kappa if infra else kappa),
                             noisy if mixed else (True if infra else noisy),
                             infra, budget)

            sizes = self.lek_sizes(self.group_size(budget), len(leks),
                                   weights)
            for lek, size in zip(leks, sizes):
                self.shrink(lek, size)
            self._record(min(lek.fitness.min() for lek in leks))

            if patience and len(leks) == 1:
                fitness = leks[0].fitness
                spread = np.ptp(fitness)
                if best - fitness.min() > GAIN * spread:
                    best, last_gain = fitness.min(), self.evaluations
                if (self.evaluations - last_gain >= patience
                        or spread <= STUCK * abs(best)):
                    break

        if len(leks) == 2:
            # never merged (MERGE >= 1): the lek with the better best agent
            # goes on to the refinement, alone
            leks = [min(leks, key=lambda lek: lek.fitness.min())]
        return leks[0].population, leks[0].fitness
