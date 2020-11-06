"""Heuristic search alorithms based on sound/light"""
from sound_heuristic import solution
from sound_heuristic import config as cfg


def main():
    """Main entry for solution"""
    print(cfg.NAME)
    fitness_func = solution.function_one
    population = solution.init_population(2, 50, [-10, 10], cfg.MINIMISATION)
    fitnesses = solution.compute_fitness(fitness_func, population)
    initial_best = solution.get_best_index(fitnesses, cfg.MINIMISATION)
    initial_vector = population[initial_best[0]]
    global_best = population[initial_best[0]]
    for iteration in range(1, 1000):
        print("Iteration:", iteration)
        population = next_population(population, fitness_func)
        fitnesses = solution.compute_fitness(fitness_func, population)
        best = solution.get_best_index(fitnesses, cfg.MINIMISATION)
        worst = solution.get_worst_index(fitnesses, cfg.MINIMISATION)
        print("  Best:", population[best[0]], fitnesses[best])
        print("  Worst:", population[worst[0]], fitnesses[worst])
        global_best = solution.compare_fitness(
            population[best[0]],
            global_best, fitness_func, cfg.MINIMISATION)
        if fitness_func(global_best) != fitnesses[best]:
            population[worst[0]] = global_best
        print("  Global Best", global_best, fitness_func(global_best))
    print("Intial Best:", initial_vector, fitness_func(initial_vector))
    # print("Zero: [0, 0]", fitness_func([0, 0]))


def next_population(pop, fitness_function):
    """Compute the agents for the next iteration"""
    intensity = solution.compute_intensity(
        pop, fitness_function, cfg.MINIMISATION)
    movement = solution.compute_change(
        intensity, pop, fitness_function, cfg.MINIMISATION)
    next_pop = movement + pop
    return next_pop


if __name__ == '__main__':
    main()
