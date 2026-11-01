# Sound Intensity Search

A population-based search method for continuous optimisation, inspired by
how peafowl use infrasonic sound in mating displays. Every candidate
solution (agent) makes a sound whose loudness depends on how good it is.
Agents listen, pick the loudest sound they hear, and move relative to it.

Based on: P. Kenekayoro, *A Meta-Heuristic Search Algorithm based on
Infrasonic Mating Displays in Peafowls*, Journal of Advances in Mathematics
and Computer Science 36(5): 98–106, 2021.
[doi:10.9734/JAMCS/2021/v36i530366](https://doi.org/10.9734/JAMCS/2021/v36i530366)

This is version 2. The sound model (steps 1–3 below) follows the paper,
with two changes: loudness comes from an agent's place in the ranking
rather than its raw value, and a loudness exponent `κ` rises during the
run. The rest was reworked to fix problems found in version 1 (see
[What changed from version 1](#what-changed-from-version-1)).

## How it works

The search looks for the lowest value of a function inside lower and upper
limits for each coordinate. It keeps `n` agents `x_1 … x_n`.

### 1. Loudness from fitness

Agents are sorted from best to worst. Loudness falls in equal steps down
that list, so the best agent is loudest and the worst is silent:

```math
p_i = \frac{n - 1 - \text{rank}_i}{n - 1},
\qquad
P_i = \frac{p_i}{\sum_j p_j}
```

(`rank` is 0 for the best agent; agents with equal values share a rank.)
Only the order matters, so one extremely bad agent cannot make every other
agent sound the same.

### 2. Sound weakens with distance

```math
I_{ij} = \frac{P_j^{\kappa}}{4 \pi r_{ij}^2},
\qquad r_{ij} = \lVert x_i - x_j \rVert
```

`κ` says how much loudness counts compared with distance. It rises from 1
to 4 during the run. Early on, an agent mostly hears its near neighbours,
so small groups explore different parts of the space. Later, the best
agents are heard from far away and everyone gathers around them.

### 3. Move relative to the loudest source

Every agent listens to the source it hears loudest, `k = argmax_j I_ij`.
It moves towards that source if the source is fitter and away from it
otherwise, plus an "ambient" term: the difference between a random agent
`x_a` and an echo `x_e` (a random current or past position):

```math
v_i = x_i + F_i \big( \pm (x_k - x_i) + (x_a - x_e) \big)
```

`F_i` is the agent's step size. Adding the difference between two agents
is the basic move of differential evolution (Storn & Price, 1997).

### 4. Only some coordinates are heard

Each coordinate of `v_i` is heard with chance `C_i` (the agent's hearing
rate), and at least one always is. The others stay as they were; this is
the crossover of differential evolution (Storn & Price, 1997). A
coordinate that goes past a limit is put halfway between its old value
and that limit (as in Tanabe & Fukunaga, 2014).

### 5. Keep only improvements

The agent moves to its new point only if that point is better. The place
it leaves becomes an echo. Up to `n` echoes are kept; when there are more,
random ones are forgotten. Keeping replaced points this way comes from
JADE (Zhang & Sanderson, 2009).

### 6. Step size and hearing rate learn from what worked

Each agent draws its own `F_i` and `C_i` around values remembered from
recent successful moves. After each iteration, the values that produced
improvements are averaged into the memory, with bigger improvements
counting more. (This scheme is from Tanabe & Fukunaga, 2013, in the form
used by L-SHADE, Tanabe & Fukunaga, 2014.)

### 7. Refinement

The last 30% of the evaluations are spent differently: the group stops,
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
result of 9e−5; handing the last 30% to the refinement gives 2.5e−20.

A run with `n` agents and `iterations` iterations uses
`n × (iterations + 1)` function evaluations, the same as one evaluation per
agent per iteration.

## Usage

Requires Python 3 and NumPy.

```bash
python entry.py -i 1 -n 1000                 # f1, 1000 iterations, 30 runs
python entry.py -i 9 -n 500 --pop 30 --seed 0
python entry.py -i 5 --kappa 8 --refine 0.2  # change settings
python entry.py --tune 5 9 10 12 -n 500 --samples 40 --runs 5 --seed 0
python benchmark.py                          # reproduce the results below
python benchmark.py --suite cec2022 --dim 10 --save results/cec2022_D10_sound.json
python compare.py results/cec2022_D10_*.json --control sound
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
| `kappa` | 4 | how much loudness counts at the end of the run (starts at 1) |
| `refine` | 0.3 | share of evaluations for the final refinement |
| `archive` | 1.0 | echoes kept, as a multiple of the number of agents |
| `pop_size` | 50 | number of agents |

## Results

All results: the 23 classic test functions of Yao et al. (1999), 30 agents
× 500 iterations (15,030 evaluations), 30 independent runs, seed 0. The
GWO (Grey Wolf Optimizer; Mirjalili et al., 2014), PSO (Particle Swarm
Optimisation; Kennedy & Eberhart, 1995) and GSA (Gravitational Search
Algorithm; Rashedi et al., 2009) values are the published averages from
the Grey Wolf Optimizer paper. Version 1 (commit `e512be8`) was
rerun with the same seeds. Everything for version 2 is reproduced by
`python benchmark.py`.

**Average place** on the 23 functions, out of 4 (lower is better; results
equal to 4 significant figures share a place):

| | all | f1–f7 | f8–f13 | f14–f23 | best on |
|---|---|---|---|---|---|
| GWO | 1.61 | 1.43 | 1.67 | 1.70 | 15 functions |
| **Sound v2** | **1.70** | 2.00 | 2.50 | **1.00** | 12 functions |
| PSO | 2.65 | 3.29 | 2.33 | 2.40 | 6 functions |
| GSA | 2.87 | 3.29 | 3.50 | 2.20 | 5 functions |
| *Sound v1* | *2.30* | *2.86* | *3.00* | *1.50* | *7 functions* |

(The v1 row is v1's own place when compared with the same three methods.)

**One-to-one** (functions won / tied / lost):

| | vs GWO | vs PSO | vs GSA |
|---|---|---|---|
| Sound v2 | 7 / 6 / 10 | 14 / 4 / 5 | 17 / 5 / 1 |
| Sound v1 | 4 / 4 / 15 | 10 / 4 / 9 | 12 / 5 / 6 |

**Per function** (average of 30 runs; "place" is v2's place out of 4):

| | Sound v2 | Sound v1 | GWO | PSO | GSA | place |
|---|---|---|---|---|---|---|
| f1 | 2.5e−20 | 0.0022 | 6.6e−28 | 1.4e−4 | 2.5e−16 | 2 |
| f2 | 0.0036 | 0.20 | 7.2e−17 | 0.042 | 0.056 | 2 |
| f3 | 0.0071 | 52.1 | 3.3e−6 | 70.1 | 897 | 2 |
| f4 | 4.21 | 7.08 | 5.6e−7 | 1.09 | 7.35 | 3 |
| f5 | 35.8 | 42.0 | 26.8 | 96.7 | 67.5 | 2 |
| f6 | **5.7e−20** | 0.0023 | 0.817 | 1.0e−4 | 2.5e−16 | 1 |
| f7 | 0.074 | 0.024 | 0.0022 | 0.123 | 0.089 | 2 |
| f8 | **−12080** | −6980 | −6123 | −4841 | −2821 | 1 |
| f9 | 14.5 | 47.1 | 0.311 | 46.7 | 26.0 | 2 |
| f10 | 2.01 | 3.09 | 1.1e−13 | 0.276 | 0.062 | 4 |
| f11 | 0.0149 | 0.0201 | 0.0045 | 0.0092 | 27.7 | 3 |
| f12 | 0.570 | 1.05 | 0.053 | 0.0069 | 1.80 | 3 |
| f13 | 0.327 | 1.19 | 0.654 | 0.0067 | 8.90 | 2 |
| f14 | **0.998** | 1.164 | 4.042 | 3.627 | 5.860 | 1 |
| f15 | **3.075e−4** | 3.942e−4 | 3.37e−4 | 5.77e−4 | 3.673e−3 | 1 |
| f16 | −1.032 | −1.032 | −1.032 | −1.032 | −1.032 | 1 (tie) |
| f17 | 0.3979 | 0.3979 | 0.3979 | 0.3979 | 0.3979 | 1 (tie) |
| f18 | 3 | 3 | 3 | 3 | 3 | 1 (tie) |
| f19 | −3.863 | −3.863 | −3.863 | −3.863 | −3.863 | 1 (tie) |
| f20 | **−3.322** | −3.318 | −3.287 | −3.266 | −3.318 | 1 |
| f21 | −10.15 | −9.567 | −10.15 | −6.865 | −5.955 | 1 (tie with GWO) |
| f22 | −10.40 | −9.925 | −10.40 | −8.457 | −9.684 | 1 (tie with GWO) |
| f23 | −10.54 | −10.06 | −10.53 | −9.953 | −10.54 | 1 (tie with GSA) |

On f14–f23 version 2 finds the best known value in every one of the 30
runs (standard deviation below 1e−14 on f15–f23).

### With the best point moved and the function turned

Seven of these functions (f1–f4, f9–f11) have their best point at the
origin, and some methods do well partly because they drift towards the
centre of the search space (Niu et al., 2019, show this for GWO). To check that version 2's gains are real, f1–f7
and f9–f13 were also run with the best point moved to a fixed random place
("moved"), and additionally turned by a fixed random angle so that the
coordinates no longer act independently ("moved + turned"). Median of 30
runs (best possible is 0 for all):

| | moved, v1 | moved, v2 | moved + turned, v1 | moved + turned, v2 |
|---|---|---|---|---|
| f1 | 0.0026 | **8.7e−21** | 0.0026 | **7.2e−21** |
| f2 | 5.24 | **0.0011** | 21.8 | **0.37** |
| f3 | 250 | **0.0079** | 246 | **0.0072** |
| f4 | 19.1 | **5.30** | 17.8 | **1.80** |
| f5 | 27.9 | **22.5** | 178 | **23.5** |
| f6 | 0.0027 | **1.5e−20** | 0.0018 | **7.8e−21** |
| f7 | 0.073 | **0.072** | **0.059** | 0.069 |
| f9 | 89.5 | **13.9** | 87.6 | **47.3** |
| f10 | 2.66 | **2.12** | 2.58 | **2.54** |
| f11 | 0.018 | **0.0099** | 0.025 | **0.011** |
| f12 | 3.69 | **0.19** | 5.10 | **0.89** |
| f13 | 38.9 | **0.026** | 0.37 | **4.4e−14** |

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
| **all parts** | **1.70** | 5.0 / 3.9 / 4.6 | – | – |
| listen to a random agent | 1.87 | 4.9 / 3.5 / 3.4 | 16 | 3 |
| listen to the nearest agent (loudness ignored) | 1.91 | 4.4 / 2.9 / 2.9 | 21 | 0 |
| κ fixed at 1 | 1.74 | 4.8 / 3.7 / 3.4 | 10 | 0 |
| never move away | 1.74 | 5.1 / 4.1 / 4.2 | 2 | 7 |
| no echoes | 1.78 | 4.8 / 3.3 / 3.1 | 16 | 1 |
| no refinement | 1.78 | 3.3 / 0.9 / 0.5 | 16 | 1 |

The sound model does real work. Listening to a random agent instead of
the loudest makes results worse on 16 of 47 and better on only 3;
ignoring loudness and listening to the nearest agent is worse on 21 and
better on none. Letting loudness count more as the run goes on (κ rising
from 1 to 4), the echoes and the refinement each help as well.

Moving away from a worse source is roughly neutral in these tests:
without it, results are better on 7 and worse on 2, mostly by small
amounts, but one f15 run gets stuck and the average place drops. It is
kept because it is part of the original model; it is worth revisiting.

Run with `python benchmark.py --ablate random` (or `nearest`, `towards`),
`--kappa 1`, `--archive 0` or `--refine 0`, adding `--suite shifted` or
`--suite rotated`.

### CEC 2022 functions

The settings above were chosen on the classic functions. The 12 CEC 2022
competition functions (Kumar et al., 2021) were not used for that, so
they give a fairer test. All of them are moved and turned, and F6–F12
mix several functions together. Each run has 10 coordinates and 200,000
evaluations (the competition rules), with 50 agents and 30 runs. The
table gives the mean error (distance above the best possible value;
errors below 10⁻⁸ count as 0). +, − and = say whether the full method is
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

These results show how the parts compare, not how good the method is: it
has not yet been compared with strong methods on these functions.

### Strengths and weaknesses

**Strengths:** the low-dimensional functions with several valleys (f14–f23:
best known value in every run), Schwefel (f8: −12080 against a best
possible −12569), and smooth bowls whether or not they are tilted or
stretched (f1, f3, f6). Results hold up when the best point is moved away
from the origin and the function is turned.

**Weaknesses:** Ackley (f10) and Rastrigin (f9), where the group often
ends in a valley near, but not at, the best one; the max function (f4);
and the noisy quartic (f7), which is worse than in version 1.

### Caveats

- The settings were chosen by comparing variants on the classic functions
  (plain, moved and turned), so those results are somewhat optimistic.
  The CEC 2022 results are free of this, but so far only at 10
  coordinates. The CEC 2017 set (Awad et al., 2016) would be another
  independent test.
- The CEC 2022 code is checked at each function's best point, but has
  not yet been compared value for value with the organisers' code.
- GWO, PSO and GSA are classic methods, not the strongest current ones.
  Their numbers come from a paper, not from runs with the same seeds.
- Several parts are borrowed from existing methods (cited above): the
  difference move and crossover from differential evolution, the echo
  archive from JADE, the success memory and limit rule from SHADE and
  L-SHADE, and the refinement from Igel et al. (2006). What is new is the
  sound model, which decides whom each agent moves relative to and in
  which direction.

## What changed from version 1

Measuring version 1 showed these problems:

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

Version 2 keeps the sound model and changes the rest: loudness by rank;
a loudness exponent that rises during the run, in place of the old pull
towards the best agent; steps taken from distances between agents and
echoes, with step size adapted to what works; only some coordinates
moving at a time; and the final refinement. Momentum and the old
exploration and pull terms were removed.

Ideas that were tried and dropped: a direct pull towards the best few
agents (faster on smooth bowls but worse on f14–f23 and on functions with
many valleys), and letting the worst agents leave over time (solves
Rastrigin only because its coordinates are independent, and is worse on
f4, f10, f12 and f13).

## References

- Awad, N. H., Ali, M. Z., Suganthan, P. N., Liang, J. J. & Qu, B. Y.
  (2016). *Problem definitions and evaluation criteria for the CEC 2017
  special session and competition on single objective real-parameter
  numerical optimization.* Technical report, Nanyang Technological
  University, Singapore; Jordan University of Science and Technology;
  Zhengzhou University.
- Demšar, J. (2006). Statistical comparisons of classifiers over multiple
  data sets. *Journal of Machine Learning Research*, 7, 1–30.
  [jmlr.org/papers/v7/demsar06a.html](https://www.jmlr.org/papers/v7/demsar06a.html)
- Derrac, J., García, S., Molina, D. & Herrera, F. (2011). A practical
  tutorial on the use of nonparametric statistical tests as a methodology
  for comparing evolutionary and swarm intelligence algorithms. *Swarm and
  Evolutionary Computation*, 1(1), 3–18.
  [doi:10.1016/j.swevo.2011.02.002](https://doi.org/10.1016/j.swevo.2011.02.002)
- Igel, C., Suttorp, T. & Hansen, N. (2006). A computational efficient
  covariance matrix update and a (1+1)-CMA for evolution strategies.
  *Proceedings of the 8th Annual Conference on Genetic and Evolutionary
  Computation (GECCO 2006)*, 453–460.
  [doi:10.1145/1143997.1144082](https://doi.org/10.1145/1143997.1144082)
- Kenekayoro, P. (2021). A meta-heuristic search algorithm based on
  infrasonic mating displays in peafowls. *Journal of Advances in
  Mathematics and Computer Science*, 36(5), 98–106.
  [doi:10.9734/JAMCS/2021/v36i530366](https://doi.org/10.9734/JAMCS/2021/v36i530366)
- Kennedy, J. & Eberhart, R. (1995). Particle swarm optimization.
  *Proceedings of ICNN'95, International Conference on Neural Networks*,
  4, 1942–1948.
  [doi:10.1109/ICNN.1995.488968](https://doi.org/10.1109/ICNN.1995.488968)
- Kumar, A., Price, K. V., Mohamed, A. W., Hadi, A. A. & Suganthan, P. N.
  (2021). *Problem definitions and evaluation criteria for the CEC 2022
  special session and competition on single objective bound constrained
  numerical optimization.* Technical report, December 2021.
- Mirjalili, S., Mirjalili, S. M. & Lewis, A. (2014). Grey Wolf Optimizer.
  *Advances in Engineering Software*, 69, 46–61.
  [doi:10.1016/j.advengsoft.2013.12.007](https://doi.org/10.1016/j.advengsoft.2013.12.007)
- Niu, P., Niu, S., Liu, N. & Chang, L. (2019). The defect of the Grey Wolf
  optimization algorithm and its verification method. *Knowledge-Based
  Systems*, 171, 37–43.
  [doi:10.1016/j.knosys.2019.01.018](https://doi.org/10.1016/j.knosys.2019.01.018)
- Rashedi, E., Nezamabadi-pour, H. & Saryazdi, S. (2009). GSA: a
  gravitational search algorithm. *Information Sciences*, 179(13),
  2232–2248. [doi:10.1016/j.ins.2009.03.004](https://doi.org/10.1016/j.ins.2009.03.004)
- Storn, R. & Price, K. (1997). Differential evolution – a simple and
  efficient heuristic for global optimization over continuous spaces.
  *Journal of Global Optimization*, 11(4), 341–359.
  [doi:10.1023/A:1008202821328](https://doi.org/10.1023/A:1008202821328)
- Tanabe, R. & Fukunaga, A. (2013). Success-history based parameter
  adaptation for differential evolution. *2013 IEEE Congress on
  Evolutionary Computation*, 71–78.
  [doi:10.1109/CEC.2013.6557555](https://doi.org/10.1109/CEC.2013.6557555)
- Tanabe, R. & Fukunaga, A. (2014). Improving the search performance of
  SHADE using linear population size reduction. *2014 IEEE Congress on
  Evolutionary Computation*, 1658–1665.
  [doi:10.1109/CEC.2014.6900380](https://doi.org/10.1109/CEC.2014.6900380)
- Yao, X., Liu, Y. & Lin, G. (1999). Evolutionary programming made faster.
  *IEEE Transactions on Evolutionary Computation*, 3(2), 82–102.
  [doi:10.1109/4235.771163](https://doi.org/10.1109/4235.771163)
- Zhang, J. & Sanderson, A. C. (2009). JADE: adaptive differential
  evolution with optional external archive. *IEEE Transactions on
  Evolutionary Computation*, 13(5), 945–958.
  [doi:10.1109/TEVC.2009.2014613](https://doi.org/10.1109/TEVC.2009.2014613)
