"""Heuristic search alorithms based on sound/light"""
from sound_heuristic import solution
from sound_heuristic import config as cfg


def main():
    """Main entry for solution"""
    print(cfg.NAME)
    print(solution.evaluation())


if __name__ == '__main__':
    main()
