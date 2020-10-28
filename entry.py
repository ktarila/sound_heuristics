"""Heuristic search alorithms based on sound/light"""
from sound_heuristic import solution
from sound_heuristic import config as cfg


def main():
    """Main entry for solution"""
    print(cfg.NAME)
    population = solution.init_population()
    intensity = solution.compute_intensity(population)
    print(intensity)


if __name__ == '__main__':
    main()
