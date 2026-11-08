"""Hearing trace: learned hearing rate over the run, and for moves with
few vs many coordinates, how often they succeed and how big the gain is
(relative to the group's spread of values). Usage: python htrace.py KEY SEEDS"""
import sys
import numpy as np
import lab
from sound_heuristic import solution
from sound_heuristic.solution import SoundSearch

key, seeds = sys.argv[1], int(sys.argv[2])
func, lower, upper, optimum, budget = lab.problem(key)


class Probe(SoundSearch):
    """Each iteration, half the agents (at random) hear at least 0.8 of the
    coordinates for this probe only; the memory learns from the rest, so
    the learned rate is the normal one."""
    def sound_phase(self, budget_, patience=None):
        start = self.evaluations
        population = self.init_population(self.group_size(budget_))
        fitness = self._evaluate(population)
        memory = solution.SuccessMemory(self.memory_size)
        echoes = np.empty((0, self.dim))
        self._record(fitness.min())
        while self.evaluations < budget_:
            progress = (self.evaluations - start) / (budget_ - start)
            kappa = self.kappa_start + (self.kappa - self.kappa_start) * progress
            size = len(population)
            step, hearing = memory.sample(size, self.rng)
            move = self.compute_move(population, fitness, echoes, step, kappa,
                                     progress >= self.noisy_after)
            wide = self.rng.random(size) < 0.5
            heard = np.where(wide, np.maximum(hearing, 0.8), hearing)
            mask = self.hearing_mask(heard)
            candidate = self.fix_boundary(np.where(mask, population + move, population), population)
            count = min(size, budget_ - self.evaluations)
            cf = np.full(size, np.inf); cf[:count] = self._evaluate(candidate[:count])
            improved = cf < fitness
            spread = max(np.ptp(fitness), 1e-300)
            gain = np.where(improved, (fitness - cf) / spread, 0.0)
            best_before = fitness.min()
            newbest = cf < best_before
            # rank the agent would have among the others after the move
            order = np.sort(fitness)
            rank_before = np.searchsorted(order, fitness) / size
            rank_after = np.searchsorted(order, cf) / size
            jump = np.where(improved, rank_before - rank_after, 0.0)
            EXTRA.append((progress, newbest[wide].mean() if wide.any() else np.nan,
                          newbest[~wide].mean() if (~wide).any() else np.nan,
                          jump[wide].mean() if wide.any() else np.nan,
                          jump[~wide].mean() if (~wide).any() else np.nan))
            LOG.append((progress, np.nanmean(memory.hearing) if not np.all(np.isnan(memory.hearing)) else 0.0,
                        improved[wide].mean() if wide.any() else np.nan,
                        improved[~wide].mean() if (~wide).any() else np.nan,
                        gain[wide].sum() / max(wide.sum(), 1), gain[~wide].sum() / max((~wide).sum(), 1)))
            learn = improved & ~wide
            memory.update(step[learn], hearing[learn], fitness[learn] - cf[learn])
            echoes = np.vstack([echoes, population[improved]])
            population[improved] = candidate[improved]; fitness[improved] = cf[improved]
            size = self.group_size(budget_)
            if size < len(population):
                keep = np.argsort(fitness, kind="stable")[:size]
                population, fitness = population[keep], fitness[keep]
            cap = int(round(self.archive * len(population)))
            if len(echoes) > cap:
                echoes = echoes[self.rng.permutation(len(echoes))[:cap]]
            self._record(fitness.min())
        return population, fitness


for seed in range(seeds):
    LOG = []; EXTRA = []
    s = Probe(func, lower, upper, pop_size=180, final_size=4, kappa_start=0.0, kappa=8.0,
              refine=0.1, stall=0, rng=np.random.default_rng(seed))
    r = s.run(evaluations=budget)
    L = np.array(LOG)
    print(f"{key} seed {seed}: final {r.best_fitness - optimum:.3f}")
    print("   share of run | learned hearing | success wide / narrow | gain per try wide / narrow")
    for lo, hi in [(0, .1), (.1, .3), (.3, .5), (.5, .7), (.7, 1.0)]:
        m = (L[:, 0] >= lo) & (L[:, 0] < hi)
        print(f"   {lo:.1f}-{hi:.1f}        {np.nanmean(L[m,1]):5.2f}            "
              f"{np.nanmean(L[m,2]):.3f} / {np.nanmean(L[m,3]):.3f}         "
              f"{np.nanmean(L[m,4]):.2e} / {np.nanmean(L[m,5]):.2e}")
    E = np.array(EXTRA)
    print("   share of run | new group best per try wide / narrow | rank gained per try wide / narrow")
    for lo, hi in [(0, .1), (.1, .3), (.3, .5), (.5, .7), (.7, 1.0)]:
        m = (E[:, 0] >= lo) & (E[:, 0] < hi)
        print(f"   {lo:.1f}-{hi:.1f}        {np.nanmean(E[m,1]):.5f} / {np.nanmean(E[m,2]):.5f}"
              f"                 {np.nanmean(E[m,3]):.4f} / {np.nanmean(E[m,4]):.4f}")
