"""Evaluation function for minimisation function"""

import numpy as np
from sklearn.metrics.pairwise import euclidean_distances

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
    # value_array = np.array(value)
    return sum(np.square(value))


def init_population(dim=2, size=50, search_space=None, use_dim=True):
    """Create an initial population for a function"""
    pop = None
    if search_space is None:
        search_space = np.array([-100, 100])
    else:
        search_space = np.array(search_space)
    if use_dim:
        if search_space[0] < 0:
            search_space = search_space ** dim
            search_space[0] *= -1
        else:
            search_space = search_space ** dim
        pop = np.random.default_rng().uniform(
            search_space[0], search_space[1], [size, dim])
        # pop = np.stack(
        #     [np.random.uniform(search_space[0],
        #                        search_space[1], dim) for _ in range(size)])
    return pop


def compute_intensity(population, fitness_function, minimisation=True):
    """Compute the intensity of a population
       Given the power (determined from the fitness)
       of an agent
    """
    # Distance between pair of agents
    distance = euclidean_distances(population, population)
    area = 4 * np.pi * np.power(distance, 2)
    # compute 1/area^2
    area_reciprocal = np.power(np.reciprocal(
        area, out=np.zeros_like(area), where=area != 0), 2)
    # Transform big_power to column vector for multiplication
    power_big = big_power(fitness_function, population, minimisation)
    # print(power_big.shape)
    # for row multiplication
    big_pow_col = np.atleast_2d(power_big).transpose()
    # print(big_pow_col.shape)
    return area_reciprocal * big_pow_col


def compute_change(intensity,
                   population, fitness_function, minimisation=True):
    """Convert intensity to range 0,1 probabilites"""
    row_total = np.sum(intensity, axis=1)
    row_total = np.atleast_2d(row_total).transpose()
    # Hold cumulative sums
    cum_total = np.cumsum((intensity / row_total), axis=1)
    # Generate a set of uniformly distributed samples...
    uniform_rand = np.random.rand(len(cum_total), 1)
    # Get index
    neighbours = population[(uniform_rand < cum_total).argmax(axis=1)]
    # Get population array
    pop_fit = compute_fitness(fitness_function, population)
    neighbour_fitness = compute_fitness(fitness_function, neighbours)
    percentage = np.zeros(pop_fit.shape)
    if minimisation:
        percentage = (neighbour_fitness / np.maximum(
            pop_fit, neighbour_fitness)) + np.random.uniform(0, 1)
    else:
        percentage = (pop_fit / np.maximum(
            pop_fit, neighbour_fitness)) + np.random.uniform(0, 1)
    percentage = np.atleast_2d(percentage).transpose() * cfg.RHO
    diff = (population - neighbours) * percentage / 100
    return diff


def compute_fitness(fitness_function, population):
    """Compute the fitness of a population
       Input is the fintess function and population
    """
    return np.apply_along_axis(fitness_function, 1, population)


def get_best(fitness_array, minimisation=True):
    """Get the best result,
       if minimisation best is smallest value
       if not minimisation best is largest value
    """
    return np.amin(fitness_array) if minimisation else np.amax(fitness_array)


def get_best_index(fitness_array, minimisation=True):
    """Get the best result,
       if minimisation best is smallest value
       if not minimisation best is largest value
    """
    if minimisation:
        return np.unravel_index(
            np.argmin(fitness_array, axis=None), fitness_array.shape)
    return np.unravel_index(
        np.argmax(fitness_array, axis=None), fitness_array.shape)


def get_worst(fitness_array, minimisation=True):
    """Get the best result,
       if minimisation best is smallest value
       if not minimisation best is largest value
    """
    return np.amax(fitness_array) if minimisation else np.amin(fitness_array)


def get_worst_index(fitness_array, minimisation=True):
    """Get the best result,
       if minimisation best is smallest value
       if not minimisation best is largest value
    """
    if minimisation:
        return np.unravel_index(
            np.argmax(fitness_array, axis=None), fitness_array.shape)
    return np.unravel_index(
        np.argmin(fitness_array, axis=None), fitness_array.shape)


def small_power(fitness_function, population, minimisation=True):
    """Calculate small p of a population"""
    fitness_array = compute_fitness(fitness_function, population)
    best = get_best(fitness_array, minimisation)
    worst = get_worst(fitness_array, minimisation)
    small_p = (fitness_array - worst) / best - worst
    return small_p


def big_power(fitness_function, population, minimisation=True):
    """Calculate the nomalized Power (fitness of agents in population)"""
    small_p = small_power(fitness_function, population, minimisation)
    total = np.sum(small_p)
    return small_p / total


def movement(population, intensity, power):
    """Calculate movement of agents in population
       Which is a fraction of calling agent (based on the intensity)
       divided by the power of agent
    """
    total_intensity = np.atleast_2d(np.sum(intensity, axis=1)).transpose()
    fraction = population * total_intensity
    total = np.sum(fraction, axis=0)
    # reshape to add repeat total
    total = np.reshape(total, (1, total.size))
    # repeat rows x times
    displacement = np.repeat(total, population.shape[0], axis=0)
    return displacement * np.atleast_2d(power).transpose()


def compare_fitness(first, second, fitness_function, minimisation=True):
    """Compare the fitness values of two agents"""
    first_fitness = fitness_function(first)
    second_fitness = fitness_function(second)
    if minimisation:
        return first if first_fitness < second_fitness else second
    return first if first_fitness > second_fitness else second
