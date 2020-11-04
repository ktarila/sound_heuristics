"""Heuristic search alorithms based on sound/light"""
from sound_heuristic import solution
from sound_heuristic import config as cfg


def main():
    """Main entry for solution"""
    print(cfg.NAME)
    fitness_func = solution.function_one
    population = solution.init_population(2, 50, [-10, 10], cfg.MINIMISATION)
    intensity = solution.compute_intensity(
        population, fitness_func, cfg.MINIMISATION)
    print(intensity.shape)
    print(intensity)
    power = solution.small_power(fitness_func, population, cfg.MINIMISATION)
    movement = solution.movement(population, intensity, power)
    print(movement)
    print(movement.shape)


if __name__ == '__main__':
    main()
