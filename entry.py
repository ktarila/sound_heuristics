"""Heuristic search alorithms based on sound/light"""
from sound_heuristic import solution
from sound_heuristic import config as cfg


def main():
    """Main entry for solution"""
    print(cfg.NAME)
    fitness_func = solution.function_one
    population = solution.init_population(2, 50, [-10, 10], True)
    intensity = solution.compute_intensity(population, fitness_func, True)
    # print(intensity.shape)
    print(intensity)


if __name__ == '__main__':
    main()
