# Sound Intensity Search

A population-based meta-heuristic for continuous optimisation, inspired by
how peafowl use infrasonic sound in mating displays. Every candidate
solution (agent) "makes a sound" whose power depends on how good it is.
Agents listen, pick the loudest source they hear, and move relative to it.

Based on: P. Kenekayoro, *A Meta-Heuristic Search Algorithm based on
Infrasonic Mating Displays in Peafowls*, Journal of Advances in Mathematics
and Computer Science 36(5): 98–106, 2021.
[doi:10.9734/JAMCS/2021/v36i530366](https://doi.org/10.9734/JAMCS/2021/v36i530366)

## The algorithm

The description below is for minimisation, with a population of `n` agents
`x_1 … x_n` in a box-bounded search space.

### 1. Sound power from fitness

Fitness is scaled to `[0, 1]`, so the best agent is loudest and the worst
is silent. It is then normalised so the powers sum to 1:

```math
p_i = \frac{\text{worst} - f(x_i)}{\text{worst} - \text{best}},
\qquad
P_i = \frac{p_i}{\sum_j p_j}
```

### 2. Sound intensity falls with distance

Sound spreads over a sphere, so the intensity agent `i` hears from agent `j`
is that source's power divided by the area of the sphere:

```math
I_{ij} = \frac{P_j}{4 \pi r_{ij}^2},
\qquad r_{ij} = \lVert x_i - x_j \rVert
```

A loud source far away and a quiet source nearby can sound equally strong.

### 3. Move relative to the loudest source

Each agent picks the neighbour it hears loudest, `k = argmax_j I_ij`. It
moves towards that neighbour if the neighbour is fitter, and away from it
otherwise:

```math
\text{step}_i = \pm \frac{\rho}{100}\,(1 + u)\,(x_k - x_i)
```

`ρ` is the step size in percent, and `u ~ U(0, 1)` is drawn separately for
each dimension.

### 4. Update

```math
v_i \leftarrow m\,v_i + \text{step}_i + \text{explore}_i + \text{pull}_i,
\qquad
x_i' = x_i + v_i
```

- `m v_i` is momentum: a random fraction `m ~ U(0, 0.27)` of the agent's last move.
- `explore_i` is Gaussian noise. Its scale starts at 5.5% of the domain
  width, decays as `(1 − t)^3` over the run (`t` = fraction of the run
  done), and it is applied to half the agents each iteration.
- `pull_i = 2.9 t² u (x_best − x_i)` is an attraction to the best solution
  found so far. It is negligible early on (exploration) and dominant late
  (convergence).
- A coordinate that leaves the domain is placed halfway between its old
  value and the bound it crossed.
- **Greedy acceptance:** the agent moves to `x_i'` only if that improves
  its fitness. Otherwise it stays put and its momentum is reset.

Each agent is evaluated once per iteration, so a run costs
`n × (iterations + 1)` fitness evaluations.

## Usage

Requires Python 3 and NumPy.

```bash
python entry.py -i 1 -n 1000                 # f1, 1000 iterations, 30 runs
python entry.py -i 9 -n 500 --pop 30 --seed 0
python entry.py -i 5 --rho 20 --pull 2.0      # override parameters
python entry.py --tune 5 9 10 12 -n 500 --samples 40 --runs 5 --seed 0
python -m unittest discover tests
```

`-i` selects one of the 23 benchmark functions in
`sound_heuristic/fitness.py`. Each run reports the mean, std, median, best
and worst result, plus the number of fitness evaluations.

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

| Parameter | Default | Meaning |
|---|---|---|
| `rho` | 16 | step towards / away from the neighbour, % of distance |
| `momentum` | 0.27 | upper bound of the fraction of the last move carried forward |
| `exploration` | 0.055 | initial noise scale, fraction of domain width |
| `pull` | 2.9 | strength of attraction to the best solution |
| `pop_size` | 50 | number of agents |

## Results

These results use the 23 classic benchmark functions at the budget of the
Grey Wolf Optimizer paper: 30 agents × 500 iterations, 30 independent runs.
The GWO, PSO and GSA values are the published means from that paper
(Mirjalili et al., 2014).

**Mean rank** across the 23 functions (lower is better):

| | all | f1–f7 | f8–f13 | f14–f23 | best on |
|---|---|---|---|---|---|
| GWO | 1.48 | 1.43 | 1.50 | 1.50 | 16 functions |
| **Sound** | **2.26** | 2.86 | 2.83 | **1.50** | 7 functions |
| PSO | 2.52 | 2.86 | 2.33 | 2.40 | 6 functions |
| GSA | 2.65 | 2.86 | 3.33 | 2.10 | 7 functions |

**Head-to-head** for Sound (win / tie / loss): vs PSO 11 / 4 / 8,
vs GSA 12 / 5 / 6, vs GWO 4 / 4 / 15.

**Per function** (mean of 30 runs; "rank" is Sound's position out of 4):

| | Sound | GWO | PSO | GSA | rank |
|---|---|---|---|---|---|
| f1 | 2.5e-3 | 6.6e-28 | 1.4e-4 | 2.5e-16 | 4 |
| f2 | 0.126 | 7.2e-17 | 0.042 | 0.056 | 4 |
| f3 | 52.1 | 3.3e-6 | 70.1 | 897 | 2 |
| f4 | 7.23 | 5.6e-7 | 1.09 | 7.35 | 3 |
| f5 | 44.2 | 26.8 | 96.7 | 67.5 | 2 |
| f6 | 2.4e-3 | 0.817 | 1.0e-4 | 2.5e-16 | 3 |
| f7 | 0.027 | 0.0022 | 0.123 | 0.089 | 2 |
| f8 | **−7370** | −6123 | −4841 | −2821 | 1 |
| f9 | 41.2 | 0.31 | 46.7 | 26.0 | 3 |
| f10 | 3.00 | 1.1e-13 | 0.276 | 0.062 | 4 |
| f11 | 0.019 | 0.0045 | 0.0092 | 27.7 | 3 |
| f12 | 0.734 | 0.053 | 0.0069 | 1.80 | 3 |
| f13 | 3.25 | 0.654 | 0.0067 | 8.90 | 3 |
| f14 | **1.26** | 4.04 | 3.63 | 5.86 | 1 |
| f15 | 3.9e-4 | 3.4e-4 | 5.8e-4 | 3.7e-3 | 2 |
| f16–f19 | optimum | optimum | optimum | optimum | 1 (tie) |
| f20 | **−3.32** | −3.29 | −3.27 | −3.32 | 1 (tie with GSA) |
| f21 | −9.98 | −10.15 | −6.87 | −5.96 | 2 |
| f22 | −10.0 | −10.40 | −8.46 | −9.68 | 2 |
| f23 | −10.1 | −10.53 | −9.95 | −10.54 | 3 |

**Strengths:** the low-dimensional functions (f14–f23), the deceptive
Schwefel function (f8), and Rosenbrock (f5).

**Weaknesses:** final precision on smooth unimodal functions (f1, f2, f4),
Ackley (f10), and the penalised functions (f12, f13).

### Caveats

- Seven of these functions (f1–f4, f9–f11) have their optimum at the
  origin, which favours algorithms biased towards the centre of the search
  space, such as GWO. When the optimum of f9 and f10 is shifted away from
  the origin, part of Sound's advantage on them disappears. Shifted and
  rotated suites (CEC 2017 / CEC 2022) are a fairer test.
- GWO, PSO and GSA are classic baselines, not the current state of the art
  (e.g. CMA-ES, L-SHADE).
- The parameter defaults were tuned on f5, f9, f10 and f12.
