# Sound Intensity Search

A population-based search method for continuous optimisation, inspired by
how peafowl use infrasonic sound in mating displays. Every candidate
solution (agent) makes a sound whose loudness depends on how good it is.
Agents listen, pick the loudest sound they hear, and move relative to it.

Based on: P. Kenekayoro, *A Meta-Heuristic Search Algorithm based on
Infrasonic Mating Displays in Peafowls*, Journal of Advances in Mathematics
and Computer Science 36(5): 98-106, 2021.
[doi:10.9734/JAMCS/2021/v36i530366](https://doi.org/10.9734/JAMCS/2021/v36i530366)

The three versions are named after how they search: **Mating Call** (version 1,
the method of the paper: every agent calls, and the others move to the loudest
call), **Echo** (version 2: each move gets a push from echoes, places agents
left behind) and **Encore** (version 3: when stuck, the group plays again from
new places). In the code and result files they are `v1`, `v2` and `v3`.

This is Encore: Echo plus starting the group again
when it gets stuck (step 8), a group that shrinks during the run
(step 9), and hearing that turns less exact after the start (step 10). The sound model (steps 1-3 below) follows
the paper, with two changes: loudness comes from an agent's place in the
ranking rather than its raw value, and a loudness exponent $\kappa$ rises
during the run. The rest was reworked to fix problems found in Mating Call
(see [What changed from Mating Call](#what-changed-from-mating-call)).

## How it works

The search looks for the lowest value of a function inside lower and upper
limits for each coordinate. It keeps $n$ agents $x_1, \dots, x_n$.

### 1. Loudness from fitness

Agents are sorted from best to worst. Loudness falls in equal steps down
that list, so the best agent is loudest and the worst is silent:

```math
p_i = \frac{n - 1 - \text{rank}_i}{n - 1},
\qquad
P_i = \frac{p_i}{\sum_j p_j}
```

($\mathrm{rank}_i$ is 0 for the best agent; agents with equal values share a rank.)
Only the order matters, so one extremely bad agent cannot make every other
agent sound the same.

### 2. Sound weakens with distance

```math
I_{ij} = \frac{P_j^{\kappa}}{4 \pi r_{ij}^2},
\qquad r_{ij} = \lVert x_i - x_j \rVert
```

$\kappa$ says how much loudness counts compared with distance. It rises from 1
to 4 during the run (from 0 to 8 on the longer CEC runs, see step 10). Early on, an agent mostly hears its near neighbours,
so small groups explore different parts of the space. Later, the best
agents are heard from far away and everyone gathers around them.

### 3. Move relative to the loudest source

Every agent listens to the source it hears loudest, $k = \arg\max_j I_{ij}$
(after the first 10% of the group search, a loud source picked at random;
see step 10).
It moves towards that source if the source is fitter and away from it
otherwise, plus an "ambient" term: the difference between a random agent
$x_a$ and an echo $x_e$ (a random current or past position):

```math
v_i = x_i + F_i \big( \pm (x_k - x_i) + (x_a - x_e) \big)
```

$F_i$ is the agent's step size. Adding the difference between two agents
is the basic move of differential evolution (Storn & Price, 1997).

### 4. Only some coordinates are heard

Each coordinate of $v_i$ is heard with chance $C_i$ (the agent's hearing
rate), and at least one always is. The others stay as they were; this is
the crossover of differential evolution (Storn & Price, 1997). A
coordinate that goes past a limit is put halfway between its old value
and that limit (as in Tanabe & Fukunaga, 2014).

### 5. Keep only improvements

The agent moves to its new point only if that point is better. The place
it leaves becomes an echo. Up to $n$ echoes are kept; when there are more,
random ones are forgotten. Keeping replaced points this way comes from
JADE (Zhang & Sanderson, 2009).

### 6. Step size and hearing rate learn from what worked

Each agent draws its own $F_i$ and $C_i$ around values remembered from
recent successful moves. After each iteration, the values that produced
improvements are averaged into the memory, with bigger improvements
counting more. (This scheme is from Tanabe & Fukunaga, 2013, in the form
used by L-SHADE, Tanabe & Fukunaga, 2014.)

### 7. Refinement

The last 30% of the evaluations (10% on the CEC functions) are spent
differently: the group stops,
and the best agent keeps improving its own point alone. It tries one random
step at a time and keeps it if it is no worse. Its steps grow when more
than about 1 in 5 work and shrink otherwise, and they stretch along the
direction recent successful steps went. (The method is from Igel, Suttorp &
Hansen, 2006.)

The two phases do different jobs. The sound phase decides which valley of
the landscape to be in, which is the hard part when there are many
valleys. The refinement cannot switch valleys, but it walks to the bottom
of the chosen one much faster than the group can. On the sphere function
(f1), spending every evaluation on the sound phase gives an average
result of $9 \times 10^{-5}$; handing the last 30% to the refinement gives $2.5 \times 10^{-20}$.

### 8. Starting again when stuck

A group can stop making progress long before the sound phase ends. Either
every agent ends up equally good, or the agents stay spread out over
different valleys and almost no move is accepted. Then the group starts
again from new random places, and loudness again counts little at first
($\kappa$ restarts at 1). The best point found so far is always kept, and the
refinement starts from it.

The group counts as stuck when its best value has not really improved
for 10% of all evaluations (`stall`). A real gain is at least 1% of the
spread between the group's best and worst values, so it does not depend
on the scale or offset of the function.

### 9. The group shrinks

On the CEC functions the group starts large, with 18 agents per
coordinate (180 for 10 coordinates), and shrinks evenly to 4 agents by
the end of the sound phase. Each time it shrinks, the worst agents leave.
Early on, many agents spread over many valleys; later, the evaluations go
to the few best agents. This schedule comes from L-SHADE (Tanabe &
Fukunaga, 2014). A group that starts again late in the run starts at the
size planned for that moment.

On the classic functions the group keeps 30 agents. Their budget is 13
times smaller, and there letting the worst agents leave did not help
(see [What changed from Mating Call](#what-changed-from-mating-call)).

A run with $n$ agents and `iterations` iterations uses
$n \times (\text{iterations} + 1)$ function evaluations, the same as one evaluation per
agent per iteration. `run(evaluations=...)` sets the number exactly.

### 10. Hearing turns less exact

For the first 10% of each group search (`noisy_after`), every agent turns
to the loudest sound it hears. After that its hearing is less exact: it
turns towards a source picked at random, with a chance proportional to the
square of how loud that source sounds (`focus` = 2):

```math
\Pr(k) = \frac{I_{ik}^{2}}{\sum_j I_{ij}^{2}}
```

The loudest source is still the most likely choice, but fainter ones are
picked too.

The two halves do different jobs. Early on, always picking the loudest
keeps each agent listening to its neighbours. On functions made of several
blended functions, the group decides which valley it settles in during the
first few percent of the budget. If agents hear far-off good agents too
soon, the whole group crowds into one valley, often the wrong one. Later,
when loudness counts more, nearly every agent hears the same best agent
loudest, and all of them move along almost the same line. Letting each
agent pick among the louder sources gives the group more directions to
try, which helps on functions with many regular valleys, such as
Rastrigin. Pulling each agent towards a random one of the best few agents,
rather than the single best, is also what JADE does (Zhang & Sanderson,
2009); here the choice comes from what each agent hears.

On the CEC functions, whose runs are 7 to 13 times longer, loudness also
counts from 0 (at first agents go only by distance) up to 8, and the
refinement gets 10% of the evaluations instead of 30%. The classic
functions keep $\kappa$ rising from 1 to 4 and 30% refinement: with their short
runs, the group needs the faster start and the longer refinement.

## Usage

Requires Python 3 and NumPy.

```bash
python entry.py -i 1 -n 1000                 # f1, 1000 iterations, 30 runs
python entry.py -i 9 -n 500 --pop 30 --seed 0
python entry.py -i 5 --kappa 8 --refine 0.2  # change settings
python entry.py --tune 5 9 10 12 -n 500 --samples 40 --runs 5 --seed 0
python benchmark.py                          # reproduce the results below
python benchmark.py --suite cec2022 --dim 10 --save results/cec2022_D10_v3-noisy.json
python benchmark.py --suite cec2022 --dim 10 --pop 50 --final-pop 50 --stall 0 \
    --kappa-start 1 --kappa 4 --refine 0.3 --noisy-after 1   # Echo
python benchmark.py --suite cec2017 --dim 10 --runs 30   # design set
python compare.py results/cec2022_D10_*.json --control v3-noisy
python compare.py results/cec2022_D10_v3-noisy.json --published  # vs CEC 2022 entries
python -m unittest discover tests
```

`compare.py` runs the statistical tests in `sound_heuristic/stats.py` on
saved results: the Wilcoxon rank-sum test on each function, and the
Friedman test with Holm's correction across functions, as recommended by
Demšar (2006) and Derrac et al. (2011). The CEC 2022 functions are in `sound_heuristic/cec2022.py`;
their data files are downloaded from the organisers' GitHub the first time
they are used (into `cec2022_data/`, or the folder named by the
`CEC2022_DATA` environment variable). They are not stored in this
repository because the organisers' repository has no license.

The CEC 2017 functions (Awad et al., 2016) are in
`sound_heuristic/cec2017.py`, a port of the organisers' C code; their
data goes into `cec2017_data/` (or `CEC2017_DATA`) in the same way. From
Encore on, settings are chosen on CEC 2017 and tested on CEC 2022, so
the CEC 2022 results stay a fair test. Where runs get stuck, the port
gives the same values as the published jSO results, to 4-7 digits.

A web page in `docs/index.html`, published at
[ktarila.com/research/sound-intensity-search](https://ktarila.com/research/sound-intensity-search/),
opens with the research report *Improving sound intensity search*: every change
that was tried, adopted or not, with its motivation, protocol and result. It
also shows all three groups of functions used here:
the 12 CEC 2022 functions (the test set), the 29 CEC 2017 functions (the design
set) and the 23 classic functions. A sidebar lists them. Each function has its
history and properties, a 3D surface, a replay of Mating Call, Echo and Encore searching
it, and curves of runs on the whole function. Other pages explain the three
versions and summarise what the method does well and what limits it. Open the
file in a browser (the chart library loads from the internet). The prose is in
`docs/functions.js` (the report in `docs/tried.js`); `python docs/make_text.py` writes `docs/meta.js` (names and
building blocks, read from the code) and `python docs/make_data.py` writes the
recorded runs in `docs/data/` and the tables in `docs/tables.js` (about 30
minutes).

The prototypes and raw results behind the report, mainly its Sections 3.2
to 3.7, are in `experiments/` (see its README). They are kept as they were
run and are not part of the package.

`-i` selects one of the 23 test functions in `sound_heuristic/fitness.py`.
Each run reports the mean, standard deviation, median, best and worst
result, and the number of function evaluations.

From Python:

```python
import numpy as np
from sound_heuristic.solution import SoundSearch

def sphere(X):                      # X has shape (n_agents, dim)
    return np.sum(X ** 2, axis=1)

result = SoundSearch(sphere, lower=[-100] * 10, upper=[100] * 10,
                     rng=np.random.default_rng(0)).run(500)
print(result.best_fitness, result.evaluations)
```

| Setting | Default | Meaning |
|---|---|---|
| `kappa_start` | 1 | how much loudness counts at the start of each group search |
| `kappa` | 4 | how much loudness counts at the end of the group search |
| `refine` | 0.3 | share of evaluations for the final refinement |
| `archive` | 1.0 | echoes kept, as a multiple of the number of agents |
| `stall` | 0.1 | start the group again after this share of all evaluations without a real gain (0: never) |
| `pop_size` | 50 | number of agents at the start |
| `final_size` | None | agents left at the end of the sound phase; the group shrinks evenly from `pop_size` (None: no shrinking) |
| `noisy_after` | 0.1 | share of each group search after which agents pick a loud source at random instead of always the loudest (1: never) |
| `focus` | 2 | how strongly a noisy listener favours louder sources |

## Results

All results: the 23 classic test functions of Yao et al. (1999), 30 agents
× 500 iterations (15,030 evaluations), 30 independent runs, seed 0. The
GWO (Grey Wolf Optimizer; Mirjalili et al., 2014), PSO (Particle Swarm
Optimisation; Kennedy & Eberhart, 1995) and GSA (Gravitational Search
Algorithm; Rashedi et al., 2009) values are the published averages from
the Grey Wolf Optimizer paper. Mating Call (commit `e512be8`) was
rerun with the same seeds. Everything for Echo is reproduced by
`python benchmark.py`.

**Average place** on the 23 functions, out of 4 (lower is better; results
equal to 4 significant figures share a place):

| | all | f1-f7 | f8-f13 | f14-f23 | best on |
|---|---|---|---|---|---|
| GWO | 1.61 | 1.43 | 1.67 | 1.70 | 15 functions |
| **Echo** | **1.70** | 2.00 | 2.50 | **1.00** | 12 functions |
| PSO | 2.65 | 3.29 | 2.33 | 2.40 | 6 functions |
| GSA | 2.87 | 3.29 | 3.50 | 2.20 | 5 functions |
| *Mating Call* | *2.30* | *2.86* | *3.00* | *1.50* | *7 functions* |

(The Mating Call row is its own place when compared with the same three methods.)

**One-to-one** (functions won / tied / lost):

| | vs GWO | vs PSO | vs GSA |
|---|---|---|---|
| Echo | 7 / 6 / 10 | 14 / 4 / 5 | 17 / 5 / 1 |
| Mating Call | 4 / 4 / 15 | 10 / 4 / 9 | 12 / 5 / 6 |

**Per function** (average of 30 runs; "place" is Echo's place out of 4):

| | Echo | Mating Call | GWO | PSO | GSA | place |
|---|---|---|---|---|---|---|
| f1 | $2.5 \times 10^{-20}$ | 0.0022 | $6.6 \times 10^{-28}$ | $1.4 \times 10^{-4}$ | $2.5 \times 10^{-16}$ | 2 |
| f2 | 0.0036 | 0.20 | $7.2 \times 10^{-17}$ | 0.042 | 0.056 | 2 |
| f3 | 0.0071 | 52.1 | $3.3 \times 10^{-6}$ | 70.1 | 897 | 2 |
| f4 | 4.21 | 7.08 | $5.6 \times 10^{-7}$ | 1.09 | 7.35 | 3 |
| f5 | 35.8 | 42.0 | 26.8 | 96.7 | 67.5 | 2 |
| f6 | $\mathbf{5.7 \times 10^{-20}}$ | 0.0023 | 0.817 | $1.0 \times 10^{-4}$ | $2.5 \times 10^{-16}$ | 1 |
| f7 | 0.074 | 0.024 | 0.0022 | 0.123 | 0.089 | 2 |
| f8 | **−12080** | −6980 | −6123 | −4841 | −2821 | 1 |
| f9 | 14.5 | 47.1 | 0.311 | 46.7 | 26.0 | 2 |
| f10 | 2.01 | 3.09 | $1.1 \times 10^{-13}$ | 0.276 | 0.062 | 4 |
| f11 | 0.0149 | 0.0201 | 0.0045 | 0.0092 | 27.7 | 3 |
| f12 | 0.570 | 1.05 | 0.053 | 0.0069 | 1.80 | 3 |
| f13 | 0.327 | 1.19 | 0.654 | 0.0067 | 8.90 | 2 |
| f14 | **0.998** | 1.164 | 4.042 | 3.627 | 5.860 | 1 |
| f15 | $\mathbf{3.075 \times 10^{-4}}$ | $3.942 \times 10^{-4}$ | $3.37 \times 10^{-4}$ | $5.77 \times 10^{-4}$ | $3.673 \times 10^{-3}$ | 1 |
| f16 | −1.032 | −1.032 | −1.032 | −1.032 | −1.032 | 1 (tie) |
| f17 | 0.3979 | 0.3979 | 0.3979 | 0.3979 | 0.3979 | 1 (tie) |
| f18 | 3 | 3 | 3 | 3 | 3 | 1 (tie) |
| f19 | −3.863 | −3.863 | −3.863 | −3.863 | −3.863 | 1 (tie) |
| f20 | **−3.322** | −3.318 | −3.287 | −3.266 | −3.318 | 1 |
| f21 | −10.15 | −9.567 | −10.15 | −6.865 | −5.955 | 1 (tie with GWO) |
| f22 | −10.40 | −9.925 | −10.40 | −8.457 | −9.684 | 1 (tie with GWO) |
| f23 | −10.54 | −10.06 | −10.53 | −9.953 | −10.54 | 1 (tie with GSA) |

On f14-f23 Echo finds the best known value in every one of the 30
runs (standard deviation below $10^{-14}$ on f15-f23).

### With the best point moved and the function turned

Seven of these functions (f1-f4, f9-f11) have their best point at the
origin, and some methods do well partly because they drift towards the
centre of the search space (Niu et al., 2019, show this for GWO). To check that Echo's gains are real, f1-f7
and f9-f13 were also run with the best point moved to a fixed random place
("moved"), and additionally turned by a fixed random angle so that the
coordinates no longer act independently ("moved + turned"). Median of 30
runs (best possible is 0 for all):

| | moved, Mating Call | moved, Echo | moved + turned, Mating Call | moved + turned, Echo |
|---|---|---|---|---|
| f1 | 0.0026 | $\mathbf{8.7 \times 10^{-21}}$ | 0.0026 | $\mathbf{7.2 \times 10^{-21}}$ |
| f2 | 5.24 | **0.0011** | 21.8 | **0.37** |
| f3 | 250 | **0.0079** | 246 | **0.0072** |
| f4 | 19.1 | **5.30** | 17.8 | **1.80** |
| f5 | 27.9 | **22.5** | 178 | **23.5** |
| f6 | 0.0027 | $\mathbf{1.5 \times 10^{-20}}$ | 0.0018 | $\mathbf{7.8 \times 10^{-21}}$ |
| f7 | 0.073 | **0.072** | **0.059** | 0.069 |
| f9 | 89.5 | **13.9** | 87.6 | **47.3** |
| f10 | 2.66 | **2.12** | 2.58 | **2.54** |
| f11 | 0.018 | **0.0099** | 0.025 | **0.011** |
| f12 | 3.69 | **0.19** | 5.10 | **0.89** |
| f13 | 38.9 | **0.026** | 0.37 | $\mathbf{4.4 \times 10^{-14}}$ |

Run with `python benchmark.py --suite shifted` and `--suite rotated`.

### What each part contributes

Each row switches off or replaces one part and reruns all three sets of
functions (23 plain, 12 moved, 12 moved + turned). *Decimal places* is
how close the typical result gets to the best possible value, averaged
over the functions (higher is better). *Worse on* / *better on* count the
47 function results whose typical error is at least twice as large /
at most half as large as with all parts.

| Version | average place | decimal places: plain / moved / moved + turned | worse on | better on |
|---|---|---|---|---|
| **all parts** | **1.70** | 5.0 / 3.9 / 4.6 | - | - |
| listen to a random agent | 1.87 | 4.9 / 3.5 / 3.4 | 16 | 3 |
| listen to the nearest agent (loudness ignored) | 1.91 | 4.4 / 2.9 / 2.9 | 21 | 0 |
| $\kappa$ fixed at 1 | 1.74 | 4.8 / 3.7 / 3.4 | 10 | 0 |
| never move away | 1.74 | 5.1 / 4.1 / 4.2 | 2 | 7 |
| no echoes | 1.78 | 4.8 / 3.3 / 3.1 | 16 | 1 |
| no refinement | 1.78 | 3.3 / 0.9 / 0.5 | 16 | 1 |

The sound model does real work. Listening to a random agent instead of
the loudest makes results worse on 16 of 47 and better on only 3;
ignoring loudness and listening to the nearest agent is worse on 21 and
better on none. Letting loudness count more as the run goes on ($\kappa$ rising
from 1 to 4), the echoes and the refinement each help as well.

Moving away from a worse source is roughly neutral in these tests:
without it, results are better on 7 and worse on 2, mostly by small
amounts, but one f15 run gets stuck and the average place drops. It is
kept because it is part of the original model; it is worth revisiting.

Run with `python benchmark.py --ablate random` (or `nearest`, `towards`, `pbest`),
`--kappa 1`, `--archive 0` or `--refine 0`, adding `--suite shifted` or
`--suite rotated`.

### CEC 2022 functions

The settings above were chosen on the classic functions. The 12 CEC 2022
competition functions (Kumar et al., 2021) were not used for that, so
they give a fairer test. All of them are moved and turned, and F6-F12
mix several functions together. Each run has 10 coordinates and 200,000
evaluations (the competition rules), with 50 agents and 30 runs. The
table gives the mean error (distance above the best possible value;
errors below $10^{-8}$ count as 0). +, − and = say whether the full method is
significantly better, worse or no different from each variant on that
function (Wilcoxon rank-sum test, 5% level).

| F | function | all parts | random agent | nearest agent | never move away |
|---|---|---|---|---|---|
| 1 | Zakharov | 0 | 0 = | 0 = | 0 = |
| 2 | Rosenbrock | 2.82 | 4.68 + | 1.86 = | 2.95 = |
| 3 | Schaffer F7 | 0 | 0 = | 0 = | 0 = |
| 4 | Rastrigin | 6.43 | 6.60 = | 10.5 + | 6.67 = |
| 5 | Levy | 0 | 0 = | 0.142 = | 0 = |
| 6 | mix of 3 | 0.108 | 0.213 + | 0.0978 = | 0.115 = |
| 7 | mix of 6 | 0.176 | 0.538 + | 0.747 + | 0.124 = |
| 8 | mix of 5 | 8.32 | 8.05 = | 10.9 = | 4.75 − |
| 9 | blend of 5 | 229 | 229 = | 229 = | 229 = |
| 10 | blend of 4 | 104 | 104 = | 10.9 − | 104 = |
| 11 | blend of 5 | 0 | 5.01 = | 0 = | 0 = |
| 12 | blend of 6 | 161 | 161 = | 160 = | 162 + |
| | **better / worse / same** | | 3 / 0 / 9 | 2 / 1 / 9 | 1 / 1 / 10 |
| | **Friedman average rank** | **2.29** | 2.88 | 2.46 | 2.38 |

Four functions are solved in every run (F1, F3, F5, F11). On F9 every run
ends at the same value, 229.3.

Here the variants are much harder to tell apart than on the classic
functions. Listening to the loudest agent is better than listening to a
random one on 3 functions and never worse. Against the nearest agent it
is better on 2 and worse on 1 (F10, where the nearest-agent version
escapes a trap that the others fall into). The Friedman test finds no
overall difference between the four (p = 0.55; Holm's adjusted p-values
are all above 0.8). With only 12 functions it can detect only large
differences.

These results show how the parts compare, not how good the method is.

#### Against the competition entries

The organisers publish the results of the 12 entries that sent in all
their runs, 30 per function, with the same budget. `python compare.py
results/cec2022_D10_sound.json --published` downloads them and runs the
same tests (full output in `results/cec2022_D10_published.txt`). Errors
are compared to 6 significant figures, because some entries wrote only
6. Average rank over the 12 functions (1 = best):

| Entry (place in the competition) | Average rank | Sound search better / worse / same |
|---|---|---|
| EA4eig (1st) | 3.92 | 0 / 8 / 4 |
| S-LSHADE-DP (4th) | 4.21 | 1 / 6 / 5 |
| NL-SHADE-LBC (2nd) | 5.29 | 1 / 5 / 6 |
| jSObinexpEig | 6.17 | 2 / 5 / 5 |
| IMPML-SHADE | 6.17 | 2 / 6 / 4 |
| NL-SHADE-RSP-MID (3rd) | 6.42 | 3 / 4 / 5 |
| OMCSOMA | 6.67 | 2 / 4 / 6 |
| **Sound search** | **7.33** | - |
| MTT-SHADE | 7.33 | 3 / 3 / 6 |
| NLSOMACLP | 7.58 | 3 / 4 / 5 |
| Co-PPSO | 9.58 | 5 / 1 / 6 |
| SPHH-Ensemble | 9.83 | 5 / 4 / 3 |
| ZOCMAES | 10.50 | 9 / 2 / 1 |

Sound search places 8th of 13, tied with MTT-SHADE. Holm's test finds no
entry significantly better or worse than it (the smallest adjusted
p-value is 0.38, for EA4eig).

- **Good:** F6 and F12, where it beats 8 of the 12 entries and loses to
  2.
- **Poor:** F2, F4, F7, F8 and F10, where 8 to 11 entries beat it.

Tracing the runs shows why. On F2, F4, F10 and F12 the best value stops
improving after 5-35% of the budget (median of 8 runs), so most of the
evaluations are wasted. The settings were chosen for the classic
functions, whose budget is 13 times smaller (15,000 evaluations against
200,000).

The comparison also checks the CEC 2022 code in this repository. The
values where runs get stuck agree with the entries' own results to 5-8
digits: F4 (0.995, 1.99, 2.98, …), F9 (229.28438) and F12 (159.3687).
EA4eig's result on F9 (185.5) is lower than any other entry's typical
result. Biedrzycki (2024) found that EA4eig could evaluate points outside
the limits, which the official code allows.

It was also run side by side with the organisers' own C code
(`cec22_test_func.cpp`, which the MATLAB version is built from) on the same
points: 1,800 to 4,500 per function, spread over the whole range and
close to every best point, at 10 and 20 coordinates. All 12 functions
agree to within about one part in $10^{12}$ (largest relative difference
$9.8 \times 10^{-13}$). The data files hold the same numbers; the C copy of
F8's shift file has nine extra rows, which F8 never reads.

#### Encore: starting again when stuck

The tables above are for Echo. Encore adds step 8. Its
settings were chosen on the classic functions moved and turned, at 30
coordinates with 300,000 evaluations, not on CEC 2022.

On CEC 2022 (`results/cec2022_D10_v3-restart.json`), Encore beats
Echo on 4 functions and loses on 1:

| | F2 | F4 | F7 | F10 | F12 |
|---|---|---|---|---|---|
| Echo | 2.82 | 6.43 | **0.176** | 104 | 161 |
| Encore | **0.664** | **5.14** | 0.487 | **100** | **160** |

Its average rank among the competition entries improves from 7.33 to
6.92. It is still 8th of 13, now just behind OMCSOMA (6.67) and
NL-SHADE-RSP-MID (6.42). F7 is worse because that function improves in
jumps after long pauses, and a restart can come in the middle of a pause.
On the classic functions at the usual budget, nothing changes.

Starting again does not get past the traps on F9, F10 and F12. Each new
group falls into the same trap as the last one.

#### Encore: a shrinking group

Step 9 was chosen on the CEC 2017 functions at 10 coordinates (100,000
evaluations, 10 runs per function), so CEC 2022 stays a fair test. On CEC
2017 (`results/cec2017_D10_*.json`) it beats Encore without shrinking
on 3 of 29 functions and loses on none. Its mean error drops most on F10
(Schwefel: 174 to 97), F12 (38 to 3.5) and F24 (288 to 180). Starting with
100 or 250 agents is slightly worse than 180, and shrinking from 50 is
worse than not shrinking at all. Once the group shrinks, restarts make
little difference: without them, the result is better on 1 function and
worse on none. Restarts were kept, because they still stop a group that
is completely stuck.

On CEC 2022 (`results/cec2022_D10_v3-shrink.json`), the shrinking group
beats Encore without it on 3 functions and loses on none. It beats
Echo on 7 and loses on none, and the Friedman and Holm tests find
this difference real over all 12 functions (adjusted p = 0.03). Mean
errors where the versions differ:

| | F2 | F4 | F6 | F7 | F8 | F10 | F12 |
|---|---|---|---|---|---|---|---|
| Echo | 2.82 | 6.43 | 0.108 | 0.176 | 8.32 | 104 | 161 |
| Encore, step 8 | 0.664 | **5.14** | 0.094 | 0.487 | 5.86 | 100 | 160 |
| Encore, steps 8 and 9 | **0.399** | **5.14** | **0.0539** | **0.0539** | **2.48** | **97.8** | **159** |

Among the competition entries, its average rank is 6.25: 4th of 13, level
with jSObinexpEig and IMPML-SHADE, behind EA4eig (4.08), S-LSHADE-DP
(4.21) and NL-SHADE-LBC (5.38). Holm's test finds no entry significantly
better (full output in `results/cec2022_D10_v3-shrink_published.txt`).
Most entries still do better on F4 (Rastrigin), F7, F8 and F10. On F9 it
ends at 229.3, like most of them.

#### Encore: hearing turns less exact

Step 10 and the CEC settings ($\kappa$ from 0 to 8, 10% refinement) were
chosen on CEC 2017 at 10 coordinates. With 30 runs per function
(`results/cec2017_D10_v3-noisy.json` against
`results/cec2017_D10_v3-shrink_30runs.json`), they beat steps 8 and 9 alone
on 11 of 29 functions and lose on 1 (F25, 398 against 388). The Friedman
and Holm tests find this difference real (adjusted p = 0.005). Mean
errors on the functions that were weakest: F5 (Rastrigin) 3.95 to 3.32,
F8 (Rastrigin) 4.84 to 3.35, F10 (Schwefel) 115 to 99, F22 37.7 to 21.1
and F24 165 to 111 (F10 and F22 are not significant on their own).

On CEC 2022 (`results/cec2022_D10_v3-noisy.json`), step 10 beats steps 8
and 9 alone on 2 functions and loses on 1. It beats Echo on 6 and
loses on none (Holm's adjusted p = 0.04):

| | F2 | F4 | F6 | F7 | F8 | F10 | F12 |
|---|---|---|---|---|---|---|---|
| Echo | 2.82 | 6.43 | 0.108 | 0.176 | 8.32 | 104 | 161 |
| Encore, step 8 | 0.664 | 5.14 | 0.094 | 0.487 | 5.86 | 100 | 160 |
| Encore, steps 8 and 9 | **0.399** | 5.14 | **0.0539** | 0.0539 | 2.48 | 97.8 | **159** |
| Encore, steps 8 to 10 | 0.664 | **3.48** | 0.0981 | **0.0267** | **1.94** | **81.1** | **159** |

F4 (Rastrigin) and F10 improve significantly; F6 gets worse. On F10, 6 of
30 runs now reach the valley of the best point instead of 1.

The F10 gain did not hold up. Run again with two new sets of random seeds
(`results/cec2022_D10_v3-seed1.json`, `-seed2.json`), 2 and then 0 of 30
runs escape the trap (mean 94.2 and 100.2), so the first result was luck.
F4 stays better than before step 10 (3.81 and 3.88). The standing holds:
4th of 13 on all three seeds, with average ranks 6.00, 5.50 and 6.17.

Among the competition entries, its average rank is 6.00: 4th of 13 on
its own, ahead of jSObinexpEig (6.25) and IMPML-SHADE (6.33), behind
EA4eig (4.08), S-LSHADE-DP (4.29) and NL-SHADE-LBC (5.38). Holm's test
finds no entry significantly better, and for the first time one entry
significantly worse: ZOCMAES (adjusted p = 0.047; full output in
`results/cec2022_D10_v3-noisy_published.txt`). Most entries still do
better on F4, F7 and F8.

#### Encore at 20 coordinates

CEC 2022 is defined at 10 and 20 coordinates. At 20 the competition budget
is 1,000,000 evaluations per run. Encore was run there with nothing
changed: the same settings, a group of 18 per coordinate (360) shrinking to
4, 30 runs per function, seed 0 (`results/cec2022_D20_v3.json`; full
comparison in `results/cec2022_D20_v3_published.txt`). The 360 runs took 2
hours 38 minutes on an 8-core machine that was running another job of the
same size at the same time.

| Entry (place in the competition) | Average rank | Encore better / worse / same |
|---|---|---|
| EA4eig (1st) | 4.25 | 3 / 5 / 4 |
| **Sound search, Encore** | **5.17** | - |
| jSObinexpEig | 5.21 | 3 / 4 / 5 |
| S-LSHADE-DP (4th) | 5.29 | 4 / 1 / 7 |
| NL-SHADE-LBC (2nd) | 5.42 | 4 / 2 / 6 |
| IMPML-SHADE | 5.96 | 6 / 1 / 5 |
| NL-SHADE-RSP-MID (3rd) | 6.96 | 6 / 1 / 5 |
| NLSOMACLP | 6.96 | 7 / 1 / 4 |
| MTT-SHADE | 7.17 | 6 / 1 / 5 |
| OMCSOMA | 7.71 | 8 / 1 / 3 |
| Co-PPSO | 8.42 | 9 / 2 / 1 |
| ZOCMAES | 9.75 | 10 / 1 / 1 |
| SPHH-Ensemble | 12.75 | 12 / 0 / 0 |

It places 2nd of 13, but the gap to the next three (5.21 to 5.42) is too
small to mean anything. Holm's test finds no entry significantly better,
and two significantly worse: SPHH-Ensemble and ZOCMAES (adjusted p = 0.00002
and 0.043). So the standing at 10 coordinates (4th, no entry significantly
better) holds at 20, and is a little better.

- **Solved:** F1, F3 and F5 in every run; F11 in 29 of 30 (one run ends
  at 300, mean 10, where 8 entries are at 150 or above); F2 in 29 of 30 (mean
  1.5; only S-LSHADE-DP and EA4eig are lower).
- **F10 (the trap):** 22 of 30 runs escape, and 8 end at about 100 (mean
  26.8). Encore is significantly better than 10 entries and worse than
  2. This is unlike 10 coordinates, where most runs are trapped. Why is
  not known; the group is twice as large and the budget 5 times larger.
- **Weak:** F4 (Rastrigin, 11.5; 5 entries better, the best 4.45), F7
  (13.3; 5 entries better, the best 2.58; about half the runs end near 21)
  and F12 (232; 3 entries better). F6 (0.371) is behind EA4eig and
  jSObinexpEig.
- **F9:** 180.78 in every run, as for most entries. EA4eig (165) and
  Co-PPSO (180) are lower, as EA4eig is at 10 coordinates.

#### Is listening better than the usual rule of differential evolution?

Much of the search is borrowed from differential evolution (the move, the
crossover, the echoes, the step-size memory), so the fair question is
whether the sound model adds anything. The test: change only whom each
agent moves towards. In place of the source it hears loudest, each agent
moves towards a random one of the best few agents, always towards (the
"current-to-pbest" rule of Zhang & Sanderson, 2009). With our random push,
this is the move of L-SHADE (Tanabe & Fukunaga, 2014). Two forms were run:
the best 11% (L-SHADE), and the best 25% shrinking to 12.5% over each
group search (jSO, Brest et al., 2017). Group size, shrinking, hearing,
step-size memory, restarts and refinement are the same. Run with
`--ablate pbest` or `pbest-jso`; results in `results/*_de-rule-*.json`
and the comparisons in `results/*_vs_de-rule.txt`.

Functions with a significant difference (Wilcoxon, 30 runs):

| | listening better | DE rule better | Friedman and Holm |
|---|---|---|---|
| CEC 2017, best 11% | 7 | 7 | no difference |
| CEC 2017, jSO form | 7 | 6 | no difference |
| CEC 2022, best 11% | 2 | 3 | no difference |
| CEC 2022, jSO form | 3 | 2 | no difference |

Overall they tie, but each is strong in different places. Listening wins on
the blended functions with traps: CEC 2017 F22 (21 against 93 and 100,
where the DE rule is trapped in almost every run), F24 (111 against 269
and 292), F12 and F18; CEC 2022 F6 and F12. The DE rule wins on the
Rastrigin and Schwefel kinds of function: CEC 2017 F5 and F8 (2.3 against
3.3), F10 (43 and 57 against 99); CEC 2022 F4 (2.4 against 3.5) and F7. On
CEC 2022 F10 listening has the lower mean (81 against 100 and 98) because 6
of 30 runs escape the trap (2 and 0 with other seeds, see above), but its
24 trapped runs end a little higher in the trap valley (median 100.26
against 100.21), so the rank-sum test favours the DE rule (best 11%) or
finds no difference (jSO form). This fits the design: an agent that mostly hears its
neighbours keeps separate groups apart and avoids rushing into one valley,
while a pull towards a few of the best agents from anywhere is better at
walking across a regular field of valleys. So the sound rule is a real
alternative to the DE rule, not a relabelling of it. Getting both
strengths in one method is still open.

#### Against the rules of its closest relatives

Two older methods also choose whom an agent moves towards from both how
good the others are and how far away they are. In the firefly algorithm
(Yang, 2009) an agent is drawn to every brighter one, less strongly the
farther away it is. In fitness-distance-ratio particle swarm optimisation
(Peram et al., 2003) a particle follows the better particle with the
largest gain in value per unit of distance. Camacho-Villalón et al. (2023)
show that several methods named after animals, the firefly algorithm among
them, are older methods under new names, so the same question applies
here: does the sound model add anything to these?

The test is the one used for the differential evolution rule. Only whom
each agent moves towards changes, and everything else is Encore. None
of the three rules uses loudness or $\kappa$, and all of them always move
towards. These are the relatives' rules, not their whole methods: the
firefly algorithm's own random step and the swarm's velocities are not
used. Run with `python benchmark.py --ablate firefly` (or `ratio-whole`,
`ratio-coord`); the rules are the `Firefly`, `RatioWhole` and
`RatioCoordinate` classes in `benchmark.py`.

- **Firefly:** one better agent per move, picked with a chance that falls
  with the squared distance, $\exp(-\gamma r^2)$. $\gamma$ is one over the mean squared
  distance between agents, so the fade follows the group's spread.
- **Ratio, whole distance:** the better agent with the largest gain per
  unit of distance.
- **Ratio, per coordinate** (as in Peram et al.): for each coordinate, the
  better agent with the largest gain per unit of distance along that
  coordinate, so each coordinate can follow a different agent.

Functions with a significant difference (Wilcoxon, 30 runs, CEC 2017 and
CEC 2022 at 10 coordinates; results in `results/*_D10_firefly.json`,
`*_ratio-whole.json`, `*_ratio-coord.json`, comparisons in
`results/*_vs_relatives.txt`):

| Rule | CEC 2017: listening better / rule better | CEC 2022: listening better / rule better |
|---|---|---|
| Differential evolution (best 11%) | 7 / 7 | 2 / 3 |
| Firefly | 8 / 6 | 3 / 2 |
| Ratio, whole distance | 3 / 1 | 1 / 2 |
| Ratio, per coordinate | 15 / 0 | 5 / 0 |

On CEC 2017 the per-coordinate ratio is significantly worse than listening
overall (Holm's adjusted p = 0.017). No other difference is significant
overall, on either set.

Where the rules differ is the same trade-off as before:

| | CEC 2017 F22: runs trapped | CEC 2017 F24: runs at 100 or less | CEC 2022 F10: runs escaping | CEC 2017 F5, F8 (Rastrigin) | CEC 2022 F4, F8 |
|---|---|---|---|---|---|
| Listening (Encore) | 5 | 28 | 6 | 3.32, 3.35 | 3.48, 1.94 |
| Differential evolution | 28 | 8 | 0 | 2.29, 2.59 | 2.39, 1.24 |
| Firefly | 26 | 11 | 0 | 2.82, 2.52 | 2.55, 1.53 |
| Ratio, whole distance | 22 | 20 | 1 | 3.48, 3.42 | 3.22, 0.681 |
| Ratio, per coordinate | 6 | 26 | 11 | 5.37, 5.97 | 7.36, 4.88 |

(Runs out of 30. On F22 a trapped run ends at about 100; on F24 the other
runs end at about 330.)

Firefly and the differential evolution rule are trapped on F22 in 26 and
28 runs of 30, against 5 for listening, and do better on the Rastrigin kind
of function. The whole-distance ratio is trapped almost as often (22)
without that gain on CEC 2017, though it is the best of the five on CEC
2022 F7 and F8. In all three an agent is often drawn to a much better agent
far away. The per-coordinate ratio keeps the protection against traps (it
escapes the CEC 2022 F10 trap more often than listening, 11 runs against
6) but is worse almost everywhere else: on the Rastrigin functions its
errors are 1.6 to 2.5 times those of listening. A likely reason is that
each coordinate follows a different agent, so a move no longer points at
any one agent. Of the five rules, listening is the only one that avoids
the traps without being worse overall.

On the test set the whole-distance ratio has the best average rank of the
five (2.38 against 2.79 for listening; Friedman p = 0.18, so no real
difference), mainly from F7 and F8. Among the competition entries it would
also be 4th (average rank 5.88 against 6.00). On the design set it is a
little behind listening (worse on 3 functions, better on 1). Picking it now
would mean choosing on the test set, so Encore keeps listening.

#### Tried and dropped in Encore: choosing between methods

A hyper-heuristic is a top-level method that picks which of several
low-level methods to use as the search goes on (Burke et al., 2003). It
was tried on CEC 2017 to choose between listening rules, at three levels:

- **For each 2% of the budget** (loudest agent, nearest agent, or
  refining the best point): worse than plain restarts on 4 functions,
  better on none.
- **For each new group** (loudest agent, nearest agent, or a group four
  times larger): the same as plain restarts on 27 of 29 functions. A run
  starts only 2 or 3 groups, too few choices to learn from.
- **For each agent at every iteration** (loudest, nearest, or the best
  agents far away; a rule is picked more often when its moves improve
  agents more): worse on 2 functions, better on none.

The listening rules are too alike, and step size and hearing rate
already adapt, so there is little left for a top-level method to gain.

#### Tried and dropped in Encore: other changes

These were tested on CEC 2017 at 10 coordinates, on the functions where
Encore was weakest: F5 and F8 (Rastrigin, turned), F10 (Schwefel,
turned), and F22 and F24, which blend several functions. On F22 a run is
"trapped" when it ends in the valley of the wrong function (error 100).
Most were checked with 51 runs per function, since 20 runs could not tell
a trap rate of 35% from 15%.

- **Different settings.** $\kappa$ ending at 2 or 8, $\kappa$ starting at 0, twice
  as many echoes, 10% refinement, or no restarts: none was better on its
  own. The settings sit on a plateau.
- **A floor on the hearing rate.** During a run the hearing rate falls to
  "one coordinate at a time", even on turned functions, because small
  one-coordinate moves succeed more often. Keeping it at least 0.7 in the
  first quarter of the run and 0.6 in the first half, as jSO does (Brest
  et al., 2017), and letting it recover after reaching 0, helped on F8. But the group settled faster, and F22 was
  trapped in 20 of 51 runs instead of 14.
- **Masking.** When the group shrinks, the agent most drowned out by a
  fitter agent nearby leaves, instead of the worst agent. This keeps
  lone explorers, but it was worse on 6 of 8 functions and did not reduce
  traps. A trace showed why: on F22 the group picks its valley in the first
  3-6% of the budget, long before shrinking matters.
- **Hearing like people.** Each agent had its
  own ears (its own $\kappa$); hearing faded with age, so older agents heard only
  nearby agents; young agents did not listen at all; and at the end of its
  life an agent was replaced by its child at the same spot. A version where
  no agent listens for the first few percent of the run was also tried.
  Each part moved the search the expected way (fewer traps, less exact
  fine-tuning), but none was better than Encore (ageing and the full
  life cycle were checked over 51 runs). Step 10 keeps one part of the
  idea: hearing that becomes less exact as the run goes on.
- **Less exact hearing from the start.** Picking a source at random in
  proportion to its loudness from the very start helped Rastrigin a lot
  (F5 3.3 against 4.1), but F22 was trapped in 36 of 51 runs. Waiting
  until 10% of the run (step 10) keeps the gain without the traps; waiting
  until 30% loses the gain. With `focus` 1 instead of 2, F7 (Lunacek's
  double Rastrigin) got worse.

#### Tried and dropped in Encore: new kinds of change

The changes above all altered whom an agent listens to or how many
coordinates it hears. The comparison with differential evolution showed the
listening rule is already as good as the usual one, and on the weak CEC 2022
functions (F8, F2) the differential evolution rule inside this search is
just as weak. So this round tried changes of a different kind. Each was run
with 31 runs on stand-ins from CEC 2017 (F5 and F8, F7, F10, F12, F17, F21,
F22, F24) plus three new instances of the CEC 2022 F8 blend, with the same
random seeds as Encore. The best was then run on all 29 CEC 2017
functions (30 runs). Off-switch settings were checked to give exactly the
built-in results.

| Idea | Result |
|---|---|
| **Infrasound.** Loudness does not fade with distance, $\kappa$ stays at 8, and sources are picked at random from the start. Peafowl infrasound travels far. | Matches the differential evolution rule on Rastrigin and Schwefel (F5 2.6 against 3.4), and is trapped like it: F22 trapped in 22 of 31 runs against 4 of 31, F24 reaches 100 in 4 of 31 against 31 of 31. |
| **Leks.** Half the group hears as in Encore, half hears infrasound, walled apart (a lek is a group of displaying males). The better half finishes the run. | Gains on the Rastrigin stand-ins, but half the agents and half the evaluations cost the trap protection (F22 trapped in 12 of 31). |
| **A chooser between the two leks.** The lek that is behind gets fewer agents as the run goes on. | No better than leks that are never changed: 0 better, 2 worse. |
| **Why splitting fails.** Encore alone, run with half the agents, half the evaluations, or both. | F22 trapped in 7, 12 and 11 of 31 runs against 4. Halving the evaluations is what costs the protection, so no chooser acting later can undo a split at the start. |
| **Ears that turn with the group.** Hearing applied along the main directions of the better half of the group instead of the coordinate axes. | 0 better, 2 worse; no Rastrigin gain. |
| **Echolocation.** Remember how good the places agents have been to are, draft three moves per agent, evaluate only the one that looks best. | More moves improve things mid-run but fewer late in the run; no gain in a first look. Not run further. |
| **Switch to infrasound at 10%.** Encore's hearing for the first 10% of the run, then infrasound. One group, nothing split. | Stand-ins: 4 better, 2 worse. Whole of CEC 2017: 7 better, 5 worse, 17 no different (Friedman p = 0.68). |
| **A share of agents switching.** After 10%, only half (or a quarter) of the agents hear infrasound. | 0 better, 0 worse on the stand-ins. |

The switch is the closest to a gain. It helps Rastrigin and Schwefel kinds
of function (F5 2.8 against 3.3, F8 2.2 against 3.4) and F22 (8.5 against
21.1), and it costs on the blended functions F7, F12, F13 and F18 (F12 2.15
against 0.14, with 5 of 30 runs ending near 11). Letting only some agents
switch gives up the gain and the loss together. Every version either gave
up the protection against traps or lost the blended functions.

### Strengths and weaknesses

**Strengths:** the low-dimensional functions with several valleys (f14-f23:
best known value in every run), Schwefel (f8: −12080 against a best
possible −12569), and smooth bowls whether or not they are tilted or
stretched (f1, f3, f6). Results hold up when the best point is moved away
from the origin and the function is turned.

**Weaknesses:** Ackley (f10) and Rastrigin (f9), where the group often
ends in a valley near, but not at, the best one; the max function (f4);
and the noisy quartic (f7), which is worse than in Mating Call.

**Encore on the CEC functions (10 coordinates).** On CEC 2022 it is 4th
of 13 entries (average rank 6.00), and no entry is significantly better.
It finds the best value on F1, F3, F5 and F11, and does well on F12 and F6.
On blended functions with traps (CEC 2017 F22 and F24) it ends at the best
valley in most runs, where the differential evolution rule is
trapped. It is weakest on:

- **F4 (Rastrigin):** 3.48, against 0.27 for the best entry and about 1.3
  for three others. Runs end one or more valleys away from the best one.
- **F8 (a blend of five functions):** 1.94, where most entries are below
  0.6. Part of the blend (Ackley) is a field of valleys the group cannot
  cross at the end of the run.
- **F10 (a trap):** 81 on average; 24 of 30 runs end in the trap (error
  about 100), and 28 and 30 of 30 with two other sets of seeds. Six
  entries have a lower average.
- **F7 and F2:** F7 is 0.027, where several entries reach 0. On F2 about 1
  run in 6 ends at 3.987, a second minimum of Rosenbrock's valley.

**At 20 coordinates** it is 2nd of 13 (average rank 5.17, behind EA4eig at
4.25 and level with jSObinexpEig, S-LSHADE-DP and NL-SHADE-LBC), again with
no entry significantly better. F10 is no longer a weakness there (22 of 30
runs escape the trap), and F11 is solved in 29 of 30 runs where most entries
are not. F4 (Rastrigin) and F7 stay weak, and F12 joins them.

Behind these limits is a shared trade-off. Hearing neighbours first, as the
sound model does, keeps separate groups apart and protects against traps.
Hearing the best agents from anywhere crosses fields of valleys faster. The
two cannot be mixed in one group: far hearers pull everyone into one valley.
Splitting the group, or switching later in the run, was tried (see above)
and traded one weakness for the other. The rules of the closest relatives
(firefly, fitness-distance ratio) fall on the same line: those that cross
fields of valleys well are trapped, and the one that avoids traps searches
worse.

### Caveats

- The settings were chosen by comparing variants on the classic functions
  (plain, moved and turned) and, from Encore on, on CEC 2017 (Awad et
  al., 2016), so those results are somewhat optimistic. The CEC 2022
  results are free of this, at both 10 and 20 coordinates (the only sizes
  CEC 2022 defines). The start of 18 agents per coordinate, and the CEC
  settings of step 10 ($\kappa$ from 0 to 8, 10% refinement), were designed at
  10 coordinates. A check on CEC 2017
  at 30 coordinates (10 runs per function, 300,000 evaluations) found
  Encore better than Echo on 24 of 29 functions and worse on none
  (Friedman p = $1.5 \times 10^{-6}$), and better than Encore without steps 8 to 10 on
  10 and worse on none (p = 0.0007). There are no published results at 30
  coordinates in this repository to compare with.
- The 20-coordinate result uses one set of seeds. At 10 coordinates, two
  more sets of seeds moved the average rank between 5.50 and 6.17 but not
  the place (4th), and changed F10 a lot (6, 2 and 0 of 30 runs escaping
  the trap), so the F10 result at 20 coordinates may also move with other
  seeds.
- GWO, PSO and GSA are classic methods, not the strongest current ones.
  Their numbers come from a paper, not from runs with the same seeds.
- Several parts are borrowed from existing methods (cited above): the
  difference move and crossover from differential evolution, the echo
  archive from JADE, the success memory, limit rule and shrinking group
  from SHADE and L-SHADE, and the refinement from Igel et al. (2006). What is new is the
  sound model, which decides whom each agent moves relative to and in
  which direction. Its closest relatives choose with similar ingredients;
  swapped in, their rules either tie with it overall or do worse (see
  [Against the rules of its closest relatives](#against-the-rules-of-its-closest-relatives)).

## What changed from Mating Call

Measuring Mating Call showed these problems:

1. **Wasted evaluations.** Its random exploration step was sized by the
   width of the search space. After about 100 of 500 iterations almost
   none of those steps were accepted, so half of all evaluations were
   wasted for most of the run.
2. **Collapse far from the answer.** On the sphere function, by iteration
   250 the agents were spread out by only 0.007 but were still 7.6 away
   from the best point. Every move was a fraction of the distance between
   agents, so after that they could only crawl.
3. **Sensitive to the scale of the function.** Loudness was a linear
   scaling of the function value, so one very bad agent made every other
   agent almost equally loud.
4. **Worse away from the origin.** With the best point moved, results on
   f2, f3, f9, f12 and f13 were 2 to 30 times worse.

Echo keeps the sound model and changes the rest: loudness by rank;
a loudness exponent that rises during the run, in place of the old pull
towards the best agent; steps taken from distances between agents and
echoes, with step size adapted to what works; only some coordinates
moving at a time; and the final refinement. Momentum and the old
exploration and pull terms were removed.

Ideas that were tried and dropped: a direct pull towards the best few
agents (faster on smooth bowls but worse on f14-f23 and on functions with
many valleys), and letting the worst agents leave over time (solves
Rastrigin only because its coordinates are independent, and is worse on
f4, f10, f12 and f13). That was with the classic budget and a group of
30. With the CEC budgets and a group that starts at 180, it helps, and
Encore uses it (step 9).

## References

- Awad, N. H., Ali, M. Z., Suganthan, P. N., Liang, J. J. & Qu, B. Y.
  (2016). *Problem definitions and evaluation criteria for the CEC 2017
  special session and competition on single objective real-parameter
  numerical optimization.* Technical report, Nanyang Technological
  University, Singapore; Jordan University of Science and Technology;
  Zhengzhou University.
- Biedrzycki, R. (2024). Revisiting CEC 2022 ranking: A new ranking
  method and influence of parameter tuning. *Swarm and Evolutionary
  Computation*, 89, 101623.
  [doi:10.1016/j.swevo.2024.101623](https://doi.org/10.1016/j.swevo.2024.101623)
- Brest, J., Sepesy Maučec, M. & Bošković, B. (2017). Single objective
  real-parameter optimization: Algorithm jSO. *2017 IEEE Congress on
  Evolutionary Computation*, 1311-1318.
  [doi:10.1109/CEC.2017.7969456](https://doi.org/10.1109/CEC.2017.7969456)
- Burke, E. K., Kendall, G. & Soubeiga, E. (2003). A tabu-search
  hyperheuristic for timetabling and rostering. *Journal of Heuristics*,
  9(6), 451-470.
  [doi:10.1023/B:HEUR.0000012446.94732.b6](https://doi.org/10.1023/B:HEUR.0000012446.94732.b6)
- Camacho-Villalón, C. L., Dorigo, M. & Stützle, T. (2023). Exposing the
  grey wolf, moth-flame, whale, firefly, bat, and antlion algorithms: six
  misleading optimization techniques inspired by bestial metaphors.
  *International Transactions in Operational Research*, 30(6), 2945-2971.
  [doi:10.1111/itor.13176](https://doi.org/10.1111/itor.13176)
- Demšar, J. (2006). Statistical comparisons of classifiers over multiple
  data sets. *Journal of Machine Learning Research*, 7, 1-30.
  [jmlr.org/papers/v7/demsar06a.html](https://www.jmlr.org/papers/v7/demsar06a.html)
- Derrac, J., García, S., Molina, D. & Herrera, F. (2011). A practical
  tutorial on the use of nonparametric statistical tests as a methodology
  for comparing evolutionary and swarm intelligence algorithms. *Swarm and
  Evolutionary Computation*, 1(1), 3-18.
  [doi:10.1016/j.swevo.2011.02.002](https://doi.org/10.1016/j.swevo.2011.02.002)
- Igel, C., Suttorp, T. & Hansen, N. (2006). A computational efficient
  covariance matrix update and a (1+1)-CMA for evolution strategies.
  *Proceedings of the 8th Annual Conference on Genetic and Evolutionary
  Computation (GECCO 2006)*, 453-460.
  [doi:10.1145/1143997.1144082](https://doi.org/10.1145/1143997.1144082)
- Kenekayoro, P. (2021). A meta-heuristic search algorithm based on
  infrasonic mating displays in peafowls. *Journal of Advances in
  Mathematics and Computer Science*, 36(5), 98-106.
  [doi:10.9734/JAMCS/2021/v36i530366](https://doi.org/10.9734/JAMCS/2021/v36i530366)
- Kennedy, J. & Eberhart, R. (1995). Particle swarm optimization.
  *Proceedings of ICNN'95, International Conference on Neural Networks*,
  4, 1942-1948.
  [doi:10.1109/ICNN.1995.488968](https://doi.org/10.1109/ICNN.1995.488968)
- Kumar, A., Price, K. V., Mohamed, A. W., Hadi, A. A. & Suganthan, P. N.
  (2021). *Problem definitions and evaluation criteria for the CEC 2022
  special session and competition on single objective bound constrained
  numerical optimization.* Technical report, December 2021.
- Mirjalili, S., Mirjalili, S. M. & Lewis, A. (2014). Grey Wolf Optimizer.
  *Advances in Engineering Software*, 69, 46-61.
  [doi:10.1016/j.advengsoft.2013.12.007](https://doi.org/10.1016/j.advengsoft.2013.12.007)
- Niu, P., Niu, S., Liu, N. & Chang, L. (2019). The defect of the Grey Wolf
  optimization algorithm and its verification method. *Knowledge-Based
  Systems*, 171, 37-43.
  [doi:10.1016/j.knosys.2019.01.018](https://doi.org/10.1016/j.knosys.2019.01.018)
- Peram, T., Veeramachaneni, K. & Mohan, C. K. (2003).
  Fitness-distance-ratio based particle swarm optimization. *Proceedings of
  the 2003 IEEE Swarm Intelligence Symposium (SIS'03)*, 174-181.
  [doi:10.1109/SIS.2003.1202264](https://doi.org/10.1109/SIS.2003.1202264)
- Rashedi, E., Nezamabadi-pour, H. & Saryazdi, S. (2009). GSA: a
  gravitational search algorithm. *Information Sciences*, 179(13),
  2232-2248. [doi:10.1016/j.ins.2009.03.004](https://doi.org/10.1016/j.ins.2009.03.004)
- Storn, R. & Price, K. (1997). Differential evolution - a simple and
  efficient heuristic for global optimization over continuous spaces.
  *Journal of Global Optimization*, 11(4), 341-359.
  [doi:10.1023/A:1008202821328](https://doi.org/10.1023/A:1008202821328)
- Tanabe, R. & Fukunaga, A. (2013). Success-history based parameter
  adaptation for differential evolution. *2013 IEEE Congress on
  Evolutionary Computation*, 71-78.
  [doi:10.1109/CEC.2013.6557555](https://doi.org/10.1109/CEC.2013.6557555)
- Tanabe, R. & Fukunaga, A. (2014). Improving the search performance of
  SHADE using linear population size reduction. *2014 IEEE Congress on
  Evolutionary Computation*, 1658-1665.
  [doi:10.1109/CEC.2014.6900380](https://doi.org/10.1109/CEC.2014.6900380)
- Yang, X.-S. (2009). Firefly algorithms for multimodal optimization.
  *Stochastic Algorithms: Foundations and Applications (SAGA 2009)*,
  Lecture Notes in Computer Science, 169-178.
  [doi:10.1007/978-3-642-04944-6_14](https://doi.org/10.1007/978-3-642-04944-6_14)
- Yao, X., Liu, Y. & Lin, G. (1999). Evolutionary programming made faster.
  *IEEE Transactions on Evolutionary Computation*, 3(2), 82-102.
  [doi:10.1109/4235.771163](https://doi.org/10.1109/4235.771163)
- Zhang, J. & Sanderson, A. C. (2009). JADE: adaptive differential
  evolution with optional external archive. *IEEE Transactions on
  Evolutionary Computation*, 13(5), 945-958.
  [doi:10.1109/TEVC.2009.2014613](https://doi.org/10.1109/TEVC.2009.2014613)

## License

MIT; see `LICENSE`. The CEC 2017 and CEC 2022 data files are not included:
they are downloaded from the organisers' repositories on first use.
