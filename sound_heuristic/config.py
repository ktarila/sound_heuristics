"""Default settings. Nothing here is mutated at run time."""


NAME = """
******************************************
Sound Intensity Heuristic Search Algorithm
******************************************
"""

MINIMISATION = True
ITERATIONS = 1000
POP_SIZE = 50
RUNS = 30

# Defaults tuned with ``entry.py --tune``-style random search on f5, f9,
# f10, f12 (30 agents x 500 iterations). Re-tune after any change to the
# update rule.

# Step size towards / away from the selected neighbour, in percent of
# the distance between the two agents.
RHO = 16.0
# Upper bound of the random fraction of last step carried forward.
MOMENTUM = 0.27
# Initial scale of random exploration, as a fraction of the domain width.
# Decays to 0 over the run.
EXPLORATION = 0.055
# Strength of the attraction to the global best; grows with progress^2.
PULL = 2.9
# Probability that an agent receives an exploration kick in an iteration.
EXPLORATION_PROB = 0.5

SEED = None
