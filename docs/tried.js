// Text of the research report "Improving sound intensity search": every
// change and diagnostic run tested from Echo on, adopted or not, with its
// motivation, exact form, protocol and measured outcome. Sources: the saved
// results in results/, the README, and the experiment log kept during
// development (not part of this repository).
// Numbers are mean errors unless stated. "{N}" and "{K}" in the text are
// replaced by the page with the number of entries and of partly kept entries
// ("{k}" is the same count written in lower case). No dates: the report
// describes what was done, in the order it was done.
window.SOUND_TRIED = {

  title: "Improving sound intensity search",

  verdicts: {adopted: "Adopted", 
    worse: "Worse",
    trade: "Trade-off",
    none: "No effect",
    luck: "Did not hold",
    check: "Explains"
  },
  verdictNotes: {adopted: "better than its baseline on the design set and not significantly worse on the guard functions; it is part of Encore", 
    worse: "significantly worse than its baseline, with no gain that offsets the loss",
    trade: "significant gains on some kinds of function offset by significant losses on others; no overall improvement",
    none: "no significant difference from its baseline",
    luck: "an apparent effect (or absence of one) that changed when the experiment was repeated with more runs or new seeds",
    check: "a diagnostic experiment, run to explain why other changes failed"
  },

  abstract: "Sound intensity search is a population-based method for continuous optimisation in which every agent moves relative to the source it hears loudest, where loudness grows with fitness rank and fades with the square of distance. Starting from its second version, Echo, this report investigates {N} changes and diagnostic experiments and settles on a third version, Encore, which adopts three of the changes: the group starts again when it stalls, the group shrinks linearly during the run, and hearing becomes less exact after the start of each group search. Encore places 4th of 13 against the entries of the CEC 2022 competition at 10 coordinates and 2nd of 13 at 20 coordinates, with no entry significantly better at either size. Each change is given with its motivation, exact form, protocol and measured outcome. Changes were designed on the CEC 2017 functions at 10 coordinates and on a bench of stand-in functions, and were judged by Wilcoxon rank-sum tests per function and by Friedman tests with Holm's correction across functions; CEC 2022 was kept as a test set. {K} of the rejected changes were partly kept and entered Encore in a changed form. Most rejected changes share one cause: a trade-off between hearing near neighbours, which keeps sub-groups in separate valleys and protects against deceptive traps, and hearing good agents from anywhere or moving many coordinates at once, which crosses regular fields of valleys and hybrid functions faster. On CEC 2017 F22 the group commits to a valley within the first 3 to 6% of the evaluation budget, so any change that speeds up early gathering, or splits the budget at the start, loses the protection, and no mechanism acting later recovers it. The same trade-off appears when the selection rules of differential evolution, the firefly algorithm and fitness-distance-ratio particle swarm optimisation replace listening inside the same framework; listening is the only one of these five rules that avoids the traps without being worse overall. Three apparent effects did not survive replication and one early dismissal was reversed; the report gives the sample sizes needed to detect differences in trap rates.",
  keywords: ["continuous optimisation", "sound intensity search", "selection rule", "success-history adaptation", "linear population size reduction", "restarts", "deceptive functions", "Friedman test"],

  intro: [
    "Population-based methods inspired by natural phenomena are often criticised for restating known methods under new names (Sörensen, 2015; Camacho-Villalón et al., 2023). The useful answer to that criticism is evidence: what the distinctive rule of a method contributes, where the method fails, and what was tried to repair those failures. Positive results are routinely published; the attempts that failed are not, although they show which directions are closed and why.",
    "Sound intensity search was introduced as the Infrasonic Search Algorithm (Kenekayoro, 2021). Every agent emits a sound whose power increases with its fitness, the intensity an agent hears falls as its distance from the source grows, and each agent moves towards the neighbour it hears with the highest intensity. Its second version, Echo, keeps this sound model with three differences from the original: loudness comes from the fitness rank, intensity follows the inverse-square law, and an agent moves away from a source that is worse than itself. Echo combines the model with techniques borrowed from differential evolution, its adaptive variants and evolution strategies (Section 2.1):",
    ["Difference moves: besides moving towards or away from the source it hears, each agent takes a random push equal to the difference between two other agents (Storn & Price, 1997). Because the push is a difference between agents, it is large while the group is spread out and small once it has gathered.",
     "Echoes: when an agent moves to a better point, the point it left is kept in a store of old positions, and the random push may use one of these in place of a current agent (Zhang & Sanderson, 2009).",
     "Crossover: a move changes only some of an agent's coordinates; each coordinate changes with a probability called the hearing rate, and at least one always does (Storn & Price, 1997).",
     "Success-history adaptation: each agent draws its step size and hearing rate near values that recently produced improvements, and those values are updated after every iteration, so the settings follow what is working at that stage of the search (Tanabe & Fukunaga, 2013).",
     "Final refinement: the last part of the budget goes to the best point alone, which is improved by a (1+1)-CMA-ES, an evolution strategy that tries one random step at a time and adapts the size and direction of its steps to the ones that succeed (Igel et al., 2006)."],
    "Each run of a method has a budget: the number of times it may evaluate the objective function, for example 200,000 evaluations for a CEC 2022 function at 10 coordinates. Echo spends the first 70% of its budget on a single group of agents and the last 30% on refining the best point found. The group is created once, at random, and is never replaced, so if it gathers in a valley that does not contain the best point it cannot leave, and the rest of the group search is spent inside that valley. Its size is fixed, so evaluations late in the run still go to every agent rather than to the few best ones. And because loudness counts more as the run goes on, late in the run nearly every agent hears the same source loudest and moves along almost the same line, which adds little new information. Against the 12 entries of the CEC 2022 competition Echo places 8th of 13 at 10 coordinates.",
    "This report investigates changes aimed at these weaknesses and settles on a third version, Encore. Every change was designed on a design set and adopted only if it passed a fixed decision rule (Section 2.5). Three were adopted: restarts, a group that shrinks linearly as in L-SHADE (Tanabe & Fukunaga, 2014), and less exact hearing after the start. Encore places 4th of 13 at 10 coordinates and 2nd of 13 at 20, with no entry significantly better, but it remains weak on rotated Rastrigin (CEC 2022 F4), on two hybrid functions (F7, F8) and, at 10 coordinates, on a deceptive composition function (F10). The report records every change, adopted or not, together with the diagnostic experiments that explain why most of them failed."
  ],
  contributions: [
    "A complete record of {N} changes and diagnostic experiments, each with its motivation, exact form, protocol and outcome, including the three adopted changes that turn Echo into Encore (Section 3).",
    "Evidence that most failures follow from one trade-off, between protection against deceptive traps and progress on regular fields of valleys and hybrid functions, and that the trap is decided in the first few percent of the budget (Section 4).",
    "A comparison of the sound selection rule with the selection rules of three related methods inside one framework, with every other part held fixed (Section 3.8).",
    "Three effects that did not survive replication, one dismissal that was reversed, and the number of runs needed to tell trap rates apart (Sections 3.9 and 4.4)."
  ],

  methods: [
    {heading: "Echo and Encore",
     paras: [
       "Encore keeps a group of $n$ agents $x_1, \\dots, x_n$ inside lower and upper limits for each coordinate. At every iteration the agents are ranked, and agent $i$ gets the loudness $$p_i = \\frac{n - 1 - \\mathrm{rank}_i}{n - 1}, \\qquad P_i = \\frac{p_i}{\\sum_j p_j}, \\tag{1}$$ where $\\mathrm{rank}_i$ is 0 for the best agent, so only the order of the values matters. Agent $i$ hears agent $j$ with intensity $$I_{ij} = \\frac{P_j^{\\kappa}}{4 \\pi r_{ij}^2}, \\qquad r_{ij} = \\lVert x_i - x_j \\rVert, \\tag{2}$$ where $\\kappa$ rises during each group search (from 0 to 8 on the CEC functions, from 1 to 4 on the classic functions). During the first 10% of each group search agent $i$ turns to the loudest source $k = \\arg\\max_j I_{ij}$; afterwards it picks $k$ with probability proportional to $I_{ik}^2$ (step 10, ‘noisy hearing’). It then forms the trial point $$v_i = x_i + F_i \\big( \\pm (x_k - x_i) + (x_a - x_e) \\big), \\tag{3}$$ moving towards $k$ if $k$ is fitter and away from it otherwise, where $x_a$ is a random agent and $x_e$ a random agent or echo (a point that an agent has left). Each coordinate of $v_i$ is taken with probability $C_i$, the agent's hearing rate, and at least one always is. The trial point replaces $x_i$ only if it is better, and $x_i$ becomes an echo.",
       "The step size $F_i$ and hearing rate $C_i$ are drawn around values kept in a success-history memory (Tanabe & Fukunaga, 2013). On the CEC functions the group starts with 18 agents per coordinate and shrinks linearly to 4 by removing its worst agents (step 9; Tanabe & Fukunaga, 2014). The group starts again from random points when its best value has not improved by 1% of the group's value spread for 10% of the budget (step 8). The last 10% of the evaluations (30% on the classic functions) refine the best point with a (1+1)-CMA-ES (Igel et al., 2006).",
       "Equations (1) and (2), the choice of the source $k$ and the towards-or-away sign in (3) form the sound model; the difference move and crossover come from differential evolution (Storn & Price, 1997), the echo archive from JADE (Zhang & Sanderson, 2009), and the memory and shrinking group from SHADE and L-SHADE. Algorithm 1 gives both methods as pseudocode: Echo is the same procedure without steps 8 to 10, the lines marked †, and with the settings listed under it. Each variant below changes one part: the source choice, the move, the hearing rate, the parameter memory, the group's size or life cycle, the control of the search, or the endgame."
     ],
     algorithm: {
      "caption": "Algorithm 1. Echo and Encore. Lines marked † are the three changes adopted in Encore (steps 8 to 10); without them the procedure is Echo. $t$ counts the evaluations used.",
      "input": "@Input:@ objective $f$, lower and upper limits for each coordinate, a budget of $T$ evaluations and the settings below. @Output:@ the best point found, $x^*$.",
      "lines": [
       {
        "d": 0,
        "enc": false,
        "c": "$T_g \\leftarrow (1 - \\rho)\\, T$",
        "note": "budget of the group searches"
       },
       {
        "d": 0,
        "enc": true,
        "c": "@repeat@",
        "note": "restarts (step 8)"
       },
       {
        "d": 1,
        "enc": true,
        "c": "$t_0 \\leftarrow t$;  $n \\leftarrow n(t)$",
        "note": "group size (step 9)"
       },
       {
        "d": 1,
        "enc": false,
        "c": "draw $x_1, \\dots, x_n$ uniformly between the limits and evaluate them; empty the echo archive $A$; reset the memory $M$",
        "note": ""
       },
       {
        "d": 1,
        "enc": false,
        "c": "@while@ $t < T_g$ @do@",
        "note": ""
       },
       {
        "d": 2,
        "enc": false,
        "c": "$\\tau \\leftarrow (t - t_0) / (T_g - t_0)$;  $\\kappa \\leftarrow \\kappa_0 + (\\kappa_1 - \\kappa_0)\\, \\tau$",
        "note": "progress of this group search"
       },
       {
        "d": 2,
        "enc": false,
        "c": "compute the loudness $P_j$ by (1) and the intensities $I_{ij}$ by (2)",
        "note": ""
       },
       {
        "d": 2,
        "enc": false,
        "c": "@for each@ agent $i$ @do@",
        "note": ""
       },
       {
        "d": 3,
        "enc": false,
        "c": "draw $F_i \\in (0, 1]$ and $C_i \\in [0, 1]$ near a random slot of $M$",
        "note": ""
       },
       {
        "d": 3,
        "enc": false,
        "c": "@if@ $\\tau < \\eta$ @then@ $k \\leftarrow \\arg\\max_j I_{ij}$",
        "note": "Echo: always"
       },
       {
        "d": 3,
        "enc": true,
        "c": "@else@ pick $k$ with probability proportional to $I_{ik}^{\\varphi}$",
        "note": "less exact hearing (step 10)"
       },
       {
        "d": 3,
        "enc": false,
        "c": "$s \\leftarrow +1$ if $f(x_k) < f(x_i)$, else $s \\leftarrow -1$",
        "note": "towards or away"
       },
       {
        "d": 3,
        "enc": false,
        "c": "$v_i \\leftarrow x_i + F_i \\big( s\\,(x_k - x_i) + (x_a - x_e) \\big)$, with $x_a$ a random agent and $x_e$ a random agent or echo",
        "note": "equation (3)"
       },
       {
        "d": 3,
        "enc": false,
        "c": "keep each coordinate of $v_i$ with probability $C_i$, at least one, and reset the others to $x_i$; put a coordinate past a limit halfway between $x_i$ and that limit",
        "note": "crossover"
       },
       {
        "d": 2,
        "enc": false,
        "c": "evaluate every $v_i$; for each $i$ with $f(v_i) < f(x_i)$, add $x_i$ to $A$ and set $x_i \\leftarrow v_i$",
        "note": ""
       },
       {
        "d": 2,
        "enc": false,
        "c": "store the means of the successful $F_i$ and $C_i$, weighted by their gains, in the next slot of $M$; keep at most $n$ echoes",
        "note": "success-history memory"
       },
       {
        "d": 2,
        "enc": true,
        "c": "remove the worst agents until $n(t)$ are left",
        "note": "shrinking group (step 9)"
       },
       {
        "d": 2,
        "enc": true,
        "c": "@if@ the best value has not improved by 1% of the spread of values for $\\beta T$ evaluations, or all values are equal, @then@ @break@",
        "note": "restart (step 8)"
       },
       {
        "d": 1,
        "enc": false,
        "c": "@end while@",
        "note": ""
       },
       {
        "d": 1,
        "enc": false,
        "c": "replace $x^*$ by the best agent if that agent is better",
        "note": ""
       },
       {
        "d": 0,
        "enc": true,
        "c": "@until@ $t \\geq T_g$, or too few evaluations are left for a new group",
        "note": "Echo: one pass"
       },
       {
        "d": 0,
        "enc": false,
        "c": "refine $x^*$ with a (1+1)-CMA-ES for the remaining $\\rho T$ evaluations",
        "note": ""
       },
       {
        "d": 0,
        "enc": false,
        "c": "@return@ $x^*$",
        "note": ""
       }
      ],
      "settings": "@Settings.@ Echo: $n(t) = n_0$, with $n_0 = 30$ on the classic functions and 50 on the CEC functions; $\\kappa_0 = 1$, $\\kappa_1 = 4$; $\\rho = 0.3$; $\\eta = 1$ and no restarts, so lines 11, 17 and 18 never act and lines 2 to 21 run once. Encore on the CEC functions: $n(t)$ falls linearly from $n_0 = 18D$, for $D$ coordinates, to $n_{\\min} = 4$ as $t$ goes from 0 to $T_g$; $\\kappa_0 = 0$, $\\kappa_1 = 8$; $\\rho = 0.1$; $\\beta = 0.1$; $\\eta = 0.1$; $\\varphi = 2$. Encore on the classic functions keeps $n = 30$, $\\kappa$ from 1 to 4 and $\\rho = 0.3$. Both: a memory of 5 slots starting at $F = C = 0.5$; step sizes are drawn from a Cauchy distribution and hearing rates from a normal distribution around the slot's values, both with scale 0.1."
     }},
    {heading: "Benchmarks",
     list: [
       "Classic suite: the 23 functions of Yao et al. (1999), plain, with the optimum moved (12 functions) and moved and rotated (12); 30 agents, 15,030 evaluations, 30 runs. Used during the Echo redesign.",
       "CEC 2017 (Awad et al., 2016): 29 functions at 10 coordinates with 100,000 evaluations. Functions keep the numbers of the organisers' C code, F1 and F3 to F30 (F2 is not used); the updated definitions number the same 29 functions 1 to 29. This is the design set of Encore: every choice between variants was made on it.",
       "Stand-in bench, 31 runs with the seeds of Encore: CEC 2017 F5 and F8 (rotated Rastrigin, standing in for CEC 2022 F4; labelled c5, c8), F10 (rotated Schwefel, c10), F7 (Lunacek bi-Rastrigin), F12, F17, F21, F22 and F24, and three new random instances, each with its own shift, rotation and coordinate order, of the CEC 2022 F8 blend (p0, p1, p2). For the experiments of Section 3.7 the bench also held new instances of the CEC 2022 F2, F4, F7 and F8 forms (q2x0, q4x0, q4x1, q7x0, q7x1, q8x0).",
       "CEC 2022 (Kumar et al., 2021): 12 functions at 10 coordinates with 200,000 evaluations, and at 20 coordinates with 1,000,000 for the final check; 30 runs. This is the test set. It was run once for each change that passed the design set, and compared with the published results of the 12 competition entries."
     ]},
    {heading: "Protocol",
     list: [
       "The budget of a run is the number of evaluations of the objective function it may use, fixed by each benchmark (Section 2.2); a share of the budget, such as ‘the first 10%’, means that share of these evaluations.",
        "The error of a run is the final best value minus the best possible value. Errors of $10^{-8}$ or less count as 0, and errors are compared to 6 significant figures.",
       "Common random numbers: within a comparison every variant used the same seeds as its baseline, so differences come from the change, not from the draw of starting points.",
       "Each prototype was written so that switching the change off reproduces the baseline's runs exactly; this was checked before each bench.",
       "Run counts grew with the question: 8 to 10 runs for a first look, 20 for a screen on 8 functions, 30 or 31 for a decision, and 51 where trap rates had to be compared.",
       "The baseline changed as Encore grew, and each stage states its baseline. Numbers are comparable only within a stage or table: for example, CEC 2017 F5 is 4.14 for the method before step 10 and 3.32 to 3.43 after it."
     ]},
    {heading: "Statistical analysis",
     list: [
       "Per function, a two-sided Wilcoxon rank-sum test at the 5% level. ‘Better on k functions’ counts only significant differences.",
       "Across functions, the Friedman test on mean errors, with Holm's step-down correction for the comparisons of each variant with the control (Demšar, 2006; Derrac et al., 2011).",
       "On CEC 2017 F22 a run is ‘trapped’ when it ends in the decoy valley (error of 50 or more; trapped runs end at about 100). On F24 the good runs end at about 100 and the others at about 330.",
       "On the classic suite, ‘worse’ and ‘better’ mean a typical error at least twice, or at most half, that of the baseline; no test was applied."
     ]},
    {heading: "Decision rule",
     paras: [
       "A change was adopted only if it was better than its baseline on the design set overall, by the Friedman and Holm tests or by clearly more significant wins than losses, and was not significantly worse on the guard functions: the traps (CEC 2017 F22, F24), rotated Schwefel (F10) and the hybrids (F7, F12, F17). CEC 2022 results were never used to choose between variants. A change justified mainly by the stand-ins built from CEC 2022 definitions (p and q) also had to hold on the whole of CEC 2017."
     ]},
    {heading: "Outcome categories",
     verdictList: true}
  ],

  resultsIntro: "Table 1 gives all {N} entries in full, in the order they were tested and grouped by development stage; the three adopted changes are entries 6, 11 and 21. For each entry it gives the part of the method changed, the motivation, the exact change and, where it differs from Section 2, the protocol, the measured result, a reading of the result and the outcome. Entries are referred to by their number in Table 1. Sections 3.1 to 3.9 then describe the setting of each stage and give the comparisons that several entries rest on (Tables 2 to 5). Mean errors are given as ‘variant against baseline’, with the baseline of each stage named in its row of Table 1.",

  stages: [
    {
      title: "Echo: the redesign",
      when: "Classic suite · baseline: Echo as it was being built",
      intro: "Mating Call spent about half of its evaluations on exploration steps sized by the width of the search space, collapsed far from the optimum, depended on the scale of the function, and was 2 to 30 times worse on several functions when the optimum was moved away from the origin. Echo replaced its update with rank-based loudness, the rising $\\kappa$, difference moves with echoes, a learned step size and hearing rate, and the final refinement. The changes below were tested during that redesign and rejected.",
      items: [
        {name: "A pull towards the best few agents",
         component: "Move",
         why: "Mating Call pulled every agent towards the best one. A pull towards a few of the best agents, added to listening, should keep that speed while spreading the pull over several leaders.",
         change: "An extra term towards a random one of the best few agents was added to the sound move.",
         result: "Faster on smooth unimodal functions, but worse on the low-dimensional multimodal functions f14 to f23 and on functions with many valleys.",
         reading: "A pull towards the best agents from anywhere overrides the local hearing that keeps sub-groups apart. Echo instead lets loudness count more as the run goes on (the $\\kappa$ ramp), which gives the late convergence without the early global pull. This was the first sign of the trade-off discussed in Section 4.1.",
         verdict: "trade"},
        {name: "Letting the worst agents leave",
         component: "Group size",
         why: "Evaluations spent late on the worst agents are wasted; L-SHADE removes them on a linear schedule (Tanabe & Fukunaga, 2014).",
         change: "The group shrank during the run, its worst agents leaving.",
         result: "Rastrigin (f9) was solved, but only because its coordinates are independent of one another; f4, f10, f12 and f13 got worse.",
         reading: "With 30 agents and 15,030 evaluations there are too few agents to lose.",
         verdict: "worse",
         kept: "With the CEC budgets, 7 to 13 times longer, and a group that starts at 18 agents per coordinate, shrinking helps; it became step 9 (entry 11)."},
        {name: "Listening to a random or the nearest agent",
         component: "Source choice",
         why: "An ablation: if the loudest source could be replaced by any agent, the sound model would contribute nothing.",
         change: "The loudest source was replaced by a random agent, or by the nearest agent with loudness ignored.",
         setup: "Classic suite, 47 results (23 plain, 12 moved, 12 moved and rotated functions). Then CEC 2022 at 10 coordinates, 30 runs.",
         result: "Classic suite: a random agent was worse on 16 of 47 results and better on 3; the nearest agent was worse on 21 and better on none. CEC 2022: listening to the loudest was better than a random agent on 3 of 12 functions and never worse; against the nearest agent it was better on 2 and worse on 1 (F10, 104 against 10.9). The Friedman test found no overall difference on CEC 2022 (p = 0.55).",
         reading: "Loudness does real work. On CEC 2022 F10, ignoring loudness escaped the trap: an early hint that hearing only near agents protects against traps.",
         verdict: "worse"},
        {name: "Never moving away",
         component: "Move",
         why: "In the published model an agent moves away from a source worse than itself. If this does not help, removing it simplifies the method.",
         change: "Agents always move towards the source heard, whether it is fitter or not.",
         setup: "Classic suite; CEC 2022, 30 runs; later CEC 2017 F5, F8, F10, F22 and F24, 51 runs.",
         result: "Classic suite: better on 7 of 47 results and worse on 2, mostly by small amounts, though one f15 run got stuck. CEC 2022: better on F8 (4.75 against 8.32), worse on F12, no overall difference. CEC 2017, 51 runs: F22 trapped in 15 of 51 runs against 14, F24 157 against 141; no significant difference.",
         reading: "Moving away is neutral. It was kept as part of the published model.",
         verdict: "none"},
        {name: "Other small settings",
         component: "Settings",
         change: "20% of the evaluations for refinement instead of 30%; a parameter memory of 10 slots; a starting hearing rate of 0.2.",
         result: "None improved on the settings chosen.",
         verdict: "none"}
      ]
    },
    {
      title: "Restarts, choosing between methods, and group size",
      when: "Classic functions moved and rotated, then CEC 2017, 29 functions, 10 runs · baseline: Echo, then Echo with restarts (step 8), 50 agents",
      intro: "Restarts were adopted first (step 8, entry 6). They left the method weak on traps and on the hybrid functions. A hyper-heuristic, a top-level method that chooses which low-level method to apply as the search goes on (Burke et al., 2003), was tried at four levels, followed by a group that shrinks during the run, which was adopted (step 9, entry 11), and other group sizes.",
      items: [
        {name: "Starting the group again when it stalls",
         component: "Restarts",
         why: "Echo runs one group for the whole budget, so a group that settles in a wrong valley stays there.",
         change: "The group starts again from new random points when its best value has not improved by at least 1% of the spread of the group's values for 10% of all evaluations, or when every agent is equally good. The best point found so far is kept and refined at the end (step 8).",
         setup: "Settings chosen on the classic functions moved and rotated, 30 coordinates, 300,000 evaluations; then the classic functions at the usual budget and CEC 2022 at 10 coordinates, 30 runs.",
         result: "Classic functions at the usual budget: unchanged. CEC 2022: better than Echo on F2 (0.664 against 2.82), F4 (5.14 against 6.43), F10 (100 against 104) and F12 (160 against 161), worse on F7 (0.487 against 0.176); average rank 6.92 against 7.33 among the 12 competition entries, 8th of 13 both times.",
         reading: "Restarts help where a group stalls early, but each new group falls into the same trap as the last on CEC 2022 F9, F10 and F12. F7 gets worse because it improves in jumps after long pauses, and a restart can come in the middle of a pause.",
         verdict: "adopted"},
        {name: "Each agent picks its own hearing rule",
         component: "Control",
         why: "Loudest-source hearing and nearest-agent hearing had complementary strengths (entry 3), so each agent might learn which suits its region.",
         change: "Each agent chose between the loudest and the nearest source with probabilities given by its own recent success with each.",
         setup: "The design set used at the time: classic functions f1 to f13, moved and rotated, 30 coordinates, 300,000 evaluations.",
         result: "Mixed, and worse on rotated Rastrigin. That design set proved too easy: most variants reached the optimum, so it could not separate them.",
         reading: "This led to CEC 2017 becoming the design set.",
         verdict: "trade"},
        {name: "A chooser for every 2% of the budget",
         component: "Control",
         change: "For each stretch of 2% of the evaluations, a chooser picked one of three low-level methods: loudest-source hearing, nearest-agent hearing ($\\kappa = 0$), or refining the best point.",
         result: "Worse than restarts alone on 4 functions and better on none (Friedman p = 0.005).",
         verdict: "worse"},
        {name: "A chooser for each new group",
         component: "Control",
         change: "At each restart, the new group used loudest-source hearing, nearest-agent hearing, or a group four times larger. Each option scored $+1$ or $-1$ by whether its last use improved the best value (capped at 3), and an option that had just failed was barred for one restart.",
         result: "The same as plain restarts on 27 of 29 functions (Friedman p = 0.11).",
         reading: "With the stagnation rule at 10% of the budget a run starts only 2 or 3 groups. The first group always counts as an improvement, because it starts from nothing, so loudest-source hearing always won the second pick: the chooser never really chose. A choice at the level of restarts cannot learn at this budget.",
         verdict: "none"},
        {name: "A chooser for each agent at every step",
         component: "Control",
         change: "At every iteration each agent used loudest, nearest or far hearing ($\\kappa$ doubled), with probability proportional to the mean gain per use of each rule and never below 0.1.",
         result: "Worse on F15 and F29, better on none.",
         reading: "The three rules are too alike, and step size and hearing rate already adapt, so a chooser has little left to gain.",
         verdict: "worse"},
        {name: "A group that shrinks",
         component: "Group size",
         why: "With a fixed group, evaluations late in the run still go to every agent rather than to the best few. L-SHADE shrinks its population on a linear schedule (Tanabe & Fukunaga, 2014). Shrinking had hurt at the classic budget (entry 2), but the CEC budgets are 7 to 13 times longer.",
         change: "The group starts with 18 agents per coordinate and shrinks linearly to 4 by the end of the group search, removing its worst agents (step 9). A group that starts again takes the size planned for that point of the run.",
         setup: "CEC 2017, 29 functions, 10 runs, against restarts alone; then CEC 2022 at 10 coordinates, 30 runs.",
         result: "CEC 2017: better on 3 of 29 functions and worse on none; F10 (Schwefel) 97 against 174, F12 3.5 against 38, F24 180 against 288. With the group shrinking, restarts made little difference (1 function better without them, none worse). CEC 2022: better than restarts alone on 3 functions and worse on none; better than Echo on 7 and worse on none (Holm-adjusted p = 0.03); average rank 6.25, 4th of 13, with no entry significantly better.",
         reading: "Many agents early spread over many valleys, and few agents late concentrate the evaluations on the best. Restarts were kept because they still stop a group that is completely stuck.",
         verdict: "adopted"},
        {name: "A larger group that does not shrink",
         component: "Group size",
         change: "100 or 200 agents for the whole run instead of 50.",
         result: "100 agents: worse on 6 functions, better on none. 200 agents: worse on 17, though better on the two trap functions (F24 100 against 288; F22 also lower).",
         reading: "A large group keeps more sub-groups apart early, which the traps need, but a fixed large group has too few iterations left to converge. Starting large and shrinking combines the two.",
         verdict: "worse"},
        {name: "Other start sizes for the shrinking group",
         component: "Group size",
         change: "Linear shrinking to 4 agents from 50, 100 or 250 agents, against 180 (18 per coordinate, the L-SHADE rule).",
         result: "From 180: better than restarts alone on 3 functions (F16, F20, F24) and worse on none (average rank 1.84 against 2.29, Holm p = 0.19; F24 180 against 288, F22 14 against 37). Starting at 100 or 250 did less well than 180, and shrinking from 50 was worse than not shrinking at all.",
         reading: "180 to 4 became step 9.",
         verdict: "worse"},
        {name: "Restart timing",
         component: "Control",
         change: "Restart after 5% of the budget without a real gain instead of 10%; or no restarts at all once the group shrinks.",
         result: "5%: no real difference. No restarts, with shrinking: better on 1 function (F29) and worse on none at 10 runs, and no different on 8 functions at 20 runs.",
         reading: "With a shrinking group restarts rarely matter, and removing them gained nothing, so they stayed. A trace also showed that the stagnation check can fire too early while the group is large: a real gain must be 1% of the group's value spread, which is wide for a large scattered group. In one Rastrigin run this restarted the group at 22% of the budget, and the new group needed until 40% to catch up.",
         verdict: "none"}
      ]
    },
    {
      title: "The weak functions",
      when: "CEC 2017 F5, F7, F8, F10, F16, F17, F22, F24 · 10, 20 and 51 runs · baseline: steps 8 and 9",
      intro: "CEC 2022 F4 is a rotated Rastrigin function, for which CEC 2017 F5 and F8 stand in. CEC 2022 F10 traps most runs in a decoy valley at error 100; CEC 2017 F22 has the same kind of trap, with a Griewank valley as the decoy. The changes below targeted these weaknesses on the design set; the last of them was adopted (step 10, entry 21). Table 2 gives the decisive 51-run comparison.",
      table: {
        caption: "Table 2. CEC 2017, 51 runs per variant, mean error (F22: runs trapped). * significantly better than the baseline (Wilcoxon rank-sum, 5%). - not recorded.",
        head: ["Variant", "F5", "F8", "F10", "F22 trapped", "F24"],
        rows: [
          ["Steps 8 and 9 (baseline)", "4.14", "4.78", "110", "14 of 51", "141"],
          ["$\\kappa$ from 0 to 8, refinement 10%", "4.10", "4.27*", "103", "11 of 51", "120"],
          ["$\\kappa$ from 1 to 8, refinement 10%", "3.84", "4.37", "110", "14 of 51", "125"],
          ["Refinement 10% only", "4.16", "4.43", "99", "15 of 51", "141"],
          ["Never move away", "4.12", "4.58", "99", "15 of 51", "157"],
          ["Hearing floor with recovery", "-", "4.06", "132", "20 of 51", "-"],
          ["Hearing loss with age", "4.19", "4.51", "120", "15 of 51", "136"],
          ["Full life cycle", "4.53", "4.76", "129", "11 of 51", "136"],
          ["Life cycle, $\\kappa$ to 8, refinement 10%", "4.10", "4.31", "89", "11 of 51", "119"],
          ["Noisy hearing from the start, $\\varphi = 1$", "3.30*", "3.34*", "86", "36 of 51", "277"],
          ["Noisy hearing from the start, $\\varphi = 4$", "3.88", "3.84*", "101", "24 of 51", "208"],
          ["Noisy hearing after 10%, $\\varphi = 1$", "3.22*", "3.51*", "95", "11 of 51", "-"],
          ["Noisy hearing after 30%, $\\varphi = 1$", "4.06", "4.27", "108", "14 of 51", "-"],
          ["Noisy after 10%, $\\kappa$ 0 to 8, refinement 10%, $\\varphi = 1$", "3.51*", "3.28*", "98", "6 of 51", "-"]
        ]
      },
      items: [
        {name: "Different settings",
         component: "Settings",
         why: "Before changing how the search works, check whether its settings are the limit.",
         change: "One at a time: $\\kappa$ ending at 2 or 8 instead of 4; $\\kappa$ starting at 0 instead of 1; twice as many echoes; refinement on 10% of the budget instead of 30%; no refinement.",
         setup: "8 functions, 20 runs (the refinement variants first at 10 runs on all 29 functions).",
         result: "$\\kappa$ to 8: better on F8 only (4.08). $\\kappa$ from 0: worse on F5, though F22 (22 against 41) and F24 (125 against 168) improved, not significantly. $\\kappa$ to 2: worse on F5. Twice the echoes: worse on F5, and F22 rose to 62. Refinement 10%: no significant difference (F10 77 against 103). No refinement: worse on F11.",
         reading: "The settings sit on a plateau, so closing the gap on Rastrigin and Schwefel needs a change in how the search works. Combined, $\\kappa$ from 0 to 8 with 10% refinement gave a small, consistent gain over 51 runs: a better mean on all five functions of Table 2, F8 significantly.",
         verdict: "none",
         kept: "$\\kappa$ from 0 to 8 with 10% refinement became part of step 10 for the CEC runs (entry 21)."},
        {name: "A floor on the hearing rate",
         component: "Hearing rate",
         why: "The hearing rate is the share of coordinates that move in a step. Traces showed it falling to one coordinate at a time by mid-run on every function, rotated ones included, for two reasons: small one-coordinate moves succeed more often, and a memory slot that reaches 0 stays at 0, a rule taken from L-SHADE. Rotated functions need several coordinates to move together.",
         change: "As in jSO (Brest et al., 2017): a hearing rate of at least 0.7 in the first quarter of the run and 0.6 in the first half, with memory slots that can recover from 0. Each part was also tested alone.",
         result: "10 runs, 29 functions: better on F8, F11 and F19 and worse on none, but F22 was trapped in 5 of 10 runs against 1. 51 runs: F8 4.06 against 4.78, but F22 trapped in 20 of 51 runs against 14, and F10 132 against 110. Recovery alone made no difference on any of the five functions.",
         reading: "Moving more coordinates makes the group gather faster, and early gathering is what feeds the trap (entry 18).",
         verdict: "trade"},
        {name: "Masking",
         component: "Group size",
         why: "When the group shrinks, its worst agents leave. In a trap, the few agents exploring the right valley may still be worse than the crowd in the decoy and leave first. Masking, the effect by which a quiet sound next to a loud one cannot be heard, suggests a sound-based alternative.",
         change: "The agent that leaves is the one most drowned out by a fitter agent nearby: the one receiving the highest intensity $P_j^{\\kappa}/(4\\pi r^2)$ from a fitter agent $j$. A lone agent far from the crowd is not masked and stays. Two pools were tried: any agent may leave, or only the worse half.",
         setup: "8 functions, 20 runs.",
         result: "Any agent: worse on 6 of 8 functions (F5 7.7 against 3.7, F10 172 against 103, F16 3.7, F17 4.3), and F22 trapped in 6 of 20 runs against 7. Worse half only: worse on F16, and F22 trapped in 10 of 20.",
         reading: "Keeping lone explorers costs fine search and does not fix the trap, so the trap is not caused by scouts of the right valley being removed. Entry 18 shows why.",
         verdict: "worse"},
        {name: "Why F22 gets trapped",
         component: "Diagnostic",
         change: "Position traces of single runs on CEC 2017 F22: at each moment, the number of agents nearest the centre of the true (Rastrigin) valley and nearest the decoy (Griewank) centre.",
         result: "The group commits to a valley within the first 3 to 6% of the budget. In trapped runs every agent is nearest the decoy by 6% of the budget; in successful runs 15 to 27 agents are still near the true centre at 6%, and they win later.",
         reading: "The trap is decided by how fast the group gathers at the start, not by the endgame. Masking, which acts while the group shrinks, came too late, as does any change that acts after the first few percent of the budget.",
         verdict: "check"},
        {name: "Hearing modelled on human hearing",
         component: "Source choice",
         why: "Hearing differs between people and fades with age. If older agents heard only near agents and young agents explored on their own, sub-groups might stay apart longer without slowing the final convergence.",
         change: "Four parts, each switchable. Individual ears: each agent keeps its own $\\kappa$ for life, $\\kappa(t)\\, e^{0.5 z}$ with $z$ drawn from a standard normal. Hearing loss: heard intensity is multiplied by $\\exp\\!\\big(-3\\, (a/L)\\, (r/\\bar r)\\big)$, where $a$ is the agent's age and $\\bar r$ a typical distance, so older agents hear only near agents. Stubborn children: for the first 10% of its life an agent ignores the others and moves only by the random push. Generations: after $L = 100$ iterations an agent is replaced by a child at the same point, with new ears; starting ages are mixed. A ‘childhood’ variant also let no agent listen during the first 3% or 6% of each group search. With identical ears and no ageing the prototype chose the same sources as the baseline.",
         setup: "8 functions, 20 runs; then F5, F8, F10, F22 and F24, 51 runs (Table 2).",
         result: "20 runs: no part was significantly better (F22 trapped: individual ears 8 of 20, hearing loss 5, stubborn children 7, full life cycle 4, baseline 7); childhood at 3% and 6% was worse on F17 and F5. 51 runs: hearing loss equal to the baseline (F22 15 of 51 against 14); the full life cycle no better (F5 4.53, F10 129, F22 11 of 51). The life cycle with $\\kappa$ to 8 and 10% refinement matched $\\kappa$ from 0 to 8 with 10% refinement alone, so its gain came from those settings.",
         reading: "Each part moved the search in the expected direction, with fewer traps and slower fine search, but none broke the trade-off. Childhood did not help because once listening starts the group still gathers within a few percent of the budget.",
         verdict: "none",
         kept: "Hearing that becomes less exact as the group search goes on became step 10 (entry 21)."},
        {name: "Less exact hearing from the start",
         component: "Source choice",
         why: "Late in the run $\\kappa$ is high, so nearly every agent hears the same best agent loudest and all move along almost the same line, which is a poor way to hop between the valleys of Rastrigin or Schwefel. jSO instead pulls each agent towards a random one of the best 10 to 25% of the group.",
         change: "Each agent turns towards source $k$ with probability proportional to $I_{ik}^{\\varphi}$ ($\\varphi = 1$ or 4) instead of always the loudest. In a random group the loudest source is then picked 17% of the time at $\\varphi = 1$ and 58% at $\\varphi = 4$. The start of the noisy choice was then delayed to 5%, 10%, 20% or 30% of each group search, and $\\varphi = 2$ was tried.",
         setup: "F5, F8, F10, F22, F24, 51 runs (Table 2); then all 29 functions, 30 runs.",
         result: "From the start, $\\varphi = 1$ cut the Rastrigin errors (F5 3.30 against 4.14, F8 3.34 against 4.78, both significant), but F22 was trapped in 36 of 51 runs against 14, and F24 at 100 in only 12 of 51 runs against 39. $\\varphi = 4$ gave a smaller gain (F8 3.84) and 24 of 51 trapped. Starting after 10% kept the gain without the extra traps (F5 3.22, F8 3.51, F22 11 of 51); starting after 30% lost the gain (F5 4.06); with $\\kappa$ from 0 to 8 and 10% refinement, starting after 5% raised the F22 mean (34.5). With $\\varphi = 1$, F7 (Lunacek bi-Rastrigin) got worse (12.1 against 8.6); $\\varphi = 2$ avoided this (9.05).",
         reading: "A noisy choice early lets far-off good agents be heard while the valley is being chosen, so the group gathers too soon; the same choice later, once the group has committed, gives it more directions to try.",
         verdict: "trade",
         kept: "Noisy hearing after 10% of each group search, with $\\varphi = 2$ and $\\kappa$ from 0 to 8 with 10% refinement, is step 10. On all 29 functions (30 runs) it is better than steps 8 and 9 on 11 and worse on 1 (Friedman and Holm, adjusted p = 0.005)."},
        {name: "Less exact hearing after the start, with the CEC settings",
         component: "Source choice",
         why: "Less exact hearing from the start gained on Rastrigin but lost the trap protection (entry 20). The trap is decided early in each group search (entry 18), so hearing exactly at the start and less exactly afterwards should keep the protection and the gain.",
         change: "During the first 10% of each group search every agent turns to the loudest source; afterwards it picks source $k$ with probability proportional to $I_{ik}^{\\varphi}$ with $\\varphi = 2$. For the CEC runs $\\kappa$ rises from 0 to 8 and the final refinement gets 10% of the evaluations instead of 30% (step 10).",
         setup: "CEC 2017, 29 functions, 30 runs, against restarts with the shrinking group; then CEC 2022 at 10 coordinates, 30 runs.",
         result: "CEC 2017: better on 11 of 29 functions and worse on 1 (F25, 398 against 388); Holm-adjusted p = 0.005. F5 (Rastrigin) 3.32 against 3.95, F8 3.35 against 4.84, F10 99 against 115, F22 21.1 against 37.7, F24 111 against 165 (F10 and F22 not significant on their own). CEC 2022: better on F4 (3.48 against 5.14) and F10 (81.1 against 97.8), worse on F6 (0.0981 against 0.0539); better than Echo on 6 functions and worse on none (Holm-adjusted p = 0.04); average rank 6.00, 4th of 13.",
         reading: "Exact hearing at the start keeps the trap protection, and less exact hearing later helps on Rastrigin. The F4 gain held with new seeds; the F10 gain, from 6 of 30 runs escaping the trap, did not (entry 49).",
         verdict: "adopted"}
      ]
    },
    {
      title: "CEC 2022 F4 and F8",
      when: "Stand-in bench, 31 runs · baseline: Encore",
      intro: "After step 10, Encore was still weak on CEC 2022 F4 (rotated Rastrigin) and F8, a hybrid of Katsuura (30% of the coordinates), HappyCat (20%), Griewank-Rosenbrock (20%), Schwefel (10%) and Ackley (20%). Splitting the error of p0 by part over six runs showed two causes. The Ackley part (2.6 to 5.4) ends one or two grid steps away from its best valley, the same problem as on Rastrigin, so F4 and F8 share a weakness. The HappyCat part (1 to 2.4) ends on its curved ring, but on the far side from the best point. Table 3 gives the variants of the hearing rate.",
      table: {
        caption: "Table 3. Stand-in bench, 31 runs, mean error. c5, c8: CEC 2017 F5 and F8; p0 to p2: new instances of the CEC 2022 F8 blend; c22, c24, c10, c7: CEC 2017 F22, F24, F10, F7. ‘Floor ℓ from t’: at least a share ℓ of coordinates move from t of the budget on. - not run.",
        head: ["Variant", "c5, c8", "p0, p1, p2", "c22", "c24", "c10", "c7"],
        rows: [
          ["Encore (baseline)", "3.43, 3.43", "3.43, 4.04, 3.89", "20.2", "102", "92.1", "9.03"],
          ["Early floor (jSO) with recovery", "3.31, 3.37", "1.14, 2.93, 2.59", "-", "-", "-", "-"],
          ["Floor 0.3 from 10%", "3.15, 3.24", "1.93, 2.20, 1.88", "-", "-", "-", "-"],
          ["Floor 0.5 from 10%", "3.72, 3.56", "0.72, 0.89, 0.77", "-", "-", "-", "-"],
          ["Floor 0.8 from 10%", "3.59, 3.53", "0.43, 0.60, 0.62", "18.0", "109", "264", "10.9"],
          ["Floor 0.8 from 50%", "3.50, 3.47", "0.92, 0.74, 0.61", "9.9", "111", "158", "9.00"],
          ["Floor 0.8 from 70%", "2.99, 3.21", "1.86, 1.76, 2.16", "12.9", "107", "143", "9.07"],
          ["Floor 0.8 from 50%, sticky slots", "3.63, 3.34", "1.15, 1.70, 1.18", "9.9", "111", "153", "9.07"],
          ["Half the agents hear widely", "3.56, 3.59", "0.47, 0.56, 0.80", "15.6", "118", "288", "10.8"],
          ["A quarter hear widely", "3.76, 3.79", "0.44, 0.93, 0.56", "14.6", "118", "190", "11.1"],
          ["A quarter wide, no memory leak", "3.08, 3.43", "3.78, 4.43, 3.83", "12.3", "100", "95", "9.84"],
          ["Half wide, no memory leak", "2.99, 2.99", "3.69, 4.02, 3.75", "13.3", "111", "124", "8.93"],
          ["Exploring memory, 20% of agents", "3.15, 3.82", "4.28, 4.85, 3.14", "12.1", "137", "127", "9.96"],
          ["Exploring memory, 10% of agents", "3.79, 4.14", "4.87, 4.78, 4.41", "28.6", "141", "91.5", "8.3"],
          ["Slot recovery only", "3.56, 3.18", "3.19, 3.29, 3.38", "16.3", "107", "115", "9.3"]
        ]
      },
      items: [
        {name: "Superposition",
         component: "Move",
         why: "Real sounds add up. Moving along the sum of all sounds heard, rather than towards one source, might average out the side valleys of Rastrigin.",
         change: "After the 10% switch, each agent moved along the sum of the directions to all agents, each weighted by its loudness to the power $\\varphi$ ($\\varphi = 2$ or 1), towards fitter agents and away from worse ones.",
         setup: "c5, c8, p0, p1, p2; 31 runs.",
         result: "$\\varphi = 2$: Rastrigin slightly better (c5 3.15, c8 3.31; not significant), but all three F8 instances about twice as bad (6.96, 7.67, 7.35; significant). $\\varphi = 1$: c5 3.05, c8 2.89; F8 instances 7.81, 6.62, 7.68.",
         reading: "The averaged direction probably points inside HappyCat's ring rather than along it.",
         verdict: "worse"},
        {name: "Doppler",
         component: "Source choice",
         why: "A moving source sounds different ahead of it. Aiming at where a source is heading, rather than where it is, might lead agents along curved valleys such as HappyCat's ring.",
         change: "Aim at the source's position plus d times its last successful move (d = 0.5 or 1; d = 0 gives Encore).",
         setup: "c5, c8, p0, p1, p2; 31 runs.",
         result: "d = 0.5: c5 3.56, c8 3.63; F8 instances 4.91, 4.66, 4.67 (p0 significantly worse). d = 1: worse on 3 of 5 functions.",
         verdict: "worse"},
        {name: "Whole hops",
         component: "Move",
         why: "On a regular grid of valleys, the gap between two agents in different valleys is a whole number of grid steps. The random push adds this gap times the step size (0.1 to 0.5 late in the run), which lands on a ridge; adding the whole gap would land in another valley. The step-size memory cannot learn this, because small steps succeed more often.",
         change: "A share h of the agents add the random push in full (h = 0.1, 0.3 or 1).",
         setup: "c5, c8, p0, p1, p2; 31 runs.",
         result: "h = 0.1: c5 3.82, c8 3.27; F8 instances 4.76, 5.15, 4.51. h = 0.3: 3.98, 4.49; 5.13, 4.36, 4.82. h = 1: c5 4.9, c8 5.4; F8 instances up to 10.9.",
         reading: "On rotated functions agents do not sit at valley bottoms, so the gaps between them are not whole grid steps.",
         verdict: "worse"},
        {name: "Larger starting groups",
         component: "Group size",
         change: "270 or 360 agents at the start (27 or 36 per coordinate) instead of 180, still shrinking to 4.",
         setup: "c5, c8, p0, p1, p2; 31 runs.",
         result: "270: c5 3.43, c8 3.18; F8 instances 2.88, 4.56, 3.28. 360: 2.99, 3.56; 3.27, 4.41, 3.23. No significant change.",
         verdict: "none"},
        {name: "Floors on the hearing rate after the start",
         component: "Hearing rate",
         why: "The F8 parts are rotated and need several coordinates to move together, but the learned hearing rate falls to one coordinate. The early floor of entry 16 caused traps because it acted while the valley is chosen; a floor that starts later should leave that decision alone.",
         change: "From a set point (10%, 50% or 70% of the budget), at least a share ℓ of the coordinates move (ℓ = 0.3, 0.5 or 0.8), with memory slots that can recover. The 50% floor was also run keeping the sticky-slot rule, and on all 29 CEC 2017 functions.",
         setup: "Table 3 (31 runs); trap check with 51 runs; all of CEC 2017 with 30 runs.",
         result: "A floor of 0.8 from 10% cut the F8 instances about six-fold (0.43, 0.60, 0.62 against 3.43, 4.04, 3.89) and left Rastrigin unchanged, but rotated Schwefel rose from 92 to 264. A floor of 0.5 from 10% kept the traps at the baseline level over 51 runs (F22 trapped in 8 of 51 against 8) but F10 rose to 248 and F7 to 10.3. From 50%: F8 instances 0.92, 0.74, 0.61 and the F22 mean halved (9.9 against 20.2), with F10 158. On all 29 CEC 2017 functions the 50% floor was better on 4 (F11, F15, F23, F29) and worse on 3 (F10 99 to 173, F17 0.24 to 3.1, F20 0 to 0.29); the average ranks tied (p = 1). With the sticky rule kept, F10 was still 153, so the floor itself, not slot recovery, costs Schwefel.",
         reading: "Rotated Schwefel prefers moving one or two coordinates at a time, even late in the run. CEC 2017 F17, the design set's closest relative of CEC 2022 F8 (four of the five parts shared, with Rastrigin instead of HappyCat and twice the Schwefel share), got 13 times worse. Adopting the floor would have tailored the search to CEC 2022 F8 through stand-ins built from it.",
         verdict: "trade"},
        {name: "Some agents hear widely",
         component: "Hearing rate",
         why: "Rather than forcing every agent, let a share of agents move many coordinates while the rest keep the learned rate, and let selection keep whichever works.",
         change: "After 10% of the budget, a share w of the agents (w = 0.5 or 0.25), drawn anew at each iteration, move at least 0.8 of the coordinates. In a second form only the other agents' successes update the memory, so the wide movers do not raise everyone's learned rate.",
         setup: "Table 3 (31 runs); the half-wide form without the leak also on the full bench.",
         result: "With the shared memory: the F8 gain stayed (a quarter wide: 0.44, 0.93, 0.56), but F10 rose to 190 (a quarter) and 288 (half) against 92, and F7 to 10.8 to 11.1. Without the leak into the memory: F10 returned to 95 to 124, but the F8 gain was gone (3.78, 4.43, 3.83 for a quarter). Half wide without the leak: the Rastrigin gain was not significant (p = 0.16 and 0.24) and F10 was significantly worse (p = 0.035).",
         reading: "The useful part for F8 was the wide movers' successes pulling everyone's learned rate up, which is exactly what hurts Schwefel.",
         verdict: "trade"},
        {name: "Why the memory settles on narrow moves",
         component: "Diagnostic",
         change: "Traces through the run of the success rate, the gain per try, the new group bests and the rank gained per try, for narrow and for wide moves, on an F8 instance and on rotated Schwefel.",
         result: "Between 10% and 70% of the run, narrow moves win by every measure on both functions (on the F8 instance between 30% and 70%, a success rate of 0.023 to 0.036 for narrow moves against 0.004 to 0.006 for wide ones), longer-term measures included. In the last 30% wide moves win clearly on both, gaining 3 to 4 times as many ranks per try. Yet forcing wide moves ends about six times better on the F8 instances.",
         reading: "The payoff of wide moves comes late: narrow moves creep into dead ends such as the far side of HappyCat's ring. The memory never notices the late advantage, because after collapsing mid-run it no longer tries wide moves. It is stuck for lack of trying, not because it is short-sighted.",
         verdict: "check"},
        {name: "A hearing memory that keeps exploring",
         component: "Parameter memory",
         why: "If the memory is stuck for lack of trying (entry 28), making it keep trying should let it find the late value of wide moves without forcing them.",
         change: "At each iteration a share e of the agents (e = 0.2 or 0.1) draws its hearing rate uniformly from 0 to 1; slots can recover; all successes update the memory by gain as usual. Slot recovery alone was run as a control.",
         setup: "Table 3 (31 runs).",
         result: "e = 0.2: no F8 gain (4.28, 4.85, 3.14) and F10 worse (127 against 92). e = 0.1: no F8 gain, F22 mean 28.6. Recovery alone: no change.",
         reading: "Late in the run the group is down to a few dozen agents, too few to produce enough exploring successes to move the memory. This closed the line of work on the hearing memory.",
         verdict: "worse"}
      ]
    },
    {
      title: "Matching the differential evolution rule on Rastrigin",
      when: "Stand-in bench, 31 runs · baseline: Encore (c5 3.43, c10 70, F22 trapped in 4 of 31)",
      intro: "The comparison of entry 45 showed that the selection rule of differential evolution, towards a random one of the best few agents, does better on Rastrigin and Schwefel. Two sound-based changes tried to reproduce that property without its traps.",
      items: [
        {name: "Sound that carries further late",
         component: "Source choice",
         why: "If distance counted less late in the run, agents would hear more good sources and spread their moves, as the differential evolution rule does.",
         change: "From 30% or 50% of the run, intensity becomes $P_j^{\\kappa} / \\big(4\\pi (r_{ij}^2)^{e}\\big)$, with $e$ lowered from 1 to 0.5 or 0.",
         result: "No effect on Rastrigin (3.4 to 3.8 against 3.43); Schwefel worse (89 to 113 against 70); F22 trapped slightly less often (1 to 2 of 31 runs against 4).",
         reading: "Late in the run $\\kappa$ is already high, so loudness rather than distance decides which source is heard; weakening distance then changes little.",
         verdict: "none"},
        {name: "Equal picks among the loudest",
         component: "Source choice",
         why: "The differential evolution rule picks evenly among the best few agents, while noisy hearing still favours the loudest.",
         change: "Pick evenly among the sources whose intensity lies within a band below the loudest.",
         result: "No effect on Rastrigin, Schwefel or the F8 instances; F10 worse (107 against 70) when it starts at 30% of the run.",
         verdict: "none"}
      ]
    },
    {
      title: "New kinds of change",
      when: "Stand-in bench, 12 functions, 31 runs; the best variant also on all of CEC 2017 · baseline: Encore",
      intro: "The changes so far altered whom an agent hears or how many coordinates it moves, and inside this framework the differential evolution rule is as weak as listening on CEC 2022 F8 and F2. This round tried changes of a different kind, drawn from peafowl displays (infrasound, leks) and from other properties of sound. Baseline on the bench: c5 3.43, c8 3.43; p0, p1, p2 3.43, 4.04, 3.89; c22 16.3 (4 of 31 trapped); c24 100 (31 of 31 at 100); c10 70; c7 9.97; c12 0.87; c17 0.28. Table 4 gives the trap counts behind the main finding of the round.",
      table: {
        caption: "Table 4. Stand-in bench, 31 runs. c5: CEC 2017 F5, mean error; c22: CEC 2017 F22, runs trapped; c24: CEC 2017 F24, runs ending at about 100. - not recorded.",
        head: ["Variant", "c5", "c22 trapped", "c24 at 100"],
        rows: [
          ["Encore (baseline)", "3.43", "4 of 31", "31 of 31"],
          ["Infrasound", "2.57", "22 of 31", "4 of 31"],
          ["Two leks walled apart", "2.89", "12 of 31", "17 of 31"],
          ["A chooser between the leks", "-", "12 of 31", "17 of 31"],
          ["Encore with half the agents", "-", "7 of 31", "27 of 31"],
          ["Encore with half the evaluations", "-", "12 of 31", "28 of 31"],
          ["Encore with both halved", "-", "11 of 31", "21 of 31"],
          ["Ears that turn with the group", "3.69", "6 of 31", "22 of 31"],
          ["Switch to infrasound at 10%", "2.66", "5 of 31", "30 of 31"],
          ["Switch to infrasound at 20%", "2.98", "2 of 31", "-"],
          ["Half the agents switch at 10%", "3.15", "3 of 31", "29 of 31"]
        ]
      },
      items: [
        {name: "Infrasound",
         component: "Source choice",
         why: "Peafowl displays include infrasound, which travels far with little loss. A group in which every agent is heard regardless of distance should behave like the differential evolution rule.",
         change: "Loudness does not fade with distance, $\\kappa$ stays at 8, and sources are picked at random in proportion to loudness from the start.",
         result: "Better on Rastrigin and the F8 instances (c5 2.57, c8 2.57; p0 1.21, p1 2.46, p2 1.48); worse on c22 (71.9, trapped in 22 of 31 runs against 4), c24 (301, at 100 in 4 of 31 against 31), c7, c12 and c21; no different on c10 and c17. Friedman p = 0.56.",
         reading: "The first sound-only rule to match the differential evolution rule on Rastrigin; it also inherits that rule's traps.",
         verdict: "trade"},
        {name: "Two leks walled apart",
         component: "Group structure",
         why: "A lek is a group of displaying males. Two walled groups, one hearing as in Encore and one hearing infrasound, should each keep its own strength.",
         change: "The starting group is split in half, and no sound, push partner or echo crosses between the halves for the whole run; the lek with the better best agent finishes with the refinement.",
         result: "Better on c5 (2.89), c8 (2.60), p0 (1.64) and p2 (2.80); worse on c22 (48.1, trapped in 12 of 31), c24 (190, at 100 in 17 of 31) and c12 (10.1). Against infrasound alone: 2 better, 1 worse, 9 no different.",
         verdict: "trade"},
        {name: "A chooser between the leks",
         component: "Control",
         why: "A hyper-heuristic again, now choosing between strategies that really differ. A trace showed that Encore's hearing gets below the decoy value on F22 by 10 to 15% of the budget in 6 of 8 runs, infrasound in only 2 of 8 and only at 86 to 89%, so a check after 15% can tell them apart.",
         change: "Two walled leks. From 15% of the budget, every 5%, the lek whose best agent is worse keeps only 70% of its planned size, and its evaluations go to the other.",
         result: "Against walled leks of fixed size: 0 better, 2 worse, 10 no different. Against Encore: better on p2, worse on c22 (47.8), c24 (194), c7 (11.8) and c12 (64.2); Friedman rank 2.83 of 4 (p = 0.57). Trap counts were identical to those of the fixed leks.",
         reading: "Both share the first 15% of the budget, during which the Encore lek has half the agents and half the evaluations. Entry 35 shows that this alone costs the protection.",
         verdict: "worse"},
        {name: "Why splitting fails",
         component: "Diagnostic",
         change: "Encore alone, run with half the agents (90), half the evaluations, or both.",
         result: "c22 trapped in 7, 12 and 11 of 31 runs against 4; c24 at 100 in 27, 28 and 21 of 31 against 31. With both halved the counts match the walled leks (12 and 17 of 31).",
         reading: "Halving the evaluations from the start, more than halving the agents, costs the trap protection. Any portfolio or allocation scheme that splits the budget at the start pays this cost, and no chooser acting later can undo it.",
         verdict: "check"},
        {name: "Ears that turn with the group",
         component: "Hearing rate",
         why: "On rotated functions the coordinate axes are arbitrary; hearing along the group's own main directions should help rotated Rastrigin.",
         change: "Half of the agents, picked at random each iteration, decide which parts of the move are heard along the main directions (principal axes) of the better half of the group instead of the coordinate axes; the move itself is unchanged.",
         result: "0 better, 2 worse (c10 149 against 70, c17 0.50 against 0.28), 10 no different. No Rastrigin gain (c5 3.69, c8 3.66).",
         reading: "Rotated Schwefel again prefers moves along the axes.",
         verdict: "worse"},
        {name: "Echolocation",
         component: "Move",
         why: "Encore remembers where agents were but not how good those places were, so every move is a blind try. Judging moves before making them could save evaluations.",
         change: "Every evaluated point is stored with its value (the most recent 50 per coordinate, 500 at 10 coordinates, plus the current group). After 10% of each group search each agent drafts three moves, rates each from the three nearest stored points weighted by inverse distance, and evaluates only the best-rated draft. No extra evaluations are spent.",
         result: "More moves improved between 20% and 40% of the run (14% against 5% on c5), fewer in the last 30% (4.5% against 8.3%). Final errors were unchanged over two seeds, and the idea was not run further.",
         verdict: "none"},
        {name: "Switching to infrasound at 10%",
         component: "Source choice",
         why: "Entry 18 places the trap decision in the first few percent of the budget. Hearing as in Encore until then and as infrasound afterwards should keep the protection and gain the Rastrigin behaviour, with nothing split.",
         change: "Encore's hearing for the first 10% of the run, then infrasound, in one group. A switch at 20% was also run.",
         setup: "Stand-in bench (31 runs), then all 29 CEC 2017 functions (30 runs).",
         result: "Bench: better on c5 (2.66), c8 (2.44), p0 (2.26) and p2 (2.02); worse on c7 (12.1 against 9.97) and c12 (27.6 against 0.87); traps kept (c22 5 of 31, c24 at 100 in 30 of 31). All of CEC 2017: better on 7, worse on 5, no different on 17; Friedman 1.47 for Encore against 1.53 (p = 0.68; Holm adjusted p = 0.71). Better: F5 2.82 against 3.32, F8 2.19 against 3.35, F11, F16, F19, F22 (8.5 against 21.1; trapped 2 of 30 against 5), F23. Worse: F7 12.2 against 8.6, F12 2.15 against 0.14 (5 of 30 runs end near 11), F13 3.6 against 2.0, F18 0.40 against 0.008, F27. Switching at 20% was weaker (c5 2.98, c10 117).",
         reading: "The first change that kept the traps and gained on Rastrigin, but it loses on the hybrid functions, where one group contains parts that need near and far hearing at the same time.",
         verdict: "trade"},
        {name: "Only some agents switch",
         component: "Source choice",
         why: "If the whole group switching loses the hybrids, letting only part of it switch might keep some of each behaviour.",
         change: "After 10%, each agent hears infrasound with probability 0.5 or 0.25 at each iteration; the rest keep Encore's hearing.",
         result: "0 better and 0 worse on all 12 bench functions for both shares. Share 0.5: c5 3.15, c8 3.18, p0 2.83, p2 3.03, c12 0.148 with no bad runs, c22 trapped in 3 of 31. Share 0.25: c12 5.06, c10 108. Friedman over the 12 functions: full switch 2.04, share 0.5 2.21, Encore 2.75, share 0.25 3.00 (p = 0.22).",
         reading: "The Rastrigin gain and the hybrid loss move together; no share keeps one without the other.",
         verdict: "none"}
      ]
    },
    {
      title: "A stronger endgame and a new algorithm",
      when: "Stand-in bench with the q instances, 8 to 31 runs; CEC 2022 for the endgame · baseline: Encore",
      intro: "Two further lines relaxed the constraint that sound is the only way agents move: a stronger endgame, and a new method, here called Valley Hopper, built on settling points into valleys and hopping between them.",
      items: [
        {name: "A population CMA-ES endgame",
         component: "Endgame",
         why: "The (1+1)-CMA-ES refinement cannot leave the valley it starts in. A population CMA-ES whose population doubles at each restart (IPOP; Auger & Hansen, 2005) can still search several valleys at the end of the run.",
         change: "The last 10% of the evaluations go to an IPOP CMA-ES instead of the (1+1)-CMA-ES.",
         setup: "Bench, 15 runs; then CEC 2022 at 10 coordinates, 30 runs, as a finished change.",
         result: "Bench: average rank 1.55 against 1.45; only q4x1 better (2.59 against 3.65). CEC 2022: F4 better (2.6 against 3.48, significant); F7 (0.122 against 0.027) and F8 (2.86 against 1.94) worse, not significantly; Friedman 1.50 against 1.50. Against the 12 entries: 4th of 13, average rank 6.17 against 6.00, inside the range of Encore itself over three sets of seeds (5.50 to 6.17).",
         verdict: "trade"},
        {name: "Valley Hopper with settling",
         component: "New method",
         why: "On a field of valleys, comparing points that sit at valley bottoms says more than comparing points on the slopes, and the gaps between settled points are whole valley steps.",
         change: "Each new point first takes a few short downhill steps (20 or 40; 0 means no settling). Agents then hop towards a nearby better point plus the gap between two others, with crowding (a newcomer competes with its nearest group member), a shrinking group and Encore's endgame.",
         setup: "8 runs on c5, c8, p0, q4x0 and c22.",
         result: "Rastrigin about twice as bad as Encore at every setting (c5 6.84, 8.58 and 8.96 for 0, 20 and 40 steps, against 3.43). Settling kept c22 out of the trap (0 of 8 runs) but runs ended near 30 instead of 0. Without settling, p0 was 1.58 against 3.43.",
         reading: "Settling spends evaluations without improving the choice of valley; the stop rule set in advance was met.",
         verdict: "worse"},
        {name: "Valley Hopper without settling",
         component: "New method",
         change: "Crowding, and a hop towards a nearby better point plus the gap between two other points, moving all coordinates at once; no crossover.",
         setup: "19 bench functions, 31 runs.",
         result: "6 better, 10 worse, 3 no different; Friedman 1.58 against 1.42 (p = 0.47). Better: F8 instances (1.53, 2.03, 1.84 against 3.43, 4.04, 3.89), q8x0 (1.45 against 4.01), the F7 forms q7x0 (0.90 against 8.65) and q7x1 (1.27 against 8.98). Worse: c5 7.7, c8 6.64, q4x0 5.62 against 3.15, c10 443 against 70, c22 trapped in 18 of 31 against 4, c24 145, c7 18, c17 18.9 against 0.28.",
         reading: "Its strengths are the mirror image of Encore's.",
         verdict: "trade"},
        {name: "Valley Hopper's parts",
         component: "New method",
         change: "The nearby-better target replaced by any better point; crowding replaced by competition with the parent.",
         setup: "19 bench functions, 31 runs.",
         result: "The nearby target made no difference (0 better, 0 worse, 19 no different). Without crowding: better on 11 and worse on 3, with Rastrigin back near Encore (c5 3.82) and the hybrids better still (q7x0 0.60, q7x1 0.54). This best form against Encore: 6 better, 8 worse, 5 no different (Friedman p = 0.64), with c22 trapped in 28 of 31 and c10 309.",
         reading: "The hybrid gain comes from the plain all-coordinates hop. It is the same trade-off as the late hearing floor: moving all coordinates helps F7 and F8 and costs Schwefel, CEC 2017 F17 and the traps. The nearby-better target, the part that echoes the sound model, does nothing here.",
         verdict: "trade"},
        {name: "Encore first, then the hop",
         component: "New method",
         why: "Keep Encore during the trap decision and use the hop afterwards.",
         change: "Encore for the first 10% (or 30%) of the run, then the hop of Valley Hopper.",
         setup: "19 bench functions, 31 runs; switching off the hop reproduced Encore exactly.",
         result: "At 10%: 6 better, 6 worse, 7 no different (Friedman 1.55 against 1.45, p = 0.64). The traps returned to Encore's level (c22 trapped in 6 of 31) and most of the hybrid gain stayed (q7x0 1.67, p0 1.56), but Rastrigin (c5 5.23), Schwefel (c10 627 against 70), c7 (14.9) and c17 (22.6) were worse. At 30%: 3 better, 7 worse.",
         reading: "Rastrigin, Schwefel, F7 and F17 need Encore's moves for the whole run, not only at the start.",
         verdict: "trade"}
      ]
    },
    {
      title: "Other methods' selection rules in place of listening",
      when: "All of CEC 2017 and CEC 2022 at 10 coordinates, 30 runs, the seeds of Encore · baseline: Encore",
      intro: "To test whether the sound model adds anything to related methods, only the rule deciding whom an agent moves towards was replaced, keeping every other part of Encore: step sizes, hearing rate, random push, shrinking, restarts and refinement. None of the replacement rules uses loudness or $\\kappa$, and all always move towards. These are the selection rules of the related methods, not the complete methods: the firefly algorithm's random step and the swarm's velocities are not used. Table 5 summarises the results.",
      table: {
        caption: "Table 5. Selection rules inside the Encore framework. ‘Listening / rule’: functions where each is significantly better (Wilcoxon, 5%). F22: runs trapped; F24: runs ending at 100 or less; CEC 2022 F10: runs escaping the trap (error below 50). Rastrigin: mean errors on CEC 2017 F5, F8 and CEC 2022 F4, F8. Out of 30 runs.",
        head: ["Rule", "CEC 2017 listening / rule", "CEC 2022 listening / rule", "F22 trapped", "F24 at 100", "CEC 2022 F10 escaping", "CEC 2017 F5, F8", "CEC 2022 F4, F8"],
        rows: [
          ["Listening (Encore)", "-", "-", "5", "28", "6", "3.32, 3.35", "3.48, 1.94"],
          ["Differential evolution, best 11%", "7 / 7", "2 / 3", "28", "8", "0", "2.29, 2.59", "2.39, 1.24"],
          ["Firefly", "8 / 6", "3 / 2", "26", "11", "0", "2.82, 2.52", "2.55, 1.53"],
          ["Fitness-distance ratio, whole distance", "3 / 1", "1 / 2", "22", "20", "1", "3.48, 3.42", "3.22, 0.681"],
          ["Fitness-distance ratio, per coordinate", "15 / 0", "5 / 0", "6", "26", "11", "5.37, 5.97", "7.36, 4.88"]
        ]
      },
      items: [
        {name: "The differential evolution rule",
         component: "Source choice",
         why: "Much of Encore is borrowed from differential evolution, so the sharpest test of the sound model is the usual selection rule of differential evolution in its place.",
         change: "Each agent moves towards a random one of the best p of the group, always towards: the current-to-pbest rule (Zhang & Sanderson, 2009), which with the random push is the move of L-SHADE (Tanabe & Fukunaga, 2014). Two forms: p = 11% (L-SHADE), and p from 25% shrinking to 12.5% over each group search (jSO; Brest et al., 2017).",
         result: "Best 11%: listening better on 7 CEC 2017 functions and the rule on 7; on CEC 2022, 2 and 3. jSO form: 7 and 6; 3 and 2. No overall difference on either set by the Friedman and Holm tests. The rule wins on Rastrigin and Schwefel (CEC 2017 F5 2.29 against 3.32, F10 43 against 99; CEC 2022 F4 2.39 against 3.48, and F7); listening wins on the traps and blends (CEC 2017 F22 21 against 93, trapped in 5 of 30 runs against 28; F24 111 against 269; F12; F18; CEC 2022 F6 and F12). On CEC 2022 F10 listening has the lower mean (81 against 100) because 6 of 30 runs escape, but its 24 trapped runs end a little higher in the trap valley (median 100.26 against 100.21), so the rank-sum test favours the rule (best 11% form) or finds no difference (jSO form).",
         reading: "The two rules tie overall and are strong in different places, so listening is an alternative to the differential evolution rule rather than a relabelling of it.",
         verdict: "trade"},
        {name: "The firefly rule",
         component: "Source choice",
         why: "In the firefly algorithm (Yang, 2009) an agent is drawn to every brighter agent, more weakly the farther away it is: the closest relative of hearing a sound that fades with distance.",
         change: "One brighter agent per move, picked with probability proportional to $\\exp(-\\gamma r^2)$, where $\\gamma$ is one over the mean squared distance between agents, so the fade follows the spread of the group.",
         result: "CEC 2017: listening better on 8 functions, the rule on 6; CEC 2022: 3 and 2; no overall difference. It behaves like the differential evolution rule: Rastrigin better (CEC 2017 F8 2.52 against 3.35; CEC 2022 F4 2.55 against 3.48, F7), traps worse (F22 trapped in 26 of 30; F24 at 100 in 11 of 30).",
         verdict: "trade"},
        {name: "Fitness-distance ratio over the whole distance",
         component: "Source choice",
         why: "Fitness-distance-ratio particle swarm optimisation (Peram et al., 2003) follows the better particle with the largest gain in value per unit of distance, which weighs both quality and distance, as hearing does.",
         change: "Move towards the better agent $j$ with the largest $\\big(f(x_i) - f(x_j)\\big) / \\lVert x_j - x_i \\rVert$.",
         result: "CEC 2017: listening better on 3 functions, the rule on 1; F22 trapped in 22 of 30, with no Rastrigin gain (F5 3.48). CEC 2022: listening better on 1, the rule on 2; the best average rank of the five rules (2.38 against 2.79 for listening; Friedman p = 0.18), from F7 and F8 (0.681 against 1.94). Among the competition entries it would also be 4th (average rank 5.88 against 6.00).",
         reading: "Adopting it would mean choosing on the test set; on the design set it is a little behind listening.",
         verdict: "trade"},
        {name: "Fitness-distance ratio per coordinate",
         component: "Source choice",
         why: "Peram et al. (2003) apply the ratio to each coordinate separately.",
         change: "For each coordinate $d$, move towards the better agent $j$ with the largest $\\big(f(x_i) - f(x_j)\\big) / \\lvert x_{jd} - x_{id} \\rvert$, so each coordinate can follow a different agent; the random push is unchanged.",
         result: "It keeps the trap protection (F22 trapped in 6 of 30; CEC 2022 F10 escaped in 11 of 30 against 6) but is worse on 15 CEC 2017 functions and better on none (Holm adjusted p = 0.017), and worse on 5 CEC 2022 functions. Its Rastrigin errors are 1.6 to 2.5 times those of listening, and CEC 2017 F30 rises to 808 against 395.",
         reading: "When each coordinate follows a different agent, a move no longer points at any one agent, which likely spoils fine search.",
         verdict: "worse"}
      ]
    },
    {
      title: "Results that did not hold up",
      when: "Checked with more runs or new seeds",
      intro: "Several early readings changed when the experiment was repeated. They are reported here because each one changed a decision.",
      items: [
        {name: "Step 10's gain on CEC 2022 F10",
         component: "Replication",
         change: "With step 10, 6 of 30 runs escaped the CEC 2022 F10 trap (mean 81 against 98 for steps 8 and 9). Encore was rerun with two new sets of seeds, 30 runs each.",
         result: "2 of 30 and then 0 of 30 runs escaped (means 94.2 and 100.2). The standing held: 4th of 13 on all three sets of seeds, with average ranks 6.00, 5.50 and 6.17, and no entry ever significantly better. F4 stayed better than before step 10 (3.81 and 3.88).",
         reading: "The F10 gain was luck. Later changes on CEC 2022 are judged against the range 5.50 to 6.17, not against 6.00.",
         verdict: "luck"},
        {name: "$\\kappa$ starting at 0 cuts traps",
         component: "Replication",
         change: "At 20 runs, $\\kappa$ starting at 0 trapped F22 in 3 runs against 7 for the baseline.",
         result: "$\\kappa$ from 0 to 8 trapped 7 of 20; over 51 runs, $\\kappa$ from 0 to 8 with 10% refinement trapped 11 of 51 against 14, not significantly different.",
         reading: "With a trap rate near 35%, 20 runs vary by about 2 trapped runs either way (Section 4.4).",
         verdict: "luck"},
        {name: "Hearing loss with age cuts traps",
         component: "Replication",
         change: "At 20 runs, hearing loss with age trapped F22 in 5 runs against 7.",
         result: "At 51 runs: 15 of 51 against 14.",
         verdict: "luck"},
        {name: "An early dismissal of the switch",
         component: "Replication",
         change: "An 8-run first look at switching to infrasound at 20% and 40% of the run (c5 2.86 and 3.73, c10 132 and 186) was read as a failure.",
         result: "At 31 runs the switch at 10% was the strongest variant of its round (entry 38). The 8-run look was misleading because c10 is bimodal: runs end either near 4 or between 140 and 250.",
         reading: "Small samples can hide an effect as easily as invent one.",
         verdict: "luck"}
      ]
    }
  ],

  discussion: [
    {heading: "One trade-off behind most failures",
     paras: [
       "Most entries fall along one line (Table 6). Hearing near neighbours first keeps sub-groups in separate valleys and protects against deceptive traps. Hearing good agents from anywhere, or moving many coordinates at once, crosses regular fields of valleys (Rastrigin, Schwefel) and hybrid functions faster. Every change that gained on one side lost on the other: noisy hearing from the start (entry 20), infrasound (entry 32), walled leks (entry 33), the differential evolution, firefly and whole-distance ratio rules (Section 3.8) gained on Rastrigin and fell into traps; masking (entry 17) and the per-coordinate ratio rule (entry 48) kept the protection and lost fine search.",
       "A second axis concerns how many coordinates move. Floors on the hearing rate (entries 16 and 26), wide movers (entry 27) and the all-coordinates hop (entries 42 to 44) helped the CEC 2022 F7 and F8 forms by factors of 2 to 10, and cost rotated Schwefel, CEC 2017 F17 and the traps. Scheduling (switching at 10%, entry 38), splitting (leks, entry 33), choosing (hyper-heuristics at five levels, entries 7 to 10 and 34) and mixing (a share of agents, entry 39) were the four ways tried to obtain both sides. Each either gave up the protection or lost elsewhere."
     ],
     table: {
       caption: "Table 6. Trap protection against progress on rotated Rastrigin: CEC 2017 F22, runs trapped; CEC 2017 F5, mean error; and the functions on which each variant is significantly worse than Encore. Within each block the seeds are the same.",
       head: ["Variant", "F22 trapped", "F5", "Significantly worse on"],
       rows: [
         "Stand-in bench, 31 runs",
         ["Encore", "4 of 31", "3.43", "-"],
         ["Infrasound", "22 of 31", "2.57", "c22, c24, c7, c12, c21"],
         ["Two leks walled apart", "12 of 31", "2.89", "c22, c24, c12"],
         ["Switch to infrasound at 10%", "5 of 31", "2.66", "c7, c12"],
         ["Half the agents switch at 10%", "3 of 31", "3.15", "none (and better on none)"],
         ["Ears that turn with the group", "6 of 31", "3.69", "c10, c17"],
         ["Valley Hopper without settling", "18 of 31", "7.7", "10 of 19 functions"],
         ["Encore first, then the hop", "6 of 31", "5.23", "6 of 19 functions"],
         "All 29 CEC 2017 functions, 30 runs",
         ["Encore", "5 of 30", "3.32", "-"],
         ["Differential evolution rule", "28 of 30", "2.29", "7 functions"],
         ["Firefly rule", "26 of 30", "2.82", "8 functions"],
         ["Fitness-distance ratio, whole distance", "22 of 30", "3.48", "3 functions"],
         ["Fitness-distance ratio, per coordinate", "6 of 30", "5.37", "15 functions"],
         ["Switch to infrasound at 10%", "2 of 30", "2.82", "5 functions (F7, F12, F13, F18, F27)"]
       ]
     }},
    {heading: "The trap is decided early",
     paras: [
       "On CEC 2017 F22 the group commits to a valley within the first 3 to 6% of the budget (entry 18). Three results follow. Changes that make the group gather sooner, such as a hearing floor or noisy hearing in the first 10%, raise the trap rate. Changes that act later, such as masking during shrinking or a chooser that reallocates after 15%, cannot lower it. And changes that split the budget at the start lose the protection even when the half that keeps Encore's hearing is unchanged: halving the evaluations alone triples the trap count (entry 35). A ‘childhood’ in which no agent listens does not help either, because the group still gathers within a few percent once listening starts."
     ]},
    {heading: "The memory learns from what works immediately",
     paras: [
       "Step sizes and hearing rates are learned from moves that improved an agent at once. Small one-coordinate moves succeed most often, so the memory settles on them, and a slot that reaches 0 stays there. Wide moves pay off only late in the run, when the memory no longer tries them (entry 28). Forcing wide moves helps the hybrids and hurts Schwefel (entries 26 and 27); letting a share of agents explore does not produce enough late successes to move the memory (entry 29). This mechanism is borrowed from SHADE, so the observation probably applies to methods of that family as well, though that was not tested."
     ]},
    {heading: "Small samples and single seed sets mislead",
     paras: [
       "Gains seen in 20 runs, or on one set of seeds, did not hold (Section 3.9), and an 8-run look once dismissed the strongest variant of its round. The trap rate is a proportion, so its noise is easy to estimate: with a rate near 35%, the number trapped in 20 runs has a standard deviation of about 2.1 runs. Telling 35% from 15% with a two-sided test at the 5% level needs about 57 runs per variant for 70% power and about 72 for 80% power. The 51-run trap checks used here are close to the lower figure; the 20-run screens could detect only very large differences. Per-function counts of significant wins and losses carry their own noise: at the 5% level about 1.5 of 29 functions differ by chance alone, which is why overall decisions rest on the Friedman and Holm tests."
     ]},
    {heading: "What the sound rule contributes",
     paras: [
       "Listening ties with the differential evolution rule overall and is the only one of the five selection rules in Table 5 that avoids the traps without being worse overall. The rules that cross fields of valleys well (differential evolution, firefly, whole-distance ratio) are trapped on CEC 2017 F22 in 22 to 28 runs of 30, against 5 for listening; the one that avoids the traps (the per-coordinate ratio) is significantly worse overall. The protection comes from the property that defines the sound model: early in each group search an agent hears its neighbours more than distant good agents. Infrasound, which removes that property, behaves like the differential evolution rule (entry 32)."
     ]}
  ],

  threats: [
    "Design and test separation. The stand-ins p and q are new random instances of CEC 2022 function definitions, so using them steers the design towards the structure of the test set. Changes justified mainly by these stand-ins (the late hearing floor) were rejected unless they also held on the whole of CEC 2017, and CEC 2022 itself was never used to choose between variants. The CMA-ES endgame was run on CEC 2022 once, as a finished change.",
    "Changing baselines. Each stage compares with the version of its time, so numbers from different stages are not comparable (for example, CEC 2017 F5 is 4.14 before step 10 and 3.32 to 3.43 after).",
    "Sample sizes. Many screens used 8 to 20 runs; a variant rejected on a small screen may have a small real effect, and entry 52 shows one such false negative. Rejected variants were rarely screened again.",
    "One set of seeds. Common random numbers reduce the noise between variants but not the dependence on the seed set itself (entry 49).",
    "One change at a time. Interactions between rejected changes were mostly untested; the exceptions are the combined settings ($\\kappa$ from 0 to 8 with 10% refinement) and the life cycle combined with those settings.",
    "Dimension and budget. Nearly all comparisons are at 10 coordinates. Only the adopted version was checked on CEC 2017 at 30 coordinates and on CEC 2022 at 20 coordinates.",
    "Re-implementation. The related methods were represented by their selection rules inside Encore, not by the complete algorithms with their own parameter settings; the conclusions concern the rules, not the published methods.",
    "Multiplicity. Per-function Wilcoxon tests are not corrected for the number of functions; Section 4.4 discusses the consequence."
  ],

  conclusion: [
    "Of the {N} entries, three changes improved on their baseline across the design set without a matching loss elsewhere: restarts, a shrinking group and less exact hearing after the start, which together turn Echo into Encore. None of the others did; the {k} that were partly kept entered Encore only in a changed form. The failures are not scattered: they fall along a trade-off between protection against deceptive traps, which needs local hearing during the first few percent of the budget, and progress on regular fields of valleys and hybrid functions, which needs wide moves and far hearing later. Scheduling, splitting, choosing and mixing all failed to obtain both. The sound rule itself held up: among five selection rules tested in one framework, it was the only one that avoided the traps without being worse overall.",
    "Directions that remain open are tests on niching benchmarks, where keeping sub-groups apart is the aim rather than a side effect; more seeds at 20 coordinates, where the F10 trap was escaped in 22 of 30 runs with a single set of seeds; and problems from applications."
  ],

  references: [
    ["Auger, A. & Hansen, N. (2005). A restart CMA evolution strategy with increasing population size. 2005 IEEE Congress on Evolutionary Computation, 2, 1769-1776.", "https://doi.org/10.1109/CEC.2005.1554902", {"checked": "Checked on Crossref: authors, year, title, venue, pages and DOI match.", "evidence": [{"for": "an IPOP CMA-ES doubles its population at each restart", "quote": "an independent restart is launched with the population size increased by a factor of 2.", "where": "Section 2, The restart CMA-ES", "src": "open copy of the conference paper"}, {"for": "a larger population searches more widely", "quote": "By increasing the population size the search characteristic becomes more global after each restart.", "where": "Abstract", "src": "publisher's record via OpenAlex"}]}],
    ["Awad, N. H., Ali, M. Z., Suganthan, P. N., Liang, J. J. & Qu, B. Y. (2016). Problem definitions and evaluation criteria for the CEC 2017 special session and competition on single objective real-parameter numerical optimization. Technical report.", "https://github.com/P-N-Suganthan/CEC2017-BoundContrained", {"checked": "Checked against the technical report in the organisers' repository (github.com/P-N-Suganthan/CEC2017-BoundContrained).", "evidence": [{"for": "29 functions", "quote": "We encourage all researchers to test their algorithms on the CEC’17 test suite which includes 29 benchmark functions.", "where": "Section 1, Introduction to the CEC’17 Benchmark Suite", "src": "technical report, final updated version"}, {"for": "100,000 evaluations at 10 coordinates", "quote": "MaxFES: 10000*D (Max_FES for 10D = 100000; for 30D = 300000; for 50D = 500000; for 100D = 1000000)", "where": "Section 2.1, Experimental Setting", "src": "technical report, final updated version"}], "note": "The updated report numbers the 29 functions 1 to 29; this report uses the original numbering, F1 and F3 to F30, in which F2 was withdrawn (Section 2.2)."}],
    ["Brest, J., Sepesy Maučec, M. & Bošković, B. (2017). Single objective real-parameter optimization: Algorithm jSO. 2017 IEEE Congress on Evolutionary Computation, 1311-1318.", "https://doi.org/10.1109/CEC.2017.7969456", {"checked": "Checked on Crossref: authors, year, title, venue, pages and DOI match.", "evidence": [{"for": "jSO as an L-SHADE variant", "quote": "The algorithm is an improved variant of the iL-SHADE algorithm, mainly with a new weighted version of mutation strategy.", "where": "Abstract", "src": "publisher's record via OpenAlex"}, {"for": "hearing-rate floors of 0.7 and 0.6, memory that can recover from 0, and p from 25% to 12.5%", "quote": "if (nfes< 0.25*max_num_evaluations && pop_cr[target] < 0.7) pop_cr[target] = 0.7;    // jSO\nif (nfes< 0.50*max_num_evaluations && pop_cr[target] < 0.6) pop_cr[target] = 0.6;    // jSO\nmemory_cr[memory_pos] = (memory_cr[memory_pos] + old_cr)/2.0;\np_best_rate = g_p_best_rate * (1.0 - 0.5*nfes /  (double)max_num_evaluations);   // JANEZ\n(main.cc: g_p_best_rate = 0.25;)", "where": "lshade.cc and main.cc", "src": "the authors' source code released with the paper (CEC 2017 competition repository, jSO-SOURCE-RESULTS)", "code": true}], "note": "The full text of the paper is not openly available, so the parameter values are shown from the authors' own code."}],
    ["Burke, E. K., Kendall, G. & Soubeiga, E. (2003). A tabu-search hyperheuristic for timetabling and rostering. Journal of Heuristics, 9(6), 451-470.", "https://doi.org/10.1023/B:HEUR.0000012446.94732.b6", {"checked": "Checked on Crossref: authors, year, title, venue, pages and DOI match.", "evidence": [], "note": "Neither the abstract nor the full text could be retrieved from an open source, so no passage is quoted. The citation is for the idea of a hyper-heuristic, which is the subject of the paper."}],
    ["Camacho-Villalón, C. L., Dorigo, M. & Stützle, T. (2023). Exposing the grey wolf, moth-flame, whale, firefly, bat, and antlion algorithms: six misleading optimization techniques inspired by bestial metaphors. International Transactions in Operational Research, 30(6), 2945-2971.", "https://doi.org/10.1111/itor.13176", {"checked": "Checked on Crossref: authors, year, title, venue, pages and DOI match.", "evidence": [{"for": "metaphor-based methods restate known methods under new names", "quote": "Our result is that the ideas proposed in the six studied algorithms have been in the literature of metaheuristics for years and that the only novelty in these self‐proclaimed novel algorithms is six different terminologies derived from the use of new metaphors.", "where": "Abstract", "src": "publisher's record via Crossref"}]}],
    ["Demšar, J. (2006). Statistical comparisons of classifiers over multiple data sets. Journal of Machine Learning Research, 7, 1-30.", "https://www.jmlr.org/papers/v7/demsar06a.html", {"checked": "Checked against the open-access article on jmlr.org: authors, year, title, volume and pages match.", "evidence": [{"for": "the Friedman test for comparing several methods", "quote": "we recommend a set of simple, yet safe and robust non-parametric tests for statistical comparisons of classifiers: the Wilcoxon signed ranks test for comparison of two classifiers and the Friedman test with the corresponding post-hoc tests for comparison of more classifiers over multiple data sets.", "where": "Abstract", "src": "open-access article (JMLR)"}, {"for": "Holm's step-down correction when each method is compared with a control", "quote": "When all classifiers are compared with a control classifier, we can instead of the Nemenyi test use one of the general procedures for controlling the family-wise error in multiple hypothesis testing, such as the Bonferroni correction or similar procedures.", "where": "Section 3.2.2, Friedman Test", "src": "open-access article (JMLR)"}, {"for": "Holm's procedure", "quote": "Holm’s step-down procedure starts with the most significant p value.", "where": "Section 3.2.2, Friedman Test", "src": "open-access article (JMLR)"}]}],
    ["Derrac, J., García, S., Molina, D. & Herrera, F. (2011). A practical tutorial on the use of nonparametric statistical tests as a methodology for comparing evolutionary and swarm intelligence algorithms. Swarm and Evolutionary Computation, 1(1), 3-18.", "https://doi.org/10.1016/j.swevo.2011.02.002", {"checked": "Checked on Crossref: authors, year, title, venue, pages and DOI match.", "evidence": [], "note": "Neither the abstract nor the full text could be retrieved from an open source, so no passage is quoted. The citation is for the use of the Friedman test with post-hoc corrections to compare evolutionary algorithms, the subject of the tutorial."}],
    ["Igel, C., Suttorp, T. & Hansen, N. (2006). A computational efficient covariance matrix update and a (1+1)-CMA for evolution strategies. Proceedings of GECCO 2006, 453-460.", "https://doi.org/10.1145/1143997.1144082", {"checked": "Checked on Crossref: authors, year, title, venue, pages and DOI match.", "evidence": [{"for": "the (1+1)-CMA-ES used for the final refinement", "quote": "First, the covariance matrix adaptation (CMA) with rank-one update is introduced into the (1+1)-evolution strategy. An improved implementation of the 1/5-th success rule is proposed for step size adaptation, which replaces cumulative path length control.", "where": "Abstract", "src": "publisher's record via OpenAlex"}]}],
    ["Kenekayoro, P. (2021). A meta-heuristic search algorithm based on infrasonic mating displays in peafowls. Journal of Advances in Mathematics and Computer Science, 36(5), 98-106.", "https://doi.org/10.9734/JAMCS/2021/v36i530366", {"checked": "Checked on Crossref: authors, year, title, venue, pages and DOI match.", "evidence": [{"for": "the method's original name", "quote": "This research proposes an Infrasonic Search Algorithm, inspired from the Gravitational Search Algorithm and the mating behaviour in peafowls.", "where": "Abstract", "src": "publisher's record via Crossref"}, {"for": "louder sound from fitter agents", "quote": "in the infrasonic search algorithm higher quality solutions produce higher sound intensity compared to poorer solutions and agents move towards regions producing high intensity infrasonic sounds.", "where": "Section 1, Introduction", "src": "author's copy (arXiv:2106.14487)"}, {"for": "intensity that falls with distance", "quote": "Given that sound intensity reduces as the distance between the originating source increases, the rate at which an agent responds to sound from another agent reduces as the euclidean distance between the two agents increases.", "where": "Section 3.1, Infrasonic Search Algorithm (ISA)", "src": "author's copy (arXiv:2106.14487)"}, {"for": "moving towards the neighbour heard loudest", "quote": "An agent moves towards its neighbour with the highest intensity by a percentage of the difference between the vector that represents the agent Vi and the vector that represents the neighbour Vj with the highest intensity as shown in Equation 3.5.", "where": "Section 3.1.1, Formulation of the ISA", "src": "author's copy (arXiv:2106.14487)"}], "note": "In the paper's equation (3.1) the intensity is the power divided by the square of 4πr², so it falls with the fourth power of distance; Echo and Encore use the inverse-square law of equation (2)."}],
    ["Kumar, A., Price, K. V., Mohamed, A. W., Hadi, A. A. & Suganthan, P. N. (2021). Problem definitions and evaluation criteria for the CEC 2022 special session and competition on single objective bound constrained numerical optimization. Technical report.", "https://github.com/P-N-Suganthan/2022-SO-BO", {"checked": "Checked against the technical report in the organisers' repository (github.com/P-N-Suganthan/2022-SO-BO).", "evidence": [{"for": "12 functions, 10 and 20 coordinates, 200,000 and 1,000,000 evaluations, 30 runs", "quote": "Problems: 12 minimization problems\nDimensions: D = 10 and 20\nRuns / problem: 30\nMaxFES: D = 10: 200,000; D = 20: 1,000,000", "where": "Section 2.1, Experimental Settings (rows of the settings list; the MaxFES row is a small table)", "src": "technical report"}]}],
    ["Peram, T., Veeramachaneni, K. & Mohan, C. K. (2003). Fitness-distance-ratio based particle swarm optimization. Proceedings of the 2003 IEEE Swarm Intelligence Symposium, 174-181.", "https://doi.org/10.1109/SIS.2003.1202264", {"checked": "Checked on Crossref: authors, year, title, venue, pages and DOI match.", "evidence": [{"for": "following better particles, weighing fitness against distance, coordinate by coordinate", "quote": "The proposed new algorithm moves particles towards nearby particles of higher fitness, instead of attracting each particle towards just the best position discovered so far by any particle. This is accomplished by using the ratio of the relative fitness and the distance of other particles to determine the direction in which each component of the particle position needs to be changed.", "where": "Abstract", "src": "publisher's record via OpenAlex"}]}],
    ["Sörensen, K. (2015). Metaheuristics - the metaphor exposed. International Transactions in Operational Research, 22(1), 3-18.", "https://doi.org/10.1111/itor.12001", {"checked": "Checked on Crossref: authors, year, title, venue, pages and DOI match.", "evidence": [{"for": "criticism of metaphor-based methods", "quote": "In recent years, the field of combinatorial optimization has witnessed a true tsunami of “novel” metaheuristic methods, most of them based on a metaphor of some natural or man‐made process.", "where": "Abstract", "src": "publisher's record via Crossref"}, {"for": "criticism of metaphor-based methods", "quote": "In this paper, we will argue that this line of research is threatening to lead the area of metaheuristics away from scientific rigor.", "where": "Abstract", "src": "publisher's record via Crossref"}]}],
    ["Storn, R. & Price, K. (1997). Differential evolution - a simple and efficient heuristic for global optimization over continuous spaces. Journal of Global Optimization, 11(4), 341-359.", "https://doi.org/10.1023/A:1008202821328", {"checked": "Checked on Crossref: authors, year, title, venue, pages and DOI match.", "evidence": [{"for": "difference moves", "quote": "DE generates new parameter vectors by adding the weighted difference between two population vectors to a third vector.", "where": "Section 2, Differential Evolution", "src": "copy of the published article"}, {"for": "crossover with a set probability, at least one coordinate changing", "quote": "CR is the crossover constant ∈ [0, 1] which has to be determined by the user. rnbr(i) is a randomly chosen index ∈ 1, 2, ..., D which ensures that ui,G+1 gets at least one parameter from vi,G+1.", "where": "Section 2, Differential Evolution (crossover)", "src": "copy of the published article"}]}],
    ["Tanabe, R. & Fukunaga, A. (2013). Success-history based parameter adaptation for differential evolution. 2013 IEEE Congress on Evolutionary Computation, 71-78.", "https://doi.org/10.1109/CEC.2013.6557555", {"checked": "Checked on Crossref: authors, year, title, venue, pages and DOI match.", "evidence": [{"for": "success-history adaptation of the step size and hearing rate", "quote": "We propose a new, parameter adaptation technique for DE which uses a historical memory of successful control parameter settings to guide the selection of future control parameter values.", "where": "Abstract", "src": "publisher's record via OpenAlex"}]}],
    ["Tanabe, R. & Fukunaga, A. (2014). Improving the search performance of SHADE using linear population size reduction. 2014 IEEE Congress on Evolutionary Computation, 1658-1665.", "https://doi.org/10.1109/CEC.2014.6900380", {"checked": "Checked on Crossref: authors, year, title, venue, pages and DOI match.", "evidence": [{"for": "a group that shrinks linearly", "quote": "This paper proposes L-SHADE, which further extends SHADE with Linear Population Size Reduction (LPSR), which continually decreases the population size according to a linear function.", "where": "Abstract", "src": "authors' copy (ryojitanabe.github.io)"}, {"for": "removing the worst agents, down to 4", "quote": "in the case of L-SHADE, Nmin = 4 because the current-to-pbest mutation operator Eq. (3) requires 4 individuals. [...] Whenever NG+1 < NG, the (NG − NG+1) worst-ranking individuals are deleted from the population.", "where": "Section II-F, Linear Population Size Reduction (LPSR) and L-SHADE", "src": "authors' copy (ryojitanabe.github.io)"}, {"for": "18 agents per coordinate at the start, and p = 11%", "quote": "we set the initial population size Ninit to the dimensionality D of the functions multiplied by a parameter rNinit, i.e., Ninit = round(D×rNinit).\nTable II, tuned settings: rNinit = 18, rarc = 2.6, p = 0.11, H = 6.", "where": "Section III-A, Algorithm Parameters, and Table II", "src": "authors' copy (ryojitanabe.github.io)"}, {"for": "the current-to-pbest move of L-SHADE", "quote": "a mutant vector vi,G is generated from an existing population members by applying the current-to-pbest/1 mutation strategy, which is the mutation strategy used by JADE [5]", "where": "Section II-B, Reproduction of trial vectors by using current-to-pbest/1/bin", "src": "authors' copy (ryojitanabe.github.io)"}]}],
    ["Yang, X.-S. (2009). Firefly algorithms for multimodal optimization. Stochastic Algorithms: Foundations and Applications (SAGA 2009), Lecture Notes in Computer Science, 169-178.", "https://doi.org/10.1007/978-3-642-04944-6_14", {"checked": "Checked on Crossref: authors, year, title, venue, pages and DOI match.", "evidence": [{"for": "drawn to every brighter agent, more weakly with distance", "quote": "Attractiveness is proportional to their brightness, thus for any two flashing fireflies, the less brighter one will move towards the brighter one. The attractiveness is proportional to the brightness and they both decrease as their distance increases.", "where": "Section 3.2, Firefly Algorithm", "src": "author's copy (arXiv:1003.1466)"}]}],
    ["Yao, X., Liu, Y. & Lin, G. (1999). Evolutionary programming made faster. IEEE Transactions on Evolutionary Computation, 3(2), 82-102.", "https://doi.org/10.1109/4235.771163", {"checked": "Checked on Crossref: authors, year, title, venue, pages and DOI match.", "evidence": [{"for": "the 23 classic functions", "quote": "For a suite of 23 benchmark problems, FEP performs much better than CEP for multimodal functions with many local minima while being comparable to CEP in performance for unimodal and multimodal functions with only a few local minima.", "where": "Abstract", "src": "publisher's record via OpenAlex"}]}],
    ["Zhang, J. & Sanderson, A. C. (2009). JADE: adaptive differential evolution with optional external archive. IEEE Transactions on Evolutionary Computation, 13(5), 945-958.", "https://doi.org/10.1109/TEVC.2009.2014613", {"checked": "Checked on Crossref: authors, year, title, venue, pages and DOI match.", "evidence": [{"for": "the current-to-pbest rule and the archive of old positions", "quote": "A new differential evolution (DE) algorithm, JADE, is proposed to improve optimization performance by implementing a new mutation strategy “DE/current-to-pbest” with optional external archive and updating control parameters in an adaptive manner. The DE/current-to-pbest is a generalization of the classic “DE/current-to-best,” while the optional archive operation utilizes historical data to provide information of progress direction.", "where": "Abstract", "src": "publisher's record via OpenAlex"}], "note": "That the archive holds the parents replaced by better trial points is stated in the body of the paper, which could not be retrieved from a trustworthy open source; L-SHADE's paper confirms that current-to-pbest comes from JADE."}]
  ]
};
