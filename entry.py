"""Heuristic search alorithms based on sound/light"""
import argparse
import numpy as np

from sound_heuristic import solution
from sound_heuristic import config as cfg
from sound_heuristic import fitness


def main():
    """Main entry for solution"""
    print(cfg.NAME)
    index, iterations = read_arguments()
    get_domain(index)
    fitness_func = cfg.FITNESS_FUNCTION
    domain = cfg.DOMAIN
    population = solution.init_population(cfg.DIM, 50, domain)
    fitnesses = solution.compute_fitness(fitness_func, population)
    initial_best = solution.get_best_index(fitnesses, cfg.MINIMISATION)
    initial_vector = population[initial_best[0]]
    global_best = population[initial_best[0]]
    for iteration in range(1, iterations):
        print("Iteration:", iteration)
        population = next_population(population, fitness_func, iteration)
        fitnesses = solution.compute_fitness(fitness_func, population)
        # print("******fitnesses*****")
        # print(fitnesses)
        best = solution.get_best_index(fitnesses, cfg.MINIMISATION)
        worst = solution.get_worst_index(fitnesses, cfg.MINIMISATION)
        print("  Best:", fitnesses[best])
        # print("  Best:", population[best[0]], fitnesses[best])
        print("  Worst:", fitnesses[worst])
        # print("  Worst:", population[worst[0]], fitnesses[worst])
        global_best = solution.compare_fitness(
            population[best[0]],
            global_best, fitness_func, cfg.MINIMISATION)
        if fitness_func(global_best) != fitnesses[best]:
            population[worst[0]] = global_best
        print("  Global Best", fitness_func(global_best))
        print("--------------------------------------------")
    # print("Intial Best:", initial_vector, fitness_func(initial_vector))
    print("Intial Best:", fitness_func(initial_vector))
    print("  Global Best", global_best, fitness_func(global_best))
    # zeros = np.zeros(30)
    # print(zeros)
    # print(fitness_func(zeros))


def next_population(pop, fitness_function, iteration):
    """Compute the agents for the next iteration"""
    intensity = solution.compute_intensity(
        pop, fitness_function, cfg.MINIMISATION)
    movement = solution.compute_change(
        intensity, pop, fitness_function, cfg.MINIMISATION, iteration)
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


def read_arguments():
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

    index = args.i
    iterations = args.n
    return (index, iterations)


if __name__ == '__main__':
    main()
