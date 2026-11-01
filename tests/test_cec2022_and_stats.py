"""Tests for the CEC 2022 functions and the statistical tests."""
import itertools
import unittest

import numpy as np

from sound_heuristic import cec2022 as C
from sound_heuristic import stats as S


def _data_available():
    try:
        C._load("shift_data_1.txt")
        return True
    except OSError:  # no data and no network
        return False


@unittest.skipUnless(_data_available(), "CEC 2022 data not available")
class TestCEC2022(unittest.TestCase):
    def test_best_value_at_shift(self):
        for dim in C.DIMS:
            for index in range(1, 13):
                shift = C._load(f"shift_data_{index}.txt")
                best_point = shift[:dim] if index < 9 else shift[0, :dim]
                with self.subTest(dim=dim, f=index):
                    self.assertAlmostEqual(C.evaluate(best_point, index),
                                           C.BEST[index], places=6)
                    self.assertTrue(np.all(np.abs(best_point) <= C.LIMIT))

    def test_many_points_match_one_at_a_time(self):
        rng = np.random.default_rng(0)
        for index in range(1, 13):
            x = rng.uniform(-100, 100, (5, 10))
            with self.subTest(f=index):
                np.testing.assert_allclose(
                    C.evaluate(x, index), [C.evaluate(r, index) for r in x])

    def test_values_above_best(self):
        rng = np.random.default_rng(1)
        for index in range(1, 13):
            values = C.evaluate(rng.uniform(-100, 100, (50, 20)), index)
            with self.subTest(f=index):
                self.assertTrue(np.all(values > C.BEST[index]))

    def test_problem_and_errors(self):
        problem = C.get_problem(3, 20)
        np.testing.assert_array_equal(problem.lower, np.full(20, -100))
        self.assertEqual(problem.optimum, 600.0)
        with self.assertRaises(ValueError):
            C.evaluate(np.zeros(5), 1)
        with self.assertRaises(ValueError):
            C.get_problem(13)


class TestStats(unittest.TestCase):
    def test_chi2_matches_tables(self):
        for x, df, p in [(3.841, 1, 0.05), (7.815, 3, 0.05),
                         (16.919, 9, 0.05), (6.635, 1, 0.01)]:
            self.assertAlmostEqual(S.chi2_sf(x, df), p, places=4)
        self.assertEqual(S.chi2_sf(0, 3), 1.0)

    def test_rank_sum_close_to_exact(self):
        rng = np.random.default_rng(1)
        a, b = rng.normal(0, 1, 8), rng.normal(0.7, 1, 8)
        ranks = S._ranks(np.concatenate([a, b]))
        centre = 8 * 17 / 2
        observed = abs(ranks[:8].sum() - centre)
        exact = np.mean([abs(ranks[list(c)].sum() - centre) >= observed - 1e-9
                         for c in itertools.combinations(range(16), 8)])
        self.assertAlmostEqual(S.rank_sum(a, b).p_value, exact, delta=0.01)

    def test_rank_sum_winner_and_ties(self):
        low, high = np.arange(10.0), np.arange(10.0) + 100
        self.assertEqual(S.rank_sum(low, high).winner, "a")
        self.assertEqual(S.rank_sum(high, low).winner, "b")
        # errors below 1e-8 count as 0, so these are all ties
        self.assertEqual(S.rank_sum(np.zeros(6), np.full(6, 1e-9)),
                         S.RankSum(1.0, "="))

    def test_friedman(self):
        # algorithm 0 always best, 2 always worst: ranks 1, 2, 3
        table = np.array([[1.0, 2.0, 3.0]] * 10)
        result = S.friedman(table)
        np.testing.assert_allclose(result.average_ranks, [1, 2, 3])
        self.assertAlmostEqual(result.statistic, 20.0)
        self.assertLess(result.p_value, 1e-4)
        # all equal: no evidence of a difference
        self.assertEqual(S.friedman(np.ones((5, 3))).p_value, 1.0)

    def test_holm(self):
        rows = S.holm([1.0, 2.0, 3.0], ["a", "b", "c"], 10, "a")
        self.assertEqual([r.name for r in rows], ["c", "b"])
        self.assertAlmostEqual(rows[0].adjusted_p_value, 2 * rows[0].p_value)
        self.assertGreaterEqual(rows[1].adjusted_p_value,
                                rows[0].adjusted_p_value)
        self.assertGreater(rows[0].z, 0)


if __name__ == "__main__":
    unittest.main()
