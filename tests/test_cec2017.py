"""Tests for the CEC 2017 functions."""
import unittest

import numpy as np

from sound_heuristic import cec2017 as C


def _data_available():
    try:
        C._load("shift_data_1.txt")
        return True
    except OSError:  # no data and no network
        return False


def _best_point(index, dim):
    shift, matrix, _ = C._data(index, dim)
    if index > 20:
        return shift[0]  # first component, which has no bias
    if index == 9:  # Levy: best where the rotated point is all ones
        return shift + np.linalg.solve(matrix, np.ones(dim))
    return shift


class TestSizes(unittest.TestCase):
    def test_sizes(self):
        self.assertEqual(C._sizes((0.3, 0.3, 0.4), 10), [3, 3, 4])
        self.assertEqual(C._sizes((0.1, 0.2, 0.2, 0.2, 0.3), 30),
                         [3, 6, 6, 6, 9])
        self.assertEqual(C._sizes((0.25, 0.75), 6), [2, 4])  # rounds up

    def test_f2_withdrawn(self):
        with self.assertRaises(ValueError):
            C.evaluate(np.zeros(10), 2)


@unittest.skipUnless(_data_available(), "CEC 2017 data not available")
class TestCEC2017(unittest.TestCase):
    def test_best_value(self):
        for dim in (10, 30):
            for index in C.FUNCS:
                best = _best_point(index, dim)
                with self.subTest(dim=dim, f=index):
                    self.assertAlmostEqual(C.evaluate(best, index),
                                           100.0 * index, places=6)
                    self.assertTrue(np.all(np.abs(best) <= C.LIMIT))

    def test_many_points_match_one_at_a_time(self):
        rng = np.random.default_rng(0)
        for index in C.FUNCS:
            x = rng.uniform(-100, 100, (4, 10))
            with self.subTest(f=index):
                np.testing.assert_allclose(
                    C.evaluate(x, index), [C.evaluate(r, index) for r in x],
                    rtol=1e-12)

    def test_values_above_best(self):
        rng = np.random.default_rng(1)
        for index in C.FUNCS:
            x = rng.uniform(-100, 100, (20, 10))
            with self.subTest(f=index):
                self.assertTrue(np.all(C.evaluate(x, index) > 100 * index))

    def test_composition_component_optima(self):
        # each component's best point gives exactly its bias
        shifts, _, _ = C._data(26, 10)
        for i, bias in enumerate((0, 100, 200, 300, 400)):
            self.assertAlmostEqual(C.evaluate(shifts[i], 26) - 2600, bias)

    def test_problem(self):
        problem = C.get_problem(5, 30)
        self.assertEqual(problem.optimum, 500)
        self.assertEqual(problem.lower.shape, (30,))
        with self.assertRaises(ValueError):
            C.get_problem(5, 20)


if __name__ == "__main__":
    unittest.main()
