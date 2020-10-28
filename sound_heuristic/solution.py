"""Evaluation function for minimisation function"""

import numpy as np

from sound_heuristic import config as cfg


def evaluation():
    """Compute Evaluation Function"""
    print(cfg.NAME)
    return 0


def function_one(value):
    """Unimodal test function for optimisation algo
       Sphere function domain range [-100, 100]^n
       #list of real values in domain range
       Input: [value1, value2, ..., valuen]
       Output: value1^2 + value2^2 + ... + valuen^2
    """
    value_array = np.array(value)
    return sum(np.square(value_array))


def init_population(dim=2, size=50, search_space=None, use_dim=True):
    """Create an initial population for a function"""
    pop = None
    if search_space is None:
        search_space = np.array([-100, 100])
    if use_dim:
        if search_space[0] < 0:
            search_space = search_space ** dim
            search_space[0] *= -1
        else:
            search_space = search_space ** dim
        pop = np.random.default_rng().uniform(
            search_space[0], search_space[1], [size, dim])
    return pop


def compute_intensity(population):
    """Compute the intensity of a population"""
    power = np.zeros((population.shape[0], population.shape[0]))
    return power
