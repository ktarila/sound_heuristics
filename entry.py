"""Heuristic search alorithms based on sound/light"""
from sound_heuristic import solution
from sound_heuristic import config as cfg


def main():
    """Main entry for solution"""
    print(cfg.NAME)
    population = solution.init_population(2, 50, [-10, 10], True)
    # intensity = solution.compute_intensity(population)
    # fitness = solution.compute_fitness(solution.function_one, population)
    small_p = solution.small_power(solution.function_one, population)
    print(small_p.shape)
    print(small_p)
    big_p = solution.big_power(solution.function_one, population)
    print(big_p.shape)
    print(big_p)
    # print(fitness)


if __name__ == '__main__':
    main()
