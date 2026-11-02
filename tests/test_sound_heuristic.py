"""Run with: python -m unittest discover tests"""
import unittest

import numpy as np

from sound_heuristic import fitness as F
from sound_heuristic import solution as S

# (index, best point)
OPTIMA = [
    (1, np.zeros(30)), (2, np.zeros(30)), (3, np.zeros(30)),
    (4, np.zeros(30)), (5, np.ones(30)), (6, np.full(30, -0.5)),
    (8, np.full(30, 420.968746)), (9, np.zeros(30)), (10, np.zeros(30)),
    (11, np.zeros(30)), (12, np.full(30, -1.0)), (13, np.ones(30)),
    (14, np.array([-32.0, -32.0])),
    (15, np.array([0.1928, 0.1908, 0.1231, 0.1358])),
    (16, np.array([0.0898, -0.7126])),
    (17, np.array([np.pi, 2.275])),
    (18, np.array([0.0, -1.0])),
    (19, np.array([0.114614, 0.555649, 0.852547])),
    (20, np.array([0.20169, 0.150011, 0.476874, 0.275332, 0.311652, 0.6573])),
    (21, np.full(4, 4.0)), (22, np.full(4, 4.0)), (23, np.full(4, 4.0)),
]


class TestFitness(unittest.TestCase):
    def test_known_optima(self):
        for index, x in OPTIMA:
            problem = F.get_problem(index)
            with self.subTest(f=index):
                self.assertAlmostEqual(problem.func(x), problem.optimum,
                                       delta=1e-3 * max(1, abs(problem.optimum)))

    def test_f7_noise_fresh_each_call(self):
        values = F.f7(np.zeros((1000, 30)))
        self.assertTrue(np.all((values >= 0) & (values < 1)))
        self.assertGreater(np.unique(values).size, 990)

    def test_vectorised_matches_single(self):
        rng = np.random.default_rng(0)
        for index in range(1, 24):
            if index == 7:
                continue
            problem = F.get_problem(index)
            pop = rng.uniform(problem.lower, problem.upper,
                              (5, problem.lower.size))
            with self.subTest(f=index):
                np.testing.assert_allclose(
                    problem.func(pop), [problem.func(row) for row in pop])

    def test_u_sum_piecewise(self):
        x = np.array([10.5, -10.5, 10.0, -10.0, 3.0])
        self.assertAlmostEqual(F.u_sum(x, 10, 100, 4), 2 * 100 * 0.5 ** 4)

    def test_wrong_dimension(self):
        with self.assertRaises(ValueError):
            F.f14(np.zeros(3))

    def test_f17_bounds_per_dimension(self):
        problem = F.get_problem(17)
        np.testing.assert_array_equal(problem.lower, [-5, 0])
        np.testing.assert_array_equal(problem.upper, [10, 15])


class TestSolution(unittest.TestCase):
    def test_sound_power(self):
        power = S.sound_power(np.array([3.0, 1.0, 2.0, 5.0]))
        self.assertAlmostEqual(power.sum(), 1)
        self.assertEqual(power.argmax(), 1)
        self.assertEqual(power[3], 0)
        # only the order counts, not the size of the values
        np.testing.assert_allclose(
            power, S.sound_power(np.array([3.0, 1.0, 2.0, 5e9])))
        np.testing.assert_allclose(power, [1 / 6, 1 / 2, 1 / 3, 0])

    def test_sound_power_ties(self):
        np.testing.assert_allclose(S.sound_power(np.zeros(4)), 0.25)
        np.testing.assert_allclose(S.sound_power(np.array([1.0, 1.0, 2.0])),
                                   [0.5, 0.5, 0.0])
        np.testing.assert_allclose(S.sound_power(np.array([7.0])), [1.0])

    def test_kappa_changes_choice_of_source(self):
        # agent 0 is closer to agent 1, but agent 2 is the best singer
        pop = np.array([[0.0], [1.0], [1.5]])
        fitness = np.array([5.0, 4.9, 0.0])
        self.assertEqual(S.compute_intensity(pop, fitness, 1)[0].argmax(), 1)
        self.assertEqual(S.compute_intensity(pop, fitness, 4)[0].argmax(), 2)

    def test_identical_agents_do_not_hear_each_other(self):
        intensity = S.compute_intensity(np.zeros((3, 2)), np.zeros(3))
        np.testing.assert_array_equal(intensity, 0)

    def test_success_memory_sample_ranges(self):
        memory = S.SuccessMemory(size=5, step=0.5, hearing=0.5)
        step, hearing = memory.sample(10000, np.random.default_rng(0))
        self.assertTrue(np.all((step > 0) & (step <= 1)))
        self.assertTrue(np.all((hearing >= 0) & (hearing <= 1)))
        self.assertAlmostEqual(np.median(step), 0.5, delta=0.02)

    def test_success_memory_update(self):
        memory = S.SuccessMemory(size=2, step=0.5, hearing=0.5)
        # weighted by gain, leaning large: (1*0.2^2 + 3*0.6^2) / (1*0.2 + 3*0.6)
        memory.update(np.array([0.2, 0.6]), np.array([0.1, 0.9]),
                      np.array([1.0, 3.0]))
        self.assertAlmostEqual(memory.step[0], (0.04 + 1.08) / 2.0)
        self.assertAlmostEqual(memory.hearing[0], (0.01 + 2.43) / 2.8)
        self.assertEqual(memory.slot, 1)
        # no successes: nothing changes
        memory.update(np.array([]), np.array([]), np.array([]))
        self.assertEqual(memory.slot, 1)
        # if every success changed one coordinate, the slot stays at 0
        memory.update(np.array([0.5]), np.array([0.0]), np.array([1.0]))
        self.assertTrue(np.isnan(memory.hearing[1]))
        memory.slot = 1
        _, hearing = memory.sample(1000, np.random.default_rng(0))
        self.assertTrue(np.any(hearing == 0))

    def test_hearing_mask_keeps_one_coordinate(self):
        search = S.SoundSearch(F.f1, np.full(5, -1), np.full(5, 1),
                               rng=np.random.default_rng(0))
        mask = search.hearing_mask(np.zeros(100))
        np.testing.assert_array_equal(mask.sum(axis=1), 1)
        self.assertTrue(search.hearing_mask(np.ones(3)).all())

    def test_fix_boundary(self):
        search = S.SoundSearch(F.f17, [-5, 0], [10, 15],
                               rng=np.random.default_rng(0))
        previous = np.array([[8.0, 5.0], [0.0, 1.0], [1.0, 1.0]])
        candidate = np.array([[20.0, 5.0], [0.0, -3.0], [1.0, 1.0]])
        fixed = search.fix_boundary(candidate, previous)
        # halfway between the old value and the crossed limit
        np.testing.assert_allclose(fixed, [[9.0, 5.0], [0.0, 0.5],
                                           [1.0, 1.0]])

    def test_refine_learns_rotated_ellipsoid(self):
        rng = np.random.default_rng(0)
        dim = 10
        rotation, _ = np.linalg.qr(rng.normal(size=(dim, dim)))
        scale = 10 ** np.linspace(0, 2, dim)

        def ellipsoid(x):
            return np.sum((scale * (np.atleast_2d(x) @ rotation.T)) ** 2,
                          axis=1)
        search = S.SoundSearch(ellipsoid, np.full(dim, -5), np.full(dim, 5),
                               rng=np.random.default_rng(1))
        start = np.full(dim, 2.0)
        _, value = search.refine_best(start, ellipsoid(start)[0], 1.0, 6000)
        self.assertLess(value, 1e-20)
        self.assertEqual(search.evaluations, 6000)

    def test_run_counts_and_curve(self):
        for refine in (0.0, 0.33):
            search = S.SoundSearch(F.f1, np.full(10, -100), np.full(10, 100),
                                   pop_size=20, refine=refine,
                                   rng=np.random.default_rng(0))
            result = search.run(50)
            with self.subTest(refine=refine):
                self.assertEqual(result.evaluations, 20 * 51)
                self.assertEqual(len(result.curve), 50)
                self.assertTrue(np.all(np.diff(result.curve) <= 0))
                self.assertEqual(result.curve[-1], result.best_fitness)
                self.assertAlmostEqual(F.f1(result.best_x),
                                       result.best_fitness)

    def test_stays_in_bounds(self):
        seen = []

        def spy(x):
            seen.append(x.copy())
            return F.f8(x)
        problem = F.get_problem(8)
        S.SoundSearch(spy, problem.lower, problem.upper, pop_size=20,
                      rng=np.random.default_rng(0)).run(60)
        points = np.vstack(seen)
        self.assertTrue(np.all(points >= problem.lower))
        self.assertTrue(np.all(points <= problem.upper))

    def test_reproducible(self):
        problem = F.get_problem(9)

        def run():
            return S.SoundSearch(problem.func, problem.lower, problem.upper,
                                 rng=np.random.default_rng(42)).run(30)
        self.assertEqual(run().best_fitness, run().best_fitness)

    def test_maximisation(self):
        problem = F.get_problem(1)
        result = S.SoundSearch(lambda x: -F.f1(x), problem.lower,
                               problem.upper, minimisation=False,
                               rng=np.random.default_rng(0)).run(100)
        self.assertLess(result.best_fitness, 0)
        self.assertTrue(np.all(np.diff(result.curve) >= 0))
        self.assertGreater(result.best_fitness, -1e-3)

    def test_converges_on_shifted_sphere(self):
        problem = F.get_problem(1)
        shift = np.random.default_rng(3).uniform(-60, 60, 30)
        result = S.SoundSearch(lambda x: F.f1(x - shift), problem.lower,
                               problem.upper,
                               rng=np.random.default_rng(0)).run(300)
        self.assertLess(result.best_fitness, 1e-10)

    def test_invalid_arguments(self):
        with self.assertRaises(ValueError):
            S.SoundSearch(F.f1, [0, 0], [1], rng=None)
        with self.assertRaises(ValueError):
            S.SoundSearch(F.f1, [1], [0])
        with self.assertRaises(ValueError):
            S.SoundSearch(F.f1, [0], [1], pop_size=3)
        with self.assertRaises(ValueError):
            S.SoundSearch(F.f1, [0], [1], refine=1.0)
        with self.assertRaises(ValueError):
            S.SoundSearch(F.f1, [0], [1], stall=-0.1)

    def test_restarts_when_stuck(self):
        class Counting(S.SoundSearch):
            starts = 0

            def init_population(self, size=None):
                self.starts += 1
                return super().init_population(size)

        def flat(x):  # every agent equally good from the start
            return np.zeros(len(np.atleast_2d(x)))

        search = Counting(flat, [-1] * 3, [1] * 3, pop_size=10, stall=0.1,
                          rng=np.random.default_rng(0))
        result = search.run(99)
        self.assertGreater(search.starts, 1)
        self.assertEqual(result.evaluations, 10 * 100)
        self.assertEqual(len(result.curve), 99)

        search = Counting(flat, [-1] * 3, [1] * 3, pop_size=10, stall=0,
                          rng=np.random.default_rng(0))
        search.run(99)
        self.assertEqual(search.starts, 1)

    def test_restart_keeps_best(self):
        lower, upper = -5.12 * np.ones(5), 5.12 * np.ones(5)
        for seed in range(3):
            search = S.SoundSearch(F.f9, lower, upper, pop_size=20,
                                   stall=0.05, refine=0.0,
                                   rng=np.random.default_rng(seed))
            result = search.run(299)
            # the result is never worse than the best seen during the run
            self.assertEqual(result.best_fitness, result.curve[-1])
            self.assertEqual(result.best_fitness, F.f9(result.best_x))

    def test_group_shrinks(self):
        sizes = []

        def spy(x):
            sizes.append(len(x))
            return F.f1(x)
        search = S.SoundSearch(spy, [-100] * 5, [100] * 5, pop_size=40,
                               final_size=4, stall=0, refine=0.3,
                               rng=np.random.default_rng(0))
        result = search.run(evaluations=10_000)
        self.assertEqual(result.evaluations, 10_000)
        self.assertEqual(sum(sizes), 10_000)
        group = [n for n in sizes if n > 1]  # refinement tries one point
        self.assertEqual(group[0], 40)
        self.assertTrue(np.all(np.diff(group) <= 0))
        self.assertEqual(group[-1], 4)
        self.assertEqual(result.curve[-1], result.best_fitness)

    def test_exact_evaluations(self):
        search = S.SoundSearch(F.f1, [-100] * 5, [100] * 5, pop_size=30,
                               rng=np.random.default_rng(0))
        result = search.run(evaluations=1000)  # not a multiple of 30
        self.assertEqual(result.evaluations, 1000)
        self.assertEqual(len(result.curve), 33)
        self.assertEqual(result.curve[-1], result.best_fitness)

    def test_invalid_final_size(self):
        for size in (3, 21):
            with self.assertRaises(ValueError):
                S.SoundSearch(F.f1, [0], [1], pop_size=20, final_size=size)


if __name__ == "__main__":
    unittest.main()
