# Experiments

The exploratory code and raw results behind the research report
*Improving sound intensity search* (`docs/`, published at
[ktarila.com/research/sound-intensity-search](https://ktarila.com/research/sound-intensity-search/)),
mainly its Sections 3.2 to 3.7. Entry numbers below are those of Table 1 in
the report.

These are prototypes, kept as they were run. They are not part of the
`sound_heuristic` package and are not tested. Paths were made relative to
the repository; the CEC data files are downloaded on first use, as for the
main code. In the code, "version 3" is Encore and "version 4" the line of
work in Section 3.7. Results from the package itself (Encore, Echo, the
differential evolution rule, the relatives' rules, the seed checks) are in
`results/`.

## `improve/`: prototypes and the test bench

`lab.py` runs one variant on the stand-in functions and saves results in
the format of `benchmark.py`, so `compare.py` can read them:

- `c5`, `c8`: CEC 2017 F5 and F8 (rotated Rastrigin), standing in for
  CEC 2022 F4;
- `c7`, `c10`, `c12`, `c17`, `c21`, `c22`, `c24`: CEC 2017 guard functions;
- `p0` to `p4`: new instances of the CEC 2022 F8 blend, each with its own
  shift, rotation and coordinate order;
- `q<F>x<k>`: new instance `k` of the CEC 2022 form `F` (see `next/forms.py`).

`python lab.py NAME VARIANT FUNCS... [--runs N] [KEY=VALUE ...]`, where
`VARIANT` is `sound` or a prototype class such as `leks.Leks`. The
`queue_*.sh` scripts are the runs of each round; `run_*.py` add a prototype
to `benchmark.py` as an `--ablate` choice for runs on the whole of CEC 2017.

| Module | What it is | Entries |
|---|---|---|
| `hyper3.py`, `hyper4.py` | choosers between hearing rules (hyper-heuristics) | 9, 10 |
| `shrink.py` | the group that shrinks | 11 to 13 |
| `hearing.py`, `htrace.py` | floors on the hearing rate; trace of the learned rate | 16, 26, 28, 29 |
| `masking.py` | the agent that leaves is the one most drowned out | 17 |
| `crossing.py`, `trap.py`, `trace.py` | when and where runs fall into the F22 trap | 18 |
| `humans.py` | hearing modelled on human hearing | 19, 51 |
| `roulette.py` | less exact hearing | 20, 21 |
| `waves.py` | superposition and Doppler | 22, 23 |
| `hop.py` | whole hops | 24 |
| `wide.py` | some agents hear widely | 27 |
| `reach.py` | sound that carries further late | 30 |
| `flat.py` | equal picks among the loudest | 31 |
| `leks.py`, `alloc_diag.py`, `halfcheck.py` | infrasound, leks, the chooser between leks, the switch at 10%, why splitting fails | 32 to 35, 38, 39, 52 |
| `turn.py` | ears that turn with the group | 36 |
| `echo.py`, `echo_diag.py` | echolocation | 37 |
| `pbest.py`, `run_pbest.py` | the differential evolution rule (first form) | 45 |
| `parts.py` | the error on an F8 stand-in split into its five parts | Section 3.4 |
| `offcheck.py`, `repro.py` | checks that a prototype with its change switched off reproduces the baseline exactly | Section 2.3 |
| `smoke.py` | a quick look at a prototype on a few seeds | |

## `next/`: Section 3.7

`v4.py` (the population CMA-ES endgame, entry 40), `valley.py` (Valley
Hopper, entries 41 to 43), `switch_hop.py` (Encore first, then the hop,
entry 44), `forms.py` (new instances of the CEC 2022 forms) and `trace.py`
(where failing runs go wrong, with its output in `trace*.txt`).

## Results

- `v4/`, `v5/`: results of the stand-in bench rounds and of the runs on the
  whole of CEC 2017 (`c17_*`, `full30_*`); file names give the variant.
  `*.log` files are the printed summaries.
- `v6/`: CEC 2017 at 30 coordinates (Echo, Encore after step 9, Encore)
  and the differential evolution rule in its two forms.
- `v7/`: the switch to infrasound at 10% on the whole of CEC 2017 (entry 38).
- `cec2022_check/`: the CEC 2022 functions of `sound_heuristic/cec2022.py`
  checked against the organisers' C code on the same points
  (`driver.cpp`, `compare_c.py`, output in `compare_c.txt`).
- `queue_d30.sh`: the run script of the 30-coordinate check.
