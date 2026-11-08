// Text for the web page: the three versions, the building blocks of the
// functions, and what is known about each function in the three groups
// (CEC 2022, CEC 2017, the classic 23).
//
// Only facts that were checked are stated. Where an origin could not be
// checked (Zakharov, Levy, Katsuura, HGBat, bent cigar, discus, ellipsoid, the
// expanded Griewank-Rosenbrock and Schaffer forms, several classic functions),
// none is given. Names, groups and building blocks of CEC 2017 and the classic
// functions come from the code (docs/meta.js, written by docs/make_text.py).
window.SOUND_TEXT = {

  versions: [
    {
      id: 1,
      name: "Mating Call",
      named: "The method is based on the infrasonic mating displays of peafowl. Every agent calls out, louder the better it is, and the others move towards the loudest call they hear, or away from it if it is worse.",
      short: ["Loudness from the raw function value", "Moves towards or away from the loudest agent, plus momentum, random kicks and a pull to the best", "Keeps a move only if it helps"],
      tagline: "Agents sound off, neighbours listen, and everyone is pulled towards the best.",
      origin: "The first form of the method, as in the 2021 paper's code (commit b703cac).",
      phases: [["Group search, every round", 100]],
      each_round: [
        "Every agent makes a sound. Its loudness is its function value scaled between the worst agent in the group (silent) and the best (loudest).",
        "Every agent hears every other agent at an intensity that falls with the square of the distance. It listens to the loudest one.",
        "It moves towards that agent if that agent is better, and away from it if not. The move is 16% to 32% of the distance, with a random factor for each coordinate.",
        "Three things are added to the move: momentum (a random share, up to 27%, of its last move), a random kick for about half of the agents (a Gaussian kick that shrinks to nothing by the end of the run), and a pull towards the best agent that grows as the run goes on.",
        "The agent keeps the new point only if it is better than where it was."
      ],
      here: {
        two: "30 agents, 165 rounds (about 5,000 evaluations).",
        real: {cec2022: "50 agents, 4,000 rounds (200,000 evaluations).", cec2017: "50 agents, 2,000 rounds (100,000 evaluations).", classic: "30 agents, 500 rounds (15,030 evaluations)."}
      },
      problem: [
        "Wasted evaluations. The random kicks were sized by the width of the search space. After about 100 of 500 rounds almost none were accepted, so half of all evaluations were wasted.",
        "It collapsed far from the answer. On the sphere function the agents were spread by only 0.007 yet still 7.6 away from the best point.",
        "It depended on the scale of the function. Loudness was a straight scaling of the function value, so one very bad agent made all the others sound nearly the same.",
        "It was worse away from the origin. With the best point moved, results on five functions were 2 to 30 times worse."
      ]
    },
    {
      id: 2,
      name: "Echo",
      named: "Each move gets its random push from echoes: places that agents have left behind. The gap between a random agent and an echo sets the size and direction of the push, so steps follow the spread of the group.",
      short: ["Loudness by rank; the exponent κ rises from 1 to 4", "An echo push, learned step sizes, only some coordinates move", "The last 30% refines the best point alone"],
      tagline: "Loudness by rank, steps that learn from what worked, and a final polish.",
      origin: "Keeps the sound model, replaces the rest (commit 9ecb68f).",
      phases: [["Group search", 70], ["Refinement", 30]],
      each_round: [
        "Loudness comes from rank only: the best agent is loudest, the worst silent, in equal steps. One extremely bad agent can no longer flatten everyone else.",
        "A loudness exponent κ rises during the run (1 to 4 here). Early on an agent mostly hears its neighbours, so small groups explore different places. Later the best agents are heard from far away and the group gathers.",
        "An agent moves towards the loudest source it hears if that source is better, away if not, plus a random push: the gap between a random agent and an echo, a place some agent left earlier. Adding gaps between agents is the basic move of differential evolution.",
        "Only some coordinates move each time. The step size and the share of coordinates that move are learned from recent successful moves (the memory scheme of SHADE and L-SHADE).",
        "Improving moves are kept; the place left behind becomes an echo.",
        "In the last 30% of the evaluations the group stops and the best agent improves its own point alone, with a small self-adapting random search (a (1+1)-CMA-ES)."
      ],
      here: {
        two: "30 agents all the way, κ from 1 to 4, 30% refinement, no restarts, no shrinking.",
        real: {cec2022: "50 agents, same settings.", cec2017: "50 agents, same settings.", classic: "30 agents, same settings."}
      },
      problem: [
        "One group for the whole run. If it settles in a wrong valley it stays there.",
        "Every agent always turns to the loudest source, so later in the run nearly all of them move along almost the same line.",
        "The group size is fixed, so late in the run evaluations still go to every agent, not only to the best few."
      ]
    },
    {
      id: 3,
      name: "Encore",
      named: "When the search stops improving, the group plays again: it starts from new random places and keeps the best point found so far.",
      short: ["Everything in Echo", "Restarts when stuck; on the CEC functions the group shrinks", "After 10% of the run it hears a random loud agent, not always the loudest"],
      tagline: "Echo that starts again when stuck, shrinks its group, and hears less exactly.",
      origin: "Echo plus three changes (steps 8 to 10 in the README).",
      phases: [["Group search: restarts, group shrinks", 90], ["Refinement", 10]],
      each_round: [
        "Everything in Echo still happens each round: rank loudness, towards or away from the loudest source, an echo-based push, learned step sizes.",
        "Restart when stuck: if the group's best value has not really improved for 10% of all evaluations (or every agent ends up equal), the group starts again from new random places. The best point so far is kept.",
        "A shrinking group (CEC functions): it starts with 18 agents per coordinate and shrinks evenly to 4. Early on many agents spread over many valleys; later the evaluations go to the few best (the schedule of L-SHADE).",
        "Less exact hearing: for the first 10% of each group search every agent turns to the loudest source. After that it picks a source at random, with a chance proportional to the square of its loudness. The loudest is still the most likely, but fainter ones are tried too.",
        "On the long CEC runs, κ rises from 0 to 8 and the refinement gets 10% of the evaluations instead of 30%. On the classic functions the group stays at 30 agents, κ rises from 1 to 4 and the refinement keeps 30%."
      ],
      here: {
        two: {cec2022: "36 agents shrinking to 4, κ from 0 to 8, 10% refinement.", cec2017: "36 agents shrinking to 4, κ from 0 to 8, 10% refinement.", classic: "30 agents, no shrinking, κ from 1 to 4, 30% refinement (the classic settings), with restarts and less exact hearing."},
        real: {cec2022: "180 agents shrinking to 4, κ from 0 to 8, 10% refinement.", cec2017: "180 agents shrinking to 4, κ from 0 to 8, 10% refinement.", classic: "30 agents, no shrinking, κ from 1 to 4, 30% refinement."}
      },
      problem: [
        "It cannot mix the two kinds of hearing. Hearing neighbours first protects against traps; hearing the best from anywhere crosses fields of valleys faster. Splitting the group, or switching between the two mid-run, each traded one weakness for the other.",
        "It is weakest on fields of regular valleys (CEC 2022 F4, F8) and on the trap in CEC 2022 F10."
      ]
    }
  ],

  // Building blocks in plain words. "origin" only where it was checked.
  parts: {
    "Zakharov": {
      plain: "Squares of the coordinates plus a weighted sum raised to the second and fourth power. It has no local minima. The fourth-power term makes the surface very steep across one narrow strip and shallow along it.",
      origin: null
    },
    "Rosenbrock": {
      plain: "A long, narrow, curved valley with an almost flat floor. With two coordinates it has one minimum; with ten, a second, shallower valley bottom exists.",
      origin: "Howard H. Rosenbrock, 1960, The Computer Journal 3(3), 175-184. Also called the banana function."
    },
    "Schaffer F7": {
      plain: "Concentric ripples: the value depends on the distance between neighbouring pairs of coordinates through a sine that oscillates faster nearer the centre. Many ring-shaped valleys around the lowest point.",
      origin: "Named after J. D. Schaffer."
    },
    "Schaffer F6": {
      plain: "Concentric ripples whose height fades only slowly with distance, so the lowest point is surrounded by many rings of valleys.",
      origin: "Named after J. D. Schaffer."
    },
    "Rastrigin": {
      plain: "A bowl with a regular grid of valleys cut into it by a cosine. Highly multimodal, with regularly spaced local minima. When the function is turned, the valleys no longer line up with the coordinate axes.",
      origin: "Proposed by L. A. Rastrigin in 1974 for two coordinates and later extended to any number of them (usually cited as Mühlenbein, Schomisch and Born, 1991; source: Wikipedia)."
    },
    "Non-continuous Rastrigin": {
      plain: "Rastrigin with a rounding step that would make it non-continuous. In the organisers' C code the step changes values that are overwritten straight away, so the function computed is plain Rastrigin (this port copies that).",
      origin: null
    },
    "Levy": {
      plain: "A gentle bowl with sine terms that add many shallow valleys. In CEC 2017 its best point lies at z = 1 rather than at the shift.",
      origin: null
    },
    "Bent cigar": {
      plain: "One coordinate counts a million times less than the others, so the valley is a long thin cigar. Only one minimum, but hard to follow for methods that move along the axes.",
      origin: null
    },
    "Discus": {
      plain: "The opposite of the bent cigar: one coordinate counts a million times more than the others.",
      origin: null
    },
    "Ellipsoid": {
      plain: "Every coordinate is weighted differently, from 1 up to a million, so the valley is far wider in some directions than in others. Only one minimum.",
      origin: null
    },
    "HGBat": {
      plain: "A valley that follows the directions where the sum of squares equals the square of the sum. It shares its second term with HappyCat, and its valley is narrow and curved.",
      origin: "Appears in the CEC 2014 set as function 14."
    },
    "HappyCat": {
      plain: "A ring-shaped valley around the sphere where the sum of squares equals the number of coordinates; the lowest point sits on the ring.",
      origin: "Beyer and Finck, 2012, in Parallel Problem Solving from Nature XII (pp. 367-376), as a function where well-known direct search methods fail."
    },
    "Katsuura": {
      plain: "A product of terms built from 32 sawtooth levels, so the surface is rough at every scale it resolves and has no smooth slope to follow.",
      origin: null
    },
    "Weierstrass": {
      plain: "A sum of 21 cosines whose frequencies grow threefold and whose sizes halve each time: a surface that is rough at fine scales, with many small valleys.",
      origin: null
    },
    "Ackley": {
      plain: "A nearly flat outer region with a large hole at the centre, covered with small local minima from a cosine term. Easy to get trapped in for hill-climbing methods.",
      origin: "David H. Ackley, 1987, A Connectionist Machine for Genetic Hillclimbing (Kluwer)."
    },
    "Schwefel": {
      plain: "A sum of -z sin(sqrt|z|): many valleys, with the lowest far from the centre, near the edge of the usual range of -500 to 500 (at about 421 in every coordinate).",
      origin: "Attributed to H.-P. Schwefel, Numerical Optimization of Computer Models (Wiley, 1981)."
    },
    "Griewank": {
      plain: "A gentle bowl with a product of cosines that adds many small, regularly placed valleys.",
      origin: "A. O. Griewank, 1981, Journal of Optimization Theory and Applications 34(1), 11-39."
    },
    "Griewank-Rosenbrock": {
      plain: "Griewank's function applied to the terms of Rosenbrock's: a long curved valley covered in small ripples.",
      origin: null
    },
    "Lunacek bi-Rastrigin": {
      plain: "The smaller of two bowls plus a Rastrigin cosine, so there are two funnels of valleys. The lowest point is in one of them; the floor of the other is higher by the number of coordinates (10 here).",
      origin: null
    },
    // classic functions
    "Sphere": {
      plain: "The sum of the squares of the coordinates: a smooth round bowl with one minimum.",
      origin: null
    },
    "Schwefel 2.22": {
      plain: "The sum of the absolute values of the coordinates plus their product. It has a sharp corner at the minimum, so it is not smooth there.",
      origin: null
    },
    "Schwefel 1.2": {
      plain: "The sum of the squares of the running totals of the coordinates. The coordinates are tied together, so the valley is narrow and runs diagonally.",
      origin: null
    },
    "Schwefel 2.21": {
      plain: "The largest absolute value among the coordinates. The surface is a pyramid with flat sides: it shrinks only when the single largest coordinate shrinks.",
      origin: null
    },
    "Step": {
      plain: "The sum of (x + 0.5) squared, as in Mirjalili's code, so the best point is every coordinate at -0.5. Yao et al. round each term down, which gives flat steps; say which form you use when comparing.",
      origin: null
    },
    "Quartic with noise": {
      plain: "A weighted sum of fourth powers plus a random number between 0 and 1, new at every evaluation. A point's value changes each time it is measured.",
      origin: null
    },
    "Schwefel 2.26": {
      plain: "A sum of -x sin(sqrt|x|): many valleys, with the lowest near the edge of the range, at about 420.97 in every coordinate, and a best value of -418.9829 per coordinate.",
      origin: "Attributed to H.-P. Schwefel, Numerical Optimization of Computer Models (Wiley, 1981)."
    },
    "Penalized 1": {
      plain: "A wavy sine surface inside a box with a steep penalty wall outside it. The best point is every coordinate at -1.",
      origin: null
    },
    "Penalized 2": {
      plain: "Like penalized 1, with faster sine waves and a different box. The best point is every coordinate at 1.",
      origin: null
    },
    "Shekel's foxholes": {
      plain: "Two coordinates. Twenty-five narrow wells on a 5 by 5 grid, 16 apart, between -32 and 32; the deepest, at (-32, -32), has the value 0.998.",
      origin: null
    },
    "Kowalik": {
      plain: "Four coordinates. The squared error of fitting a model with four parameters to 11 measured values. The best value is 0.0003075.",
      origin: null
    },
    "Six-hump camel": {
      plain: "Two coordinates. A smooth surface with six local minima, two of them the lowest.",
      origin: "Properties as listed in the Virtual Library of Simulation Experiments (Surjanovic and Bingham)."
    },
    "Branin": {
      plain: "Two coordinates. A curved valley with three separate lowest points, all with the value 0.397887.",
      origin: "The Virtual Library of Simulation Experiments cites Dixon and Szego (1978) for it."
    },
    "Goldstein-Price": {
      plain: "Two coordinates. A surface of steep walls with several local minima; the lowest, 3, is at (0, -1).",
      origin: "The Virtual Library of Simulation Experiments cites Dixon and Szego (1978) for it."
    },
    "Hartman 3": {
      plain: "Three coordinates. Four overlapping smooth dips, with four local minima.",
      origin: null
    },
    "Hartman 6": {
      plain: "Six coordinates. Four overlapping smooth dips, in the same form as Hartman 3.",
      origin: null
    },
    "Shekel 5": {
      plain: "Four coordinates. Five narrow dips of different depths; the deepest is at (4, 4, 4, 4).",
      origin: null
    },
    "Shekel 7": {
      plain: "Four coordinates. Seven narrow dips of different depths; the deepest is at (4, 4, 4, 4).",
      origin: null
    },
    "Shekel 10": {
      plain: "Four coordinates. Ten narrow dips of different depths; the deepest is at (4, 4, 4, 4).",
      origin: null
    }
  },

  groups: {
    "Basic": "One function, moved so its lowest point is not at the centre and, except for F3, turned by a random rotation so the coordinates are tangled together.",
    "Hybrid": "After the move, turn and a shuffle of the coordinates, the coordinates are split into parts and each part is a different function. The value is the sum of the parts.",
    "Composition": "Several functions, each with its own lowest point and a bias added. The value is a weighted average with weights that fall with the distance from each point, so the surface has one valley per function. The overall lowest point is the first function's; the others are decoys with a higher bottom.",
    "Unimodal": "Moved so the lowest point is not at the centre and turned by a random rotation. With a single valley, these functions test how fast a method moves rather than whether it avoids traps.",
    "Simple multimodal": "A single function moved so its lowest point is not at the centre and turned by a random rotation, with many valleys.",
    "Multimodal, many local minima": "One of the classic functions with many local minima, in 30 coordinates. Not moved or turned: the best point sits on a coordinate axis or at a simple place.",
    "Multimodal, few local minima": "One of the classic functions with only a few local minima, in 2 to 6 coordinates."
  },

  suites: {
    cec2022: {
      label: "CEC 2022", short: "12 functions · test set", order: ["Basic", "Hybrid", "Composition"],
      title: "CEC 2022 single-objective functions",
      blurb: "12 functions from the CEC 2022 competition on single-objective optimisation. The test set: Encore was never tuned on them.",
      intro: "The test set. These are the 12 functions of the CEC 2022 competition on single-objective, bound-constrained numerical optimisation (Kumar et al., 2021): five basic ones (F1 to F5), three hybrids (F6 to F8) and four compositions (F9 to F12). Each is defined for 10 and 20 coordinates and every coordinate lies between -100 and 100. At 10 coordinates a run gets 200,000 evaluations, at 20 it gets 1,000,000. The pages below are for 10 coordinates; the results at 20 are on the Strengths and limits page. The error is the function value minus its best possible value, and errors up to 1e-8 count as zero. Encore was designed on CEC 2017 and never tuned on these functions, so they are a fair test. (CEC 2022 also ran other competitions, for example one on dynamic multimodal optimisation; those are different problems and are not used here.)",
      compareHead: "Best of 12 entries", placeHead: "Encore place of 13",
      dimText: "10 coordinates", evalsText: "200,000 evaluations", rangeText: "-100 to 100",
      realTitle: "The real problem: ten coordinates"
    },
    cec2017: {
      label: "CEC 2017", short: "29 functions · design set", order: ["Unimodal", "Simple multimodal", "Hybrid", "Composition"],
      title: "CEC 2017 functions, the design set",
      blurb: "29 functions from the CEC 2017 competition. The design set: the settings of Encore were chosen on them.",
      intro: "The design set: the settings of Encore were chosen on these functions, so their results are somewhat optimistic. This is the CEC 2017 competition on single-objective real-parameter numerical optimisation (Awad et al., 2016): 30 functions of which the organisers withdrew F2, leaving 29. Each is shown at 10 coordinates, with every coordinate between -100 and 100 and 100,000 evaluations per run. The best value of Fk is 100k, and the error is the value minus that. The comparison column is the usual differential evolution rule (the L-SHADE form) in place of listening, with everything else the same (see the README).",
      compareHead: "DE rule (L-SHADE form)", placeHead: "Encore against the DE rule",
      dimText: "10 coordinates", evalsText: "100,000 evaluations", rangeText: "-100 to 100",
      realTitle: "The real problem: ten coordinates"
    },
    classic: {
      label: "Classic 23", short: "f1 to f23 · first benchmark", order: ["Unimodal", "Multimodal, many local minima", "Multimodal, few local minima"],
      title: "The 23 classic functions",
      blurb: "The 23 test functions of Yao et al. (1999), the first benchmark, with published results for GWO, PSO and GSA to compare.",
      intro: "The first benchmark, used for Mating Call and Echo. These are the 23 test functions of Yao, Liu and Lin (1999), as used in the Grey Wolf Optimizer paper (Mirjalili et al., 2014): f1 to f7 have one valley, f8 to f13 have many local minima, f14 to f23 have only a few. f1 to f13 have 30 coordinates; f14 to f23 have 2 to 6. A run is 30 agents for 500 rounds (15,030 evaluations), the effort of the Grey Wolf paper. The comparison columns are the averages published in that paper for the Grey Wolf Optimizer (GWO), Particle Swarm Optimisation (PSO) and the Gravitational Search Algorithm (GSA); they are not run with the same seeds. Shown here as errors, with 30 runs for the versions.",
      compareHead: "Best of GWO, PSO, GSA", placeHead: "Encore place of 4",
      dimText: null, evalsText: "15,030 evaluations", rangeText: null,
      realTitle: "The real problem"
    }
  },

  // Per function: history and, where useful, a note. CEC 2022 also has parts
  // (here) and a "look" line; the other groups take parts from docs/meta.js.
  functions: {
    cec2022: {
      1: {
        name: "Zakharov", group: "Basic", bias: 300, also2017: "F3",
        parts: [["Zakharov", "all coordinates"]],
        history: "Zakharov is a standard test function with no local minima, so it checks how fast a method moves along a narrow, steep-sided valley rather than whether it avoids traps. I did not find its original source. It is F3 in CEC 2017.",
        look: "A single narrow strip. All three versions find the bottom; Mating Call takes the longest."
      },
      2: {
        name: "Rosenbrock", group: "Basic", bias: 400, also2017: "F4",
        parts: [["Rosenbrock", "all coordinates"]],
        history: "Introduced by Howard H. Rosenbrock in 1960 in a paper on an automatic method for finding the greatest or least value of a function, and known as the banana function. It is F4 in CEC 2017.",
        look: "The floor of the curved valley is almost flat, so progress slows on the way along it. In ten coordinates a second valley bottom (error 3.987) exists, and 5 of 30 runs of Encore end there."
      },
      3: {
        name: "Schaffer F7", group: "Basic", bias: 600, also2017: "F6",
        parts: [["Schaffer F7", "all coordinates"]],
        history: "Named after J. D. Schaffer. In the organisers' code, which this repository follows, it is shifted but not turned. It is F6 in CEC 2017.",
        look: "Rings of ripples around the centre. Agents have to cross many ridges, but the rings point towards the centre."
      },
      4: {
        name: "Rastrigin", group: "Basic", bias: 800, also2017: "F5 and F8",
        parts: [["Rastrigin", "all coordinates"]],
        history: "Proposed by L. A. Rastrigin in 1974 for two coordinates and later extended to any number (usually cited as Mühlenbein, Schomisch and Born, 1991; source: Wikipedia). The competition reports F4 as the non-continuous version, but in the organisers' code the step that would make it non-continuous has no effect, so it is plain Rastrigin. It is F5 and F8 in CEC 2017.",
        look: "A regular field of valleys. In two coordinates the groups cross it; in ten, every run of Encore ends one to six valleys from the best."
      },
      5: {
        name: "Levy", group: "Basic", bias: 900, also2017: "F9",
        parts: [["Levy", "all coordinates"]],
        history: "I did not find the original source of this function. It is F9 in CEC 2017.",
        look: "Shallow ripples over a bowl. Encore solves it in every run."
      },
      6: {
        name: "Hybrid of three", group: "Hybrid", bias: 1800, also2017: null,
        parts: [["Bent cigar", "40% of the coordinates"], ["HGBat", "40%"], ["Rastrigin", "20%"]],
        history: "CEC 2017 has the same kind of function (F11 to F20). Here a long thin valley, a narrow curved valley and a field of valleys are added together, each in its own share of the coordinates.",
        look: "One group of coordinates is a field of valleys, the others are valleys that are hard to follow. No run of Encore reaches zero; the average is 0.098."
      },
      7: {
        name: "Hybrid of six", group: "Hybrid", bias: 2000, also2017: null,
        parts: [["HGBat", "10%"], ["Katsuura", "20%"], ["Ackley", "20%"], ["Rastrigin", "20%"], ["Schwefel", "10%"], ["Schaffer F7", "20%"]],
        history: "Six parts, so almost every coordinate belongs to a different kind of terrain. In the organisers' code the Schaffer F7 part reads the first coordinates of the shuffled vector rather than its own, and this repository copies that.",
        look: "Several entries reach 0 in every run; Encore reaches 0 in 7 of 30 runs and comes close in most of the rest."
      },
      8: {
        name: "Hybrid of five", group: "Hybrid", bias: 2200, also2017: null,
        parts: [["Katsuura", "30%"], ["HappyCat", "20%"], ["Griewank-Rosenbrock", "20%"], ["Schwefel", "10%"], ["Ackley", "20%"]],
        history: "The hardest function for this method. Part of it (Ackley) is a field of valleys the group cannot cross at the end of the run, and it also stalls on the far side of HappyCat's ring.",
        look: "No run of Encore reaches zero. Most competition entries average under 0.6; Encore averages 1.94."
      },
      9: {
        name: "Composition of five", group: "Composition", bias: 2300, also2017: null,
        parts: [["Rosenbrock", "sigma 10, bias 0"], ["Ellipsoid", "sigma 20, bias 200"], ["Bent cigar", "sigma 30, bias 300"], ["Discus", "sigma 40, bias 100"], ["Ellipsoid", "sigma 50, bias 400, not turned"]],
        history: "CEC 2017 has composition functions too (F21 to F30). The true lowest point is Rosenbrock's centre; the other four centres are decoys with a higher floor.",
        look: "Every run of Encore ends at 229.3, as do most competition entries. The average of EA4eig, 185.5, is below that, so some of its runs must find a lower point."
      },
      10: {
        name: "Composition of three", group: "Composition", bias: 2400, also2017: null,
        parts: [["Schwefel", "sigma 20, bias 0"], ["Rastrigin", "sigma 10, bias 200"], ["HGBat", "sigma 10, bias 100"]],
        history: "The true lowest point is the Schwefel centre. The HGBat centre is a decoy whose floor lies 100 above it, and it traps most runs.",
        look: "24 of 30 runs of Encore end in the decoy (error about 100), and 28 and 30 of 30 with two other sets of seeds. Six entries have a lower average."
      },
      11: {
        name: "Composition of five", group: "Composition", bias: 2600, also2017: null,
        parts: [["Schaffer F6", "sigma 20, bias 0"], ["Schwefel", "sigma 20, bias 200"], ["Griewank", "sigma 30, bias 300"], ["Rosenbrock", "sigma 30, bias 400"], ["Rastrigin", "sigma 20, bias 200"]],
        history: "Five functions blended, the first (Schaffer F6) being the true lowest point.",
        look: "Encore solves it in every run."
      },
      12: {
        name: "Composition of six", group: "Composition", bias: 2700, also2017: null,
        parts: [["HGBat", "sigma 10, bias 0"], ["Rastrigin", "sigma 20, bias 300"], ["Schwefel", "sigma 30, bias 500"], ["Bent cigar", "sigma 40, bias 100"], ["Ellipsoid", "sigma 50, bias 400"], ["Schaffer F6", "sigma 60, bias 200"]],
        history: "Six functions blended, with the widest decoys. The first (HGBat) is the true lowest point.",
        look: "Encore ends between 158.6 and 159.4 in all 30 runs and is 2nd of 13; the best entry, EA4eig, averages 147.4."
      }
    },

    // CEC 2017: history by function; hybrids and compositions share a text.
    cec2017: {
      1: {history: "Bent cigar on its own: one valley, long and thin. In CEC 2022 it appears only as a part of other functions (F6, F9, F12)."},
      3: {history: "Zakharov, which has no local minima. It is the same function as CEC 2022 F1."},
      4: {history: "Rosenbrock (Rosenbrock, 1960). It is the same function as CEC 2022 F2."},
      5: {history: "Rastrigin: a regular field of valleys. It is the same function as CEC 2022 F4.",
          note: "On F5 and F8 the differential evolution rule does better than listening (error 2.3 against 3.3). This fits the design: pulling towards a few of the best agents from anywhere crosses a regular field of valleys more easily."},
      6: {history: "Schaffer F7: rings of ripples around the centre. It is the same function as CEC 2022 F3."},
      7: {history: "Lunacek's bi-Rastrigin, in the code as the smaller of two bowls plus a Rastrigin cosine, so there are two funnels of valleys. It is not in CEC 2022."},
      8: {history: "Listed as the non-continuous Rastrigin. In the organisers' C code, and in this port, the step that makes it non-continuous changes values that are overwritten straight away, so the function computed is plain Rastrigin. It is the same function as CEC 2022 F4.",
          note: "On F5 and F8 the differential evolution rule does better than listening (error 2.3 against 3.3)."},
      9: {history: "Levy. Its best point is at z = 1 rather than at the shift, so the page finds it by search. It is the same function as CEC 2022 F5."},
      10: {history: "Schwefel: many valleys, the lowest near the edge of the range.",
           note: "The differential evolution rule does better here (error 43 and 57 against 99), as it does on Rastrigin."},
      12: {note: "Listening beats the differential evolution rule on this blended function."},
      18: {note: "Listening beats the differential evolution rule on this blended function."},
      22: {note: "A blend of Rastrigin, Griewank and Schwefel. A run is trapped when it ends in the valley of the wrong function (error about 100). Encore averages 21; the differential evolution rule is trapped in almost every run (93 and 100)."},
      24: {note: "A blend of four functions. Encore averages 111 (100 is the best valley); the differential evolution rule averages 269 and 292."}
    },

    // classic: history by function
    classic: {
      1: {history: "The simplest bowl, f1 of Yao et al. (1999). It checks whether a method can walk down a smooth slope and then settle exactly.",
          note: null},
      2: {history: "f2 of Yao et al. (1999). The sharp corner at the minimum, where the surface is not smooth, favours methods that do not rely on slopes."},
      3: {history: "f3 of Yao et al. (1999). Because the running totals link all coordinates, a method that changes one coordinate at a time makes slow progress along the narrow diagonal valley."},
      4: {history: "f4 of Yao et al. (1999), a 'max' function. The value changes only when the largest coordinate changes, which gives a method little to follow."},
      5: {history: "Rosenbrock (Rosenbrock, 1960), f5 of Yao et al. (1999) in 30 coordinates. It is F4 in CEC 2017 and F2 in CEC 2022. The long curved valley has a nearly flat floor, so every method slows down on it."},
      6: {history: "f6 of Yao et al. (1999), in the form used in Mirjalili's code, so the best point is at -0.5 in every coordinate."},
      7: {history: "f7 of Yao et al. (1999). The value changes every time a point is measured, so a result is partly luck."},
      8: {history: "Schwefel's function, f8 of Yao et al. (1999). The lowest valley lies near the edge of the range, far from the next best valleys. It is F10 in CEC 2017.",
          note: "In the README Echo averaged -12080 against a best possible -12569.5, while the three published methods averaged -6123, -4841 and -2821. Errors are shown here, so those are far apart in the table."},
      9: {history: "Rastrigin, f9 of Yao et al. (1999). It is F4 in CEC 2022 and F5 in CEC 2017.",
          note: "Rastrigin's regular field of valleys is a weakness: the group often ends in a valley near, but not at, the best."},
      10: {history: "Ackley's function, f10 of Yao et al. (1999). The group often ends in a valley near, but not at, the best.",
           note: "Along with Rastrigin, this is a function where the group often ends in a valley near the best."},
      11: {history: "Griewank's function, f11 of Yao et al. (1999)."},
      12: {history: "The first penalized function, f12 of Yao et al. (1999)."},
      13: {history: "The second penalized function, f13 of Yao et al. (1999)."},
      14: {history: "f14 of Yao et al. (1999). Two coordinates, so the surface shown is the whole function, not a slice."},
      15: {history: "f15 of Yao et al. (1999), a model-fitting problem with four parameters."},
      16: {history: "f16 of Yao et al. (1999). Two coordinates, so the surface shown is the whole function. The usual range in other sources is smaller (-3 to 3 by -2 to 2); here it is -5 to 5."},
      17: {history: "f17 of Yao et al. (1999). Two coordinates, so the surface shown is the whole function."},
      18: {history: "f18 of Yao et al. (1999). Two coordinates, so the surface shown is the whole function."},
      19: {history: "f19 of Yao et al. (1999), in three coordinates."},
      20: {history: "f20 of Yao et al. (1999), in six coordinates."},
      21: {history: "f21 of Yao et al. (1999)."},
      22: {history: "f22 of Yao et al. (1999)."},
      23: {history: "f23 of Yao et al. (1999)."}
    }
  },

  sources: [
    ["Rosenbrock: H. H. Rosenbrock (1960), The Computer Journal 3(3), 175-184, doi:10.1093/comjnl/3.3.175", "https://doi.org/10.1093/comjnl/3.3.175"],
    ["Rastrigin function (history and references), Wikipedia", "https://en.wikipedia.org/wiki/Rastrigin_function"],
    ["Griewank: A. O. Griewank (1981), Journal of Optimization Theory and Applications 34(1), 11-39", "https://link.springer.com/article/10.1023/a:1021956306041"],
    ["Beyer and Finck (2012), HappyCat, in Parallel Problem Solving from Nature XII, pp. 367-376 (Springer)", "https://niapy.readthedocs.io/en/latest/_modules/niapy/problems/happy_cat.html"],
    ["Ackley (1987), A Connectionist Machine for Genetic Hillclimbing, Kluwer", "https://link.springer.com/book/9781461291923"],
    ["Schwefel (1981), Numerical Optimization of Computer Models, Wiley (as cited by the EmiR documentation)", "https://search.r-project.org/CRAN/refmans/EmiR/html/schwefel_func.html"],
    ["Yao, Liu and Lin (1999), Evolutionary programming made faster, IEEE Transactions on Evolutionary Computation 3(2), 82-102 (the 23 classic functions)", "https://www.cse.unr.edu/%7Esushil/class/gas/papers/EPMadeFaster.pdf"],
    ["Mirjalili, Mirjalili and Lewis (2014), Grey Wolf Optimizer, Advances in Engineering Software 69, 46-61 (the published GWO, PSO and GSA averages)", "https://doi.org/10.1016/j.advengsoft.2013.12.007"],
    ["Surjanovic and Bingham, Virtual Library of Simulation Experiments (properties of Rosenbrock, Rastrigin, Zakharov, Griewank, Ackley, Branin, Goldstein-Price, six-hump camel, Hartmann, Shekel)", "https://www.sfu.ca/~ssurjano/"],
    ["Kumar et al. (2021), Problem definitions and evaluation criteria for the CEC 2022 competition on single objective bound constrained numerical optimization (technical report; data files)", "https://github.com/P-N-Suganthan/2022-SO-BO"],
    ["Awad et al. (2016), Problem definitions and evaluation criteria for the CEC 2017 competition on single objective real-parameter numerical optimization (technical report)", "https://github.com/P-N-Suganthan/CEC2017-BoundContrained"],
    ["Yang (2009), Firefly algorithms for multimodal optimization, Stochastic Algorithms: Foundations and Applications (SAGA 2009), Lecture Notes in Computer Science, 169-178 (the firefly rule)", "https://doi.org/10.1007/978-3-642-04944-6_14"],
    ["Peram, Veeramachaneni and Mohan (2003), Fitness-distance-ratio based particle swarm optimization, Proceedings of the 2003 IEEE Swarm Intelligence Symposium, 174-181 (the fitness-distance ratio rules)", "https://doi.org/10.1109/SIS.2003.1202264"],
    ["Camacho-Villalón, Dorigo and Stützle (2023), Exposing the grey wolf, moth-flame, whale, firefly, bat, and antlion algorithms, International Transactions in Operational Research 30(6), 2945-2971", "https://doi.org/10.1111/itor.13176"]
  ]
};
