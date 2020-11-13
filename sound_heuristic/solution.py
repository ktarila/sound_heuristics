"""Evaluation function for minimisation function"""

from math import exp
import numpy as np
from sklearn.metrics.pairwise import euclidean_distances

from sound_heuristic import config as cfg


def init_population(dim=2, size=50, search_space=None):
    """Create an initial population for a function"""
    pop = None
    if search_space is None:
        search_space = np.atleast_2d(np.array([-100, 100]))
        # search_space = np.array([[-5, 10], [0, 15]])
        # print(search_space.shape)
    else:
        search_space = np.atleast_2d(np.array(search_space))
        if search_space.shape[0] == 1:
            pop = np.random.default_rng().uniform(
                search_space[0][0], search_space[0][1], [size, dim])
        if search_space.shape[0] == 2:
            # stack by columns because range depends on axis
            pop = np.stack(
                [np.random.uniform(
                    search_space[0][i],
                    search_space[1][i], size) for i in range(dim)], axis=1)
    cfg.HISTORY = np.zeros(pop.shape)
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
                   population, fitness_function, minimisation, iteration):
    """Convert intensity to range 0,1 probabilites"""
    # print("***intensity**")
    # print(intensity)
    # print("***Cumsum***")
    row_total = np.sum(intensity, axis=1)
    # print(row_total)
    row_total = np.atleast_2d(row_total).transpose()
    # Hold cumulative sums
    cum_total = np.cumsum((intensity / row_total), axis=1)
    # Generate a set of uniformly distributed samples...
    uniform_rand = np.random.rand(len(cum_total), 1)
    # Get index
    neighbours = population[(uniform_rand < cum_total).argmax(axis=1)]

    # maximum based on highest intensity --- no probability
    neighbours = population[intensity.argmax(axis=1)]

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
    # percentage = np.atleast_2d(percentage).transpose() * decay(iteration)
    percentage = np.atleast_2d(percentage).transpose() * cfg.RHO
    diff = (population - neighbours) * percentage / 100
    # rand_num = np.random.default_rng().uniform(
    #     0, 1, [population.shape[0], 1])
    # diff = (population - neighbours) * rand_num
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
    # print("********small_p**********")
    # print(small_p)
    # print("******big_p**********")
    # print(small_p / total)
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


def decay(iteration):
    """ decay to 37% of previous value at
        every 100 intervals. Initial value at iteration = 0 is rho
    """
    return cfg.RHO * exp(-1 * iteration / 600)


def fix_boundary(population):
    """Adjust population to be in boundary"""
    next_pop = np.copy(population)
    search_space = np.atleast_2d(np.array(cfg.DOMAIN))
    if search_space.shape[0] == 1:
        # keep next pop in range
        # all greater than is upper limit minus random value
        next_pop[
            next_pop > search_space[0][1]
        ] = search_space[0][1] - np.random.uniform(0, search_space[0][1])
        # next_pop[next_pop > cfg.DOMAIN[1]] = cfg.DOMAIN[
        #     1] - np.random.uniform(0, 1)
        # all less is lowwer limit plus random value
        next_pop[
            next_pop < search_space[0][0]
        ] = search_space[0][0] + np.random.uniform(0, search_space[0][1])
        # next_pop[next_pop < cfg.DOMAIN[0]] = cfg.DOMAIN[
        #     0] + np.random.uniform(0, 1)
    if search_space.shape[0] == 2:
        # update first axis(0)
        next_pop[:, 0][
            next_pop[:, 0] < search_space[0][0]
        ] = search_space[0][0] + np.random.uniform(0, search_space[1][0])
        next_pop[:, 0][
            next_pop[:, 0] > search_space[1][0]
        ] = search_space[1][0] - np.random.uniform(0, search_space[1][0])

        # update second axis
        next_pop[:, 1][
            next_pop[:, 1] < search_space[0][1]
        ] = search_space[0][1] + np.random.uniform(0, search_space[1][1])
        next_pop[:, 0][
            next_pop[:, 1] > search_space[1][1]
        ] = search_space[1][1] - np.random.uniform(0, search_space[1][1])
    return next_pop


def parameter_combinations():
    """get possible variables"""
    rho = np.linspace(10, 95, 30)
    momentum = np.linspace(0, 1, 30)
    # cartesian product to get all combinations
    cart = np.transpose(
        [np.tile(rho, len(momentum)), np.repeat(momentum, len(rho))])
    return cart
