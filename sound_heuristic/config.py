"""Default settings. Nothing here changes while running."""


NAME = """
******************************************
Sound Intensity Heuristic Search Algorithm
******************************************
"""

MINIMISATION = True
ITERATIONS = 1000
POP_SIZE = 50
RUNS = 30

# Defaults picked by comparing settings on the benchmark functions (see
# README). Check them again after changing how agents move.

# How much loudness counts compared with distance (kappa in
# I = P^kappa / (4 pi r^2)); rises from KAPPA_START to KAPPA during the run.
KAPPA_START = 1.0
KAPPA = 4.0
# Share of all evaluations used at the end for the best agent to refine
# its point alone.
REFINE = 0.3
# Echoes (places agents recently left) kept for random pushes, as a
# multiple of the number of agents. 0 turns echoes off.
ARCHIVE = 1.0
# Start the group again (keeping the best point) when its best value has
# not really improved for this share of all evaluations. 0: never.
STALL = 0.1  # chosen on the moved and turned classic functions, 30 coordinates
# Agents left when the group search ends: the group shrinks evenly from
# POP_SIZE to this, dropping its worst agents (Tanabe & Fukunaga, 2014).
# None: no shrinking. It helps only when the group starts large (about
# 18 agents per coordinate); see benchmark.py for the CEC settings.
FINAL_SIZE = None
# Slots in the memory of what worked, and the starting step size and
# hearing rate (chance that each coordinate takes part in a move).
MEMORY_SIZE = 5
STEP_INIT = 0.5
HEARING_INIT = 0.5

SEED = None
