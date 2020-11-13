"""Heuristic search alorithms based on sound/light"""
import argparse
import numpy as np

from sound_heuristic import solution
from sound_heuristic import config as cfg
from sound_heuristic import fitness


def main():
    """Main entry of program"""
    print(cfg.NAME)
    results = [run_search(cfg.FITNESS_FUNCTION) for _ in range(30)]
    print()
    print("Median", np.median(results))
    print("Mean", np.average(results))
    print("Best", np.min(results))
    # print(results)


def run_search(fitness_func):
    """Run sound search"""
    print('.', end='', flush=True)
    population = solution.init_population(cfg.DIM, 50, cfg.DOMAIN)
    fitnesses = solution.compute_fitness(fitness_func, population)
    initial_best = solution.get_best_index(fitnesses, cfg.MINIMISATION)
    # initial_vector = population[initial_best[0]]
    global_best = population[initial_best[0]]
    for iteration in range(cfg.ITERATIONS):
        # print("Iteration:", iteration)
        population = next_population(population, fitness_func, iteration)
        fitnesses = solution.compute_fitness(fitness_func, population)
        # print("******fitnesses*****")
        # print(fitnesses)
        best = solution.get_best_index(fitnesses, cfg.MINIMISATION)
        worst = solution.get_worst_index(fitnesses, cfg.MINIMISATION)
        # print("  Best:", fitnesses[best])
        # print("  Best:", population[best[0]], fitnesses[best])
        # print("  Worst:", fitnesses[worst])
        # print("  Worst:", population[worst[0]], fitnesses[worst])
        global_best = solution.compare_fitness(
            population[best[0]],
            global_best, fitness_func, cfg.MINIMISATION)
        if fitness_func(global_best) != fitnesses[best]:
            population[worst[0]] = global_best
        # print("  Global Best", fitness_func(global_best))
        # print("--------------------------------------------")
    # print("Intial Best:", initial_vector, fitness_func(initial_vector))
    # print("Intial Best:", fitness_func(initial_vector))
    return fitness_func(global_best)
    # print("  Global Best", global_best, fitness_func(global_best))
    # zeros = np.zeros(30)
    # print(zeros)
    # print(fitness_func(zeros))


def next_population(pop, fitness_function, iteration):
    """Compute the agents for the next iteration"""
    intensity = solution.compute_intensity(
        pop, fitness_function, cfg.MINIMISATION)
    movement = solution.compute_change(
        intensity, pop, fitness_function, cfg.MINIMISATION, iteration)
    # print(movement.shape)
    # print(cfg.HISTORY.shape)
    # add fraction of history as past momentum
    rand_array = np.atleast_2d(np.random.uniform(0, cfg.MOMENTUM, len(pop))).T
    movement = (rand_array * cfg.HISTORY) + movement
    cfg.HISTORY = np.copy(movement)
    next_pop = movement + pop
    next_pop = solution.fix_boundary(next_pop)
    return next_pop


def get_domain(index):
    """Get domain boundaries given an index"""
    if index < 1 or index > 23:
        raise Exception("Domain index should be between 1 and 23")
    domains = {
        1: ([-100, 100], 30, fitness.f1),
        2: ([-10, 10], 30, fitness.f2),
        3: ([-100, 100], 30, fitness.f3),
        4: ([-100, 100], 30, fitness.f4),
        5: ([-30, 30], 30, fitness.f5),
        6: ([-100, 100], 30, fitness.f6),
        7: ([-1.28, 1.28], 30, fitness.f7),
        8: ([-500, 500], 30, fitness.f8),
        9: ([-5.12, 5.12], 30, fitness.f9),
        10: ([-32, 32], 30, fitness.f10),
        11: ([-600, 600], 30, fitness.f11),
        12: ([-50, 50], 30, fitness.f12),
        13: ([-50, 50], 30, fitness.f13),
        14: ([-65.53, 65.53], 2, fitness.f14),
        15: ([-5, 5], 4, fitness.f15),
        16: ([-5, 5], 2, fitness.f16),
        17: ([[-5, 10], [0, 15]], 2, fitness.f17),
        18: ([-5, 5], 2, fitness.f18),
        19: ([0, 1], 3, fitness.f19),
        20: ([0, 1], 6, fitness.f20),
        21: ([0, 10], 4, fitness.f21),
        22: ([0, 10], 4, fitness.f22),
        23: ([0, 10], 4, fitness.f23)
    }
    cfg.DOMAIN = domains[index][0]
    cfg.DIM = domains[index][1]
    cfg.FITNESS_FUNCTION = domains[index][2]
    # set random value for fitness function f7
    cfg.RAND_VALUE = np.random.uniform(0, 1)
    # cfg.RAND_VALUE = 0.1


def set_hyperparams(index):
    """set params"""
    if index < 1 or index > 23:
        raise Exception("Domain index should be between 1 and 23")
    params = {
        1: (18.16326531, 0.69387755),
        2: (64.73684211, 0.10526316)
    }
    cfg.RHO = params[index][0]
    cfg.MOMENTUM = params[index][1]


def initialize():
    """Read program arguments
       Single argument that contains the index of fitness function
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-i', type=int, required=True,
        help="Enter the index of fitness function between 1 - 23")

    parser.add_argument('-n', type=int, required=True,
                        help="Enter number of interations program should run")

    args = parser.parse_args()

    cfg.INDEX = args.i
    cfg.ITERATIONS = args.n
    get_domain(cfg.INDEX)
    # set_hyperparams(cfg.INDEX)


def find_parameter():
    """exhaustive search for parameters"""
    combinations = solution.parameter_combinations()
    print(len(combinations), "Combinations")
    cfg.RHO = combinations[0, 0]
    cfg.MOMENTUM = combinations[0, 1]
    # print(combinations)
    best_param = combinations[0, :]
    best = best_of_five()
    print(best_param, best)
    length = len(combinations)
    for i in range(1, length):
        print("---------")
        print(i)
        cfg.RHO = combinations[i, 0]
        cfg.MOMENTUM = combinations[i, 1]
        res = best_of_five()
        print(combinations[i, :], res)
        if cfg.MINIMISATION:
            if res < best:
                best = res
                best_param = combinations[i, :]
        else:
            if res > best:
                best = res
                best_param = combinations[i, :]
    print("-------Best-----------")
    print(best_param, best)
    print("----------------------")


def best_of_five():
    """get best result out of five"""
    results = [run_sound_search(100) for _ in range(20)]
    return np.average(results)  # return average
    # return np.min(results) if cfg.MINIMISATION else np.max(results)


def run_sound_search(iterations):
    """run sound search"""
    population = solution.init_population(cfg.DIM, 50, cfg.DOMAIN)
    fitness_func = cfg.FITNESS_FUNCTION
    fitnesses = solution.compute_fitness(fitness_func, population)
    initial_best = solution.get_best_index(fitnesses, cfg.MINIMISATION)
    global_best = population[initial_best[0]]
    for iteration in range(iterations):
        population = next_population(population, fitness_func, iteration)
        fitnesses = solution.compute_fitness(fitness_func, population)
        best = solution.get_best_index(fitnesses, cfg.MINIMISATION)
        worst = solution.get_worst_index(fitnesses, cfg.MINIMISATION)
        global_best = solution.compare_fitness(
            population[best[0]],
            global_best, fitness_func, cfg.MINIMISATION)
        if fitness_func(global_best) != fitnesses[best]:
            population[worst[0]] = global_best
    return fitness_func(global_best)


if __name__ == '__main__':
    initialize()
    find_parameter()
    # set_hyperparams(cfg.INDEX)
    # main()
